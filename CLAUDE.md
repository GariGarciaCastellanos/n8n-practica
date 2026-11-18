# Proyecto n8n-practica

Soy principiante absoluto con n8n, Docker, Postgres y Cloudflare. Trabajo en Windows con Docker Desktop. Este proyecto es una práctica y el encargo completo está en PLAN.md.

## Cómo quiero que trabajes
- Respóndeme siempre en español, con frases cortas y sin jerga. Si usas una palabra técnica, explícala en una línea.
- Antes de ejecutar algo, dime en una frase qué vas a hacer. Al terminar, dime en una frase qué ha pasado y cómo sé que ha ido bien.
- Haz solo lo que te pida en cada mensaje. Si falta información, pregúntamela; no improvises.
- Si algo falla, explícame el error en lenguaje sencillo y propón la solución antes de cambiar nada.

## Reglas de seguridad
- No leas, no muestres ni copies el contenido de .env.
- No pongas contraseñas, claves ni tokens dentro de los flujos, del código ni de archivos que vayan a Git.
- No ejecutes `docker compose down -v` ni borres volúmenes o carpetas sin que yo lo pida expresamente.
- No publiques flujos de n8n, no envíes correos reales y no hagas `git push` sin preguntarme antes.
- Usa solo datos de prueba. Nunca datos reales de clientes.
- Cuando algo requiera mi cuenta de Google, mi contraseña o aceptar permisos, para y dime que lo haga yo.

## Nombres
- Los servicios de Docker se llaman: postgres, n8n, validador y cloudflared.
- Los flujos y nodos de n8n se llaman exactamente como en PLAN.md.

## Módulo 4: leads y facturas
- Para este trabajo usa PLAN-LEADS.md. Cuando te pida una "Parte", haz esa parte entera y nada más.
- Los emails de prueba de los leads son siempre alias de mi correo (por ejemplo, nombre+laura@gmail.com). Nunca escribas a direcciones de terceros.
- No pongas claves de Pipedrive, Airtable ni Anthropic en flujos ni en archivos que vayan a Git. Las claves van en credenciales de n8n o en .env, que no puedes leer.
- Los flujos nuevos se crean sin publicar. Publicar lo hago yo.
- Los datos de los leads son datos personales: en las pruebas usa solo datos inventados.
- Las facturas no se emiten desde n8n ni desde código propio: solo recordatorios y avisos sobre datos de una hoja.
