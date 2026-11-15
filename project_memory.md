# Memoria del proyecto BÉRONT

## Restablecimiento de la base Docker — 14 de noviembre de 2026

La conexión vigente del equipo es `beront-bd` en PostgreSQL de Docker (`127.0.0.1:5432`),
con los roles `beront_app` y `beront_migrator` de `backend/.env`. Por solicitud del propietario,
tras borrar las imágenes de `uploads`, se restablece el esquema con downgrade a base y upgrade
a head de las migraciones Alembic existentes, dentro de una transacción. Se conserva únicamente
el administrador con sus credenciales actuales y se restituyen los permisos de funciones del
rol de ejecución. Se vuelve a cargar la semilla v2 y el Home; se conservan el contenedor,
los roles, `.env` y los servidores del propietario. Las referencias a `beront-bd2` siguientes
describen una instalación anterior y no la conexión vigente de este equipo.
Verificado: 127 perfumes, 43 marcas, 425 presentaciones, 133 respuestas de medios con SHA-256
idéntico a la semilla y seis mensajes del Home (cinco públicos). Inventario cero, sin pedidos,
movimientos ni sesiones. `alembic check` no detecta diferencias con los modelos; staging vacío.

## Semilla canónica del catálogo final — 14 de noviembre de 2026

El propietario establece como única fuente los 127 perfumes de Decants y las imágenes de sus
URL vigentes listadas en la conversación. Se sustituye la semilla anterior en su ubicación
existente: `backend/semillas/catalogo/catalogo.json` v2 y `imagenes/`. Contiene 127 perfumes,
43 marcas, 425 presentaciones (400 decants y 25 completos, nueve desactivadas) y 133 fotos
WebP RGBA: 127 principales y seis adicionales. Los archivos se copian del almacenamiento del
producto final, conservando sus bytes, transparencia y dimensiones; no se regeneran desde diseño.
Delina incluye su foto actual. Se retiran únicamente los 132 archivos de la semilla antigua.

El importador verifica las huellas SHA-256 y los metadatos antes de importar; conserva los
estados de las presentaciones y sigue omitiendo perfumes existentes sin sobrescribir cambios
administrativos ni existencias. La instalación nueva no depende de `design/` ni necesita
`importar-recortes`, que rechaza la semilla v2. Los nombres de archivo `/media/` se generan
por instalación y no son identificadores compartidos; el contenido de las fotos sí coincide.
Los registros anteriores de 130 perfumes, 132 originales y Delina sin foto son históricos.

Aplicado en `beront-bd2`: cuatro migraciones hasta `de252c02c932`, 127 perfumes, 133 medios y
seis mensajes del Home. Se conserva el administrador local con las mismas credenciales y sin
sesiones copiadas; los saldos empiezan en cero. Ambas conexiones de `backend/.env` apuntan a
`beront-bd2`; la base anterior queda intacta. Verificados los 127 nombres y las 133 respuestas
de imagen byte por byte, sin cambios de calidad. Suite de 187 pruebas backend, Ruff y formato
correctos. Los servidores del propietario no se reinician: el backend leerá la nueva conexión
al reiniciarlo el propietario. No se realizan commits, push ni cambios de historial Git.

## Navidad R01 — propuestas visuales, 14 de noviembre de 2026

Se preparan tres prototipos autónomos en design/: A · Noche de nieve, B · El arte de regalar,
C · Gabinete de Navidad, con comparador navidad-r01-propuestas.html. Fuentes y recortes existentes;
sin cambios en el producto, datos o servidores habituales. Referencias primarias de premios
públicos CSS Design Awards y campaña Dior 2026 documentadas en design/reviews/navidad-r01-referencias.md.
288 combinaciones responsivas y 21 recorridos interactivos correctos en tres motores, con
textos ampliados, reducción de movimiento, teclado y simulación de dispositivos. Pendiente
de elección/aprobación; no integrar en frontend hasta recibir instrucción explícita.
El comparador se abre desde archivo en Chrome y no depende del servidor temporal de revisión.
## Semilla e imágenes cargadas; footer corregido — 14 de noviembre de 2026

El propietario solicita eliminar la franja blanca bajo el footer e importar la semilla
porque faltan las imágenes. Crea el administrador desde su terminal; después se ejecutan
los importadores existentes de catálogo y Home. Resultado: 130 perfumes, 400 presentaciones,
132 imágenes nuevas y seis mensajes del Home, cinco activos. Los saldos nuevos quedan en
cero y se conserva el carrito abierto. Las 132 imágenes públicas responden HTTP 200 como WebP.

Esta instalación usa las fotos originales de `backend/semillas/catalogo/imagenes`.
Delina Eau de Parfum sigue sin foto en esa fuente; los recortes R02 no están presentes
en el equipo y no se aplicaron. Los registros de transparencia anteriores corresponden
a otra instalación y se conservan como histórico.

La reserva inferior del menú flotante se traslada del body público al interior del footer
mediante el token compartido `--main-menu-clearance` de `global.css`. Se conserva el
espaciado de administración, el diseño aprobado y el acceso al menú sin tapar el footer.
Las comprobaciones usan el backend del propietario y un frontend temporal en 4323;
los procesos habituales 4322 y 5000 permanecen intactos.

Verificación completada: 270 comprobaciones de footer y menú en Chromium, Firefox y
WebKit, 15 anchos entre 320 y 2560 px, texto normal/ampliado y navegación por teclado.
Se inspeccionan capturas de escritorio y móvil y se confirma el ajuste en 4322. Prettier
correcto. El frontend temporal se detiene y se eliminan sus capturas y registros.

## Preparación local con Docker y Mailpit — 14 de noviembre de 2026

El propietario solicita crear los `.env` de backend y frontend, preparar una base nueva
en Docker, usar Mailpit local y detener los contenedores que estaban activos. Se detiene
`deploy-dev-db-1`, conservando su contenedor y volumen. Se crean `beront-postgres`
(PostgreSQL 18, `127.0.0.1:5432`) y `beront-mailpit` (SMTP 1025 y web 8025, solo loopback),
con volúmenes persistentes propios; estos dos servicios quedan activos.

`beront-bd` se instala desde vacío con las cuatro migraciones existentes revisadas,
hasta `de252c02c932`; `alembic check` no encuentra diferencias. Se separan los roles
`beront_migrator` y `beront_app`: la aplicación ejecuta funciones SQL sin privilegios
de superusuario, creación de objetos ni acceso directo a tablas. Los secretos nuevos
permanecen en la configuración local y no se registran en documentación.

Ambos `.env` están excluidos de Git. Se conserva el frontend en `localhost:4322`, la API
en `127.0.0.1:5000`, el catálogo público limitado y el carrito abierto sin exigir saldo.
Mailpit usa el remitente local de captura `beront@localhost.test`. La base nueva queda
sin administrador, productos ni existencias: esta preparación no importa datos comerciales.
Los comandos de arranque y la operación de Docker se documentan al inicio de `docs/LOCAL.md`.

Se instalan las dependencias de ambos locks sin modificarlos. Bun se actualiza de 1.3.14
a la versión estable 1.4.4 porque la anterior no reconoce el formato de `bun.lock`.
La configuración histórica y los datos comerciales descritos en otras fechas no se
trasladan automáticamente a esta instalación.

Verificados los permisos restringidos, las rutas públicas de API y las tres páginas
del catálogo con su proxy; la sesión anónima devuelve 401. Mailpit responde por web y
SMTP sin enviar mensajes. Los servidores y archivos de verificación temporales se
eliminan; quedan únicamente los dos contenedores de infraestructura solicitados.

## Auditoría funcional, rendimiento y dependencias — 13 de noviembre de 2026

Se completa la auditoría solicitada; informe vigente en `docs/AUDITORIA.md`, con histórico
conservado. Se corrigen filtros obsoletos por concurrencia, identificadores manipulados del
carrito, reemplazo por la misma presentación, errores con caracteres dañados y bloqueo de
recopilación de pytest. Se comparten cotizaciones idénticas solo mientras están en curso,
sin caché de importes; se eliminan consultas repetidas de definiciones, páginas vacías y
consultas de stock sin identificadores. No se cambian datos comerciales, fotos ni diseño.

Benchmark aislado con 130 perfumes: filtros de 15 a 8 llamadas PostgreSQL; catálogo de 3 a 2;
cambio de cantidad de dos a un POST de cotización. Los tiempos locales mejoran ligeramente;
no representan capacidad de producción. Se conserva un benchmark reproducible en
`backend/tests/integration/benchmark_catalog.py`. Minimatch se fija en 11.0.1 con bun.lock
para corregir el aviso moderado de herramientas; auditorías Python/Bun sin avisos conocidos
(beront local omitido en PyPI). Se actualizan expectativas de navegador al diseño aprobado y
se aíslan las salidas del harness para impedir colisiones de trazas.

Verificación: 184 pruebas backend, cobertura combinada 93,82 %, 28 unitarias frontend,
63 escenarios de navegador del perfil completo y 12 del perfil WhatsApp aprobados en los tres
motores. Ruff, tipos, ESLint, formato y build correctos. Bases, almacenamiento y servidores
de pruebas temporales. No hay mensajes ni correos reales, movimientos o pedidos del propietario.

Pendientes documentados: conexión local PostgreSQL con privilegios de superusuario y peso
alto de imágenes. Se mantienen credenciales y calidad aprobada. Las correcciones Python
se activaron tras autorización explícita de reiniciar solo el backend 5000: PID 44808.
Frontend 4322 conservado con PID 91551; catálogo, filtros, Home y sus tres páginas públicos
responden HTTP 200. Se cierra solo el frontend temporal 4323. No realizar operaciones Git sin orden expresa.


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


## Carrito por WhatsApp — decisión vigente del 13 de noviembre de 2026

El propietario solicita habilitar carrito y resumen a 0939237376 y aclara «por ahora coloquemos
abierto, sin especificar cantidad». Se prepara `CART_REQUIRES_STOCK=false` en backend local y
se configura `593939237376` mediante CommerceService, sin modificar términos ni inventario.
La apertura permite solicitudes; manualmente agotados, ocultos o inactivos siguen bloqueados.
Checkout/pedidos conservan validación estricta. El carrito almacena IDs/cantidades, cotiza desde
backend y abre WhatsApp con marca/modelo/ml/cantidad/importes/total, sin envío automático.
`PUBLIC_CART_ENABLED` reactiva los controles aprobados y conserva solo Inicio, Decants y
Perfumes completos en el menú. No reactivar pedidos/admin/checkout en navegación pública.
El propietario autorizó reiniciar únicamente el backend 5000 y se activó el cambio.
Se corrigió FRONTEND_ORIGIN a http://localhost:4322; el frontend existente no se reinició.
Comprobado en Chrome: agregar Amber Oud Gold Edition (120 ml, $90), aumentar a dos ($180)
y eliminar. El producto de prueba se retiró del carrito; no se envió ningún WhatsApp.


Fecha de consolidación: **4 de noviembre de 2026**. Zona: **America/Guayaquil**.
Actualización de decisiones, navegación, imágenes y Home: **9 de noviembre de 2026**.
Creada por solicitud expresa del propietario para conservar el estado, las decisiones y el
registro de cambios del software principal y de cada familia de prototipos.

## 1. Lectura rápida para retomar el trabajo

| Tema | Estado al cierre de este registro |
|---|---|
| Etapa | Desarrollo y ejecución local; sin despliegue autorizado. |
| Software principal | Backend Flask/PostgreSQL y frontend Astro/Bun implementados; la última auditoría general está en docs/AUDITORIA.md, 13 de noviembre. |
| Portada del software | `/[locale]/index.astro` carga `HomePage.astro`, con mensajes persistentes, recortes R02, cinta y accesos; integrado el 9 de noviembre. |
| Perfumes completos del software | `CylinderPage.astro`, carrusel manual con cinta de marcas, aprobado e implementado el 2 de noviembre. |
| Decants del software | `DecantStudio.astro`, basado en C / Frasco vivo con lista y carrito, aprobado e implementado el 2 de noviembre. |
| Menú principal nuevo | Aprobado el 3 de noviembre, navegación integrada el 7; Home y gestión de mensajes implementados el 9. |
| Recortes sin fondo | Las ediciones previas a Inkscape siguen descartadas. R02, solo frascos, aprobado e integrado el 8 de noviembre. |
| Última entrega de recortes | 132 PNG maestros y SVG editables R02; 135 vínculos del catálogo local actualizados. |
| Alcance de la última intervención funcional | Home con backend de mensajes, gestión en Configuración y fotografías R02 sin fondo. |
| Catálogo fuente | Semilla v2: 127 perfumes, 43 casas, 425 presentaciones y 133 archivos/vínculos de fotos. |
| Vistas del último prototipo | 24 perfumes completos y 119 decants. Son grupos que se superponen, no 143 perfumes diferentes. |
| Fotografía faltante | Ninguna en la semilla v2; Delina Eau de Parfum incluye la foto vigente del producto final. |
| Datos comerciales actuales | La semilla reproduce los precios y presentaciones actuales de los 127 perfumes; los nuevos saldos empiezan en cero. |
| Procesos observados ahora | API en 5000 y aplicación real en 4322; diseño en 4367. 4321 pertenece a otro proyecto. No detener ni reemplazar. |
| Git | Árbol de trabajo con numerosos cambios anteriores; no hacer commit, push, merge, ramas ni restauraciones sin orden expresa. |

**Los apartados históricos conservan estados anteriores.** La solicitud del 8 de noviembre
autoriza integrar R02 en el producto; el registro vigente está en `docs/DESIGN_APPROVALS.md`.
Otras propuestas siguen sujetas a su aprobación específica.

## 2. Fuentes y prioridad de la información

