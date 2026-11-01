# Reporte del backend de BÉRONT

Este documento conserva la auditoría del 26 de octubre y el alcance anterior.
La ampliación del 27 de octubre está en ejecución y se registra en
[IMPLEMENTATION.md](IMPLEMENTATION.md). Sus avances y pendientes sustituyen
las cifras y decisiones históricas de este reporte cuando difieran.

Fecha de revisión: **26 de octubre de 2026**, zona de referencia `America/Guayaquil`.
Ámbito: código, configuración, persistencia, contratos HTTP, seguridad, pruebas y estado local.
Documentos de referencia: [arquitectura](ARCHITECTURE.md), [ejecución local](LOCAL.md) y
[catálogo temporal](TEMPORARY_CATALOG.md).

## 1. Estado actual

El backend tiene implementados los cuatro módulos del alcance: identidad administrativa,
catálogo, inventario y cotización del carrito con enlace WhatsApp. Su comportamiento se
verificó contra PostgreSQL temporal. **La instancia comercial local todavía no está inicializada.**

| Área | Estado comprobado |
|---|---|
| Código de la aplicación | Monolito modular Flask con capas separadas y 24 operaciones HTTP registradas. |
| Pruebas del backend | 82 aprobadas; ninguna fallida ni omitida. |
| Cobertura global, líneas y ramas combinadas | 96,53 %. |
| Cobertura de ramas de dominio y aplicación | 96,43 %: 108 de 112 ramas. |
| Calidad estática | Ruff sin incidencias; 92 archivos Python con formato correcto. |
| Dependencias | Auditoría sin vulnerabilidades conocidas entre los paquetes consultados; detalle en sección 14. |
| Configuración real | `backend/.env` existe, es válido y conecta a `beront-bd`. |
| PostgreSQL real | Versión 18.6; conexión a `127.0.0.1:5432` con usuario `postgres`. |
| Esquema comercial | `public` está vacío; no existe `alembic_version` ni ninguna de las diez tablas del modelo. |
| Migración del repositorio | Una revisión, `e58826a8b8c7`; instalación y reversión verificadas en bases temporales. |
| Administrador y catálogo reales | No pueden estar registrados en las tablas del sistema porque estas aún no existen. |
| API local | No se encontró un servicio escuchando en `127.0.0.1:5000` durante la revisión. |
| Fotografías del backend | `backend/var/uploads/` y `staging/` existen y no contienen archivos. |
| WhatsApp | Omitido del `.env` por solicitud del propietario; no se configuró otro mecanismo persistente. |
| Hallazgo funcional | Desactivar la última presentación activa puede dejar un perfume publicado sin presentaciones visibles; reproducido y pendiente. |

La revisión no aplicó migraciones, creó usuarios ni cargó productos en `beront-bd`.
Las escrituras de verificación se hicieron exclusivamente en clústeres PostgreSQL temporales,
eliminados al terminar. No se modificó código funcional, dependencias ni historial Git.
Este documento no contiene contraseñas, claves secretas, cookies o tokens.

## 2. Alcance de la revisión

Se revisaron los 79 archivos Python de `src/beront/`, incluidos los paquetes vacíos;
los archivos de pruebas y su infraestructura; la migración inicial y su entorno Alembic;
los manifiestos, lockfile, plantilla de entorno y exclusiones de archivos.

Comprobaciones realizadas:

1. Lectura de entidades, reglas, casos de uso, repositorios, modelos, rutas y serializadores.
2. Inspección de las rutas registradas y sus metadatos de autenticación y permisos.
3. Ejecución completa de pytest con cobertura de ramas, lint y comprobación de formato.
4. Consulta de versiones instaladas y correspondencia con `uv.lock` para los paquetes principales.
5. Auditoría de dependencias con `pip-audit`.
6. Consulta de solo lectura de configuración, versión de PostgreSQL y tablas de la base real.
7. Reproducción aislada del hallazgo de publicación y ciclo Alembic `upgrade → downgrade → upgrade`.

No se ejecutaron pruebas de carga ni una auditoría de penetración. El ejecutor de pruebas
de navegador se revisó, pero no se volvió a ejecutar para este reporte del backend.
Los resultados de cobertura no sustituyen la revisión de reglas o de casos no probados.

## 3. Stack y dependencias

Paquete local: `beront` 0.1.0. Entorno inspeccionado: Python 3.14.0.
`.python-version` fija la familia 3.14; `pyproject.toml` admite Python desde 3.13.

| Componente | Versión instalada | Uso |
|---|---|---|
| Flask | 3.1.3 | Factory HTTP, rutas, cookies firmadas y CLI. |
| SQLAlchemy | 2.1.6 | Modelos ORM, consultas, transacciones y control de versiones. |
| Alembic | 1.20.1 | Versionado del esquema desde metadata ORM. |
| psycopg | 3.3.6 | Conexión PostgreSQL. |
| Pydantic | 2.14.1 | Contratos y validación de entradas HTTP. |
| Flask-WTF | 1.3.0 | CSRF de autenticación y operaciones administrativas. |
| Flask-Limiter | 4.1.1 | Límites de solicitudes con almacenamiento local en memoria. |
| Pillow | 13.0.0 | Validación y normalización de fotografías. |
| python-dotenv | 1.2.4 | Lectura local del entorno por CLI y migraciones. |
| pytest / pytest-cov | 9.1.1 / 7.1.0 | Pruebas y cobertura. |
| Ruff | 0.17.2 | Lint y formato. |
| pip-audit | 2.10.1 | Consulta de avisos de seguridad de dependencias. |

Las versiones principales instaladas coinciden con `uv.lock`.
uv gestiona dependencias y entorno; Hatchling construye el paquete Python.
No hay Redis, colas, microservicios, motor de búsqueda externo ni framework de API adicional.

Fuentes: [pyproject.toml](../backend/pyproject.toml), [uv.lock](../backend/uv.lock),
[.python-version](../backend/.python-version).

## 4. Arquitectura y organización efectiva

```text
Petición HTTP
  -> presentación: validación, sesión, permisos y serialización
  -> aplicación: caso de uso y transacción
  -> dominio: reglas puras y valores
  -> puertos de repositorio / almacenamiento
  -> infraestructura: SQLAlchemy, PostgreSQL y archivos locales
```

