# PLAN.md: encargo técnico del proyecto n8n-practica

Objetivo: un formulario de contacto llega a n8n por webhook, se valida con un servicio en Python, se guarda en una hoja de Google, avisa por correo y avisa si algo falla.

Todo se ejecuta con Docker Compose en mi ordenador con Windows. Haz solo la parte que te pida ("Parte 1", "Parte 2"...).

## Parte 1. Carpeta y Docker

Archivos que debe haber en la carpeta del proyecto:
- compose.yml
- .env (secretos; lo crea un script, no se lee ni se muestra)
- .env.ejemplo (mismas variables que .env, sin valores)
- .gitignore con: .env, GUIA.md, __pycache__/, .venv/, *.log, .claude/settings.local.json
- workflows/ (flujos exportados)

compose.yml define estos servicios:
1. postgres: imagen postgres:18; POSTGRES_USER, POSTGRES_PASSWORD y POSTGRES_DB tomados de .env; PGDATA=/var/lib/postgresql/data; volumen db-storage en esa ruta; healthcheck con pg_isready; restart unless-stopped.
2. n8n: imagen n8nio/n8n con la versión de N8N_VERSION; puerto 5678:5678; usa Postgres (DB_TYPE=postgresdb, DB_POSTGRESDB_HOST=postgres, DB_POSTGRESDB_PORT=5432, y DB_POSTGRESDB_DATABASE, DB_POSTGRESDB_USER y DB_POSTGRESDB_PASSWORD tomados de .env); N8N_ENCRYPTION_KEY desde .env; GENERIC_TIMEZONE y TZ = Europe/Madrid; N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true; N8N_EDITOR_BASE_URL=http://localhost:5678; WEBHOOK_URL desde .env, con http://localhost:5678/ por defecto si está vacía; volumen n8n-data en /home/node/.n8n; depende de que postgres esté sano; restart unless-stopped.
3. cloudflared: imagen cloudflare/cloudflared; perfil "tunnel" (no arranca salvo que se pida); comando: tunnel --no-autoupdate --url http://n8n:5678
4. validador (se añade en la Parte 6): se construye desde la carpeta validador; puerto 8000:8000; restart unless-stopped.
Volúmenes: db-storage y n8n-data.

Variables de .env: N8N_VERSION (empieza con 2.46.6; si esa etiqueta no existe, usa la última versión estable), POSTGRES_USER=n8n, POSTGRES_PASSWORD (aleatoria), POSTGRES_DB=n8n, N8N_ENCRYPTION_KEY (aleatoria) y WEBHOOK_URL (vacía al principio).

Cómo crear .env: con un script que genere los valores aleatorios y los escriba en el archivo sin mostrarlos ni leerlos. Luego dime que abra yo el archivo con el Bloc de notas para guardar la clave de cifrado en mi gestor de contraseñas.

Comprobaciones tras arrancar: postgres en estado healthy; n8n responde en http://localhost:5678/healthz; y con psql dentro del contenedor (docker compose exec postgres psql -U n8n -d n8n -c '\dt') aparecen las tablas de n8n.

## Parte 2. Túnel

Arrancarlo con: docker compose --profile tunnel up -d cloudflared. Buscar en sus registros la dirección https://....trycloudflare.com. Escribirla en .env como WEBHOOK_URL=https://....trycloudflare.com/ (con la barra final) con un script que no lea el resto de .env. Recrear solo n8n (docker compose up -d n8n) y comprobar con: docker compose exec n8n printenv WEBHOOK_URL. La dirección cambia cada vez que se reinicia el túnel. El túnel expone todo n8n a Internet: recuérdame pararlo cuando no lo use (docker compose stop cloudflared).

## Parte 3. Hoja de Google (la creo yo, o Cowork; tú solo la usas)

Hoja "n8n-practica" con dos pestañas. Las cabeceras van en la fila 1, en minúsculas y exactamente así:
- Contactos: fecha | nombre | email | telefono | mensaje | origen
- Errores: fecha | nombre | email | telefono | mensaje | origen | motivo

## Parte 4. Flujo "Formulario de contacto"

Nodos, con estos nombres exactos:
1. Webhook: método POST, path formulario-contacto, Respond = Immediately, sin autenticación (es una práctica).
2. Limpiar datos (Edit Fields, modo manual, sin incluir otros campos):
   - fecha = {{ $now.toFormat('yyyy-MM-dd HH:mm') }}
   - nombre = {{ ($json.body.nombre || '').trim() }}
   - email = {{ ($json.body.email || '').trim().toLowerCase() }}
   - telefono = {{ ($json.body.telefono || '').replace(/[^\d+]/g, '') }}
   - mensaje = {{ ($json.body.mensaje || '').trim() }}
   - origen = formulario web (texto fijo)
