"""Container entrypoint: wait for DB, migrate, then serve Gateway (PHX-G50)."""

from __future__ import annotations

import os
import subprocess
import sys
import time


def _wait_for_database(*, timeout_seconds: int = 90) -> None:
    url = os.environ.get("EAOS_DATABASE_URL", "").strip()
    if not url:
        print("EAOS_DATABASE_URL is required", file=sys.stderr)
        raise SystemExit(1)

    from sqlalchemy import create_engine, text

    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            engine = create_engine(url, pool_pre_ping=True)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            engine.dispose()
            return
        except Exception as exc:  # noqa: BLE001 — retry until timeout
            last_error = exc
            time.sleep(1)
    print(f"database not ready: {last_error}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    _wait_for_database()
    subprocess.check_call(["alembic", "upgrade", "head"], cwd="/app")
    os.execvp(
        "uvicorn",
        [
            "uvicorn",
            "api.gateway.app:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
    )


if __name__ == "__main__":
    main()