- El dominio no importa Flask, SQLAlchemy, Pydantic ni Werkzeug.
- Los repositorios convierten modelos ORM a entidades o proyecciones; no salen modelos ORM por la API.
- La presentación no importa repositorios ni modelos de persistencia.
- `bootstrap.py` compone dependencias explícitamente; no utiliza un contenedor externo.
- Cada caso de uso confirma su transacción. Los repositorios hacen `flush`, no `commit`.
- El catálogo consulta inventario mediante contratos de aplicación; el carrito usa la fachada del catálogo.

### Inventario de archivos funcionales

Se omiten los `__init__.py` vacíos, cachés, entorno virtual y artefactos generados.

```text
backend/
├── .env, .env.example                 # Configuración real privada y plantilla
├── .gitignore, .python-version        # Exclusiones y versión local de Python
├── pyproject.toml, uv.lock            # Dependencias, herramientas y resolución
├── alembic.ini                       # Configuración de migraciones sin credenciales
├── migrations/
│   ├── env.py                        # Metadata registrada y conexión de migraciones
│   ├── script.py.mako                # Plantilla de revisiones
│   └── versions/e58826a8b8c7_initial_approved_schema.py
├── src/beront/
│   ├── app.py                        # Factory, extensiones, rutas y límites
│   ├── config.py                     # Settings y validación del perfil local
│   ├── bootstrap.py                  # Composición de servicios y adaptadores
│   ├── cli.py                        # Alta y recuperación de administradores
│   ├── shared/
│   │   ├── domain/{errors,values}.py
│   │   ├── application/contracts.py
│   │   ├── infrastructure/{database,logging}.py
│   │   └── presentation/{errors,schemas,security}.py
│   └── modules/
│       ├── identity/
│       │   ├── domain/{entities,policies}.py
│       │   ├── application/{contracts,authenticate}.py
│       │   ├── infrastructure/{models,repositories,passwords}.py
│       │   └── presentation/{routes,schemas,serializers,decorators}.py
│       ├── catalog/
│       │   ├── domain/{entities,policies}.py
│       │   ├── application/{contracts,manage_catalog,query_catalog}.py
│       │   ├── infrastructure/{models,repositories,images}.py
│       │   └── presentation/{routes,schemas,serializers}.py
│       ├── inventory/
│       │   ├── domain/{entities,policies}.py
│       │   ├── application/{contracts,availability,adjust_inventory}.py
│       │   ├── infrastructure/{models,repositories}.py
│       │   └── presentation/{routes,schemas,serializers}.py
│       └── cart/
│           ├── domain/{entities,policies}.py
│           ├── application/{contracts,build_quote}.py
│           ├── infrastructure/whatsapp.py
│           └── presentation/{routes,schemas,serializers}.py
├── tests/
│   ├── conftest.py
│   ├── unit/{test_configuration,test_rules}.py
│   ├── architecture/test_boundaries.py
│   ├── migrations/test_schema.py
│   └── integration/
│       ├── test_catalog.py
│       ├── test_concurrency.py
│       ├── test_http_security.py
│       ├── test_identity.py
│       ├── test_inventory_cart.py
│       └── frontend_browser.py
└── var/{uploads,staging,logs}/         # Fotografías, cargas intermedias y registros
```

### Patrones y límites

| Patrón | Implementación | Resultado |
|---|---|---|
| Strategy | `DecantStockPolicy`, `BottleStockPolicy` | Consumo por ml o por unidades. |
| Adapter | `LocalImageStorage`, `WerkzeugPasswordHasher`, `WhatsAppLinkBuilder` | Separar archivos, hashes y construcción del enlace de los casos de uso. |
| Facade | `CatalogQueryFacade` | Resolver consultas públicas y selección para cotización. |
| Repository | `SqlIdentityRepository`, `SqlCatalogRepository`, `SqlStockRepository` | Traducir entre ORM y entidades de dominio. |
| Unit of Work | `SqlUnitOfWork` | Confirmar o revertir cambios y auditoría de forma conjunta. |

Los contratos existen como `Protocol`, pero varios constructores no los anotan explícitamente
y usan composición por comportamiento. No hay un comprobador estático de tipos Python configurado.
La separación se verifica parcialmente mediante pruebas AST y revisión de importaciones.

## 5. Identidad, autenticación y permisos

Fuentes: [IdentityService](../backend/src/beront/modules/identity/application/authenticate.py),
[decoradores](../backend/src/beront/modules/identity/presentation/decorators.py),
[políticas](../backend/src/beront/modules/identity/domain/policies.py).

### Implementado

- Alta local mediante `create-admin`, con entrada oculta y confirmación de contraseña.
- Usuario normalizado con `strip().casefold()`, máximo 100 caracteres y unicidad en PostgreSQL.
- Contraseñas de 14 a 128 caracteres, almacenadas con scrypt de Werkzeug.
- Verificación contra un hash ficticio cuando el usuario no existe; respuesta genérica de credenciales.
- Administradores inactivos rechazados al iniciar sesión y al autenticar una sesión existente.
- Token de sesión opaco aleatorio. PostgreSQL almacena su SHA-256, no el token original.
- Cookie Flask firmada con `sid`; sin contraseñas ni permisos como autoridad en la cookie.
- Vencimiento por 30 minutos de inactividad y máximo absoluto de ocho horas.
- Actualización de `last_seen_at` al autenticar correctamente una petición protegida.
- Rotación de token y revocación de la sesión anterior al repetir login.
- Logout revoca la sesión persistida y limpia la cookie.
- `reset-password` cambia el hash y revoca todas las sesiones del administrador.
- Auditoría de altas, login, intentos fallidos, logout y recuperación de contraseña.

### Permisos actuales

Solo existe el rol lógico `admin`, con cuatro permisos fijos:

| Permiso | Operaciones |
|---|---|
| `catalog:read_private` | Catálogo administrativo, borradores, casas y fotografías privadas. |
| `catalog:write` | Crear y modificar casas, productos, presentaciones y fotografías. |
| `inventory:read` | Consultar saldos e historial. |
| `inventory:adjust` | Registrar ajustes. |

