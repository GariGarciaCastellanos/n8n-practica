import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List

from esquemas import Factura

TOLERANCIA = Decimal("0.02")
TIPOS_IVA_VALIDOS = {Decimal("0"), Decimal("4"), Decimal("10"), Decimal("21")}
CAMPOS_OBLIGATORIOS = ("proveedor", "numero", "fecha", "total")

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"
LETRAS_CIF_CONTROL = "JABCDEFGHI"
CIF_SOLO_LETRA = set("KPQS")
CIF_SOLO_DIGITO = set("ABEH")
PREFIJOS_NIE = {"X": 0, "Y": 1, "Z": 2}

PATRON_DNI = re.compile(r"^(\d{8})([A-Za-z])$")
PATRON_NIE = re.compile(r"^([XYZxyz])(\d{7})([A-Za-z])$")
PATRON_CIF = re.compile(r"^([A-HJNPQRSUVWabhjnpqrsuvw])(\d{7})([0-9A-Za-z])$")


@dataclass
class ResultadoValidacion:
    estado: str  # "aprobado" | "revision" | "rechazado"
    motivos: List[str]


def _nif_valido(nif: str) -> bool:
    nif = nif.strip().upper().replace(" ", "")

    coincidencia = PATRON_DNI.match(nif)
    if coincidencia:
        numero, letra = coincidencia.groups()
        return LETRAS_DNI[int(numero) % 23] == letra

    coincidencia = PATRON_NIE.match(nif)
    if coincidencia:
        prefijo, numero, letra = coincidencia.groups()
        numero_completo = PREFIJOS_NIE[prefijo] * 10**7 + int(numero)
        return LETRAS_DNI[numero_completo % 23] == letra

    coincidencia = PATRON_CIF.match(nif)
    if coincidencia:
        letra, digitos, control = coincidencia.groups()
        cifras = [int(c) for c in digitos]
        suma_pares = sum(cifras[1::2])
        suma_impares = 0
        for cifra in cifras[0::2]:
            doble = cifra * 2
            suma_impares += doble if doble < 10 else doble - 9
        control_num = (10 - (suma_pares + suma_impares) % 10) % 10
        if letra in CIF_SOLO_LETRA:
            return control == LETRAS_CIF_CONTROL[control_num]
        if letra in CIF_SOLO_DIGITO:
            return control == str(control_num)
        return control == str(control_num) or control == LETRAS_CIF_CONTROL[control_num]

    return False


def _total_aparece_en_texto(total: Decimal, texto: str) -> bool:
    con_punto = f"{total:.2f}"
    con_coma = con_punto.replace(".", ",")
    return con_punto in texto or con_coma in texto


def validar_factura(
    factura: Factura,
    *,
    texto_extraido: str = "",
    camino: str = "texto",
    importe_max_auto: Decimal = Decimal("1500"),
) -> ResultadoValidacion:
    if not factura.es_factura:
        return ResultadoValidacion("rechazado", ["No es una factura"])

    motivos: List[str] = []

    for campo in CAMPOS_OBLIGATORIOS:
        if getattr(factura, campo) in (None, ""):
            motivos.append(f"Falta {campo}")

    if factura.fecha:
        try:
            fecha_valida = date.fromisoformat(factura.fecha)
        except ValueError:
            motivos.append("Fecha no válida")
        else:
            if fecha_valida > date.today():
                motivos.append("Fecha futura")

    if not factura.nif_proveedor:
        motivos.append("Falta el NIF del proveedor")
    elif not _nif_valido(factura.nif_proveedor):
        motivos.append("NIF no válido")

    if factura.total is not None:
        suma_desglose = sum(
            (linea.base + linea.cuota for linea in factura.desglose_iva), Decimal("0")
        )
        if abs(suma_desglose - factura.retencion_irpf - factura.total) > TOLERANCIA:
            motivos.append("El total no cuadra con el desglose")

    if any(
        abs(linea.base * linea.tipo_iva / Decimal("100") - linea.cuota) > TOLERANCIA
        for linea in factura.desglose_iva
    ):
        motivos.append("Una cuota de IVA no cuadra")

    if any(linea.tipo_iva not in TIPOS_IVA_VALIDOS for linea in factura.desglose_iva):
        motivos.append("Tipo de IVA inusual")

    if factura.total is not None and factura.total > importe_max_auto:
        motivos.append("Importe superior al máximo automático")

    if camino == "texto" and factura.total is not None:
        if not _total_aparece_en_texto(factura.total, texto_extraido):
            motivos.append("El total no aparece en el documento")

    if factura.moneda != "EUR":
        motivos.append("Moneda distinta de euro")

    estado = "aprobado" if not motivos else "revision"
    return ResultadoValidacion(estado, motivos)
