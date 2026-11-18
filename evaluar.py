#!/usr/bin/env python3
"""Evalúa el extractor contra datos-prueba/esperado.json (Parte 4 de PLAN-DOCUMENTOS.md).

Se ejecuta dentro de un contenedor temporal (ver evaluar.sh en la raíz del
proyecto), conectado a la misma red que el servicio extractor. Para usar otro
modelo sin tocar .env: MODELO_IA=otro-modelo ./evaluar.sh
"""
import json
import os
import statistics
from decimal import Decimal
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent
DATOS_PRUEBA = RAIZ / "datos-prueba"
INFORME = RAIZ / "docs" / "informe.md"

URL_EXTRACTOR = os.environ.get("URL_EXTRACTOR", "http://extractor:8000/extraer")
MODELO_IA = os.environ.get("MODELO_IA")  # si no se pone, usa el del extractor

CAMPOS_COMPARABLES = ["proveedor", "nif_proveedor", "numero", "fecha", "total"]
ESTADOS = ["aprobado", "revision", "rechazado"]


def cargar_esperado() -> dict:
    with open(DATOS_PRUEBA / "esperado.json", encoding="utf-8") as fh:
        return json.load(fh)


def extraer(archivo: Path) -> dict:
    with open(archivo, "rb") as fh:
        datos = {"modelo": MODELO_IA} if MODELO_IA else {}
        respuesta = requests.post(
            URL_EXTRACTOR,
            files={"archivo": (archivo.name, fh)},
            data=datos,
            timeout=120,
        )
    respuesta.raise_for_status()
    return respuesta.json()


def evaluar_campos(resultados: list) -> dict:
    aciertos = {c: 0 for c in CAMPOS_COMPARABLES}
    comparables = {c: 0 for c in CAMPOS_COMPARABLES}
    for _, obtenido, exp in resultados:
        factura_obtenida = obtenido.get("factura") or {}
        for campo in CAMPOS_COMPARABLES:
            esperado_valor = exp.get(campo)
            if esperado_valor is None:
                continue
            comparables[campo] += 1
            if factura_obtenida.get(campo) == esperado_valor:
                aciertos[campo] += 1
    return {c: (aciertos[c], comparables[c]) for c in CAMPOS_COMPARABLES}


def evaluar_proceso_automatico(resultados: list):
    facturas_correctas = [r for r in resultados if r[2]["estado_esperado"] == "aprobado"]
    aprobadas_solas = [r for r in facturas_correctas if r[1]["estado"] == "aprobado"]
    return aprobadas_solas, facturas_correctas


def evaluar_falsos_aprobados(resultados: list) -> list:
    return [
        r for r in resultados
        if r[2]["estado_esperado"] in ("revision", "rechazado") and r[1]["estado"] == "aprobado"
    ]


def evaluar_coste(resultados: list):
    costes = [Decimal(str(o["coste_eur"])) for _, o, _ in resultados if o.get("coste_eur") is not None]
    if not costes:
        return None
    return sum(costes) / len(costes)


def tabla_estados(resultados: list) -> dict:
    tabla = {e: {o: 0 for o in ESTADOS} for e in ESTADOS}
    for _, obtenido, exp in resultados:
        tabla[exp["estado_esperado"]][obtenido["estado"]] += 1
    return tabla


