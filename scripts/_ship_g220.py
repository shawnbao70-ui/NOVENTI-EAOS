"""Ship PHX-G220: cross-domain elevation details anyOf $ref composition."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "docs" / "api"

ELEVATION_SCHEMA = """    ContextElevationDenialDetails:
      type: object
      additionalProperties: false
      description: >
        Known details shape for code TERMINAL_CONTEXT_ELEVATION_DENIED
        (live /context/echo elevation deny). PHX-G208/G220 per-code honesty;
        other error codes may use different details keys.
      required: [fields]
      properties:
        fields:
          type: array
          items:
            type: string
          description: Sorted denied elevation field names.
"""

NEW_DETAILS = """        details:
          description: >
            Optional structured denial context (G202/G204/G216/G220). Known
            elevation shape is composed via anyOf $ref to
            ContextElevationDenialDetails; residual object allows other keys.
          anyOf:
            - $ref: "#/components/schemas/ContextElevationDenialDetails"
            - type: object
              additionalProperties: true
"""

# Match fields-only details blocks (G216 merged description or older variants).
DETAILS_RE = re.compile(
    r"        details:\n"
    r"          type: object\n"
    r"          additionalProperties: true\n"
    r"          description: >\n"
    r"(?:            .*\n)+?"
    r"          properties:\n"
    r"            fields:\n"
    r"              type: array\n"
    r"              items:\n"
    r"                type: string\n"
    r"              description: Present for context-elevation denials \(sorted field names\)\.\n",
    re.M,
)

TARGETS = (
    "ai.openapi.yaml",
    "brain.openapi.yaml",
    "event.openapi.yaml",
    "identity.openapi.yaml",
    "knowledge.openapi.yaml",
    "organization.openapi.yaml",
    "package.openapi.yaml",
    "permission.openapi.yaml",
    "platform.openapi.yaml",
    "workflow.openapi.yaml",
)


def bump_version(text: str) -> str:
    m = re.search(r"^  version: (\d+)\.(\d+)\.(\d+)\s*$", text, flags=re.M)
    if not m:
        raise SystemExit("version missing")
    return re.sub(
        r"^  version: (\d+)\.(\d+)\.(\d+)\s*$",
        f"  version: {m.group(1)}.{m.group(2)}.{int(m.group(3)) + 1}",
        text,
        count=1,
        flags=re.M,
    )


for name in TARGETS:
    path = API / name
    text = path.read_text(encoding="utf-8")
    new_text, n = DETAILS_RE.subn(NEW_DETAILS, text)
    if n < 1:
        raise SystemExit(f"{name}: no details blocks replaced")
    if "ContextElevationDenialDetails:" not in new_text:
        # Insert before first ErrorBody or ErrorResponse schema
        m = re.search(r"^    (ErrorBody|ErrorResponse):\n", new_text, flags=re.M)
        if not m:
            raise SystemExit(f"{name}: no ErrorBody/ErrorResponse to anchor schema")
        new_text = new_text[: m.start()] + ELEVATION_SCHEMA + new_text[m.start() :]
    new_text = bump_version(new_text)
    path.write_text(new_text, encoding="utf-8")
    print(f"updated {name} replacements={n}")

# inventory
inv = ROOT / "api" / "gateway" / "openapi_inventory_product.py"
it = inv.read_text(encoding="utf-8")
it = it.replace('"milestone": "PHX-G218"', '"milestone": "PHX-G220"')
it = it.replace(
    '"t0188_status": "mount_parity_complete_named_details_ref_composition_honest"',
    '"t0188_status": "mount_parity_complete_cross_domain_elevation_details_ref_honest"',
)
needle = '    "named_details_ref_composition_honest_g218",\n'
insert = (
    '    "named_details_ref_composition_honest_g218",\n'
    '    "cross_domain_elevation_details_ref_honest_g220",\n'
)
if "cross_domain_elevation_details_ref_honest_g220" not in it:
    if needle not in it:
        raise SystemExit("inventory needle missing")
    it = it.replace(needle, insert, 1)
inv.write_text(it, encoding="utf-8")
print("inventory ok")

# ops
ops = API / "ops.openapi.yaml"
ot = ops.read_text(encoding="utf-8")
ot = ot.replace("version: 1.0.35", "version: 1.0.36", 1)
ot = ot.replace("const: PHX-G218", "const: PHX-G220")
ot = ot.replace(
    "mount_parity_complete_named_details_ref_composition_honest",
    "mount_parity_complete_cross_domain_elevation_details_ref_honest",
)
ot = ot.replace(
    "Remains false after PHX-G218 named Details $ref composition honesty (semantic remainder).",
    "Remains false after PHX-G220 cross-domain elevation details $ref honesty (semantic remainder).",
)
ops.write_text(ot, encoding="utf-8")
print("ops ok")
print("done")