`require_auth` valida sesión y administrador. `require_permission` comprueba el permiso
obtenido en el backend. Las 15 operaciones bajo `/api/v1/admin/` tienen ambos decoradores.
Consulta de sesión y logout exigen autenticación; no necesitan un permiso comercial adicional.

No existen registro público, usuarios compradores, editor de roles, OAuth, JWT, 2FA,
recuperación por correo o interfaz de administración de cuentas. La propiedad `active`
existe, pero no hay endpoint o comando específico para activarla o desactivarla.

## 6. Catálogo y fotografías

Fuentes: [CatalogService](../backend/src/beront/modules/catalog/application/manage_catalog.py),
[consultas](../backend/src/beront/modules/catalog/application/query_catalog.py),
[almacenamiento](../backend/src/beront/modules/catalog/infrastructure/images.py).

### Casas y perfumes

- Crear y editar casas comerciales, con nombre normalizado único, estado y versión.
- Crear perfumes como borradores; editar casa, nombre, slug, público y descripciones ES/EN.
- Clasificaciones multiselección `arabic`, `designer`, `niche`; público `male`, `female`, `unisex`.
- Publicar, archivar y marcar agotado mediante cambios con versión esperada.
- Una casa inactiva oculta sus perfumes del catálogo público.
- Publicar mediante la edición del perfume exige al menos una presentación activa.
- Los perfumes se archivan; no existe eliminación física de productos por API.
- Traducción inglesa opcional: si falta, se devuelve español y `description_locale: es`.

### Presentaciones

- Un perfume puede tener decants y botellas completas sin duplicar su ficha.
- Volúmenes configurables, positivos, con hasta dos decimales; no hay una lista cerrada de tamaños.
- Precio USD propio por presentación, positivo y con precisión decimal.
- Creación de botellas genera su saldo por unidades; creación de perfume genera su saldo de decants.
- Precio, activo y agotado son editables con control de versión.
- Tipo y volumen no están admitidos por el contrato de edición; se crea otra presentación para cambiarlos.
- No hay cálculo automático de precios por ml ni conversión de botellas a saldo de decants.

### Búsqueda, filtros y disponibilidad

| Parámetro | Comportamiento |
|---|---|
| `q` | Nombre de perfume o casa, sin distinguir mayúsculas; comodines SQL escapados. No hay normalización de acentos. |
| `kind` | `decant` o `full_bottle`, admite varios valores. |
| `brand_id` | UUID de una o más casas. |
| `classification` | Una o más clasificaciones. |
| `audience` | Uno o más públicos; valores exactos. Para incluir unisex junto a hombre se envían ambos valores. |
| `volume_ml` | Uno o más tamaños, como cadenas decimales. |
| `min_price`, `max_price` | Intervalo no negativo; mínimo no mayor que máximo. |
| `available` | Filtra presentaciones por disponibilidad efectiva. |
| `sort` | `name`, `price_asc`, `price_desc`. |
| `page`, `page_size` | Página 1..10000; tamaño predeterminado 24 y máximo 48. |
| `locale` | `es` o `en`. |

AND entre dimensiones y OR entre valores de una misma dimensión. Precio, tipo y volumen
deben coincidir sobre una misma presentación. El precio desde utiliza las presentaciones
que coinciden con los filtros, incluida disponibilidad cuando se solicita.

Las respuestas públicas excluyen borradores, archivados, cantidades exactas de inventario,
versiones y marcas administrativas. Los agotados pueden seguir apareciendo, con disponibilidad
falsa, si no se filtra por disponibles. `facets` obtiene casas y tamaños del catálogo visible.

### Fotografías

- Una fotografía por petición `multipart/form-data`, campo `file`.
- Máximo cinco fotografías por perfume y 5 MiB por archivo; petición multipart de hasta 5 MiB + 64 KiB.
- JPEG, PNG y WebP; imagen estática y máximo 20 megapíxeles.
- Verificación del contenido con Pillow, orientación EXIF y recodificación WebP a calidad 88.
- Conversión a RGB y eliminación de EXIF/perfil ICC/metadatos. La transparencia no se conserva.
- Nombres generados como `<uuid_hex>.webp`; no se usa el nombre o la ruta del cliente.
- Escritura intermedia en `var/staging/`, traslado a `var/uploads/` y limpieza del intermedio.
- Orden y textos alternativos ES/EN editables con versión.
- Si falla la persistencia tras guardar una foto, se intenta eliminar el archivo creado.
- La eliminación confirma el cambio en PostgreSQL y después retira el archivo; un fallo del
  sistema de archivos se registra como `image.cleanup_failed`.
- `/media/` valida el patrón del archivo y la visibilidad de su perfume. Una sesión válida
  de administrador permite ver fotos de borradores; un visitante recibe 404.
- Se sirve `image/webp`, con respuesta condicional y `Cache-Control: private, no-store`.

SVG cargado por un usuario no está admitido. La iconografía SVG del frontend es un recurso
separado; no se sube por este endpoint.

## 7. Inventario y concurrencia

Fuentes: [InventoryService](../backend/src/beront/modules/inventory/application/adjust_inventory.py),
[disponibilidad](../backend/src/beront/modules/inventory/application/availability.py),
[repositorio](../backend/src/beront/modules/inventory/infrastructure/repositories.py).

### Reglas implementadas

- Decants: saldo compartido de ml por perfume; todas sus presentaciones consumen de ese saldo.
- Botellas: saldo entero independiente por presentación.
- Saldos iniciales en cero. No se inventan existencias al crear o publicar un producto.
- Agotado manual prevalece sobre saldo positivo. Retirar la marca no convierte un saldo cero en disponible.
- La disponibilidad exige perfume visible, casa activa, presentación activa, sin marcas de agotado
  y saldo suficiente. El tamaño de decant se compara con los ml disponibles.
