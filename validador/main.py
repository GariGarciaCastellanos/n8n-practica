import re
from typing import List, Optional

import phonenumbers
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidarEntrada(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    mensaje: Optional[str] = None


class ValidarSalida(BaseModel):
    valido: bool
    errores: List[str]
    nombre: str
    email: str
    telefono: Optional[str]
    mensaje: str


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/validar", response_model=ValidarSalida)
def validar(entrada: ValidarEntrada):
    errores: List[str] = []

    nombre = (entrada.nombre or "").strip()
    email = (entrada.email or "").strip().lower()
    mensaje = (entrada.mensaje or "").strip()
    telefono = entrada.telefono

    if not nombre:
        errores.append("Falta el nombre")

    if not email:
        errores.append("Falta el email")
    elif not EMAIL_RE.match(email):
        errores.append("El email no tiene un formato válido")

    if telefono:
        try:
            numero = phonenumbers.parse(telefono, "ES")
            if phonenumbers.is_valid_number(numero):
                telefono = phonenumbers.format_number(
                    numero, phonenumbers.PhoneNumberFormat.E164
                )
            else:
                errores.append("El teléfono no es válido")
        except phonenumbers.NumberParseException:
            errores.append("El teléfono no es válido")

    return ValidarSalida(
        valido=len(errores) == 0,
        errores=errores,
        nombre=nombre,
        email=email,
        telefono=telefono,
        mensaje=mensaje,
    )
