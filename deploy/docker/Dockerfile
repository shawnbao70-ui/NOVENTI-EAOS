# PHX-G50 — EAOS Gateway image (Foundation 0.2.0)
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app:/app/sdk

COPY pyproject.toml README.md ./
COPY kernel ./kernel
COPY runtime ./runtime
COPY eaos_platform ./eaos_platform
COPY smart_terminal ./smart_terminal
COPY api ./api
COPY noventi ./noventi
COPY sdk ./sdk
COPY alembic ./alembic
COPY alembic.ini ./
COPY docs/release ./docs/release
COPY docs/api ./docs/api
COPY deploy/docker/entrypoint.py /entrypoint.py
COPY deploy/docker/smoke_imports.py /smoke_imports.py
COPY constraints/production.txt /constraints/production.txt

RUN pip install --no-cache-dir -e ".[persistence,api]" "PyYAML==6.0.3" \
    -c /constraints/production.txt \
    && groupadd -g 10001 eaos \
    && useradd -u 10001 -g eaos -r -s /usr/sbin/nologin eaos \
    && chown -R eaos:eaos /app

USER 10001

EXPOSE 8000
ENTRYPOINT ["python", "/entrypoint.py"]
