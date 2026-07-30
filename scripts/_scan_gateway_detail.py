"""Scan GatewayDetailError and other structural honesty gaps."""
from __future__ import annotations

from pathlib import Path

import yaml

API = Path("docs/api")
for path in sorted(API.glob("*.openapi.yaml")):
    schemas = yaml.safe_load(path.read_text(encoding="utf-8")).get("components", {}).get(
        "schemas", {}
    )
    for name in ("GatewayDetailError", "ErrorBody", "ErrorResponse"):
        s = schemas.get(name)
        if not isinstance(s, dict):
            continue
        print(f"{path.name}:{name}: ap={s.get('additionalProperties')!r}")

# requestBody anonymous objects missing AP
print("--- anon requestBody ---")
for path in sorted(API.glob("*.openapi.yaml")):
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    for pth, item in (doc.get("paths") or {}).items():
        for method, op in item.items():
            if method.startswith("x") or not isinstance(op, dict):
                continue
            rb = ((op.get("requestBody") or {}).get("content") or {}).get(
                "application/json", {}
            ).get("schema")
            if not isinstance(rb, dict):
                continue
            if "$ref" in rb:
                continue
            if rb.get("type") == "object" and "additionalProperties" not in rb:
                if not any(k in rb for k in ("allOf", "anyOf", "oneOf")):
                    print(f"MISSING {path.name} {method.upper()} {pth}")
            elif rb.get("additionalProperties") is True:
                print(f"AP_TRUE {path.name} {method.upper()} {pth}")
