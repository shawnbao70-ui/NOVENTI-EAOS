"""PHX-G407 — image / layout import smoke for runtime packages.

Run inside the gateway image (or host with PYTHONPATH=/app:/app/sdk):

    python /smoke_imports.py

This proves packaging only. It does NOT authorize host OS installs,
Marketplace host-acquire runtime, or Industry package host-install invent.
"""

from __future__ import annotations

import importlib
import sys

REQUIRED = (
    "api.gateway.app",
    "noventi.crm",
    "noventi.finance",
    "noventi.purchase",
    "noventi.inventory",
)


def main() -> int:
    failures: list[str] = []
    for name in REQUIRED:
        try:
            importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001 — smoke must surface any import break
            failures.append(f"{name}: {exc}")
    if failures:
        print("SMOKE_IMPORTS_FAIL", file=sys.stderr)
        for line in failures:
            print(line, file=sys.stderr)
        return 1
    print("SMOKE_IMPORTS_OK")
    for name in REQUIRED:
        print(f"  imported {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
