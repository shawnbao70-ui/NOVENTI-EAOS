from pathlib import Path
import yaml

API = Path("docs/api")
gaps = []
for path in sorted(API.glob("*.openapi.yaml")):
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
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
print("bare_success_objects", gaps)
