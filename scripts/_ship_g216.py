"""Ship PHX-G216: ErrorResponse.details duplicate-description honesty."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "docs" / "api"

TARGETS = (
    "organization.openapi.yaml",
    "permission.openapi.yaml",
    "platform.openapi.yaml",
    "workflow.openapi.yaml",
)

# Remove the trailing duplicate description block that overwrites the known-shape one.
DUP = re.compile(
    r"(?P<head>details:\n"
    r"          type: object\n"
    r"          additionalProperties: true\n"
    r"          description: >\n"
    r"            Optional structured denial context \(G202/G204\)\. Known elevation shape\n"
    r"            may include fields\[\] \(TERMINAL_CONTEXT_ELEVATION_DENIED\); other codes\n"
    r"            may add additional keys\.\n"
    r"          properties:\n"
    r"            fields:\n"
    r"              type: array\n"
    r"              items:\n"
    r"                type: string\n"
    r"              description: Present for context-elevation denials \(sorted field names\)\.\n)"
    r"          description: >\n"
    r"            Optional structured denial context from live gateway emit\n"
    r"            \(KernelError\.details / elevation fields\)\. PHX-G202 inventory\.\n",
    re.M,
)

MERGED_TAIL = (
    "          description: >\n"
    "            Optional structured denial context (G202/G204/G216). Known elevation\n"
    "            shape may include fields[] (TERMINAL_CONTEXT_ELEVATION_DENIED);\n"
    "            mirrors live KernelError.details emit. Duplicate sibling description\n"
    "            keys removed so known-shape text is not overwritten at parse time.\n"
)

# Better: keep single description after additionalProperties and before properties
REPLACE = re.compile(
    r"details:\n"
    r"          type: object\n"
    r"          additionalProperties: true\n"
    r"          description: >\n"
    r"            Optional structured denial context \(G202/G204\)\. Known elevation shape\n"
    r"            may include fields\[\] \(TERMINAL_CONTEXT_ELEVATION_DENIED\); other codes\n"
    r"            may add additional keys\.\n"
    r"          properties:\n"
    r"            fields:\n"
    r"              type: array\n"
    r"              items:\n"
    r"                type: string\n"
    r"              description: Present for context-elevation denials \(sorted field names\)\.\n"
    r"          description: >\n"
    r"            Optional structured denial context from live gateway emit\n"
    r"            \(KernelError\.details / elevation fields\)\. PHX-G202 inventory\.\n",
    re.M,
)

NEW = (
    "details:\n"
    "          type: object\n"
    "          additionalProperties: true\n"
    "          description: >\n"
    "            Optional structured denial context (G202/G204/G216). Known elevation\n"
    "            shape may include fields[] (TERMINAL_CONTEXT_ELEVATION_DENIED);\n"
    "            mirrors live KernelError.details emit. Single description key only\n"
    "            so known-shape text is not overwritten at YAML parse time.\n"
    "          properties:\n"
    "            fields:\n"
    "              type: array\n"
    "              items:\n"
    "                type: string\n"
    "              description: Present for context-elevation denials (sorted field names).\n"
)

for name in TARGETS:
    path = API / name
    text = path.read_text(encoding="utf-8")
    new_text, n = REPLACE.subn(NEW, text, count=1)
    if n != 1:
        raise SystemExit(f"{name}: expected 1 replacement, got {n}")
    # bump info.version patch if present
    def bump(m: re.Match[str]) -> str:
        major, minor, patch = m.group(1), m.group(2), int(m.group(3))
        return f"  version: {major}.{minor}.{patch + 1}"

    new_text2, bn = re.subn(
        r"^  version: (\d+)\.(\d+)\.(\d+)\s*$", bump, new_text, count=1, flags=re.M
    )
    if bn != 1:
        raise SystemExit(f"{name}: version bump failed")
    path.write_text(new_text2, encoding="utf-8")
    print("updated", name)

# inventory
inv = ROOT / "api" / "gateway" / "openapi_inventory_product.py"
it = inv.read_text(encoding="utf-8")
it = it.replace(
    '"milestone": "PHX-G214"',
    '"milestone": "PHX-G216"',
)
it = it.replace(
    '"t0188_status": "mount_parity_complete_oidc_mfa_enrollment_details_honest"',
    '"t0188_status": "mount_parity_complete_error_details_description_key_honest"',
)
needle = '    "oidc_mfa_enrollment_details_honest_g214",\n'
insert = (
    '    "oidc_mfa_enrollment_details_honest_g214",\n'
    '    "error_details_description_key_honest_g216",\n'
)
if insert.strip() not in it:
    if needle not in it:
        raise SystemExit("inventory needle missing")
    it = it.replace(needle, insert, 1)
inv.write_text(it, encoding="utf-8")
print("inventory ok")

# ops
ops = API / "ops.openapi.yaml"
ot = ops.read_text(encoding="utf-8")
ot = ot.replace("version: 1.0.33", "version: 1.0.34", 1)
ot = ot.replace(
    "t0188_status=mount_parity_complete_oidc_mfa_enrollment_details_honest",
    "t0188_status=mount_parity_complete_error_details_description_key_honest",
)
ot = ot.replace("const: PHX-G214", "const: PHX-G216")
# also update example/const for t0188 if present
ot = ot.replace(
    "mount_parity_complete_oidc_mfa_enrollment_details_honest",
    "mount_parity_complete_error_details_description_key_honest",
)
ops.write_text(ot, encoding="utf-8")
print("ops ok")
print("done")
