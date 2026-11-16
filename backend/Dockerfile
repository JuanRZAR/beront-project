FROM python:3.14-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY src ./src
RUN uv sync --locked --no-dev

FROM python:3.14-slim
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY --from=build /app/.venv ./.venv
COPY src ./src
COPY bd ./bd
COPY migrations ./migrations
COPY semillas ./semillas
COPY alembic.ini ./
RUN mkdir -p var/uploads var/staging && chown -R 10001:10001 var
USER 10001:10001
EXPOSE 8000
CMD ["gunicorn", "beront.app:create_app()", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "60", "--graceful-timeout", "15", "--access-logfile", "-", "--no-control-socket"]
