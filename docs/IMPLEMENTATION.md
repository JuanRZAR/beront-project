# Ampliación de BÉRONT: implementación y cumplimiento

## Semilla canónica y base local nueva, 14 de noviembre de 2026

Por instrucción del propietario, la lista del catálogo final de Decants pasa a ser la fuente
de la semilla: 127 perfumes, 43 marcas, 425 presentaciones y 133 imágenes (127 principales y
seis adicionales). Se reemplaza el JSON anterior y sus 132 fotos dentro de
`backend/semillas/catalogo/`. Los nuevos WebP proceden de `backend/var/uploads/` y conservan
exactamente los bytes, dimensiones y transparencia que tenía el proyecto final. No se borran
las fotografías del almacenamiento del propietario ni los maestros de diseño.

La semilla v2 incluye SHA-256 y metadatos por foto; el cargador rechaza archivos modificados,
opacos, faltantes o sin asociación. El importador conserva las nueve presentaciones inactivas
y los precios existentes en la captura del catálogo. La instalación nueva no depende de diseño
ni requiere `importar-recortes`; se corrigen dos referencias antiguas de la semilla del Home.

Se revisa que `beront-bd2` esté vacía y se aplican las cuatro migraciones existentes hasta
`de252c02c932`; Alembic no detecta diferencias con los modelos. Se conserva el administrador
local con sus credenciales actuales, sin copiar sesiones ni incluir credenciales en archivos
de semilla. Se importan los 127 perfumes y 133 fotos y se inicializan seis mensajes del Home.
Todos los saldos empiezan en cero, sin movimientos. `DATABASE_URL` y `MIGRATION_DATABASE_URL`
de `backend/.env` apuntan a `beront-bd2`; las demás variables se conservan. La base anterior
no se modifica y los servidores del propietario no se reinician.

Verificación: 187 pruebas de backend aprobadas con PostgreSQL y almacenamiento temporales;
Ruff y formato correctos. La prueba completa de semilla compara las 133 respuestas de medios
con SHA-256 y comprueba la repetición sin perder cambios administrativos. En `beront-bd2`
se comprueban de nuevo los 127 nombres, sus presentaciones, los 133 archivos HTTP exactos,
transparencia y saldos cero. La normalización de las 133 fuentes conserva sus bytes.
La aplicación habitual leerá la nueva base cuando el propietario reinicie su backend.

## Carrito: fotos vigentes y decants animados, 13 de noviembre de 2026

El propietario solicita mostrar la foto del perfume en los completos y la foto junto al decant
animado en los decants, sobre el diálogo existente mostrado en su captura. Se integra ese ajuste
puntual en `features/cart/dialog.ts`, reutilizando `image_url` ya devuelto por la cotización.
No cambia el backend, la persistencia, los precios, las cantidades ni el resumen de WhatsApp.

Cada completo muestra solo su fotografía; cada decant añade el mini frasco SVG, con color de
la foto, llenado y ondas. El nivel responde a los ml elegidos y se respeta movimiento reducido.
Las fotos conservan su proporción con object-fit: contain y texto alternativo. Sin foto o con
error se indica su ausencia, sin sustituir el completo por un decant. El diálogo usa su Container
Query existente: foto y decant al lado en escritorio, apilados en compacto para dejar espacio
a los controles. Las acciones, precios y cantidades se conservan.

Verificación del ajuste: 12 escenarios en Chromium, Firefox y WebKit aprobados, con fotos
cargadas desde el backend temporal, ausencia de mini vial en completos, animación/nivel según ml,
movimiento reducido y recuperación ante foto fallida. Se recorren 320/360/390/768/1024/1440/1920/2560
px con texto normal y ampliado, sin desbordamientos ni superposición entre fotos y controles.
Astro check, ESLint, formato, build y 27 pruebas unitarias de frontend correctos.
Revisado también en Chrome con Dunescape y Odyssey Mandarin Sky completos, y Arabian Sky y
Bacio Immortale en decants: cuatro fotos, dos mini frascos y total $170.24 conservado. Los
servidores habituales no se reiniciaron; las pruebas temporales cerraron sus procesos y base.
No se verificaron dispositivos físicos.


## Resumen legible de WhatsApp y catálogo abierto, 13 de noviembre de 2026

El propietario solicita que no aparezca ningún agotado y separar claramente los productos
en WhatsApp. Se consulta el catálogo completo vigente: 127 decants y 17 completos, todas sus
presentaciones disponibles para solicitar en el modo abierto. No se modifican existencias ni
marcas manuales; una pestaña antigua mostraba datos y navegación previos. Se abre Decants
actualizado en Chrome conservando los siete artículos del carrito del propietario.

WhatsAppLinkBuilder genera bloques numerados, con líneas para marca/modelo, presentación en ml,
cantidad, precio unitario y subtotal. Una línea en blanco separa productos; el total se destaca
al final, seguido de envío no incluido y confirmación de disponibilidad. Se mantienen ES/EN,
codificación del enlace, Decimal y recotización desde el backend. No se envían mensajes.

Verificación de este ajuste: 49 pruebas de backend y seis escenarios de navegador aprobados
en Chromium, Firefox y WebKit; Ruff, ESLint y formato correctos. Las siete páginas vigentes
del catálogo no contienen etiquetas Agotado. El propietario autorizó reiniciar solo el backend
5000 y el nuevo texto quedó activo. Se verificó mediante el proxy del frontend 4322 con dos
productos reales, bloques separados y total $94.95. Frontend y carrito del propietario
conservados; no se abrió WhatsApp ni se envió ningún mensaje.


## Carrito y solicitudes por WhatsApp, 13 de noviembre de 2026

