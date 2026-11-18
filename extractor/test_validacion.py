from datetime import date, timedelta
from decimal import Decimal

from esquemas import Factura
from validacion import validar_factura

NIF_VALIDO = "12345678Z"


def _factura(
    es_factura=True,
    proveedor="Proveedor de Prueba S.L.",
    nif_proveedor=NIF_VALIDO,
    numero="F-001",
    fecha="2025-10-01",
    desglose_iva=None,
    retencion_irpf=Decimal("0"),
    total=None,
    moneda="EUR",
):
    if desglose_iva is None:
        desglose_iva = [{"base": Decimal("100.00"), "tipo_iva": Decimal("21"), "cuota": Decimal("21.00")}]
    if total is None:
        suma = sum((Decimal(l["base"]) + Decimal(l["cuota"]) for l in desglose_iva), Decimal("0"))
        total = suma - retencion_irpf
    return Factura(
        es_factura=es_factura,
        proveedor=proveedor,
        nif_proveedor=nif_proveedor,
        numero=numero,
        fecha=fecha,
        desglose_iva=desglose_iva,
        retencion_irpf=retencion_irpf,
        total=total,
        moneda=moneda,
    )


def test_factura_correcta_se_aprueba():
    factura = _factura()
    resultado = validar_factura(factura, texto_extraido=f"TOTAL: {factura.total} EUR")
    assert resultado.estado == "aprobado"
    assert resultado.motivos == []


def test_total_incoherente_pasa_a_revision():
    factura = _factura(total=Decimal("999.99"))
    resultado = validar_factura(factura, texto_extraido="TOTAL: 999.99 EUR")
    assert resultado.estado == "revision"
    assert "El total no cuadra con el desglose" in resultado.motivos


def test_cuota_iva_incoherente_pasa_a_revision():
    desglose = [{"base": Decimal("100.00"), "tipo_iva": Decimal("21"), "cuota": Decimal("30.00")}]
    factura = _factura(desglose_iva=desglose, total=Decimal("130.00"))
    resultado = validar_factura(factura, texto_extraido="TOTAL: 130.00 EUR")
    assert resultado.estado == "revision"
    assert "Una cuota de IVA no cuadra" in resultado.motivos


def test_nif_incorrecto_pasa_a_revision():
    factura = _factura(nif_proveedor="12345678A")
    resultado = validar_factura(factura, texto_extraido=f"TOTAL: {factura.total} EUR")
    assert resultado.estado == "revision"
    assert "NIF no válido" in resultado.motivos


def test_fecha_futura_pasa_a_revision():
    fecha_futura = (date.today() + timedelta(days=10)).isoformat()
    factura = _factura(fecha=fecha_futura)
    resultado = validar_factura(factura, texto_extraido=f"TOTAL: {factura.total} EUR")
    assert resultado.estado == "revision"
    assert "Fecha futura" in resultado.motivos


def test_tipo_iva_inusual_pasa_a_revision():
    desglose = [{"base": Decimal("100.00"), "tipo_iva": Decimal("15"), "cuota": Decimal("15.00")}]
    factura = _factura(desglose_iva=desglose, total=Decimal("115.00"))
    resultado = validar_factura(factura, texto_extraido="TOTAL: 115.00 EUR")
    assert resultado.estado == "revision"
    assert "Tipo de IVA inusual" in resultado.motivos


def test_importe_superior_al_maximo_pasa_a_revision():
    desglose = [{"base": Decimal("2000.00"), "tipo_iva": Decimal("21"), "cuota": Decimal("420.00")}]
    factura = _factura(desglose_iva=desglose, total=Decimal("2420.00"))
    resultado = validar_factura(
        factura, texto_extraido="TOTAL: 2420.00 EUR", importe_max_auto=Decimal("1500")
    )
    assert resultado.estado == "revision"
    assert "Importe superior al máximo automático" in resultado.motivos


def test_moneda_distinta_de_euro_pasa_a_revision():
    factura = _factura(moneda="USD")
    resultado = validar_factura(factura, texto_extraido=f"TOTAL: {factura.total} EUR")
    assert resultado.estado == "revision"
    assert "Moneda distinta de euro" in resultado.motivos


def test_dos_tipos_de_iva_con_retencion_se_aprueba():
    desglose = [
        {"base": Decimal("100.00"), "tipo_iva": Decimal("21"), "cuota": Decimal("21.00")},
        {"base": Decimal("50.00"), "tipo_iva": Decimal("10"), "cuota": Decimal("5.00")},
    ]
    retencion = Decimal("10.00")
    total = Decimal("100.00") + Decimal("21.00") + Decimal("50.00") + Decimal("5.00") - retencion
    factura = _factura(desglose_iva=desglose, retencion_irpf=retencion, total=total)
    resultado = validar_factura(factura, texto_extraido=f"TOTAL: {total} EUR")
    assert resultado.estado == "aprobado"
    assert resultado.motivos == []
