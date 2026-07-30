"""Ship PHX-G218: named *Details $ref composition on Error*.details."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "docs" / "api"

# --- auth ---
auth = API / "auth.openapi.yaml"
at = auth.read_text(encoding="utf-8")
old_details = """        details:
          type: object
          additionalProperties: true
          description: >
            Optional structured denial context (G202/G204/G210/G214). Known shapes
            include elevation fields[] and OIDC claim/role/amr/acr details
            (see Oidc*Details schemas). Other codes may add keys.
          properties:
            fields:
              type: array
              items:
                type: string
              description: Present for context-elevation denials (sorted field names).
            claims:
              type: array
              items:
                type: string
              description: GATEWAY_OIDC_REQUIRED_CLAIM_MISSING.
            role_claim:
              type: string
              description: GATEWAY_OIDC_ROLE_REQUIRED.
            mapped_roles:
              type: array
              items:
                type: string
            required_amr:
              type: array
              items:
                type: string
            present_amr:
              type: array
              items:
                type: string
            required_acr:
              type: array
              items:
                type: string
            present_acr:
              type: [string, "null"]
            mfa_enrollment_url:
              type: string
              format: uri
              description: OIDC amr/acr denial MFA enrollment hint (G214).
"""
new_details = """        details:
          description: >
            Optional structured denial context (G202/G204/G210/G214/G218). Known
            per-code shapes are composed via anyOf $ref to named *Details schemas;
            residual object keeps elevation fields[] catalog. Other codes may add keys.
          anyOf:
            - $ref: "#/components/schemas/OidcRequiredClaimMissingDetails"
            - $ref: "#/components/schemas/OidcRoleRequiredDetails"
            - $ref: "#/components/schemas/OidcAmrRequiredDetails"
            - $ref: "#/components/schemas/OidcAcrRequiredDetails"
            - type: object
              additionalProperties: true
              properties:
                fields:
                  type: array
                  items:
                    type: string
                  description: Present for context-elevation denials (sorted field names).
"""
if old_details not in at:
    raise SystemExit("auth details block not found")
at = at.replace(old_details, new_details, 1)
at = re.sub(r"^  version: 1\.3\.17\s*$", "  version: 1.3.18", at, count=1, flags=re.M)
auth.write_text(at, encoding="utf-8")
print("auth ok")

# --- marketplace ---
mp = API / "marketplace.openapi.yaml"
mt = mp.read_text(encoding="utf-8")
old_m = """        details:
          type: object
          additionalProperties: true
          description: >
            Optional structured denial context (G202/G204/G212). Known shapes
            include elevation fields[] and host-acquire package_key
            (HostAcquireAllowlistDenialDetails). Other codes may add keys.
          properties:
            fields:
              type: array
              items:
                type: string
              description: Present for context-elevation denials (sorted field names).
            package_key:
              type: string
              description: Host-acquire allowlist denial (G212).
"""
new_m = """        details:
          description: >
            Optional structured denial context (G202/G204/G212/G218). Known
            host-acquire shape is composed via anyOf $ref; residual object keeps
            elevation fields[] catalog. Other codes may add keys.
          anyOf:
            - $ref: "#/components/schemas/HostAcquireAllowlistDenialDetails"
            - type: object
              additionalProperties: true
              properties:
                fields:
                  type: array
                  items:
                    type: string
                  description: Present for context-elevation denials (sorted field names).
"""
if old_m not in mt:
    raise SystemExit("marketplace details block not found")
mt = mt.replace(old_m, new_m, 1)
# bump marketplace version
m = re.search(r"^  version: (\d+)\.(\d+)\.(\d+)\s*$", mt, flags=re.M)
if not m:
    raise SystemExit("marketplace version missing")
mt = re.sub(
    r"^  version: (\d+)\.(\d+)\.(\d+)\s*$",
    f"  version: {m.group(1)}.{m.group(2)}.{int(m.group(3)) + 1}",
    mt,
    count=1,
    flags=re.M,
)
mp.write_text(mt, encoding="utf-8")
print("marketplace ok", m.group(0), "->", int(m.group(3)) + 1)

# --- ops ---
ops = API / "ops.openapi.yaml"
ot = ops.read_text(encoding="utf-8")
old_o = """        details:
          type: object
          additionalProperties: true
          description: >
            Optional structured denial context (G197/G204). Known elevation shape
            includes fields[] for TERMINAL_CONTEXT_ELEVATION_DENIED on /context/echo;
            other codes may add additional keys.
          properties:
            fields:
              type: array
              items:
                type: string
              description: Present for context-elevation denials (sorted field names).