Se conecta el carrito aprobado en catálogos y fichas con la cotización existente del backend.
El propietario autoriza temporalmente solicitudes sin cantidades de inventario: configuración
`CART_REQUIRES_STOCK=false`, con validación de publicación, actividad y agotado manual vigente.
La validación estricta sigue siendo el valor predeterminado y se conserva para checkout y pedidos.
El número se guarda mediante CommerceService, con auditoría, como `593939237376`; se conservan
los términos. No hay migraciones, dependencias nuevas ni cambios de inventario.

El frontend mantiene el menú de tres secciones y habilita carrito con `PUBLIC_CART_ENABLED`.
Se reutilizan persistencia de identificadores/cantidades, resumen, controles de cantidad y
eliminación, recotización y manejo de cambios de precio. En el perfil limitado, WhatsApp sustituye
la continuación a checkout. El enlace incluye los importes determinados por el backend y una
nota de disponibilidad/envío por confirmar; el mensaje se envía manualmente desde WhatsApp.


Verificación: 80 pruebas de backend (configuración, carrito/inventario, comercio, pedidos,
catálogo y seguridad), 27 unitarias de frontend y 15 escenarios integrados en Chromium,
Firefox y WebKit. El perfil WhatsApp recorre 320/360/390/768/1024/1440/1920/2560 px;
verifica cantidades, eliminación, persistencia ES/EN, total, enlace y nota de confirmación,
con navegación a WhatsApp interceptada. Pasan Astro check, ESLint, formato, Ruff y build.
No se verificaron dispositivos físicos. Las pruebas usaron bases y servidores temporales.

Activación local autorizada: backend 5000 reiniciado; frontend 4322 conservado. Se corrigió
FRONTEND_ORIGIN de localhost:4321 a localhost:4322 para aceptar el origen real de la tienda.
Comprobación adicional sobre la API real: decant Afnan 9 AM Dive 3 ml ($4.95) y completo
Amber Oud Gold Edition 120 ml ($90), total $94.95, enlace al número configurado. Chrome
verifica agregar, incrementar ($90 a $180), eliminar y WhatsApp habilitado; se retira el
producto de prueba del carrito. No se envían mensajes ni se modifican existencias.

## Oferta de perfumes completos, 10 de noviembre de 2026

Por indicación del propietario, la sección de completos pasa a tener 12 perfumes. Se aplicó
en la base local `beront-bd` mediante `CatalogService`, con auditoría y control de versión,
sin SQL directo ni cambios de esquema: presentación de completo de 120 ml; marcas Bharara
(Árabe) y Billie Eilish (Diseñador); perfumes nuevos Armaf Dunescape y Odyssey Mandarin Sky
Vintage Edition, Bharara King, Billie Eilish Eilish No. 2 y Lattafa Khamrah Qahwa, publicados
sin descripción ni fotografía; completos añadidos a Stronger With You Intensely, Amber Oud
Gold Edition (120 ml), Club de Nuit Intense Man (200 ml) y Yara Candy; nuevos precios de
Mandarin Sky, Khamrah Waha y Angham Second Song. Los otros 21 completos se desactivaron (no
se borraron); los 10 perfumes que solo existían como completo quedaron despublicados. Ninguno
tenía pedidos ni existencias. Todas las existencias de completos son cero, por lo que la tienda
los muestra agotados hasta registrar un ajuste de inventario. La API pública devuelve los 12.
Fotografías pendientes de aprobación: ver `docs/DESIGN_APPROVALS.md`.

## Decants nuevos, 11 de noviembre de 2026

Por indicación del propietario, mediante `CatalogService` y con auditoría: Lorenzo Pazzaglia
Speachless (unisex, solo decants) se crea y publica con los precios de Summer Hammer
(3 ml $19.29, 5 ml $30.10, 10 ml $56.99) y fotografía recortada; Lattafa Khamrah Qahwa recibe
los decants de Khamrah (3 ml $3.50, 5 ml $5.25, 10 ml $9.80) y Armaf Dunescape los suyos
(3 ml $5.24, 5 ml $6.74, 10 ml $10.54). Ambos conservan su completo. Las existencias de decants
son cero, como en el resto del catálogo. Evidencia en `design/reviews/decants-nuevos-*`.

Después, Afnan 9 AM Dive (despublicado al retirar su completo) recibe decants de 3 ml $4.95,
5 ml $6.25 y 10 ml $9.55 y vuelve a publicarse; su completo sigue desactivado. Se crea y publica
Jo Milano Paris Game of Spades Emerald (unisex, solo decants): 3 ml $7.85, 5 ml $10.90,
10 ml $18.65. Bharara King (3 ml $6.26, 5 ml $8.40, 10 ml $13.77) y Armaf Odyssey Mandarin
Sky Vintage Edition (3 ml $5.45, 5 ml $7.26, 10 ml $11.56) reciben decants y conservan su completo.
Lo mismo Lattafa Angham Second Song: 3 ml $5.78, 5 ml $7.61, 10 ml $12.24.

## Selector del Home, 9 de noviembre de 2026

El propietario solicita juntar los iconos de completos. El patrón pasa a cuatro columnas
uniformes con ocho apariciones de sus cuatro motivos, conservando escala y opacidad. Se reduce
a la mitad la distancia horizontal media. Prototipo y recurso público idénticos; pasan 72
comprobaciones en tres motores, seis anchos y dos tamaños de texto, enlace y build. Evidencias
`design/reviews/home-bottles-density-*`; sin cambios de código o datos comerciales.

