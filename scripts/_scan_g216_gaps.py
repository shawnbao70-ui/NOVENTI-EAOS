"""Scan OpenAPI for next charter-safe semantic gaps after G215."""
from __future__ import annotations

from pathlib import Path
import yaml

API = Path("docs/api")


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def bare_success() -> list[str]:
    gaps = []
    for path in sorted(API.glob("*.openapi.yaml")):
        spec = load(path)
        for route, methods in (spec.get("paths") or {}).items():
            if not isinstance(methods, dict):
                continue
            for method, op in methods.items():
                if method.startswith("x-") or not isinstance(op, dict):
                    continue
                for code, resp in (op.get("responses") or {}).items():
                    if str(code) not in ("200", "201"):
                        continue
                    content = (resp or {}).get("content") or {}
                    for _mt, body in content.items():
                        sch = (body or {}).get("schema") or {}
                        if "$ref" in sch:
                            continue
                        if (
                            sch.get("type") == "object"
                            and not sch.get("properties")
                            and sch.get("additionalProperties") is not False
                        ):
                            gaps.append(f"{path.name} {method.upper()} {route} {code}")
    return gaps


def single_enum_without_const() -> list[str]:
    gaps = []
    for path in sorted(API.glob("*.openapi.yaml")):
        spec = load(path)

        def walk(node, trail: str) -> None:
            if isinstance(node, dict):
                enum = node.get("enum")
                if (
                    isinstance(enum, list)
                    and len(enum) == 1
                    and "const" not in node
                    and node.get("type") in (None, "string", "integer", "boolean", "number")
                ):
                    gaps.append(f"{path.name} {trail} enum={enum}")
                for k, v in node.items():
                    walk(v, f"{trail}.{k}" if trail else str(k))
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{trail}[{i}]")

        walk(spec, "")
    return gaps


def details_oneOf_or_bare() -> list[str]:
    gaps = []
    for path in sorted(API.glob("*.openapi.yaml")):
        spec = load(path)
        schemas = (spec.get("components") or {}).get("schemas") or {}
        for name, sch in schemas.items():
            if not isinstance(sch, dict):
                continue
            props = sch.get("properties") or {}
            details = props.get("details")
            if not isinstance(details, dict):
                continue
            if details.get("additionalProperties") is True and not details.get("properties"):
                gaps.append(f"{path.name} {name}.details bare additionalProperties")
            if "oneOf" in details or "anyOf" in details:
                gaps.append(f"{path.name} {name}.details polymorphic")
            # named *Details schemas referenced?
            for k in ("oneOf", "anyOf", "allOf"):
                if k in details:
                    gaps.append(f"{path.name} {name}.details {k}")
    return gaps


def named_details_schemas() -> list[str]:
    out = []
    for path in sorted(API.glob("*.openapi.yaml")):
        spec = load(path)
        schemas = (spec.get("components") or {}).get("schemas") or {}
        for name, sch in schemas.items():
            if name.endswith("Details") and isinstance(sch, dict):
                props = list((sch.get("properties") or {}).keys())
                out.append(f"{path.name} {name} props={props}")
    return out


print("=== bare_success ===")
for g in bare_success():
    print(g)
print("=== single_enum_without_const ===")
for g in single_enum_without_const()[:40]:
    print(g)
print("count", len(single_enum_without_const()))
print("=== details bare ===")
for g in details_oneOf_or_bare()[:40]:
    print(g)
print("=== named Details ===")
for g in named_details_schemas():
    print(g)
