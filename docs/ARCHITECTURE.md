# BÉRONT — Arquitectura técnica de la primera versión

Estado: arquitectura aprobada por el propietario el 23 de octubre de 2026.
Entorno: ejecución local. Despliegue fuera de alcance.
La aprobación arquitectónica no aprueba los prototipos visuales.
Conexión vigente en este equipo: `beront-bd`, PostgreSQL de Docker en `127.0.0.1:5432`,
para ejecución y migraciones, según `backend/.env`.

## Preferencia de animaciones del sitio, 14 de noviembre de 2026

Por solicitud expresa del propietario, las animaciones están activas por defecto aunque
el sistema operativo indique reducción de movimiento. Solo «Reducir animaciones» en el
panel de accesibilidad aplica `data-motion="reduce"`; la elección se conserva en
`beront.a11y.v1`. Desmarcarla o restablecer las preferencias recupera el movimiento.
CSS y TypeScript comparten esta decisión sin consultar `prefers-reduced-motion`.
Los controles de pausa y navegación manual del carrusel conservan su funcionamiento.
Esta decisión sustituye la dependencia del sistema descrita en aprobaciones anteriores;
no cambia las vistas aprobadas, las capas, el stack ni las dependencias.

## Semilla canónica del catálogo final, 14 de noviembre de 2026

El propietario declara como única fuente los 127 perfumes de Decants listados desde el
catálogo final, con sus nombres y fotografías vigentes. Autoriza sustituir la semilla anterior
y aplicarla en la base local nueva `beront-bd2`. La ubicación continúa siendo
`backend/semillas/catalogo/{catalogo.json,imagenes/}`; no cambian capas, stack ni esquema.

La versión 2 contiene 127 perfumes, 43 marcas, 425 presentaciones (400 decants y 25 completos,
nueve presentaciones desactivadas) y 133 fotografías: 127 principales y seis adicionales.
Se conservan los precios y estados vigentes de sus presentaciones. Las 133 fotos WebP RGBA
son copias exactas de los archivos servidos en el catálogo aprobado, incluidas las incorporadas
posteriormente a R02. El manifiesto comprueba SHA-256, tamaño, dimensiones, transparencia y
correspondencia entre productos y archivos antes de conectar con la base.

Una instalación nueva usa `importar-catalogo` directamente. No necesita los maestros de
`design/` ni ejecutar `importar-recortes`; el adaptador histórico rechaza su uso sobre la
semilla v2. El almacenamiento existente conserva los bytes al normalizar estas imágenes y
genera sus URL `/media/` propias. Las pruebas comparan las 133 respuestas con las huellas
de la semilla e incluyen repetición sin sobrescribir cambios administrativos ni inventario.
Los nuevos saldos empiezan en cero. No se incorporan credenciales a la semilla.

## Infraestructura local Docker autorizada el 14 de noviembre de 2026

Por solicitud expresa del propietario, PostgreSQL 18 y el SMTP de captura Mailpit se
ejecutan en contenedores Docker locales con volúmenes persistentes dedicados y puertos
publicados únicamente en loopback. Flask y Astro/Bun se ejecutan en el equipo anfitrión;
se conservan el stack, las capas y el acceso a PostgreSQL mediante funciones.

La instalación nueva usa `beront-bd` y roles separados `beront_migrator` y `beront_app`.
Los `.env` locales se mantienen fuera de Git; los comandos y puertos vigentes están
en `docs/LOCAL.md`. Esta preparación utiliza Docker CLI y no añade archivos Compose
ni ubicaciones nuevas al repositorio.

## Auditoría y optimización local, 13 de noviembre de 2026

La consulta de filtros reutiliza sus definiciones dentro de la misma unidad de trabajo y
detiene la paginación tras un lote incompleto. La disponibilidad omite grupos de stock vacíos.
El carrito comparte únicamente solicitudes idénticas de cotización que siguen en curso;
no almacena respuestas como caché ni modifica la autoridad del backend sobre los importes.
Los filtros descartan peticiones anteriores canceladas. No cambian contratos, esquema ni diseño.
La auditoría y sus mediciones se registran en `docs/AUDITORIA.md`, conservando su histórico.
El benchmark y las regresiones pertenecen a los patrones existentes de `backend/tests/` y
`frontend/tests/`. El harness de navegador utiliza un directorio temporal de resultados por
ejecución; Playwright directo conserva `frontend/test-results` como valor predeterminado.

## Fotografías del carrito, 13 de noviembre de 2026

El diálogo aprobado utiliza la imagen vigente de cada línea (`image_url` existente). Los completos
muestran la foto; los decants muestran foto y mini frasco animado con nivel según ml. Se reutiliza
`shared/components/vial.ts`, las preferencias de accesibilidad y la Container Query del diálogo.
No hay cambios de módulos, esquema, endpoints ni contratos.

## Solicitudes de compra por WhatsApp, 13 de noviembre de 2026

El propietario solicita habilitar el carrito y enviar su resumen al WhatsApp 0939237376,
registrado mediante CommerceService como `593939237376`, conservando los términos existentes.
Ante la ausencia de existencias registradas, autoriza «por ahora coloquemos abierto, sin
especificar cantidad». Esta excepción permite solicitudes; no confirma ventas ni inventa stock.

`CART_REQUIRES_STOCK=true` mantiene la validación estricta por defecto. El entorno local usa
`false`: CatalogQueryFacade admite cotizar sin saldo y el catálogo público presenta como
seleccionables los productos publicados, activos y no agotados manualmente. `available` en este
modo indica que se admite solicitar la presentación; no acredita existencias. Las consultas
privadas, el checkout, los pedidos y las validaciones de pago mantienen las reglas de inventario.
La selección estática utilizada por OrderService conserva `require_stock=true` por defecto.
No cambia el esquema, los saldos ni los contratos estructurales de respuesta.

El resumen de WhatsApp usa bloques numerados separados por líneas en blanco; presentación,
cantidad, precio unitario y subtotal ocupan líneas independientes, con el total al final.

El carrito conserva únicamente identificadores y cantidades en el navegador. El backend valida
las presentaciones, calcula importes con Decimal y genera el enlace wa.me desde la configuración
persistente. El texto incluye marca, modelo, presentación, cantidad, importes y total en USD,
con disponibilidad y envío por confirmar. Cotizar o abrir WhatsApp no reserva ni descuenta stock;
el cliente revisa el mensaje y decide enviarlo. No se envían mensajes automáticamente.

`PUBLIC_CART_ENABLED=true` habilita los controles y el diálogo ya aprobados independientemente de
`PUBLIC_CATALOG_ONLY`. Inicio, Decants y Perfumes completos siguen siendo las únicas secciones
públicas de navegación; el carrito es una utilidad. En este perfil se omite la continuación a
checkout y WhatsApp pasa a ser la acción principal. `PUBLIC_CART_ENABLED=false` permite ocultar
los controles; `PUBLIC_CATALOG_ONLY=false` conserva el flujo completo existente.

## Navegación pública limitada al catálogo, 13 de noviembre de 2026

El propietario solicita mostrar temporalmente solo Inicio, Decants y Perfumes completos.
`features/catalog/storefront.ts` centraliza `PUBLIC_CATALOG_ONLY`, activo por defecto.
SiteLayout aplica el modo al menú público, cabecera, pie y carrito; MainMenu mantiene el
menú completo en AdminLayout. Idioma y accesibilidad permanecen disponibles en cabecera.
El Home omite mensajes con destinos fuera de estas secciones y las fichas del catálogo.
Se conservan fotos, variantes, precios, filtros y fichas; las acciones de compra y el
resumen del carrito se omiten del HTML público mientras este modo está activo.

La administración conserva su URL, autenticación y permisos. Las rutas y endpoints
existentes no se eliminan ni se bloquean por este ajuste de visibilidad. No constituye
una barrera de autorización ni cambia los contratos del backend. `PUBLIC_CATALOG_ONLY=false`
restaura la interfaz completa. Las pruebas integradas de funciones existentes usan ese
perfil con base y servidores temporales. No se modifica la arquitectura ni el esquema.

