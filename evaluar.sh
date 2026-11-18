#!/usr/bin/env bash
set -euo pipefail

RED="$(docker inspect n8n-practica-extractor-1 --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || true)"
if [ -z "$RED" ]; then
  echo "El servicio extractor no está arrancado. Ejecuta: docker compose up -d extractor" >&2
  exit 1
fi

MSYS_NO_PATHCONV=1 docker run --rm \
  --network "$RED" \
  -v "$(pwd):/trabajo" \
  -w /trabajo \
  ${MODELO_IA:+-e MODELO_IA="$MODELO_IA"} \
  python:3.12-slim \
  bash -c "pip install --quiet --no-cache-dir requests && python evaluar.py"
