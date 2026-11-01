# Recursos temporales del catálogo BÉRONT

Conservar estos archivos hasta completar su carga en el backend real.

- `catalog.json`: 130 perfumes y 400 presentaciones extraídos del HTML del propietario.
- `media/`: 132 fotografías WebP locales, consumidas mediante URLs HTTP.
- Prototipo: http://localhost:4321/temporal/ con `bun.cmd run dev` desde `frontend/`.

La URL principal muestra la revisión 03, pendiente de aprobación visual.
La revisión 02, no aprobada, se conserva en /temporal/catalog-import.html.
La nueva revisión muestra un resumen de WhatsApp simulado sin enviar mensajes.

No constituyen inventario confirmado. No habilitan compras reales ni alteran PostgreSQL.
El catálogo principal y su API real permanecen separados de esta demostración.
Una fotografía, Delina Eau de Parfum, sigue pendiente porque su URL respondió HTTP 403.

Procedencia, límites y pasos de sustitución: [docs/TEMPORARY_CATALOG.md](../../../docs/TEMPORARY_CATALOG.md).
La excepción temporal fue solicitada por el propietario el 25 de octubre de 2026.
