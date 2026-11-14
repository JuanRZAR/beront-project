# Auditoría de BÉRONT — 13 de noviembre de 2026

Estado: correcciones verificadas y activadas tras autorización del propietario. Ejecución exclusivamente local.

## Alcance y protección de datos

Revisión de catálogo, filtros, carrito, cotización, errores, dependencias y herramientas de prueba.
Se ejecutaron pruebas de dominio, integración HTTP/PostgreSQL, arquitectura, migraciones y navegador.
Las operaciones de prueba de inventario, pedidos y administración utilizaron bases y servidores
temporales. La aplicación del propietario solo recibió lecturas para medir la carga pública.
No se modificaron productos, fotografías, precios, existencias, pedidos ni el carrito del propietario.
No se enviaron mensajes de WhatsApp ni correos reales.

Se conserva la arquitectura Flask/PostgreSQL/Astro, las funciones SQL a través de repositorios,
Decimal para dinero y ml, los contratos HTTP y el diseño aprobado. No hay migraciones nuevas.
El árbol de trabajo ya contenía cambios anteriores; este informe describe únicamente esta auditoría.

## Errores corregidos

| ID | Gravedad estimada | Fallo reproducido | Corrección y evidencia |
|---|---|---|---|
| AUD-01 | Media | Una búsqueda anterior fallaba después de completarse una nueva y redirigía a los resultados antiguos. | `liveFilters.ts` cancela la petición anterior y descarta sus errores/respuestas mediante la generación vigente. Prueba de navegador con peticiones controladas. |
| AUD-02 | Media | Un cambio de cantidad generaba dos POST idénticos de cotización desde el diálogo y el resumen. | `quote.ts` comparte únicamente la promesa en curso para el mismo idioma y contenido del carrito; la elimina al resolverse o fallar. Medición: dos solicitudes antes, una después. |
| AUD-03 | Media | Un identificador guardado como arreglo en localStorage superaba la expresión regular por coerción y bloqueaba la cotización con HTTP 422. | `CartStore.read()` exige que el identificador sea texto y descarta las entradas manipuladas. Prueba unitaria de datos malformados. |
| AUD-04 | Media | Reemplazar una presentación por ella misma eliminaba la línea del carrito. | `CartStore.replace()` conserva la línea y cantidad cuando ambos identificadores son iguales. Regresión con cantidad dos. |
| AUD-05 | Baja | Varios errores de negocio mostraban caracteres dañados, como «presentaciÃƒÂ³n». | Se reparan siete literales de `pg_call.py`; seis códigos de negocio tienen regresión parametrizada. Se conservan códigos y estados HTTP. |
| AUD-06 | Bloqueante para pruebas | La suite Python se detenía al recopilar pruebas de migraciones por `ModuleNotFoundError: tests.conftest`. | `tests/migrations/test_home.py` importa el helper desde `conftest`, conforme al entorno real de pytest. La suite completa vuelve a ejecutarse. |
| AUD-07 | Media, herramientas | `minimatch` 10.2.6 figuraba con aviso de denegación de servicio en la cadena de ESLint/TypeScript. | Override a 11.0.1 y actualización de `bun.lock`; auditoría posterior sin avisos y validación de lint, tipos y build. |
| AUD-08 | Baja, herramientas | Los escenarios antiguos esperaban selección automática en Decants y un decant ilustrado en el carrito de completos. | Se actualizan las pruebas para pulsar el perfume y comprobar su foto sin mini vial, según el diseño vigente. No se cambia la interfaz para satisfacer expectativas antiguas. |
| AUD-09 | Baja, herramientas | Dos ejecuciones de Playwright compartían `test-results`, borraban trazas de la otra y producían errores ENOENT. | Cada ejecución del harness usa una salida dentro de su directorio temporal mediante `BERONT_E2E_OUTPUT_DIR`. La ejecución directa conserva su salida habitual. Se repiten las suites secuencialmente para el cierre. |

La actualización de `minimatch` corrige el aviso moderado
[GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249).
Pertenece a las herramientas de desarrollo; no se observó explotación en BÉRONT. No se añaden
capacidades ni dependencias directas nuevas. `uv.lock` permanece sin cambios.

## Optimizaciones de rendimiento

### Backend

- Las definiciones de categorías, públicos, presentaciones y opciones se consultan una vez por
  petición de filtros y se reutilizan para construir las dos representaciones de la respuesta.
- Se evita solicitar una página vacía cuando el último lote contiene menos de 100 productos.
  Un lote completo sigue comprobando la página siguiente.
