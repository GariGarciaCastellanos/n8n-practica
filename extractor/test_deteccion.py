import fitz
import pytest

from deteccion import detectar_tipo_documento


def _pdf_con_texto() -> bytes:
    documento = fitz.open()
    pagina = documento.new_page()
    pagina.insert_text((50, 50), "Factura de prueba. " * 10)
    datos = documento.tobytes()
    documento.close()
    return datos


def _pdf_sin_texto() -> bytes:
    documento = fitz.open()
    pagina = documento.new_page()
    forma = pagina.new_shape()
    forma.draw_rect(fitz.Rect(50, 50, 300, 300))
    forma.finish(fill=(0.85, 0.85, 0.85))
    forma.commit()
    datos = documento.tobytes()
    documento.close()
    return datos


def _png_minimo() -> bytes:
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 10, 10))
    pix.clear_with(255)
    return pix.tobytes("png")


def test_pdf_con_texto_se_detecta_como_pdf_texto():
    resultado = detectar_tipo_documento(_pdf_con_texto())
    assert resultado.tipo_documento == "pdf_texto"
    assert resultado.camino == "texto"
    assert "Factura de prueba" in resultado.texto


def test_pdf_sin_texto_se_detecta_como_pdf_escaneado():
    resultado = detectar_tipo_documento(_pdf_sin_texto())
    assert resultado.tipo_documento == "pdf_escaneado"
    assert resultado.camino == "vision"


def test_pdf_con_pocos_caracteres_se_detecta_como_pdf_escaneado():
    documento = fitz.open()
    pagina = documento.new_page()
    pagina.insert_text((50, 50), "Hola")
    datos = documento.tobytes()
    documento.close()

    resultado = detectar_tipo_documento(datos)
    assert resultado.tipo_documento == "pdf_escaneado"


def test_png_se_detecta_como_imagen():
    resultado = detectar_tipo_documento(_png_minimo())
    assert resultado.tipo_documento == "imagen"
    assert resultado.camino == "vision"


def test_archivo_no_soportado_lanza_error():
    with pytest.raises(ValueError):
        detectar_tipo_documento(b"esto no es ni un pdf ni una imagen")
