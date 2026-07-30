"""PHX-G212: host-acquire package_key details schema + inventory tip."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET = ROOT / "docs" / "api" / "marketplace.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"
INV = ROOT / "api" / "gateway" / "openapi_inventory_product.py"

SCHEMA = """\
    HostAcquireAllowlistDenialDetails:
      type: object
      additionalProperties: false
      description: >
        Known details when host-acquire rejects a listing whose package_key
        is outside the first-party allowlist (live emit uses
        COMMON_VALIDATION_FAILED + details.package_key). PHX-G212.
      required: [package_key]
      properties:
        package_key:
          type: string
          minLength: 1
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
"""

DETAILS_NEW = """\
        details:
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


def main() -> None:
    text = MARKET.read_text(encoding="utf-8")
    if "HostAcquireAllowlistDenialDetails:" not in text:
        if "    ErrorBody:\n" not in text:
            raise SystemExit("ErrorBody missing")
        text = text.replace("    ErrorBody:\n", SCHEMA + "    ErrorBody:\n", 1)
    if DETAILS_OLD not in text:
        raise SystemExit("details block missing")
    text = text.replace(DETAILS_OLD, DETAILS_NEW, 1)
    text = text.replace("  version: 1.2.7\n", "  version: 1.2.8\n", 1)
    MARKET.write_text(text, encoding="utf-8")
    print("patched marketplace")

    ops = OPS.read_text(encoding="utf-8")
    ops = ops.replace("version: 1.0.31", "version: 1.0.32", 1)
    ops = ops.replace(
        "t0188_status=mount_parity_complete_oidc_details_code_shapes_honest",
        "t0188_status=mount_parity_complete_host_acquire_details_code_shape_honest",
        1,
    )
    ops = ops.replace("const: PHX-G210", "const: PHX-G212", 1)
    ops = ops.replace(
        "Remains false after PHX-G210 OIDC details per-code shapes honesty (semantic remainder).",
        "Remains false after PHX-G212 host-acquire details per-code shape honesty (semantic remainder).",
        1,
    )
    ops = ops.replace(
        "const: mount_parity_complete_oidc_details_code_shapes_honest",
        "const: mount_parity_complete_host_acquire_details_code_shape_honest",
        1,
    )
    OPS.write_text(ops, encoding="utf-8")
    print("patched ops")

    inv = INV.read_text(encoding="utf-8")
    if "host_acquire_details_code_shape_honest_g212" not in inv:
        inv = inv.replace(
            '"oidc_details_code_shapes_honest_g210",\n',
            '"oidc_details_code_shapes_honest_g210",\n'
            '    "host_acquire_details_code_shape_honest_g212",\n',
            1,
        )
    inv = inv.replace('"milestone": "PHX-G210"', '"milestone": "PHX-G212"', 1)
    inv = inv.replace(
        '"t0188_status": "mount_parity_complete_oidc_details_code_shapes_honest"',
        '"t0188_status": "mount_parity_complete_host_acquire_details_code_shape_honest"',
        1,
    )
    INV.write_text(inv, encoding="utf-8")
    print("patched inventory")


if __name__ == "__main__":
    main()
