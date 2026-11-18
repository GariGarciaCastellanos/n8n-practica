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


def test_normalizar_lead_correcto():
    respuesta = client.post(
        "/normalizar",
        json={
            "nombre": "  Laura Martín ",
            "email": " enviosmspython+laura@gmail.com ",
            "telefono": "612 34 56 78",
            "servicio": "Ortodoncia",
            "mensaje": "Quiero pedir cita para una revisión de ortodoncia",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is True
    assert datos["errores"] == []
    assert datos["nombre"] == "Laura Martín"
    assert datos["email"] == "enviosmspython+laura@gmail.com"
    assert datos["telefono"] == "+34612345678"
    assert datos["servicio"] == "ortodoncia"
    assert datos["mensaje"] == "Quiero pedir cita para una revisión de ortodoncia"


def test_normalizar_sin_email():
    respuesta = client.post(
        "/normalizar",
        json={
            "nombre": "Marta Gil",
            "telefono": "611 222 333",
            "servicio": "blanqueamiento",
            "mensaje": "Se me ha olvidado el correo",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert "Falta el email" in datos["errores"]


def test_normalizar_email_sin_arroba():
    respuesta = client.post(
        "/normalizar",
        json={
            "nombre": "Pablo Ruiz",
            "email": "pablo.ejemplo.es",
            "servicio": "implantes",
            "mensaje": "Correo mal escrito",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert "El email no tiene un formato válido" in datos["errores"]


def test_normalizar_telefono_invalido():
    respuesta = client.post(
        "/normalizar",
        json={
            "nombre": "Ane Sáez",
            "email": "enviosmspython+ane@gmail.com",
            "telefono": "123",
            "servicio": "limpieza",
            "mensaje": "Teléfono mal puesto",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert "El teléfono no es válido" in datos["errores"]


def test_normalizar_sin_nombre():
    respuesta = client.post(
        "/normalizar",
        json={
            "email": "enviosmspython+test@gmail.com",
            "servicio": "limpieza",
            "mensaje": "Falta el nombre",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is False
    assert "Falta el nombre" in datos["errores"]


def test_normalizar_email_con_etiqueta():
    respuesta = client.post(
        "/normalizar",
        json={
            "nombre": "Iker Aguirre",
            "email": "ENVIOSMSPYTHON+IKER@GMAIL.COM",
            "servicio": "limpieza",
            "mensaje": "Necesito una limpieza dental esta semana",
        },
    )
    datos = respuesta.json()
    assert respuesta.status_code == 200
    assert datos["valido"] is True
    assert datos["email"] == "enviosmspython+iker@gmail.com"