- Para cotizar varias líneas del mismo perfume se suman los ml requeridos antes de comprobar el saldo.
- Ajuste con `kind`, `target_id`, `delta`, `version`, `reason` y `operation_id` UUID.
- Delta no nulo y de hasta dos decimales; botellas solo en unidades enteras.
- Prohibidos saldos negativos y desbordamientos: ml hasta 9.999.999.999,99; botellas hasta 2.147.483.647 unidades.
- Cada movimiento registra delta, saldo final, versión final, actor, motivo, fecha y operación.

### Atomicidad e idempotencia

El ajuste bloquea el saldo mediante `SELECT ... FOR UPDATE`, verifica versión y guarda
saldo, movimiento y auditoría en una misma transacción. SQLAlchemy añade comprobación
optimista de versión al actualizar el modelo.

`operation_id` es único. Una huella SHA-256 vincula operación, destino, delta, versión,
motivo y administrador. Repetir el mismo contenido devuelve el movimiento original con
HTTP 200; una creación devuelve 201. Reutilizar la clave con contenido diferente da 409.
La lectura de la operación se repite después del bloqueo para resolver reintentos simultáneos.

Las pruebas verifican dos ajustes concurrentes sobre la misma versión y dos reintentos
simultáneos de una operación: no sobrescriben ni duplican el movimiento.

El backend no registra ventas automáticas ni botellas parciales. Tras una venta externa,
el administrador registra el ajuste y, cuando corresponde, marca la presentación agotada.
Los listados de saldos y movimientos están paginados; no tienen filtros propios de búsqueda
por perfume, casa o tipo en el contrato actual.

## 8. Carrito y WhatsApp

Fuentes: [BuildCartQuote](../backend/src/beront/modules/cart/application/build_quote.py),
[política de carrito](../backend/src/beront/modules/cart/domain/policies.py),
[constructor de enlace](../backend/src/beront/modules/cart/infrastructure/whatsapp.py).

```text
UUID de presentación + cantidad
  -> validar y consolidar duplicados
  -> leer producto, precio actual y estado
  -> comprobar stock conjunto
  -> construir líneas e importes con Decimal
  -> serializar resumen + enlace WhatsApp, si hay teléfono configurado
```

- No hay tabla de carritos o pedidos: el backend cotiza, no persiste la selección del navegador.
- Entrada limitada a identificadores, cantidades y locale; campos de precio o total se rechazan.
- Cantidades estrictamente enteras entre 1 y 20; booleanos y cadenas numéricas no se aceptan.
- El contrato admite hasta 400 líneas de entrada para consolidar duplicados, con un máximo
  final de 20 presentaciones y 20 unidades por presentación.
- Se vuelven a leer precios y disponibilidad en cada solicitud.
- Producto inexistente, oculto, agotado o sin saldo produce 409 con detalles por presentación.
- Precios, subtotales, total y ml se devuelven como cadenas decimales; moneda única USD.
- Mensaje ES/EN con marca, perfume, tipo, volumen, cantidad, precio unitario, subtotal y total.
- El enlace usa `https://wa.me/` y texto codificado con `urllib.parse.quote`.
- Sin teléfono: resumen válido, `whatsapp_url: null` y `configuration_error: WHATSAPP_NOT_CONFIGURED`.
- No se cobra, reserva, registra una venta ni descuenta inventario al cotizar o abrir WhatsApp.
- No se solicitan nombre o destino del cliente; no se calculan envío, descuentos o impuestos adicionales.

La interfaz debe volver a cotizar antes de continuar y gestionar cambios de precio o stock.
La API entrega el resultado; no puede comprobar que el usuario realmente completó una venta
en una conversación externa.

## 9. Superficie HTTP completa

Se comprobaron **24 combinaciones de método y ruta**. `HEAD` y `OPTIONS` automáticos de Flask
no se cuentan como funcionalidades adicionales. `id` representa un UUID válido.

| Método | Ruta | Acceso | Resultado principal |
|---|---|---|---|
| GET | `/api/v1/auth/csrf` | Público | Token CSRF y cookie de contexto. |
| POST | `/api/v1/auth/login` | Público + CSRF | Administrador, sesión renovada y nuevo CSRF. |
| GET | `/api/v1/auth/session` | Sesión | Administrador y permisos. |
| POST | `/api/v1/auth/logout` | Sesión + CSRF | Revocación, HTTP 204. |
| GET | `/api/v1/catalog/products` | Público | Listado filtrado y `meta`. |
| GET | `/api/v1/catalog/products/{slug}` | Público | Ficha visible. |
| GET | `/api/v1/catalog/facets` | Público | Casas, tamaños y valores de filtro. |
| GET | `/api/v1/admin/products` | `catalog:read_private` | Listado administrativo paginado. |
| GET | `/api/v1/admin/products/{id}` | `catalog:read_private` | Ficha administrativa. |
| POST | `/api/v1/admin/products` | `catalog:write` | Crear borrador, HTTP 201. |
| PATCH | `/api/v1/admin/products/{id}` | `catalog:write` | Editar, publicar, archivar o marcar agotado. |
| POST | `/api/v1/admin/products/{id}/variants` | `catalog:write` | Crear presentación, HTTP 201. |
| PATCH | `/api/v1/admin/variants/{id}` | `catalog:write` | Precio y disponibilidad manual. |
| GET | `/api/v1/admin/brands` | `catalog:read_private` | Todas las casas. |
| POST | `/api/v1/admin/brands` | `catalog:write` | Crear casa, HTTP 201. |
| PATCH | `/api/v1/admin/brands/{id}` | `catalog:write` | Editar casa o estado. |
| POST | `/api/v1/admin/products/{id}/images` | `catalog:write` | Subir fotografía, HTTP 201. |
| PATCH | `/api/v1/admin/images/{id}` | `catalog:write` | Editar orden o textos alternativos. |
| DELETE | `/api/v1/admin/images/{id}` | `catalog:write` | Retirar foto, HTTP 204; cuerpo con versión. |
| GET | `/media/{filename}` | Público condicionado por visibilidad; admin opcional | Archivo WebP o 404. |
| GET | `/api/v1/admin/inventory` | `inventory:read` | Saldos paginados. |
| GET | `/api/v1/admin/inventory/movements` | `inventory:read` | Historial paginado. |
| POST | `/api/v1/admin/inventory/adjustments` | `inventory:adjust` | Movimiento nuevo 201 o repetición 200. |
| POST | `/api/v1/cart/quote` | Público, sin CSRF | Cotización sin efectos persistentes. |

