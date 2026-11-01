# Ampliación de BÉRONT: implementación y cumplimiento

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

Cada función tiene su archivo, módulo y versión en `bd/`. Las migraciones registran ruta y SHA-256 y rechazan fuentes modificadas. No se editó la migración inicial aplicada. Cada cambio posterior tiene su revisión propia; la última revisión modifica una función sin cambiar tablas.

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
uv run flask --app beront.app:create_app createsuperuser
uv run python semillas/importar_catalogo.py
uv run python semillas/importar_catalogo.py --apply
uv run flask --app beront.app:create_app run --host 127.0.0.1 --port 5000
~~~

La base ya está migrada: repetir `upgrade head` no modifica revisiones aplicadas. `createsuperuser` pide usuario y contraseña oculta; solo se ejecuta para crear al propietario una vez. No se inventó una cuenta. Para recuperar acceso:

~~~powershell
uv run flask --app beront.app:create_app reset-password NOMBRE_DE_USUARIO
~~~

Antes de probar checkout, registrar contacto, ciudades/tarifas, bancos y términos desde sus endpoints administrativos; las nuevas pantallas de configuración esperan aprobación visual.

En otra terminal, desde `frontend/`:

~~~powershell
bun.cmd install --frozen-lockfile
bun.cmd run dev
~~~

Abrir `http://localhost:4321`, coherente con `FRONTEND_ORIGIN`. Los prototipos están en `/temporal/checkout.html`, `/temporal/order-tracking.html`, `/temporal/admin-settings.html`, `/temporal/admin-media.html` y `/temporal/admin-orders.html`.

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
$env:BERONT_TEMPORARY_BASE_URL='http://127.0.0.1:4321'
bun.cmd x --bun playwright test tests/e2e/temporary-commerce.spec.ts --workers=1
~~~

## Próximo paso y cierre pendiente

La revisión 04 se documenta en [design/README.md](../design/README.md). `AGENTS.md`, regla 9, exige: “No implementar una vista del producto sin aprobación explícita de su prototipo vigente.”

Una vez aprobadas las nuevas vistas se implementarán sus páginas Astro contra las APIs reales, se sustituirán las opciones comerciales anteriores y se retirarán las copias y simulador temporal del frontend tras verificar la importación comercial. Después se ejecutarán las pruebas integrales de aplicación y se cerrará la matriz de cumplimiento.

No se realizaron operaciones que modifiquen Git, ni tareas de despliegue.

