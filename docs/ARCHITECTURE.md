# BÉRONT — Arquitectura técnica de la primera versión

Estado: arquitectura aprobada por el propietario el 23 de octubre de 2026.
Entorno: ejecución local. Despliegue fuera de alcance.
La aprobación arquitectónica no aprueba los prototipos visuales.

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

Ubicaciones y archivos de esta ampliación, dentro de los patrones ya autorizados:

```text
bd/catalog/funciones/v0004/ y bd/orders/funciones/v0003/
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
- Las funciones SQL se organizan por módulo y versión en `bd/<modulo>/funciones/vNNNN/`,
  una función por archivo. Alembic instala versiones inmutables y verifica sus huellas.
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
bd/{comunes,identity,catalog,inventory,media,commerce,orders}/funciones/vNNNN/<funcion>.sql
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
├── AGENTS.md, .gitignore, README.md
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

### Excepción temporal autorizada: catálogo importado

El propietario autorizó el 25 de octubre de 2026 una demostración con datos e imágenes
de su HTML, antes de conectar el catálogo comercial. Esta excepción permite conservar
los recursos de la demostración hasta completar su migración; no son archivos de limpieza.

Ubicaciones adicionales autorizadas para esta demostración:
- `frontend/public/temporal/`: catálogo JSON, fotografías WebP y README de transición.
- `frontend/src/pages/temporal/[...path].ts`: servidor local del prototipo y API simulada.
- `frontend/src/features/catalog/temporary.ts`: consultas y cotización de demostración.
- `design/prototypes/catalog-import.html`: prototipo con el catálogo proporcionado.
- `design/assets/catalog-import.js` y `catalog-import.css`: interacción y ajustes del prototipo.
- `design/prototypes/catalog-refined.html` y `design/assets/catalog-refined.{js,css}`:
  nueva revisión solicitada, con controles, fondos y recorrido simplificados.
- `docs/TEMPORARY_CATALOG.md`: origen, límites y procedimiento de retirada.

El prototipo se sirve en `/temporal/` únicamente durante desarrollo local. Usa peticiones
HTTP a `/temporal/api/v1/` y URLs de imágenes `/temporal/media/`. La aplicación y los
contratos Flask reales conservan su comportamiento. No simula autenticación administrativa,
no escribe en PostgreSQL y no envía conversaciones de WhatsApp. La ausencia de inventario
numérico en el archivo se conserva como disponibilidad sin confirmar.
La revisión visual importada se somete a aprobación; no sustituye la revisión 01 aprobada.

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
Pruebas 360/390/768/1024/1440; panel móvil y lateral escritorio;
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

## 10. Responsividad y accesibilidad
Verificar los tamaños y navegadores definidos en la arquitectura.
Mantener navegación por teclado, foco visible, etiquetas y contraste.
No dar una vista por terminada si falla en los tamaños acordados.

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