- La disponibilidad omite consultas de inventario para grupos sin identificadores.
- El modo abierto evita construir requisitos de stock que no necesita. El modo estricto y la
  marca manual de agotado conservan sus comprobaciones.
- No se introduce caché persistente, caché global de catálogo ni precios almacenados en frontend.

### Medición comparativa reproducible

Herramienta permanente: `backend/tests/integration/benchmark_catalog.py`.
Misma semilla de 130 perfumes, PostgreSQL temporal, modo abierto, dos calentamientos y 20 muestras
seriales por endpoint. Se cuentan llamadas desde `PgCall` a funciones PostgreSQL; no son todos los
comandos internos ejecutados por esas funciones. Se usa Flask test client, sin coste de red HTTP.

| Endpoint | Llamadas PostgreSQL antes → después | Mediana antes → después | p95 antes → después | Bytes antes/después |
|---|---:|---:|---:|---:|
| Catálogo de decants | 3 → 2 | 25,58 → 25,14 ms | 26,24 → 25,46 ms | 22.787 / 22.787 |
| Filtros `/catalog/facets` | 15 → 8 | 27,68 → 26,47 ms | 28,35 → 26,78 ms | 5.442 / 5.442 |
| Mensajes Home | 3 → 3 | 26,29 → 26,44 ms | 26,88 → 26,78 ms | 5.210 / 5.210 |

Reducción de llamadas: **46,7 % en filtros** y **33,3 % en catálogo**. La mediana observada mejora
aproximadamente 4,4 % y 1,7 %, respectivamente. Home no presenta mejora de mediana; la diferencia
es pequeña y no permite atribuir una regresión. No se promete una mejora significativa de latencia
con una muestra local tan pequeña.

Carga concurrente: 40 solicitudes al catálogo, cuatro trabajadores; **cero errores antes y después**.
Rendimiento observado: 104,68 → 106,96 solicitudes/s. Es una comparación local breve, no una prueba
de capacidad de producción, saturación ni usuarios simultáneos reales.

Prueba de regresión adicional: con un perfume, `/catalog/facets` realiza siete llamadas
(una página y seis definiciones), sin consultas duplicadas.

### Frontend

Una modificación de cantidad pasa de **dos a un POST de cotización** en el escenario reproducido:
50 % menos solicitudes duplicadas. La respuesta no se conserva como caché; una nueva cotización
posterior vuelve al backend. Un filtro anterior se aborta al iniciar otro para evitar trabajo y
navegación obsoletos.

Observación de carga en Chromium 156.0.8078.4, frontend local de desarrollo, caché fría y una sola
muestra por ruta/tamaño, sin limitar CPU ni red. Altura: 900 px. Bytes transferidos incluyen recursos
de desarrollo y fotografías. No son métricas de una compilación publicada.

| Ancho CSS | Ruta | TTFB | FCP | LCP observado | Transferencia | Peticiones de recursos | Desbordamiento horizontal |
|---|---|---:|---:|---:|---:|---:|---|
| 390 | Inicio | 172 ms | 212 ms | 212 ms | 5.057.783 B | 42 | No |
| 390 | Decants | 91 ms | 128 ms | 128 ms | 10.405.453 B | 57 | No |
| 390 | Completos | 96 ms | 136 ms | 180 ms | 8.031.002 B | 51 | No |
| 1440 | Inicio | 86 ms | 124 ms | 124 ms | 5.057.783 B | 42 | No |
| 1440 | Decants | 91 ms | 136 ms | 136 ms | 10.405.453 B | 57 | No |
| 1440 | Completos | 83 ms | 132 ms | 156 ms | 8.031.002 B | 51 | No |

Solo se observó una tarea larga de 54 ms, en Completos a 1440 px; las otras cinco cargas no
registraron tareas superiores a 50 ms durante la observación. El LCP es una observación corta,
no una evaluación de Core Web Vitals de campo. No se calculó un percentil de usuarios ni se
verificaron teléfonos físicos, televisores o conexiones móviles reales.

## Verificación

- Backend: **184 pruebas aprobadas**; cobertura combinada de líneas y ramas **93,82 %**
  (3.118 líneas cubiertas de 3.284; 496 ramas cubiertas de 568). Ruff y formato: correctos,
  169 archivos. Incluye contratos HTTP, permisos, stock/carrito/pedidos, migraciones y arquitectura.
- Frontend: **28 pruebas unitarias aprobadas**, Astro check sin errores ni advertencias;
  ESLint, Prettier y build correctos después de actualizar el lock.
