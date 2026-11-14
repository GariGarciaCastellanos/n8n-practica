from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_formulario_correcto():
    respuesta = client.post(
        "/validar",
        json={
            "nombre": "  Ana López ",
            "email": " Ana@Ejemplo.ES ",
            "telefono": "612 34 56 78",
            "mensaje": "Quiero información sobre una cita",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is True
    assert datos["errores"] == []
    assert datos["nombre"] == "Ana López"
    assert datos["email"] == "ana@ejemplo.es"
    assert datos["telefono"] == "+34612345678"
    assert datos["mensaje"] == "Quiero información sobre una cita"


def test_sin_email():
    respuesta = client.post(
        "/validar",
        json={
            "nombre": "Marta Gil",
            "telefono": "611 222 333",
            "mensaje": "Se me ha olvidado el correo",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert "Falta el email" in datos["errores"]


def test_email_sin_arroba():
    respuesta = client.post(
        "/validar",
        json={
            "nombre": "Pablo Ruiz",
            "email": "pablo.ejemplo.es",
            "mensaje": "Correo mal escrito",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert "El email no tiene un formato válido" in datos["errores"]


def test_telefono_invalido():
    respuesta = client.post(
        "/validar",
        json={
            "nombre": "Luis",
            "email": "luis@ejemplo.es",
            "telefono": "123",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert "El teléfono no es válido" in datos["errores"]


def test_sin_nombre():
    respuesta = client.post(
        "/validar",
        json={
            "email": "ana@ejemplo.es",
            "mensaje": "Falta el nombre",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert "Falta el nombre" in datos["errores"]
