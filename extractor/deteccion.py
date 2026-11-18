from dataclasses import dataclass

import fitz

UMBRAL_CARACTERES_POR_PAGINA = 50


@dataclass
class DeteccionResultado:
    tipo_documento: str  # "pdf_texto" | "pdf_escaneado" | "imagen"
    camino: str  # "texto" | "vision"
    texto: str
    num_paginas: int


def _es_pdf(contenido: bytes) -> bool:
    return contenido[:5] == b"%PDF-"


def _es_imagen(contenido: bytes) -> bool:
    return contenido[:2] == b"\xff\xd8" or contenido[:8] == b"\x89PNG\r\n\x1a\n"


def detectar_tipo_documento(contenido: bytes) -> DeteccionResultado:
    if _es_pdf(contenido):
        with fitz.open(stream=contenido, filetype="pdf") as documento:
            num_paginas = documento.page_count
            texto = "\n".join(pagina.get_text() for pagina in documento)
        caracteres_por_pagina = len(texto) / num_paginas if num_paginas else 0
        if caracteres_por_pagina < UMBRAL_CARACTERES_POR_PAGINA:
            return DeteccionResultado("pdf_escaneado", "vision", texto, num_paginas)
        return DeteccionResultado("pdf_texto", "texto", texto, num_paginas)

    if _es_imagen(contenido):
        return DeteccionResultado("imagen", "vision", "", 1)

    raise ValueError("Tipo de archivo no soportado")
