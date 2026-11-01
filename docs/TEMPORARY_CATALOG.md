# Catálogo temporal importado

Estado: demostración local solicitada el 25 de octubre de 2026. Revisión visual 02
no aprobada; revisión 03 pendiente de aprobación. No sustituye las vistas aprobadas
ni el catálogo comercial.

## Abrir

Desde `frontend/`, ejecutar `bun.cmd run dev` y abrir
[el prototipo](http://localhost:4321/temporal/).
Esta URL sirve la revisión 03. La revisión 02 se conserva en
http://localhost:4321/temporal/catalog-import.html.

No necesita Flask ni credenciales PostgreSQL. El catálogo principal de `/es/` y `/en/`
continúa utilizando el backend real. La administración sigue exigiendo su sesión real.

## Origen y conversión

Archivo del propietario: `C:\Users\juanr\Downloads\index (3).html`.
Su SHA-256 se conserva en `frontend/public/temporal/catalog.json`, campo `source.sha256`.
El archivo original permanece intacto. No se ejecutaron ni copiaron sus scripts,
instrucciones, enlaces de compra o teléfono al prototipo.

Conversión local mediante `base64.b64decode` de Python y Pillow, ya instalado:
decodificación validada, comprobación de imagen, orientación EXIF, recodificación WebP
con calidad 95 y eliminación de metadatos. Sin recortes, fotografías generadas ni
dependencias adicionales. El nombre de cada fotografía deriva del SHA-256 de su original.

Resultado:

| Elemento | Cantidad |
|---|---:|
| Fichas del HTML | 143 |
| Perfumes después de agrupar coincidencias exactas de casa y nombre | 130 |
| Perfumes con decants | 119 |
| Perfumes con botellas completas | 24 |
| Presentaciones con precio propio | 400 |
| Fotografías distintas extraídas de base64 | 122 |
| Fotografías enlazadas en el HTML y guardadas localmente | 10 |
| Archivos WebP locales | 132 |
| Perfumes sin fotografía accesible | 1 |

Los apartados comparten 13 perfumes. Los identificadores temporales son UUID derivados
del contenido; no son identificadores ya registrados en PostgreSQL. `source_rows` permite
relacionar cada perfume con sus fichas originales. No se dedujeron equivalencias entre
nombres diferentes, precios por ml, géneros, categorías o inventario.

Se conservaron todos los tamaños del HTML, incluidos 1, 20 y 30 ml. Los importes se
almacenan como cadenas decimales. Los selectores de cantidad del HTML no representan
existencias: todas las fichas mantienen `stock_status: unknown` y muestran
«Consultar disponibilidad».

La fotografía enlazada de **Parfums de Marly Delina Eau de Parfum** respondió HTTP 403.
Su ficha conserva tamaños y precios y muestra «Fotografía pendiente». El URL original y
el resultado de las descargas se encuentran en `issues` del JSON. No se sustituyó por
una fotografía de otro perfume.

## Flujo simulado

```text
design/prototypes/catalog-refined.html
    -> fetch /temporal/api/v1/catalog/products?... + facets + overview
    -> ruta Astro temporal
    -> adaptador de consultas -> catalog.json
    -> JSON con URLs /temporal/media/<hash>.webp
    -> navegador solicita esas URLs
    -> frontend/public/temporal/media/<hash>.webp

Selección de tamaños y cantidades
    -> carrito separado, solo variant_id y quantity
    -> POST /temporal/api/v1/cart/quote
    -> importes del JSON y cálculo exacto mediante enteros de centavos
    -> resumen sin reserva, descuento de inventario o conversación WhatsApp
```

La API temporal usa peticiones HTTP reales al servidor Astro, sin contactar Flask.
El navegador no carga base64 ni solicita imágenes a sitios externos. Todas las imágenes
se resuelven mediante URLs locales, como ocurrirá con el almacenamiento del backend.

Las consultas soportan búsqueda, casa, clasificación, público, tipo, volumen, rango de
precio, orden y paginación. Precio y volumen deben coincidir en la misma presentación.
La ficha consulta el producto completo y permite cambiar entre sus presentaciones.

La cotización no acepta precios del navegador, consolida presentaciones repetidas,
admite como máximo 20 presentaciones y 20 unidades por presentación y rechaza datos
inválidos. No comprueba inventario porque la fuente no lo proporciona.

La revisión 02 mantiene WhatsApp deshabilitado. La revisión 03 abre una vista simulada
del resumen que permite copiar texto; no configura un teléfono ni envía mensajes.
El carrito utiliza
`beront.temporary-cart.v1`, separado de `beront.cart.v1`; si el navegador bloquea
localStorage, la selección funciona durante la sesión de la página.

El servidor del prototipo está limitado a desarrollo mediante `import.meta.env.DEV`.
Los archivos de `public/temporal/` son recursos estáticos y se copian al compilar:
deben retirarse junto con la demostración cuando termine su uso.

## Archivos y responsabilidades

| Ubicación | Función |
|---|---|
| `frontend/public/temporal/catalog.json` | Datos importados, procedencia e incidencias. |
| `frontend/public/temporal/media/` | Fotografías WebP. Conservar hasta migrarlas. |
| `frontend/public/temporal/README.md` | Aviso junto a los recursos. |
| `frontend/src/features/catalog/temporary.ts` | Filtros, detalle y cotización de demostración. |
| `frontend/src/pages/temporal/[...path].ts` | API simulada y entrega de prototipos con rutas fijas. |
| `design/prototypes/catalog-import.html` | Revisión visual importada. |
| `design/assets/catalog-import.js` | Cliente HTTP, filtros, ficha y carrito independientes. |
| `design/assets/catalog-import.css` | Ajustes sobre los tokens aprobados. |
| `design/prototypes/catalog-refined.html` | Revisión 03, con negro, carrusel y acceso directo. |
| `design/assets/catalog-refined.{js,css}` | Interacción y presentación de la revisión 03. |
| `design/reviews/catalog-import-*.png` | Capturas de catálogo, ficha y carrito. |
| `design/reviews/catalog-refined-*.png` | Capturas de la revisión 03. |
| `frontend/tests/unit/temporary-catalog.test.ts` | Importes, filtros, límites y ausencia de cambios de datos. |
| `frontend/tests/e2e/temporary-catalog.spec.ts` | Interacción y contratos en tres navegadores. |
| `frontend/tests/e2e/temporary-refined.spec.ts` | Tres acciones, carrusel, teclado y responsividad. |

La revisión 03 aplica mezcla CSS y compensación visual de fondos claros neutros mediante
una medición de los bordes de cada imagen local. No modifica los 132 archivos WebP,
sus identificadores ni sus rutas; esta presentación pertenece al prototipo y debe revisarse
con las fotografías definitivas antes de aplicarse al producto principal.

La excepción autorizada está registrada en `docs/ARCHITECTURE.md`. Las fotografías
y el JSON se mantienen por solicitud del propietario, aunque su finalidad sea temporal;
no deben eliminarse como archivos exploratorios al cerrar esta tarea.

## Sustituir por el backend real

El backend ya tiene endpoints de catálogo, fotografías, inventario y carrito. La tarea
pendiente para estos datos es cargarlos y conectar su catálogo comercial, no crear un
segundo esquema o persistencia paralela.

1. Revisar con el propietario los productos, precios y categorías importados y aportar
   la fotografía pendiente de Delina. No usar la fecha del HTML como garantía de vigencia.
2. Crear casas, productos y presentaciones mediante la API administrativa autenticada,
   respetando CSRF, validaciones y permisos. No copiar el JSON a tablas manualmente.
   Si hiciera falta un cambio de esquema, usar modelos SQLAlchemy y Alembic.
3. Conservar una correspondencia de UUID temporales a los UUID reales devueltos por
   la API. Comprobar cada tamaño y precio y no duplicar perfumes compartidos entre apartados.
4. Subir cada WebP mediante `POST /api/v1/admin/products/{id}/images`. El backend volverá
   a validar, normalizar y almacenar cada imagen. Guardar sus textos alternativos y orden.
   Utilizar la URL `/media/<archivo>.webp` devuelta por el backend, sin construirla desde
   el nombre temporal ni relajar `mediaUrl` del frontend principal.
5. Registrar existencias reales por ml o unidades mediante ajustes de inventario con
   motivo e idempotencia. La disponibilidad desconocida de la demostración no autoriza
   publicar inventario positivo o quitar marcas de agotado.
6. Configurar y arrancar Flask y verificar `/api/v1/catalog/products`, `/catalog/facets`,
   `/media/` y `/cart/quote` desde el frontend principal. La aplicación principal ya usa
   esos contratos; no cambiar sus URLs al prefijo temporal.
7. Revisar en las vistas reales las fotografías, idiomas, tamaños, filtros, precios,
   agotados y carrito. Configurar el teléfono comercial para habilitar WhatsApp real.
   La cotización real debe comprobar stock y seguir sin descontarlo al abrir WhatsApp.
8. Tras verificar la carga y conservar las fotografías originales, retirar el adaptador,
   la ruta y `frontend/public/temporal/`. Eliminar la excepción `temporal` del middleware,
   las pruebas exclusivas de esta demostración y su selector de Playwright.
   Limpiar únicamente `beront.temporary-cart.v1` del navegador; no borrar el carrito real.
   Los prototipos y capturas pueden conservarse como referencia dentro de `design/`.
9. Actualizar este documento a «retirado», registrar la revisión aprobada y ejecutar
   tipos, lint, compilación y pruebas de la aplicación conectada. Verificar que no queden
   imports o URLs temporales en el producto final.

## Verificación de esta revisión

- 16 pruebas unitarias aprobadas, incluidas cuatro de la simulación.
- Seis pruebas de la revisión 02 y nueve de la revisión 03 aprobadas en Chromium, Firefox y WebKit.
- Revisados 320, 360, 390, 768, 1024 y 1440 px, incluyendo ficha y carrito sin desbordamientos.
- Los 132 archivos de imagen responden correctamente como WebP.
- Confirmado que el prototipo no solicita `/api/v1/` real ni imágenes externas.
- Tipos, lint y compilación del frontend sin errores.

Para repetir las pruebas de navegador con el frontend levantado, desde `frontend/`:

```powershell
$env:BERONT_TEMPORARY_BASE_URL = 'http://localhost:4321'
bun.cmd x --bun playwright test
Remove-Item Env:\BERONT_TEMPORARY_BASE_URL
```