- [AGENTS.md](AGENTS.md): reglas de trabajo del propietario.
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): arquitectura y ampliaciones autorizadas.
- [DESIGN_APPROVALS.md](docs/DESIGN_APPROVALS.md): aprobaciones, rechazos y decisiones visuales.
- [AUDITORIA.md](docs/AUDITORIA.md): auditoría de integración del 2 de noviembre.
- [IMPLEMENTATION.md](docs/IMPLEMENTATION.md): avances por fecha; contiene apartados históricos.
- [LOCAL.md](docs/LOCAL.md): preparación, comandos y operación local; contiene estados fechados.
- [reporte.md](docs/reporte.md): auditoría histórica del 26 de octubre; no representa por sí sola el estado vigente.
- [design/README.md](design/README.md): acceso a la revisión actual y sus capturas.
- Código y archivos presentes, inventariados al crear esta memoria, más las decisiones expresadas
  por el propietario en esta conversación.

Los resultados de pruebas anteriores se identifican por su fecha y origen. Esta consolidación
documental **no ejecutó de nuevo la suite del software principal** ni volvió a auditar su seguridad.
Un archivo presente no demuestra por sí solo que una funcionalidad esté operativa contra la base
comercial. Una captura o una prueba técnica no sustituye una aprobación visual.

Las revisiones se numeraron por familias. La **revisión global 04** corresponde al checkout y
la administración de octubre; la **revisión 04 de recortes** corresponde a las fotos sin fondo
del 4 de noviembre. No son la misma revisión.

## 3. Decisiones que deben conservarse

### 3.1. Arquitectura y organización

- Monolito modular Flask y PostgreSQL; frontend Astro SSR, TypeScript, Tailwind y Bun.
- Dominio independiente de Flask, SQLAlchemy, Pydantic y frontend.
- Capas `domain`, `application`, `infrastructure` y `presentation`; controladores sin reglas
  comerciales ni SQL directo; no acceder a modelos internos de otro módulo.
- SQLAlchemy es la única definición del esquema para Alembic. El acceso de la aplicación usa
  funciones PostgreSQL mediante repositorios y `shared/infrastructure/pg_call.py`, con parámetros
  enlazados y nombres permitidos; no usa sesiones ORM para leer o escribir datos de aplicación.
- Funciones vigentes en `backend/bd/<modulo>/funciones/`, una por archivo, sin carpetas `vNNNN`.
- Esquema mediante migraciones generadas desde modelos y revisadas; sin `create_all`, alteraciones
  manuales de tablas ni edición de migraciones ya aplicadas.
- Conservar `uv.lock` y `bun.lock`. Consultar dependencias que cambien la arquitectura o añadan
  capacidades no autorizadas. Los recortes actuales no añadieron dependencias.
- Prototipos, fuentes visuales y capturas dentro de `design/`. La solicitud de esta memoria
  autoriza el documento `project_memory.md` en la raíz, registrado también en la arquitectura.
- No se modificó la arquitectura funcional para preparar los recortes o esta memoria.

### 3.2. Negocio, dinero, pedidos e inventario

- Español e inglés, importes en USD y operación para Ecuador continental; Galápagos y destinos
  insulares fuera del alcance comercial autorizado.
- Dinero y mililitros con `Decimal` en el backend. El servidor determina precios, totales,
  disponibilidad, tarifas y permisos; el navegador no es autoridad comercial.
- La marca manual de agotado prevalece sobre existencias positivas.
- El carrito y el checkout incompleto no vencen, no reservan y no descuentan inventario.
- Crear un pedido pendiente o subir un comprobante no confirma un pago ni una venta.
- Solo la aprobación administrativa del pago puede producir la salida de inventario, comprobando
  todas las líneas en una transacción, sin saldos negativos ni movimientos parciales.
- Entre pagos concurrentes, la primera aprobación con existencias obtiene el stock. Otro pago real
  sin stock se registra como incidencia y se coordina por WhatsApp.
- Conservar la cotización firmada de una transferencia ya realizada aunque cambien precios,
  tarifas, cuenta o stock antes de subir el comprobante; registrarla no confirma la venta.
- Estados y transiciones administrables en PostgreSQL y en el panel, con fases técnicas que no
  permiten saltarse las comprobaciones de pago, inventario o despacho.
- Ajustes de existencias con motivo, actor e idempotencia.
- Pedidos persistentes, revisión manual de transferencias, pago coordinado por WhatsApp y
  seguimiento autorizados. No introducir cobros automáticos, reservas, reembolsos automáticos
  ni nuevas políticas comerciales sin decisión expresa.
- Categorías, públicos, casas, presentaciones, acordes, usos y perfiles provienen de datos
  persistentes; no fijar «5 ml», «unisex» ni listas comerciales como supuestos del producto.
- Un administrador creado por CLI; sin registro público. No inventar usuarios, contraseñas,
  teléfonos, bancos, tarifas, productos o promociones.

### 3.3. Diseño, accesibilidad y autorización de implementación

- Backend completo de punta a punta antes de implementar el frontend de una capacidad nueva.
- Prototipo vigente aprobado expresamente antes de implementar una vista; registrar la aprobación
  en `docs/DESIGN_APPROVALS.md`. Aprobación arquitectónica y visual son decisiones diferentes.
- Tokens aprobados: blanco `#F8F8F8`, negro `#0B0B0B` y champán `#B8A58A`.
- Cormorant Garamond para títulos y Source Sans 3 para lectura y controles, con fuentes locales.
- Iconografía SVG revisada; sin emojis en interfaz, código ni documentación.
- Accesibilidad WCAG 2.2 AA: teclado, foco, etiquetas, contraste y controles táctiles accesibles.
- Panel visible con tamaño del texto, contraste y reducción de animaciones, sin sustituir las
  herramientas de accesibilidad del dispositivo.
- Adaptación de todas las alternativas a los rangos compacto, mediano, expandido, grande y
  extragrande, y a Android, iPhone, tablet, laptop, escritorio y TV/control remoto.
- Referencias de rango: menos de 600, 600–839, 840–1199, 1200–1599 y 1600 en adelante.
- Priorizar tokens, componentes compartidos, Grid/Flexbox, unidades relativas y Container Queries;
  evitar parches acumulativos y cambios arquitectónicos para resolver detalles visuales.
- La skill interna `/design` no figuraba entre las skills disponibles en esta conversación.

### 3.4. Operación y cuidado del trabajo existente

- Solo ejecución local en esta etapa; no publicar ni desplegar.
- No detener, reiniciar ni reemplazar los servidores que el propietario tenga levantados.
- Para revisar interfaces, reutilizar el backend del propietario y abrir un frontend de revisión
  en un puerto libre. Las pruebas con datos propios usan base y servidores temporales.
- No usar la base comercial para crear pedidos, existencias o cuentas de prueba.
- Limpiar los scripts y datos temporales propios, conservando pruebas permanentes aprobadas,
  fotografías originales y datos de negocio.
- No ejecutar operaciones Git que cambien historial o remoto sin solicitud expresa. El árbol
  de trabajo actual no está limpio; no restaurar ni borrar cambios para «ordenarlo».
- No registrar secretos, cookies, tokens o contraseñas. Esta memoria no contiene valores de `.env`.

## 4. Software principal: estado por módulo

| Área | Funcionalidad y evidencia presente | Límite o pendiente |
|---|---|---|
| Identidad | Autenticación, contraseñas protegidas, sesiones revocables, CSRF, permisos y CLI de administrador en `modules/identity/`. | Confirmar existencia del administrador comercial sin inventar credenciales. |
| Catálogo | Perfumes, casas, categorías, públicos, variantes, imágenes, acordes/usos/perfiles, búsqueda, facetas y filtros en `modules/catalog/`. | Datos comerciales efectivos no consultados en esta tarea. |
| Inventario | Saldos por ml/unidades, ajustes, concurrencia, versiones e idempotencia en `modules/inventory/`. Listados devuelven nombres y permiten búsqueda/tipo. | No cambiar existencias por la preparación de prototipos. |
| Carrito | Cotización validada por backend; por línea devuelve `product_slug`, `image_url` y `options` para presentaciones hermanas. | El carrito simulado de los HTML de diseño no es este carrito comercial. |
| Medios | Biblioteca reutilizable, deduplicación, vinculación y comprobantes privados en `modules/media/`; imágenes originales en infraestructura de catálogo. | No existe todavía el proceso aprobado para guardar y revisar derivados sin fondo. |
| Comercio | Contacto, bancos, tarifas por ciudad, términos y configuración administrable en `modules/commerce/`. | Datos comerciales reales corresponden al propietario. |
| Pedidos | Pedidos persistentes, transferencias, WhatsApp, cotizaciones firmadas, revisión manual, transiciones, guía, seguimiento y recuperación por correo en `modules/orders/`. | No se documentó una prueba de envío SMTP real; sin cobro automático ni API del transportista. |
| Frontend público | Estudio de decants, carrusel de completos, ficha, carrito, checkout y seguimiento en `frontend/src/`. | Menú nuevo y recortes recientes siguen como prototipos. |
| Administración | Acceso, catálogo, editor, inventario, configuración, medios y pedidos. | No atribuirle funcionalidades nuevas solo porque aparezcan en un HTML de diseño. |

Rutas reales presentes, bajo `/[locale]`:

- `/`: carga `features/catalog/DecantStudio.astro`.
- `/catalog/decants`: carga el mismo estudio.
- `/catalog/full-bottles`: carga `features/catalog/CylinderPage.astro`.
- `/products/[slug]`, `/checkout` y `/orders`.
- `/admin/login`, `/admin`, `/admin/inventory`, `/admin/products`, `/admin/products/new`,
  `/admin/products/[id]`, `/admin/settings`, `/admin/media` y `/admin/orders`.
- Proxy de destino fijo para `/api/*` y `/media/*`; el backend conserva autenticación y autorización.

Archivos centrales del catálogo actual:

- `frontend/src/features/catalog/{DecantStudio,CylinderPage,StudioFilters,CartSummary}.astro`.
- `frontend/src/features/catalog/{studio,cylinder,cylinder-layout,liveFilters,summary,perfume}.ts`.
- `frontend/src/features/cart/{CartDialog.astro,dialog.ts,store.ts,quote.ts}`.
- `frontend/src/shared/components/{AccessibilityPanel.astro,accessibility.ts,vial.ts,motion.ts}`.
- `frontend/src/features/admin/{ProductEditor.astro,editor.ts,options.ts}`.

Las preferencias de accesibilidad del producto usan `beront.a11y.v1`; son distintas de las marcas
y notas de revisión del prototipo de fotos.

### 4.1. Migraciones y versiones declaradas

Cadena de migraciones presente en el repositorio:

1. `0e7393567f81_initial_schema.py`: esquema inicial consolidado y funciones SQL.
2. `87313231bdf2_inventory_labels_and_filters.py`: nombres y filtros de inventario.
3. `49ce23c2f0c8_keep_inactive_classification_links.py`: conserva vínculos a opciones desactivadas.

La cabeza **del código** es `49ce23c2f0c8`. La auditoría del 2 de noviembre informó la misma
revisión aplicada y sin diferencias con los modelos; no se consultó Alembic contra la base
comercial al crear esta memoria.

Inventario actual: 89 archivos SQL en `backend/bd/`. Backend y frontend declaran versión de
proyecto `0.1.0`. Dependencias declaradas relevantes: Python `>=3.13`, Flask 3.x, SQLAlchemy 2.x,
Alembic, psycopg, Pydantic 2.x, Pillow, Astro `^7.4.2`, adaptador Node `^11.1.9`, Tailwind 4.x,
TypeScript y Playwright. Las versiones resueltas las determinan los lockfiles.

### 4.2. Limitación concreta para implementar la transparencia

`backend/src/beront/modules/catalog/infrastructure/images.py`, clase `LocalImageStorage`,
normaliza actualmente las cargas con `ImageOps.exif_transpose(image).convert("RGB")` y guarda WebP
con calidad 88. Por tanto, el proceso vigente no conserva un canal alfa de entrada como tal.

**No basta con copiar los recortes al frontend o subir un PNG transparente por la vía existente.**
Antes de implementar deben definirse y aprobarse los derivados, su preservación de transparencia,
almacenamiento, vínculos, revisión y permisos, y completar el backend con sus pruebas. Si se
elige un modelo de segmentación, su dependencia se consulta por separado. La implementación
debe conservar el original y no alterar fotografías comerciales para adaptarlas al prototipo.

## 5. Registro cronológico del software principal

