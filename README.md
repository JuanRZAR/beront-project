# BÉRONT

Catálogo de decants y perfumes completos para Ecuador continental. Español e inglés, precios en
USD, pedidos persistentes con pago por transferencia revisada manualmente o coordinado por WhatsApp.

## Estado

Home integrado el 9 de noviembre de 2026 con carrusel informativo, recortes sin fondo, cinta de
marcas y accesos rápidos. Los mensajes se administran en Configuración → Inicio y mensajes.
La base local contiene el catálogo y está migrada a `de252c02c932`. Estado y verificaciones en
[docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md); auditoría previa en [docs/AUDITORIA.md](docs/AUDITORIA.md).

## Documentación

- [Memoria del proyecto y registro de cambios](project_memory.md).
- [Arquitectura aprobada](docs/ARCHITECTURE.md).
- [Preparación y comandos locales](docs/LOCAL.md).
- [Auditoría y estado](docs/AUDITORIA.md) e [implementación](docs/IMPLEMENTATION.md).
- [Registro de aprobación visual](docs/DESIGN_APPROVALS.md).
- [Funciones SQL](backend/bd/README.md).
- [Reglas de trabajo](AGENTS.md).

## Puesta en marcha

Para una instalación nueva, desde `backend/` (requiere `backend/.env`, ver docs/LOCAL.md):

```powershell
uv sync --locked
uv run beront migrate
uv run beront createsuperuser
uv run beront importar-catalogo
uv run beront importar-recortes --manifiesto ../design/assets/inkscape-catalog-r02-manifest.json
uv run beront inicializar-home
uv run beront run
```

Desde `frontend/`:

```powershell
bun.cmd install --frozen-lockfile
bun.cmd run dev --port 4322
```

Abrir http://localhost:4322/es/ . Configurar `FRONTEND_ORIGIN` con ese origen en `backend/.env`.
El acceso administrativo está en `/es/admin/login`. La instalación local ya tiene administrador
y datos; no repetir su creación ni detener los servidores existentes.

## Verificación

```powershell
# backend/
uv run ruff check src tests semillas
uv run pytest --cov=beront

# frontend/
bun.cmd run check
bun.cmd run lint
bun.cmd run test
bun.cmd run build
bun.cmd run test:app
```

`test:app` usa Flask y PostgreSQL temporales y no modifica la base comercial.
