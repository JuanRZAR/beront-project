# Ejecución y verificación local

## Requisitos

- Python 3.14, fijado en backend/.python-version.
- uv.
- PostgreSQL 18 y sus herramientas de línea de comandos.
- Bun. En PowerShell puede utilizarse bun.cmd si la política de ejecución bloquea bun.ps1.

No cambiar la política de seguridad de PowerShell para ejecutar este proyecto.

## Dependencias

Desde backend/:

```powershell
uv sync --locked
```

Desde frontend/:

```powershell
bun.cmd install --frozen-lockfile
```

uv.lock y bun.lock contienen las versiones verificadas.
La configuración de Bun fija esbuild corregido mediante overrides para evitar
la vulnerabilidad de lectura local detectada en versiones anteriores de su servidor.

## Base de datos local

Estado del equipo, 27 de octubre de 2026: `beront-bd` ya está migrada hasta
`c449e445ed3d` y `alembic check` no detecta diferencias con los modelos.
`DATABASE_URL` usa el rol restringido `beront_app_2ec87f29`; `MIGRATION_DATABASE_URL`
conserva `postgres`. No repetir la preparación manual siguiente en esta base existente.
El siguiente paso del propietario es crear el administrador y ejecutar la semilla.

### Preparación manual para una instalación nueva

Usar una base dedicada a BÉRONT. No reutilizar tablas de otros proyectos.
Conectarse con psql como un administrador PostgreSQL que el propietario ya controle.

Crear los roles y asignar sus contraseñas de forma interactiva:

```sql
CREATE ROLE beront_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
\password beront_migrator
CREATE ROLE beront_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
\password beront_app
CREATE DATABASE "beront-bd" OWNER beront_migrator;
\connect beront-bd
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO beront_app;
```

No ejecutar CREATE DATABASE si `beront-bd` ya existe, como ocurre en el equipo del propietario.
Estos comandos describen la preparación de una base nueva y roles separados. Las tablas se crean
exclusivamente mediante Alembic; no escribir CREATE TABLE ni ALTER TABLE manuales.

## Variables

Copiar backend/.env.example a backend/.env y completar los valores localmente:

| Variable | Uso |
|---|---|
| APP_ENV | Solo local. |
| SECRET_KEY | Secreto aleatorio de al menos 32 caracteres. |
| DATABASE_URL | PostgreSQL local, driver postgresql+psycopg y rol beront_app. |
| MIGRATION_DATABASE_URL | Misma base con el rol beront_migrator. |
| FRONTEND_ORIGIN | http://localhost:4321. |
| SMTP_HOST | Servidor SMTP local para recuperar códigos de pedido. Vacío desactiva la recuperación. |
| SMTP_PORT | Puerto del servidor SMTP; 25 si se omite. |
| SMTP_SECURITY | `none`, `starttls` o `ssl`; `none` si se omite. |
| SMTP_USERNAME / SMTP_PASSWORD | Credenciales opcionales; se definen juntas. |
| SMTP_SENDER | Correo remitente; obligatorio cuando existe SMTP_HOST. |

`DATABASE_URL` la usa Flask para leer y modificar los datos de la aplicación.
`MIGRATION_DATABASE_URL` la usa Alembic para crear y modificar el esquema mediante
migraciones. No representan dos bases: ambas deben apuntar a la misma base y pueden
usar usuarios diferentes para separar permisos de ejecución y migración.

El 26 de octubre se configuraron ambas conexiones con `postgres`, por indicación del propietario.
El 27 de octubre se separaron los roles: Flask ejecuta funciones con `beront_app_2ec87f29`,
sin superusuario, DDL ni acceso directo a tablas. La credencial aleatoria de ese rol se guardó
solo en `backend/.env`. El secreto de Flask y las credenciales de migración no se modificaron.

WhatsApp se omite del `.env` y de su plantilla por solicitud del propietario.
El código ya no lee `WHATSAPP_NUMBER`, aunque exista en el entorno del proceso.
El teléfono se registra mediante `PUT /api/v1/admin/settings` y se consulta desde PostgreSQL.
Mientras falte, el catálogo y la cotización del carrito funcionan con el enlace deshabilitado;
crear un pedido para pago por WhatsApp exige configurar el número.