El fondo de «Perfumes completos» se sustituye posteriormente por cuatro iconos basados en las
fotografías del propietario: tapa en punta y placa trapezoidal, torso con franjas y atomizador,
frasco redondeado con picos y trofeo con asas. Todos son SVG de trazo champán, sin fotografías
incrustadas. Se revisa primero el patrón del prototipo y se copia idéntico al recurso público
existente. Pasan 240 comprobaciones de prototipo/aplicación, ES/EN, tres motores, diez anchos
y dos tamaños de texto; enlaces y build correctos. Evidencias `design/reviews/home-four-bottles-*`.
No cambia el código, el backend ni los datos comerciales; no se probaron dispositivos físicos.

El patrón de decants se redibuja posteriormente siguiendo la fotografía aportada por el
propietario: pulsador con orificio visible, cuello ancho, vidrio alargado, resorte y tubo curvo.
Se conserva el SVG decorativo champán y su repetición, actualizando primero el recurso del
prototipo y después su copia pública. Pasan 120 comprobaciones de prototipo/aplicación en tres
motores, diez anchos y dos tamaños de texto; enlace y build correctos. Evidencias
`design/reviews/home-decant-reference-*`. Sin cambios de código, backend o datos comerciales.

Revisión posterior: texto de ambas tarjetas centrado y fotografías sustituidas por patrones SVG
en champán. Decants usa varios atomizadores; completos usa torso, cilindro y frasco con picos,
sin marcas. Prototipo actualizado primero; recursos idénticos en `design/assets/` y
`frontend/public/brand/`, coloreados mediante el token existente. Los adornos no intervienen
en el foco ni en la lectura accesible. El catálogo sigue aportando cifras y precio mínimo.
Pasan 360 comprobaciones del selector y 12 de alto contraste en tres motores, teclado y
navegación, además de Astro, ESLint, formato y compilación. Capturas a 390/1440 px y resultados
en `design/reviews/home-category-patterns-*`. Se corrige la cabecera del simulador para que
reorganice sus controles por debajo de 1200 px. La pasada final no detecta desbordamiento
horizontal en prototipo ni aplicación. Home real actualizado abierto en Chrome. No se probaron
dispositivos físicos; los servidores del propietario mantienen sus procesos.

El bloque de acceso al catálogo pregunta «¿Qué estás buscando hoy?» y presenta dos tarjetas:
Decants y Perfumes completos, con fotografías sin fondo y cifras del backend. Se actualizan
prototipo y traducción EN; la cuadrícula usa dos columnas desde 600 px y una en móvil.
Pedidos y carrito conservan sus accesos de navegación. No cambia el backend ni sus datos.

Verificadas 360 combinaciones de prototipo/aplicación en tres motores, ES/EN, 15 anchos y
texto normal/XL, más navegación a ambos catálogos. Astro, ESLint y compilación correctos.
Evidencias `design/reviews/home-choice-*`. Se abre el bloque real en Chrome sin reiniciar servidores.

## Home integrado, 9 de noviembre de 2026

El inicio ahora carga `HomePage.astro` en ES/EN con el carrusel aprobado: cinco mensajes activos,
flechas, indicadores, pausa, teclado, cinta de marcas y accesos a decants, completos, pedidos y
carrito. Se usan recortes R02 sin marcos ovalados. Las cifras, marcas y muestras proceden del
catálogo; no hay precios nuevos ni ofertas inventadas. La promoción de ejemplo está desactivada.

Backend completo antes del frontend: modelos de mensajes y fotos en `commerce`, funciones SQL,
validación de enlaces y fechas, permisos `commerce:write`, CSRF, versiones, auditoría y control
de visibilidad de medios. La migración `de252c02c932` se generó desde modelos, revisó y aplicó;
Alembic no detecta diferencias. `beront inicializar-home` creó seis mensajes sin tocar catálogo,
precios o inventario y conserva las ediciones cuando se repite. Configuración incorpora la
pestaña «Inicio y mensajes» para texto ES/EN, imágenes de biblioteca, enlaces, orden y vigencia.

Verificados: suite de 157 pruebas de backend más una de migración posterior; 27 unitarias y
57 pruebas de navegador aprobadas. Astro, ESLint, Prettier, Ruff y compilación correctos.
Revisión adicional de lectura con el backend real: 900 combinaciones de idioma/ancho/texto/mensaje
en los tres motores. Las nueve fotos del carrusel conservan todos los píxeles RGBA de los PNG
aprobados. Recuentos: 130 perfumes, 400 variantes, 154 saldos y cero movimientos. Evidencia:
`design/reviews/home-implemented-*`. Capturas revisadas en móvil y escritorio.

El propietario autorizó reiniciar únicamente el backend 5000 y se activó el Home. El frontend
4322 permanece en su proceso existente. El Home real quedó abierto en Chrome. La preservación
de alfa para nuevas subidas, pendiente de un arranque desde la integración R02, también queda
cargada. Los servidores y bases de pruebas se retiran al cerrar; no se usaron datos comerciales
para las pruebas que escriben. No se probaron dispositivos físicos ni lectores de pantalla.

## Ajuste de decants del 8 de noviembre de 2026

Por indicación visual del propietario se intercambian las columnas del estudio: selección y
filtros a la izquierda, fotografía y frasco animado a la derecha desde 840 px. En móvil se mantiene
el frasco arriba y la lista debajo. Se actualiza primero el prototipo R02 y se registra la aprobación.
El ajuste usa las áreas del Grid existente; conserva proporciones, controles y comportamiento.

Verificados prototipo y aplicación: 180 combinaciones de ancho/texto en Chromium, Firefox y
WebKit, más selección por teclado, filtros y nivel del líquido. Astro sin diagnósticos, ESLint,
Prettier y compilación correctos. Evidencias `design/reviews/decants-left-selection-*`.
Las comprobaciones usan un frontend separado contra el backend existente y no escriben datos.

