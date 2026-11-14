# Aprobaciones de diseño

## Última vista del proyecto — aprobación explícita, 13 de noviembre de 2026

El propietario declara: «apruebo todos los cambios de la ultima vista que me diste del proyecto,
agregarlos al proyecto». Queda aprobada la vista vigente mostrada en la aplicación local,
incluido el carrito con fotos de los completos y foto más decant animado para los decants,
con su adaptación móvil y accesibilidad. Se conservan Inicio, Decants y Perfumes completos,
el modo de solicitud abierto y el resumen legible de WhatsApp ya integrados.

Los cambios se encuentran en el código del producto, especialmente `features/cart/dialog.ts`,
`shared/components/vial.ts` y `shared/styles/global.css`; no requieren copiar archivos desde
prototipos ni modificar datos comerciales. Esta aprobación corresponde a la última vista
mostrada y no reactiva alternativas anteriores rechazadas. Se solicita comprobarla de nuevo
en Chrome mediante la aplicación habitual del puerto 4322.

Confirmación realizada en Chrome sobre `http://localhost:4322/es/`: navegación pública vigente
y carrito con las fotos de Dunescape y Odyssey Mandarin Sky completos, más Arabian Sky,
Bacio Immortale y Odyssey Limoni como decants con sus controles. Se observa el total vigente
$182.13 después de cambios realizados por el propietario durante la revisión. No se alteran
su selección ni cantidades; ambos servidores habituales se conservan. Se verifica la
integración existente; esta aprobación documental no requiere cambios adicionales de código.


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


## Carrito y WhatsApp — reactivación solicitada el 13 de noviembre de 2026

El propietario pide agregar productos, consultar el carrito, cambiar cantidades, eliminar y
preparar el resumen para WhatsApp. Se reutilizan el diálogo y controles de compra ya aprobados,
sin introducir otra vista ni alterar los diseños de Inicio, Decants o Perfumes completos.
Las tres secciones permanecen en el menú; el carrito vuelve como utilidad de cabecera y resumen.
En el modo limitado, WhatsApp es la acción principal del diálogo y se oculta el acceso a checkout.
Se indica que disponibilidad, pago y envío se confirman por WhatsApp. La autorización posterior
«por ahora coloquemos abierto, sin especificar cantidad» permite solicitar sin saldo registrado;
no se añaden existencias ni se omite el agotado manual. Ver contrato en ARCHITECTURE.md.


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

La arquitectura fue aprobada el 23 de octubre de 2026.
Revisión visual 01 preparada y aprobada por el propietario el 24 de octubre de 2026.

El propietario aprobó la revisión 01 de las seis vistas y solicitó levantar el frontend.
Cualquier modificación visual posterior debe identificarse en otra revisión.

## Perfumes completos — Frascos protagonistas R05, 12 de noviembre de 2026 — Aprobado

El propietario solicita «agrega los cambios de los perfumes completos, donde se puede
visualisar mejor todos los elementos», autorizando integrar el prototipo vigente R05 con
su último ajuste: frascos grandes, ml junto al nombre, precio y compra debajo, sin cinta
de marcas y exactamente tres nombres decorativos detrás del carrusel. Se integra en los
componentes y estilos existentes; filtros, datos comerciales, carrito y menú conservan
sus contratos. Los párrafos siguientes documentan la preparación previa a esta aprobación.

Integración verificada: 288 casos (doce perfumes, tres navegadores y ocho tamaños), sin
desbordamientos ni superposición de nombre, ml, precio o compra con el menú. Navegación,
teclado, filtros sin recarga, ES/EN, alto contraste, texto ampliado y paneles comprobados.
Astro check (98 archivos), ESLint, formato, build y dos pruebas unitarias del carrusel
correctos. Evidencias `design/reviews/completos-r05-integrated-*`. Vista habitual en 4322
abierta y revisada en Chrome; servidores existentes conservados. Sin dispositivos físicos.

Ajuste previo a aprobación solicitado el 12 de noviembre: se oculta la cinta de marcas y
el nombre seleccionado aparece exactamente tres veces dentro del área del carrusel,
detrás de los frascos y ajustado a ancho/altura. Se conserva la geometría de R05: frascos
grandes, ml junto al nombre y precio con botón en una fila inferior. El producto no cambia.
Pasan 63 comprobaciones en tres navegadores/siete tamaños y la revisión de los doce nombres
a 320/1440 px. Evidencias `completos-protagonista-r05-fondo-*`. Continúa pendiente.

El propietario pide frascos mayores, mililitros junto al nombre y precio con el botón a
su lado en una fila inferior. Permite que las miniaturas queden fuera de la primera pantalla.
Prototipo vigente de esta petición: `design/prototypes/completos-protagonista-r05.html`.
Se conserva R04 para comparación; el producto no cambia.

R05 aumenta la altura del carrusel según el viewport, conserva navegación y menú inferior.
Su ajuste vigente sustituye la cinta por tres nombres decorativos detrás de los frascos. Agrupa el nombre y el selector real de volumen en una fila; el importe ya
no se duplica dentro de los botones de volumen. Precio y botón de compra se mantienen en
una fila debajo de la identificación. Se preservan todos los importes, variantes y estados
de disponibilidad. Las miniaturas siguen accesibles desplazándose hacia abajo.

Estilos y agrupación exclusivos de design/assets/completos-protagonista-r05.*. Se reutiliza
el motor del carrusel de la copia de R04. Las pantallas pequeñas y de poca altura ajustan
la escala para conservar los datos de compra sin superposición del menú.

Pasan 288 comprobaciones: doce perfumes en Chromium/Firefox/WebKit a 320×568, 360×667,
390×844, 768×1024, 1024×768, 1440×900, 1920×1080 y 2560×1440. Se verifican filas de
nombre/ml y precio/botón, visibilidad, márgenes y separación del menú. Texto ampliado al
125% y apertura de menú/accesibilidad comprobados en Chromium a 320/390 px.
Evidencias design/reviews/completos-protagonista-r05-*. Sin pruebas en dispositivos físicos.
Pendiente de aprobación; ningún cambio en el frontend del producto, backend ni servidores.

## Aprobación de Decants y revisión de completos, 12 de noviembre de 2026

El propietario aprueba el último diseño de Decants mostrado: R05, la vista original con
catálogo inicial a todo el ancho y estudio revelado tras seleccionar. Ya estaba integrado;
se registra esta aprobación expresa. No corresponde al R04 desplegable rechazado antes.

El propietario rechaza las alternativas A/B de completos R03 y pide conservar la vista
aprobada de su captura, ajustando tamaños y espacios para que nombre, mililitros, precio y
botón de compra sean visibles sin que el menú los tape. La nueva revisión se prepara solo
en `design/prototypes/completos-visibilidad-r04.html`, con estilos propios y copia compilada
de los controles originales en `design/assets/completos-visibilidad-r04*`.

Conserva carrusel centrado, cinta de marcas, nombre decorativo único, distribución centrada
de información y menú inferior fijo. Se reducen la altura de los frascos, las miniaturas
y los espacios verticales. Los móviles de poca altura tienen una adaptación adicional.
Los textos, productos, precios y estados de disponibilidad de la copia permanecen iguales;
no se simula disponibilidad ni se habilita compra de productos agotados.

Pasan 72 comprobaciones de apertura/visibilidad en Chromium/Firefox/WebKit a 320×568,
360×667, 390×844, 768×1024, 1024×768, 1440×900, 1920×1080 y 2560×1440; tres perfumes
por tamaño. Nombre, medidas, precio y botón permanecen dentro del viewport y sin
superposición del menú. También se verifican los doce nombres a 320×568 y 1440×900.
Evidencias `design/reviews/completos-visibilidad-r04-*`. Sin pruebas en dispositivos físicos.
Completos R04 queda pendiente de aprobación visual; el producto y sus servidores no cambian.

## Perfumes completos — Armonía R03 A/B, 11 de noviembre de 2026 — Rechazadas el 12 de noviembre

El propietario pide dos propuestas que armonicen la composición y dejen el precio visible
al abrir, sin que el menú lo tape. Prototipos independientes:
`design/prototypes/completos-armonia-r03-a.html` (Escaparate compacto) y
`design/prototypes/completos-armonia-r03-b.html` (Ficha junto al perfume).

A conserva el carrusel centrado en menor altura y agrupa nombre, medida, precio y acción
en una franja inferior; en móviles se ordenan verticalmente. B distribuye carrusel y ficha
lateral en anchos expandidos y los apila en compacto/mediano, conservando la ficha oscura.
Ambas reducen la prominencia del nombre decorativo y reservan un espacio en el flujo para
el menú después de las miniaturas: ya no flota sobre el precio. El precio aparece dentro
del primer viewport en los tamaños comprobados. Fotos copiadas sin modificación a
`design/assets/completos-armonia-r03-photo-*` para independizar la revisión de peticiones
repetidas al backend. Se conservan productos, importes y presentaciones de la copia inicial.

Pasan 126 comprobaciones de nombre/márgenes/fotos/precio/menú en Chromium/Firefox/WebKit,
a 360×667, 390×844, 768×1024, 1024×768, 1440×900, 1920×1080 y 2560×1440, con tres
perfumes por caso. Se comprueba apertura del menú y accesibilidad en ambas alternativas.
Capturas y resultados `design/reviews/completos-armonia-r03-*`. Sin pruebas en dispositivos
físicos. Prototipos servidos por el servidor estático existente 4330; sin cambios en el
producto ni en los servidores del propietario. Ambas alternativas esperan aprobación.

## Perfumes completos — Fondo R02, 11 de noviembre de 2026 — Pendiente

El propietario solicita un prototipo sin la cinta móvil de marcas y con el nombre del
perfume seleccionado repetido en el fondo, íntegro dentro de los márgenes. Referencia:
`design/prototypes/completos-fondo-r02.html`. Se conserva la vista vigente mediante una
copia de su HTML/estilos y una copia compilada de los controles existentes, exclusivamente
en `design/`; recursos `design/assets/completos-fondo-r02*`. El producto no se modifica.

El fondo tiene cinco filas con el nombre seleccionado, contorno y tipografía originales;
la medida se ajusta al ancho disponible y a la longitud real del nombre al cambiar de
perfume o de pantalla. La cinta queda oculta. Los frascos, información y controles se
conservan por encima del texto decorativo, que está excluido de lectores de pantalla.
El panel de accesibilidad reutiliza el comportamiento existente.

Pasan 54 verificaciones de nombre/márgenes en Chromium/Firefox/WebKit a
390/768/1024/1440/1920/2560 px y una revisión de todos los nombres a 390/1440 px.
Capturas y resultados `design/reviews/completos-fondo-r02-*`. Sin pruebas en dispositivos
físicos. El prototipo usa las fotos del servidor local 4322 y el servidor estático existente
4330 para su revisión interactiva. Pendiente de aprobación antes de integrarlo.

