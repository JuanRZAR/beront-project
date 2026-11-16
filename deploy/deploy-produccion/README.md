# Despliegue de BÉRONT en el VPS

Forma «Frontend con SSR + API» de la guía de `JuanRZAR/infra-vps-tecnomovil` (guía 02, 2.0).
Arquitectura y decisiones: «Despliegue en el VPS» en `docs/ARCHITECTURE.md`.

## Qué despliega

| Servicio | Imagen | Función |
|---|---|---|
| `app` | `${IMAGE}` (`frontend/Dockerfile`) | Astro SSR con Node. Único servicio público; reenvía `/api` y `/media` a `api` |
| `api` | `${IMAGE_API}` (`backend/Dockerfile`) | Flask con gunicorn (1 worker, 4 hilos). Interno, sin puertos. Redes `default` e `infra` |
| `migrate` | `${IMAGE_API}` | `alembic upgrade head` antes de cada despliegue |

Ambos escuchan en el puerto 8000 como usuario 10001 y responden `GET /health` sin base de datos.
`app` llama a `api` en `http://api:8000`. Las fotografías se guardan en
`/srv/apps/beront/data/var`, montado en `/app/var` de `api`.

## Variables

`.env.example` lista las variables. `app` y `api` leen el mismo `.env`.

| Variable | Servicio | Uso |
|---|---|---|
| `APP_ENV` | api | `production` |
| `DATABASE_URL` | api, migrate | URL generada por `vps-new-project`, con esquema `postgresql+psycopg://` |
| `SECRET_KEY` | api | Clave aleatoria de al menos 32 caracteres |
| `FRONTEND_ORIGIN` | api | `https://beront.com` |
| `CART_REQUIRES_STOCK` | api | `true` |
| `BACKEND_URL` | app | `http://api:8000` |
| `SITE_HOSTS` | app | `beront.com` |
| `TRUST_PROXY` | app | `true`: acepta `X-Real-IP` de nginx |
| `SMTP_*` | api | Gmail con contraseña de aplicación; vacías hasta activar el correo |

## Base de datos

Un solo rol, dueño de la base. `migrate` aplica `alembic upgrade head` con `DATABASE_URL`.
Las migraciones conservan compatibilidad con la versión anterior (guía 02, 2.8).

## Carga inicial (la ejecuta el admin, una vez, tras el primer despliegue)

Dentro del contenedor `api` activo:

```bash
beront createsuperuser
beront importar-catalogo
beront inicializar-home
```