| Fecha / registro | Cambio o decisión | Resultado y procedencia |
|---|---|---|
| 23 oct., SW-01 | Arquitectura inicial aprobada; monolito modular, stack, organización y límites. | Arquitectura vigente con ampliaciones fechadas posteriores. |
| 24 oct., SW-02 | Aprobación de seis vistas de la revisión visual 01 y solicitud de implementación. | Integradas en Astro con autenticación, proxy, administración, inventario y carrito. Según registro visual: 12 pruebas unitarias y 6 de aplicación de aquella integración. |
| 25 oct., SW-03 | Catálogo importado y demostraciones con el HTML del propietario. | Los datos originales se consolidaron después en la semilla del backend; el contenido temporal del frontend fue retirado. |
| 26 oct., SW-04 | Auditoría histórica de backend. | `docs/reporte.md`: 82 pruebas, cobertura y hallazgos de esa fecha. Su alcance precede los pedidos persistentes y ampliaciones posteriores. |
| 27 oct., SW-05 | Acceso mediante funciones PostgreSQL, modelos solo para esquema, administrador único, catálogos comerciales, medios, checkout y pedidos. | Backend ampliado; documentación histórica informa 120 pruebas y 94,10 % de cobertura. Vistas nuevas aún no estaban integradas en ese corte. |
| 27 oct., SW-06 | Cotización firmada de transferencias ya realizadas y concurrencia de pagos. | Pedido pendiente conserva la cotización; inventario solo al aprobar; pago sin stock como incidencia. |
| 31 oct., SW-07 | Aprobadas e implementadas revisiones globales 04/05: checkout, seguimiento, biblioteca, pedidos y configuración. | Backend primero; integración Astro de las cinco áreas. Documento de implementación informa 139 pruebas backend y 21 de navegador en ese corte. |
| 31 oct., SW-08 | Acordes, usos y perfiles persistentes; recuperación de códigos por correo y límite de 10 minutos; `X-Client-IP` desde proxy. | Se sustituyó la atención administrativa de recuperaciones. Pruebas de correo simuladas/locales; sin prueba SMTP real registrada. |
| 31 oct., SW-09 | Revisión global 06: unificación de tienda negra, carrito como diálogo, checkout y seguimiento. | Aprobada e implementada; se retiró `/cart`. El prototipo temporal de esta unificación se eliminó por orden del propietario. |
| 1 nov., SW-10 | `bd/` pasa a `backend/bd/`; desaparecen carpetas SQL de versión; consolidación de migraciones; CLI `beront`. | Cadena inicial única más correcciones posteriores. Se retiraron huellas SQL del proceso de instalación. |
| 1 nov., SW-11 | Retiro del catálogo temporal del frontend. | Eliminados `public/temporal`, ruta temporal y adaptador temporal; se conservan semilla y fotos originales del backend. |
| 2 nov., SW-12 | Auditoría de alineación backend/frontend. | Nombres/filtros de inventario, conservación de vínculos inactivos, opciones configurables, activación/desactivación y mensajes ES/EN corregidos. |
| 2 nov., SW-13 | Backend de carrito ampliado para el estudio de decants. | Cotización añade slug, foto y opciones hermanas; se revalida stock. |
| 2 nov., SW-14 | Aprobación e implementación de Decants C / Frasco vivo con lista y carrito. | Componentes de estudio, cambios de ml por línea, accesibilidad compartida y resumen en página por defecto. |
| 2 nov., SW-15 | Aprobación e implementación de Cilindro con cinta para completos. | Carrusel manual, filtros vivos y paginación del backend; retirada de componentes antiguos de cuadrícula/héroe. La portada pasa al estudio de decants. |
| 2 nov., SW-16 | Retiro de supuestos comerciales fijos y correcciones de infraestructura de pruebas. | Etiquetas desde facetas, presentaciones configuradas, `workers: 1` y Astro temporal con `--ignore-lock`; ver auditoría. |
| 3 nov., SW-17 | Menú principal y mensajes destacados aprobados visualmente. | Solo prototipo. Backend de mensajes y luego frontend pendientes; no darlo por implementado. |
| 4 nov., SW-18 | Galería y vistas de recortes sin fondo. | Solo `design/` y documentación. No cambió el software comercial, el esquema, las fotos originales, las dependencias ni el inventario. |
| 7 nov., SW-19 | El propietario descarta imágenes sin fondo y señala la ausencia del menú aprobado. | Navegación inferior integrada con sesión, permisos, idiomas, carrito y accesibilidad existentes. Fotos originales conservadas. Portada de mensajes aún pendiente. |
| 4 nov., SW-19 | Creación de esta memoria por solicitud del propietario. | Registro consolidado, referencias desde README y organización documental; sin nuevas funcionalidades. |

Los cambios del software anteriores a los recortes proceden de documentación y del árbol de
trabajo existente. No se atribuyen a las últimas intervenciones de prototipos. El árbol Git no
permite reconstruir todas esas etapas como commits independientes.

### 5.1. Auditoría general documentada del 2 de noviembre

Correcciones registradas en `docs/AUDITORIA.md`:

1. Inventario devuelve nombre de producto/casa y volumen, busca por `q`, filtra por `kind` y pagina
   en SQL; también se corrigieron los movimientos.
2. Guardar opciones de un perfume solo reemplaza los vínculos activos; los inactivos se conservan.
3. Editor y filtros públicos reciben acordes, usos y perfiles que el backend ya admitía.
4. Nombres de categorías y públicos desde `facets.definitions`, sin etiquetas comerciales fijas.
5. Editor ofrece presentaciones configuradas que el perfume todavía no tiene.
6. Retiro de presentación preferida de 5 ml, público unisex por defecto y categorías buscadas por nombre fijo.
7. Activar/desactivar categorías, públicos, opciones, presentaciones, ciudades, bancos, estados y transiciones.
8. Siete códigos de error recibieron mensajes ES/EN en vez de caer en el mensaje genérico.
9. Inventario distingue «Con existencias» y «Sin existencias», sin confundir saldo con disponibilidad comercial.
10. Retiro de recursos/pruebas temporales, textos de demostración y configuración obsoleta de prototipos.

Resultados históricos informados: 145 pruebas backend, cobertura 94,12 %, 18 unitarias frontend,
27 de navegador con Flask/PostgreSQL/Astro temporales; tipos, lint, formato y compilación sin
incidencias; `pip-audit` sin vulnerabilidades conocidas en esa fecha.

Limitaciones de ese registro: aviso moderado de `minimatch` en herramientas de desarrollo,
rol local de ejecución con privilegios elevados por decisión del propietario, configuración/datos
comerciales pendientes y cálculo de facetas a vigilar si aumenta mucho el catálogo. No se afirma
que el aviso de dependencias continúe vigente hoy sin ejecutar una auditoría nueva.

## 6. Catálogo y fotografías de referencia

Fuente: `backend/semillas/catalogo/catalogo.json` y `backend/semillas/catalogo/imagenes/`.
Sus conteos se volvieron a leer al redactar esta memoria:

| Elemento | Cantidad / estado |
|---|---|
| Perfumes únicos | 127 |
| Casas comerciales | 43 |
| Presentaciones | 425: 400 decants y 25 completos; nueve desactivadas |
| Archivos de imagen únicos | 133 |
| Asociaciones de fotografía con perfumes | 133 |
| Perfumes con decants | 127 |
| Sin fotografía | Ninguno |

Un perfume puede pertenecer a ambos tipos. Se incluyen las 127 fotos principales y seis
alternativas. Cada archivo tiene su SHA-256 y conserva la transparencia del catálogo final.

Las fotos, nombres, casas, tamaños y precios del prototipo proceden de la semilla. No son una
consulta en vivo a existencias, publicación, precios o configuración comercial de PostgreSQL.
La semilla y el importador no asignan existencias positivas ni reinician saldos.

## 7. Historial de prototipos anteriores y sus decisiones

### 7.1. Revisiones globales de octubre

| Prototipo / revisión | Cambios y evolución | Decisión / estado del archivo hoy |
|---|---|---|
| `catalog.html`, global 01 | Catálogo y filtros de la primera revisión. | Aprobado el 24 de octubre e integrado; HTML no presente hoy en `design/prototypes/`. |
| `product.html`, global 01 | Ficha de perfume para decant y botella completa. | Aprobado e integrado; HTML histórico ausente hoy. La ficha real sigue siendo una página. |
| `cart.html`, global 01 | Carrito inicial y continuación comercial. | Aprobado e integrado; evolucionó a diálogo en global 06. HTML histórico ausente. |
| `login.html`, global 01 | Acceso administrativo. | Aprobado e integrado; HTML histórico ausente. |
| `admin-catalog.html`, global 01 | Administración de perfumes y editor. | Aprobado e integrado; ampliado con catálogos y opciones persistentes. HTML histórico ausente. |
| `admin-inventory.html`, global 01 | Saldos y ajustes de inventario. | Aprobado e integrado; API y filtros corregidos el 2 de noviembre. HTML histórico ausente. |
| `catalog-import.html`, global 02 | Demostración de catálogo/ficha/carrito con 130 perfumes del HTML original y disponibilidad sin confirmar. | Solicitado el 25 de octubre, no aprobado. Recursos temporales del frontend retirados el 1 de noviembre; HTML ausente hoy. |
| `catalog-refined.html`, global 03 | Cabecera, héroe y pie negros; carrusel, presentaciones y agregado desde tarjetas, resumen y accesibilidad. | Aprobado el 31 de octubre con modificaciones; integrado mediante global 06. Archivo ausente hoy. |
| `checkout.html`, global 04 | Datos, envío y checkout. | Preparado el 27 de octubre, aprobado el 31 e integrado. HTML ausente hoy. |
| `order-tracking.html`, global 04/05 | Pedido recibido y seguimiento; recuperación cambia a cédula con envío al correo registrado. | Aprobado e integrado; cambió con global 05. HTML ausente hoy. |
| `admin-media.html`, global 04 | Biblioteca de fotografías y selección/vinculación. | Aprobado e integrado. La aplicación vincula desde el detalle de una foto. HTML ausente hoy. |
| `admin-orders.html`, global 04/05 | Gestión, comprobantes, pagos y transiciones; retirada de la pestaña de recuperación administrativa. | Aprobado e integrado. HTML ausente hoy. |
| `admin-settings.html`, global 04/05 | Primera pestaña de catálogo rechazada por mezclar conceptos; rehecha separando categoría/casa, género, acordes, uso, perfil y presentaciones. | Global 05 aprobada el 31 de octubre e integrada. HTML ausente hoy. |
| Tienda unificada, global 06 | Unió catálogo negro, checkout, seguimiento y administración; carrito único como diálogo, cantidades y presentación por tarjeta. | Aprobado e implementado el 31 de octubre; prototipo, capturas y pruebas temporales retirados por instrucción del propietario. |

La documentación antigua conserva huellas y referencias a archivos que ya no están en la carpeta
actual. Esas referencias acreditan decisiones históricas; no garantizan disponibilidad del
artefacto ni autorizan reconstruirlo, restaurarlo desde Git o declarar reproducible su huella.

### 7.2. Propuestas del 2 de noviembre que sí se conservan

| Archivo presente | Propuesta y cambios | Decisión del propietario / relación con el producto |
|---|---|---|
| `home-1-luces-apagadas.html` | Showroom oscuro, foco que sigue el cursor e interruptor de luces. | Conservado como alternativa; no elegido como portada vigente. No consta aprobación para implementarlo. |
| `home-2-cilindro.html` | Carrusel 3D de frascos, nombre grande de fondo y color ambiente de la foto. Revisión 2.1 añade la cinta de marcas tomada de Bento. | Elegido para perfumes completos, aprobado e implementado el 2 de noviembre. |
| `home-3-bento-vivo.html` | Mosaico claro, inclinación 3D, contadores y filtro por familia. | No elegido como página completa; se conserva la cinta de marcas para el Cilindro. |
| `decants-a-cata-en-cartas.html` | Cartas para probar/pasar y bandeja «Tu cata» con tamaños y total. | Descartado; conservar como antecedente, no reimplementarlo como opción elegida. |
| `decants-b-estuche-de-cata.html` | Catálogo y estuche ilustrativo de cuatro huecos con frasquitos que se llenan. | Descartado como página; sus tarjetas se trasladan al diseño del carrito. Cuatro huecos no es una regla comercial aprobada. |
| `decants-c-frasco-vivo.html` | Frasco con líquido animado y nivel por ml; se añadió lista derecha, búsqueda/filtros, datos/precio a izquierda, botones/marcas/arrastre y carrito lateral por línea. | Elegido, aprobado e implementado el 2 de noviembre. |

Evolución concreta de C y del Cilindro al software principal:

- C conserva filtros reales adicionales en «Más filtros»; la lista se actualiza sin recargar.
- Carrito por línea con frasquito, cantidad, ml editables, precio y total según cotización backend.
- Se retiró el avance automático y el selector experimental a/b de C.
- Tras agregar se implementó por defecto a) resumen en página con cantidad y total. Sigue pendiente
  que el propietario elija b) solo contador; no inferir su decisión.
- El Cilindro real es manual: flechas, teclado, miniaturas y arrastre. La cinta sí se mueve y
  respeta reducción de movimiento, resaltando la casa del frasco activo.
- Filtros del Cilindro bajo las miniaturas, conservando paginación del backend.
- Se retiró la cuadrícula/héroe anterior del catálogo y la portada pasó al estudio de decants.

Otras propuestas de degradado que desplazaban el catálogo fueron rechazadas; sus archivos se
eliminaron según el registro del propietario. No forman parte de las alternativas actuales.

### 7.3. Menú principal del 3 de noviembre

Archivo: `design/prototypes/home-menu-principal.html`.

Cambios y decisiones:

- Carrusel de seis mensajes y promociones destacadas, con pausa visible, indicadores, flechas,
  teclado y respeto a reducción de movimiento.
- Accesos rápidos a decants y completos y cinta diagonal sutil de marcas, sin tapar contenido.
- Botón central inferior «Menú» con navegación de tienda, preferencias y administración.
- Las demás páginas se presentan como capturas del software, no como rediseños nuevos aprobados.
- Mensajes con datos reales de la semilla; la diapositiva de promoción es un ejemplo de diseño,
  sin inventar una oferta comercial.
- Selector iPhone, Android, tablet, laptop, escritorio y TV; navegación con flechas.

**Aprobado visualmente el 3 de noviembre. Navegación inferior integrada el 7 de noviembre.** La
portada con mensajes sigue pendiente. Antes de implementar ese frontend hacen
falta tabla, casos de uso, repositorios, endpoints, validaciones, permisos y pruebas para mensajes
destacados con texto ES/EN, foto, enlace, orden, vigencia y activo, además de gestión en el panel.

La integración sigue la ubicación del prototipo aprobado: menú inferior central y carrito en
cabecera/panel. Se conserva también el acceso desde el resumen tras agregar.

## 8. Historial de la eliminación del fondo

**Decisión posterior, 7 de noviembre de 2026: propuesta descartada por el propietario.** Los
estados de revisión de los apartados siguientes describen la preparación del 4 de noviembre,
no un pendiente actual. Se conservan las fotografías originales y su presentación en el producto.

### 8.1. Requisito expreso del propietario

- Eliminar únicamente lo que no pertenece al perfume, mostrando **solo el frasco**, sin caja.
- Conservar forma, tapón, etiquetas, relieves, vidrio, líquido, colores, brillos y reflejos blancos
  del propio objeto. No confundir blanco con fondo.
- No sustituir el fondo por otra silueta, óvalo, plinto, sombra o marco.
- Retirar restos y reflejos del suelo que no pertenecen al frasco.
- Retirar el fondo visible dentro de huecos reales, como el asa de Odyssey Mandarin Sky.
- Mostrar todos los perfumes para revisión y después presentarlos dentro de completos y decants.
- El propietario confirmó expresamente «Mostrar únicamente el frasco» al preguntarle por las cajas.