## Actualización del 8 de noviembre de 2026: Inkscape R02

El propietario aprueba e integra los recortes de solo frascos. Se aplicaron 132 PNG maestros a
135 vínculos de 129 perfumes del catálogo local mediante `beront importar-recortes`. El proceso
valida las huellas aprobadas, reemplaza los vínculos en una transacción, conserva orden y textos
alternativos, rechaza asociaciones cambiadas y omite las ya aplicadas. Los originales siguen en
la biblioteca y en la semilla. Delina permanece sin foto original.

El almacenamiento conserva el alfa con WebP sin pérdida y RGBA exacto, manteniendo el contrato
de medios y sin cambios de esquema o dependencias. El frontend usa estos recursos en carrusel,
decants, ficha y carrito; se retiran fondos ovalados, filtros de brillo y mezcla de color. La
extracción del color ambiental del decant ignora píxeles invisibles y pondera la transparencia.

Verificados los 132 derivados contra sus PNG: igualdad de todos los píxeles RGBA. Se compararon
antes/después los productos, variantes, precios, 154 saldos, movimientos, posiciones, etiquetas
y huellas de los 132 originales: sin cambios fuera de los vínculos previstos. Validación posterior:
135 ya aplicados. Evidencia en `design/reviews/implemented-r02-data-check.json`.

Pruebas ejecutadas: 152 de backend, Ruff, `astro check` sin diagnósticos, ESLint, Prettier,
compilación y 27 unitarias del frontend. Las 48 pruebas de navegador pasan en Chromium, Firefox
y WebKit usando PostgreSQL, API y frontend temporales. La prueba nueva carga un PNG con alfa por
la administración y verifica transparencia, contención y ausencia de marcos/filtros en 15 anchos
de 320 a 1920 px, con texto normal y muy grande, más la ficha. Se corrigió una espera prematura
de inicio de sesión en esa prueba; la ejecución completa posterior terminó sin fallos.

La aplicación real se abrió en Chrome en `localhost:4322`. No se reiniciaron los servidores del
propietario. El código para futuras cargas con alfa se activará en el siguiente arranque normal
del backend; el importador ya usa el código nuevo y las fotos actuales funcionan en el proceso
existente. La portada de mensajes destacados continúa fuera de esta integración.

Revisión adicional de solo lectura del catálogo real: 360 combinaciones entre carrusel, decants,
frasco ancho y ficha, con 15 anchos y dos tamaños de texto, en los tres motores. Los 132 medios
responden por HTTP y se decodifican con alfa en cada motor; las respuestas se reutilizan para
respetar el límite de peticiones. Delina oculta el espacio de foto vacía. Se revisaron capturas
a 390 y 1440 px de completos, decants y ficha; evidencias `design/reviews/implemented-r02-*`.
No se probaron dispositivos físicos ni lectores de pantalla.

## Actualización del 7 de noviembre de 2026

Se integra la navegación inferior del prototipo aprobado `home-menu-principal.html`: botón
central, panel de tienda, idioma, accesibilidad y administración según sesión y permisos del
backend. Se comparte entre los layouts público y administrativo; el carrito mantiene los accesos
de cabecera, panel y resumen y deja de ocupar la posición flotante central. La portada con
mensajes destacados continúa pendiente del backend; no se añadieron endpoints ni esquema.

El propietario descarta las imágenes sin fondo, incluida la revisión 04 de recortes y sus vistas.
Se actualizan el registro visual, el índice de diseño y la memoria. Las fotos originales y su
presentación actual se conservan; los HTML de recortes quedan como antecedentes descartados.

Verificación ejecutada: `astro check` sin diagnósticos, ESLint, Prettier, compilación, 27 pruebas
unitarias y 45 pruebas de navegador aprobadas en Chromium, Firefox y WebKit. Las nuevas pruebas
comprueban el menú en 14 anchos de 320 a 1920 px, texto muy grande, contraste, movimiento reducido,
teclado/flechas, retorno del foco, cambio de idioma, carrito, permisos y cierre de sesión. La
primera ejecución detectó una salida del foco al recorrer con Tab en Chromium; se corrigió y la
segunda ejecución completa terminó con 45 aprobadas y cero fallos.

Las pruebas de navegador usaron PostgreSQL, API y frontend temporales, eliminados al finalizar;
no usaron datos comerciales. No se probaron dispositivos físicos ni lectores de pantalla.

## Actualización del 2 de noviembre de 2026

Backend y frontend quedaron alineados y el contenido temporal se retiró; ver
[AUDITORIA.md](AUDITORIA.md). Lo anterior en este documento es histórico: las revisiones de
migración `c449e445ed3d` y anteriores se sustituyeron por la migración única `0e7393567f81` y dos
revisiones posteriores, y el editor de perfumes ya asigna acordes, usos y perfiles.

## Actualización del 2 de noviembre de 2026 (estudio de decants)

El propietario aprobó la vista C (Frasco vivo con lista y carrito) y se implementó primero el
backend: `POST /cart/quote` devuelve por línea `product_slug`, `image_url` y `options`, con prueba
de integración. En el frontend: nueva página de decants, carrito con tarjeta por línea (frasco,
mililitros editables, cantidad y total), `CartStore.replace`, panel de accesibilidad (tamaño de
texto, contraste y reducción de animaciones), tipografías en `rem` y verificación en los anchos
320, 390, 600, 768, 840, 1024, 1200, 1440, 1600 y 1920 px. El mismo día se implementó el carrusel de perfumes completos con la cinta de marcas
(`/es/catalog/full-bottles`) y la portada pasó a mostrar el estudio de decants. Pendiente: decidir
entre el resumen en página (a) o solo el contador (b) tras agregar.