Las contraseñas con caracteres reservados deben codificarse al incluirlas en una URL.
No compartir .env ni copiar sus valores a documentación o registros.
El secreto no tiene un valor predeterminado.

## Migraciones y administrador

Desde backend/:

```powershell
uv run alembic upgrade head
uv run alembic check
uv run flask --app beront.app:create_app createsuperuser
```

El comando solicita usuario y contraseña oculta de 14..128 caracteres.
Un segundo administrador se rechaza también por restricción de PostgreSQL.
`create-admin NOMBRE_DE_USUARIO` se conserva como alias con el mismo límite.

Después de migrar, conceder ejecución de funciones al usuario de la aplicación,
con psql y el rol propietario. Repetir el GRANT de funciones después de nuevas migraciones:

El ejemplo siguiente usa el nombre de la instalación actual. En una instalación nueva,
sustituirlo por el rol elegido para `DATABASE_URL`.

```sql
REVOKE ALL ON TABLE alembic_version FROM beront_app_2ec87f29;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM beront_app_2ec87f29;
GRANT USAGE ON SCHEMA beront_api TO beront_app_2ec87f29;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA beront_api TO beront_app_2ec87f29;
```

Para recuperar acceso localmente:

```powershell
uv run flask --app beront.app:create_app reset-password NOMBRE_DE_USUARIO
```

Esto solicita una contraseña nueva y revoca todas las sesiones del administrador.
No existe registro público ni recuperación por correo.

## Semilla del catálogo original

Desde `backend/`, verificar sin acceder a la base:

```powershell
uv run python semillas/importar_catalogo.py
```

Después de migrar y crear el administrador, importar:

```powershell
uv run python semillas/importar_catalogo.py --apply
```

La fuente está en `backend/semillas/catalogo/`: 130 perfumes, 400 presentaciones,
42 marcas y 132 archivos. Las categorías, públicos y tamaños se leen del JSON;
no son listas de negocio en el código de ejecución. Se publican los perfumes
importados con saldo cero y fotografías vinculadas mediante URLs `/media/` persistidas.
Falta la fotografía de Delina Eau de Parfum en la fuente original.

La importación se puede repetir. Omite perfumes con el mismo UUID y conserva sus
precios, publicación, fotografías y existencias editados. Reutiliza definiciones por
slug o tipo/volumen y marcas por nombre normalizado. No fuerza la reactivación de
configuraciones desactivadas por el administrador. Un conflicto no se sobreescribe:
se corrige en el catálogo antes de repetir. Cada perfume nuevo se guarda en una
transacción; el proceso puede retomarse tras una interrupción.

La misma semilla instala estados y transiciones iniciales editables y términos de prueba.
No inventa un WhatsApp, cuentas bancarias ni tarifas. Antes de probar checkout, el propietario
debe registrar contacto, provincias continentales, ciudades con sus tarifas y cuentas reales.
No se incorporó una API de Servientrega ni una integración de correo; guía y seguimiento
se registran manualmente y las recuperaciones se atienden por los contactos del pedido.

Las fotografías de origen se conservan como entrada de semilla. Las copias servidas
se validan y normalizan en `backend/var/uploads/`. La versión temporal del frontend
se retirará después de verificar esta integración en la base comercial local.

## Arrancar la API

Desde backend/:

```powershell
uv run flask --app beront.app:create_app run --host 127.0.0.1 --port 5000
```

Mantener FLASK_DEBUG desactivado.
La API escucha en http://127.0.0.1:5000 .
La configuración y las conexiones son exclusivamente locales.