## Decants R05 — Conservación de la vista vigente, 11 de noviembre de 2026 — Aprobado el 12 de noviembre

El propietario rechaza R04 y ordena conservar exactamente la vista del producto que
adjunta en su captura: filtros directos, tarjetas, tipografía, colores, distribución del
estudio, frasco y animación vigentes. Autoriza únicamente iniciar con el catálogo a todo
el ancho disponible y contraerlo hasta su distribución actual cuando el usuario elige
un perfume, revelando el estudio. Esta instrucción sustituye la propuesta R04; no se
integran sus controles ni estilos. Se conserva como referencia rechazada.

Se modifica exclusivamente la selección inicial de `DecantStudio.astro`, la revelación
del estudio en `studio.ts` y las reglas de estado/transición en `global.css`. Sin selección
explícita no se elige un producto automáticamente. Una URL con `selected` válido conserva
la vista seleccionada al recargar. Los filtros del componente original no se modifican.
No se cambia backend, datos, dependencias ni arquitectura.

Verificación: 18 combinaciones de Chromium/Firefox/WebKit a 390/768/1024/1440/1920/2560 px,
sin desbordamientos. En Chromium a 390/1440/1920 px, los estilos y dimensiones registrados
de lista, filtros, tarjetas, estudio y visuales coinciden con la versión anterior al ajuste.
Se prueban filtros sin apertura automática, selección, transición con movimiento y recarga
con `selected`. `astro check`: 0 errores/advertencias; cuatro pruebas unitarias del estudio
correctas. Evidencias `design/reviews/decants-r05-*`. No se probaron dispositivos físicos.
Se conserva el servidor del propietario y se cierra únicamente el frontend temporal 4323.

## Decants R04 — Catálogo desplegable, 11 de noviembre de 2026 — Rechazado

Ajuste solicitado: Familia y Público conservan botones directos visibles, con estado
seleccionado y combinación de ambos filtros; no se presentan como desplegables en R04.
Verificadas doce combinaciones de navegador/ancho y limpieza de filtros; evidencias
`design/reviews/decants-r04-filtros-*`.

El propietario solicita iniciar Decants con el catálogo a todo el ancho disponible y
revelar el estudio únicamente tras seleccionar un perfume. Prototipo vigente de esta
petición: `design/prototypes/decants-r04-desplegable.html`. No está aprobado ni integrado.

El catálogo adapta sus columnas con Grid; al seleccionar se contrae a la izquierda y
entra el detalle a la derecha con perfume sin fondo, decant animado, medidas y precios.
En compacto y mediano, el detalle sustituye visualmente la lista; volver o Escape
recupera búsqueda, página y foco. Reutiliza los controles y filtros de los prototipos R03.
Los datos comerciales son la copia del 9 de noviembre, con fotografías sustituidas
recientemente; el prototipo no modifica carrito, catálogo ni base de datos.

Verificación: 21 combinaciones de Chromium, Firefox y WebKit a 360, 390, 768, 1024,
1440, 1920 y 2560 px, incluida apertura directa del HTML. Estados inicial/selección/regreso
sin desbordamiento; pruebas adicionales de teclado, filtros y ajustes de accesibilidad.
Evidencias `design/reviews/decants-r04-*`. Las resoluciones representan rangos de dispositivos;
no se realizaron pruebas físicas de Android, iOS ni televisores. Pendiente de aprobación
visual antes de modificar el producto, conforme a la regla 9.

## Fotografías Argos Neptune’s Trident y Triumph of Bacchus, 11 de noviembre de 2026

El propietario aporta ambas referencias para sustituir las fotografías del catálogo. Se
recupera la toma exacta de Neptune’s Trident del sitio oficial de Argos (4162 × 4162) y la
de Triumph of Bacchus de Essence Garden (1000 × 1000). El MCP de Inkscape aplica sendos
contornos vectoriales conservando tapa, cuello, frasco y pedestal físico con ARGOS; excluye
fondo y reflejos inferiores. Exporta PNG transparentes de 1000 × 2368 y 520 × 1232 px y
SVG nativos. Originales y maestros: `design/assets/argos-neptune-*` y
`design/assets/argos-triumph-of-bacchus-*`.

Se sustituyen dos vínculos mediante `ImportCatalogPhotos`, conservando las fotografías
anteriores en biblioteca y los campos ajenos a imágenes. Ambos WebP conservan RGBA exacto.
Pasan doce verificaciones en Chromium/Firefox/WebKit a 390/1440 px: fotos nuevas cargadas,
contenidas y sin desbordamientos; se revisan las cuatro capturas sobre fondo oscuro.
Evidencias y fuentes en `design/reviews/argos-neptune-*` y
`design/reviews/argos-triumph-of-bacchus-*`. Sin pruebas en dispositivos físicos.
Se cierra solo el frontend temporal de revisión; se conservan los servidores del propietario.

## Fotografía de Orto Parisi Megamare, 11 de noviembre de 2026

El propietario aporta una referencia de Megamare para sustituir su foto. Se recupera la
misma toma de My Perfume Shop (1000 × 1000 px). El MCP de Inkscape aplica el contorno que
excluye la sombra exterior y conserva tapa, cuello y base. Exporta PNG transparente de
338 × 765 px y SVG nativo; original y maestros en `design/assets/orto-megamare-*`.

Se sustituye un vínculo mediante `ImportCatalogPhotos`, conservando la foto anterior en
biblioteca y los campos ajenos a imágenes. El WebP mantiene RGBA exacto. Pasan seis
verificaciones en Chromium/Firefox/WebKit a 390/1440 px: imagen nueva cargada, contenida
y sin desbordamiento. Evidencias `design/reviews/orto-megamare-*`. Sin pruebas en
dispositivos físicos. Se cierra solo el frontend temporal de revisión.

## Fotografía de Parfums de Marly Delina, 11 de noviembre de 2026

El propietario aporta una referencia nueva de Delina. Se recupera la misma imagen oficial
de 1080 × 1080 px y el MCP de Inkscape aplica un contorno vectorial que excluye la sombra
exterior conservando frasco, tapa, cordón y borlas. Exporta PNG transparente de 338 × 673 px
y SVG nativo. Original y maestros: `design/assets/pdm-delina-*`.

Se sustituye un vínculo mediante `ImportCatalogPhotos`, conservando la imagen anterior
en biblioteca y los campos ajenos a imágenes. El WebP conserva RGBA exacto. Pasan seis
verificaciones en Chromium/Firefox/WebKit a 390/1440 px: imagen nueva cargada, contenida y
sin desbordamiento. Evidencias `design/reviews/pdm-delina-*`. Sin pruebas en dispositivos
físicos. Se cierra solo el frontend temporal y se conservan los servidores del propietario.

## Fotografía de Lorenzo Pazzaglia Speachless, 11 de noviembre de 2026

El propietario aporta una foto nueva de Speachless para reemplazar la del catálogo. Se
recupera la misma toma de Fragrantica a 700 × 700 px. El MCP de Inkscape aplica un contorno
vectorial suavizado y exporta PNG transparente de 342 × 626 px y SVG nativo. Original y
maestros en `design/assets/lorenzo-speachless-*`.

Se revisa el recorte sobre el fondo oscuro y se sustituye un vínculo mediante
`ImportCatalogPhotos`, conservando la imagen anterior y los campos ajenos a imágenes.
El WebP conserva RGBA exacto. Pasan seis verificaciones en Chromium/Firefox/WebKit a
390/1440 px: imagen nueva cargada, contenida y sin desbordamiento. Evidencias
`design/reviews/lorenzo-speachless-*`. Sin pruebas en dispositivos físicos. Se cierra
solo el frontend temporal y se conservan los servidores del propietario.

## Fotografía de Lorenzo Pazzaglia Summer Hammer, 11 de noviembre de 2026

El propietario aporta la referencia de Summer Hammer para reemplazar su foto. Se recupera
el mismo original de Fragrantica (1600 × 1600 px). El MCP de Inkscape aplica el contorno
vectorial suavizado y exporta PNG transparente de 762 × 1402 px y SVG nativo. Maestros y
original en `design/assets/lorenzo-summer-hammer-*`.

Se revisa el recorte y se sustituye un único vínculo mediante `ImportCatalogPhotos`,
conservando la imagen anterior en biblioteca y los campos ajenos a imágenes. El WebP
conserva RGBA exacto. Pasan seis verificaciones en Chromium/Firefox/WebKit a 390/1440 px:
imagen nueva cargada, contenida y sin desbordamiento. Evidencias
`design/reviews/lorenzo-summer-hammer-*`. Sin pruebas en dispositivos físicos.
Se cierra únicamente el frontend temporal; los servidores del propietario se conservan.

## Fotografía de Zoologist Rabbit, 11 de noviembre de 2026

El propietario aporta la foto oficial de Rabbit para reemplazar la del catálogo. Se conserva
el original de 2200 × 2200 px y el MCP de Inkscape aplica el contorno vectorial del frasco,
incluida su base de cristal. Exporta PNG transparente de 990 × 1830 px y SVG nativo en
`design/assets/zoologist-rabbit-bottle.{png,svg}`; original `zoologist-rabbit-original.jpg`.

Se sustituye un vínculo mediante `ImportCatalogPhotos`, conservando la fotografía anterior
en biblioteca y los campos ajenos a imágenes. El WebP conserva RGBA exacto. Pasan seis
verificaciones en Chromium/Firefox/WebKit a 390/1440 px: imagen nueva cargada, contenida y
sin desbordamiento. Se revisan las capturas sobre el fondo oscuro. Evidencias
`design/reviews/zoologist-rabbit-*`. Sin pruebas en dispositivos físicos. Se cierra solo
el frontend temporal de revisión y se conservan los servidores del propietario.

## Fotografía de Zoologist Nightingale, 11 de noviembre de 2026

El propietario aporta una referencia y solicita continuar su sustitución. Se recupera la
misma foto de The Perfume Apothecary (2048 × 2048 px). Se contrasta la base con una foto
oficial de Zoologist para conservar su pie de cristal completo. El MCP de Inkscape aplica
un contorno Bézier, elimina el fondo floral y exporta un PNG transparente de 770 × 1456 px.
Original y maestros: `design/assets/zoologist-nightingale-{original.png,bottle.svg,bottle.png}`.