### 8.2. Intentos rechazados

| Versión / fecha | Qué se intentó o mostró | Problema y decisión |
|---|---|---|
| Tres propuestas sin óvalo, 3 nov. | Silueta de frasco en color representativo, sin silueta y foco con plinto. | Ninguna aprobada; archivos eliminados. No son el diseño vigente. |
| Recortes 01, 4 nov. | Segmentación para quitar el fondo. | Rechazada: hacía transparente vidrio e interior del frasco y dañaba su integridad. |
| Recortes 02, 4 nov. | Ajuste del recorte anterior. | Rechazada: seguía recortando bordes y partes de la base. |
| Recortes 03, 4 nov. | Delimitación conservadora del perfume y caja; se preservaba lo encerrado y se descontaba el fondo exterior. | Rechazada: conservaba caja, sombras/reflejos del suelo y restos exteriores. La fidelidad sobre fondo original no resolvía esos defectos. |

Ejemplos aportados por el propietario:

- **Khamrah Waha:** conservar el tapón blanco, el vidrio claro y sus reflejos; eliminar restos del
  suelo bajo el frasco.
- **Valentino Uomo Born in Roma Intense:** conservar los cristales y la base, eliminando el reflejo
  exterior inferior sin abrir huecos dentro del vidrio.
- **Odyssey Mandarin Sky:** conservar tapa y asa naranja; retirar el área blanca de fondo dentro
  del hueco del asa. Los brillos blancos del material no se borran por su color.

Las versiones anteriores no están conservadas como tres entregas separadas reproducibles. El
archivo `perfumes-sin-fondo.html` se actualizó posteriormente; hoy ya no representa el recorte
rechazado 03. No usar su nombre para atribuirle el contenido antiguo.

### 8.3. Recortes 04: galería completa del 4 de noviembre

Archivo vigente: `design/prototypes/perfumes-sin-fondo-catalogo.html`.

Cambios realizados:

1. Se revisaron las fotos originales de la semilla y los ejemplos del propietario.
2. Se sustituyó la presentación basada en derivados anteriores por **contornos SVG por fotografía
   aplicados sobre los bytes originales**, con huecos explícitos donde corresponde.
3. Se prepararon contornos para las 135 asociaciones de fotos, reutilizando geometrías donde
   correspondía. No se regeneraron etiquetas, textura, líquido ni partes de los frascos.
4. Se delimitó solo el frasco, separándolo de cajas y suelo.
5. Se incluyeron los 130 perfumes, las fotos alternativas y el aviso de Delina sin foto.
6. Se colocaron primero los tres casos señalados y se añadió un filtro específico para ellos.
7. Se añadió comparación original/recorte, ampliación a igual escala, foto completa y zoom.
8. Se añadieron fondos oscuro, claro y de cuadrícula, búsqueda, casa y estado de revisión.
9. Se añadieron marcas «Se ve bien» / «Necesita ajuste», notas y descarga JSON.
10. Se incorporaron controles de accesibilidad y adaptación por rango de ancho.
11. Se verificaron y corrigieron contornos observados en las hojas de revisión, incluidos detalles
    de tapones, hombros y bases. Un ajuste automático exploratorio de bordes produjo halos y fue
    retirado; no forma parte de la entrega.

Archivos creados o mantenidos para esta revisión:

- `design/assets/perfumes-contornos.js`: definiciones de contornos y alias de geometrías.
- `design/assets/perfumes-revision.js`: comparación, filtros, ampliación, marcas, notas y exportación.
- `design/assets/perfumes-revision.css`: tokens, presentación, controles y adaptación.
- `design/prototypes/perfumes-sin-fondo-catalogo.html`: entrega con datos, fotos y fuentes de la
  revisión integrados en el HTML; tipografías locales referenciadas desde el proyecto.
- `design/reviews/perfumes-frascos-{390,1440}.png`: capturas de revisión.
- `design/README.md` y `docs/DESIGN_APPROVALS.md`: acceso y estado de aprobación.

El HTML y las fuentes de `assets/` son artefactos separados: editar una fuente no actualiza por
sí solo la copia integrada en el HTML. Deben mantenerse sincronizados en próximas revisiones.
Los scripts de compilación, inspección y prueba usados temporalmente se limpiaron al terminar;
no quedó instalado un generador permanente ni una dependencia de segmentación.

Persistencia de revisión:

- Marcas y notas: `beront.prototype.photo-review.v4` en `localStorage`.
- Accesibilidad del revisor: `beront.prototype.photo-review.a11y`.
- Exportación: `beront-revision-frascos.json`.
- Estas observaciones viven en el navegador, no en PostgreSQL ni en la biblioteca comercial.
- Marcar una fotografía «Se ve bien» no autoriza automáticamente implementar la funcionalidad.

**Estado: pendiente de aprobación visual.** La fidelidad de píxeles no demuestra que todos los
contornos estén definitivamente aprobados. Las partes ya ausentes o cortadas en una fotografía
de origen no se inventaron ni reconstruyeron.

### 8.4. Misma revisión dentro de completos y decants

Después de recibir la galería, el propietario pidió ver cómo se verían las fotos en las dos
páginas de producto. Se actualizó `design/prototypes/perfumes-sin-fondo.html`.

| Antes | Última entrega |
|---|---|
| Selección de 24 perfumes completos y 18 decants. | 24 perfumes completos y los 119 decants de la semilla. |
| Recortes anteriores incrustados en el prototipo de recorridos. | Misma fotografía y mismo contorno de la revisión 04; sin caja ni reflejo exterior del suelo. |
| Comparación interna de una selección. | Enlace a la galería completa y enlaces de regreso a cada vista. |
| Elección por miniaturas/lista. | Selector de nombre en completos y búsqueda por perfume/casa en decants. |

Cambios de esta presentación:

- `#/bottles`: frasco principal del carrusel, posiciones laterales y miniaturas con los recortes;
  selector entre 24 perfumes y navegación manual.
- `#/decants`: foto principal y tarjetas de lista con los recortes; 119 perfumes, búsqueda, filtros
  por familia, tamaños y precios de la semilla.
- Para decants se usa la fotografía alternativa cuando la fuente dispone de ella, con su
  contorno correspondiente. Se comprobaron las dos fotos de los casos señalados.
- Delina sigue con aviso de foto ausente; no se crea un frasco ficticio para completar la lista.
- Conmutador «Sin fondo» / «Presentación actual» para comparar dentro del diseño.
- Selector de pantalla propia, iPhone, Android, tablet, laptop, escritorio y TV.
- Fuentes de Google sustituidas por los archivos locales del proyecto.
- Navegación por fragmentos de URL, incluido `hashchange`, sin exigir recargar la página.
- Ajustes de cabecera y lista para anchos medianos/compactos, logo centrado y controles accesibles.
- Foco conservado al cambiar texto en el panel de accesibilidad y devuelto al control al cerrar;
  flechas para navegar por la lista de decants y el carrusel.
- La galería recibió enlaces «Perfumes completos» y «Decants».
- Capturas: `design/reviews/recortes-{bottles,decants}-{390,1440}.png`.

Estas páginas son una **simulación visual de diseño** con datos de semilla. Su acción «Agregar»
es la del prototipo; no demuestra disponibilidad ni crea un pedido comercial. No sustituyen a
`DecantStudio.astro` o `CylinderPage.astro`, ni incorporan todos los comportamientos del software
principal. No asumir equivalencia funcional de sus filtros, carrito o configuración.

**Estado: preparado para revisión y pendiente de aprobación.** Mostrarlo dentro de ambas vistas
fue autorizado; trasladarlo al producto comercial aún no está aprobado.

## 9. Verificaciones de los últimos prototipos

### 9.1. Ejecutadas durante la preparación de recortes

- Galería: 130 tarjetas, una sin fotografía y 135 referencias fotográficas.
- Verificación de que las 135 referencias contienen los bytes de los archivos de la semilla.
- Muestreo de **505 218 píxeles opacos renderizados**, con diferencia RGB máxima **cero** frente
  al original en los puntos muestreados. No representa una comparación de todos los píxeles.
- Puntos de control: hueco de Mandarin fuera del recorte y etiqueta dentro; tapón blanco y base
  de Waha dentro y suelo fuera; cristales/base de Valentino dentro y suelo fuera.
- Apertura de la galería directamente como archivo local comprobada.
- Chromium, Firefox y WebKit; anchos 320, 360, 390, 412, 600, 768, 820, 840, 1024, 1280, 1440,
  1600 y 1920 px; sin desbordamiento horizontal en los escenarios comprobados.
- Filtros, estados vacíos, ampliación, cambios de fotografía, notas/marcas y accesibilidad.
- Vistas de completos y decants en los tres motores y los mismos 13 anchos, también con texto muy
  grande, modos de imagen, selector de completos, buscador de decants y Delina sin foto.
- Comprobación de los índices de foto de Waha, Valentino y Mandarin en ambas vistas, para asegurar
  que usan los recortes correspondientes de la galería.
- Sintaxis JavaScript comprobada con `node --check` después de las modificaciones finales.

### 9.2. Límites e intentos no completados

- No son pruebas en dispositivos Android, iPhone o televisores físicos; son comprobaciones de
  navegador y tamaños de viewport.
- No se ejecutó una nueva suite integral del software comercial por cambiar estos HTML.
- Un intento de abrir Google Chrome mediante control de la aplicación fue rechazado por permisos.
  Las comprobaciones automatizadas de navegador que sí se ejecutaron se registran por separado.
- La ejecución adicional final para renovar capturas y añadir comprobaciones puntuales de
  enlaces/foco/flechas fue rechazada por el usuario en la aprobación de la herramienta. **No se
  ejecutó.** Las pruebas de ambas vistas y las capturas existentes ya habían terminado antes.
- Las capturas conservadas proceden de esos recorridos anteriores. Pueden mostrar selección,
  tamaño de texto o desplazamiento resultante de las pruebas; no presentarlas como una renovación
  adicional ni como un estado inicial uniforme de todas las vistas.
- Los scripts exploratorios y sus datos temporales se eliminaron. Las capturas entregadas y los
  archivos de diseño se conservaron.

La consolidación de memoria solo comprobó archivos, documentación, conteos y procesos locales.
No debe atribuirse a ella una nueva ejecución de las pruebas anteriores.

## 10. Estado operativo actual y ejecución local

Puertos relevantes observados al crear esta memoria:

| Puerto | Uso previsto | Observación actual |
|---|---|---|
| 5432 | PostgreSQL local | Proceso escuchando. Esto no verifica datos ni revisión Alembic de la base comercial. |
| 5000 | API Flask | Sin proceso escuchando observado. |
| 4321 | Frontend Astro | Sin proceso escuchando observado. |
| 4367 | Servidor estático de prototipos | Sin proceso escuchando observado. |

En intervenciones anteriores el servidor de prototipos se levantó en 4367, se verificó HTTP 200
y se entregaron enlaces locales. Durante pruebas se detuvo un servidor temporal propio; después
el propietario pidió ejecutar el prototipo y se dejó otro servidor para su revisión. **Esa
ejecución no sigue activa en el inventario actual.** No se reinició al redactar esta memoria.

Ubicaciones vigentes del prototipo:

- Galería: `design/prototypes/perfumes-sin-fondo-catalogo.html`.
- Completos: `design/prototypes/perfumes-sin-fondo.html#/bottles`.
- Decants: `design/prototypes/perfumes-sin-fondo.html#/decants`.
- Inicio conservado en el prototipo de recorridos: `#/home`.

Si se solicita ejecutarlo por HTTP, desde la raíz y con el puerto libre:

```sh
python3 -m http.server 4367 --bind 127.0.0.1
```

En ese caso las URL son:

```text
http://127.0.0.1:4367/design/prototypes/perfumes-sin-fondo-catalogo.html
http://127.0.0.1:4367/design/prototypes/perfumes-sin-fondo.html#/bottles
http://127.0.0.1:4367/design/prototypes/perfumes-sin-fondo.html#/decants
```

Para la aplicación principal, consultar `docs/LOCAL.md`: desde `backend/`, `uv run beront run`;
desde `frontend/`, `bun run dev`. Antes de arrancar comprobar procesos existentes y respetar los
servidores del propietario. No ejecutar creación de administrador, importación, migración o
cambios de datos solo porque un documento antiguo los enumere como pendientes.

## 11. Discrepancias históricas que no deben convertirse en trabajo duplicado

| Registro anterior | Información más reciente o comprobación | Cómo interpretarlo |
|---|---|---|
| Resumen original de arquitectura sin pedidos ni pagos. | Ampliaciones del 27 y 31 de octubre autorizan pedidos persistentes y revisión manual. | Aplicar las decisiones fechadas posteriores; no retirar pedidos por leer solo el resumen inicial. |
| Recuperación de código atendida por administrador en texto histórico de implementación. | Decisión del 31 de octubre: recuperación por correo, respuesta uniforme y tiempo de espera. | El flujo administrativo anterior quedó sustituido. |
| Editor de acordes/usos/perfiles pendiente en apartados anteriores. | Auditoría del 2 de noviembre, `admin/options.ts` y controles actuales muestran incorporación por orden del propietario. | No volver a construirlos como si no existieran; un diseño posterior puede reemplazarlos. |
| Cadenas antiguas de ocho migraciones y carpetas SQL versionadas. | Tres migraciones actuales y SQL vigente en `backend/bd/`. | No restaurar migraciones o carpetas antiguas ni editar revisiones aplicadas. |
| `LOCAL.md` del 1 de noviembre menciona cabeza `0e7393567f81`. | Código y auditoría del 2 de noviembre incluyen las dos correctivas, hasta `49ce23c2f0c8`. | Distinguir fecha de documento, cabeza del código y revisión aplicada real. |
| README/auditoría del 2 de noviembre dicen base migrada y vacía, administrador/semilla pendientes. | Otro apartado de diseño del mismo día describe todo agotado por falta de existencias. Hoy no se consultaron datos comerciales. | Importación, administrador y existencias actuales por confirmar; no decidirlos desde estas frases. |
| Rol de ejecución restringido en la implementación histórica. | Auditoría posterior documenta privilegios elevados autorizados para el desarrollo local. | No afirmar aislamiento efectivo actual; verificar configuración sin revelar secretos cuando corresponda. |
| H02 del informe del 26 de octubre: desactivar la última presentación activa. | Código actual de `update_variant` llama a `ensure_publishable` sobre variantes actualizadas; la política rechaza un perfume publicado sin presentación activa. | El código refleja una corrección posterior. No se volvió a ejecutar su regresión en esta tarea documental. |
| Prototipos globales 01–05 «conservados» según referencias antiguas. | Actualmente solo están los nueve HTML inventariados al final. | Marcar ausencias históricas; no prometer acceso o reproducción de archivos inexistentes. |
| `perfumes-sin-fondo.html` descrito como versión anterior rechazada. | El archivo se actualizó con recortes 04 y 24/119 productos. | Es ahora el prototipo vigente de las dos vistas; el historial de rechazo corresponde a contenidos anteriores. |
| «Prototipo final» o verificación técnica. | Recortes 04 y sus vistas aún no tienen aprobación visual expresa. | Mantener estado pendiente y no implementar por inferencia. |