## Actualización del 31 de octubre de 2026

El propietario aprobó las revisiones 04 y 05 (checkout, seguimiento, biblioteca, gestión de pedidos
y configuración). Se implementó:

- Backend: acordes, tipos de uso y perfiles olfativos (modelos, migración `5a1c9e7d3b20`, funciones
  `catalog_option_*`, asignación por perfume, filtros y facetas); recuperación de códigos por correo
  con tiempo de espera de 10 minutos por cédula y por dirección; retiro de las solicitudes
  administrativas de recuperación; cabecera `X-Client-IP` desde el proxy.
- Frontend: `/[locale]/checkout`, `/[locale]/orders`, `/[locale]/admin/{settings,media,orders}`,
  enlace "Continuar con la compra" en el carrito y navegación administrativa.
- Verificación del 31 de octubre: 139 pruebas de backend aprobadas, cobertura 94,31 %, Ruff sin incidencias;
  20 pruebas unitarias del frontend, `astro check` sin errores, ESLint, Prettier y compilación sin
  incidencias; 21 comprobaciones de navegador con Flask y PostgreSQL temporales en Chromium, Firefox
  y WebKit (compra con comprobante, seguimiento, administración de pedidos, recuperación, configuración,
  biblioteca y ausencia de desbordamiento a 320, 390, 768, 1024 y 1440 px). La migración se probó
  hacia arriba, hacia abajo y otra vez hacia arriba, y se aplicó a la base local (`5a1c9e7d3b20`,
  sin diferencias con los modelos).
- No se ejecutó un envío real de correo: la recuperación se probó con un buzón simulado y con un
  servidor SMTP mínimo local. El propietario debe definir `SMTP_*` en `backend/.env`.
- Se corrigió el editor de perfumes, que enviaba `classifications` y creaba casas sin categoría.

Pendiente: la aprobación de la revisión 03 con sus modificaciones, el editor de perfumes con
acordes/uso/perfil y sus filtros públicos, la importación comercial y el retiro del catálogo temporal.
La migración `5a1c9e7d3b20` debe aplicarse a la base real (`uv run alembic upgrade head`) y repetir
el `GRANT EXECUTE` de LOCAL.md.


Fecha: 27 de octubre de 2026. Estado: backend implementado y verificado; nuevas vistas pendientes de aprobación e integración. Este documento sustituye el avance anterior de esta ampliación. La auditoría del 26 de octubre se conserva como antecedente en [reporte.md](reporte.md).

## Resultado y límites actuales

- Persistencia de la aplicación mediante funciones PostgreSQL y parámetros JSONB; SQLAlchemy define exclusivamente tablas/relaciones para Alembic.
- Administrador único por CLI, también protegido por restricción SQL.
- Catálogos comerciales configurables, biblioteca de imágenes, tarifas por ciudad, contacto, bancos, pedidos, comprobantes, estados, transiciones y recuperación implementados en el backend.
- Primera aprobación con existencias confirma la venta; otro pago real sin stock queda como incidencia, sin saldos negativos ni movimientos parciales.
- La revisión visual 04 contiene cinco prototipos navegables en ES/EN. No son páginas comerciales integradas ni registran pedidos reales.
- `beront-bd` ya tiene las siete revisiones aplicadas hasta `c449e445ed3d`. Alembic no detecta diferencias con los modelos.
- Flask usa `beront_app_2ec87f29`; su contraseña aleatoria está únicamente en `backend/.env`. `postgres` conserva la conexión de migración. No se cambió `SECRET_KEY`.
- La importación comercial espera la creación del administrador por el propietario. No se crearon credenciales administrativas ficticias.
- La ampliación completa todavía no se declara terminada: faltan aprobación visual, páginas Astro nuevas, conexión de sus formularios y retirada del catálogo temporal anterior.

## Matriz de los diez puntos solicitados

| Punto | Evidencia y estado |
|---|---|
| 1. SQL organizado, pg_call y modelos | Implementado. 101 archivos SQL versionados para 86 funciones vigentes; repositorios llaman a `pg_call.py`. Tablas por módulo en `shared/infrastructure/modelos/`. |
| 2. Un administrador por CLI | Implementado. `createsuperuser`, alias `create-admin`, recuperación de contraseña, unicidad y prueba concurrente. Sin registro público. |
| 3. Fotografías en backend y URLs en BD | Biblioteca e importador implementados y probados con los 130 perfumes. La importación a la base comercial espera al propietario. Las copias temporales del frontend se conservan hasta completar esa integración. |
| 4. Datos comerciales administrables | Backend implementado para categorías, públicos, presentaciones, marcas, precios, tarifas, bancos, contacto y estados. Persisten opciones y etiquetas anteriores en el frontend; el cumplimiento total está pendiente de sustituirlas. |
| 5. Biblioteca y selección de fotografías | API implementada y probada; prototipo del archivador/modal disponible. La vista Astro espera aprobación. |
| 6. Checkout y seguimiento | Backend implementado para transferencia y WhatsApp, código, historial, guía, comprobante corregido y recuperación. Checkout y panel visuales pendientes de integración. |
| 7. Pagos simultáneos por última existencia | Implementado y probado, incluidas concurrencia, saldo compartido de decants, varias líneas, rollback y llegada tardía del comprobante. |
| 8. Integración final frontend/backend | Parcial. Proxy, cargas y permisos preparados; las páginas nuevas todavía son prototipos. No se presenta como cumplido. |
| 9. Seguridad y permisos | Controles del backend y proxy probados; rol real de ejecución restringido. La verificación de las nuevas páginas comerciales se hará al integrarlas. |
| 10. Pruebas, comandos y reporte | 120 pruebas de backend, 18 unitarias de frontend y 12 visuales aprobadas. Comandos a continuación. El cierre integral depende de los pendientes anteriores. |