3. Guardar en Contactos (Google Sheets): operación Append or Update Row; hoja n8n-practica, pestaña Contactos; columnas mapeadas a mano con {{ $json.campo }} para fecha, nombre, email, telefono, mensaje y origen; columna de coincidencia: email.
4. Avisar por correo (Gmail, enviar mensaje): para mi correo; asunto "Nuevo contacto: {{ $('Limpiar datos').item.json.nombre }}"; texto con nombre, email, teléfono, mensaje y fecha, leídos con $('Limpiar datos').item.json.CAMPO; sin el pie de atribución de n8n.
Conexiones: Webhook → Limpiar datos → Guardar en Contactos → Avisar por correo.
Los nodos de Google se dejan SIN credencial: las asigno yo. No se publica nada: lo publico yo.

## Parte 5. Rama de errores y aviso de fallos

a) En "Formulario de contacto", entre "Limpiar datos" y "Guardar en Contactos": un If llamado "¿Tiene email?" con dos condiciones (AND): email no vacío y email contiene @. Salida true → Guardar en Contactos. Salida false → un nodo Google Sheets "Guardar en Errores": Append Row, pestaña Errores, mismas columnas más motivo = "Falta el email o no es válido".
b) Flujo nuevo "Aviso de errores": Error Trigger → Gmail "Enviar aviso" a mi correo. Asunto: "Fallo en {{ $json.workflow.name }}". Texto con: flujo {{ $json.workflow.name }}, nodo {{ $json.execution.lastNodeExecuted }}, error {{ $json.execution.error.message }} y enlace {{ $json.execution.url }}. Yo lo asigno como flujo de errores en los ajustes de "Formulario de contacto".
c) Interruptor de prueba (temporal): justo después del Webhook, un If "¿Fallo de prueba?" con la condición {{ $json.body.provocar_fallo === true }}. Su salida true va a un nodo Stop and Error llamado "Fallo provocado" (mensaje: "Fallo provocado a propósito para probar el aviso"); la false sigue con el resto. Se elimina al terminar las pruebas.

## Parte 6. Servicio validador (Python con FastAPI)

Carpeta validador con requirements.txt (fastapi, uvicorn[standard], phonenumbers), main.py y Dockerfile (python:3.12-slim, uvicorn en 0.0.0.0:8000).
Rutas:
- GET /salud devuelve {"estado":"ok"}.
- POST /validar. Entrada JSON con campos opcionales nombre, email, telefono y mensaje (ignora cualquier otro campo). Salida JSON: valido (true o false), errores (lista de textos), nombre, email, telefono y mensaje.
Reglas: nombre, email y mensaje se limpian con trim, y el email se pone en minúsculas. Errores posibles: "Falta el nombre"; "Falta el email"; "El email no tiene un formato válido" (si no tiene la forma texto@texto.texto); el teléfono es opcional: si viene, se normaliza a formato internacional con región ES (por ejemplo +34612345678) y, si no es válido, error "El teléfono no es válido". valido es true si no hay errores. Un dato malo NO lanza un error HTTP: devuelve valido=false con la lista.
Pruebas con pytest que cubran: formulario correcto, sin email, email sin arroba, teléfono inválido y sin nombre.
Cambios en el flujo "Formulario de contacto":
- Nuevo nodo HTTP Request "Validar formulario" (después del interruptor de prueba, o del Webhook si ya no está): POST a http://validador:8000/validar (nunca localhost), cuerpo JSON {{ JSON.stringify($json.body) }}, con reintentos (3 intentos, 1000 ms entre ellos).
- "Limpiar datos" pasa a copiar nombre, email, telefono y mensaje desde {{ $json.campo }}; mantiene fecha y origen; añade valido = {{ $json.valido }} (booleano) y motivo = {{ $json.errores.join('; ') }}.
- "¿Tiene email?" se renombra "¿Es válido?" y queda con una sola condición: {{ $json.valido }} es true.
- "Guardar en Errores" usa motivo = {{ $json.motivo }}.

## Parte 7. Git

- Un script (exportar.sh o equivalente para Windows) que exporte todos los flujos de n8n a la carpeta workflows con: docker compose exec -u node n8n n8n export:workflow --backup --output=/tmp/export/ y copie los archivos con docker compose cp.
- Revisar que ningún JSON exportado contiene password, secret, token ni apikey.
- README.md con: qué es, cómo arrancar y cómo exportar los flujos. Sin secretos.
- Primer commit con un mensaje claro. Antes del commit, enséñame git status y confirma que .env y .claude/settings.local.json no entran.
- El git push lo hago yo, después de que me lo pidas.

## Pruebas del formulario (datos de ejemplo)

Se envían con POST, con cabecera Content-Type: application/json, a http://localhost:5678/webhook/formulario-contacto (con el flujo publicado):
- Correcto: {"nombre":"  Ana López ","email":" Ana@Ejemplo.ES ","telefono":"612 34 56 78","mensaje":"Quiero información sobre una cita"}
- Sin email: {"nombre":"Marta Gil","telefono":"611 222 333","mensaje":"Se me ha olvidado el correo"}
- Email sin arroba: {"nombre":"Pablo Ruiz","email":"pablo.ejemplo.es","mensaje":"Correo mal escrito"}
- Fallo provocado: {"nombre":"Prueba","email":"prueba@ejemplo.es","provocar_fallo":true}
