"""PHX-G210: OIDC known details per-code schemas + inventory tip."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"
INV = ROOT / "api" / "gateway" / "openapi_inventory_product.py"

SCHEMAS = """\
    OidcRequiredClaimMissingDetails:
      type: object
      additionalProperties: false
      description: >
        Known details for GATEWAY_OIDC_REQUIRED_CLAIM_MISSING (live OIDC
        required-claims assert). PHX-G210 per-code honesty.
      required: [claims]
      properties:
        claims:
          type: array
          items:
            type: string
          description: Missing required id_token claim names.
    OidcRoleRequiredDetails:
      type: object
      additionalProperties: false
      description: >
        Known details for GATEWAY_OIDC_ROLE_REQUIRED when mapped roles are
        required but empty. PHX-G210 per-code honesty.
      required: [role_claim, mapped_roles]
      properties:
        role_claim:
          type: string
        mapped_roles:
          type: array
          items:
            type: string
          description: Always empty for this denial code.
    OidcAmrRequiredDetails:
      type: object
      additionalProperties: true
      description: >
        Known details for GATEWAY_OIDC_AMR_REQUIRED. May include MFA
        enrollment hint keys from live emit. PHX-G210.
      required: [required_amr, present_amr]
      properties:
        required_amr:
          type: array
          items:
            type: string
        present_amr:
          type: array
          items:
            type: string
    OidcAcrRequiredDetails:
      type: object
      additionalProperties: true
      description: >
        Known details for GATEWAY_OIDC_ACR_REQUIRED. May include MFA
        enrollment hint keys from live emit. PHX-G210.
      required: [required_acr]
      properties:
        required_acr:
          type: array
          items:
            type: string
        present_acr:
          type: [string, "null"]
"""

DETAILS_OLD = """\
        details:
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
          description: >
            Optional structured denial context from live gateway emit
            (KernelError.details / elevation fields). PHX-G202 inventory.
"""

DETAILS_NEW = """\
        details:
          type: object
          additionalProperties: true
          description: >
            Optional structured denial context (G202/G204/G210). Known shapes
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
"""


def main() -> None:
    auth = AUTH.read_text(encoding="utf-8")
    if "OidcRequiredClaimMissingDetails:" in auth:
        print("schemas already present")
    else:
        if "    ErrorResponse:\n" not in auth:
            raise SystemExit("ErrorResponse marker missing")
        auth = auth.replace("    ErrorResponse:\n", SCHEMAS + "    ErrorResponse:\n", 1)
    if DETAILS_OLD not in auth:
        raise SystemExit("details block missing or already changed")
    auth = auth.replace(DETAILS_OLD, DETAILS_NEW, 1)
    auth = auth.replace("  version: 1.3.15\n", "  version: 1.3.16\n", 1)
    AUTH.write_text(auth, encoding="utf-8")
    print("patched auth.openapi.yaml")

    ops = OPS.read_text(encoding="utf-8")
    ops = ops.replace("version: 1.0.30", "version: 1.0.31", 1)
    ops = ops.replace(
        "t0188_status=mount_parity_complete_elevation_details_code_shape_honest",
        "t0188_status=mount_parity_complete_oidc_details_code_shapes_honest",
        1,
    )
    ops = ops.replace("const: PHX-G208", "const: PHX-G210", 1)
    ops = ops.replace(
        "Remains false after PHX-G208 elevation details per-code shape honesty (semantic remainder).",
        "Remains false after PHX-G210 OIDC details per-code shapes honesty (semantic remainder).",
        1,
    )
    ops = ops.replace(
        "const: mount_parity_complete_elevation_details_code_shape_honest",
        "const: mount_parity_complete_oidc_details_code_shapes_honest",
        1,
    )
    OPS.write_text(ops, encoding="utf-8")
    print("patched ops")

    inv = INV.read_text(encoding="utf-8")
    if "oidc_details_code_shapes_honest_g210" not in inv:
        inv = inv.replace(
            '"elevation_details_code_shape_honest_g208",\n',
            '"elevation_details_code_shape_honest_g208",\n'
            '    "oidc_details_code_shapes_honest_g210",\n',
            1,
        )
    inv = inv.replace('"milestone": "PHX-G208"', '"milestone": "PHX-G210"', 1)
    inv = inv.replace(
        '"t0188_status": "mount_parity_complete_elevation_details_code_shape_honest"',
        '"t0188_status": "mount_parity_complete_oidc_details_code_shapes_honest"',
        1,
    )
    INV.write_text(inv, encoding="utf-8")
    print("patched inventory")


if __name__ == "__main__":
    main()