Todas las mutaciones administrativas necesitan sesión, permiso y CSRF. No hay OpenAPI/Swagger
generado ni un endpoint de salud configurado en esta versión.

### Contratos y validaciones transversales

- Campos extra prohibidos mediante Pydantic; cadenas recortadas salvo la contraseña de login.
- UUID para identificadores; cantidades y versiones de edición con enteros estrictos.
- Dinero y ml entran como cadenas decimales finitas, hasta dos decimales y rango NUMERIC(12,2).
- Un PATCH exige `version` positiva y al menos un campo adicional; no admite `null` explícito.
- Nombres de perfume: hasta 120 caracteres, sin caracteres de control.
- Slug: hasta 160 caracteres, minúsculas alfanuméricas y guiones.
- Descripciones: hasta 5.000 caracteres por idioma; textos alternativos hasta 250.
- Motivo de inventario: 1..300 caracteres; espacios en blanco solos se rechazan.
- Parámetros desconocidos o repetidos sin permiso de repetición producen 422.
- Máximo 50 valores por dimensión de filtro repetible.
- El formato habitual de éxito es `{"data": ...}`; listados paginados añaden
  `meta: {page, page_size, total}`. La carga de fotos usa multipart, no JSON.

Ejemplo técnico de entrada, con un identificador marcador que debe sustituirse:

```json
{
  "locale": "es",
  "items": [{"variant_id": "UUID_DE_LA_PRESENTACION", "quantity": 2}]
}
```

