"""Deep scan for remaining inventable OpenAPI honesty debt."""
from __future__ import annotations

from pathlib import Path

import yaml

API = Path("docs/api")
INTENTIONAL_TOP = {
    "WebauthnAuthenticatorAttestationResponse",
    "WebauthnPublicKeyCredential",
    "WebauthnRegisterVerifyRequest",
    "IdpJwksKey",
    "IdpJwksDocument",
}
# Nested free-form property names that are intentional by prior ADRs
INTENTIONAL_PROP = {
    "value",  # MemoryEntry
    "payload",  # EventEnvelope etc
    "attributes",
    "details",  # Knowledge / ErrorBody residual
    "state",  # Twin
    "config",
    "metadata",
    "extensions",
    "context",
    "input",
    "output",
    "params",
    "arguments",
    "data",  # sometimes free-form — flag but classify
}


def walk(node, path: str, hits: list[str]) -> None:
    if not isinstance(node, dict):
        return
    if node.get("type") == "object" and "properties" in node:
        ap = node.get("additionalProperties")
        if ap is None and not any(k in node for k in ("allOf", "anyOf", "oneOf", "$ref")):
            hits.append(f"MISSING_AP {path}")
        elif ap is True:
            hits.append(f"AP_TRUE {path}")
    for k, v in node.items():
        if k in ("example", "examples", "description"):
            continue
        if isinstance(v, dict):
            walk(v, f"{path}.{k}", hits)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    walk(item, f"{path}[{i}]", hits)


def main() -> None:
    missing_top = []
    ap_true_top = []
    anon_inline = []
    for path in sorted(API.glob("*.openapi.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        schemas = (doc.get("components") or {}).get("schemas") or {}
        for name, schema in schemas.items():
            if not isinstance(schema, dict):
                continue
            if schema.get("type") == "object" and "additionalProperties" not in schema:
                if not any(k in schema for k in ("allOf", "anyOf", "oneOf")):
                    missing_top.append(f"{path.name}:{name}")
            if schema.get("additionalProperties") is True:
                tag = "INTENTIONAL" if name in INTENTIONAL_TOP else "CHECK"
                ap_true_top.append(f"{tag} {path.name}:{name}")
            # nested property objects
            props = schema.get("properties") or {}
            for pname, pschema in props.items():
                if not isinstance(pschema, dict):
                    continue
                # resolve simple inline object
                if pschema.get("type") == "object" and "$ref" not in pschema:
                    if "additionalProperties" not in pschema and not any(
                        k in pschema for k in ("allOf", "anyOf", "oneOf")
                    ):
                        anon_inline.append(f"{path.name}:{name}.{pname}")
                    elif pschema.get("additionalProperties") is True:
                        kind = "intentional_prop" if pname in INTENTIONAL_PROP else "check_prop"
                        anon_inline.append(f"{kind} {path.name}:{name}.{pname} AP=true")
        # also scan path response inline schemas lightly via walk
        hits: list[str] = []
        walk(doc.get("paths") or {}, f"{path.name}:paths", hits)
        for h in hits:
            if "MISSING_AP" in h and "Error" not in h:
                anon_inline.append(h)

    print("=== missing AP top-level ===", len(missing_top))
    for x in missing_top:
        print(x)
    print("=== AP=true top-level ===", len(ap_true_top))
    for x in ap_true_top:
        print(x)
    print("=== nested/inline interesting ===", len(anon_inline))
    for x in anon_inline[:100]:
        print(x)
    if len(anon_inline) > 100:
        print(f"... +{len(anon_inline)-100}")


if __name__ == "__main__":
    main()