- Navegadores: **63 escenarios aprobados, cero fallos**, en el perfil completo; sus 12 escenarios
  exclusivos de WhatsApp se omiten allí y se ejecutan por separado: **12 aprobados, cero fallos**.
  Total: 75 ejecuciones aprobadas en Chromium, Firefox y WebKit. La repetición final no comparte
  salidas entre procesos; se descartan las ejecuciones afectadas por la colisión de trazas.
- Python: `pip-audit` sin vulnerabilidades conocidas en los 60 paquetes consultados. El paquete
  local `beront` no se audita en PyPI; se informa como omitido. No equivale a auditar su código.
- JavaScript: `bun audit --json` devuelve `{}` después de la actualización, sin avisos conocidos.
- No se modifica el esquema; la cabeza sigue siendo `de252c02c932`.

Los escenarios existentes abarcan teclado, accesibilidad, movimiento reducido, ES/EN, fotos,
carrito, pedidos y controles privados en Chromium, Firefox y WebKit. Recorridos responsivos de
320 a 1920 px, además de otros tamaños definidos por los escenarios del carrito. Son pruebas de
navegadores con viewports emulados, no certificación WCAG ni validación en dispositivos físicos.

## Hallazgos pendientes y límites

1. **Permisos de PostgreSQL local — riesgo alto de configuración.** Se verificó por lectura de
   metadatos que la conexión de ejecución tiene privilegios de superusuario, creación de bases y
   creación de roles. Es la configuración previamente elegida por el propietario y documentada en
   `LOCAL.md`; el código no puede imponer aislamiento de mínimo privilegio sobre ese rol. No se
   cambian roles, credenciales ni `.env` sin resolver esa decisión. La configuración objetivo y los
   permisos del rol de aplicación se describen en `LOCAL.md`. Las pruebas aisladas sí usan un rol
   de ejecución sin esos privilegios y verifican los límites de acceso.
2. **Peso de imágenes.** Las cargas de desarrollo observadas transfieren entre 5,06 y 10,41 MB.
   Se conserva la calidad aprobada y no se recomprimen ni sustituyen fotos. Optimizar con derivados
   responsivos requeriría definir ese tratamiento dentro del contrato de imágenes antes de aplicarlo.
   La medición local rápida no demuestra buena experiencia en una conexión móvil lenta.
3. **Escala.** La consulta ordenada y los filtros aún recorren el catálogo por lotes. La reducción
   de llamadas mejora el caso medido, pero no resuelve el coste de un catálogo mucho mayor.
4. **Seguridad.** Las suites comprueban defensas de acceso, autenticación, CSRF, inyección, límites,
   integridad, errores y migraciones. La revisión de dependencias y estas pruebas no son un pentest
   exhaustivo ni una garantía de ausencia de vulnerabilidades. SMTP y WhatsApp reales no se usan.
5. **Activación local completada.** El propietario autorizó reiniciar únicamente el backend
   5000. Se sustituyó el proceso 18195 por 44808; el frontend 4322 conserva su proceso 91551.
   Catálogos de 127 decants y 17 completos, filtros y mensajes Home respondieron HTTP 200;
   Inicio, Decants y Completos del frontend también respondieron HTTP 200. Se cerró solo
   el frontend temporal 4323. No se alteró el carrito ni se realizaron escrituras comerciales.

## Archivos de esta intervención

- Backend: `modules/catalog/application/query_catalog.py`,
  `modules/inventory/application/availability.py`, `shared/infrastructure/pg_call.py`.
- Frontend: `features/catalog/liveFilters.ts`, `features/cart/{store,quote}.ts`.
- Dependencias: `frontend/package.json`, `frontend/bun.lock`.
- Pruebas: `backend/tests/migrations/test_home.py`, `backend/tests/unit/test_pg_call.py`,
  `backend/tests/integration/{test_catalog,benchmark_catalog,frontend_browser}.py`,
  `frontend/tests/unit/cart.test.ts`,
  `frontend/tests/e2e/{application,application-commerce,application-audit}.spec.ts`,
  `frontend/playwright.config.ts`.
- Documentación: este informe, `docs/LOCAL.md`, `docs/ARCHITECTURE.md` y `project_memory.md`.

Las rutas de código anteriores son relativas a `backend/src/beront/` o `frontend/src/` según el caso.
Los cambios anteriores del proyecto no se atribuyen a esta auditoría.

## Cómo repetir las comprobaciones

Desde `backend/`, con dependencias instaladas desde `uv.lock`:

```sh
POSTGRES_BIN=/Applications/Postgres.app/Contents/Versions/latest/bin .venv/bin/pytest
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/pip-audit
POSTGRES_BIN=/Applications/Postgres.app/Contents/Versions/latest/bin .venv/bin/python tests/integration/benchmark_catalog.py --output /tmp/beront-benchmark.json
POSTGRES_BIN=/Applications/Postgres.app/Contents/Versions/latest/bin .venv/bin/python tests/integration/frontend_browser.py
BERONT_E2E_WHATSAPP_ONLY=true POSTGRES_BIN=/Applications/Postgres.app/Contents/Versions/latest/bin .venv/bin/python tests/integration/frontend_browser.py
```

El harness crea y elimina PostgreSQL, almacenamiento y servidores temporales. Sus resultados de
Playwright pertenecen al directorio temporal de la ejecución y se eliminan al terminar; la ejecución
directa de Playwright sigue usando `frontend/test-results`. No apunta a la base del propietario.

Desde `frontend/`:

```sh
bun install --frozen-lockfile --ignore-scripts
bun run check
bun run lint
bun run format
bun test tests/unit
bun run build
bun audit
```

Los binarios de PostgreSQL dependen del equipo. No ejecutar pruebas que escriben contra la base
habitual ni detener los servidores del propietario. Los archivos exploratorios de esta auditoría
se eliminan al cerrar; se conservan las pruebas de regresión y el benchmark reproducible.

---

# Histórico conservado

El informe siguiente corresponde al 2 de noviembre. Sus datos y pendientes son históricos;
para el estado actual prevalece la auditoría del 13 de noviembre anterior.

# Auditoría backend/frontend del 2 de noviembre de 2026

Alcance: contratos HTTP, esquemas, funciones SQL, vistas Astro, pruebas, migraciones y documentación.
Criterio: la regla 8 de `AGENTS.md` (backend completo antes del frontend) y la retirada del
contenido temporal ordenada por el propietario. Solo se conserva la semilla de perfumes.

## Resultado

Backend y frontend quedan alineados. Todas las rutas que usa el frontend existen en el backend,
cada carga útil coincide con su esquema y las capacidades del backend ya tienen su control en el
panel. `alembic check` no detecta diferencias con los modelos y la cabeza de migraciones es
`49ce23c2f0c8`.

## Hallazgos corregidos

### El backend no cubría lo que el frontend necesitaba

1. **Inventario sin nombres ni filtros.** `GET /admin/inventory` devolvía saldos con un
   identificador. Para mostrar nombres, filtrar por tipo y buscar, el frontend descargaba todo el
   catálogo y todos los saldos en cada petición. Ahora la API devuelve `product_id`, `product_name`,
   `brand_name` y `volume_ml`, acepta `kind` y `q`, ordena por nombre y pagina en SQL. Lo mismo
   aplica a `/admin/inventory/movements`. Migración `87313231bdf2`.
2. **Guardar un perfume borraba vínculos a opciones desactivadas.** La arquitectura exige que una
   opción desactivada conserve sus vínculos, pero `catalog_product_options_set` eliminaba todos los
   de la dimensión. Ahora solo reemplaza los de opciones activas; reactivar la opción restaura el
   vínculo. Migración `49ce23c2f0c8` y prueba.

### El frontend no cubría lo que el backend ya ofrecía

3. **Acordes, tipos de uso y perfiles olfativos** no se podían asignar ni filtrar. Se añadieron al
   editor de perfumes, a los filtros públicos, a la tarjeta y a la ficha.
4. **Etiquetas fijas.** Categorías y públicos estaban escritos en el diccionario (`arabic`,
   `designer`, `niche`, `male`, `female`, `unisex`) y como listas por defecto. Ahora los nombres ES/EN
   vienen de `facets.definitions`; una categoría nueva se ve con su nombre sin tocar el código.
5. **Presentaciones del editor.** Ofrecía tipo libre y una lista fija de 3, 5 y 10 ml, aunque el
   backend solo admite presentaciones configuradas. Ahora se elige entre las configuradas que el
   perfume aún no tiene.
6. **Suposiciones de negocio en el código:** presentación preferida «5 ml», público por defecto
   «unisex» y un carrusel que buscaba las categorías «diseñador» y «nicho». Se eliminaron.
7. **Activar y desactivar.** El backend admite `active` en categorías, públicos, acordes, usos,
   perfiles, presentaciones, ciudades, bancos, estados y transiciones; el panel solo creaba y
   editaba nombres. Cada fila tiene ahora su botón y muestra «Inactivo».