Se revisa sobre el fondo oscuro del estudio y se sustituye un único vínculo mediante
`ImportCatalogPhotos`, conservando la foto anterior en biblioteca y los campos ajenos a
imágenes. El WebP mantiene los píxeles RGBA exactos del PNG. Pasan seis verificaciones en
Chromium, Firefox y WebKit a 390/1440 px: imagen nueva cargada, contenida y sin desbordamiento.
Evidencias `design/reviews/zoologist-nightingale-*`. Sin pruebas en dispositivos físicos.
Se cierra únicamente el frontend temporal de revisión; los servidores del propietario se conservan.

## Fotografías de cuatro Xerjoff, 11 de noviembre de 2026

El propietario solicita reemplazar Erba Pura, Naxos, Torino21 y Tony Iommi Monkey Special
con las referencias aportadas, dejando solo los frascos. Para Erba Pura proporciona después
el enlace de Falabella que se utiliza como fuente vigente. Naxos se recupera de LEVEL,
Torino21 de Xerjoff y Tony Iommi de Perfumes Bogotá. Originales y maestros en
`design/assets/xerjoff-{erba-pura,naxos,torino21,tony-iommi}-*`.

El MCP de Inkscape aplica contornos vectoriales y exporta los cuatro PNG transparentes:
Erba Pura 422 × 844, Naxos 449 × 981, Torino21 626 × 1362 y Tony Iommi 522 × 1124 px.
Se excluyen fondos, sombras y reflejos inferiores; se conservan tapas, placas y bases.
La entrada WebP de Falabella se normaliza a PNG con `sips` para la lectura de Inkscape,
comprobando RGBA exacto; el recorte y la exportación finales se realizan en Inkscape.
La revisión visual detecta un borde claro en la tapa de Tony Iommi y se afina su contorno
antes del cierre, manteniendo ambas versiones en biblioteca.

`ImportCatalogPhotos` sustituye los cuatro vínculos y conserva las fotos anteriores.
Los campos del producto ajenos a imágenes no cambian; cada WebP conserva RGBA exacto
del PNG final. Pasan 24 comprobaciones finales: cuatro perfumes, Chromium/Firefox/WebKit
y anchos 390/1440 px, con imagen nueva cargada, contenida y sin desbordamiento. Las seis
pruebas de Tony Iommi se repiten tras afinar la tapa. Evidencias en
`design/reviews/xerjoff-four-replacements.json` y `xerjoff-*-app-{390,1440}.png`.
Sin pruebas en dispositivos físicos. Los servidores del propietario no se reinician.

## Fotografía de Argos Bacio Immortale, 11 de noviembre de 2026

El propietario aporta una foto para reemplazar la del catálogo. Se recupera la misma imagen
de Sayhar (2000 × 2000 px), conservada en diseño. El contorno vectorial excluye fondo y reflejo
inferior, conservando tapa, cuello, cuerpo y base de cristal con ARGOS. El MCP de Inkscape
aplica el recorte nativo y exporta el PNG transparente de 585 × 1377 px. Maestros:
`design/assets/argos-bacio-immortale-{original.webp,bottle.svg,bottle.png}`.

Se revisa sobre el fondo oscuro del estudio y se sustituye un único vínculo mediante
`ImportCatalogPhotos`. La foto anterior permanece en biblioteca y los demás campos del
producto no cambian. El WebP conserva RGBA exacto del PNG. Pasan seis comprobaciones en
Chromium, Firefox y WebKit a 390/1440 px: imagen nueva cargada, contenida y sin desbordamiento.
Evidencias `design/reviews/argos-bacio-immortale-*`. Sin pruebas en dispositivos físicos.

## Fotografía de YSL Y Iced Cologne, 11 de noviembre de 2026

El propietario aporta una foto para reemplazar la del catálogo, dejando solo la botella.
Se recupera de Fragrantica una versión de la misma toma a 605 × 1200 px. El contorno SVG
suavizado conserva tapa, cristal, base y muesca lateral; el MCP de Inkscape aplica el recorte
nativo y exporta el PNG transparente. Original y maestros:
`design/assets/ysl-y-iced-cologne-{original.jpg,bottle.svg,bottle.png}`.

Se revisa sobre el fondo oscuro del estudio y se sustituye un único vínculo mediante
`ImportCatalogPhotos`. La fotografía anterior permanece en biblioteca. Los campos ajenos
a imágenes no cambian y el WebP conserva RGBA exacto del PNG. Pasan seis verificaciones
en Chromium, Firefox y WebKit a 390/1440 px: imagen nueva cargada, contenida y sin
desbordamiento. Evidencias `design/reviews/ysl-y-iced-cologne-*`. Sin pruebas en dispositivos físicos.

## Fotografía de Valentino Purple Melancholia, 11 de noviembre de 2026

El propietario aporta una fotografía nueva para reemplazar la del catálogo, conservando solo
el frasco. Se recupera la misma referencia de Fragrantica (1433 × 1791 px) y se conserva el
original. Un contorno SVG suavizado sigue la tapa, los relieves y la base; el MCP de Inkscape
aplica el recorte nativo y exporta el PNG transparente de 425 × 727 px. Maestros en
`design/assets/valentino-purple-melancholia-{original.jpg,bottle.svg,bottle.png}`.

Se revisa sobre el fondo oscuro del estudio y se sustituye un único vínculo mediante
`ImportCatalogPhotos`. La imagen anterior permanece en biblioteca; los demás campos del
producto no cambian. El WebP conserva los píxeles RGBA exactos del PNG. Pasan seis
comprobaciones en Chromium, Firefox y WebKit a 390/1440 px: imagen nueva cargada, contenida
y sin desbordamiento. Evidencias `design/reviews/valentino-purple-melancholia-*`.
No se probaron dispositivos físicos.

## Fotografía de Azzaro The Most Wanted Parfum, 11 de noviembre de 2026

El propietario aporta otra referencia, correspondiente al Parfum de líquido ámbar. Se recupera
la misma foto de Las Fragancias (4167 × 4167), conservada en diseño. Un contorno Bézier excluye
el fondo y las sombras lateral e inferior; el MCP de Inkscape aplica el recorte y exporta el PNG
transparente de 1000 × 1793 px. Maestros: `design/assets/azzaro-most-wanted-parfum-{original.jpg,bottle.svg,bottle.png}`.

Se revisa antes de sustituir una única imagen mediante `ImportCatalogPhotos`. Los campos
comerciales no cambian; el archivo anterior permanece en biblioteca. El WebP conserva los
píxeles RGBA exactos del PNG. Pasan seis comprobaciones de Chromium/Firefox/WebKit a 390/1440 px,
con la foto nueva cargada, contenida y sin desbordamiento. Evidencias
`design/reviews/azzaro-most-wanted-parfum-*`. No se probaron dispositivos físicos.

## Fotografía de Azzaro The Most Wanted EDP Intense, 11 de noviembre de 2026

El propietario solicita reemplazar la foto por su referencia. Se localiza la misma fuente de
Venba, se conserva en `design/assets/azzaro-most-wanted-intense-original.png` y se obtiene un
contorno SVG suavizado desde los límites de la botella, sin modificar los píxeles del original.
El MCP ejecuta el recorte nativo de Inkscape y exporta `azzaro-most-wanted-intense-bottle.{svg,png}`,
PNG RGBA de 499 × 949 px. Se revisa sobre blanco y dentro de la escena oscura del producto.

Se sustituye exactamente un vínculo mediante `ImportCatalogPhotos`, conservando la foto anterior
en biblioteca. Los demás campos del producto no cambian y el WebP conserva RGBA exacto del PNG.
Pasan seis comprobaciones de Chromium/Firefox/WebKit a 390/1440 px: imagen nueva cargada,
contenida y sin desbordamiento. Evidencias `design/reviews/azzaro-most-wanted-intense-*`.
No se probaron dispositivos físicos.

## Fotografía nueva de Valentino Extradose, 11 de noviembre de 2026

El propietario solicita sustituir la fotografía de Uomo Born in Roma Extradose por la referencia
aportada, conservando solo la botella. Se localiza la misma imagen en la fuente abierta por el
propietario y se guarda como `design/assets/valentino-extradose-original.png`. La fuente ya
contiene transparencia; el MCP de Inkscape aplica `object-set-clip` para excluir la caja y exporta
`valentino-extradose-bottle.{svg,png}` a 402 × 710 px, sin alterar el alfa del contorno original.
Se revisa el PNG antes de sustituir un único vínculo mediante `ImportCatalogPhotos`.

El archivo anterior permanece en biblioteca. Los campos del producto ajenos a imágenes se
comparan antes/después y no cambian; el WebP público conserva exactamente los píxeles RGBA del
PNG. Verificado en Chromium, Firefox y WebKit a 390/1440 px: fotografía nueva cargada, contenida
y sin desbordamiento. Evidencias `design/reviews/valentino-extradose-replacement.json` y
`valentino-extradose-app-{390,1440}.png`. Sin pruebas en dispositivos físicos.

## Fotos de los perfumes completos nuevos, 10 de noviembre de 2026

El propietario sustituye la oferta de perfumes completos y aporta cinco fotografías con fondo
blanco: Dunescape, Odyssey Mandarin Sky Vintage Edition, Bharara King, Angham Second Song y
Eilish No. 2. Elige recortarlas y revisarlas antes de publicarlas. Los recortes conservan los
píxeles RGB originales y solo vuelven transparente el fondo conectado con el borde y el hueco
del asa de Mandarin Sky Vintage. Originales y PNG en `design/assets/completos-r01-*`; revisión
en `design/prototypes/completos-nuevos-r01.html`. Pasan 48 combinaciones de tres motores, ocho
anchos de 320 a 3840 px y texto normal/125 %. Evidencias `design/reviews/completos-nuevos-r01-*`.
Aprobados por el propietario el mismo día («se ven bien los recortes») y aplicados con
`CatalogService.add_image`: WebP RGBA con fondo transparente, un vínculo por perfume. En
Second Song la foto nueva sustituye al vínculo anterior; el archivo anterior sigue en la
biblioteca. Sección de completos verificada a 1440 y 390 px: 12 miniaturas, ninguna imagen
rota y sin desbordamiento. Evidencias `design/reviews/completos-nuevos-app-*`.

El propietario aporta después las fotos de Lattafa Khamrah Qahwa y de Parfums de Marly Delina
Eau de Parfum, que nunca tuvo fotografía. Se recortan con el mismo método aprobado, con umbral
de blanco 251 para conservar los reflejos de la tapa de cristal de Khamrah Qahwa, y se vinculan
como foto principal. Originales y PNG en `design/assets/completos-r01-*`. Revisadas en la
tienda: completos a 1440 px y decants a 1440/390 px, sin imágenes rotas ni desbordamiento.
Evidencias `design/reviews/completos-nuevos-app-qahwa-1440.png` y `decants-delina-app-*`.
Con esto, todos los perfumes publicados tienen fotografía.