## 12. Pendientes y siguiente paso autorizado

### 12.1. Revisión visual de los frascos

Flujo retirado el 7 de noviembre por descarte expreso del propietario. La secuencia siguiente
se conserva únicamente como antecedente del trabajo planteado el 4 de noviembre.

1. El propietario revisa los recortes en la galería y dentro de completos/decants.
2. Recoger observaciones por perfume/foto y corregir contornos sin alterar el contenido original.
3. Revisar especialmente bordes, tapones blancos, bases de vidrio, huecos de asas y ausencia de
   cajas/suelo. Mantener las fotos alternativas y el aviso de ausencia.
4. Registrar únicamente las aprobaciones expresas que realmente se reciban, con revisión y fecha.
5. Tras aprobación, definir el contrato de derivados y completar primero el backend de imágenes.
6. Integrar después las vistas reales y verificar con datos y servidores temporales cuando corresponda.

La aprobación del menú principal no aprueba los recortes, y aprobar un recorte no decide la
ubicación del carrito ni completa el backend de mensajes destacados.

### 12.2. Otros pendientes conocidos

- Backend y administración de mensajes destacados; después implementar la portada aprobada.
  El menú inferior ya se integra independientemente con las capacidades existentes.
- Decisión del propietario sobre resumen tras agregar: a) resumen en página o b) solo contador.
- El menú ocupa el centro inferior; el carrito conserva accesos de cabecera, panel y resumen.
- Confirmar estado real de la base comercial antes de proponer inicialización o importación.
- Fotografía original de Delina Eau de Parfum.
- Datos reales de contacto, bancos, destinos/tarifas y términos definitivos por el propietario.
- Configuración y prueba SMTP real cuando se solicite; no enviar mensajes sin autorización.
- Revisión de accesibilidad pendiente de otras vistas antiguas, según matriz visual, sin asumir
  que las pruebas de recortes cubren toda la administración o el checkout.
- Reevaluar avisos de dependencias con una auditoría nueva cuando corresponda; conservar locks.
- No declarar despliegue, cobertura total, pruebas físicas o ausencia absoluta de vulnerabilidades.

## 13. Estado de Git y alcance de los cambios recientes

HEAD observado: `f4042890ae7d5eeaed9633443d75be0af5427ffd`, «Versión inicial de BÉRONT»,
fechado el 31 de octubre de 2026. Es el único commit mostrado por la consulta de historial corta.

Antes de crear esta memoria, `git status --short -uall` enumeró 436 entradas: 56 modificadas,
267 eliminadas y 113 sin seguimiento. El conteo es una instantánea, no una lista de cambios
realizados por esta tarea. Incluye migraciones antiguas retiradas, traslado de SQL, contenido
temporal eliminado y componentes/pruebas nuevos de la aplicación.

Familias de cambios presentes respecto de HEAD:

- Consolidación de migraciones y traslado de funciones a `backend/bd/`.
- CLI, importador, cotización del carrito y contratos/filtros de inventario.
- Correcciones de SQL, clasificación y pruebas.
- Editor/configuración, estudio de decants, Cilindro, filtros compartidos y accesibilidad.
- Retirada de catálogo temporal, cuadrícula/héroe y pruebas temporales.
- Documentación de arquitectura, operación, implementación, auditoría y decisiones visuales.

La regla `/design/` en `.gitignore` fue comprobada: los prototipos y capturas son archivos locales
ignorados por Git. Las huellas del apartado siguiente permiten identificarlos, pero **no hacen
que sus contenidos estén guardados en el historial de Git**. No cambiar esa regla ni agregar
archivos a Git por inferencia de esta memoria.

Las tareas de recortes modificaron únicamente los artefactos de diseño y su documentación.
Esta tarea de memoria crea el registro y enlaza su ubicación desde README y arquitectura.
No hizo commit, push, merge, ramas, restauraciones, migraciones, importación, pruebas de negocio
ni cambios de datos comerciales.

## 14. Mantenimiento de esta memoria

- Añadir cada nueva intervención con fecha, objetivo, decisiones del propietario, archivos
  modificados, pruebas realmente ejecutadas, resultado y pendientes.
- Registrar cambios por prototipo, usando su familia de revisión para evitar confusiones de números.
- Conservar los rechazos y sus motivos; no sustituirlos por una narración de éxito posterior.
- Al actualizar «estado actual», conservar la fecha de los estados anteriores y su procedencia.
- Cambiar una aprobación solo ante una instrucción explícita del propietario.
- Verificar archivos y procesos de nuevo al retomar; los puertos y el contenido de la base no
  permanecen vigentes por estar anotados aquí.
- Actualizar enlaces y las huellas de los artefactos que cambien. Las huellas son de identificación,
  no firmas de aprobación ni garantía de que los contornos son definitivos.
- Mantener secretos fuera de esta memoria. Referenciar la configuración por nombre de archivo o
  variable, sin copiar sus valores.

Formato sugerido para una entrada futura:

```text
Fecha y familia/revisión:
Solicitud y decisiones expresas:
Estado anterior:
Cambios por archivo o componente:
Efecto en software principal / solo prototipo:
Verificaciones ejecutadas y resultado:
Verificaciones pendientes o rechazadas:
Aprobación recibida o pendiente:
Siguiente paso:
```

## 15. Inventario verificable de la entrega vigente

Inventario y huellas tomados el 4 de noviembre. Los archivos de recortes permanecen en disco
como antecedentes descartados desde el 7 de noviembre; su presencia no los hace vigentes.

Los archivos y huellas siguientes se leyeron al consolidar la memoria. Son el contenido presente
en disco, no las huellas históricas de aprobación guardadas en otros documentos.

### 15.1. Prototipos presentes

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| [design/prototypes/decants-a-cata-en-cartas.html](design/prototypes/decants-a-cata-en-cartas.html) | 158762 | `ec3da9409fa5b69beadc2e66004332615ba9bce3c1f302fdc4deb671f40e09f6` |
| [design/prototypes/decants-b-estuche-de-cata.html](design/prototypes/decants-b-estuche-de-cata.html) | 176069 | `c72adb3e315ce86c0b3db9b7bf30a6bb64fcff55f1626d0933c5a585c27d8a91` |
| [design/prototypes/decants-c-frasco-vivo.html](design/prototypes/decants-c-frasco-vivo.html) | 706724 | `eb035995777ae2a3b234b37eaa5f08e3b749ccaa33c9b7d16decefed0af9428c` |
| [design/prototypes/home-1-luces-apagadas.html](design/prototypes/home-1-luces-apagadas.html) | 326889 | `f4b39d38cfcfcdcc46028f7c14253fb42e2be2d679fdc90e06a55883bad14c4f` |
| [design/prototypes/home-2-cilindro.html](design/prototypes/home-2-cilindro.html) | 602674 | `0100fe99889bbe87c0e92396a87047ae96ec4d9d2db691f04d9274d7acb52605` |
| [design/prototypes/home-3-bento-vivo.html](design/prototypes/home-3-bento-vivo.html) | 361263 | `5d9b341f73b61eb614b82f70d40349e5fa11c8a807b551d5ca41beaefc8cd500` |
| [design/prototypes/home-menu-principal.html](design/prototypes/home-menu-principal.html) | 3119620 | `0eff31fc14fe212fbc6fc52c29f57c9ea20fd7f240b9d0888ff4d209d5812e9c` |
| [design/prototypes/perfumes-sin-fondo-catalogo.html](design/prototypes/perfumes-sin-fondo-catalogo.html) | 4425835 | `ce30c416e2d0fa663a2125421126843c80b2aaa94e2f410550455a07dad3c00a` |
| [design/prototypes/perfumes-sin-fondo.html](design/prototypes/perfumes-sin-fondo.html) | 4439504 | `ca63ebddc22031121ad5574e569debbf04f1bd29452f14545e56f69c3968f6bd` |

### 15.2. Fuentes de la revisión de recortes

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| [design/assets/perfumes-contornos.js](design/assets/perfumes-contornos.js) | 24454 | `32c8af577aecb5c445956f76e7f969e933f972748ed2b6ac1ecc9ceb425497db` |
| [design/assets/perfumes-revision.css](design/assets/perfumes-revision.css) | 8733 | `3f89fd3bce3563092d3fc8ef65e3d18132f8e97eca4be62736d9b3f495ad2207` |
| [design/assets/perfumes-revision.js](design/assets/perfumes-revision.js) | 17031 | `39835b277040370c9f8a180892a6ff980ce34abdbe71d0adcf2a32cc8ed3fbb0` |

### 15.3. Capturas conservadas

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| [design/reviews/perfumes-frascos-1440.png](design/reviews/perfumes-frascos-1440.png) | 320777 | `f3adeb926329c0cbafbdd70c345bf4656966099754e879cc634a8bfd92bef200` |
| [design/reviews/perfumes-frascos-390.png](design/reviews/perfumes-frascos-390.png) | 296355 | `f163cbc9e0b64d108df29bca56a1ef2a196ba4351bb77b11e8ac8f13239e0d3c` |
| [design/reviews/recortes-bottles-1440.png](design/reviews/recortes-bottles-1440.png) | 638891 | `3d729a6e5fca62da8532216a8c932c1c4024679010713815e46a8a117611e2bd` |
| [design/reviews/recortes-bottles-390.png](design/reviews/recortes-bottles-390.png) | 245316 | `77b029b5ad01f3997e92b0cc1210a5627871a45afd86a01d8381980a5876336a` |
| [design/reviews/recortes-decants-1440.png](design/reviews/recortes-decants-1440.png) | 303909 | `a5c37fc2919028fe883eb4aa02a1831cd2c8c317b536e81ddd60555ddcfb2ba4` |
| [design/reviews/recortes-decants-390.png](design/reviews/recortes-decants-390.png) | 114575 | `8143c771b728845079330fa1f085d3fd215d893ad046e080977b0f32fd382dbe` |

### 15.4. Instantánea de archivos centrales del software y la semilla

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| [backend/pyproject.toml](backend/pyproject.toml) | 1069 | `402b64de0741735946e6830748f352d52095b071a7bf7f89470851e3c57191f4` |
| [backend/uv.lock](backend/uv.lock) | 263966 | `c729a2bd385894b61839630fa01acf232e992cc1870ba84de4fea76dc81ab527` |
| [frontend/package.json](frontend/package.json) | 1144 | `6a891a7f8c37e576bff0771be26cf6b7e1eca912916a8da61a1441003cb96a20` |
| [frontend/bun.lock](frontend/bun.lock) | 119855 | `3e7e3a094eeb9ddebe221e7b5ad01b26196e6f3a7c2b84b3316faea7f360d55e` |
| [backend/semillas/catalogo/catalogo.json](backend/semillas/catalogo/catalogo.json) | 215167 | `b5b9f41cf053b43297fd03b16ad9a7bd79342e0066a10ae74148aaec44e9a072` |
| [backend/semillas/importar_catalogo.py](backend/semillas/importar_catalogo.py) | 5534 | `a7dffe1a1d54679dac30bf0d133d454d48120b6879f48a4d8b6c2ae2da5177be` |
| [backend/src/beront/cli.py](backend/src/beront/cli.py) | 2974 | `a43a1f2cdc7fafd655ce650e70132c89a38d463a7e1f1b782743928acdf85dd5` |
| [backend/src/beront/shared/infrastructure/pg_call.py](backend/src/beront/shared/infrastructure/pg_call.py) | 6753 | `ef119e55dda3b43a4cd0e2bfccb11f995111fba492ccd15e8797ba11adcdb6e9` |
| [backend/src/beront/modules/catalog/infrastructure/images.py](backend/src/beront/modules/catalog/infrastructure/images.py) | 2822 | `f0b1c7ce0b1f8f12d9a2b0ff824c9c31058c83374a0bae687490834e8c4eeec9` |
| [backend/src/beront/modules/cart/application/build_quote.py](backend/src/beront/modules/cart/application/build_quote.py) | 1625 | `2d1db5cb1508f4ac84514e6adeaa809841238fa2120a7f99a8d4cb4e935b697b` |
| [backend/migrations/versions/0e7393567f81_initial_schema.py](backend/migrations/versions/0e7393567f81_initial_schema.py) | 33710 | `5f59cf927a8b2375ed0077b8f870e3a726bf779f2802fcb590641f31cb917214` |
| [backend/migrations/versions/87313231bdf2_inventory_labels_and_filters.py](backend/migrations/versions/87313231bdf2_inventory_labels_and_filters.py) | 712 | `5bff4f8c05420e8843d492951719d894353dc3f780f3b81165765a198404a594` |
| [backend/migrations/versions/49ce23c2f0c8_keep_inactive_classification_links.py](backend/migrations/versions/49ce23c2f0c8_keep_inactive_classification_links.py) | 626 | `798c0961e764d00a64314bae8ec1153dba094f178a384a70bb75fdb3e13d8397` |
| [frontend/src/pages/[locale]/index.astro](frontend/src/pages/[locale]/index.astro) | 249 | `dda9b29d04ff718ea27c5853091a3fb598418258c417426481ce54919b4bb0c4` |
| [frontend/src/features/catalog/DecantStudio.astro](frontend/src/features/catalog/DecantStudio.astro) | 10518 | `5b1278051ead63fee19fc90cd4a5d209ef147a718c3e3fcbd5e045a67a7f2360` |
| [frontend/src/features/catalog/CylinderPage.astro](frontend/src/features/catalog/CylinderPage.astro) | 7001 | `d213d8fc2ea56605679b6e76acb6d69e5923df2ec473b8db172fe428f6e24db8` |
| [frontend/src/features/catalog/StudioFilters.astro](frontend/src/features/catalog/StudioFilters.astro) | 5769 | `db34dbe15b45a1a8dc69e51811d9000bfefe06de073d75bfde69fc722da5d653` |
| [frontend/src/features/cart/store.ts](frontend/src/features/cart/store.ts) | 3405 | `9f7274b5a5aab8aa547379fb2edfdf84291702ef5c0460aae3e3911da4853c5c` |
| [frontend/src/shared/components/AccessibilityPanel.astro](frontend/src/shared/components/AccessibilityPanel.astro) | 1466 | `00ed83c5f2bbb7d840cf5b2103e131b1f13db360b3c17b8e30bbf97a32f9bce7` |