## Acceso a datos y esquema

El flujo es endpoint, validación/decoradores, caso de uso, repositorio y función PostgreSQL. Los endpoints no reciben SQL, nombres de tablas ni destinos de base de datos.

`pg_call.py` utiliza una lista técnica de funciones permitidas, identificadores SQL seguros y parámetros enlazados. Serializa UUID, Decimal y fechas sin convertir dinero a punto flotante. El usuario de Flask no lee ni modifica tablas directamente.

Cada función tiene su archivo en `backend/bd/<modulo>/funciones/`, con su definición vigente y sin carpetas de versión. La migración inicial única instala todas las funciones; un cambio posterior de una función se instala con una migración nueva.

Las unidades de trabajo confirman las operaciones completas; un error revierte cambios y cierra la conexión. El dominio permanece independiente de Flask, SQLAlchemy y Pydantic.

Las tablas actuales se definen en módulos de modelos de identidad, catálogo, inventario, medios, comercio y pedidos. No se crearon tablas mediante `create_all` ni mediante SQL manual fuera de Alembic.

## Configuración y semilla

Una marca referencia una categoría obligatoria. Los perfumes heredan esa categoría; no reciben una clasificación independiente editable. Los públicos, categorías y presentaciones tienen nombres ES/EN y estado activo en PostgreSQL.

Una presentación global define tipo y volumen. Cada variante de perfume referencia un tipo/volumen configurado y tiene precio propio. El administrador puede crear medidas nuevas; no hay una lista de 3, 5 y 10 ml en el código de ejecución.

La fuente del HTML se conserva en `backend/semillas/catalogo/`: 130 perfumes, 42 marcas, 400 variantes y 132 archivos. Contiene también medidas de 1, 20 y 30 ml y las medidas de botellas de la fuente. Falta la fotografía de Delina Eau de Parfum; no se inventó.

El importador:
- valida la fuente antes de escribir;
- instala opciones, estados/transiciones iniciales y términos de prueba desde JSON;
- no inventa teléfonos, bancos ni tarifas;
- crea saldos iniciales cero;
- normaliza imágenes y persiste sus URLs `/media/<archivo-generado>.webp`;
- crea 135 asociaciones independientes para las fotografías compartidas;
- importa cada perfume en una transacción;
- omite perfumes ya importados y conserva precios, publicación, imágenes e inventario editados;
- no reactiva opciones desactivadas por el administrador.

Una segunda importación se probó después de cambiar un precio y asignar stock: no alteró esos cambios.

## Biblioteca y comprobantes

La biblioteca permite subir, buscar, renombrar y eliminar recursos no utilizados. Imágenes idénticas se deduplican por checksum y tipo bajo bloqueo transaccional. Varias fichas pueden reutilizar un mismo recurso.

Desvincular una imagen conserva el archivo de la biblioteca. Eliminar un recurso vinculado se rechaza. Las imágenes se decodifican, se recodifican como WebP y se eliminan metadatos; máximo 5 MiB, 20 megapíxeles y cinco fotos por perfume.

Los comprobantes tienen tipo privado `receipt`: no aparecen en la biblioteca de productos, no pueden asociarse como fotos públicas y requieren sesión administrativa para consultarse. Un comprobante corregido se añade al historial sin confirmar ni modificar el pago, incluso si ya fue revisado.

## Pedidos, pagos e inventario

Checkout consta de carrito, datos/envío y pedido recibido. El servidor calcula precios, subtotal, envío por ciudad y total USD.

La cotización se firma con HMAC-SHA-256. Contiene la selección, importes, destino, términos y bancos que se mostraron; no contiene datos del cliente. El cliente no puede cambiar importes, cantidades o destino conservando una firma válida.

En WhatsApp se revisan de nuevo disponibilidad y valores antes de crear el pedido. En una transferencia ya realizada se conserva la cotización firmada aunque cambien precio, tarifa, banco o stock antes de enviar el comprobante. El pedido queda pendiente y recibe código; esto no aprueba el pago ni obliga a confirmar la venta.

No hay reservas, descuentos de inventario ni vencimientos por cotizar, crear un pedido, cargar una foto o abrir WhatsApp. Una cotización no vence por tiempo; rotar `SECRET_KEY` invalida firmas y sesiones anteriores.

La aprobación administrativa:
1. bloquea el pedido y las existencias en orden estable;
2. agrupa ml por perfume y unidades por variante;
3. comprueba todas las líneas antes de modificar alguna;
4. confirma saldos, movimientos, pago, historial y auditoría en una misma transacción;
5. reconoce reintentos y nunca vuelve a descontar un pago confirmado.

Si falta alguna existencia, se registra pago revisado sin stock y se coordina la solución por WhatsApp. No se descuentan parcialmente otras líneas disponibles. Esto evita sobreventa de inventario; no impide que dos personas realicen transferencias externas, según la política elegida por el propietario.

Los nombres de estado y las transiciones son datos editables. Las fases técnicas inmutables protegen las reglas: un cambio de etiqueta no valida un pago y no habilita despacho sin pago confirmado y guía. Devoluciones de ventas ya confirmadas y reembolsos automáticos quedan fuera de esta versión.