def escribir_informe(resultados: list) -> None:
    total_docs = len(resultados)
    acierto_campos = evaluar_campos(resultados)
    aprobadas_solas, facturas_correctas = evaluar_proceso_automatico(resultados)
    falsos_aprobados = evaluar_falsos_aprobados(resultados)
    tiempo_medio = statistics.mean(o["ms"] for _, o, _ in resultados) if resultados else 0
    coste_medio = evaluar_coste(resultados)
    tabla = tabla_estados(resultados)
    modelo_usado = MODELO_IA or "(el configurado en el extractor)"

    lineas = []
    lineas.append("# Informe de evaluación del extractor")
    lineas.append("")
    lineas.append(f"- Documentos evaluados: {total_docs}")
    lineas.append(f"- Modelo: {modelo_usado}")
    lineas.append("")

    lineas.append("## Acierto por campo")
    lineas.append("")
    lineas.append("| Campo | Aciertos | Comparados | % |")
    lineas.append("| --- | --- | --- | --- |")
    for campo in CAMPOS_COMPARABLES:
        aciertos, comparados = acierto_campos[campo]
        pct = f"{(aciertos / comparados * 100):.1f}%" if comparados else "—"
        lineas.append(f"| {campo} | {aciertos} | {comparados} | {pct} |")
    lineas.append("")

    lineas.append("## Tasa de proceso automático")
    lineas.append("")
    if facturas_correctas:
        tasa = len(aprobadas_solas) / len(facturas_correctas) * 100
        lineas.append(
            f"{len(aprobadas_solas)} de {len(facturas_correctas)} facturas correctas "
            f"se aprobaron solas ({tasa:.1f}%)."
        )
    else:
        lineas.append("No hay facturas correctas en el lote evaluado.")
    lineas.append("")

    lineas.append("## Falsos aprobados")
    lineas.append("")
    lineas.append(f"{len(falsos_aprobados)} (deben ser 0)")
    for nombre, obtenido, exp in falsos_aprobados:
        lineas.append(f"- {nombre}: esperado `{exp['estado_esperado']}`, se aprobó solo")
    lineas.append("")

    lineas.append("## Tiempo medio")
    lineas.append("")
    lineas.append(f"{tiempo_medio:.0f} ms por documento")
    lineas.append("")

    tokens_entrada_medio = statistics.mean(o["tokens_entrada"] for _, o, _ in resultados) if resultados else 0
    tokens_salida_medio = statistics.mean(o["tokens_salida"] for _, o, _ in resultados) if resultados else 0
    lineas.append("## Tokens medios por documento")
    lineas.append("")
    lineas.append(f"- Entrada: {tokens_entrada_medio:.0f} tokens")
    lineas.append(f"- Salida: {tokens_salida_medio:.0f} tokens")
    lineas.append("")

    lineas.append("## Coste")
    lineas.append("")
    if coste_medio is not None:
        lineas.append(f"- Coste medio por documento: {coste_medio:.6f} €")
        lineas.append(f"- Coste estimado por 1000 documentos: {(coste_medio * 1000):.2f} €")
    else:
        lineas.append(
            "No hay precios configurados (PRECIO_ENTRADA_EUR_MTOK / "
            "PRECIO_SALIDA_EUR_MTOK), así que no se calcula el coste."
        )
    lineas.append("")

    lineas.append("## Estado esperado frente a estado obtenido")
    lineas.append("")
    lineas.append("| Esperado \\ Obtenido | " + " | ".join(ESTADOS) + " |")
    lineas.append("| --- | " + " | ".join("---" for _ in ESTADOS) + " |")
    for esperado_estado in ESTADOS:
        fila = [str(tabla[esperado_estado][o]) for o in ESTADOS]
        lineas.append(f"| {esperado_estado} | " + " | ".join(fila) + " |")
    lineas.append("")

    INFORME.parent.mkdir(parents=True, exist_ok=True)
    INFORME.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Informe escrito en {INFORME}")


def main() -> None:
    esperado = cargar_esperado()
    archivos = sorted(p for p in DATOS_PRUEBA.iterdir() if p.name in esperado)

    resultados = []
    for archivo in archivos:
        obtenido = extraer(archivo)
        exp = esperado[archivo.name]
        resultados.append((archivo.name, obtenido, exp))
        print(f"{archivo.name}: obtenido={obtenido['estado']} esperado={exp['estado_esperado']}")

    escribir_informe(resultados)


if __name__ == "__main__":
    main()