## 16. Intervención del 7 de noviembre de 2026

- Solicitud: descartar imágenes sin fondo y atender la ausencia del menú inferior aprobado.
- Decisión: recortes 04, galería y vistas en completos/decants descartados; se conservan como
  antecedentes y dejan de estar pendientes de aprobación. Fotos originales y producto intactos.
- Navegación: nuevos `shared/components/MainMenu.astro` y `main-menu.ts`, usados por ambos layouts.
  Reutilizan sesión, permisos, rutas, carrito, accesibilidad y ES/EN. Los iconos proceden del
  prototipo aprobado y se centralizan en `Icon.astro`. Cierre de sesión reutilizable desde el panel.
- El menú ocupa el centro inferior como en el prototipo; carrito disponible en cabecera/panel y
  resumen. Se retiran el botón flotante del carrito y sus estilos/eventos sin uso.
- La portada con mensajes sigue pendiente del backend; no se añaden tablas, migraciones,
  endpoints, módulos ni dependencias. No se cambian datos de negocio ni fotografías.
- Verificaciones: `astro check` sin diagnósticos, ESLint, Prettier, compilación, 27 pruebas unitarias
  aprobadas y 45 de navegador aprobadas en Chromium, Firefox y WebKit. La primera ejecución dio
  44 aprobadas y un fallo de foco en Chromium; tras corregirlo, la ejecución completa dio 45/45.
- `application-menu.spec.ts` comprueba 14 anchos de 320 a 1920 px y seis anchos con texto muy grande
  y 500 px de alto; teclado/flechas, foco, idioma, carrito, permisos, cierre y fallo de sesión.
  PostgreSQL, API y frontend de pruebas fueron temporales y se cerraron al finalizar.
- Se abrió el menú implementado en Chrome contra `http://localhost:4322/es/`. La API local se
  mantiene en 5000; el puerto 4321 pertenecía a otro proyecto y no se intervino.
- Documentación: arquitectura, aprobaciones, implementación, índice de diseño y esta memoria.
  Sin Git de escritura, despliegue, pruebas en dispositivos físicos ni lectores de pantalla.

## 17. Ensayo nuevo con Inkscape y MCP, 7 de noviembre de 2026

- Nueva solicitud: descartar las ediciones previas, instalar Inkscape y usar realmente sus
  herramientas mediante MCP, con dos originales aleatorios y prototipo en su contexto final.
- Instalado Inkscape 1.4.4 arm64 en `/Applications/Inkscape.app`, firma y notarización verificadas.
  MCP `jjjsood/inkscape-mcp-server` 0.1.0 aislado en uv, registrado como `beront_inkscape`.
  Lanzador persistente `~/.local/share/beront-inkscape/launch.py`; raíces de trabajo temporales
  y `design/assets/`. No se alteran locks ni dependencias del proyecto.
- Se usa el motor CLI de Inkscape mediante protocolo MCP STDIO real; no hay conexión en vivo
  de la ventana de macOS. Esta limitación se explicó. La ventana abrió el SVG de B correctamente.
- Elegidos Dior Sauvage Eau de Toilette (un frasco) y Lattafa Fakhar Black (frasco y caja).
  No se usan contornos anteriores. Los WebP originales permanecen intactos; las importaciones
  PNG realizadas con sips tienen los mismos píxeles RGB. El binario de Inkscape aplica el clip
  nativo y exporta ambos PNG y SVG mediante MCP.
- Entregas: `design/assets/inkscape-{a-sauvage,b-fakhar}-r01.{png,svg}` y
  `design/prototypes/inkscape-pilot-r01.html`. A tiene 147 × 348 px útiles; B, 451 × 449.
  Flujo completo: `design/INKSCAPE_WORKFLOW.md`; evidencia y verificaciones en `design/reviews/`.
- Carrusel con originales de los 24 completos; solo A/B reciben PNG. Comparación, cuatro fondos,
  zoom, seis tamaños y accesibilidad. 180 combinaciones verificadas en Chromium/Firefox/WebKit,
  15 anchos de 320 a 1920, dos casos y texto normal/muy grande, más controles. Capturas revisadas.
- R01 pendiente del propietario por recorte y presentación. No se da por perfecta ni se integra
  al producto. Las ediciones anteriores continúan descartadas; no se borran originales.

## 18. Inkscape R02, catálogo completo y solo frascos

- El propietario solicita eliminar las cajas y aplicar el flujo a todos los perfumes. Autoriza
  extender el trabajo; los resultados del catálogo siguen en diseño para revisión visual.
- Inventario: 130 perfumes, 135 vínculos de foto y 132 originales distintos. Delina carece de foto.
- 132 PNG RGBA y 132 SVG editables en `design/assets/inkscape-r02-NNN.{png,svg}`. Manifiesto
  `inkscape-catalog-r02-manifest.json`; trazados nuevos `inkscape-contours-r02.json`. Sauvage
  conserva el contorno del ensayo Inkscape R01; no se usan los contornos previos descartados.
- MCP STDIO real con el lanzador registrado `beront_inkscape`, motor Inkscape 1.4.4. Cada fuente
  pasa por creación de trazado, `object-set-clip`, exportación y validación del documento.
  Se corrigen halos y bases detectados al inspeccionar el lote. Registro en
  `design/reviews/inkscape-r02-mcp-session.jsonl`; el intento inválido de normalización de Sauvage
  queda resuelto. No se afirma control en vivo de la ventana del editor.
- Verificados los hashes de los 132 originales; los SVG conservan todos los píxeles RGB de sus
  fuentes. Ambos ZIP de 132 archivos tienen contenido idéntico a las exportaciones nativas.
- Prototipo vigente `design/prototypes/inkscape-catalog-r02.html`: galería de 130 perfumes,
  alternativas, filtros, notas, revisión por foto y exportación JSON; comparación alineada y
  ampliable sobre cuatro fondos; completos y decants con los PNG, miniaturas y seis tamaños.
- Comprobaciones en Chromium/Firefox/WebKit: 180 combinaciones de vistas/anchos/texto,
  858 comprobaciones de productos a 390/1440 px, 132 PNG cargados por motor y controles funcionales.
  Corregido un desbordamiento de tarjetas de decants a 320 px con texto muy grande. La ejecución
  posterior completa no tuvo fallos. Resultados y verificación de archivos en `design/reviews/`.
- Las limitaciones de resolución y encuadre de los originales se muestran en la galería. Los
  estados locales de revisión no se consideran aprobación documental del propietario. No se
  reconstruye fotografía ausente, ni se altera producto, backend, locks o servidores del propietario.
- Entrega local: `http://127.0.0.1:4367/design/prototypes/inkscape-catalog-r02.html`.
  Descargas `design/assets/inkscape-catalog-r02-{png,svg}.zip`. Fases: `design/INKSCAPE_WORKFLOW.md`.

## 19. Cierre de revisión Inkscape R02, 8 de noviembre de 2026

- Reanudado el cierre: 132 fuentes y exportaciones, y contenido de ambos ZIP, verificados otra vez
  mediante hashes. Descargas PNG/SVG y exportación de revisión comprobadas en los tres motores.
- Corregida una superposición de imágenes sobre el texto de las tarjetas de la galería con una
  fila Grid acotada y `object-fit: contain`. Las 11 610 comprobaciones posteriores de contención,
  en 15 anchos y texto normal/muy grande, no detectan superposición. Capturas limpias de galería
  a 390 y 1440 px guardadas y revisadas. Resultados añadidos al informe de navegador R02.
- Prototipo R02 abierto en Chrome. Se preserva la navegación activa del propietario. El servidor
  de diseño sigue en 4367; sus servidores de aplicación permanecen intactos.
- Limpieza de scripts, importaciones y láminas temporales; se conservan los entregables y evidencias.
  Todo sigue en diseño para aprobación visual, con Delina sin foto original y límites de fuente señalados.

## 20. Integración R02 aprobada, 8 de noviembre de 2026

- El propietario solicita implementarlo y mostrar la aplicación funcionando. Queda aprobada R02;
  esta decisión sustituye la espera de aprobación de los apartados históricos anteriores.
- Backend completo y probado antes de tocar la presentación. El almacenamiento conserva alfa
  mediante WebP sin pérdida y píxeles RGBA exactos, sin cambiar el contrato `/media/`, permisos,
  esquema, SQL ni dependencias. Los PNG maestros y SVG de Inkscape permanecen en diseño.
- `beront importar-recortes --manifiesto ../design/assets/inkscape-catalog-r02-manifest.json`
  valida huellas de originales/PNG y reemplaza las asociaciones en una transacción, con auditoría,
  idempotencia y rechazo de vínculos cambiados. Adaptador en `catalog/infrastructure/approved_images.py`;
  caso de uso en `catalog/application/import_photos.py`. Sin consultas ORM ni SQL directo.
- Aplicados 132 recortes a 135 vínculos de 129 perfumes. Comparación antes/después: todos los RGBA
  coinciden con los PNG; 132 originales, productos, variantes, precios, 154 saldos, movimientos,
  posiciones y textos alternativos conservados. La validación posterior omite los 135 vínculos.
- Carrusel, estudio y fotografías compartidas del producto usan los medios nuevos. Se retiran
  fondos ovalados, filtros y mezcla de color; se elimina `photos.ts`. El muestreo ambiental del
  decant pondera alfa. Delina oculta su espacio vacío; no se inventa una fotografía.
- Verificados 152 tests de backend, Ruff, Astro sin diagnósticos, ESLint, Prettier, compilación,
  27 unitarios y 48 pruebas de aplicación en Chromium/Firefox/WebKit. Las pruebas de escritura
  utilizan PostgreSQL/API/frontend temporales, eliminados después. La prueba nueva cubre carga
  PNG con alfa por administración, preservación en las vistas y 15 anchos con texto normal/XL.
- Verificación adicional del catálogo real, solo lectura: 360 combinaciones de vista/ancho/texto,
  132 medios HTTP decodificados en cada motor y ausencia de foto de Delina. Una primera pasada
  alcanzó el límite de medios; se descargó cada recurso una vez y se reutilizaron sus bytes en los
  tres motores. No se alteraron los límites del servidor. Evidencias `design/reviews/implemented-r02-*`.
- Aplicación real abierta en Chrome en `http://localhost:4322/es/catalog/full-bottles`; el propietario
  navega también por decants. Se conserva su navegación activa. Backend 5000 y frontend 4322 no se
  reinician. La preservación de alfa en futuras subidas se cargará con el siguiente arranque normal
  del backend; el importador nuevo ya produjo y registró correctamente las imágenes actuales.
- El frontend de comprobación en 4323 se detiene al cerrar la tarea; no se toca 4321, otro proyecto.
  Sin pruebas en dispositivos físicos, lectores de pantalla o televisor real.

## 21. Distribución de decants, 8 de noviembre de 2026

- El propietario señala la captura del estudio y solicita selección de modelos a la izquierda,
  fotografía y decant animado a la derecha. Se toma como aprobación de ese ajuste concreto.
- Se actualiza el prototipo R02 antes del CSS del producto. Grid intercambia las áreas desde
  840 px conservando proporciones; por debajo mantiene el frasco arriba y la lista debajo.
- Pasan 180 comprobaciones de prototipo/aplicación: tres motores, 15 anchos, texto normal/XL;
  selección por teclado, filtros en vivo y mililitros verificados. Astro sin diagnósticos,
  ESLint, Prettier y compilación correctos. Evidencias `design/reviews/decants-left-selection-*`.
- No cambia backend, datos ni contratos. Frontend de comprobación en 4323 contra backend 5000,
  con solo lecturas; se detiene al terminar. Los procesos existentes 4322/5000 se conservan.

## 22. Home implementado, cierre del 9 de noviembre de 2026

- El propietario solicita implementar el Home aprobado, con imágenes sin fondo. Se adapta el
  prototipo a los PNG R02, conservando composición, carrusel, cinta, accesos y menú.
- Backend completo y probado antes del frontend. Se amplía `commerce` sin módulos o dependencias
  nuevos: modelos `FeaturedMessageModel`/`FeaturedMessageImageModel`, funciones `commerce_message_*`,
  validación de enlaces internos/fechas, ES/EN, activo, orden, versión, imágenes y auditoría.
  Endpoints públicos y protegidos documentados en `docs/ARCHITECTURE.md` y `docs/LOCAL.md`.
- Migración `de252c02c932` generada desde modelos, revisada y aplicada localmente. Reversión y
  reaplicación verificadas en una base temporal; Alembic no detecta diferencias con los modelos.