## Orden público del catálogo, 12 de noviembre de 2026

Por solicitud del propietario, Decants y Perfumes completos se ordenan por marca y después
por nombre de modelo, sin distinguir mayúsculas. `CatalogQueryFacade.search` aplica este
orden a todos los resultados antes de paginarlos. El valor existente `sort=name`, también
predeterminado, representa este orden en el catálogo público; el control se etiqueta
«Marca y modelo». Los órdenes explícitos por precio y el listado privado conservan su
comportamiento. No cambian esquema, funciones SQL, endpoints ni forma de respuesta.

## Fotografías y rotación diaria del Home, 12 de noviembre de 2026

Por solicitud del propietario, los mensajes iniciales `welcome`, `decants` y `full-bottles`
resuelven sus tres imágenes desde los vínculos vigentes del catálogo público: un perfume
árabe (`arabic`), uno de diseñador (`designer`) y uno de nicho (`niche`). Se usa la foto
principal actual, conservando su URL y definición; reemplazarla en el catálogo se refleja
en la siguiente lectura del Home. Se recorre toda la paginación del repositorio existente.

La selección aleatoria es estable durante cada fecha de `America/Guayaquil` y cambia al
consultar después de medianoche. Por mensaje y categoría se barajan ciclos de productos,
sin repetir el del día anterior mientras haya alternativas y el conjunto no cambie. No
requiere tareas programadas, estado persistente ni migraciones. Si falta una categoría con
fotografía, se usa el símbolo alternativo existente, sin mezclar categorías ni recuperar
una foto antigua. Los demás mensajes conservan las imágenes configuradas; la administración
devuelve su configuración guardada y no la selección diaria calculada. Se mantienen la
forma de la respuesta, los permisos, los repositorios, el diseño aprobado y las dependencias.

## Home aprobado, 8 de noviembre de 2026

El propietario solicita implementar `home-menu-principal.html` usando los recortes sin fondo.
Se completa el requisito de mensajes destacados dentro del módulo `commerce`, reutilizando
sus capas, UoW, permisos `commerce:write`, biblioteca y panel de configuración. Los modelos
`FeaturedMessageModel` y `FeaturedMessageImageModel` definen contenido ES/EN, enlaces internos,
orden, fechas UTC, activo, versión e imágenes ordenadas. Alembic genera el esquema desde modelos;
las funciones `commerce_message_*` realizan la persistencia mediante `pg_call.py`.
`GET /api/v1/home/messages` devuelve solo mensajes activos y vigentes. La administración usa
`GET/POST /api/v1/admin/home/messages` y `PUT /api/v1/admin/home/messages/{id}`, con sesión,
permisos, CSRF, auditoría y control de versión. Las fotos privadas de comprobantes no se admiten.

La portada se implementa en `features/catalog/{HomePage.astro,home.ts}` y usa la ruta de inicio
existente. La gestión se integra en `features/settings/{FeaturedMessages.astro,messages.ts}`,
sin rutas de administración nuevas. Los recursos y pruebas siguen las ubicaciones autorizadas.
Los datos numéricos se consultan al catálogo; la promoción de ejemplo permanece desactivada.
Se conservan stack y límites de módulos, sin dependencias nuevas.

Activado el 9 de noviembre con la migración `de252c02c932`, generada desde modelos y revisada.
`beront inicializar-home` instala los seis mensajes iniciales de forma idempotente, sin
sobrescribir ediciones; cinco están activos y la promoción de ejemplo queda desactivada.
El propietario autoriza reiniciar solo el backend para cargar los endpoints nuevos.
La portada ya sustituye al estudio en `/[locale]/`; el estudio conserva su ruta de catálogo.

## Fotografías Inkscape R02 integradas el 8 de noviembre de 2026

El propietario aprueba implementar R02 en el producto. Los 132 PNG maestros permanecen en
`design/assets/`; el almacenamiento existente los normaliza a WebP con alfa, sin pérdida y
con conservación exacta de RGBA. Las entradas opacas mantienen su normalización habitual.
No cambian `/media/<identificador>.webp`, el esquema, los permisos, las dependencias ni los módulos.

El comando `beront importar-recortes --manifiesto <ruta> [--solo-validar]` valida las huellas
de originales y PNG contra el manifiesto aprobado. `catalog/application/import_photos.py`
reemplaza los 135 vínculos mediante los repositorios existentes en una transacción; conserva
orden, textos alternativos y archivos originales de biblioteca. Identificadores deterministas
permiten omitir vínculos ya aplicados; un vínculo original modificado se rechaza para revisión.
No escribe productos, variantes, precios ni inventario. El adaptador del manifiesto pertenece a
`catalog/infrastructure/approved_images.py`; las pruebas siguen los patrones existentes.

El frontend comparte las imágenes del backend en carrusel, estudio, ficha y carrito. Se retiran
los fondos ovalados, la mezcla de color y el muestreo de brillo de `photos.ts`; el color ambiental
del decant pondera el alfa. Delina permanece sin foto. Esta decisión sustituye el estado de
espera de R02 descrito en el apartado histórico siguiente.

## Navegación aprobada integrada el 7 de noviembre de 2026

El botón inferior central y el panel de `design/prototypes/home-menu-principal.html` se integran
en `SiteLayout.astro` y `AdminLayout.astro` mediante los componentes compartidos
`MainMenu.astro` y `main-menu.ts`. Reutilizan la sesión y los permisos de `/api/v1/auth/session`,
las rutas existentes, el carrito y el panel de accesibilidad. Los controles privados permanecen
ocultos hasta validar la sesión; el backend conserva la autorización de los recursos.
El carrito mantiene sus accesos de cabecera, panel y resumen; se retira el botón flotante central.
La prueba `frontend/tests/e2e/application-menu.spec.ts` sigue el patrón de pruebas existente.
No se añaden módulos, endpoints, dependencias ni cambios de esquema.

La portada con mensajes destacados no forma parte de esta integración de navegación y continúa
pendiente de su backend. El propietario descarta las imágenes sin fondo; se mantienen las fotos
y la presentación actuales, sin proceso nuevo de derivados en la aplicación. Posteriormente
solicita el ensayo Inkscape R01 y su ampliación R02 a todo el catálogo, con solo los frascos;
ambos se realizan exclusivamente en `design/` y R02 espera revisión visual. No cambia el
contrato de fotografías del backend ni se incorpora un proceso de derivados al producto.

## Memoria documental solicitada el 4 de noviembre de 2026

El propietario pidió crear `project_memory.md` si no existía y registrar las decisiones, el
estado actual y el historial de cambios por prototipo y del software principal. Se autoriza ese
archivo en la raíz como memoria documental; no sustituye las reglas de `AGENTS.md`, los contratos
de esta arquitectura ni las aprobaciones de `docs/DESIGN_APPROVALS.md`.

## Alineación backend/frontend del 2 de noviembre de 2026

- `GET /api/v1/admin/inventory` y `/movements` devuelven `product_id`, `product_name`, `brand_name` y
  `volume_ml`; el listado de saldos acepta `kind` y `q`. El frontend no reconstruye nombres.
- Guardar las opciones de un perfume (`accords`, `usages`, `profiles`) solo reemplaza los vínculos de
  opciones activas; los de opciones desactivadas se conservan.
- Los nombres de categorías, públicos y clasificaciones se leen de `facets.definitions`; el frontend
  no contiene listas de negocio.
- Ubicaciones nuevas dentro de patrones existentes: `frontend/src/features/admin/options.ts`,
  `frontend/tests/unit/i18n.test.ts`, `backend/tests/integration/test_cli.py` y las migraciones
  `87313231bdf2` y `49ce23c2f0c8`.

## Ampliación autorizada el 1 de noviembre de 2026

- La carpeta `bd/` se traslada a `backend/bd/` y las funciones SQL pierden las carpetas de versión
  `vNNNN`: cada archivo contiene la definición vigente y el historial queda en Git. La cadena de
  ocho migraciones se sustituye por una migración inicial única generada desde los modelos, que
  también crea el esquema `beront_api` e instala las funciones. Se retiran las huellas SHA-256 de
  las fuentes SQL; un cambio posterior de una función se instala con una migración nueva.