El 11 de noviembre el propietario aporta la foto de Lorenzo Pazzaglia Speachless, perfume nuevo
solo en decants. Se recorta con el mismo método (umbral 238) y se vincula como foto principal.
Original y PNG en `design/assets/decants-r01-lorenzo-pazzaglia-speachless*`. Revisado en decants
a 1440/390 px junto con los decants nuevos de Khamrah Qahwa y Dunescape, sin desbordamiento.
Evidencias `design/reviews/decants-nuevos-*`.

Ese mismo día aporta las fotos de Afnan 9 AM Dive y Jo Milano Paris Game of Spades Emerald,
recortadas con el mismo método (umbral 238). La de 9 AM Dive (349×720) sustituye como foto
principal a la anterior de 183×450, cuyo archivo permanece en la biblioteca. Originales y PNG
en `design/assets/decants-r01-*`; revisadas en decants sin desbordamiento ni imágenes rotas.
Después aporta una foto nueva de Carolina Herrera Bad Boy Extreme; recortada igual (umbral 238),
sustituye como foto principal a la anterior, que tenía el frasco cortado por el borde izquierdo
y permanece en la biblioteca. Evidencias `design/reviews/decants-bad-boy-extreme-app-*`.
El propietario observa bordes irregulares y pide alisarlos. Se rehace el recorte: el contorno
se suaviza a 4x (desenfoque gaussiano 2.6 y umbral) y se reduce con antialias, limitado al
área de la máscara original para no invadir el fondo; los píxeles semitransparentes del borde
se desmezclan del blanco para eliminar el halo. Sustituye a la versión anterior.
Evidencia `design/reviews/decants-bad-boy-extreme-bordes-lisos.png`.
Con el mismo criterio de bordes lisos se sustituye la foto de Afnan 9 PM Night Out (la anterior
cortaba la tapa y la base). Fondo gris uniforme (239) con sombra: el relleno de fondo solo avanza
por transiciones suaves, de modo que absorbe la sombra y se detiene en el canto del frasco; la
desmezcla del borde se hace contra ese gris. Reducida a 1400 px de alto. Evidencias
`design/reviews/decants-9-pm-night-out-*`.
Se sustituyen también las fotos de Parfums de Marly Althaïr y Layton con bordes lisos. Althaïr
(fondo blanco puro): solo cuenta como fondo el blanco igual o superior a 253, para no invadir
la tapa plateada (251), y el contorno se contrae 2 px para quitar el halo claro del JPEG. Layton
llega con transparencia y sombra negra semitransparente: se usa su canal alfa (opaco igual o
superior a 128), lo que elimina la sombra. Evidencias `design/reviews/decants-parfums-de-marly-*`.
Después aporta una foto de Althaïr de mayor resolución (1800 px, `...-althair-original-2.png`) que
sustituye a la anterior. Trae transparencia, sombra semitransparente y una banda gris opaca
desplazada a la derecha y abajo: se elimina el gris neutro conectado al fondo solo a la derecha
de la tapa o por debajo de ella, para no tocar la tapa plateada; contorno contraído 1 px y suavizado.
Se sustituyen las fotos de Afnan 9 PM Rebel y Al Haramain Amber Oud Aqua Dubai. Las fuentes traen
un logotipo ajeno en la esquina: se conserva solo la pieza conectada más grande (el frasco).
Fondo blanco igual o superior a 252, contorno contraído 1 px y suavizado. Evidencias
`design/reviews/decants-9-pm-rebel-*`, `decants-amber-oud-aqua-dubai-*` y `decants-afnan-9-pm-rebel-app-*`.
El propietario envía otra foto de Aqua Dubai sin logotipo (`...-aqua-dubai-original-2.png`, 375×500),
que se recorta con el mismo método y queda como foto principal; la anterior permanece en la biblioteca.
Igual con una foto nueva de 9 PM Rebel (`...-rebel-original-2.png`, 1080 px, fondo gris 239 con
sombra), recortada con el relleno por transiciones suaves; sustituye a la anterior.
Armaf Arabian Sky recibe una foto nueva (`decants-r01-armaf-arabian-sky*`, 1000 px, fondo blanco):
umbral 252, pieza mayor, contorno contraído 1 px y suavizado; corona, joya y listón completos.
El propietario observa bordes irregulares en el cuerpo y la base: la fuente ya llega con un recorte
escalonado pegado sobre blanco. Se rehace con suavizado fuerte (radio 9) desde la base de la tapa
hacia abajo, limitado a 2 px fuera de la máscara, y la corona conserva el suavizado fino; se eliminan
los píxeles blancos atrapados junto al listón. Sustituye a la versión anterior.
Armaf Club de Nuit Iconic recibe una foto nueva (`decants-r01-armaf-club-de-nuit-iconic*`, 900 px):
umbral 253 para conservar la tapa plateada (bordes de hasta 247), pieza mayor, contorno contraído
1 px y suavizado. Revisada en decants a 1440/390 px, sin desbordamiento ni imágenes rotas.
Después la sustituye una foto frontal de mayor resolución (`...-iconic-original-2.png`, 1052 px;
umbral 250, tapa hasta 236), recortada igual y revisada en decants a 1440/390 px.
Jo Milano Paris Game of Spades Wildcard recibe una foto nueva (`decants-r01-jo-milano-paris-game-of-spades-wildcard*`,
800×1200). Halo claro y suelo beige bajo la base: relleno por transiciones suaves con tolerancia de
tono 28 (el dorado de la tapa queda muy por encima) y corte bajo la última fila oscura de la base.
Rasasi Hawas Verde recibe una foto nueva (`decants-r01-rasasi-hawas-verde*`, 1200 px) que sustituye a
la anterior (frasco inclinado y deformado). Vidrio claro: relleno por transiciones suaves (umbral 235),
suavizado fuerte (radio 7) bajo la tapa y limpieza de blancos solo en la franja del borde, para no
perforar los reflejos interiores.
Rasasi Hawas Ice recibe una foto nueva (`decants-r01-rasasi-hawas-ice*`, 1080 px) con tapa casi blanca
y reflejo bajo el frasco: umbral 253 (borde de la tapa hasta 251), corte de la fuente en la base y
eliminación de los grises claros del reflejo en las últimas filas. Sustituye a la anterior.
Rasasi Hawas Fire recibe una foto nueva (`decants-r01-rasasi-hawas-fire*`, 1000 px): relleno por
transiciones suaves (umbral 230), suavizado fuerte (radio 10) desde los hombros y limpieza de grises
claros en la franja del borde; se conserva el borde de vidrio transparente de los hombros.
Rasasi Hawas Tropical recibe una foto principal nueva (`decants-r01-rasasi-hawas-tropical*`, 1790 px,
reducida a 1400 px de alto): umbral 245 y suavizado fuerte (radio 10) bajo la tapa. Solo se sustituye
la foto principal; la secundaria (posición 1) se conserva.
Lattafa Khamrah recibe una foto nueva (`decants-r01-lattafa-khamrah*`, 1500 px, fondo gris plano 246).
La tapa de cristal es más clara que el fondo, así que solo cuenta como fondo el color a ±4 del gris;
pieza mayor, suavizado (radio 4) y desmezcla contra ese gris. Sustituye a la anterior, desenfocada.
Armaf Arabian Sky recibe otra foto, sobre fondo negro (`...-arabian-sky-original-2.png`, 1080×1350),
que sustituye a la anterior de bordes escalonados: fondo negro ±12, pieza mayor, suavizado (radio 4)
y desmezcla contra el negro para evitar halo oscuro sobre fondos claros.
Lattafa Pride Art of Universe recibe una foto nueva (`decants-r01-lattafa-pride-art-of-universe*`,
1200 px, fondo gris 234 con sombra): relleno por transiciones suaves hasta luminancia 140, que absorbe
la sombra y se detiene en el marco azul y la tapa oscura; contorno suavizado. Sustituye a la anterior.
Armaf Odyssey Mandarin Sky recibe una foto principal nueva (`decants-r01-armaf-odyssey-mandarin-sky*`,
2000 px, reducida a 1400 de alto): semilla de fondo dentro del asa para vaciar el hueco, eliminación
del reflejo cian bajo la base curva (luminancia igual o superior a 192 en esa franja) y suavizado
fuerte (radio 9) en el cuerpo. La foto secundaria se conserva; visible en decants y completos.
French Avenue Vulcan Feu recibe una foto nueva (`decants-r01-french-avenue-vulcan-feu*`, 1548 px):
corte de la fuente bajo el aro dorado de la base para quitar el reflejo, umbral 248 y suavizado.
Sustituye a la anterior, que tenía la tapa cortada.
Dolce & Gabbana Devotion Eau de Parfum: el propietario envía una foto de la versión Intense (frasco
más coral) y decide usarla igualmente como foto principal. Se recorta solo el frasco, sin la caja
(`decants-r01-dolce-gabbana-devotion-eau-de-parfum*`); umbral 245 y suavizado fuerte (radio 5) en
el cuerpo para corregir los artefactos JPEG del borde.
Después el propietario envía una foto de Devotion Pour Homme e indica cambiarla por la existente: pasa
a ser la foto principal de Devotion (solo el frasco, sin caja; umbral 246, suavizado fuerte radio 5 en
el cuerpo). Original en `decants-r01-dolce-gabbana-devotion-pour-homme-original.png`. Nombre, público
y precios del perfume no se modificaron.
Dior Homme Cologne recibe una foto nueva (`decants-r01-dior-dior-homme-cologne*`, 1136×2132). El vidrio
es casi blanco y un relleno de fondo invadiría el frasco, así que el contorno se construye como
rectángulo de esquinas redondeadas a 4x sobre los bordes medidos (izquierda 151-155, derecha 966-968,
arriba 60, abajo 2082, radio 12). Sustituye a la anterior, con el lateral izquierdo deformado.
Versace Eros Eau de Toilette recibe una foto nueva (`decants-r01-versace-eros-eau-de-toilette*`, 399×501,
fondo gris plano 242): fondo ±8, pieza mayor y suavizado (radio 3). Sustituye a la anterior.
Después la sustituye otra foto con el frasco más grande (`...-eros-eau-de-toilette-original-2.png`, 900×1200):
se recorta solo el frasco, sin caja ni logotipo, y se corta la fuente en el borde inferior para quitar la sombra.
Versace Dylan Blue recibe una foto nueva (`decants-r01-versace-dylan-blue*`, 1000 px, fondo gris 241): corte
de la fuente en la base para quitar la sombra, relleno por transiciones suaves y suavizado. Sustituye a la
anterior, borrosa y con la tapa cortada.
Versace Eros Energy recibe una foto de escena (pared con sombras y pedestal de mármol,
`decants-r01-versace-eros-energy*`, 1208×1500). Sin fondo liso, el contorno se construye con formas medidas
por saturación: cuerpo rectangular con hombro curvo (Bézier 512/491/512) y esquinas inferiores de radio 12,
tapa y cuello rectangulares; el remate tallado de la tapa se toma de la máscara de saturación. Sustituye a la
anterior, de colores verdosos.
Rabanne Invictus Parfum recibe una foto nueva (`decants-r01-rabanne-invictus-parfum*`, 1200 px con marco
blanco y recuadro gris 242): se recorta al recuadro, semillas de fondo dentro de las dos asas y tolerancia
de tono 8 para conservar la base celeste. Sustituye a la anterior, borrosa y con un asa cortada.
Jean Paul Gaultier Le Beau Eau de Toilette recibe una foto nueva (`decants-r01-jean-paul-gaultier-le-beau-eau-de-toilette*`,
2000×3123, reducida a 1400 de alto): umbral 248, pieza mayor y relleno por filas en la base (desde y 2650)
para que el cristal blanco del fondo del frasco no se confunda con el fondo. Sustituye a la anterior.
Le Beau Flower Edition recibe una foto nueva (`decants-r01-jean-paul-gaultier-le-beau-flower-edition*`, 1268×2388):
mismo método (umbral 246, relleno por filas en la base desde y 1950). Sustituye a la anterior, con halo blanco.
Le Beau Le Parfum recibe una foto principal nueva (`decants-r01-jean-paul-gaultier-le-beau-le-parfum*`, 1000 px):
mismo método (relleno por filas desde y 800). La foto secundaria se conserva.
Le Beau Paradise Garden recibe una foto nueva (`decants-r01-jean-paul-gaultier-le-beau-paradise-garden*`,
1433×1791, fondo gris 242): relleno por transiciones suaves con tolerancia de tono 8 y relleno por filas
en la base desde y 1150. Sustituye a la anterior.
Jean Paul Gaultier Le Male Eau de Toilette recibe una foto de escena en blanco y negro con letras superpuestas
(`decants-r01-jean-paul-gaultier-le-male-eau-de-toilette*`, 1024 px). El torso se separa por tono (H 112-148,
S igual o superior a 18), apertura 9 px, pieza mayor, huecos rellenos, contracción 3 px y suavizado fuerte
(radio 6); la tapa plateada, sin color, se traza con rectángulos medidos (cilindro, conector y collarín).
Sustituye a la anterior, desenfocada.
Jean Paul Gaultier Le Male Elixir recibe una foto nueva (`decants-r01-jean-paul-gaultier-le-male-elixir*`, 1000 px):
semillas de fondo en los huecos del anillo del cuello y suavizado fuerte (radio 6) desde los hombros para que
las vueltas del hilo dorado no dejen el contorno dentado. Sustituye a la anterior.
Le Male Elixir Absolu recibe una foto nueva que ya llega con transparencia
(`decants-r01-jean-paul-gaultier-le-male-elixir-absolu*`): se usa su canal alfa y suavizado fuerte (radio 5)
desde los hombros. Frasco de 268×612 frente a 177×417 de la anterior, que tenía una línea blanca en la base.
Le Male Le Parfum recibe una foto nueva (`decants-r01-jean-paul-gaultier-le-male-le-parfum*`, 1200×620): pieza
mayor para excluir el logotipo ajeno de la esquina y suavizado fuerte (radio 6) bajo el cuello. Sustituye a la
anterior, con halo blanco en los hombros.
Versace Pour Homme recibe una foto nueva (`decants-r01-versace-pour-homme*`, 1000 px). El vidrio del borde es
casi blanco, así que el contorno se traza con rectángulos medidos de esquinas redondeadas a 4x: tapa
(404-597 × 59-161), cuello (426-573 × 158-262) y cuerpo (249-750 × 260-945). Sustituye a la anterior,
recortada por arriba y con colores apagados.
Dior Sauvage Elixir recibe una foto nueva (`decants-r01-dior-sauvage-elixir*`, 1000 px): umbral 240, pieza mayor
y suavizado fuerte (radio 6) bajo la tapa. Sustituye a la anterior, que se veía casi negra.
Valentino Uomo Born in Roma Intense recibe una foto principal nueva (`decants-r01-valentino-uomo-born-in-roma-intense*`,
1179×1570, fondo en degradado con foco): relleno por transiciones suaves (paso 2) y suavizado moderado (radio 2)
para conservar el relieve real de las tachas del contorno. La foto secundaria se conserva.
Jean Paul Gaultier Ultra Male recibe una foto nueva (`decants-r01-jean-paul-gaultier-ultra-male*`, 1000×1356):
umbral 242, pieza mayor y suavizado fuerte (radio 6) desde los hombros. Sustituye a la anterior, con halo blanco.
Valentino Uomo Born in Roma Coral Fantasy: el propietario pide usar una foto publicitaria (Coliseo, salpicaduras,
manzana y lima; `decants-r01-valentino-uomo-born-in-roma-coral-fantasy*`, 1024 px) tras advertirle que no tiene
fondo liso. El contorno se traza con medidas tomadas a 4-5x: tapa, cuello y collar con sus tachas laterales,
hombros con perfil distinto a cada lado (el derecho queda junto a la lima) y cuerpo de semiancho 166 px con
esquinas inferiores de radio 18. Las tachas del borde quedan dentro de un contorno liso. Sustituye a la anterior,
de 143×238 y borrosa.
Azzaro Forever Wanted Elixir recibe una foto nueva del frasco dorado (`decants-r01-azzaro-forever-wanted-elixir*`,
1460×2292, reducida a 1400 de alto): umbral 242 y suavizado fuerte (radio 6) bajo el tambor. Sustituye a la
anterior, recortada por arriba y los lados. Revisada en decants a 1440/390 px, sin desbordamiento ni imágenes rotas.