- `beront inicializar-home` instala seis mensajes de forma idempotente y conserva las ediciones.
  Bienvenida, decants, completos, envíos y pago activos; promoción de ejemplo desactivada.
- `HomePage.astro`, `home.ts` y `home.css` sirven el inicio en ES/EN. Pausa, flechas, indicadores,
  teclado, foco, suspensión por pestaña oculta/hover y reducción de movimiento. Marcas, cifras
  y muestras proceden del catálogo. Las nueve fotos principales coinciden con los PNG RGBA.
- La pestaña «Inicio y mensajes» del panel de Configuración gestiona texto, biblioteca, enlaces,
  orden, activo y vigencia. Las imágenes vinculadas no se eliminan de biblioteca; comprobantes
  rechazados como arte del Home. Las fechas locales se convierten a UTC.
- Verificados 157 tests de suite backend más uno de migración posterior, 27 unitarios frontend y
  57 pruebas de aplicación en tres motores. Ruff, Astro, ESLint, Prettier y compilación correctos.
  La primera pasada de navegador tuvo un fallo de preparación Firefox; fijado el tiempo de
  prueba también para la preparación, la repetición completa termina con 57 aprobadas.
- QA adicional del Home real: 900 combinaciones de ES/EN, 15 anchos, texto normal/XL y cinco
  mensajes en Chromium/Firefox/WebKit. Nueve fotos RGBA exactas; 130 perfumes, 400 variantes,
  154 saldos y cero movimientos. Evidencias `design/reviews/home-implemented-*`.
- El propietario autoriza explícitamente «Sí, reinicia solo el backend». Se reemplaza el proceso
  del backend 5000 para activar el código; el frontend 4322 mantiene su proceso. La preservación
  de alfa en futuras subidas también queda activa. Home abierto en Chrome en `http://localhost:4322/es/`.
- Bases y servidores de escritura temporales eliminados; frontend separado de lectura cerrado.
  No se modifican precios ni inventario. Sin pruebas en dispositivos físicos o lectores de pantalla.

## 23. Elección de catálogo en el Home, 9 de noviembre de 2026

- Por indicación del propietario, el bloque pregunta «¿Qué estás buscando hoy?» y muestra las
  dos opciones de compra: Decants y Perfumes completos. Fotografías R02 y cifras del backend.
  Pedidos y carrito mantienen sus accesos en la navegación existente.
- Prototipo actualizado primero, traducción EN y cuadrícula simplificada a dos columnas desde
  600 px; una en móvil. Corregido el ajuste de miniaturas del prototipo a 320 px y texto grande.
- Pasan 360 combinaciones de prototipo/aplicación en tres motores, ES/EN, 15 anchos y dos tamaños
  de texto, además de enlaces a ambos catálogos. Astro sin diagnósticos, ESLint y build correctos.
  Capturas y resultados `design/reviews/home-choice-*`.
- Bloque real abierto en Chrome en `http://localhost:4322/es/#home-shortcuts-title`. Backend y
  frontend del propietario conservados; frontend temporal 4323 cerrado. Sin cambios de datos.
- Ajuste posterior: pregunta centrada, tamaño fluido de 2,5 a 4 rem, peso 600 y líneas equilibradas.
  Prototipo y aplicación verificados en 360 combinaciones, con capturas a 390/1440 px y sin
  desbordamientos. Evidencias `design/reviews/home-choice-centered-*`.

## 24. Patrones de las opciones del Home, 9 de noviembre de 2026

- El propietario indica centrar los textos y sustituir las fotografías de las dos tarjetas por
  varios iconos champán según categoría. Se actualiza primero el prototipo vigente y se registra
  la indicación como aprobación de ese ajuste concreto.
- SVG propios: atomizadores para decants; torso, cilindro y frasco con picos para completos.
  Recursos revisados visualmente, sin marcas ni imágenes rasterizadas, con copias idénticas en
  `design/assets/` y `frontend/public/brand/`. El color usa el token champán existente.
- Integrado en `HomePage.astro` y `home.css`, con título, cifras y entrada centrados; fondo
  decorativo sin interacción. Se conserva la pregunta grande y el catálogo real, solicitando
  solo el primer resultado para obtener precio mínimo y total. Sin cambios de backend o datos.
- Pasan 360 comprobaciones del selector, 12 de alto contraste, foco y navegación en Chromium,
  Firefox y WebKit; Astro, ESLint, formato y build correctos. Se corrige la cabecera del simulador
  para reorganizar controles por debajo de 1200 px; la pasada final comprueba prototipo y
  aplicación sin desbordamientos. Capturas y resultados en `design/reviews/home-category-patterns-*`.
  Home real actualizado abierto en Chrome, con los servidores del propietario conservados.
  No se prueban dispositivos físicos.

## 25. Icono de decant según referencia, 9 de noviembre de 2026

- El propietario descarta el aspecto del icono anterior y aporta una fotografía del atomizador.
  Se redibuja en SVG con sus proporciones: pulsador descubierto, orificio, cuello ancho, vidrio
  alargado, resorte y tubo curvo. Conserva el champán y la repetición del fondo de la tarjeta.
- Revisión visual primero en `design/`; copia idéntica en `frontend/public/brand/` y aprobación
  de la sustitución registrada. Las comprobaciones del recurso y 120 combinaciones de
  prototipo/aplicación, tres motores, diez anchos y texto normal/125 % pasan. Enlace de decants
  y compilación correctos. Evidencias `design/reviews/home-decant-reference-*`.
- Sin cambios de código, backend o datos comerciales; servidores del propietario conservados.
  No se prueban dispositivos físicos.

## 26. Cuatro iconos de perfumes completos, 9 de noviembre de 2026

- El propietario aporta cuatro fotografías y solicita convertirlas en iconos para el fondo de
  «Perfumes completos». Se redibujan la tapa en punta con placa trapezoidal, el torso con franjas
  y atomizador descubierto, el frasco redondeado con picos y el trofeo con asas.
- SVG champán revisado ampliado y en el prototipo; sustituye el recurso del patrón existente.
  Aprobación de la sustitución registrada y copia idéntica en `frontend/public/brand/`.
- Pasan 240 combinaciones de prototipo/aplicación, ES/EN, tres motores, diez anchos entre
  320 y 1920 px y texto normal/125 %. Se verifican el XML SVG, las cuatro referencias internas,
  los enlaces de completos y la compilación. Evidencias `design/reviews/home-four-bottles-*`.
- Sin cambios de código, backend o datos comerciales; servidores del propietario conservados.
  No se prueban dispositivos físicos.
- Ajuste posterior indicado por el propietario: iconos más juntos. El patrón repite los cuatro
  motivos en cuatro columnas uniformes y dos filas, conservando escala y opacidad. La distancia
  horizontal media se reduce a la mitad. Prototipo revisado primero y copia pública idéntica.
  Pasan 72 comprobaciones en tres motores, seis anchos y texto normal/125 %, enlace y build.
  Evidencias `design/reviews/home-bottles-density-*`; servidor temporal de revisión retirado.


## Fotografía de Extradose sustituida, 11 de noviembre de 2026

El propietario pide reemplazarla por su referencia, solo la botella. Se recupera la misma
fuente pública abierta en Chrome, ya transparente, y el MCP de Inkscape elimina la caja
mediante recorte SVG; PNG de 402 × 710 px revisado antes de integrar. Se reemplaza una imagen
con ImportCatalogPhotos, conservando originales y campos comerciales. El WebP conserva RGBA
exacto del PNG y el contorno conserva el alfa original. Pasan seis comprobaciones de navegador
(Chromium, Firefox y WebKit a 390/1440 px). Evidencias en design/reviews/valentino-extradose-*.
Los servidores del propietario permanecen activos; el frontend temporal de revisión se retira.

## Fotografía de Azzaro EDP Intense sustituida, 11 de noviembre de 2026

Por petición del propietario se reemplaza la imagen de The Most Wanted Eau de Parfum Intense
por su referencia de Venba. Original conservado en diseño; recorte SVG y exportación PNG
realizados por el MCP de Inkscape (op_f6c216f5), 499 × 949 px y transparencia. Se sustituye
un vínculo mediante ImportCatalogPhotos y se conserva el archivo anterior. Precios y demás
campos del producto sin cambios, WebP con RGBA exacto del PNG. Pasan seis comprobaciones
en tres motores a 390/1440 px. Evidencias design/reviews/azzaro-most-wanted-intense-*.
Servidores del propietario conservados y frontend temporal de verificación cerrado.

## Fotografía de Azzaro Parfum sustituida, 11 de noviembre de 2026

Se sustituye la foto de The Most Wanted Parfum por la referencia ámbar enviada por el propietario.
Fuente idéntica recuperada de Las Fragancias, original de 4167 × 4167 conservado. Contorno
Bézier para excluir fondo y sombras, recorte nativo por MCP de Inkscape (op_8d211443) y PNG
RGBA de 1000 × 1793. Un vínculo sustituido con ImportCatalogPhotos; foto anterior conservada
y campos comerciales sin cambios. WebP con RGBA exacto del PNG. Pasan seis comprobaciones
de tres motores a 390/1440 px. Evidencias design/reviews/azzaro-most-wanted-parfum-*.
Servidores del propietario conservados; frontend temporal de revisión retirado.

## 11 de noviembre de 2026 — Foto de Valentino Purple Melancholia

Se reemplaza la fotografía de Uomo Born in Roma Purple Melancholia por la referencia aportada
por el propietario, recuperada de Fragrantica. El MCP de Inkscape recorta el frasco y exporta
un PNG transparente de 425 × 727 px; original y maestros en `design/assets/valentino-purple-melancholia-*`.
`ImportCatalogPhotos` sustituye un vínculo y conserva el archivo anterior en biblioteca. Los
campos comerciales permanecen iguales y el WebP conserva RGBA exacto. Pasan seis verificaciones
en Chromium/Firefox/WebKit a 390/1440 px. Evidencias en `design/reviews/valentino-purple-melancholia-*`.

## 11 de noviembre de 2026 — Foto de YSL Y Iced Cologne

Se sustituye una fotografía de Y Iced Cologne por la toma aportada por el propietario,
recuperada en mayor resolución de Fragrantica. El MCP de Inkscape recorta el frasco y exporta
un PNG transparente de 605 × 1200 px. Maestros en `design/assets/ysl-y-iced-cologne-*`.
Se conserva la foto anterior en biblioteca y los campos comerciales permanecen iguales.
El WebP conserva RGBA exacto. Pasan seis verificaciones en Chromium/Firefox/WebKit a
390/1440 px, con evidencias en `design/reviews/ysl-y-iced-cologne-*`.

## 11 de noviembre de 2026 — Foto de Argos Bacio Immortale

Se reemplaza la foto por la referencia del propietario recuperada de Sayhar. El MCP de
Inkscape recorta la botella con su base de cristal y elimina fondo y reflejo inferior; PNG
transparente de 585 × 1377 px. Maestros en `design/assets/argos-bacio-immortale-*`. Se sustituye
un único vínculo mediante `ImportCatalogPhotos`, conservando el original en biblioteca y
los campos comerciales. El WebP mantiene RGBA exacto. Pasan seis verificaciones en
Chromium/Firefox/WebKit a 390/1440 px; evidencias en `design/reviews/argos-bacio-immortale-*`.

## 11 de noviembre de 2026 — Cuatro fotografías Xerjoff

Se sustituyen Erba Pura, Naxos, Torino21 y Tony Iommi Monkey Special por recortes de solo
los frascos mediante el MCP y exportación nativa de Inkscape. El propietario proporciona
para Erba Pura el enlace de Falabella usado como fuente vigente. Su WebP se normaliza a
PNG para lectura con sips, verificando RGBA exacto; el recorte se hace en Inkscape. Los
maestros y originales están en `design/assets/xerjoff-*`. Se afina la tapa negra de Tony
Iommi tras revisar un borde claro. Las fotos anteriores permanecen en biblioteca y los
campos comerciales no cambian. Los WebP conservan RGBA exacto de los PNG finales. Pasan
24 comprobaciones finales en Chromium/Firefox/WebKit a 390/1440 px, repitiendo las seis
de Tony Iommi después del ajuste. Evidencias en `design/reviews/xerjoff-four-replacements.json`
y `xerjoff-*-app-*`. Se cierra únicamente el frontend temporal de revisión.

## 11 de noviembre de 2026 — Fotografía de Zoologist Nightingale

Se sustituye la foto por la referencia aportada, recuperada de The Perfume Apothecary.
Se comprueba la forma de la base con una foto oficial y se conserva todo el pie de cristal.
El MCP de Inkscape elimina el fondo floral y exporta el PNG transparente de 770 × 1456 px.
Maestros y original en `design/assets/zoologist-nightingale-*`. La foto anterior permanece
en biblioteca y los campos comerciales no cambian. El WebP conserva RGBA exacto. Pasan seis
comprobaciones en Chromium/Firefox/WebKit a 390/1440 px; evidencias en
`design/reviews/zoologist-nightingale-*`. Se cierra solo el frontend temporal de revisión.

## 11 de noviembre de 2026 — Fotografía de Zoologist Rabbit

Se reemplaza la foto por la referencia oficial aportada, recortada mediante el MCP de
Inkscape con base de cristal completa. Original de 2200 × 2200 y maestros PNG transparente
de 990 × 1830 y SVG en `design/assets/zoologist-rabbit-*`. Se conserva la foto anterior en
biblioteca y los campos comerciales no cambian. WebP con RGBA exacto del PNG. Pasan seis
verificaciones en Chromium/Firefox/WebKit a 390/1440 px, con evidencias en
`design/reviews/zoologist-rabbit-*`. Se cierra solo el frontend temporal de revisión.

## 11 de noviembre de 2026 — Foto de Summer Hammer

