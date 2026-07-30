"""PHX-G214: OIDC MFA enrollment URL details honesty + inventory tip."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"
INV = ROOT / "api" / "gateway" / "openapi_inventory_product.py"

AMR_OLD = """\
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
"""

AMR_NEW = """\
    OidcAmrRequiredDetails:
      type: object
      additionalProperties: true
      description: >
        Known details for GATEWAY_OIDC_AMR_REQUIRED. When MFA enrollment URL
        is configured, live emit also includes mfa_enrollment_url. PHX-G214.
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
        mfa_enrollment_url:
          type: string
          format: uri
          description: Present when EAOS_OIDC_MFA_ENROLLMENT_URL is configured.
"""

ACR_OLD = """\
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

ACR_NEW = """\
    OidcAcrRequiredDetails:
      type: object
      additionalProperties: true
      description: >
        Known details for GATEWAY_OIDC_ACR_REQUIRED. When MFA enrollment URL
        is configured, live emit also includes mfa_enrollment_url. PHX-G214.
      required: [required_acr]
      properties:
        required_acr:
          type: array
          items:
            type: string
        present_acr:
          type: [string, "null"]
        mfa_enrollment_url:
          type: string
          format: uri
          description: Present when EAOS_OIDC_MFA_ENROLLMENT_URL is configured.
"""


def main() -> None:
    auth = AUTH.read_text(encoding="utf-8")
    if AMR_OLD not in auth or ACR_OLD not in auth:
        raise SystemExit("AMR/ACR blocks missing or already changed")
    auth = auth.replace(AMR_OLD, AMR_NEW, 1).replace(ACR_OLD, ACR_NEW, 1)
    if "mfa_enrollment_url:" not in auth.split("ErrorResponse:")[1]:
        # add to ErrorResponse.details.properties after present_acr
        needle = """\
            present_acr:
              type: [string, "null"]
"""
        insert = """\
            present_acr:
              type: [string, "null"]
            mfa_enrollment_url:
              type: string
              format: uri
              description: OIDC amr/acr denial MFA enrollment hint (G214).
"""
        # only replace inside ErrorResponse details — first present_acr in ErrorResponse block
        # safer: replace the details description line and present_acr that follows claims block
        err_marker = "Optional structured denial context (G202/G204/G210)."
        if err_marker not in auth:
            raise SystemExit("ErrorResponse details description missing")
        auth = auth.replace(
            err_marker,
            "Optional structured denial context (G202/G204/G210/G214).",
            1,
        )
        # Find ErrorResponse details present_acr — appears after mapped_roles in details props
        details_present = """\
            present_acr:
              type: [string, "null"]
        correlation_id:
"""
        details_present_new = """\
            present_acr:
              type: [string, "null"]
            mfa_enrollment_url:
              type: string
              format: uri
              description: OIDC amr/acr denial MFA enrollment hint (G214).
        correlation_id:
"""
        if details_present not in auth:
            raise SystemExit("ErrorResponse details present_acr trailer missing")
        auth = auth.replace(details_present, details_present_new, 1)
    auth = auth.replace("  version: 1.3.16\n", "  version: 1.3.17\n", 1)
    AUTH.write_text(auth, encoding="utf-8")
    print("patched auth")

    ops = OPS.read_text(encoding="utf-8")
    ops = ops.replace("version: 1.0.32", "version: 1.0.33", 1)
    ops = ops.replace(
        "t0188_status=mount_parity_complete_host_acquire_details_code_shape_honest",
        "t0188_status=mount_parity_complete_oidc_mfa_enrollment_details_honest",
        1,
    )
    ops = ops.replace("const: PHX-G212", "const: PHX-G214", 1)
    ops = ops.replace(
        "Remains false after PHX-G212 host-acquire details per-code shape honesty (semantic remainder).",
        "Remains false after PHX-G214 OIDC MFA enrollment details honesty (semantic remainder).",
        1,
    )
    ops = ops.replace(
        "const: mount_parity_complete_host_acquire_details_code_shape_honest",
        "const: mount_parity_complete_oidc_mfa_enrollment_details_honest",
        1,
    )
    OPS.write_text(ops, encoding="utf-8")
    print("patched ops")

    inv = INV.read_text(encoding="utf-8")
    if "oidc_mfa_enrollment_details_honest_g214" not in inv:
        inv = inv.replace(
            '"host_acquire_details_code_shape_honest_g212",\n',
            '"host_acquire_details_code_shape_honest_g212",\n'
            '    "oidc_mfa_enrollment_details_honest_g214",\n',
            1,
        )
    inv = inv.replace('"milestone": "PHX-G212"', '"milestone": "PHX-G214"', 1)
    inv = inv.replace(
        '"t0188_status": "mount_parity_complete_host_acquire_details_code_shape_honest"',
        '"t0188_status": "mount_parity_complete_oidc_mfa_enrollment_details_honest"',
        1,
    )
    INV.write_text(inv, encoding="utf-8")
    print("patched inventory")


if __name__ == "__main__":
    main()
