# Funciones PostgreSQL de BÉRONT

Las tablas y relaciones se definen en
`backend/src/beront/shared/infrastructure/modelos/`. Alembic genera y revisa sus cambios.
La aplicación lee y escribe mediante funciones SQL; no utiliza sesiones ORM.

```text
backend/bd/
└── <modulo>/funciones/<funcion>.sql
```

Módulos: `comunes`, `identity`, `catalog`, `inventory`, `media`, `commerce` y `orders`.
Una función por archivo, con el nombre de la función. Cada archivo contiene la definición
vigente; el historial está en Git. No existen carpetas de versión.

Las funciones usan parámetros JSONB enlazados, `SECURITY DEFINER`, `search_path`
explícito y revocación de ejecución para PUBLIC. El usuario de ejecución requiere
USAGE del esquema `beront_api` y EXECUTE de las funciones permitidas; no necesita
leer ni modificar tablas directamente.

`pg_call.py` mantiene una lista técnica de funciones permitidas. Ningún endpoint
acepta nombres de función, tablas o SQL aportados por el cliente.

## Instalación

Desde `backend/`:

```powershell
uv run alembic upgrade head
uv run alembic check
```

La migración inicial crea las tablas desde los modelos, el esquema `beront_api` y todas las
funciones de esta carpeta. Generar SQL para revisión sin aplicar cambios:

```powershell
uv run alembic upgrade head --sql
```

## Cambiar una función

1. Editar el archivo de la función (`CREATE OR REPLACE FUNCTION`).
2. Crear una migración Alembic nueva cuyo `upgrade()` llame a
   `install_functions(op.get_bind(), ["bd/<modulo>/funciones/<funcion>.sql"])`.
   Si la función cambia de firma o se retira, la migración ejecuta además `DROP FUNCTION`.
3. Aplicarla con `alembic upgrade head` y repetir el `GRANT EXECUTE` al usuario de la aplicación.

El instalador rechaza rutas fuera de `backend/bd/` y archivos que no sean `.sql`. Instala con
`check_function_bodies = off` dentro de la transacción porque las funciones se invocan entre sí.
