#!/usr/bin/env bash
set -euo pipefail

mkdir -p datos-prueba

MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd)/datos-prueba:/datos-prueba" \
  -w /datos-prueba \
  python:3.12-slim \
  bash -c "pip install --quiet --no-cache-dir reportlab pillow pymupdf && python generar_datos.py"

echo "Documentos de prueba generados en datos-prueba/"