- Las migraciones y la aplicación usan la base PostgreSQL local `beront-bd`.
- La administración local se invoca con el script de consola `beront` (`[project.scripts]` en
  `backend/pyproject.toml`, implementado en `beront/cli.py`) en lugar de `flask --app`.

## Ampliación autorizada el 31 de octubre de 2026

El propietario aprobó, en esta fecha, el checkout, el seguimiento, la biblioteca de fotografías,
la gestión de pedidos y la configuración de la revisión 05. Las decisiones siguientes modifican
las del apartado del 27 de octubre cuando las contradicen.

- Clasificaciones del perfume. Además de categoría (por casa comercial) y género
  (`audiences`), cada perfume admite varios acordes, tipos de uso y perfiles olfativos,
  administrados desde datos persistentes. Las tablas `classification_options` (dimensión
  `accord`, `usage` o `profile`, slug estable por dimensión, nombres ES/EN, activo, versión) y
  `product_classifications` (perfume y opción) las definen. Las funciones SQL `catalog_option_*`
  y `catalog_product_options_set` las gestionan. Una opción desactivada deja de mostrarse y de
  filtrar, pero conserva sus vínculos.
- La API reutiliza `/admin/catalog-options/{accords|usages|profiles}`; los perfumes aceptan
  `accords`, `usages` y `profiles` como listas de slugs en `POST/PATCH /admin/products`.
  El catálogo público filtra con `accord`, `usage` y `profile` (OR dentro de la dimensión, AND
  entre dimensiones) y `GET /catalog/facets` los devuelve.
- Recuperación del código por correo. `POST /orders/recovery` valida la cédula, aplica un tiempo
  de espera de 10 minutos por cédula y por dirección del cliente, y envía los códigos al correo
  registrado en cada pedido. La respuesta pública es uniforme; el tiempo de espera responde 429
  con `RECOVERY_COOLDOWN` y los segundos restantes. El administrador no atiende solicitudes: se
  retiraron `/admin/order-recoveries`, la tabla `order_recoveries` y sus funciones SQL. El
  intento se registra en `order_recovery_attempts` (cédula y HMAC de la dirección).
