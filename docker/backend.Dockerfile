# Build context is the repo root (see docker/docker-compose.yml).
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY apps/api/pyproject.toml ./
# --no-install-project: this pyproject has no [build-system], it's only used
# to declare dependencies for this app, not to be built/installed as a package.
RUN uv sync --no-install-project --no-dev

COPY apps/api/ .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
