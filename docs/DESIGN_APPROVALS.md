# Aprobaciones de diseño

La arquitectura fue aprobada el 23 de octubre de 2026.
Revisión visual 01 preparada y aprobada por el propietario el 24 de octubre de 2026.

El propietario aprobó la revisión 01 de las seis vistas y solicitó levantar el frontend.
Cualquier modificación visual posterior debe identificarse en otra revisión.

## Referencias de revisión

Prototipos y capturas: [design/README.md](../design/README.md).

| Vista | Revisión | Estado | Archivo | SHA-256 del HTML |
|---|---|---|---|---|
| Catálogo y filtros | 01 | Aprobada | [catalog.html](../design/prototypes/catalog.html) | `35eb153cf3863a7acb748a90163e7ddb7313bffdf49c5af59ce8e2e879136a39` |
| Producto (decant y botella completa) | 01 | Aprobada | [product.html](../design/prototypes/product.html) | `32b72f42ce3a7119f1af241af7916655dae77ac081842eb1183401ee92f087f1` |
| Carrito | 01 | Aprobada | [cart.html](../design/prototypes/cart.html) | `1527e023fbbed37b121cf64f2df517e040bb07058a41bd0aa394ee91f6ef40d5` |
| Acceso administrativo | 01 | Aprobada | [login.html](../design/prototypes/login.html) | `ef0e042c89c50fe7776c301e2624fc88c520497732a0725e9e351995f6b9bf75` |
| Administración de catálogo | 01 | Aprobada | [admin-catalog.html](../design/prototypes/admin-catalog.html) | `7d768edf55fb219deda5663f38740db7b01b21946f5fe6d297998307e931d8e0` |
| Inventario y movimientos | 01 | Aprobada | [admin-inventory.html](../design/prototypes/admin-inventory.html) | `4c4bdd61654b12deed65550dd02483a709c8e90e718b8541fe86d75892ca0ce1` |

SHA-256 del conjunto HTML + CSS + JavaScript + fuentes, en el orden indicado arriba:

`c8ccac9dc863a0246246fff27d9e233f028280085b6b2edf6cb2b3379a7e416b`

La huella incorpora las rutas relativas y separadores NUL antes y después de cada contenido.

## Verificación técnica realizada

- 82 pruebas de backend aprobadas; cobertura global 96,53 %.
- Cobertura de ramas de dominio y aplicación: 96,43 %.
- 36 pruebas de prototipos aprobadas en Chromium, Firefox y WebKit.
- Tamaños comprobados: 320, 360, 390, 768, 1024 y 1440 px.
- Capturas de escritorio y móvil generadas con Chromium.
- Verificar técnicamente una vista no constituye aprobación visual del propietario.

## Implementación aprobada

Las seis vistas se integraron en Astro, con sesiones verificadas por Flask,
proxy de un único origen, formularios administrativos e inventario y carrito reales.
Se conservaron la paleta y la composición de la revisión aprobada.

Verificación del frontend: 12 pruebas unitarias y 6 pruebas de aplicación aprobadas,
con Chromium, Firefox y WebKit. La aplicación se verificó con Flask y PostgreSQL
temporales. Tipos, lint, compilación y auditoría de dependencias completados.

La conexión comercial continúa pendiente de backend/.env y de los datos reales
del catálogo, el teléfono de WhatsApp y los archivos originales de marca.

## Revisión 02: catálogo importado

Solicitada el 25 de octubre de 2026. Estado: no aprobada por el propietario.
La autorización para crear esta demostración no constituye aprobación de su resultado.

