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
- **extractor**: servicio en Python que extrae datos de facturas con la API
  de Claude (http://localhost:8001).
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

## Captación de leads

Este es el módulo de práctica de leads y facturas (PLAN-LEADS.md). Son varios
flujos de n8n que trabajan juntos sobre una hoja de Google ("leads-practica",
pestañas Leads, Errores y Facturas) y sobre Pipedrive como CRM:

- **Captación de leads**: recibe el formulario por webhook
  (`POST /captacion-leads`), lo normaliza con el servicio validador
  (`/normalizar`), y si es válido guarda la fila en Leads, avisa al lead y al
  equipo por Gmail, y envía el lead al CRM. Si no es válido, lo guarda en
  Errores con el motivo.
- **Enviar lead a Pipedrive**: sub-flujo que busca o crea la persona en
  Pipedrive, crea el negocio si es nueva y añade una nota con los datos del
  lead.
- **Reintentos de Pipedrive**: cada 15 minutos busca en Leads los que se
  quedaron con `estado_crm = pendiente` (porque el envío al CRM falló) y
  vuelve a intentarlo.
- **Seguimiento de leads**: cada hora avisa por correo de los leads que
  llevan más de 2 horas con `estado = nuevo` y sin recordatorio previo.

### Cómo se prueba

Con el flujo "Captación de leads" publicado, se envían los leads de prueba
de la sección "Datos de prueba" de PLAN-LEADS.md por POST a
`http://localhost:5678/webhook/captacion-leads`, con cabecera
`Content-Type: application/json`. Los emails de prueba son siempre alias del
correo propio (por ejemplo `+laura`), nunca direcciones de terceros. Hay un
caso pensado para provocar un fallo del CRM a propósito (mensaje
`PROVOCAR_FALLO_CRM`) y comprobar que el lead queda pendiente en vez de
perderse.

### Cómo se recupera si el CRM falla

Si Pipedrive no responde o da error al enviar un lead, "Captación de leads"
no se detiene ni pierde el lead: el nodo que llama al CRM tiene activado
"On Error: Continue", así que el resto del flujo sigue (el lead ya quedó
guardado en la hoja) y la fila se queda marcada como `estado_crm = pendiente`
en vez de `ok`. El flujo "Reintentos de Pipedrive" revisa esa columna cada 15
minutos y reintenta el envío al CRM de los leads pendientes, hasta que se
marcan como `ok`. No hace falta intervención manual salvo que el fallo sea
persistente.

## Facturas por correo

Este es el módulo de práctica de documentos (PLAN-DOCUMENTOS.md): un sistema
que recibe facturas de proveedores por correo, extrae sus datos con la API de
Claude y solo pasa a una persona lo dudoso ("el modelo propone y el código
comprueba").

- **extractor**: servicio en Python (FastAPI) que recibe un PDF o una imagen
  (`POST /extraer`), detecta si tiene texto o hay que usar visión, extrae los
  datos con Claude y los valida con código antes de decidir el estado. También
  tiene `POST /extraer-pedido`, que saca los datos de un pedido escrito en el
  cuerpo de un correo (Parte 6, opcional).
- **Facturas por correo**: flujo de n8n que vigila
  `<tu correo>+facturas@gmail.com`, manda cada archivo adjunto al extractor,
  comprueba si ya existe esa factura (por proveedor + número) y guarda el
  resultado en la pestaña correspondiente de la hoja `facturas-practica`
  (Facturas, Revision o Rechazados), avisando por correo si hace falta
  revisión. Cada documento procesado queda siempre anotado en la pestaña
  Registro, aunque se rechace o sea un duplicado.

### Los tres estados

- **aprobado**: la factura pasó todas las comprobaciones automáticas (campos
  completos, NIF válido, cuentas cuadradas, importe dentro del máximo...). Se
  guarda directamente en la pestaña Facturas, sin que nadie tenga que mirarla.
- **revision**: algo no cuadra o no se ha podido comprobar (falta un dato, el
  NIF no es válido, el total no coincide con el desglose, el documento supera
  el máximo automático...). Se guarda en Revision con los motivos exactos y se
  avisa por correo para que una persona lo revise. Nunca se aprueba algo solo
  porque "parezca" correcto.
- **rechazado**: el documento no es una factura (un presupuesto, un
  albarán...) o es un duplicado de una factura ya registrada. Se guarda en
  Rechazados con el motivo.

### Cómo se prueba

1. Arrancar el extractor (necesita `ANTHROPIC_API_KEY` en `.env`):

   ```bash
   docker compose up -d extractor
   ```

2. Evaluación automática contra los 25 documentos inventados de
   `datos-prueba/`:

   ```bash
   ./evaluar.sh
   ```

   Genera `docs/informe.md` con el acierto por campo, la tasa de aprobación
   automática, los falsos aprobados (deben ser siempre 0) y el coste. Para
   probar con otro modelo sin tocar `.env`:
   `MODELO_IA=claude-sonnet-5-5 ./evaluar.sh`.

3. Prueba de extremo a extremo: con el flujo "Facturas por correo" publicado,
   se envía un correo a `<tu correo>+facturas@gmail.com` con alguno de los
   archivos de `datos-prueba/` adjuntos, y se revisa en qué pestaña de la hoja
   ha caído y la ejecución correspondiente en n8n.

Los documentos de prueba (carpeta `datos-prueba/`) son siempre inventados;
nunca se usan facturas ni datos reales.
