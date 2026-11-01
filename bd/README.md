# Funciones PostgreSQL de BÉRONT

Las tablas y relaciones se definen en
`backend/src/beront/shared/infrastructure/modelos/`. Alembic genera y revisa sus cambios.
La aplicación lee y escribe mediante funciones SQL; no utiliza sesiones ORM.

```text
bd/
├── comunes/funciones/v0001/            # Auditoría transaccional
├── identity/funciones/v0001/           # Administrador y sesiones
├── catalog/funciones/v0001/            # Catálogo inicial
├── catalog/funciones/v0002/            # Referencias a imágenes reutilizables
├── catalog/funciones/v0003/            # Categorías, públicos y presentaciones configurables
├── inventory/funciones/v0001/          # Saldos y movimientos
├── media/funciones/v0001..v0002/        # Biblioteca y visibilidad de archivos
├── commerce/funciones/v0001/           # Configuración, destinos y bancos
└── orders/funciones/v0001..v0002/       # Pedidos, estados y transferencias ya realizadas
```

Una función por archivo. Hay 101 fuentes versionadas para 86 funciones vigentes.

Las migraciones registran las rutas y SHA-256 de los archivos que instalan.
Una fuente ya aplicada no se edita: se añade otra versión y una migración nueva.
El instalador rechaza rutas fuera de `bd/` y archivos cuyo contenido no coincide
con su huella registrada.

Las funciones usan parámetros JSONB enlazados, `SECURITY DEFINER`, `search_path`
explícito y revocación de ejecución para PUBLIC. El usuario de ejecución requiere
USAGE del esquema `beront_api` y EXECUTE de las funciones permitidas; no necesita
leer ni modificar tablas directamente. La configuración local
adoptó esa separación de roles el 27 de octubre. Flask usa `beront_app_2ec87f29`;
la lectura directa de tablas y la creación de objetos se comprobaron denegadas.
Las pruebas también usan un usuario restringido.

`pg_call.py` mantiene una lista técnica de funciones permitidas. Ningún endpoint
acepta nombres de función, tablas o SQL aportados por el cliente.

Instalación, desde `backend/`:

```powershell
uv run alembic upgrade head
uv run alembic check
```

Generar SQL para revisión sin aplicar cambios:

```powershell
uv run alembic upgrade head --sql
```

La generación de tablas parte de los modelos. Las funciones se incorporan a cada
revisión de forma explícita; Alembic no deduce su lógica comercial de los modelos.