- El envío usa un servidor SMTP configurado en `backend/.env` (`SMTP_HOST`, `SMTP_PORT`,
  `SMTP_SECURITY`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_SENDER`) mediante `smtplib`, sin
  dependencias nuevas, desde `modules/orders/infrastructure/mailer.py`. Sin `SMTP_HOST`, la
  recuperación responde 503 `RECOVERY_UNAVAILABLE`. El envío ocurre fuera de la petición para
  no revelar por el tiempo de respuesta si la cédula tiene pedidos.
- La dirección del cliente llega al backend por la cabecera `X-Client-IP`, que el proxy de
  Astro establece y que Flask acepta únicamente desde loopback. También alimenta los límites de
  solicitudes.
- La consulta por código reutiliza el código guardado del pedido; la recuperación no lo rota.

Tienda pública (revisión 06, aprobada e implementada el 31 de octubre de 2026): cabecera, pie y
carrusel negros, tarjetas con presentación y cantidad, y carrito como diálogo (`CartDialog.astro`,
`features/cart/dialog.ts`) con continuación al checkout. La página `/cart` se retiró. Componentes
nuevos dentro de los patrones ya autorizados: `features/catalog/{Hero,ProductCard}.astro`,
`features/catalog/{cards,hero}.ts`, `shared/components/{stepper,photos}.ts`.

Estudio de decants (2 de noviembre de 2026, aprobado por el propietario): la página de decants es
`features/catalog/DecantStudio.astro` y `studio.ts` (más `perfume.ts`), con la lista renderizada en
el servidor y actualizada sin recargar mediante la misma URL. La cotización del carrito añade por
línea `product_slug`, `image_url` y `options` (presentaciones hermanas del mismo tipo, activas y no
agotadas) para mostrar el frasco y cambiar mililitros; el stock se vuelve a validar en cada
cotización. Componentes compartidos nuevos dentro de `shared/components/`: `vial.ts`, `motion.ts`,
`AccessibilityPanel.astro` y `accessibility.ts` (preferencias en `localStorage` bajo
`beront.a11y.v1`, aplicadas como atributos `data-text`, `data-contrast` y `data-motion` de `html`;
sin scripts en línea por la política CSP). Los tamaños de letra se expresan en `rem`; el
estudio usa Container Queries en 600/840/1200/1600 px.

Carrusel de perfumes completos (2 de noviembre de 2026, aprobado): `features/catalog/CylinderPage.astro`,
`cylinder.ts` y `cylinder-layout.ts`. Comparte con el estudio de decants `StudioFilters.astro`,
`CartSummary.astro`, `liveFilters.ts`, `summary.ts` y `perfume.ts`. Se retiraron `CatalogPage.astro`,
`Hero.astro`, `ProductCard.astro`, `cards.ts`, `filters.ts` y `hero.ts`.

Ubicaciones y archivos de esta ampliación, dentro de los patrones ya autorizados:

```text
backend/bd/catalog/funciones/ y backend/bd/orders/funciones/
backend/src/beront/modules/orders/infrastructure/mailer.py
backend/tests/{integration/test_classifications.py,unit/test_mailer.py}
frontend/src/pages/[locale]/{checkout.astro,orders/index.astro}
frontend/src/pages/[locale]/admin/{settings,media,orders}/index.astro
frontend/src/features/{checkout/page.ts,orders/{page,admin}.ts,settings/page.ts,media/page.ts}
frontend/src/shared/{components/dom.ts,i18n/commerce.ts,styles/commerce.css}
frontend/tests/e2e/application-commerce.spec.ts
```

Pendientes de esta ampliación: la asignación de acordes, tipos de uso y perfiles al perfume desde
el editor administrativo y sus filtros en el catálogo público requieren un prototipo aprobado;
la API ya los admite.

## Ampliación autorizada el 27 de octubre de 2026

Las decisiones de este apartado sustituyen los límites anteriores de acceso a datos,
configuración comercial, imágenes y pedidos. El resto del documento describe la primera versión
y continúa aplicando donde no contradiga esta ampliación.

- SQLAlchemy conserva la definición única de tablas y relaciones para Alembic; la aplicación
  deja de utilizar consultas y sesiones ORM. Los modelos se organizan en
  `backend/src/beront/shared/infrastructure/modelos/<modulo>/`.
- Las funciones SQL se organizan por módulo en `backend/bd/<modulo>/funciones/`, una función por
  archivo con su definición vigente y sin carpetas de versión. Alembic las instala desde esa carpeta.
- `shared/infrastructure/pg_call.py` usa nombres de función permitidos y parámetros enlazados.
  Los endpoints delegan en casos de uso y repositorios; no construyen SQL ni aceptan destinos SQL.
- Solo existe un administrador, creado mediante CLI y protegido también por unicidad en PostgreSQL.
  No hay registro público de cuentas en este alcance.
- Categorías, marcas, públicos, presentaciones, precios, tarifas, bancos, WhatsApp y estados
  comerciales se administran desde datos persistentes. Una marca pertenece a una sola categoría.
- La semilla conserva el HTML proporcionado como fuente: 130 perfumes, 42 marcas y 400 presentaciones.
  Toda existencia inicial es cero; importar o volver a ejecutar la semilla no asigna stock.
- Las imágenes y sus URLs se registran en el backend y su biblioteca de medios. Cada perfume
  se vincula a sus imágenes importadas; las que faltan no se inventan.
- Carrito, datos/envío y pedido recibido forman un checkout con pedidos persistentes.
  Comprobantes solo en fotografía. El teléfono y las cuentas bancarias se configuran en el panel.
- No hay vencimiento ni reserva de inventario por tener un carrito o checkout incompleto.
  El inventario cambia únicamente al validar el pago. Se permiten transferencias concurrentes;
  la primera aprobación con existencias confirma la venta. Otro pago real sin stock queda
  registrado como incidencia para resolver con el propietario por WhatsApp, sin saldo negativo.
- El propietario autoriza términos de prueba durante el desarrollo local; el contenido legal
  definitivo queda para una revisión posterior.
- El seguimiento usa un código único. La recuperación mediante cédula se resuelve por correo
  (ampliación del 31 de octubre) con respuesta pública uniforme. No se muestran códigos
  públicamente al introducir una cédula.
- El envío se configura por ciudad. Una dirección vacía indica entrega en agencia; el propietario
  coordina la agencia concreta con el cliente. Galápagos y destinos insulares quedan excluidos.

Ubicaciones adicionales autorizadas por el nuevo alcance:

```text
backend/bd/{comunes,identity,catalog,inventory,media,commerce,orders}/funciones/<funcion>.sql
backend/src/beront/shared/infrastructure/modelos/{identity,catalog,inventory,media,commerce,orders}/
backend/src/beront/shared/infrastructure/{pg_call,sql_migrations}.py
backend/semillas/catalogo/{catalogo.json,imagenes/<archivo>.webp}
backend/semillas/importar_catalogo.py
backend/src/beront/modules/{media,commerce,orders}/{domain,application,infrastructure,presentation}/
frontend/src/features/{checkout,orders,settings,media}/
frontend/src/pages/[locale]/{checkout,orders}/
frontend/src/pages/[locale]/admin/{settings,media,orders}/
design/prototypes/{checkout,order-tracking,admin-settings,admin-media,admin-orders}.html
design/assets/{checkout,admin-commerce}.{css,js}
docs/IMPLEMENTATION.md
```

Los nuevos prototipos requieren aprobación antes de implementar las vistas del producto.
El frontend de una funcionalidad se desarrolla solo después de su backend completo y probado.

### Catálogos comerciales configurables

`categories` y `audiences` contienen UUID, slug estable, nombres ES/EN, activo y versión.
`presentations` contiene UUID, nombres ES/EN, tipo técnico de inventario, volumen,
activo y versión. No hay tamaños, públicos ni categorías comerciales obligatorios en código.
`brands.category_id` es una FK obligatoria; la categoría del perfume se deriva de la marca.
La respuesta `classifications` se conserva como una lista derivada de un único elemento
para compatibilidad del contrato de lectura. No se acepta como campo de escritura del perfume.

Los tipos técnicos `decant` y `full_bottle` seleccionan reglas de inventario en ml o unidades.
Cada variante referencia una presentación configurada por su clave única tipo/volumen,
protegida por FK. Slugs y tipo/volumen son inmutables; los nombres, precios y disponibilidad
siguen siendo editables. Las opciones activas y sus nombres se consultan desde la API.

API protegida de configuración: `GET/POST /api/v1/admin/catalog-options/{resource}` y
`PATCH /api/v1/admin/catalog-options/{resource}/{id}`; recursos permitidos:
`categories`, `audiences` y `presentations`. Exige permisos de catálogo y CSRF en mutaciones.
Desactivar una categoría o un público retira sus perfumes del catálogo público. Para desactivar
una presentación global hay que retirarla antes de los perfumes publicados que la utilizan.

`backend/semillas/importar_catalogo.py` valida la fuente y ejecuta el caso de uso
`catalog/application/import_seed.py`. La importación es reanudable por perfume, no sobrescribe
perfumes existentes ni reinicia saldos. Las fotografías compartidas tienen un recurso de medios
y vínculos independientes por perfume; las URLs temporales nunca se guardan como URLs de servicio.

### Comercio, checkout y pedidos

`commerce` gestiona contacto, términos, provincias, ciudades con tarifa individual y cuentas
bancarias. `orders` gestiona estados, transiciones, pedidos, líneas históricas, comprobantes,
historial e intentos de recuperación. Sus puertos se componen en `bootstrap.py` y sus tablas
se registran desde `shared/infrastructure/modelos/`. No hay integraciones bancarias automáticas.

Los nombres ES/EN, estados activos y transiciones se guardan en PostgreSQL. Los estados tienen
una fase técnica inmutable que permite aplicar las reglas de pago, despacho y cancelación;
no es una lista cerrada de nombres comerciales. Las finalidades de entrada identifican el
estado inicial de transferencia, WhatsApp y la incidencia de stock. Su configuración inicial
vive en la semilla, junto con términos identificados como texto de prueba.

```text
GET /checkout/options                         contacto, términos, destinos y bancos activos
POST /checkout/quote                          importes y cotización firmada, sin reserva
POST /orders                                  pedido pendiente y comprobante si es transferencia
POST /orders/track                            consulta por código, sin datos personales
POST /orders/recovery                         solicitud por cédula, respuesta uniforme
POST /admin/orders/{id}/approve-payment        validación y salida atómica de existencias
POST /admin/orders/{id}/transition             transición configurada, sin eludir pago
PATCH /admin/orders/{id}/shipping              guía y seguimiento manuales
POST /admin/orders/{id}/receipts               comprobantes corregidos privados
```

Prefijo común `/api/v1`. Configuración protegida: `GET/PUT /admin/settings`,
`GET/POST /admin/commerce/{provinces|cities|banks}`, edición por `PATCH` con versión,
y `GET/POST/PATCH /admin/order-flow/{statuses|transitions}`.

La cotización de checkout contiene líneas, ciudad, subtotal, envío, total, términos y bancos
mostrados. El servidor firma su representación con HMAC-SHA-256 y la clave privada de la
aplicación; nunca acepta importes del navegador sin verificar esa firma. No contiene datos
del cliente y no tiene vencimiento temporal. El cliente envía `quote_token`, identificadores,
cantidades, método de pago y sus datos. No envía precios como autoridad.

Para WhatsApp se vuelven a comprobar importes y disponibilidad antes de crear el pedido.
Para una transferencia ya realizada, se conserva la cotización firmada aunque los precios,
tarifa, cuenta bancaria o existencias hayan cambiado antes de enviar la fotografía: el pedido
se registra pendiente y recibe código. Así el dinero recibido no queda sin un pedido consultable.
Rotar `SECRET_KEY` invalida las cotizaciones anteriores, además de las sesiones; no se rotará
durante una compra de prueba sin advertir esa consecuencia.

Los pedidos usan un código aleatorio de 144 bits, índice único, solicitud de creación idempotente
y snapshots de precios, envío, banco y términos. No se reserva ni descuenta stock al cotizar,
crear pedidos, subir imágenes o abrir WhatsApp. No hay tareas de vencimiento de pedidos.

La aprobación bloquea el pedido, los perfumes y los saldos en orden estable. Agrupa ml por
perfume y unidades por presentación; comprueba todas las líneas antes de modificar alguna.
Saldos, movimientos, confirmación, historial y auditoría se confirman en la misma transacción.
Repetir la aprobación no vuelve a descontar. Dos pedidos por la última existencia producen una
confirmación y una incidencia de pago sin stock; esta última no genera movimientos parciales.

Una transición ordinaria no confirma pagos ni permite despachar sin pago validado y guía.
Cancelar un pedido sin venta confirmada no toca inventario porque no hubo reserva. Devoluciones
de ventas ya confirmadas y reembolsos automáticos no forman parte del alcance autorizado.
Un comprobante corregido puede añadirse a la historia sin cambiar el pago ni el stock.

Los comprobantes se normalizan como imágenes privadas de tipo `receipt`; no aparecen en la
biblioteca pública de perfumes ni se pueden vincular como fotos de productos. El seguimiento
devuelve estado, selección, importes y guía; omite cédula, dirección, teléfono, correo y archivos.
La recuperación responde igual haya o no coincidencias y nunca devuelve códigos al
solicitante: los envía por correo al contacto registrado del pedido.

Permisos nuevos: `commerce:write`, `orders:read`, `orders:manage`, `orders:approve_payment`.
Todos los endpoints administrativos exigen decoradores de autenticación y permiso; mutaciones
administrativas y creación/recuperación públicas exigen CSRF. Solo cotización y consulta por
código están exentas como lecturas. Hay límites de solicitudes, origen fijo y `no-store`.
Las imágenes admiten hasta 5 MiB; los mensajes JSON mantienen el límite de 64 KiB.

El frontend dispone de proxy de destino fijo para `/checkout` y `/orders`, con límites de
carga, cookies y CSRF preservados. Las páginas de checkout, seguimiento, configuración,
biblioteca y pedidos se implementaron el 31 de octubre de 2026 a partir de los prototipos
aprobados (revisiones 04 y 05).

## Resumen

Catálogo bilingüe ES/EN de decants y perfumes completos, filtros, carrito local y continuación por WhatsApp.
Administración de perfumes, casas, fotografías, presentaciones, precios, disponibilidad e inventario.
Decants: saldo compartido de ml por perfume. Botellas: unidades por presentación.
Abrir WhatsApp no crea una venta, no reserva y no descuenta existencias.
Visitantes sin cuenta; administradores con contraseña; USD; America/Guayaquil.
Envíos al Ecuador continental, excluyendo Galápagos según la política indicada por el propietario.
Sin pedidos persistentes, pagos, cuentas de clientes, traducción automática ni cálculo de envíos.

## A. Arquitectura global

### Backend
Monolito modular Flask con PostgreSQL:
- identity: administradores, sesiones revocables y permisos.
- catalog: productos, casas, clasificaciones, descripciones ES/EN, imágenes y presentaciones.
- inventory: saldos, movimientos manuales e idempotencia.
- cart: cotización y enlace WhatsApp; no persiste carritos ni pedidos.

Cada módulo tiene domain, application, infrastructure y presentation.
Dominio: biblioteca estándar y reglas puras; no importa Flask, SQLAlchemy ni Pydantic.
Aplicación: casos de uso, puertos, DTO y unidades de trabajo; sin HTTP.
Infraestructura: ORM y adaptadores; convierte explícitamente a entidades/DTO.
Presentación: validación HTTP, autorización y serialización; sin consultas ORM.
bootstrap.py compone dependencias sin contenedor de inyección.
Los repositorios no hacen commit; el caso de uso confirma una unidad de trabajo.
Los módulos se comunican por contratos, nunca mediante modelos ORM ajenos.

### Frontend
Astro SSR, TypeScript y Tailwind; funcionalidades catalog, cart, identity y admin.
Sin frameworks de componentes adicionales. Componentes Astro y scripts TypeScript.
Formularios GET conservan filtros y ordenamiento en la URL.
localStorage conserva únicamente identificadores de presentación y cantidades.
El servidor determina precios, stock y permisos.
Adaptador @astrojs/node; runtime Bun explícito con bunx --bun astro.
La compatibilidad se verifica antes de desarrollar vistas.
Referencias: https://docs.astro.build/en/guides/on-demand-rendering/
y https://bun.com/guides/ecosystem/astro .

### Comunicación
Navegador -> Astro/Bun localhost:4321 -> Flask 127.0.0.1:5000 -> PostgreSQL.
Astro proporciona proxy de destino fijo para /api/* y /media/*.
Conserva cookies, códigos y cabeceras; prohíbe destinos controlados por el usuario.
SSR reenvía cookies exclusivamente al backend configurado.
Tiempos de espera y errores controlados en todas las llamadas.

### Datos
UUID; precios NUMERIC(12,2)/Decimal; ml NUMERIC(12,2)/Decimal; unidades enteras.
Fechas UTC; visualización America/Guayaquil.
- Brand: nombre, estado, versión.
- Product: casa, nombre, slug, clasificaciones multiselección, público, descripciones ES/EN,
  estado de publicación, archivo y agotado manual.
- Variant: perfume, decant/full_bottle, volumen, precio propio, activo, agotado y versión.
- Image: perfume, archivo generado, orden y textos alternativos ES/EN.
- DecantStock: perfume, ml y versión.
- BottleStock: presentación, unidades y versión.
- Movement: existencia, delta, motivo, administrador, fecha y clave única de operación.
- Administrator: usuario, hash y estado.
- AdminSession: administrador, identificador protegido, expiración y revocación.
- AuditEvent: actor, acción, recurso, fecha y request_id.

Un perfume ofrece ambos tipos sin duplicar ficha. Tamaños iniciales sugeridos 3, 5 y 10 ml,
editables mediante nuevas presentaciones; nunca una lista cerrada del backend.
El tipo y volumen de una presentación son inmutables: desactivar y crear otra para cambiarlos.
El precio sí es editable. No hay conversión automática de precio por ml.
Clasificaciones: arabic, designer, niche, combinables. Público: male, female, unisex.
Descripción inglesa ausente: mostrar española con lang=es.
Archivar, no borrar productos con historial.
Restricciones, índices, unicidad, FK y checks se declaran en modelos ORM.
SQLAlchemy es la única fuente del esquema; Alembic autogenera migraciones revisadas.
No create_all ni modificaciones manuales de tablas, incluso en pruebas.
Referencia: https://alembic.sqlalchemy.org/en/latest/autogenerate.html .

### Inventario
Disponible = producto publicado y no archivado + presentación activa + ninguna marca de agotado
+ existencia suficiente. Una marca manual prevalece sobre un saldo positivo.
Quitar agotado no hace disponible un saldo cero; marcar agotado no modifica saldo.
Decants agregan cantidad * volumen por perfume antes de comprobar el saldo compartido.
Botellas usan unidades independientes.
Ajustes manuales tras la venta: motivo obligatorio, auditoría, idempotencia y transacción.
Nunca saldo negativo; control de versión para cambios concurrentes.
Una venta de botella parcial retira una unidad completa y permite marcar esa presentación agotada.
No se incorpora venta de botellas parciales ni conversión automática entre botellas y ml.

## B. Patrones

| Patrón | Implementación | Función |
|---|---|---|
| Strategy (GoF) | DecantStockPolicy / BottleStockPolicy | Validación por ml o unidades. |
| Adapter (GoF) | LocalImageStorage / ImageStorage | Separar almacenamiento del negocio. |
| Facade (GoF) | CatalogQueryFacade | Componer producto, presentaciones y disponibilidad. |
| Repository | Repositorios de cada módulo | Mapear ORM a dominio/DTO. |
| Unit of Work | Unidad de trabajo SQLAlchemy | Atomicidad con commit explícito de aplicación. |

Repository y Unit of Work no se clasifican como GoF.

## C. Principios y herramientas

DRY: modelos ORM para esquema; inventory/domain para disponibilidad; cart para importes;
schemas HTTP para contratos; permisos backend para autorización; tokens para estilos;
diccionarios ES/EN para interfaz. No exportar modelos ORM.
SRP: controladores validan y delegan; aplicación coordina; repositorios persisten.

Stack obligatorio: PostgreSQL, Python/Flask/uv, SQLAlchemy 2.x, Alembic, Astro/Bun y Tailwind.
Complementos aprobados:
- psycopg: driver PostgreSQL.
- Pydantic: contratos HTTP.
- Flask-WTF: CSRF.
- Flask-Limiter: límites locales en memoria.
- Pillow: validar/recodificar fotografías y retirar metadatos.
- pytest/pytest-cov: pruebas y cobertura.
- Ruff: lint y formato Python.
- TypeScript/astro check: tipos.
- ESLint/Prettier con plugins Astro: calidad frontend.
- Bun Test: unidades frontend.
- Playwright: navegador, responsividad y permisos.
- pip-audit/bun audit: vulnerabilidades.
- @tailwindcss/vite: estilos.
- python-dotenv: carga local de .env por Flask CLI; no sustituye la validación de configuración.

Versiones estables compatibles fijadas en uv.lock y bun.lock.
Sin microservicios, Redis, colas, motor de búsqueda externo, GraphQL, CMS ni contenedor DI.
Búsqueda PostgreSQL parametrizada y paginada; ampliar solo tras mediciones y aprobación.

## D. Organización autorizada

```text
/
├── AGENTS.md, CLAUDE.md, .gitignore, README.md, project_memory.md
├── docs/
│   ├── ARCHITECTURE.md                 # Arquitectura aprobada
│   ├── LOCAL.md                        # Configuración y verificación local
│   ├── reporte.md                      # Estado del backend revisado, solicitado por el propietario
│   └── DESIGN_APPROVALS.md             # Revisiones y decisiones visuales
├── design/
│   ├── README.md, tokens.css
│   ├── assets/                         # Referencias, fuentes y recursos de prototipos
│   ├── prototypes/
│   │   ├── catalog.html, product.html, cart.html
│   │   └── login.html, admin-catalog.html, admin-inventory.html
│   └── reviews/                        # Capturas por viewport
├── backend/
│   ├── .gitignore, .env.example, .python-version, pyproject.toml, uv.lock
│   ├── alembic.ini
│   ├── bd/<modulo>/funciones/<funcion>.sql
│   ├── migrations/env.py, script.py.mako, versions/<revision>.py
│   ├── src/beront/
│   │   ├── __init__.py, app.py, bootstrap.py, config.py, cli.py
│   │   ├── shared/
│   │   │   ├── domain/                 # Errores y valores comunes
│   │   │   ├── application/            # Contratos de UoW/auditoría
│   │   │   ├── infrastructure/         # Base ORM, SQL, logs
│   │   │   └── presentation/           # Validación, cabeceras y errores
│   │   └── modules/{identity,catalog,inventory,cart}/
│   │       ├── domain/entities.py, policies.py, errors.py
│   │       ├── application/contracts.py, <use_case>.py
│   │       ├── infrastructure/models.py, repositories.py, <adapter>.py
│   │       └── presentation/routes.py, schemas.py, serializers.py
│   ├── tests/conftest.py
│   ├── tests/{unit,integration,architecture,migrations}/
│   └── var/{uploads,staging,logs}/
└── frontend/
    ├── .gitignore, .env.example, package.json, bun.lock
    ├── astro.config.mjs, tsconfig.json, eslint.config.js
    ├── prettier.config.mjs, playwright.config.ts
    ├── public/{brand,fonts}/
    ├── src/env.d.ts, middleware.ts
    ├── src/pages/index.astro, 404.astro
    ├── src/pages/api/[...path].ts, media/[...path].ts
    ├── src/pages/[locale]/index.astro, cart.astro
    ├── src/pages/[locale]/catalog/decants.astro, full-bottles.astro
    ├── src/pages/[locale]/products/[slug].astro
    ├── src/pages/[locale]/admin/login.astro, index.astro, inventory.astro
    ├── src/pages/[locale]/admin/products/index.astro, new.astro, [id].astro
    ├── src/features/{catalog,cart,identity,admin}/
    ├── src/shared/{components,layouts,http,i18n,styles}/
    └── tests/{unit,e2e}/
```

Los paquetes incluyen __init__.py. Se permiten archivos Python por responsabilidad dentro de
las capas, componentes .astro y lógica .ts dentro de funcionalidades y archivos de pruebas
en las ubicaciones designadas. cart no tiene modelos/repositories propios.
No añadir ubicaciones sin aprobación. Los artefactos de gestores/build son ignorados.

### Catálogo importado (retirado)

La demostración con datos e imágenes del HTML del propietario se retiró del frontend el
1 de noviembre de 2026 (`frontend/public/temporal/`, `frontend/src/pages/temporal/`,
`frontend/src/features/catalog/temporary.ts`, la excepción de middleware y sus pruebas). La
única fuente de perfumes es la semilla `backend/semillas/catalogo/`, que se importa con
`uv run beront importar-catalogo`. Su versión vigente y conteos se definen en el apartado
«Semilla canónica del catálogo final»; los 130 perfumes y 132 fotografías originales quedan
como antecedente histórico sustituido.

## E. Flujo y contratos

Selección de presentación -> carrito local (variant_id, quantity) -> POST /cart/quote ->
validación HTTP -> BuildCartQuote -> CatalogQueryFacade -> repositorios ->
validación agregada de stock -> cálculo Decimal -> resumen/enlace.
Antes de abrir WhatsApp se cotiza otra vez. Cambios de precio requieren nueva confirmación
visible; falta de stock bloquea la continuación. Nunca vaciar carrito por abrir WhatsApp.

Todas las rutas siguientes llevan prefijo /api/v1:
- GET /catalog/products, /catalog/products/{slug}, /catalog/facets.
- POST /cart/quote.
- GET /auth/csrf, POST /auth/login, POST /auth/logout, GET /auth/session.
- GET/POST /admin/products, GET/PATCH /admin/products/{id}.
- POST /admin/products/{id}/variants, PATCH /admin/variants/{id}.
- GET/POST /admin/brands, PATCH /admin/brands/{id}.
- POST /admin/products/{id}/images, PATCH/DELETE /admin/images/{id}.
- GET /admin/inventory, /admin/inventory/movements, POST /admin/inventory/adjustments.
- GET /media/{archivo} queda fuera de /api/v1 y verifica visibilidad.

Entrada de carrito:
```json
{"locale":"es","items":[{"variant_id":"d4f8c5e0-5d30-43d4-89d2-cd7aa94101af","quantity":2}]}
```
Salida: data.currency, data.items (id, marca, producto, tipo, volume_ml, quantity, unit_price,
line_total), data.total, data.whatsapp_url.
Importes y ml como cadenas decimales; nunca confiar en precios enviados por el navegador.
Máximo 20 presentaciones distintas y 1..20 unidades tras consolidar duplicados.
Mensaje: marca, perfume, tipo, ml, cantidad, subtotales, total de productos.
Envío no incluido, se coordina por WhatsApp. Sin nombre ni dirección del cliente.
WHATSAPP_NUMBER internacional configurado, sin valor inventado.
Si falta, cotizar sigue siendo posible; enlace nulo y aviso de configuración controlado.

Errores:
```json
{"error":{"code":"INSUFFICIENT_STOCK","message":"La disponibilidad ha cambiado.","details":[{"field":"items","variant_id":"...","code":"UNAVAILABLE_QUANTITY"}],"request_id":"..."}}
```
HTTP: 200 lectura/edición/cotización; 201 creación; 204 logout/eliminación de imagen;
400 JSON; 401 sesión; 403 permisos/CSRF; 404 no visible/inexistente; 409 conflicto/stock/duplicado;
413 tamaño; 415 MIME; 422 validación; 429 límites; 500 inesperado; 503 dependencia/configuración.
La interfaz interpreta code, no message. Ediciones requieren versión actual.

Filtros: q, kind, brand_id, classification, audience, volume_ml, min_price, max_price,
available, sort, page, page_size, locale.
AND entre dimensiones; OR entre valores de una dimensión. Precio/tamaño deben coincidir
en la misma presentación. Precio desde y ordenamiento usan las presentaciones coincidentes.
Agotados visibles salvo filtro available. Orden name, price_asc, price_desc.
Página 24, máximo 48. Rechazar parámetros desconocidos. Nombre/casa en búsqueda textual.

## F. OWASP Top 10:2025

Referencia: https://top10.owasp.org/2025/ .

| Categoría | Amenaza | Mitigación | Capa/módulo |
|---|---|---|---|
| A01 acceso | Edición/lectura privada o proxy manipulado | Decoradores, recursos visibles y destino fijo | identity/presentation; middleware/proxy |
| A02 configuración | Debug, secretos, CORS, recursos ilimitados | Validación, loopback, debug off, límites/cabeceras | config; shared/presentation |
| A03 suministro | Dependencias/script vulnerable | Locks, auditorías, revisión de scripts | Manifiestos y controles |
| A04 criptografía | Contraseña legible/cookie falsa | scrypt, secreto aleatorio, sesiones revocables | identity/infrastructure |
| A05 inyección | SQL/XSS/cargas activas | Parametrización, allowlists, texto escapado, recodificación | Repositorios, esquemas, Astro |
| A06 diseño | Totales falsos, saldo compartido, venta ficticia | Autoridad backend y separación consulta/venta | cart/inventory |
| A07 autenticación | Fuerza bruta/fijación/reutilización | Límites, mensajes genéricos, rotación y expiración | identity y limiter |
| A08 integridad | Reintentos/sobrescrituras/manipulación local | Versiones, idempotencia, constraints, UoW | Aplicación e infraestructura SQL |
| A09 registros | Cambios/intrusiones invisibles | Auditoría, logs sin secretos, request_id, alertas locales | shared e identity/inventory |
| A10 excepciones | Actualización parcial/fail-open | Rollback, timeout, fail-closed y errores uniformes | UoW, HTTP, clientes |

CSRF en login/logout y mutaciones admin; quote público exento.
JSON máximo 64 KiB. Imagen JPEG/PNG/WebP máximo 5 MiB y 20 MP, cinco por perfume.
Prohibir SVG subido; SVG de iconos/marca revisado como recurso del proyecto.
Generar nombres en servidor, recodificar y retirar EXIF/metadatos. Archivos fuera del código.
Fotografías de borradores/archivados solo para admin.
Cabeceras CSP, nosniff, referencias y anti-iframe; excepciones de desarrollo solo loopback.
Cache-Control no-store para administración, sesión y carrito.
PostgreSQL: rol runtime sin DDL; rol de migraciones separado.
HTTP y cookie Secure=false únicamente en perfil local; no configuración pública.
Referencia: https://flask.palletsprojects.com/en/stable/web-security/ .

## G. Autorización

| Acción | Visitante | Administrador |
|---|---|---|
| Consultar catálogo publicado, buscar y filtrar | Sí | Sí |
| Cambiar idioma y administrar su carrito local | Sí | Sí |
| Obtener resumen y enlace de WhatsApp | Sí | Sí |
| Consultar borradores y productos archivados | No | Sí |
| Crear y editar productos, casas y presentaciones | No | Sí |
| Publicar, archivar y marcar agotado | No | Sí |
| Gestionar fotografías | No | Sí |
| Consultar saldos y movimientos | No | Sí |
| Registrar ajustes de existencias | No | Sí |

Visitante: catálogo publicado, filtros, idiomas, carrito y WhatsApp.
Admin: lo anterior más privado, CRUD/archivo, fotografías, agotado, saldos y movimientos.
Permisos fijos: catalog:read_private, catalog:write, inventory:read, inventory:adjust.
Rol admin tiene todos; no editor de roles.
Cada endpoint protegido aplica require_auth y require_permission.
Sesión firmada de Flask con ID opaco; registro servidor con hash del identificador.
30 min inactivo, 8 h absoluto; login renueva ID; logout revoca y limpia cookie;
reset de contraseña revoca todas las sesiones.
Alta/reset mediante CLI con entrada oculta, sin credenciales predeterminadas ni correo.
Frontend middleware consulta sesión antes de renderizar admin.
Fallo de backend no revela contenido privado. Controles se guían por permisos del backend.
No tokens en localStorage.

## H. Prototipos y accesibilidad

Tokens: blanco principal #F8F8F8, negro secundario #0B0B0B, champán #B8A58A.
Botón champán con texto negro; no texto pequeño champán sobre blanco.
Tailwind @theme centraliza tokens. Fuente Cormorant Garamond para títulos y
Source Sans 3 para lectura/controles, locales con licencias.
Fotografía principal, jerarquía perfume/casa/presentación/precio.
Logo original pendiente; identificar cualquier representación provisional.
Solo SVG para iconos, cero emojis.

Prototipos HTML/CSS en design/, aprobados por vista y revisión antes de implementar.
Vistas: catálogo/filtros/vacíos/agotados, ficha, carrito/errores, login,
edición de catálogo y movimientos de inventario.
Revisar móvil/escritorio, teclado, estados y ES/EN.
docs/DESIGN_APPROVALS.md registra revisión, fecha y referencia verificable.

Mínimo 320 px; breakpoints 640/768/1024/1280.
Rangos de referencia de diseño (regla 10 de AGENTS.md): compacto <600, mediano 600-839,
expandido 840-1199, grande 1200-1599 y extragrande >=1600; los breakpoints de
implementación anteriores se mantienen hasta que el propietario apruebe ajustarlos.
Pruebas 360/390/768/1024/1440, más un ancho extragrande (1920); panel de accesibilidad
(texto, contraste, animaciones); panel móvil y lateral escritorio;
formularios de una columna en móvil, sin desbordamiento, objetivos 44 px,
foco visible, contraste AA, movimiento reducido.
Chromium, Firefox y WebKit.

## I. Archivos de reglas y exclusiones

Los contenidos completos se reproducen al final de este documento.
Los locks y las migraciones se conservan; design/ se ignora en la raíz.

## J. Secuencia y aceptación

0. AGENTS, tres gitignore, estructura y arquitectura.
1. Fundamentos, manifiestos/locks, configuración SQL/Alembic, UoW, errores, compatibilidad.
2. identity backend completo con CSRF, permisos, expiración y revocación probados.
3. catalog backend: CRUD, fotografías, traducciones, presentaciones, búsqueda.
4. inventory backend: ml/unidades, historial, ajustes atómicos, idempotencia, agotado.
5. cart backend: precios/stock agregados y enlace sin mutaciones.
6. Prototipos concretos para aprobación explícita por vista.
7. Frontend integrado solo con backend terminado y prototipo aprobado.
8. Verificación integral y documentación local; sin despliegue.

Pruebas obligatorias:
- Tamaños no predefinidos; precisión Decimal; saldo compartido; límites y cantidades inválidas.
- Agotado prevalece; saldo cero no se vuelve disponible; botellas/ml separados.
- Alembic desde vacío, ausencia de drift, PostgreSQL real; no create_all.
- Conflictos de versión, idempotencia y rollback integral.
- Sin borradores/stock exacto/campos administrativos en API pública.
- Mismo variant para filtros precio/tamaño.
- Acceso sin sesión/permiso/CSRF rechazado.
- Cargas falsas/excesivas/rutas manipuladas rechazadas.
- No confianza en navegador; recotización; fallos preservan carrito;
  no descuento por quote/WhatsApp; codificación; teléfono ausente controlado.
- Persistencia entre idiomas/recargas y fallback en memoria.
- ES/EN, sesión vencida, historial de filtros, vacíos/errores y teclado/responsividad.
Cobertura objetivo: 90% ramas dominio/aplicación; 80% global backend.
Los escenarios críticos no se sustituyen por porcentajes.

Pendientes de contenido: número WhatsApp, marca original y catálogo real.
No inventar esos datos. Fixtures/prototipos se identifican expresamente como demostración.
No declarar terminada la versión completa sin frontend aprobado, integrado y verificado.


### AGENTS.md

```text
# Reglas de trabajo de BÉRONT

## 1. Arquitectura
Cumplir docs/ARCHITECTURE.md.
No cambiar arquitectura, contratos estructurales, stack ni límites de módulos
sin aprobación previa y explícita del propietario.
Si una instrucción nueva contradice la arquitectura, señalar la contradicción
y resolverla antes de implementar.

## 2. Organización de archivos
Crear archivos únicamente en las ubicaciones y patrones autorizados por
docs/ARCHITECTURE.md.
Proponer y obtener aprobación antes de añadir una ubicación nueva.
No crear carpetas auxiliares fuera de esa organización.

## 3. Separación de capas
El dominio no depende de Flask, SQLAlchemy, Pydantic ni del frontend.
Los modelos de tablas pertenecen a infraestructura/modelos y se usan para metadata y Alembic.
El acceso a datos de la aplicación utiliza funciones PostgreSQL mediante pg_call.py,
invocado por repositorios de infraestructura; no utilizar sesiones ORM para leer o escribir.
Los repositorios traducen resultados SQL a entidades o DTO de aplicación.
Los controladores no contienen reglas comerciales ni llamadas SQL directas.
No acceder directamente a los modelos internos de otro módulo.

## 4. Comentarios
Usar comentarios breves y técnicos solo para lógica no evidente,
decisiones de seguridad o workarounds justificados.
No añadir comentarios narrativos, históricos o que repitan el código.
No explicar en comentarios que un cambio se hizo por una petición o un bug.

## 5. Git
No ejecutar commit, push, merge, creación de ramas ni operaciones que
modifiquen el historial o el remoto sin solicitud explícita del propietario.
No inicializar Git ni usar generadores que lo hagan automáticamente.
Crear los .gitignore aprobados no autoriza otras operaciones de Git.

## 6. Archivos temporales
Eliminar al terminar los scripts, pruebas exploratorias y datos temporales
creados para la tarea.
Mantener las pruebas permanentes aprobadas.
No eliminar archivos del usuario, fotografías reales ni datos de negocio
como parte de una limpieza.
Usar directorios temporales del sistema o ubicaciones aprobadas.

## 7. Autorización
Aplicar decoradores reutilizables de autenticación y permisos en cada
endpoint protegido.
Verificar autorización y acceso al recurso en el backend.
Proteger rutas, páginas y controles en el frontend según la sesión
y los permisos devueltos por el backend.
Nunca considerar el frontend una barrera de seguridad suficiente.

## 8. Orden de desarrollo
No implementar el frontend de una funcionalidad mientras su backend
no esté completo de punta a punta.
Esto incluye dominio, casos de uso, repositorios, endpoints, validaciones,
permisos, errores, migraciones necesarias y pruebas.
No dejar backend pendiente para después.

## 9. Diseño
Crear los prototipos dentro de design/.
No implementar una vista del producto sin aprobación explícita de su
prototipo vigente.
Registrar las aprobaciones en docs/DESIGN_APPROVALS.md.
La aprobación de arquitectura no equivale a aprobación visual.
Respetar los tokens y la identidad visual aprobados.

## 10. UX/UI, accesibilidad y responsividad
Aplica a los diseños ya aceptados (de forma retroactiva), a los prototipos nuevos
y al proyecto final. Son obligatorios los estándares de UX/UI, usabilidad,
accesibilidad y diseño responsivo y adaptativo.

Versiones por dispositivo:
- Cada prototipo incluye versiones adaptadas para Android, iPhone (iOS), tablets,
  laptops, computadoras de escritorio, monitores LCD, televisores y otros
  dispositivos compatibles.
- Si una propuesta tiene alternativas (A, B, C, etc.), cada una dispone de sus propias
  versiones responsivas y conserva su identidad visual, estructura y funcionalidades.
  No basta con adaptar la alternativa elegida ni mostrar solo la versión de escritorio.

Rangos de ancho de referencia (dp, pt o píxeles CSS según la plataforma):
compacto (menos de 600), mediano (600-839), expandido (840-1199),
grande (1200-1599) y extragrande (1600 en adelante). Pueden ajustarse según el
contenido real y el framework. El diseño se adapta a resoluciones, orientaciones y
métodos de interacción (táctil, puntero, teclado, control remoto), reorganizando
los elementos sin desbordamientos, superposiciones ni pérdida de funcionalidades.

Implementación responsiva:
- Respetar la arquitectura, los patrones, las convenciones y las tecnologías del
  proyecto. En aplicaciones nativas, usar los mecanismos adaptativos del framework.
- Priorizar componentes reutilizables, Design Tokens centralizados, CSS Grid, Flexbox,
  unidades relativas, clamp() y Container Queries cuando correspondan.
- Usar Media Queries solo cuando estén justificadas; evitar su proliferación,
  duplicación y dispersión.
- No introducir parches CSS acumulativos, valores arbitrarios, !important injustificado,
  estilos redundantes ni cambios arquitectónicos innecesarios.
- Reutilizar componentes y estilos compartidos sin perder las diferencias visuales
  entre alternativas.

Accesibilidad:
- Botón o panel de accesibilidad visible, consistente y funcional en todas las
  versiones, con ajuste del tamaño del texto, mejora del contraste y reducción de
  animaciones, sin sustituir las herramientas nativas de accesibilidad.
- Cumplir WCAG 2.2 nivel AA: legibilidad, navegación por teclado, lectores de pantalla,
  controles táctiles accesibles, foco visible, etiquetas y contraste, y navegación con
  control remoto en televisores.
- Mantener coherencia visual, jerarquía de contenidos y experiencia consistente entre
  dispositivos.

Proceso:
- Usar la skill interna /design, cuando esté disponible, al crear, evaluar, mejorar e
  implementar diseños.
- Antes de modificar una interfaz, analizar la arquitectura y las soluciones existentes
  para evitar duplicaciones, regresiones y cambios innecesarios.
- Verificar los tamaños y navegadores definidos en la arquitectura y los rangos de
  referencia, en cada prototipo y alternativa, antes de darlos por terminados.
  No dar una vista por terminada si falla en alguno de ellos.

## 11. Iconografía
Usar exclusivamente iconos SVG revisados.
No utilizar emojis en interfaz, código, commits ni documentación.
Las fotografías de productos no se consideran iconos.

## 12. Incertidumbres
Preguntar antes de implementar una decisión de negocio ambigua o un cambio
no cubierto por la arquitectura aprobada.
No inventar productos reales, precios, teléfonos, políticas comerciales
ni credenciales.
Las decisiones técnicas ya aprobadas no requieren confirmación repetida.

## 13. Esquema de base de datos
Los modelos SQLAlchemy son la única fuente de verdad del esquema.
Modificar el esquema exclusivamente mediante migraciones Alembic
generadas desde los modelos y revisadas antes de aplicarlas.
No alterar tablas manualmente.
No usar create_all para crear el esquema, tampoco en pruebas.
No editar migraciones ya aplicadas; crear una nueva migración correctiva.

## 14. Inventario y carrito
Usar Decimal para dinero y mililitros.
El backend determina precios, totales y disponibilidad.
La marca manual de agotado prevalece sobre existencias positivas.
El carrito y el checkout incompleto no vencen, no reservan y no descuentan inventario.
Crear un pedido pendiente no equivale a confirmar un pago.
Solo la validación del pago por el administrador permite registrar una salida de inventario.
La primera aprobación con existencias obtiene el stock. Un pago real sin existencias
queda como incidencia para coordinar por WhatsApp, sin movimientos parciales ni saldos negativos.
Conservar la cotización firmada de una transferencia ya realizada aunque cambien precios
o disponibilidad antes de enviar el comprobante; registrarla no confirma la venta.
Los estados y transiciones del pedido se configuran en PostgreSQL y en el panel,
sin permitir que una etiqueta de estado omita las comprobaciones de pago e inventario.
Registrar ajustes de existencias con motivo, actor e idempotencia.
El propietario autorizó pedidos persistentes, revisión manual de transferencias,
pago coordinado por WhatsApp y seguimiento; no introducir cobros automáticos.

## 15. Seguridad y dependencias
Aplicar las diez categorías OWASP documentadas.
No guardar secretos en código, documentación, registros ni ejemplos.
No exponer contraseñas, cookies o tokens en mensajes de error.
Mantener uv.lock y bun.lock.
Justificar dependencias nuevas y consultar las que alteren la arquitectura
o añadan capacidades no aprobadas.

## 16. Verificación y cierre
Ejecutar las comprobaciones pertinentes antes de declarar terminado.
Informar qué cambió, qué se verificó y cualquier limitación real.
No afirmar que una prueba pasó si no se ejecutó.
Actualizar documentación cuando cambie un contrato aprobado.
Trabajar solo en ejecución local durante esta etapa.

## 17. Servidores locales y migraciones
No detener, reiniciar ni reemplazar los servidores de backend y frontend que el
propietario tenga levantados.
Para revisar o probar, usar el backend del propietario y levantar otro servidor de
frontend en un puerto libre; detenerlo al terminar.
Las pruebas que necesiten datos propios (existencias, pedidos) usan una base y
servidores temporales, nunca la base del propietario.
Las migraciones Alembic que requieran los cambios propios se generan desde los
modelos, se revisan y se aplican a la base local sin pedir confirmación adicional;
siguen vigentes las reglas del apartado 13.
```


### .gitignore

```text
/design/

.env
.env.*
!.env.example

*.log
*.tmp
*.swp
*~

.DS_Store
Thumbs.db
Desktop.ini

.idea/
.vscode/

```


### backend/.gitignore

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
.coverage.*
htmlcov/
coverage.xml
build/
dist/
*.egg-info/
.env
.env.*
!.env.example
/var/

```


### frontend/.gitignore

```text
node_modules/
.astro/
dist/
coverage/
playwright-report/
test-results/
.env
.env.*
!.env.example
*.tsbuildinfo
.eslintcache

```
