"""Scan residual OpenAPI honesty gaps after G217."""
from __future__ import annotations

import re
from pathlib import Path
import yaml

API = Path("docs/api")


def dup_desc() -> list[str]:
    out = []
    for path in sorted(API.glob("*.openapi.yaml")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if not re.match(r"^ {8,10}details:\s*$", line):
                continue
            base = len(line) - len(line.lstrip(" "))
            descs = 0
            for j in range(i + 1, len(lines)):
                if not lines[j].strip():
                    continue
                cur = len(lines[j]) - len(lines[j].lstrip(" "))
                if cur <= base:
                    break
                if lines[j].strip().startswith("description:") and cur == base + 2:
                    descs += 1
            if descs >= 2:
                out.append(f"{path.name}:L{i+1} descs={descs}")
    return out


def error_details_without_properties() -> list[str]:
    out = []
    for path in sorted(API.glob("*.openapi.yaml")):
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        schemas = (spec.get("components") or {}).get("schemas") or {}
        for name in ("ErrorBody", "ErrorResponse"):
            sch = schemas.get(name)
            if not isinstance(sch, dict):
                continue
            details = (sch.get("properties") or {}).get("details")
            if not isinstance(details, dict):
                out.append(f"{path.name} {name} missing details")
                continue
            if details.get("additionalProperties") is True and not details.get(
                "properties"
            ):
                out.append(f"{path.name} {name}.details bare")
    return out


def named_details_unrefed() -> list[str]:
    out = []
    for path in sorted(API.glob("*.openapi.yaml")):
        text = path.read_text(encoding="utf-8")
        spec = yaml.safe_load(text)
        schemas = (spec.get("components") or {}).get("schemas") or {}
        for name in schemas:
            if not name.endswith("Details"):
                continue
            # referenced anywhere?
            if f"#/components/schemas/{name}" not in text.replace(
                f"{name}:", "", 1
            ):
                # crude: count occurrences of name
                if text.count(name) <= 1:
                    out.append(f"{path.name} {name} unreferenced")
    return out


print("dup_desc", dup_desc())
print("bare_details", error_details_without_properties())
print("unrefed_Details", named_details_unrefed())