## Armonía del estudio y tres propuestas nuevas, 9 de noviembre de 2026

El propietario solicita centrar y equilibrar el estudio actual de decants y, por separado,
preparar tres alternativas para elegir o rechazar. Su indicación aprueba el ajuste del diseño
vigente: selección a la izquierda en escritorio, perfume y decant agrupados a alturas
equivalentes a la derecha, información y controles centrados debajo y encabezado equilibrado.
Se refleja primero en el prototipo R02. Las tres propuestas nuevas permanecen pendientes
de elección y no sustituyen al estudio actual.

Cierre del 10 de noviembre. Propuestas R03: A Vitrina, B Galería y C Selección guiada
(`design/prototypes/decants-r03-{vitrina,galeria,guiada}.html`), más la página de comparación
`decants-r03-propuestas.html`, enlazada desde «Comparar», que faltaba. Esa página muestra las
tres a escala en Android, iPhone, tablet, laptop, escritorio, monitor LCD y televisor, y aplica
a la vez el tamaño de texto, el contraste y la reducción de animaciones. Se corrige el título de
Vitrina, que desbordaba a 320 px con texto muy grande. Pasan 234 combinaciones: tres motores,
13 anchos de 320 a 3840 px y texto normal/125 %, sin desbordamiento ni errores de consola.
Evidencias en `design/reviews/decants-r03-*`. **Siguen pendientes de elección**; ninguna se
implementa en el producto sin aprobación expresa.

El 10 de noviembre el propietario pide conservar la idea original del estudio, con los
elementos alineados y el perfume completo al lado de la animación del decant. Su indicación
aprueba este ajuste: las marcas de mililitros pasan al lado exterior del frasco, de modo que
decant y perfume quedan contiguos, con la misma base y centrados sobre la información; las
marcas conservan su línea de ancho fijo y la seleccionada solo se alarga hacia el frasco.
Sin cambios de estructura, datos ni comportamiento. Medidos sin desbordamiento a 390, 820,
1280 y 1920 px. Evidencias `design/reviews/decants-side-by-side-*`.

Ajuste del estudio vigente: la etiqueta «Agotado» tapaba el nombre de la casa en las tarjetas
estrechas. La casa ahora reserva el espacio de la etiqueta y se recorta con puntos suspensivos.
Corrección de alineación del diseño aprobado, sin cambios de estructura. Evidencia
`design/reviews/decants-badge-app-1280.png`.

## Fondos por categoría del Home, 9 de noviembre de 2026

Ajuste de densidad indicado por el propietario: los iconos de completos se ven demasiado
separados. Se revisa primero el patrón del prototipo, pasando de dos a cuatro motivos por
fila, con separación horizontal uniforme. Se conservan los cuatro dibujos, su tamaño,
el color champán y la opacidad aprobada. La indicación aprueba este ajuste del patrón vigente.
Aplicado al recurso público con copia idéntica: ocho apariciones de los cuatro iconos por
repetición, separadas uniformemente por 90 unidades SVG. Pasan 72 comprobaciones de
prototipo/aplicación en tres motores, seis anchos de 320 a 1920 px y texto normal/125 %.
Revisado visualmente en móvil y escritorio; enlace y compilación correctos. Evidencias
`design/reviews/home-bottles-density-*`. No se probaron dispositivos físicos.

Revisión de completos con cuatro fotografías del propietario: solicita convertir sus frascos
en iconos y sustituir con ellos el fondo de «Perfumes completos». Esta indicación aprueba la
sustitución del patrón vigente. Se redibujan en SVG champán el frasco con tapa en punta y
placa trapezoidal, el torso con franjas y atomizador descubierto, el frasco redondeado con
picos y el trofeo con asas. Se revisa primero el recurso en el prototipo de `design/`.
Integrado con copia idéntica en `frontend/public/brand/home-bottles-pattern.svg`. Se revisan
los cuatro dibujos ampliados y el patrón en prototipo y aplicación. Pasan 240 combinaciones
de tres motores, ES/EN, diez anchos de 320 a 1920 px, texto normal/125 % y ambas versiones.
SVG válido, cuatro motivos autónomos, enlaces y compilación correctos. Evidencias
`design/reviews/home-four-bottles-*`. No se probaron dispositivos físicos.

Revisión del decant con referencia del propietario: solicita sustituir el icono genérico por
el atomizador de su fotografía. Se redibuja como SVG champán con pulsador descubierto y orificio,
cuello ancho, vidrio alargado, resorte y tubo curvo. Esta indicación aprueba la sustitución
del motivo del patrón vigente; se actualiza y revisa primero en `design/`.
Integrado con copia SVG idéntica en `frontend/public/brand/`. Revisados el icono ampliado y
su uso en las tarjetas; pasan 120 combinaciones de prototipo/aplicación, tres motores,
diez anchos entre 320 y 1920 px y texto normal/125 %. Enlace de decants y compilación
correctos. Evidencias `design/reviews/home-decant-reference-*`. Sin pruebas en dispositivos físicos.