Formato de error:

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "La disponibilidad del carrito ha cambiado.",
    "details": [{"field": "items", "variant_id": "UUID", "code": "UNAVAILABLE_QUANTITY"}],
    "request_id": "UUID_DE_LA_SOLICITUD"
  }
}
```

| HTTP | Uso implementado |
|---|---|
| 200 / 201 / 204 | Lectura o cambio, creación, cierre o eliminación sin cuerpo. |
| 400 | JSON o petición mal formada; host inválido. |
| 401 / 403 | Sesión o credenciales inválidas; permiso, origen o CSRF rechazado. |
| 404 / 405 | Recurso no visible o inexistente; método no permitido. |
| 409 | Versión obsoleta, conflicto de datos, operación reutilizada o stock insuficiente. |
| 413 / 415 | Tamaño excedido o contenido no admitido. |
| 422 | Validación o regla comercial incumplida. |
| 429 | Límite de solicitudes excedido. |
| 500 / 503 | Excepción inesperada o dependencia de base de datos indisponible. |

Las excepciones no devuelven SQL, valores de entradas, contraseñas ni tracebacks.
Errores PostgreSQL de serialización `40001` o deadlock `40P01` se traducen a conflicto 409.

## 10. Modelo de persistencia y migraciones

SQLAlchemy es la fuente del esquema. Existen **diez tablas de aplicación**:

| Tabla | Datos y restricciones relevantes |
|---|---|
| `administrators` | UUID, usuario único, hash y activo. |
| `admin_sessions` | FK a administrador, hash único del token, creación, último uso, vencimiento y revocación. |
| `brands` | Nombre y nombre normalizado únicos; activo y versión ORM. |
| `products` | FK a casa, nombre, slug único, público, array de clasificaciones, descripciones, estados y versión. Checks de público y clasificaciones. |
| `variants` | FK a perfume, tipo, volumen y precio NUMERIC(12,2), activo, agotado y versión. Checks de tipo y valores positivos. |
| `product_images` | FK a perfume, archivo único, posición no negativa, textos alternativos y versión. |
| `decant_stock` | FK única a perfume, saldo NUMERIC(12,2) no negativo y versión. |
| `bottle_stock` | FK única a presentación, saldo entero no negativo y versión. |
| `stock_movements` | Un único destino de stock, actor con FK, delta y saldo, motivo, versión, operación UUID única y huella. Checks de destino, tipo, unidades y cantidades. |
| `audit_events` | Actor UUID opcional, acción, recurso, request ID y fecha. Actor y recurso no son FK en este modelo. |

`alembic_version` es una tabla adicional de seguimiento de migraciones, no un agregado comercial.
Los UUID, fechas y valores predeterminados se generan desde la aplicación/ORM; no todos son
defaults SQL del servidor. Las fechas persistidas usan columnas con zona horaria y UTC.

Índices explícitos: referencias de productos, variantes, imágenes y sesiones; nombre de perfume;
GIN sobre clasificaciones; combinación tipo/volumen/precio de presentaciones; fechas de
movimientos y auditoría. Los campos únicos tienen sus restricciones correspondientes.

### Transacciones y conexiones

- Pool de cinco conexiones y hasta cinco adicionales por proceso.
- `pool_pre_ping` comprueba conexiones antes de reutilizarlas.
- Timeout de conexión de cinco segundos y de sentencias de diez segundos en el motor de la aplicación.
- Las conexiones de la aplicación fijan `timezone=UTC`.
- Unidad de trabajo con rollback y cierre al salir; confirmación explícita en el caso de uso.
- Bloqueos pesimistas para modificaciones coordinadas de perfume/saldos y versiones ORM para ediciones.
- Alembic usa su conexión separada con `NullPool`; no hereda automáticamente la configuración del motor de Flask.

### Migración revisada

Archivo: [e58826a8b8c7_initial_approved_schema.py](../backend/migrations/versions/e58826a8b8c7_initial_approved_schema.py).

- Revisión inicial y única; `down_revision = None`.
- Crea las diez tablas y sus índices, claves y comprobaciones.
- `downgrade` retira objetos en orden inverso respetando referencias.
- `migrations/env.py` registra metadata y compara tipos para autogeneración.
- Acepta una conexión suministrada por pruebas o lee `MIGRATION_DATABASE_URL`.
- Ningún archivo de ejecución utiliza `create_all`.
- En PostgreSQL temporal se comprobó instalación de once tablas contando Alembic,
  reversión hasta base —queda la tabla de control— y nueva instalación sin diferencias ORM.

**En `beront-bd` no se aplicó esta revisión durante la inspección ni se encontró aplicada previamente.**

## 11. Configuración local y estado operativo

Fuentes: [config.py](../backend/src/beront/config.py), [.env.example](../backend/.env.example),
[LOCAL.md](LOCAL.md). El `.env` real está excluido por los `.gitignore` de raíz y backend.

| Variable | Finalidad y situación |
|---|---|
| `APP_ENV` | Solo se admite el perfil `local`. |
| `SECRET_KEY` | Presente y aceptada por las validaciones; su valor se mantiene privado. |
| `DATABASE_URL` | Conexión de ejecución a `beront-bd` mediante psycopg local. |
| `MIGRATION_DATABASE_URL` | Conexión Alembic a la misma base; actualmente con el mismo usuario. |
| `FRONTEND_ORIGIN` | Origen local del frontend para comprobar `Origin` en mutaciones. |
| `WHATSAPP_NUMBER` | Ausente del archivo y de la plantilla por instrucción del propietario. El código aún permite la variable del proceso. |

La clave debe tener al menos 32 caracteres y no comenzar por los marcadores rechazados
por `Settings`; la validación no mide entropía criptográfica.
El teléfono, cuando se proporciona por entorno del proceso, debe tener 8..15 dígitos ASCII
internacionales y no empezar por cero.

Las dos URLs separan funciones, no bases. El usuario real actual es `postgres`, confirmado
como superusuario. **La separación de permisos de ejecución y migración prevista en la
arquitectura no está aplicada en esta configuración local.** Las pruebas sí verifican un
rol de ejecución sin CREATE en `public` y sin acceso a `alembic_version`.

El servidor PostgreSQL informa `America/Bogota` como zona predeterminada. El motor de la
aplicación fuerza UTC por conexión, por lo que esa configuración del servidor no cambia
la estrategia de persistencia. La presentación comercial corresponde a `America/Guayaquil`.

Observaciones operativas:

- La factory no migra automáticamente ni valida que existan tablas al crear la aplicación.
- El puerto 5000 no estaba escuchando al comprobarlo; no se inició Flask para este reporte.
- `uploads/` y `staging/` no tienen fotografías comerciales.
- No hay comandos de carga del HTML comercial ni importador del catálogo temporal al backend.
- No hay limpieza periódica de sesiones vencidas, proceso de reconciliación de fotos huérfanas,
  tareas de respaldo/restauración o ejecutor de tareas programadas implementados.

## 12. Seguridad y auditoría

### Controles efectivos

- Debug desactivado; hosts permitidos `localhost`, `127.0.0.1` y `[::1]`.
- Límite general de 300 solicitudes por minuto; login 5 por 15 minutos y cotización 30 por minuto.
- Límites en memoria por proceso e IP remota; no son un contador compartido entre varios procesos.
- JSON de hasta 64 KiB, formularios con límites de memoria y máximo ocho partes.
- CSRF con vigencia de una hora en login, logout y mutaciones administrativas; cotización pública exenta.
- Si una mutación incluye `Origin`, debe coincidir exactamente con el frontend configurado.
  Su ausencia no sustituye ni desactiva el control CSRF de rutas protegidas.
- Cookie `HttpOnly`, `SameSite=Lax`, ruta `/`; `Secure=False` corresponde al perfil HTTP local.
- Cabeceras `nosniff`, `DENY`, `no-referrer`, política de permisos y CSP restrictiva para la API.
- Sin CORS abierto; el navegador usa el proxy del frontend.
- `Cache-Control: no-store` en administración, autenticación y carrito; fotos privadas sin almacenamiento.
- SQL parametrizado y filtros/ordenamientos permitidos por contrato; sin interpolación SQL de entradas HTTP.
- Request ID UUID generado en servidor y devuelto en cabecera y errores.

### Correspondencia con el marco OWASP Top 10:2025 adoptado

Esta tabla describe implementación observable y límites; no certifica cobertura exhaustiva de ataques.

| Categoría | Implementación actual | Límite o pendiente observado |
|---|---|---|
| A01 — Control de acceso | Decoradores, permisos backend y visibilidad de fotos/productos. | Un único rol con permisos fijos; no administración granular de roles. |
| A02 — Configuración | Perfil local, validación, hosts, límites, debug y cabeceras. | La conexión local utiliza superusuario, sin separación efectiva de privilegios. |
| A03 — Cadena de suministro | Lockfile y auditoría de paquetes. | Auditoría de avisos conocidos; paquete local no consultable en PyPI. |
| A04 — Criptografía | scrypt, tokens aleatorios, hash del token y cookie firmada. | HTTP y cookie sin Secure por alcance local; no se evaluó otra configuración. |
| A05 — Inyección | Consultas parametrizadas, listas de valores y recodificación de fotos. | Descripciones se entregan como texto JSON; su renderizado seguro corresponde también al frontend. |
| A06 — Diseño inseguro | Precios del servidor, saldo compartido, cotización sin venta ficticia. | Invariante de publicación incompleta al desactivar la última presentación. |
| A07 — Autenticación | Límites, errores genéricos, expiración, revocación y rotación. | Sin 2FA ni recuperación por correo, fuera del alcance aprobado. |
| A08 — Integridad | FK, checks, versiones, idempotencia y transacciones. | No se realizan reservas; una cotización no garantiza disponibilidad futura. |
| A09 — Registro y alertas | Auditoría SQL, logs JSON y avisos WARNING/ERROR en consola. | No existe agregador de alertas, notificación activa o panel/endpoint de auditoría. |
| A10 — Excepciones | Rollback, timeouts, errores uniformes y cierre seguro. | Limpieza de archivos posterior a commit puede requerir revisión si falla el sistema de archivos. |

### Registros implementados

`audit_events` persiste cambios de catálogo, fotografías, inventario y acciones de identidad.
La misma transacción incluye el evento de auditoría cuando hay una mutación de negocio.
Los saldos y movimientos se consultan por API; los eventos generales no tienen endpoint propio.

Logs JSON de `beront`: hora UTC, nivel, evento, request ID y tipo de excepción.
Archivo `var/logs/application.log`, rotación a 2.000.000 bytes y tres copias de respaldo.
La consola recibe eventos WARNING o superiores. Los manejadores evitan imprimir entradas,
SQL o textos de excepciones que podrían contener secretos.

## 13. Pruebas y cobertura verificadas

Ejecución del 26 de octubre de 2026: **82 pruebas aprobadas en 26,36 segundos**.

| Grupo | Casos ejecutados | Contenido |
|---|---:|---|
| Dominio/configuración | 35 | Dinero, cantidades, saldos, sesión, contraseñas, imágenes, WhatsApp y configuración. |
| Integración | 42 | API, repositorios, permisos, CSRF, archivos, versiones, concurrencia y transacciones. |
| Arquitectura | 4 | Dominio sin frameworks, presentación sin ORM, permisos y ausencia de `create_all`. |
| Migraciones | 1 | Correspondencia del esquema con modelos y rol de ejecución sin DDL. |
| **Total** | **82** | Incluye casos parametrizados. |

### Aislamiento

`tests/conftest.py` inicia PostgreSQL real en un directorio y puerto temporales con contraseña
aleatoria y autenticación SCRAM. Cada caso usa su propia base y la prepara con Alembic.
El usuario de aplicación recibe DML, no DDL, y se le retira acceso a la tabla de Alembic.
Los archivos de fotografías también son temporales. No se usa `DATABASE_URL` comercial
para ejecutar estas pruebas; los recursos creados se cierran y eliminan al finalizar.

### Escenarios cubiertos

- Login con y sin CSRF, credenciales genéricas, límites, cookies, sesión renovada y revocada.
- Expiración por inactividad y vencimiento absoluto; recuperación y administrador inactivo.
- Falta de sesión o permiso, origen no permitido y host ajeno.
- Crear, editar, publicar y archivar; filtros y precios sobre una misma presentación.
- Tamaño no predeterminado de 7,50 ml; traducción y respaldo a español.
- Conflictos por versión y nombres duplicados de casas.
- Subida, edición, visibilidad, límites, eliminación y limpieza por fallo de fotografías.
- Saldos compartidos de decants e independientes de botellas; agotado manual y stock cero.
- Ajustes repetidos y concurrentes; rechazo de negativos y rollback ante fallo de auditoría.
- Manipulación de precios/totales del carrito, cantidades inválidas y consolidación de duplicados.
- Recalcular precios, error por falta de teléfono y cotización sin movimiento de inventario.
- Errores sin SQL o secretos, límites HTTP, cabeceras y migración coherente con los modelos.

### Métricas

| Métrica | Resultado |
|---|---:|
| Cobertura combinada global | 96,53 % |
| Sentencias cubiertas | 1.517 / 1.563: 97,06 % |
| Ramas globales cubiertas | 233 / 250: 93,20 % |
| Ramas de dominio y aplicación | 108 / 112: 96,43 % |
| Objetivo global configurado | 80 %; alcanzado. |
| Objetivo arquitectónico de ramas de dominio/aplicación | 90 %; alcanzado. |

Cobertura combinada por área, calculada sobre sentencias y ramas:

| Área | Resultado |
|---|---:|
| Factory, composición, configuración y CLI | 100,00 % |
| Identidad | 97,63 % |
| Catálogo | 96,92 % |
| Inventario | 97,80 % |
| Carrito | 97,89 % |
| Compartido | 90,84 % |

El formato resumido de coverage redondea el global a 97 %; el porcentaje exacto es 96,53 %.
Persisten rutas sin cubrir: configuración del logger fuera de testing —44 % en ese archivo—,
algunos errores de archivos, concurrencia y validaciones. Algunos archivos `Protocol`
aparecen al 0 % por no ejecutarse en runtime; no significa que sus repositorios estén ausentes.

No hay cobertura explícita de cada combinación posible de filtros ni mediciones de carga.
El caso de desactivar la última presentación no forma parte de los 82 casos existentes;
se comprobó con una reproducción adicional aislada y se documenta a continuación.

## 14. Calidad y dependencias

| Comprobación ejecutada | Resultado |
|---|---|
| `ruff check src tests migrations` | Sin incidencias. |
| `ruff format --check src tests migrations` | 92 archivos ya formateados. |
| `pip-audit --local --progress-spinner off --format json` | 63 paquetes enumerados, 62 consultables, cero vulnerabilidades conocidas devueltas. |
| Paquete local `beront` | No encontrado en PyPI; excluido de consulta de avisos, no de revisión de código. |
| Versiones principales frente a `uv.lock` | Coinciden. |
| Upgrade/downgrade/upgrade aislado | Correcto; reinstalación sin diferencias con metadata ORM. |

Estos resultados reflejan el entorno y los avisos disponibles en la fecha de revisión.
No se añadieron ni actualizaron paquetes para elaborar este reporte.

## 15. Hallazgos y pendientes concretos

### H01. Base comercial sin inicializar

**Evidencia:** conexión válida a `beront-bd`; `public` sin tablas, sin `alembic_version` y
sin revisiones registradas. El repositorio tiene `e58826a8b8c7` como head.

**Efecto:** los casos de uso funcionan en las bases temporales, pero el entorno comercial
no puede consultar ni mantener datos del sistema hasta instalar su esquema.

**Pendiente:** aplicar la migración revisada, verificar coherencia y crear el administrador
con los comandos existentes. No se hizo sobre la base comercial durante este reporte.

### H02. Desactivación de la última presentación de un producto publicado

**Ubicación:** `CatalogService.update_variant` frente a `ensure_publishable` y
`CatalogQueryFacade.detail`.

Reproducción realizada exclusivamente en PostgreSQL temporal:

1. Crear perfume y una presentación activa.
2. Publicar mediante `update_product`; la validación de publicación lo permite.
3. Desactivar esa presentación mediante `update_variant` con versión válida.
4. El perfume conserva `published=True`.
5. La ficha por slug se obtiene con cero presentaciones activas; el catálogo lo excluye del listado.

**Efecto:** se produce una diferencia entre lo que significa publicado, lo que muestra
el listado y lo que permite la ficha directa.

**Pendiente:** hacer cumplir la regla aprobada de al menos una presentación activa al
modificar presentaciones de un producto publicado y agregar una prueba de regresión.
No se cambió el comportamiento en una tarea cuyo alcance es elaborar el reporte.

### H03. Privilegios locales compartidos

**Evidencia:** ejecución y migraciones utilizan el mismo `postgres`, confirmado como
superusuario. Es la configuración local solicitada por el propietario.

**Efecto:** conservar dos variables no separa privilegios por sí mismo. El aislamiento
de roles previsto en la arquitectura solo está demostrado en el entorno de pruebas.

**Pendiente:** si se adopta la separación prevista, asignar las dos URLs a los roles
correspondientes; no requiere cambiar las entidades ni los contratos de API.

### H04. Teléfono sin ubicación alternativa configurada

El número se retiró del `.env` y de la plantilla. `Settings.from_env` aún admite
`WHATSAPP_NUMBER` en el entorno del proceso, pero no existen tabla de ajustes,
pantalla de configuración o archivo alternativo implementados.
Sin un número válido el enlace real no se habilita. Definir otra forma de gestionarlo
requiere una decisión posterior; no se inventó ni guardó un teléfono.

### H05. La paginación pública no limita todo el trabajo de consulta

`CatalogQueryFacade.search` recorre todos los candidatos en lotes de 100, calcula disponibilidad,
acumula resultados y después corta la página. `facets` también recorre el catálogo visible.
Existe paginación en la respuesta y consultas parametrizadas, pero el coste de procesar
el resultado crece con el número de candidatos. No se midió un umbral de volumen o latencia.

Es una limitación de escalabilidad de la implementación actual, no un fallo demostrado con
el catálogo comercial, que todavía no está cargado. Antes de dimensionar grandes volúmenes,
medir y valorar el traslado de disponibilidad, orden y paginación al motor SQL.

### H06. Diferencia entre disponibilidad pública y ciertas respuestas administrativas

`product_data` solo calcula disponibilidad cuando recibe un `ProductView` con sus resultados.
El listado administrativo usa esa vista; detalle privado y respuestas de creación/edición
pueden serializar sin ella y devolver `available=False` aunque el saldo sea suficiente.

Observación por lectura del código, sin reproducción adicional específica en esta revisión.
Esos campos no deben interpretarse como una consulta autoritativa de stock en el editor;
conviene unificar su semántica si se van a utilizar allí.

### H07. Observabilidad y mantenimiento acotados

Hay auditoría persistente y logs rotados, pero no alertas agregadas, consulta general de
auditoría por API, limpieza periódica de sesiones o reconciliación de archivos huérfanos.
La retirada de archivos tras un commit es una operación separada de PostgreSQL.
Estas capacidades no se deben presentar como terminadas.

## 16. Relación con el frontend temporal

Las 130 fichas agrupadas, 400 presentaciones y 132 fotografías del HTML proporcionado
están en `frontend/public/temporal/`. Las revisiones visuales consumen una API simulada
de Astro bajo `/temporal/api/v1/`; ese contenido **no ha sido cargado al backend**.

El backend real mantiene `/api/v1/` y `/media/`. Para trasladar el catálogo deben usarse
los endpoints administrativos de casas, productos, presentaciones y fotografías, con sesión
y CSRF, y registrar inventario real mediante ajustes. No copiar datos directamente a tablas.
Los UUID temporales requieren correspondencia con los IDs devueltos por el backend.

La disponibilidad desconocida del HTML no sirve como inventario. Tampoco su simulación
de WhatsApp configura un teléfono en Flask. El procedimiento de sustitución está documentado
en [TEMPORARY_CATALOG.md](TEMPORARY_CATALOG.md).

## 17. Operación disponible y secuencia pendiente

Los siguientes comandos son la operación prevista y documentada; no implican que se hayan
ejecutado contra `beront-bd` al elaborar este informe. Se ejecutan desde `backend/`.

```powershell
uv sync --locked
uv run alembic upgrade head
uv run alembic check
uv run flask --app beront.app:create_app create-admin NOMBRE_DE_USUARIO
uv run flask --app beront.app:create_app run --host 127.0.0.1 --port 5000
```

La contraseña del administrador se solicita de forma oculta. Su recuperación existente es:

```powershell
uv run flask --app beront.app:create_app reset-password NOMBRE_DE_USUARIO
```

Para repetir la verificación del backend:

```powershell
uv run pytest --cov=beront --cov-branch --cov-report=term-missing
uv run ruff check src tests migrations
uv run ruff format --check src tests migrations
uv run pip-audit --local --progress-spinner off
```

Las pruebas necesitan PostgreSQL local instalado con `initdb` y `pg_ctl`; `POSTGRES_BIN`
permite señalar su carpeta de ejecutables. No se debe reemplazar ese aislamiento por la base comercial.

`tests/integration/frontend_browser.py` es un ejecutor adicional: levanta Flask, PostgreSQL y Astro
temporales, crea un administrador de prueba y ejecuta Playwright del frontend. No lo recoge
pytest automáticamente y no se ejecutó de nuevo para este reporte. Su comando está en `LOCAL.md`.

Orden de pendientes para disponer de la instancia comercial local:

1. Corregir y verificar H02 antes de considerar cerrado ese flujo de publicación.
2. Instalar la migración en la base real y comprobar `alembic check`.
3. Crear el administrador e iniciar Flask.
4. Cargar catálogo, fotos y existencias reales por los casos de uso existentes.
5. Resolver la configuración del teléfono sin contrariar la instrucción sobre `.env`.
6. Revisar H03, H05, H06 y H07 según el uso requerido y mantener actualizado este reporte.

## 18. Funcionalidades excluidas del backend actual

No existen pagos en línea, pedidos persistentes, cobros, reservas de stock, carrito persistido,
cuentas de clientes, venta automática por conversación, recepción de mensajes de WhatsApp,
integración con WhatsApp Business API, cálculo de transporte, verificación de destinos,
traducción automática ni importación comercial automática desde el HTML.

La política de envíos a Ecuador continental se comunica en la interfaz; no hay checkout
de direcciones que pueda validarla en el backend. Las ventas y el transporte se coordinan
externamente, conforme al alcance aprobado.