Prototipo: [catalog-import.html](../design/prototypes/catalog-import.html).
Capturas de catálogo, ficha y carrito en escritorio y móvil:
[índice de revisión](../design/README.md#revisión-02-catálogo-importado).

Utiliza 130 perfumes, 400 presentaciones y 132 fotografías del HTML proporcionado,
con filtros, cantidades y carrito simulados mediante HTTP. La fotografía de Delina
está pendiente. Mantiene disponibilidad sin confirmar y no envía compras.

La revisión 01 conserva sus archivos y aprobaciones. La aplicación principal continúa
conectándose a Flask. Excepción, alcance y retirada de los recursos temporales:
[TEMPORARY_CATALOG.md](TEMPORARY_CATALOG.md).

## Revisión 03: simplificación del catálogo

Solicitada el 25 de octubre de 2026. Estado: aprobada por el propietario el 31 de octubre de 2026,
con modificaciones por detallar; cada una se registrará en una revisión posterior.
El propietario confirmó un carrusel de fotografías en el bloque principal.

SHA-256 de los archivos aprobados:

| Archivo | SHA-256 |
|---|---|
| `design/prototypes/catalog-refined.html` | `3673ab593cc3d6eff667a131e1894415d6359f39e9970513e2a719a9cb5d45cf` |
| `design/assets/catalog-refined.css` | `bdc585ca238e7327aa0069050952311619551a79496442e908f5cb7cffad9d8e` |
| `design/assets/catalog-refined.js` | `91b33b243fe929741532c29e55b3d63b02b11f6b10a94839895e8149b7698239` |

Prototipo: [catalog-refined.html](../design/prototypes/catalog-refined.html), servido en
http://localhost:4321/temporal/. La revisión 02 se conserva en
http://localhost:4321/temporal/catalog-import.html.

Cambios sometidos a revisión: cabecera, bloque principal y pie negros; carrusel manual;
selección de presentación y agregado desde tarjetas; resumen automático y continuación
WhatsApp simulada; controles amplios, accesibilidad y armonización CSS de fondos de fotografías.
No se modificaron las vistas de la aplicación principal conectada a Flask.

Referencias visuales y recorrido medido de tres acciones:
[índice de revisión 03](../design/README.md#revisión-03-recorrido-y-controles).
Nueve pruebas de navegador de esta revisión aprobadas. Tipos, lint y compilación sin errores.


## Revisión 04: checkout, seguimiento y administración

Preparada el 27 de octubre de 2026. Decisiones del propietario el 31 de octubre de 2026:

| Vista | Decisión |
|---|---|
| `checkout.html` (datos y envío) | Aprobada. |
| `order-tracking.html` (pedido recibido y seguimiento) | Aprobada; el diálogo de recuperación cambia por la decisión descrita en la revisión 05. |
| `admin-media.html` (biblioteca de fotografías) | Aprobada. |
| `admin-orders.html` (gestión de pedidos) | Aprobada; se retira la pestaña de recuperación de códigos (revisión 05). |
| `admin-settings.html` (configuración) | No aprobada: la pestaña de catálogo mezclaba conceptos. Rehecha en la revisión 05. |

La huella conjunta siguiente corresponde a la preparación original del 27 de octubre y ya no
es reproducible, porque los archivos modificados por la revisión 05 comparten fuentes con ella.
SHA-256 de los archivos aprobados sin modificación posterior:

| Archivo | SHA-256 |
|---|---|
| `design/prototypes/checkout.html` | `9a9217c4df9dfdbdb71db54f6311264785121c596e5ed81f0d691b5919c14ce2` |
| `design/prototypes/admin-media.html` | `b8dd2c4232020ad9fc4561fff7167176d375b368f64d91881d44145a32306570` |
| `design/assets/checkout.css` | `5b8027bcc5c43cad956b25fd112c0bbd6b3e565d1632fc7d82ac23f401641a8a` |
| `design/assets/admin-commerce.css` | `290346e6fdb44b867acea8c49f76d10cca8d347fe5b5da9becb3ee3ea38cdb35` |

Vistas: `checkout.html`, `order-tracking.html`, `admin-settings.html`, `admin-media.html`
y `admin-orders.html`. Apertura e interacciones: [design/README.md](../design/README.md).
Las rutas de revisión leen la semilla y fotografías de `backend/semillas/catalogo/`;
no son páginas Astro comerciales ni envían formularios a la API real.

Huella SHA-256 conjunta de los cinco HTML y cuatro CSS/JS, ordenados por ruta,
con separadores NUL antes y después del contenido:

`187455823a6f1e47e98b948aaacf2ac450f10e795116e5d37dd8a90e5e9a9052`

Fuente de datos de esta revisión (SHA-256 del JSON de semilla):
`cd38e9946fb1771a02f82f27c31f8cd50014a4cc5fa47504c32e94bc729a4256`.

Verificación: 12 pruebas aprobadas entre Chromium, Firefox y WebKit;
anchos 320, 360, 390, 768, 1024 y 1440 px, ES/EN, controles, foco y ausencia de desbordamiento.
Capturas de las cinco vistas a 390 y 1440 px en `design/reviews/commerce-<vista>-<ancho>.png`.
La verificación técnica no constituye aprobación visual.


## Revisión 05: ajustes de la revisión 04

Preparada el 31 de octubre de 2026. Estado: aprobada por el propietario el 31 de octubre de 2026.
Aplica las decisiones del propietario sobre la revisión 04; no modifica la revisión 03.

Configuración (`admin-settings.html`), pestañas separadas por concepto:
- Categorías: agrupan casas comerciales (árabe, diseñador, nicho). Cada categoría muestra sus
  casas y cada casa pertenece a una sola categoría; sus perfumes la heredan.
- Género: mujer, hombre y unisex, separado de las categorías.
- Acordes, Tipo de uso y Perfil olfativo: listas propias, sin valores precargados. Los nombres
  de pestaña "Tipo de uso" y "Perfil olfativo" son propuestas pendientes de confirmar.
- Presentaciones en ml: pestaña propia, con nombres ES/EN.
- Envíos, Bancos y contacto y Estados: sin cambios.

Gestión de pedidos (`admin-orders.html`): se retira la pestaña de recuperación de códigos.
Seguimiento (`order-tracking.html`): la recuperación verifica la cédula y anuncia el envío del
código al correo registrado, con respuesta uniforme. El tiempo de espera de 10 minutos entre
reenvíos no se representa todavía: está pendiente de confirmar su alcance.

La semilla corrige el nombre de la categoría "Árabe" (antes "Arábe").

SHA-256 de los archivos modificados:

| Archivo | SHA-256 |
|---|---|
| `design/prototypes/admin-settings.html` | `090ddb6de4489bc0b8ca01a3f1e288e840518238fe8f1c9eddd2636892804f8d` |
| `design/prototypes/admin-orders.html` | `2f913300ac2f082780a8955565a7ce290df386d479894810e970252aaad88535` |
| `design/prototypes/order-tracking.html` | `fb93010c41a711ae6929c39f144512f5e472811a10ecf10389859b0bc5fe8480` |
| `design/assets/checkout.js` | `95601402124a877acb238c5ffc6d0dd5cdfd4ed803487857fecdd60e132032a6` |
| `design/assets/admin-commerce.js` | `a41bae6626e68e838e21b5579c4b5910c9464f51318900680dfb34fba568a65e` |
| `backend/semillas/catalogo/catalogo.json` | `34aa443bfd3bfac7d6172937dcf7a7178fd339257fe3a51a8cc48c9788f9e764` |

Verificación del prototipo: 12 pruebas de navegador aprobadas en Chromium, Firefox y WebKit; anchos
320, 360, 390, 768, 1024 y 1440 px, ES/EN y sin desbordamiento. Capturas regeneradas en
`design/reviews/commerce-<vista>-<390|1440>.png`.

## Implementación de las revisiones 04 y 05

El 31 de octubre de 2026 el propietario aprobó las revisiones 04 y 05 y pidió implementarlas.
Se integraron en Astro, con backend completo y probado, las cinco vistas: checkout, pedido recibido
y seguimiento, biblioteca de fotografías, gestión de pedidos y configuración. Diferencias respecto
de los prototipos, por no existir su equivalente en la aplicación:

- La configuración reemplaza el selector de escenarios por datos reales de la API y crea los
  identificadores (slug) a partir del nombre.
- La biblioteca vincula una fotografía a un perfume desde su diálogo de detalle, en lugar del
  selector de hasta cinco fotografías del prototipo.
- El resumen del checkout muestra texto sin fotografía, igual que el carrito aprobado.
- Si el propietario no configuró el WhatsApp comercial, el pago por WhatsApp se deshabilita.
- El carrito añade el enlace "Continuar con la compra" hacia el checkout.
- La navegación administrativa incorpora Pedidos, Biblioteca y Configuración.
- El editor de perfumes (revisión 01) recibe el género y la categoría de la casa desde la API;
  la asignación de acordes, tipos de uso y perfiles al perfume y sus filtros públicos requieren un
  prototipo que todavía no existe.

La revisión 03 se implementó mediante la revisión 06.


## Revisión 06: tienda unificada de las revisiones 03, 04 y 05

Solicitada y preparada el 31 de octubre de 2026 como un prototipo único que unía el catálogo
negro de la revisión 03 con el checkout, el seguimiento y la administración de las revisiones 04
y 05. El propietario la aprobó el 31 de octubre de 2026 y pidió implementarla y retirar el
prototipo temporal; sus archivos, capturas y pruebas se eliminaron tras la implementación.
Los prototipos de las revisiones 03 a 05 se conservan como referencia en `design/`.

Decisiones aprobadas e implementadas en Astro (`frontend/src/`):

- Cabecera, franja de envíos y pie negros en toda la tienda, con "Mi pedido" en la cabecera y
  "Acceso administrativo" en el pie. La administración conserva su navegación lateral negra.
- Bloque principal negro con carrusel manual (flechas, indicadores, teclado y gesto táctil, sin
  avance automático) con perfumes que tienen fotografía; sin fotografías muestra la ilustración.
- Tarjetas con presentaciones visibles, precio por tamaño, cantidad con botones SVG y
  "Agregar" directo; una presentación agotada deshabilita su botón.
- Un solo carrito, abierto como diálogo desde la cabecera, la barra flotante o al agregar.
  "Continuar con la compra" es la acción principal; "Continuar por WhatsApp" queda como
  secundaria y revisa precios y disponibilidad antes de abrir WhatsApp.
- Checkout y seguimiento comparten cabecera y pie; el primer paso del checkout vuelve al catálogo.

Diferencias respecto del prototipo, por no existir su equivalente en la aplicación:

- Los datos proceden de la API real: sin la línea de totales del catálogo importado ni disponibilidad
  "por confirmar"; la disponibilidad es la del backend.
- El resumen de WhatsApp simulado y copiable se sustituye por el enlace real configurado por el
  propietario; sin teléfono configurado, el botón se deshabilita con aviso.
- La ficha del perfume sigue siendo una página (`/products/<slug>`), con el mismo pie, cabecera y
  apertura del carrito al agregar, en lugar del diálogo del prototipo.
- Se retiró la página `/cart`; el carrito vive en el diálogo.
- Los filtros móviles conservan el panel lateral de la revisión 01.

Verificación: 24 pruebas de navegador de la aplicación real (Flask y PostgreSQL temporales) en
Chromium, Firefox y WebKit, incluidas las del catálogo, el carrito y el checkout; tipos, lint y
formato sin errores.
