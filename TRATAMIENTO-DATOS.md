# Tratamiento de datos personales

Este documento describe, en lenguaje sencillo, qué datos personales trata el
módulo de leads y facturas (PLAN-LEADS.md) y el módulo de documentos
(PLAN-DOCUMENTOS.md), y con qué fin. **No es asesoramiento legal.** Es solo
un resumen para que un profesional (abogado o delegado de protección de
datos) revise lo que falta antes de usar este sistema con datos reales.

En las pruebas de este proyecto nunca se usan datos reales de clientes: los
leads de prueba usan nombres inventados y los correos son siempre alias del
correo propio (por ejemplo `+laura@gmail.com`).

## Qué datos personales se tratan

- **Nombre**
- **Email**
- **Teléfono**
- **Mensaje** (el texto libre que escribe la persona en el formulario)

También se guarda la fecha y el origen del lead ("formulario web"), que no
son datos personales por sí mismos pero van ligados a los anteriores.

## Con qué finalidad

- Responder al lead (acuse de recibo) y gestionar su solicitud.
- Avisar al equipo de que ha entrado un lead nuevo.
- Dar de alta o actualizar el contacto en el CRM (Pipedrive) y hacer
  seguimiento comercial.
- Avisar internamente si un lead lleva mucho tiempo sin atender.

## Con qué servicios se comparten

- **Google** (Google Sheets y Gmail): los datos del lead se guardan en una
  hoja de cálculo y se usan para enviar los correos de acuse y aviso.
- **Pipedrive**: se crea o actualiza la persona, el negocio y una nota con
  los datos del lead, para el seguimiento comercial.
- **Anthropic**: *solo si se activa la Parte 9 (opcional) de PLAN-LEADS.md*,
  que todavía no está implementada en este proyecto. Si se activa en el
  futuro, se enviaría el servicio y el mensaje del lead (nunca el nombre, el
  email ni el teléfono) a la API de Claude para clasificar el interés y la
  urgencia.

## Cuánto tiempo se conservan

Este proyecto de práctica no implementa ningún borrado automático: los datos
quedan en la hoja de Google y en Pipedrive hasta que alguien los borra a
mano. Antes de usar este sistema con datos reales, hay que definir un plazo
de conservación y, si procede, un proceso de borrado o anonimización.

## Qué debe revisar un profesional

Antes de usar este sistema con datos de clientes reales, una persona con
formación legal debería revisar al menos:

- **RGPD**: base legal del tratamiento, información a las personas
  interesadas (aviso de privacidad en el propio formulario), derechos de
  acceso, rectificación, supresión, etc., y si aplica una evaluación de
  impacto.
- **Contrato de encargado de tratamiento** con cada proveedor que trata
  datos por cuenta del responsable (Google, Pipedrive y, si se activa, el
  proveedor de la API de IA).
- **Consentimiento**: si el formulario recoge el consentimiento necesario
  para tratar los datos y, si corresponde, para el envío de comunicaciones
  comerciales.
- **Comunicaciones comerciales**: que el correo de acuse y cualquier aviso
  posterior cumplan la normativa aplicable (por ejemplo, LSSI en España) si
  se usan con fines comerciales.

## Facturas de proveedores (módulo de documentos, PLAN-DOCUMENTOS.md)

En las pruebas de este módulo nunca se usan facturas ni datos reales: los
documentos de `datos-prueba/` están inventados (empresas, NIF y direcciones
ficticios, sin personas reales).

### Qué datos personales se tratan

La factura de un proveedor que es **autónomo** (una persona física, no una
sociedad) contiene datos personales suyos: su **nombre** y su **NIF**, y su
dirección si aparece en el documento. Cuando el proveedor es una sociedad
(S.L., S.A...), su CIF y su razón social no se consideran datos personales
por sí mismos.

### Con qué finalidad

Registrar y comprobar automáticamente las facturas recibidas de proveedores,
para facilitar la contabilidad: extraer los datos, comprobar que son
correctos (NIF válido, cuentas cuadradas, dentro del importe máximo...) y
dejar solo los casos dudosos para que una persona los revise.

### Con qué servicios se comparten

- **Google** (Gmail y Google Sheets): el correo con la factura adjunta se
  recibe por Gmail, y los datos ya extraídos se guardan en una hoja de
  cálculo.
- **Anthropic**: el contenido del documento (su texto, o la imagen de la
  página si es un escaneado o una foto) se envía a la API de Claude para
  extraer los datos de la factura.

### El servicio no guarda los documentos

El servicio extractor no escribe los documentos en disco ni los guarda en
ningún sitio: los recibe, los procesa en memoria y devuelve el resultado.
Tampoco escribe el contenido de los documentos en sus registros (logs).

### Cuánto tiempo se conservan

Este proyecto de práctica no implementa ningún borrado automático. Los
plazos de conservación de las facturas los fija la normativa (mercantil,
contable y fiscal), no este sistema: antes de usar esto con facturas reales,
el gestor o asesor fiscal debe confirmar cuánto tiempo hay que conservarlas y
cómo.

### Qué debe revisar un profesional

Como con los leads, antes de usar este sistema con facturas reales una
persona con formación legal y el gestor o asesor fiscal deberían revisar al
menos la base legal del tratamiento, el contrato de encargado de tratamiento
con Google y con Anthropic, y los plazos de conservación exigidos por la
normativa aplicable. Como con el resto de este documento, esto no es
asesoramiento legal.