Comprobaciones públicas:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/catalog/facets
Invoke-RestMethod http://127.0.0.1:5000/api/v1/catalog/products
```

El catálogo estará vacío hasta que el administrador cree y publique productos.
Crear el perfume, añadir presentaciones y después publicarlo.
Registrar existencias mediante los ajustes de inventario.

## Autenticación y contratos

1. GET /api/v1/auth/csrf inicia una cookie y devuelve data.csrf_token.
2. POST /api/v1/auth/login envía username/password en JSON,
   conserva la cookie y añade X-CSRFToken.
3. La respuesta renueva la sesión y entrega un csrf_token nuevo.
4. Reutilizar ese token y la cookie en operaciones administrativas.
5. GET /api/v1/auth/session devuelve usuario, rol y permisos.
6. POST /api/v1/auth/logout requiere cookie y CSRF.

Las ediciones requieren version. Un conflicto 409 exige recargar el registro.
Un ajuste requiere kind, target_id, delta como cadena decimal, version, reason y
operation_id UUID. Reintentar exactamente la misma operación conserva operation_id.
Una operación nueva utiliza otro UUID.

Antes de crear una marca, configurar una categoría y enviar su `category_id`.
Cada marca pertenece a una sola categoría; los perfumes heredan esa categoría.
Configurar también públicos y presentaciones antes de asignarlos a perfumes.

API de configuración protegida: `GET/POST /api/v1/admin/catalog-options/{resource}`
y `PATCH /api/v1/admin/catalog-options/{resource}/{id}`. Los recursos permitidos son
`categories`, `audiences` y `presentations`. Las definiciones tienen `name_es`,
`name_en`, `active` y `version`; categorías/públicos tienen `slug` y las presentaciones
`kind` y `volume_ml`. El tipo técnico distingue saldo en ml y unidades; los volúmenes
y etiquetas comerciales los registra el administrador.

Se admite cualquier volumen positivo de hasta dos decimales previamente configurado.
No cambiar tipo/volumen ni slug por PATCH; editar nombres o desactivar y crear otra
definición. Una presentación usada por perfumes publicados debe retirarse de ellos
antes de desactivar la definición global. No se elimina el historial.

Biblioteca protegida: `GET/POST /api/v1/admin/media`, `PATCH/DELETE
/api/v1/admin/media/{id}`. Para reutilizar una fotografía, enviar `asset_id`,
`position`, `alt_es` y `alt_en` como JSON al endpoint de imágenes del perfume.
Desvincularla no borra el archivo de la biblioteca.

El resumen del carrito se obtiene con POST /api/v1/cart/quote:

```json
{
  "locale": "es",
  "items": [
    {"variant_id": "UUID_DE_LA_PRESENTACION", "quantity": 1}
  ]
}
```

El UUID indicado es un marcador; usar un identificador existente.
No enviar precios o totales. El servidor devuelve importes decimales como cadenas.
Si no hay teléfono configurado, data.whatsapp_url es null y
data.configuration_error es WHATSAPP_NOT_CONFIGURED.
Cotizar no modifica inventario.

## Checkout y pedidos

`GET /api/v1/checkout/options` devuelve contacto/términos y destinos/bancos activos.
`POST /api/v1/checkout/quote` recibe `items`, `locale` y `city_id`; devuelve importes,
términos, bancos y `quote_token` firmado. No guardar el token en registros ni alterarlo.

`POST /api/v1/orders` requiere CSRF, `operation_id` UUID estable para reintentos,
`quote_token`, la misma selección/destino/idioma, `customer` con cédula, nombres,
apellidos, teléfono y correo, dirección opcional, método y aceptación de términos.
Para WhatsApp, JSON con `bank_id: null`; para transferencia, `multipart/form-data`
con `payload` JSON, `bank_id` de la cotización y `file` con la fotografía obligatoria.

Una transferencia conserva la cotización firmada aunque cambien las condiciones
antes de subir el comprobante. No se confirma el pago por subirlo. El propietario
lo aprueba en `/api/v1/admin/orders/{id}/approve-payment` con versión y estado destino.
El resultado distingue `confirmed`, `already_confirmed` y `stock_issue`; no tratar
cualquier respuesta 200 como venta confirmada sin revisar el resultado y el pedido.

El seguimiento usa `POST /api/v1/orders/track` con `code`. La recuperación utiliza
`POST /api/v1/orders/recovery` con cédula y CSRF; siempre responde sin revelar pedidos y envía
los códigos al correo registrado de cada pedido mediante el SMTP configurado. Tras una solicitud,
la misma cédula y la misma dirección esperan 10 minutos (429 `RECOVERY_COOLDOWN`). Sin SMTP
configurado responde 503 `RECOVERY_UNAVAILABLE`. El administrador no atiende solicitudes.
Para probar localmente se puede usar un servidor SMTP de captura en 127.0.0.1.

La cancelación de pedidos sin venta confirmada no modifica saldos. Las devoluciones
y reembolsos de ventas confirmadas no se implementaron en esta etapa.

## Revisar los prototipos

Desde la raíz:

```powershell
backend\.venv\Scripts\python.exe -m http.server 4322 --bind 127.0.0.1 --directory design
```

Abrir http://127.0.0.1:4322/prototypes/catalog.html .
Consultar design/README.md y las capturas de design/reviews/.
Detener el servidor con Ctrl+C al terminar.

## Arrancar el frontend

Desde frontend/:

```powershell
bun.cmd run dev
```

Abrir http://localhost:4321/es/ . El acceso administrativo está en
http://localhost:4321/es/admin/login . El origen utilizado debe coincidir
con FRONTEND_ORIGIN del backend para las operaciones protegidas por CSRF.

El frontend funciona con Astro SSR y Bun, y envía /api/ y /media/ al backend local.
BACKEND_URL puede definirse en frontend/.env; el valor predeterminado es
http://127.0.0.1:5000. No se necesitan credenciales de PostgreSQL en el frontend.
Si Flask no está disponible, las vistas conservan la navegación y muestran un error controlado.
La barra interna de desarrollo de Astro está desactivada.

## Pruebas del backend

Desde backend/:

```powershell
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest --cov=beront --cov-report=term-missing
```

Las pruebas de integración:
- Inician un PostgreSQL temporal autenticado en un puerto local disponible.
- Crean bases con nombres beront_test_ y roles limitados al clúster temporal.
- Aplican Alembic sobre cada base, sin create_all.
- Verifican que el rol runtime no tenga permisos DDL.
- Eliminan sus bases y detienen el clúster al terminar.
- No usan DATABASE_URL ni la base comercial.

POSTGRES_BIN permite indicar la carpeta que contiene initdb y pg_ctl.
En Windows se detecta por defecto C:\Program Files\PostgreSQL\18\bin.
El contexto de ejecución debe permitir iniciar PostgreSQL local.

Para nuevos cambios del esquema, modificar primero los modelos y ejecutar:

```powershell
uv run alembic revision --autogenerate -m "descripcion tecnica"
```

Revisar el archivo completo antes de aplicar la migración.
No modificar revisiones que ya se hayan aplicado.

## Pruebas visuales y herramientas frontend

La demostración adicional con el HTML del propietario se abre en
http://localhost:4321/temporal/ con el frontend levantado. No requiere Flask.
Su API simulada, fotografías locales y sustitución por el catálogo comercial
se documentan en [TEMPORARY_CATALOG.md](TEMPORARY_CATALOG.md).

Desde frontend/:

```powershell
bun.cmd x --bun playwright install chromium firefox webkit
bun.cmd x --bun playwright test
bun.cmd run check
bun.cmd run lint
bun.cmd run format
bun.cmd run build
bun.cmd run test
bun.cmd run test:app
```

playwright test mantiene las pruebas de los prototipos aprobados. Cubren 320, 360,
390, 768, 1024 y 1440 px, filtros, diálogos, idioma y teclado, y administran su propio servidor.

bun run test verifica el carrito persistente, la vista previa decimal exacta de inventario,
el JSON incrustado y los límites, rutas y cookies del proxy.

bun run test:app ejecuta backend/tests/integration/frontend_browser.py. Este proceso
inicia Flask, PostgreSQL y Astro en puertos temporales, crea una cuenta de prueba aleatoria
solo en esa base y comprueba la aplicación en Chromium, Firefox y WebKit. Verifica
creación y publicación de productos, fotografías, inventario, ambos tipos de presentación,
carrito sin reservas, idiomas, agotados, cierre de sesión, CSRF, límites y responsividad.
El informe se guarda en frontend/test-results/application-report.json.
Los procesos y datos temporales se eliminan al finalizar. El servidor normal del frontend
y la base comercial permanecen separados de estas pruebas.

BUN_BIN permite indicar el ejecutable de Bun si no está disponible en PATH.
Los plugins Astro de ESLint y Prettier están fijados a versiones compatibles con Astro 7.

## Auditorías

Desde backend/: uv run pip-audit --local --progress-spinner off.
Desde frontend/: bun.cmd audit.

El paquete local beront no está publicado en PyPI y se excluye de la consulta
de avisos de paquetes públicos. Su código se verifica mediante las pruebas y revisión local.