Cancelar un pedido sin venta confirmada no toca inventario porque nunca hubo reserva. La guía y el seguimiento de Servientrega los registra el administrador; no se incorporó una API del transportista.

## Seguimiento y recuperación

Cada pedido usa un código aleatorio de 144 bits y único en PostgreSQL. La creación admite una clave idempotente para evitar duplicados por reintentos.

La consulta por código devuelve selección, importes, estado, historial y seguimiento. Omite cédula, dirección, correo, teléfono y comprobantes. El código se envía en POST para evitar colocarlo en la URL de la API.

La recuperación por cédula registra una solicitud con respuesta uniforme, exista o no un pedido. No devuelve códigos ni datos personales. El administrador consulta los pedidos asociados y entrega el código por los contactos registrados; después marca la solicitud atendida. El sistema no envía correos o mensajes automáticamente.

## Seguridad verificada

Se mantiene la tabla de las diez categorías de [OWASP Top 10:2025](https://top10.owasp.org/2025/) en la arquitectura. Aplicación a esta ampliación:

| Categoría | Control concreto y ubicación |
|---|---|
| A01. Acceso | Decoradores en todos los endpoints administrativos; permisos de comercio/pedidos; serialización pública explícita y comprobantes privados. |
| A02. Configuración | Debug desactivado, loopback, origen y proxy fijos, límites de carga y `no-store` en checkout/pedidos. |
| A03. Dependencias | Sin dependencias nuevas; se conservan lockfiles y herramientas de calidad existentes. La auditoría de dependencias anterior conserva su fecha, no se presenta como una auditoría nueva. |
| A04. Criptografía | Contraseñas scrypt, sesiones protegidas, códigos aleatorios y cotizaciones HMAC; credenciales solo en `.env`. |
| A05. Inyección | Funciones permitidas, parámetros JSONB, nombres SQL cerrados, validación de entradas e imágenes recodificadas. |
| A06. Diseño | Aprobación manual, separación entre foto/pago, ausencia de reservas y comprobación conjunta de inventario. |
| A07. Autenticación | Administrador único, sesiones revocables y límites de solicitudes; sin registro público. |
| A08. Integridad | Firmas, snapshots, versiones, idempotencia, bloqueos y transacciones con restricciones SQL. |
| A09. Registro | Auditoría de ajustes, pagos, transiciones y solicitudes atendidas, con actor e identificador de petición; sin registrar cuerpos con PII o comprobantes. |
| A10. Excepciones | Rollback probado ante fallo intermedio, errores uniformes y ausencia de descuentos parciales. |

Las mutaciones administrativas, creación de pedidos y recuperación requieren CSRF. Cotización y consulta por código son lecturas con límites de solicitudes. El frontend conserva cookies y cabeceras CSRF hacia un único backend.

La exclusión de Galápagos se trata como política comercial del propietario. El código provincial 20 se verificó en la [codificación del INEC](https://www.ecuadorencifras.gob.ec/wp-content/uploads/downloads/2022/04/202101_SIEH_Marco-Maestro-de-Muestreo.pdf). El modelo impide tratar esa provincia como continental; los destinos publicados requieren provincia continental activa.

La conexión real de Flask se comprobó sin superusuario, sin CREATE en el esquema y sin SELECT directo a productos. Ejecutar las funciones permitidas sí funciona. Las credenciales de migración permanecen separadas.

Estos controles y pruebas no equivalen a afirmar ausencia absoluta de vulnerabilidades. La seguridad de las nuevas páginas deberá comprobarse después de su implementación y aprobación.

## Verificación

- Backend: **120 pruebas aprobadas**, sin fallos ni omisiones.
- Cobertura global: **94,10 %**.
- Ramas de dominio/aplicación: **90,32 %**, 224 de 248.
- Ruff sin incidencias; **162 archivos** con formato comprobado.
- Frontend: **18 pruebas unitarias aprobadas**, incluidas destino del proxy, cookies, CSRF y límites de tamaño.
- Prototipos: **12 pruebas aprobadas** entre Chromium, Firefox y WebKit.
- Tamaños revisados: 320, 360, 390, 768, 1024 y 1440 px; ES/EN, teclado, diálogos y ausencia de desbordamiento.
- Se corrigieron el ancho mínimo de navegación a 320 px y el retorno del foco en WebKit.
- Migraciones aplicadas a la base real; `alembic check` sin operaciones pendientes.
- La semilla completa se verificó contra PostgreSQL temporal con el rol restringido.
- Las pruebas nuevas no enviaron mensajes, pagos ni pedidos a servicios externos.
- Tipos, lint y compilación del frontend completados sin incidencias; las páginas nuevas siguen siendo prototipos.
- API real a través de Astro: catálogo y opciones de checkout respondieron 200; una escritura administrativa anónima con CSRF válido recibió 401. No se crearon pedidos ni clientes de prueba en la base comercial.

## Comandos

Desde `backend/`:

~~~powershell
uv sync --locked
uv run alembic upgrade head
uv run alembic check
uv run beront createsuperuser
uv run beront importar-catalogo --solo-validar
uv run beront importar-catalogo
uv run beront run
~~~

La base ya está migrada: repetir `upgrade head` no modifica revisiones aplicadas. `createsuperuser` pide usuario y contraseña oculta; solo se ejecuta para crear al propietario una vez. No se inventó una cuenta. Para recuperar acceso:

~~~powershell
uv run beront reset-password NOMBRE_DE_USUARIO
~~~

Antes de probar checkout, registrar contacto, ciudades/tarifas, bancos y términos desde sus endpoints administrativos; las nuevas pantallas de configuración esperan aprobación visual.

En otra terminal, desde `frontend/`:

~~~powershell
bun.cmd install --frozen-lockfile
bun.cmd run dev
~~~

Abrir `http://localhost:4321`, coherente con `FRONTEND_ORIGIN`.

Verificación:

~~~powershell
# backend/
uv run ruff check src tests semillas migrations
uv run ruff format --check src tests semillas migrations
uv run pytest --cov=beront --cov-report=term-missing

# frontend/
bun.cmd run check
bun.cmd run lint
bun.cmd run test
bun.cmd run build
bun.cmd run test:app
~~~

## Próximo paso y cierre pendiente

La revisión 04 se documenta en [design/README.md](../design/README.md). `AGENTS.md`, regla 9, exige: “No implementar una vista del producto sin aprobación explícita de su prototipo vigente.”

Una vez aprobadas las nuevas vistas se implementarán sus páginas Astro contra las APIs reales, se sustituirán las opciones comerciales anteriores y se retirarán las copias y simulador temporal del frontend tras verificar la importación comercial. Después se ejecutarán las pruebas integrales de aplicación y se cerrará la matriz de cumplimiento.

No se realizaron operaciones que modifiquen Git, ni tareas de despliegue.


## Perfumes completos R05 integrado, 12 de noviembre de 2026

El propietario autoriza integrar la revisión vigente de completos. `CylinderPage.astro`
agrupa nombre y selector de mililitros, con precio y botón a su lado debajo. El carrusel
conserva frascos grandes y miniaturas accesibles más abajo. Se retiran la cinta de marcas,
su animación y su región de actualización; los filtros siguen usando las regiones reales
existentes. El fondo contiene tres filas decorativas con el nombre activo, ajustadas a su
ancho y altura por `cylinder.ts`. Los estilos se integran en el bloque existente de
`global.css`, sin duplicar capas del prototipo. Se conservan datos y disponibilidad del backend.

288 comprobaciones de los doce perfumes en Chromium, Firefox y WebKit a 320×568, 360×667,
390×844, 768×1024, 1024×768, 1440×900, 1920×1080 y 2560×1440. Se verifican visibilidad de
compra, margen respecto al menú, filas y fondo, filtros sin recarga, teclado, ES/EN, texto
ampliado, alto contraste y paneles de menú/accesibilidad. Astro check, ESLint, Prettier,
build y dos pruebas unitarias correctos. Evidencias `design/reviews/completos-r05-integrated-*`.
Vista real abierta en Chrome; no se reinician los servidores 5000/4322. Se cierra 4323 al terminar.

## Orden alfabético por marca y modelo, 12 de noviembre de 2026

`CatalogQueryFacade.search` ordena los resultados públicos por marca, modelo e identificador
antes de aplicar la paginación. Afecta al orden predeterminado y al valor existente `sort=name`
en decants y completos. Los órdenes por precio y los listados privados se conservan. No se
modifican funciones SQL ni esquema. El selector compartido etiqueta el orden «Marca y modelo»
en español y «Brand and name» en inglés. 19 pruebas de catálogo, Ruff, ESLint, formato y
Astro check correctos. Los datos locales se consultaron sin escritura para comprobar el
orden completo, documentado en `design/reviews/catalog-brand-order-data.json`.

## Cinco completos añadidos, 12 de noviembre de 2026

Por solicitud del propietario se reutilizan las fichas y fotografías actuales, mediante
`CatalogService`, con auditoría y control de versión. Se reactivan Le Male Le Parfum
125 ml $165, Le Beau Le Parfum 125 ml $168 y Valentino Uomo Born in Roma Intense 100 ml
$168. Se crean las presentaciones completas de Le Male Elixir 125 ml $165 y Ultra Male
125 ml $155. Las presentaciones globales de 100/125 ml ya existían y estaban activas.
El catálogo público pasa de 12 a 17 completos. Se conservan fotos, fichas y decants;
no se registran movimientos de inventario y las cinco presentaciones tienen stock cero.

La API confirma los cinco precios, tamaños y fotografías. 120 comprobaciones correctas
en Chromium, Firefox y WebKit a 320×568, 360×667, 390×844, 768×1024, 1024×768, 1440×900,
1920×1080 y 2560×1440, con los cinco perfumes: información comercial visible y sin
superposición del menú. Evidencias `design/reviews/completos-added-jpg-valentino*`.
No se modificó código ni esquema y no se reiniciaron los servidores existentes.

## Navegación temporal de catálogo, 13 de noviembre de 2026

`PUBLIC_CATALOG_ONLY` activa por defecto Inicio, Decants y Perfumes completos en la interfaz
pública. `features/catalog/storefront.ts` centraliza el modo y los destinos del Home.
SiteLayout omite pedidos, carrito y acceso administrativo; MainMenu recibe el modo desde
ese layout, mientras AdminLayout conserva sus controles privados. Los botones de compra
y resúmenes no se renderizan en catálogos/ficha; sus controladores admiten la ausencia de
estos controles, manteniendo la selección de tamaños, precios y fotos. Idioma y panel de
accesibilidad siguen disponibles en cabecera. No se retiran rutas, APIs ni datos.

El arnés de pruebas existentes inicia el frontend con `PUBLIC_CATALOG_ONLY=false` para
conservar las regresiones de las funciones completas. Se actualiza la prueba de fotos
para seleccionar explícitamente un decant, conforme al R05 aprobado que no autoselecciona.
75 comprobaciones de modo catálogo y 15 pruebas de funciones completas correctas en tres
navegadores; 27 unitarias correctas, tipos, lint, formato y build sin errores. Capturas y
resultados `design/reviews/catalog-only-*`. Se conserva 5000/4322 y se cierra la revisión 4323.
