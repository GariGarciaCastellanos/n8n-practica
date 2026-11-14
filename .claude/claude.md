# Proyecto n8n-practica

Sistema de práctica: n8n + Postgres + validador FastAPI + túnel Cloudflare,
con Docker Compose en Ubuntu (WSL). La guía completa está en GUIA.md.

## Reglas
- Respóndeme en español y explícame cada paso en pocas líneas: soy principiante
  con n8n, Docker, Postgres y Cloudflare.
- Antes de ejecutar un comando de Docker, dime qué hace.
- Nunca ejecutes `docker compose down -v` ni borres volúmenes sin que yo lo pida.
- Nunca muestres, copies ni imprimas el contenido de `.env`.
- No pongas contraseñas ni claves dentro de los flujos ni de archivos del repositorio.
- No publiques flujos, no envíes correos reales ni hagas `git push` sin preguntarme.
- Usa solo datos de prueba, nunca datos reales de clientes.

## Convenciones
- Servicios de compose: postgres, n8n, validador y cloudflared (perfil `tunnel`).
- Los nodos de n8n se llaman exactamente como en GUIA.md.
- Hoja de Google con las pestañas Contactos y Errores.