"""
new_o = """        details:
          description: >
            Optional structured denial context (G197/G204/G218). Known elevation
            shape is composed via anyOf $ref to ContextElevationDenialDetails;
            residual object allows other keys.
          anyOf:
            - $ref: "#/components/schemas/ContextElevationDenialDetails"
            - type: object
              additionalProperties: true
"""
if old_o not in ot:
    raise SystemExit("ops details block not found")
ot = ot.replace(old_o, new_o, 1)
ot = ot.replace("version: 1.0.34", "version: 1.0.35", 1)
ot = ot.replace("const: PHX-G216", "const: PHX-G218")
ot = ot.replace(
    "mount_parity_complete_error_details_description_key_honest",
    "mount_parity_complete_named_details_ref_composition_honest",
)
ot = ot.replace(
    "Remains false after PHX-G216 ErrorResponse.details description-key honesty (semantic remainder).",
    "Remains false after PHX-G218 named Details $ref composition honesty (semantic remainder).",
)
ops.write_text(ot, encoding="utf-8")
print("ops ok")

# --- terminal ---
term = API / "terminal.openapi.yaml"
tt = term.read_text(encoding="utf-8")
old_t = """        details:
          type: object
          additionalProperties: true
          description: >
            Optional structured denial context (G202/G204). Known elevation shape
            may include fields[] (TERMINAL_CONTEXT_ELEVATION_DENIED); other codes
            may add additional keys.
          properties:
            fields:
              type: array
              items:
                type: string
              description: Present for context-elevation denials (sorted field names).
"""
new_t = """        details:
          description: >
            Optional structured denial context (G202/G204/G218). Known elevation
            shape is composed via anyOf $ref to ContextElevationDenialDetails;
            residual object allows other keys.
          anyOf:
            - $ref: "#/components/schemas/ContextElevationDenialDetails"
            - type: object
              additionalProperties: true
"""
if old_t not in tt:
    raise SystemExit("terminal details block not found")
tt = tt.replace(old_t, new_t, 1)
tm = re.search(r"^  version: (\d+)\.(\d+)\.(\d+)\s*$", tt, flags=re.M)
if not tm:
    raise SystemExit("terminal version missing")
tt = re.sub(
    r"^  version: (\d+)\.(\d+)\.(\d+)\s*$",
    f"  version: {tm.group(1)}.{tm.group(2)}.{int(tm.group(3)) + 1}",
    tt,
    count=1,
    flags=re.M,
)
term.write_text(tt, encoding="utf-8")
print("terminal ok", tm.group(0), "->", int(tm.group(3)) + 1)

# inventory
inv = ROOT / "api" / "gateway" / "openapi_inventory_product.py"
it = inv.read_text(encoding="utf-8")
it = it.replace('"milestone": "PHX-G216"', '"milestone": "PHX-G218"')
it = it.replace(
    '"t0188_status": "mount_parity_complete_error_details_description_key_honest"',
    '"t0188_status": "mount_parity_complete_named_details_ref_composition_honest"',
)
needle = '    "error_details_description_key_honest_g216",\n'
insert = (
    '    "error_details_description_key_honest_g216",\n'
    '    "named_details_ref_composition_honest_g218",\n'
)
if "named_details_ref_composition_honest_g218" not in it:
    if needle not in it:
        raise SystemExit("inventory needle missing")
    it = it.replace(needle, insert, 1)
inv.write_text(it, encoding="utf-8")
print("inventory ok")
print("done")
