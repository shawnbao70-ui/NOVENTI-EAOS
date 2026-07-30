"""Find live gateway details keys vs OpenAPI Error*.details properties."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import yaml

ROOT = Path(".")
API = ROOT / "docs" / "api"
GW = ROOT / "api" / "gateway"

# Collect keys from details={"k": ...} and details.update patterns via regex
src = "\n".join(p.read_text(encoding="utf-8") for p in GW.rglob("*.py"))
keys = set(re.findall(r'details\s*=\s*\{([^}]+)\}', src, flags=re.S))
literal_keys = set()
for block in keys:
    for m in re.finditer(r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']\s*:', block):
        literal_keys.add(m.group(1))

# Also look for details.update({...}) and detail dict builders
for m in re.finditer(r'details\.update\((\{[^}]+\})\)', src):
    for k in re.finditer(r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']\s*:', m.group(1)):
        literal_keys.add(k.group(1))

print("live_details_literal_keys", sorted(literal_keys))

# Catalog documented Error*/ErrorBody details properties
doc_keys: dict[str, set[str]] = {}
for path in sorted(API.glob("*.openapi.yaml")):
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    schemas = (spec.get("components") or {}).get("schemas") or {}
    for name in ("ErrorBody", "ErrorResponse"):
        sch = schemas.get(name)
        if not isinstance(sch, dict):
            continue
        details = (sch.get("properties") or {}).get("details") or {}
        props = set((details.get("properties") or {}).keys())
        if props:
            doc_keys[f"{path.name}:{name}"] = props

all_doc = set().union(*doc_keys.values()) if doc_keys else set()
print("documented_union", sorted(all_doc))
print("live_not_in_any_error_details", sorted(literal_keys - all_doc))

# Duplicate YAML keys under details
print("\n=== duplicate description under details ===")
for path in sorted(API.glob("*.openapi.yaml")):
    text = path.read_text(encoding="utf-8")
    # crude: count "description:" under a details block is hard; check known pattern
    if re.search(r"details:\n(?:.*\n){0,20}?properties:\n(?:.*\n){0,30}?description:", text):
        # properties then another description sibling - suspicious
        if text.count("details:") >= 1:
            # find blocks with two description under details before next top-level key at same indent
            pass

# Find schemas with two description keys by parsing lines
for path in sorted(API.glob("*.openapi.yaml")):
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        if re.match(r"^ {8}details:\s*$", lines[i]) or re.match(r"^ {10}details:\s*$", lines[i]):
            base = len(lines[i]) - len(lines[i].lstrip(" "))
            descs = 0
            j = i + 1
            while j < len(lines):
                if lines[j].strip() and not lines[j].startswith(" " * (base + 1)) and not lines[j].startswith(" "):
                    break
                cur = len(lines[j]) - len(lines[j].lstrip(" ")) if lines[j].strip() else 999
                if lines[j].strip().startswith("description:") and cur == base + 2:
                    descs += 1
                if cur <= base and lines[j].strip():
                    break
                j += 1
            if descs >= 2:
                print(f"{path.name} details has {descs} sibling description keys near L{i+1}")
        i += 1

# Status endpoints missing schema refs?
print("\n=== status ops without $ref success schema ===")
for path in sorted(API.glob("*.openapi.yaml")):
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    for route, methods in (spec.get("paths") or {}).items():
        if "status" not in route:
            continue
        if not isinstance(methods, dict):
            continue
        for method, op in methods.items():
            if method.startswith("x-") or not isinstance(op, dict):
                continue
            resp = ((op.get("responses") or {}).get("200") or {})
            content = (resp.get("content") or {}).get("application/json") or {}
            sch = content.get("schema") or {}
            if not sch:
                print(f"{path.name} {method.upper()} {route} no schema")
            elif "$ref" not in sch and not sch.get("properties") and not sch.get("allOf"):
                print(f"{path.name} {method.upper()} {route} weak schema {sch}")
