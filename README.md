# n8n-practica

Proyecto de práctica para aprender n8n, Docker, Postgres y Cloudflare.

## Qué es

Un formulario de contacto llega a n8n por webhook, se valida con un servicio
en Python (FastAPI), se guarda en una hoja de Google, avisa por correo y
avisa si algo falla.

Servicios de Docker:

- **postgres**: base de datos de n8n.
- **n8n**: motor de automatización (http://localhost:5678).
- **validador**: servicio en Python que valida nombre, email, teléfono y
  mensaje (http://localhost:8000).
- **cloudflared**: túnel para exponer el webhook a Internet (opcional,
  perfil `tunnel`).

## Cómo arrancar

1. Si no existe `.env`, crearlo con:

   ```bash
   ./crear-env.sh
   ```

   Abre `.env` con el Bloc de notas y guarda la clave de cifrado en tu
   gestor de contraseñas.

2. Arrancar todo:

   ```bash
   docker compose up -d
   ```

3. Comprobar que funciona:

   - n8n: http://localhost:5678/healthz
   - validador: http://localhost:8000/salud

4. Si necesitas exponer el webhook a Internet con un túnel:

   ```bash
   docker compose --profile tunnel up -d cloudflared
   ```

   Recuerda pararlo cuando no lo uses:

   ```bash
   docker compose stop cloudflared
   ```

## Cómo exportar los flujos

Para guardar una copia de todos los flujos de n8n en la carpeta
`workflows/`:

```bash
./exportar.sh
```