El propietario indica centrar el texto de las dos opciones, retirar sus fotografías y usar
fondos con varios iconos champán: atomizadores para decants y siluetas de torso, frasco
cilíndrico y frasco con picos para perfumes completos. Esta indicación aprueba ese ajuste del
selector vigente. Se refleja primero en `design/prototypes/home-menu-principal.html` con
los SVG de `design/assets/home-{decants,bottles}-pattern.svg`. Se conservan la pregunta grande
y centrada, las dos opciones y su distribución adaptativa. Los dibujos son decorativos, sin
logotipos, y toman el color champán aprobado; las fotografías del carrusel no cambian.

Integrado en el Home con copias idénticas de los SVG en `frontend/public/brand/`. Patrones
revisados visualmente en prototipo y aplicación a 390/1440 px. El selector pasa 360
combinaciones de idioma, ancho, texto normal/125 %, prototipo/aplicación y tres motores,
más 12 comprobaciones de alto contraste. Enlaces y foco por teclado correctos; Astro,
ESLint, formato y compilación correctos. Evidencias `design/reviews/home-category-patterns-*`.
Se corrige el ajuste de la cabecera del simulador en anchos menores de 1200 px para que sus
controles se reorganicen sin desbordar. La pasada final verifica también la ausencia de
desbordamiento horizontal de prototipo y aplicación. Home actualizado abierto en Chrome;
servidores del propietario conservados. No se prueban dispositivos físicos.

## Selección del catálogo en el Home, 9 de noviembre de 2026

Ajuste posterior indicado por el propietario: centrar la pregunta y darle mayor presencia.
El título usa tamaño fluido de 2,5 a 4 rem, peso 600, líneas equilibradas y mayor separación
respecto de las opciones. Se actualiza primero el prototipo y después la misma regla del Home.
Verificado el ajuste en 360 combinaciones de prototipo/aplicación, ES/EN, 15 anchos, texto
normal/XL y tres motores, sin desbordamientos. Capturas revisadas a 390/1440 px y resultados
en `design/reviews/home-choice-centered-*`. Astro, ESLint y compilación correctos.

El propietario solicita «¿Qué estás buscando hoy?» sobre las opciones de decants y perfumes
completos. Se actualiza primero el prototipo vigente y después el Home: el bloque contiene esas
dos opciones, con sus fotografías sin fondo y datos del catálogo. Traducción EN: «What are you
looking for today?». Se reutiliza la cuadrícula adaptativa existente, apilada en móvil y con dos
columnas desde 600 px. Los accesos a pedidos y carrito siguen disponibles en la navegación.

Verificados prototipo y aplicación en Chromium, Firefox y WebKit: 360 combinaciones de ES/EN,
15 anchos y texto normal/XL; ambas opciones abren su catálogo. Se ajustan las miniaturas del
prototipo para 320 px con texto ampliado. Astro sin diagnósticos, ESLint y compilación correctos.
Capturas y resultados: `design/reviews/home-choice-*`. Bloque real abierto en Chrome; los
servidores existentes no se reinician y se retira el frontend temporal de comprobación.

## Implementación del Home con recortes, 8 de noviembre de 2026

El propietario solicita implementar el Home aprobado el 3 de noviembre utilizando las imágenes
sin fondo. Se conserva el carrusel informativo, sus controles, la cinta de marcas, los accesos
rápidos y el menú integrado. Los recortes R02 sustituyen los marcos ovalados y fotografías con
fondo del prototipo. Los datos del catálogo se consultan al backend y la promoción de ejemplo
no se publica. Se completa primero el backend de mensajes y luego la portada y su gestión,
reutilizando los patrones del panel de configuración aprobado.

Integración terminada el 9 de noviembre: inicio en `/es/` y `/en/`, cinco mensajes activos y
una promoción de ejemplo desactivada. Nueve fotografías del carrusel coinciden píxel por píxel
con los PNG R02; accesos rápidos y cinta toman fotos, cifras y marcas del catálogo actual.
El panel añade «Inicio y mensajes» en Configuración. Se conservan precios e inventario.

Backend completado antes del frontend: suite de 157 pruebas y una prueba posterior de reversión
y reaplicación de la migración `de252c02c932`, sin diferencias con los modelos. Pasan 27 unitarias
y 57 pruebas de aplicación en Chromium, Firefox y WebKit, más 900 combinaciones de la portada
real (ES/EN, 15 anchos, texto normal/XL y cinco mensajes). Se comprueban pausa, teclado, movimiento
reducido, gestión, transparencia, CSRF, versiones y ausencia de interpretación de HTML.
Un fallo inicial al preparar una página Firefox se resolvió fijando el tiempo de prueba también
para la preparación; la ejecución completa posterior pasa sin fallos.

El propietario autoriza expresamente reiniciar solo el backend 5000. Se activa el código nuevo
sin detener el frontend 4322 y se abre `http://localhost:4322/es/` en Chrome. Evidencias:
`design/reviews/home-implemented-{checks,data}.json` y capturas a 390/820/1440/1920 px.
No se probaron dispositivos físicos ni lectores de pantalla.

## Ajuste de distribución de decants, 8 de noviembre de 2026

El propietario señala la captura de la aplicación y solicita la selección de modelos a la
izquierda y la fotografía con el decant animado a la derecha. Esta indicación aprueba ese ajuste
de la disposición vigente; se refleja primero en el prototipo R02 y después en el estudio real.
Desde 840 px se intercambian las dos columnas conservando sus proporciones y funcionalidades.
Por debajo de ese ancho se conserva la vista apilada: frasco seleccionado y después lista.
Prototipo vigente: `design/prototypes/inkscape-catalog-r02.html?preview=decant`.

Aplicado en el CSS compartido, reutilizando Grid y el corte de 840 px existente. Pasan 180
comprobaciones del prototipo y de la aplicación en Chromium, Firefox y WebKit: 15 anchos,
texto normal/muy grande, selección por teclado, filtros en vivo y cambio de nivel por mililitros.
Astro sin diagnósticos, ESLint, Prettier y compilación correctos. Evidencia:
`design/reviews/decants-left-selection-checks.json` y capturas de ambas vistas a 390/1440 px.

## Aprobación e integración de Inkscape R02, 8 de noviembre de 2026

El propietario solicita implementar R02 en el proyecto, levantar la aplicación local y mostrarla
funcionando. Quedan aprobados los recortes del catálogo y su presentación sin cajas en las vistas
de completos y decants. Se integran también en las fotografías compartidas del producto.
Los originales se conservan en la biblioteca. Los PNG maestros de Inkscape se importan mediante
el almacenamiento existente, como WebP con alfa y codificación sin pérdida, conservando sus píxeles.
Se mantiene el contrato `/media/<identificador>.webp`, la autorización y las ubicaciones aprobadas.
Delina conserva su estado sin fotografía original.

Integración aplicada: 132 recortes, 129 perfumes y 135 vínculos. Verificados los 132 RGBA contra
los maestros; originales, precios, 154 saldos y movimientos intactos. Pasan 152 pruebas de
backend, 27 unitarias del frontend y 48 de aplicación en tres motores. Revisión de lectura del
catálogo real: 360 combinaciones de vista/ancho/texto y los 132 medios decodificados en cada
motor; medios descargados una vez y reutilizados para respetar el límite de peticiones.
Capturas revisadas a 390 y 1440 px de completos, decants y ficha:
`design/reviews/implemented-r02-{bottles,decants,product}-{390,1440}.png`.
Resultados en `design/reviews/implemented-r02-{data-check,browser-check}.json`.
Aplicación abierta en Chrome en `http://localhost:4322`; servidores existentes conservados.

## Inkscape R02, 7 de noviembre de 2026: catálogo completo, solo frascos

Después de revisar R01, el propietario pide: «quiero solo el frasco, ahora aplicalo con todos
lo perfumes, el catalogo completo». Autoriza extender el flujo Inkscape/MCP al catálogo.
El caso B con caja deja de ser la presentación propuesta. Esta ampliación no constituye una
aceptación anticipada de cada PNG nuevo ni de las vistas del conjunto.

- 130 perfumes, 135 vínculos de fotografía y 132 fuentes distintas; Delina no tiene imagen.
- 132 PNG RGBA y 132 SVG, con solo el frasco, exportados mediante el binario real de Inkscape.
- Prototipo vigente: `design/prototypes/inkscape-catalog-r02.html`, con galería y vistas de
  24 completos y 119 decants. Fotografías alternativas, comparación, revisión y descargas.
- Fases, límites y evidencias: `design/INKSCAPE_WORKFLOW.md`. Originales intactos y RGB conservado
  en los documentos editables. Las ediciones previas a Inkscape siguen descartadas.
- Verificados Chromium, Firefox y WebKit: 180 combinaciones de vista/ancho/texto, 858 comprobaciones
  de productos a 390/1440 px y los 132 PNG por motor, más controles de revisión y accesibilidad.
- Estado al 7 de noviembre: pendiente de aprobación visual por imagen y presentación. Todo permanece en `design/`.
  El producto y sus datos conservan las fotografías actuales. Sin pruebas en dispositivos físicos.

## Antecedente: ensayo Inkscape R01, 7 de noviembre de 2026

Nueva solicitud del propietario: instalar Inkscape, conectarlo mediante MCP y recortar dos
fotografías originales elegidas aleatoriamente, un frasco y dos objetos en la misma foto.
Las propuestas anteriores siguen descartadas. El ensayo no autoriza un proceso masivo ni cambia
la decisión del catálogo de mostrar solo frascos; frasco y caja se conservan únicamente en el caso B.

- Caso A: Dior Sauvage Eau de Toilette; caso B: Lattafa Fakhar Black (frasco y caja).
- Prototipo: `design/prototypes/inkscape-pilot-r01.html`; PNG y SVG R01 en `design/assets/`.
- Fases, configuración y evidencias: `design/INKSCAPE_WORKFLOW.md`. El MCP usa el motor CLI
  real de Inkscape, sin control de su ventana en vivo. PNG exportados por Inkscape 1.4.4.
- Se muestran en el carrusel y sus miniaturas con comparación original/PNG y revisión ampliada
  sobre negro, blanco, champán y cuadrícula. Solo estos dos casos usan los recortes nuevos.
- Verificadas 180 combinaciones de dos casos, 15 anchos y dos tamaños de texto en Chromium,
  Firefox y WebKit, además de los controles y las capturas. Sin prueba en dispositivos físicos.
- Pendientes por separado: PNG A, PNG B y su presentación en el carrusel. Ninguno está aprobado.
  La resolución de A (147 × 348 px útiles) también debe evaluarse. No se modifica el producto.

