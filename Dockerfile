# =============================================================================
# redesolidaria — imagem unica da API servindo o SPA Angular buildado.
#   Stage 1 (web):     builda o SPA Angular.
#   Stage 2 (runtime): Python 3.13 + uv; roda migrations e API (uvicorn).
# A API serve o SPA buildado (mesma origem, sem CORS).
# =============================================================================

# ---------- Stage 1: build do SPA Angular ----------
FROM node:22-alpine AS web
ARG BASE_HREF=/
WORKDIR /web
# manifests primeiro (cache de layer do npm ci)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# configuracao "docker"
RUN npm run build -- --configuration docker --base-href ${BASE_HREF}

# ---------- Stage 2: runtime Python (API) ----------
FROM python:3.13-slim AS runtime
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app

# dependencias primeiro (cache): so os manifests, sem o projeto
COPY backend/project.toml backend/uv.lock ./
RUN cp project.toml pyproject.toml && uv sync --frozen --no-dev --no-install-project

# codigo do backend + sincroniza manifesto e instala o projeto
COPY backend/ ./
RUN python scripts/sync_manifest.py && uv sync --frozen --no-dev

# SPA buildada -> pasta de estaticos servida pela API
COPY --from=web /web/dist/redesolidaria/browser ./web/static/app

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn web.main:app --host 0.0.0.0 --port 8000"]
