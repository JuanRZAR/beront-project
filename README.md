# BÉRONT

La ampliación de comercio y pedidos está documentada en
[docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md). El backend está migrado y verificado y las
vistas aprobadas de las [revisiones 04 y 05](design/README.md) están integradas (checkout,
seguimiento, configuración, biblioteca y pedidos). La revisión 03 espera sus modificaciones;
la importación comercial y la configuración de SMTP en `backend/.env` siguen pendientes.

Catálogo de decants y perfumes completos para Ecuador continental.
Español e inglés, precios en USD y continuación por WhatsApp.

## Estado

- Backend Flask implementado con catálogo, administración, inventario y carrito.
- Esquema PostgreSQL definido por SQLAlchemy y creado mediante Alembic.
- Revisión visual 01 de las seis vistas aprobada por el propietario.
- Frontend Astro integrado: catálogo bilingüe, carrito, acceso y administración.
- La conexión a la base comercial requiere completar backend/.env.
- El número de WhatsApp, el logotipo original y los productos comerciales no están configurados.

## Documentación

- [Arquitectura aprobada](docs/ARCHITECTURE.md).
- [Preparación y comandos locales](docs/LOCAL.md).
- [Prototipos para revisión](design/README.md).
- [Registro de aprobación visual](docs/DESIGN_APPROVALS.md).
- [Reglas de trabajo](AGENTS.md).

## Abrir la aplicación

Desde frontend/:

```powershell
bun.cmd run dev
```

Abrir http://localhost:4321/es/ . Para administrar productos, iniciar también
Flask con la configuración descrita en docs/LOCAL.md. Si el backend no está
disponible, el frontend muestra un estado de conexión controlado.

Comprobaciones del frontend:

```powershell
bun.cmd run test
bun.cmd run check
bun.cmd run lint
bun.cmd run build
bun.cmd run test:app
```

test:app utiliza Flask y PostgreSQL temporales y no modifica la base comercial.

## Revisar los prototipos

Desde la raíz del proyecto:

```powershell
backend\.venv\Scripts\python.exe -m http.server 4322 --bind 127.0.0.1 --directory design
```

Abrir http://127.0.0.1:4322/prototypes/catalog.html .

Los enlaces de la franja superior permiten recorrer las seis vistas.
Son demostraciones visuales; no crean productos, no registran ventas y no envían credenciales.
Las capturas de revisión están en design/reviews/.