## Decisión del 7 de noviembre de 2026: imágenes sin fondo descartadas

El propietario descarta la propuesta de imágenes sin fondo, incluida la revisión 04 de recortes,
su galería y las presentaciones en completos y decants. Dejan de estar pendientes de aprobación.
Los archivos de diseño se conservan como antecedentes descartados; las fotografías originales
y su presentación actual en el producto se conservan. No se implementará el proceso de derivados
sin fondo a partir de esta propuesta.

El propietario señala que no ve el menú aprobado en el producto. Se integra el botón inferior
central y su panel del prototipo `home-menu-principal.html`, usando las rutas, la sesión y los
permisos existentes. El carrito se accede desde la cabecera y el panel; se retira su botón flotante
central para dar lugar al menú, como en el prototipo aprobado. La portada con mensajes destacados
permanece pendiente del backend correspondiente; esta integración no la da por implementada.

Verificación ejecutada: tipos, lint, formato y compilación; 27 pruebas unitarias y 45 de navegador
aprobadas en Chromium, Firefox y WebKit. El menú se verifica en 14 anchos de 320 a 1920 px y con
texto muy grande, contraste, reducción de movimiento y navegación por Tab/flechas. Se comprueban
carrito, idioma, permisos y cierre de sesión con servidores y base temporales. No son pruebas en
dispositivos físicos ni con lectores de pantalla.

## Menú principal: prototipo de inicio con carrusel y menú inferior (3 de noviembre de 2026)

Solicitado por el propietario: página de inicio con carrusel de mensajes y promociones destacadas,
accesos rápidos a decants y perfumes completos, cinta de marcas en diagonal sutil sin cubrir el
contenido del carrusel, y un botón central inferior que abre el menú de toda la página.

Prototipo: `design/prototypes/home-menu-principal.html`. Estado: aprobado por el propietario el
3 de noviembre de 2026. El 7 de noviembre se integra su navegación inferior; la portada y el
carrusel de mensajes siguen pendientes del backend de mensajes.

- Carrusel de 6 mensajes con pausa visible, anterior/siguiente, indicadores y teclado; sin avance
  con "Reducir animaciones". Los textos usan datos reales (119 decants desde $3.00, 24 perfumes
  completos de $63.00 a $255.00, envíos con Servientrega, pago por transferencia o WhatsApp).
- El último mensaje es un ejemplo de diseño para una promoción; no se inventó ninguna oferta.
- Cinta de marcas en flujo normal bajo los controles del carrusel, inclinada 1,7 grados, translúcida,
  sin superponerse a textos ni botones.
- Botón central inferior "Menú" con panel de toda la navegación: tienda, preferencias (idioma y
  accesibilidad) y administración (acceso o secciones tras iniciar sesión).
- Las demás vistas se muestran como capturas de las pantallas actuales para recorrerlas; no son
  nuevos diseños.
- Versiones por dispositivo: selector iPhone, Android, tablet, laptop, escritorio y TV, con
  rangos 600/840/1200/1600 y navegación con flechas para control remoto.
- Integración del 7 de noviembre: el menú ocupa la posición inferior central y el carrito conserva
  el acceso desde la cabecera y el panel.
- Requisito de backend si se aprueba: tabla y endpoints de mensajes destacados (texto ES/EN, imagen,
  enlace, orden, vigencia y activo) con gestión en el panel, antes de implementar el frontend.

## Presentación del perfume sin marco ovalado (3 de noviembre de 2026): propuestas rechazadas

El propietario pidió eliminar las siluetas semiovaladas blancas y mostrar solo la imagen sin fondo.
Se presentaron tres propuestas (silueta de frasco en el color representativo, sin silueta, y foco con
plinto) y el propietario no aprobó ninguna. Sus archivos se eliminaron de `design/prototypes/`.
Vigente: la presentación actual con marco ovalado. Pendiente: nueva petición del propietario.

## Perfumes sin fondo (4 de noviembre de 2026)

Solicitado por el propietario: quitar solo el fondo de las fotografías, sin silueta, sombra ni marco.

- Primera versión rechazada: el modelo de segmentación dejaba transparente el vidrio y el interior
  de algunos frascos.
- Segunda versión rechazada: aún recortaba bordes y restos de la base.
- Tercera versión rechazada: el modelo solo delimita el perfume y la caja, que se conservan
  intactos junto con todo lo que encierran; fuera de ellos se descuenta únicamente el color del
  fondo. Recompuesto sobre el fondo original, el resultado reproduce la foto (diferencia máxima de
  16 sobre 255, solo en ruido del fondo). Sombras y reflejos del suelo quedan como parte de la foto.

El propietario señaló restos del suelo en Khamrah Waha y Valentino, y fondo blanco dentro del asa
de Odyssey Mandarin Sky. También confirmó que deben mostrarse únicamente los frascos, sin cajas.

Revisión vigente 04: `design/prototypes/perfumes-sin-fondo-catalogo.html`.

- Galería de los 130 perfumes de la semilla y sus 135 fotografías vinculadas (132 archivos únicos).
  Delina Eau de Parfum figura sin fotografía porque no tiene una en la fuente.
- Contornos SVG por fotografía sobre los bytes originales, con huecos explícitos para las asas.
  El interior conserva la fotografía, incluidos blancos, etiquetas, vidrio y reflejos. Se separan
  las cajas y los reflejos del suelo mediante el contorno; no se regenera ni se recolorea el frasco.
- Comparación ampliada a igual escala, fotografía completa, zoom, fondos oscuro/claro/cuadrícula,
  buscador, filtro por casa, fotografías alternativas y los tres casos señalados al principio.
- Marcas y notas de revisión guardadas solo en el navegador, con descarga JSON. Estas marcas no
  constituyen una aprobación para implementar ni cambian el catálogo.
- Panel de accesibilidad con tamaño del texto, contraste y reducción de movimiento; navegación
  con teclado y flechas. Adaptación comprobada a 320, 360, 390, 412, 600, 768, 820, 840, 1024,
  1280, 1440, 1600 y 1920 px en Chromium, Firefox y WebKit, además de texto muy grande.
- Verificación de fidelidad: las 135 referencias contienen los bytes de sus archivos originales;
  505 218 píxeles opacos muestreados tras renderizar los recortes tuvieron diferencia RGB cero.
  Comprobados el hueco del asa de Mandarin, el tapón y la base de Waha, y la base de Valentino.
  Esto comprueba la conservación del contenido visible; los contornos siguen sujetos a revisión.
- La apertura directa del HTML local se comprobó. Capturas en
  `design/reviews/perfumes-frascos-{390,1440}.png`.

Estado: descartada por el propietario el 7 de noviembre de 2026. No se ha implementado nada en Astro ni se han
modificado las fotografías, el backend o las dependencias. La fotografía de origen limita lo que
puede conservarse: los tramos que ya llegan cortados en la fuente no se reconstruyen.

Presentación de la revisión 04 en las vistas, solicitada por el propietario:

- `design/prototypes/perfumes-sin-fondo.html#/bottles` muestra los mismos contornos de la galería
  en el carrusel de los 24 perfumes completos, su frasco principal y las miniaturas.
- `design/prototypes/perfumes-sin-fondo.html#/decants` incluye los 119 decants de la semilla,
  búsqueda por nombre/casa, filtros y fotografía principal. Las fotos alternativas de los decants
  reutilizan sus contornos correspondientes. Delina conserva el aviso de fotografía ausente.
- Los tamaños y precios proceden de la semilla; se mantienen los estilos de las vistas y el
  conmutador de comparación con la presentación anterior. La galería enlaza a ambas vistas.
- Fuentes locales, navegación por URL, selector de dispositivo y panel de accesibilidad. Teclado
  para el carrusel y la lista de decants; el foco regresa al control de accesibilidad al cerrar.
- Verificadas ambas vistas en Chromium, Firefox y WebKit en los mismos 13 anchos de 320 a 1920 px,
  incluidos texto muy grande, filtros, selector de perfume, modos de imagen y los tres casos
  señalados. Capturas `design/reviews/recortes-{bottles,decants}-{390,1440}.png`.

La presentación en estas vistas también se descarta el 7 de noviembre; solo cambió el prototipo.

La preparación contemplaba, antes del frontend, un proceso de imágenes en el backend de medios
(generar y guardar la versión con transparencia, con revisión en el panel). Si se elige un modelo
para automatizar el proceso, su dependencia requiere una decisión aparte (regla 15). La revisión
04 no incorpora modelos ni dependencias nuevas.

## Regla de UX/UI, accesibilidad y responsividad (2 de noviembre de 2026)

El propietario incorporó la regla 10 de `AGENTS.md`, que aplica de forma retroactiva a los
diseños aceptados y de forma obligatoria a los nuevos y al proyecto final. Cada prototipo y cada
alternativa debe tener versiones por dispositivo (rangos compacto, mediano, expandido, grande y
extragrande, incluidos televisores) y un panel de accesibilidad (texto, contraste, animaciones).

Estado frente a la regla (aún no cumplen; se adaptan antes de pedir aprobación):

| Diseño | Estado |
|---|---|
| Revisiones 01 a 05 implementadas en Astro | Pendiente de revisión: panel de accesibilidad y verificación en el rango extragrande y televisores |
| Perfumes completos: Cilindro con cinta | Aprobado e implementado el 2 de noviembre de 2026 con panel de accesibilidad y verificación por rangos; no se prepararon prototipos por dispositivo |
| Decants C (con lista y carrito) | Aprobado e implementado el 2 de noviembre de 2026 con panel de accesibilidad y verificación por rangos; no se prepararon prototipos por dispositivo |
| Decants A y B | Descartados; B solo aporta las tarjetas del carrito |

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
conectándose a Flask. Los recursos temporales del frontend se retiraron el 1 de noviembre de 2026.

## Extensión sin prototipo: acordes, usos y perfiles (2 de noviembre de 2026)

Por instrucción del propietario se incorporaron al frontend, sin un prototipo nuevo, los controles
de acordes, tipos de uso y perfiles olfativos que el backend ya admitía: grupos de casillas en el
editor de perfumes y en los filtros públicos, y etiquetas en la tarjeta y la ficha. Reutilizan los
componentes aprobados (`filter-group`, `check-label`, `attribute`). No constituyen una aprobación
visual nueva; un prototipo posterior puede reemplazarlos. En configuración, cada fila incorpora un
botón Activar/Desactivar con el mismo estilo de «Editar».

## Presentación de la portada (2 de noviembre de 2026): propuestas rechazadas