Se sustituye la foto de Lorenzo Pazzaglia Summer Hammer por la referencia aportada,
recuperada de Fragrantica. El MCP de Inkscape aplica el recorte vectorial y exporta PNG
transparente de 762 × 1402 y SVG nativo; maestros en `design/assets/lorenzo-summer-hammer-*`.
La foto anterior permanece en biblioteca y los campos comerciales no cambian. WebP con
RGBA exacto del PNG. Pasan seis verificaciones en Chromium/Firefox/WebKit a 390/1440 px;
evidencias en `design/reviews/lorenzo-summer-hammer-*`. Se cierra solo el frontend temporal.

## 11 de noviembre de 2026 — Foto de Speachless

Se reemplaza la foto de Lorenzo Pazzaglia Speachless por la referencia aportada, recuperada
de Fragrantica. El MCP de Inkscape aplica el recorte vectorial y exporta PNG transparente
de 342 × 626 y SVG nativo; maestros en `design/assets/lorenzo-speachless-*`. La foto anterior
permanece en biblioteca y los campos comerciales no cambian. WebP con RGBA exacto del PNG.
Pasan seis verificaciones en Chromium/Firefox/WebKit a 390/1440 px, con evidencias en
`design/reviews/lorenzo-speachless-*`. Se cierra únicamente el frontend temporal de revisión.

## 11 de noviembre de 2026 — Foto de Delina

Se reemplaza la foto de Delina por la nueva referencia oficial aportada. El MCP de Inkscape
excluye la sombra exterior conservando frasco, tapa, cordón y borlas; PNG transparente de
338 × 673 y SVG nativo en `design/assets/pdm-delina-*`, junto al original. Se conserva la
foto anterior en biblioteca y los campos comerciales no cambian. WebP con RGBA exacto.
Pasan seis verificaciones en Chromium/Firefox/WebKit a 390/1440 px; evidencias en
`design/reviews/pdm-delina-*`. Se cierra solo el frontend temporal de revisión.

## 11 de noviembre de 2026 — Foto de Megamare

Se sustituye la foto de Orto Parisi Megamare por la referencia aportada, recuperada de
My Perfume Shop. El MCP de Inkscape recorta frasco, tapa y base, excluyendo la sombra
exterior; PNG transparente de 338 × 765 y SVG nativo en `design/assets/orto-megamare-*`.
La foto anterior permanece en biblioteca y los campos comerciales no cambian. WebP con
RGBA exacto del PNG. Pasan seis verificaciones en Chromium/Firefox/WebKit a 390/1440 px,
con evidencias en `design/reviews/orto-megamare-*`. Se cierra solo el frontend temporal.

## 11 de noviembre de 2026 — Fotos Argos Neptune’s Trident y Triumph of Bacchus

Se reemplazan ambas fotos por las referencias aportadas, recuperadas de Argos y Essence
Garden. El MCP de Inkscape conserva frascos y pedestales físicos, excluyendo fondo y reflejos.
PNG de 1000 × 2368 y 520 × 1232, SVG y originales en `design/assets/argos-neptune-*` y
`design/assets/argos-triumph-of-bacchus-*`. Se conservan fotos anteriores en biblioteca,
precios y variantes; ambos WebP mantienen RGBA exacto. Pasan doce verificaciones en
Chromium/Firefox/WebKit a 390/1440 px, con revisión de capturas oscuras y evidencias en
`design/reviews/argos-neptune-*` y `design/reviews/argos-triumph-of-bacchus-*`.
Se cierra únicamente el frontend temporal 4323.

## 11 de noviembre de 2026 — Prototipo Decants R04 desplegable

Se prepara `design/prototypes/decants-r04-desplegable.html`: catálogo a ancho completo
con columnas adaptables y estudio revelado después de elegir, a la derecha en anchos
expandidos y como vista siguiente en móviles/tablets. Volver/Escape conserva filtros y foco.
Reutiliza el motor de prototipos R03 con una variante aislada y estilos `decants-r04.css`.
21 combinaciones de navegador/ancho verificadas, más teclado y accesibilidad. Evidencias
en `design/reviews/decants-r04-*`. Pendiente de aprobación; sin cambios en el frontend del
producto ni backend. Servidor temporal de prototipos cerrado al finalizar.

Ajuste de R04 solicitado el 11 de noviembre: Familia y Público usan botones directos
visibles (Todos, Árabe/Diseñador/Nicho y Hombre/Mujer/Unisex), con filtros combinables
y limpieza funcional. Se verifica en Chromium/Firefox/WebKit a 390/768/1440/1920 px.
Continúa como prototipo pendiente de aprobación.

## 11 de noviembre de 2026 — R04 rechazado; apertura sobre la vista original R05

El propietario rechaza R04 y autoriza conservar exactamente la presentación actual de su
captura, cambiando solo el estado inicial y su transición. Se integra catálogo a ancho
completo sin selección automática; al elegir, se restaura la distribución original y aparece
el estudio. Se mantienen filtros, tarjetas, medidas, precios y animación existentes. Los
links con `selected` válido mantienen selección al recargar. R04 no se integra.
18 combinaciones de navegador/ancho correctas, comparación exacta de estilos/dimensiones
en Chromium a 390/1440/1920 px, filtros/transición/recarga comprobados. Astro check sin
errores ni advertencias; cuatro pruebas unitarias correctas. Evidencias decants-r05-*.
Se cierra solo el frontend temporal 4323 y se conserva el del propietario en 4322.

## 11 de noviembre de 2026 — Prototipo de fondo de perfumes completos R02

Se prepara `design/prototypes/completos-fondo-r02.html`, copiando la vista actual sin cambiar
el producto. Oculta la cinta de marcas y repite cinco veces el nombre seleccionado en el
fondo; ajusta tipografía al ancho y a la longitud para evitar cortes laterales. Usa controles
y estilos originales, con texto decorativo detrás de frascos/contenido y panel accesible.
54 comprobaciones de márgenes en tres navegadores/seis anchos y todos los nombres en
móvil/escritorio; evidencias completos-fondo-r02-*. Pendiente de aprobación visual.

## 11 de noviembre de 2026 — Dos propuestas de armonía para perfumes completos R03

Se preparan completos-armonia-r03-a.html (carrusel compacto y franja de información) y
completos-armonia-r03-b.html (carrusel y ficha lateral), ambas en design/prototypes.
Precio visible en la apertura y menú en un espacio propio del flujo, después de miniaturas.
Patrón de nombres más discreto, fotos originales copiadas localmente sin modificarlas.
126 comprobaciones correctas en tres navegadores/siete tamaños; menú y accesibilidad
funcionales en las dos. Evidencias completos-armonia-r03-*. Pendientes de aprobación;
el proyecto principal no cambia.

## 12 de noviembre de 2026 — Decants R05 aprobado; completos R04 para revisión

El propietario aprueba expresamente el último Decants R05, ya integrado; se registra la
aprobación. Rechaza las alternativas A/B R03 de completos. Se prepara completos-visibilidad-r04.html
con la vista original centrada, cinta y menú inferior conservados, ajustando altura de
frascos, miniaturas y espacios para mostrar nombre, ml, precio y botón dentro de la pantalla.
72 comprobaciones correctas en tres navegadores y ocho tamaños, incluida pantalla 320×568,
y revisión de todos los nombres en móvil/escritorio. Evidencias completos-visibilidad-r04-*.
Esta revisión de completos espera aprobación y no modifica el producto.

## 12 de noviembre de 2026 — Completos R05 con frascos mayores

Se prepara completos-protagonista-r05.html en design/prototypes: carrusel más grande,
ml junto al nombre y precio con botón a su lado debajo. Miniaturas pueden quedar fuera
del primer viewport, según indicación del propietario. Conserva controles, cinta, fondo y
menú inferior; datos comerciales intactos. 288 verificaciones correctas en tres navegadores,
ocho tamaños y doce perfumes; controles y texto 125% comprobados en móvil. Evidencias
completos-protagonista-r05-*. Pendiente de aprobación y sin integración en el producto.

### Ajuste de R05 antes de aprobación — 12 de noviembre de 2026

El propietario solicita quitar la cinta de marcas y dejar exactamente tres repeticiones del
nombre seleccionado detrás de los frascos. Se ajustan únicamente CSS/JS del prototipo R05;
se conservan tamaños y distribución de nombre/ml y precio/botón. Las filas se ajustan al
ancho/altura del carrusel. 63 comprobaciones en tres navegadores/siete tamaños y todos los
nombres en móvil/escritorio; evidencias completos-protagonista-r05-fondo-*. Pendiente de
aprobación; sin integración en el producto.

## 12 de noviembre de 2026 — Fotos vigentes y rotación diaria del Home

El Home resuelve las fotos principales actuales del catálogo en los mensajes welcome,
decants y full-bottles, evitando las referencias antiguas guardadas por la semilla. Cada
trío contiene árabe, diseñador y nicho, con selección aleatoria estable durante la fecha de
Ecuador y cambio al consultar después de medianoche. Ciclos por categoría evitan repetir
el perfume del día anterior cuando hay alternativas y el catálogo no cambia. Sin tareas
programadas, migraciones, dependencias nuevas ni cambios de diseño. La configuración privada
y los mensajes personalizados se conservan. Si falta una categoría fotografiada, se usa el
símbolo alternativo existente.

18 pruebas correctas; Ruff y formato correctos. 45 comprobaciones de navegador en tres
motores y cinco anchos, fotos vigentes y sin desbordamientos. Evidencias home-daily-*.
Con autorización expresa del propietario, se reinicia solo el backend 5000; frontend 4322
conserva PID 91551. Home habitual comprobado con las nueve fotos actuales cargadas. Las
instancias temporales 5001/4323 se cierran al terminar.

## 12 de noviembre de 2026 — Completos R05 aprobado e integrado

El propietario pide agregar los cambios de completos para visualizar mejor todos los elementos;
se registra la aprobación de R05 con su último ajuste. Se integran frascos grandes, ml junto
al nombre, precio y compra en fila inferior, eliminación de cinta y tres nombres de fondo.
Se modifica CylinderPage.astro, cylinder.ts y el bloque existente de global.css; no cambia el
backend, inventario ni precios. Las regiones de filtros ya no incluyen la cinta retirada.
288 casos correctos (12 perfumes, 3 motores, 8 tamaños); teclado, filtros sin recarga, ES/EN,
texto ampliado, contraste y paneles comprobados. Astro check sin errores, lint, formato,
build y dos pruebas unitarias correctos. Evidencias completos-r05-integrated-*.
Vista integrada abierta en Chrome en 4322, revisada visualmente. Se conservan los servidores
habituales y se cierra únicamente el frontend temporal 4323.

## 12 de noviembre de 2026 — Catálogos por marca y modelo

El propietario solicita agrupar alfabéticamente por marca y ordenar sus modelos. Se prepara
el orden público en CatalogQueryFacade antes de paginar, manteniendo sort=name y los otros
órdenes por precio. Administración conserva su orden. El selector compartido se etiqueta
Marca y modelo / Brand and name. Sin migraciones ni cambios de datos. 19 pruebas de catálogo
correctas; Ruff, ESLint, formato y Astro check sin errores. Se verifican los 127 decants y
12 completos mediante lectura local; evidencia catalog-brand-order-data.json. El propietario
autoriza reiniciar solo el backend 5000; se activa el orden y el frontend 4322 conserva su
proceso. 14 comprobaciones de API y navegador correctas en tres motores, móvil/escritorio;
evidencia catalog-brand-order-checks.json. Se cierra únicamente el frontend temporal 4323.

## 12 de noviembre de 2026 — Frascos laterales sin perspectiva y hover del Home

Por instrucción del propietario, se quitan translateZ/rotateY y perspectiva del carrusel:
los vecinos comparten escala 0,9 y el seleccionado mantiene escala 1. R05 se sincroniza
con un runtime propio para no modificar R04. En Home, cada imagen crece un 8% al pasar un
puntero preciso, sin alterar las transformaciones del contenedor y respetando reducción
de movimiento. 315 comprobaciones correctas en tres motores y ocho tamaños; Astro check,
lint, formato, build y dos pruebas unitarias correctos. Evidencias completos-frontal-*,
home-bottle-hover.png y frontal-hover-checks.json. Se revisa completos en Chrome 4322;
los servidores del propietario se conservan y se cierra solo el frontend temporal 4323.

## 12 de noviembre de 2026 — Cinco completos JPG/Valentino

El propietario solicita Le Male Le Parfum 125 ml $165, Le Beau Le Parfum 125 ml $168,
Le Male Elixir 125 ml $165, Ultra Male 125 ml $155 y Valentino Born in Roma Intense
100 ml $168. Se usa la ficha existente Uomo Born in Roma Intense. Se reactivan tres
variantes y se crean dos mediante CatalogService, con auditoría; las presentaciones
100/125 ml estaban configuradas. El catálogo público pasa de 12 a 17 completos.
Fotos, productos y decants se mantienen; sin movimientos de inventario ni asignación
de existencias. Las cinco variantes tienen saldo cero y se muestran agotadas.
120 comprobaciones correctas en tres navegadores y ocho tamaños. Evidencias
completos-added-jpg-valentino*. Se abre Le Male Le Parfum en Chrome 4322; servidores
habituales conservados y solo el frontend temporal 4323 se cierra al terminar.

## 13 de noviembre de 2026 — Lanzamiento por etapas: interfaz de catálogo

El propietario solicita ocultar temporalmente los demás menús y conservar Inicio, Decants
y Perfumes completos. Se activa PUBLIC_CATALOG_ONLY por defecto, centralizado en
features/catalog/storefront.ts; false restaura las funciones completas. Se limitan menú,
cabecera, pie, destinos del Home y acciones de compra en catálogos/ficha. Se conservan los
precios, tamaños, fotos, filtros, animación, accesibilidad e idioma. Administración conserva
su URL y su menú privado, con autenticación/permisos. No se bloquean rutas ni APIs ni se
borran datos; el alcance es visibilidad pública. Los servidores existentes se conservan.
75 comprobaciones de catálogo en tres motores y ocho tamaños, 15 pruebas de menú completo,
sesión y fotos en PostgreSQL temporal, y 27 unitarias correctas. Astro, ESLint, Ruff, formato
y build correctos. Evidencias catalog-only-*. El frontend temporal 4323 se cierra al terminar.
