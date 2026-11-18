import os
import time
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel, ValidationError

from cliente_claude import (
    calcular_coste,
    extraer_de_documento_visual,
    extraer_de_texto,
    extraer_pedido_de_texto,
    limite_superado,
)
from deteccion import detectar_tipo_documento
from esquemas import Factura, Pedido
from limpieza_correo import limpiar_texto_correo
from validacion import validar_factura

app = FastAPI()

MODELO_IA = os.environ.get("MODELO_IA", "claude-haiku-5-5")
IMPORTE_MAX_AUTO = Decimal(os.environ.get("IMPORTE_MAX_AUTO", "1500"))


class RespuestaExtraer(BaseModel):
    archivo: str
    tipo_documento: str
    camino: str
    estado: str
    motivos: List[str]
    factura: Optional[Dict[str, Any]]
    tokens_entrada: int
    tokens_salida: int
    coste_eur: Optional[Decimal]
    ms: int


@app.get("/salud")
def salud():
    return {"estado": "ok"}


def _respuesta(archivo, tipo_documento, camino, estado, motivos, factura, tokens_entrada, tokens_salida, inicio):
    coste = calcular_coste(tokens_entrada, tokens_salida) if (tokens_entrada or tokens_salida) else None
    return RespuestaExtraer(
        archivo=archivo,
        tipo_documento=tipo_documento,
        camino=camino,
        estado=estado,
        motivos=motivos,
        factura=factura,
        tokens_entrada=tokens_entrada,
        tokens_salida=tokens_salida,
        coste_eur=coste,
        ms=int((time.monotonic() - inicio) * 1000),
    )


@app.post("/extraer", response_model=RespuestaExtraer)
async def extraer(archivo: UploadFile = File(...), modelo: Optional[str] = Form(None)):
    inicio = time.monotonic()
    nombre = archivo.filename or "archivo"
    contenido = await archivo.read()
    modelo_efectivo = modelo or MODELO_IA

    try:
        deteccion = detectar_tipo_documento(contenido)
    except ValueError:
        return _respuesta(
            nombre, "desconocido", "desconocido", "revision",
            ["Error de extracción: tipo de archivo no soportado"],
            None, 0, 0, inicio,
        )

    if deteccion.camino == "vision":
        motivo_limite = limite_superado(deteccion.tipo_documento, deteccion.num_paginas, contenido)
        if motivo_limite:
            return _respuesta(
                nombre, deteccion.tipo_documento, deteccion.camino, "revision",
                [motivo_limite],
                None, 0, 0, inicio,
            )

    try:
        if deteccion.camino == "texto":
            datos_brutos, tokens_entrada, tokens_salida = extraer_de_texto(deteccion.texto, modelo_efectivo)
        else:
            es_pdf = deteccion.tipo_documento == "pdf_escaneado"
            datos_brutos, tokens_entrada, tokens_salida = extraer_de_documento_visual(contenido, es_pdf, modelo_efectivo)
    except Exception:
        return _respuesta(
            nombre, deteccion.tipo_documento, deteccion.camino, "revision",
            ["Error de extracción: no se pudo contactar con el modelo"],
            None, 0, 0, inicio,
        )

    try:
        factura = Factura(**datos_brutos)
    except ValidationError:
        return _respuesta(
            nombre, deteccion.tipo_documento, deteccion.camino, "revision",
            ["Error de extracción: la respuesta del modelo no tiene el formato esperado"],
            None, tokens_entrada, tokens_salida, inicio,
        )

    resultado = validar_factura(
        factura,
        texto_extraido=deteccion.texto,
        camino=deteccion.camino,
        importe_max_auto=IMPORTE_MAX_AUTO,
    )

    return _respuesta(
        nombre, deteccion.tipo_documento, deteccion.camino,
        resultado.estado, resultado.motivos,
        factura.model_dump(mode="json"), tokens_entrada, tokens_salida, inicio,
    )


class EntradaPedido(BaseModel):
    texto: str


class RespuestaPedido(BaseModel):
    pedido: Optional[Dict[str, Any]]
    tokens_entrada: int
    tokens_salida: int
    coste_eur: Optional[Decimal]
    ms: int


@app.post("/extraer-pedido", response_model=RespuestaPedido)
async def extraer_pedido(entrada: EntradaPedido, modelo: Optional[str] = None):
    inicio = time.monotonic()
    modelo_efectivo = modelo or MODELO_IA
    texto_limpio = limpiar_texto_correo(entrada.texto)

    try:
        datos_brutos, tokens_entrada, tokens_salida = extraer_pedido_de_texto(texto_limpio, modelo_efectivo)
    except Exception:
        return RespuestaPedido(
            pedido=None, tokens_entrada=0, tokens_salida=0, coste_eur=None,
            ms=int((time.monotonic() - inicio) * 1000),
        )

    try:
        pedido = Pedido(**datos_brutos)
    except ValidationError:
        return RespuestaPedido(
            pedido=None, tokens_entrada=tokens_entrada, tokens_salida=tokens_salida,
            coste_eur=calcular_coste(tokens_entrada, tokens_salida),
            ms=int((time.monotonic() - inicio) * 1000),
        )

    return RespuestaPedido(
        pedido=pedido.model_dump(mode="json"),
        tokens_entrada=tokens_entrada,
        tokens_salida=tokens_salida,
        coste_eur=calcular_coste(tokens_entrada, tokens_salida),
        ms=int((time.monotonic() - inicio) * 1000),
    )
