# Informe de evaluación del extractor

- Documentos evaluados: 25
- Modelo: claude-haiku-5-5

## Acierto por campo

| Campo | Aciertos | Comparados | % |
| --- | --- | --- | --- |
| proveedor | 21 | 25 | 84.0% |
| nif_proveedor | 21 | 25 | 84.0% |
| numero | 22 | 25 | 88.0% |
| fecha | 23 | 25 | 92.0% |
| total | 22 | 24 | 91.7% |

## Tasa de proceso automático

14 de 18 facturas correctas se aprobaron solas (77.8%).

## Falsos aprobados

0 (deben ser 0)

## Tiempo medio

1565 ms por documento

## Tokens medios por documento

- Entrada: 2343 tokens
- Salida: 290 tokens

## Coste

No hay precios configurados (PRECIO_ENTRADA_EUR_MTOK / PRECIO_SALIDA_EUR_MTOK), así que no se calcula el coste.

## Estado esperado frente a estado obtenido

| Esperado \ Obtenido | aprobado | revision | rechazado |
| --- | --- | --- | --- |
| aprobado | 14 | 4 | 0 |
| revision | 0 | 5 | 0 |
| rechazado | 0 | 0 | 2 |
