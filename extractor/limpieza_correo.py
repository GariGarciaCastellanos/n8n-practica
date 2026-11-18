import re

PATRON_CITA_INTRO = re.compile(r"^El .+ escribió:\s*$")


def limpiar_texto_correo(texto: str) -> str:
    lineas = texto.splitlines()
    resultado = []
    for linea in lineas:
        limpia = linea.strip()
        if PATRON_CITA_INTRO.match(limpia):
            break
        if limpia == "--":
            break
        if limpia.startswith(">"):
            continue
        resultado.append(linea)
    return "\n".join(resultado).strip()