8. **Siete códigos de error sin mensaje** (`CART_LIMIT`, `INVALID_QUANTITY`, `UNAVAILABLE_QUANTITY`,
   `INVALID_PRESENTATION`, `INVALID_VARIANT`, `ORDER_TOTAL_LIMIT`, `UNEXPECTED_RECEIPT`) caían en el
   mensaje genérico. Ya tienen texto ES/EN y prueba.
9. **Inventario:** la columna de estado ahora indica «Con existencias» o «Sin existencias» según el
   saldo, ya que el listado no calcula disponibilidad comercial.

### Contenido temporal y de prueba retirado

- `frontend/public/temporal/`, `src/pages/temporal/`, `features/catalog/temporary.ts`, su excepción en
  el middleware y sus 4 archivos de prueba (retirado en la sesión anterior; las 132 fotografías siguen en
  `backend/semillas/catalogo/imagenes/`).
- `tests/e2e/prototypes.spec.ts` y el servidor de `design/` de `playwright.config.ts`: apuntaban a una
  carpeta que ya no existe y a una ruta de Windows.
- 45 textos de demostración o sin uso del diccionario (por idioma), la clase `demo-upload` y
  `docs/TEMPORARY_CATALOG.md`. Se actualizaron README, LOCAL, IMPLEMENTATION, ARCHITECTURE y
  DESIGN_APPROVALS.
- Se conservan las pruebas permanentes de backend y frontend.

### Infraestructura de pruebas

- La prueba de navegador fallaba de forma intermitente en Chromium: tres navegadores corrían a la vez
  sobre la misma base y la misma fotografía. Ahora se ejecutan de uno en uno (`workers: 1`).
- Astro 7 dejaba el servidor de desarrollo como proceso huérfano y la ejecución siguiente fallaba
  («ya hay un servidor»). El arnés lo inicia con `--ignore-lock`, sin tocar el servidor del propietario.
- Migraciones, carpeta `bd/` y CLI `beront`: ver [ARCHITECTURE.md](ARCHITECTURE.md), apartado del
  1 de noviembre.

## Verificación

| Comprobación | Resultado |
|---|---|
| Backend: Ruff, formato | Sin incidencias |
| Backend: pytest | 145 pruebas aprobadas, cobertura 94,12 % |
| Backend: `alembic check` | Sin diferencias; base `beront-bd` en `49ce23c2f0c8` |
| Backend: `pip-audit` | Sin vulnerabilidades conocidas |
| Frontend: `astro check`, ESLint, Prettier, compilación | Sin incidencias |
| Frontend: pruebas unitarias | 18 aprobadas |
| Navegador (Flask + PostgreSQL temporal + Astro) | 27 aprobadas en Chromium, Firefox y WebKit |

## Limitaciones y decisiones pendientes

- **Diseño.** Los controles de acordes, usos y perfiles (editor, filtros y ficha) se hicieron con los
  componentes ya aprobados y sin un prototipo propio, por instrucción del propietario. Queda
  registrado en [DESIGN_APPROVALS.md](DESIGN_APPROVALS.md); un prototipo posterior puede sustituirlos.
- **Dependencias.** `bun audit` informa una vulnerabilidad moderada en `minimatch` (<11.0.1) dentro de la
  cadena de ESLint. Es solo de desarrollo y no llega al producto; no se alteró `bun.lock`.
- **Rol de base de datos.** `DATABASE_URL` usa `juanra` (superusuario) por indicación del propietario;
  no hay aislamiento de rol de ejecución. Se puede restablecer según LOCAL.md.
- **Datos.** `beront-bd` está migrada pero vacía: falta crear el administrador
  (`uv run beront createsuperuser`) e importar la semilla (`uv run beront importar-catalogo`). Hasta
  entonces el catálogo no muestra perfumes. No se probó un envío real de correo (`SMTP_*`).
- **Fuera de alcance de esta auditoría:** cambios de negocio, devoluciones y reembolsos, WhatsApp
  comercial, cuentas bancarias y tarifas reales (los registra el propietario en el panel).
- **Rendimiento a vigilar.** `GET /catalog/facets` recorre el catálogo por páginas para calcular casas y
  tamaños; es adecuado para 130 perfumes y conviene pasarlo a una consulta SQL si crece mucho.
- **Cobertura de la revisión.** Checkout, seguimiento, biblioteca y pedidos se verificaron con las
  pruebas de navegador y la comparación de esquemas, no con una lectura línea por línea.