La franja de degradado bajo la portada se rechazó porque desplazaba el catálogo hacia abajo y se
retiró del código. Los tres prototipos siguientes (degradado a media pantalla con tarjetas en
negativo) también se rechazaron y sus archivos se eliminaron.

## Presentación de la portada (2 de noviembre de 2026): nuevas propuestas con animación

El propietario pidió tres propuestas de tendencia que armonicen con la marca. Pendientes de elección:

| Prototipo | Archivo | Idea | Estado |
|---|---|---|---|
| 1 Luces apagadas | `design/prototypes/home-1-luces-apagadas.html` | Showroom oscuro con foco que sigue el cursor e interruptor de luces (negro a blanco con tarjetas en negativo) | Pendiente de elección |
| 2 Cilindro | `design/prototypes/home-2-cilindro.html` | Carrusel 3D de frascos con tipografía fantasma y color ambiente tomado de la foto | Gusta; se usará para perfumes completos |
| 3 Bento vivo | `design/prototypes/home-3-bento-vivo.html` | Mosaico claro con inclinación 3D, contadores y filtro por familia | Solo se conserva la cinta de marcas |

Respuesta del propietario: el Cilindro se reserva para perfumes completos con la cinta inclinada de
marcas del Bento (revisión 2.1) y los decants necesitan una propuesta propia, simple de usar.

### Revisión 2.1 y propuestas para decants (2 de noviembre de 2026)

| Prototipo | Archivo | Idea | Estado |
|---|---|---|---|
| Perfumes completos: Cilindro con cinta | `design/prototypes/home-2-cilindro.html` | 24 frascos completos de la semilla, cinta de marcas en movimiento que resalta la casa del frasco activo | Aprobado e implementado el 2 de noviembre de 2026 |
| Decants A: Cata en cartas | `design/prototypes/decants-a-cata-en-cartas.html` | Cartas que se deslizan (probar o pasar), bandeja "Tu cata" con tamaños y total | Descartado |
| Decants B: Estuche de cata | `design/prototypes/decants-b-estuche-de-cata.html` | Catálogo con filtro por familia y estuche de 4 huecos con frasquitos que se llenan | Descartado como página; sus tarjetas pasan al carrito |
| Decants C: Frasco vivo | `design/prototypes/decants-c-frasco-vivo.html` | Un frasco con líquido animado cuyo nivel es el tamaño elegido; color tomado de la foto | Aprobado e implementado el 2 de noviembre de 2026 |

### Decants C elegido: revisión con lista y carrito (2 de noviembre de 2026)

Decisión del propietario: se elige C (Frasco vivo). B no se usará como página; sus tarjetas con
frasquito, mililitros y precio pasan al carrito. Cambios pedidos y reflejados en
`design/prototypes/decants-c-frasco-vivo.html`, aprobado por el propietario el 2 de noviembre de 2026
y implementado en `frontend/src/features/catalog/DecantStudio.astro`:

- Lista de decants a la derecha, en tarjetas, con búsqueda, filtros por familia y público y orden.
- Frasco animado, datos del perfume y precio a la izquierda; al elegir otro perfume cambian.
- Mililitros por botones visibles junto al frasco, y también por las marcas del frasco y el arrastre.
- Tras agregar, el propietario no eligió entre a) resumen con total y cantidad en la página y
  b) solo el contador del carrito. Se implementó a) por defecto; pasar a b) es un cambio menor
  pendiente de su decisión.
- Carrito en panel lateral con una tarjeta por línea: frasquito, mililitros editables, cantidad,
  precio y total.

Diferencias de la implementación respecto del prototipo:

- La lista conserva los filtros del backend (casa, acordes, usos, perfiles, tamaños, precio y
  disponibilidad) dentro de "Más filtros", además de los chips de familia y público.
- El carrito muestra el frasquito con el color de la fotografía y los ml editables a partir de la
  cotización del backend; el límite de 20 unidades por presentación sigue vigente.
- Se retiró el avance automático y el conmutador a/b propio del prototipo.
- Con el inventario sin existencias (estado actual de `beront-bd`) todo figura "Agotado".

Límite de 4 huecos del estuche (B) es solo ilustrativo: cualquier límite o combinación es una decisión
comercial del propietario, no se ha definido ni se implementará sin su aprobación.

Datos de los prototipos: fotos, nombres, casas y precios reales de la semilla (130 perfumes, 42 casas,
decants desde $3.00). Respetan `prefers-reduced-motion` y no usan emojis.

### Perfumes completos: implementación del Cilindro con cinta (2 de noviembre de 2026)

Implementado en `frontend/src/features/catalog/CylinderPage.astro` y `cylinder.ts`. Diferencias
respecto del prototipo:

- Sin avance automático: el carrusel es manual (flechas, miniaturas, teclado, arrastre y botones
  visibles en todos los tamaños), como en la tienda aprobada; la cinta de marcas sí se mueve y se
  detiene con "Reducir animaciones" o con la preferencia del sistema.
- La cinta usa las casas de los perfumes que se están mostrando y resalta la del frasco activo.
- Búsqueda, familia, público, orden y "Más filtros" quedan debajo de las miniaturas, para no bajar el
  carrusel; filtran sin recargar la página y la paginación del backend se conserva.
- Tras agregar se muestra el resumen con cantidad y total (opción a) y no se abre el carrito.
- La portada (`/es/`) muestra el estudio de decants, igual que `/es/catalog/decants`.
- Se retiraron los componentes de catálogo anteriores (cuadrícula, héroe y filtros laterales) y
  sus estilos.

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

Prototipo: [catalog-refined.html](../design/prototypes/catalog-refined.html).

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

## Home: fotografías vigentes y selección diaria — 12 de noviembre de 2026

El propietario solicita usar en el carrusel las fotografías nuevas que reemplazaron a las
anteriores en el catálogo y cambiar los tres perfumes cada día al azar, siempre un árabe,
un diseñador y un nicho. Se conserva la vista aprobada; esta autorización comprende la fuente
de imágenes y la rotación, sin una propuesta visual nueva. Se consulta la foto principal
vigente, sin modificar fotografías ni sus vínculos. Los mensajes personalizados conservan
su configuración. El propietario autoriza expresamente reiniciar solo el backend del puerto
5000 para activar este cambio; se conserva el frontend 4322.

Verificación: 18 pruebas de dominio, integración PostgreSQL temporal y arquitectura; Ruff y
formato correctos. 45 comprobaciones de imágenes y desbordamientos en Chromium, Firefox y
WebKit a 390/768/1024/1440/1920 px. Se verifican la estabilidad durante el día, el cambio a
medianoche de Ecuador, las tres categorías y la actualización inmediata tras sustituir una
foto. El Home habitual en 4322 sirve las nueve fotos vigentes de los tres mensajes iniciales.
Evidencias `design/reviews/home-daily-*`. Sin pruebas en dispositivos físicos.

## Orden de ambos catálogos por marca y modelo — 12 de noviembre de 2026

El propietario solicita ordenar alfabéticamente los catálogos por marcas, con sus modelos
ordenados dentro de cada marca. Se autoriza este cambio de orden en Decants y Perfumes
completos, conservando las vistas aprobadas. El orden predeterminado del backend se aplica
antes de paginar; la opción existente pasa a decir «Marca y modelo» / «Brand and name».
Se conservan los órdenes explícitos por precio y el listado privado.

19 pruebas de catálogo correctas en PostgreSQL temporal, incluyendo marcas, modelos,
paginación, filtros y precios en ambos tipos. Ruff, formato, ESLint y Astro check (98
archivos, sin errores ni advertencias) correctos. Lectura de los 127 decants y 12 completos
ordenados comprobada; evidencia `design/reviews/catalog-brand-order-data.json`.

Con autorización expresa del propietario, se reinicia solo el backend 5000 para activarlo.
14 comprobaciones correctas del orden completo de la API y del listado inicial de ambas
vistas en Chromium, Firefox y WebKit a 390/1440 px; etiqueta y márgenes correctos. Evidencia
`design/reviews/catalog-brand-order-checks.json`. Se conserva el frontend habitual 4322 y
se cierra la instancia temporal 4323. Sin pruebas en dispositivos físicos.

## Ajuste de completos y Home — 12 de noviembre de 2026 — Autorizado e integrado

El propietario solicita quitar la deformación y reducción progresiva de los frascos
laterales en completos, manteniendo el seleccionado algo mayor, y ampliar los perfumes
del Home al pasar el cursor. Se retiran perspectiva, profundidad y giro del carrusel:
los cuatro vecinos usan la misma escala 0,9 y el activo conserva escala 1. La revisión
vigente de `design/prototypes/completos-protagonista-r05.html` usa su propio runtime
actualizado; R04 conserva su motor anterior. El Home amplía cada imagen un 8% con puntero
preciso, respetando la reducción de movimiento y sin sustituir el movimiento del grupo.

315 comprobaciones correctas en Chromium, Firefox y WebKit: doce perfumes en ocho tamaños,
proporciones sin giro, escalas laterales iguales, activo mayor y datos de compra visibles;
y ampliación de las nueve imágenes de los tres primeros mensajes del Home. Astro check,
ESLint, formato, build y dos pruebas unitarias correctos. Capturas y resultados en
`design/reviews/{completos-frontal-*,home-bottle-hover.png,frontal-hover-checks.json}`.
Vista real de completos revisada en Chrome. Servidores habituales conservados y frontend
temporal 4323 cerrado al terminar. No se probaron dispositivos físicos.

## Navegación pública de catálogo — 13 de noviembre de 2026 — Autorizada e integrada

El propietario solicita ocultar por ahora los demás menús y dejar Home, Decants y Perfumes
completos. Se conserva la identidad del menú aprobado, mostrando sus tres accesos en una
columna compacta y tres columnas cuando hay espacio. Cabecera y pie usan esas secciones;
idioma y accesibilidad permanecen en cabecera. Pedidos, carrito, compra y accesos de
administración se omiten de las vistas públicas. Los catálogos conservan precios, fotos,
selección, animación y filtros; el Home muestra sus tres mensajes dirigidos al catálogo.
El menú privado permanece completo. Es una configuración reversible, sin borrar funciones.

75 comprobaciones correctas en Chromium/Firefox/WebKit, ocho tamaños y las tres secciones,
incluyendo teclado, precios/variantes en ficha, idioma, accesibilidad y carrito previamente
guardado. No se emiten solicitudes de cotización desde estas vistas. Otras 15 pruebas de
menú completo, sesión, permisos y fotos pasan con PostgreSQL y servidores temporales;
27 pruebas unitarias, Astro check, ESLint, Ruff, formato y build correctos. Evidencias
`design/reviews/catalog-only-*`. No se reinician los servidores del propietario ni se
modifica la base de datos. No se probaron dispositivos físicos.
