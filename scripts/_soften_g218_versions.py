"""Bump version sets for auth/marketplace/terminal after G218."""
from pathlib import Path

edits = [
    (
        "tests/contracts/test_api_gateway_g185_openapi_auth_permission_product_posture_schema.py",
        "'1.3.17'}",
        "'1.3.17', '1.3.18'}",
    ),
    (
        "tests/contracts/test_api_gateway_g187_openapi_oidc_login_product_posture_schema.py",
        "'1.3.17'}",
        "'1.3.17', '1.3.18'}",
    ),
    (
        "tests/contracts/test_api_gateway_g188_openapi_jwt_status_body_parity.py",
        "'1.3.17'}",
        "'1.3.17', '1.3.18'}",
    ),
    (
        "tests/contracts/test_api_gateway_g189_openapi_idp_status_body_parity.py",
        "'1.3.17'}",
        "'1.3.17', '1.3.18'}",
    ),
    (
        "tests/contracts/test_api_gateway_g190_openapi_oidc_status_body_parity.py",
        '"1.3.17"}',
        '"1.3.17", "1.3.18"}',
    ),
    (
        "tests/contracts/test_api_gateway_g202_openapi_errorbody_details_inventory.py",
        '"auth.openapi.yaml": {"1.3.14", "1.3.15", "1.3.16", "1.3.17"},',
        '"auth.openapi.yaml": {"1.3.14", "1.3.15", "1.3.16", "1.3.17", "1.3.18"},',
    ),
    (
        "tests/contracts/test_api_gateway_g198_openapi_terminal_extension_list_response.py",
        '{"1.1.5", "1.1.6", "1.1.7", "1.1.8", "1.1.9"}',
        '{"1.1.5", "1.1.6", "1.1.7", "1.1.8", "1.1.9", "1.1.10"}',
    ),
    (
        "tests/contracts/test_api_gateway_g199_openapi_terminal_extension_invoke_response.py",
        '{"1.1.6", "1.1.7", "1.1.8", "1.1.9"}',
        '{"1.1.6", "1.1.7", "1.1.8", "1.1.9", "1.1.10"}',
    ),
    (
        "tests/contracts/test_api_gateway_g206_openapi_single_enum_const.py",
        '{"1.1.8", "1.1.9"}',
        '{"1.1.8", "1.1.9", "1.1.10"}',
    ),
    (
        "tests/contracts/test_api_gateway_g208_openapi_elevation_details_code_shape.py",
        '((TERMINAL, {"1.1.9"}), (OPS, {"1.0.30", "1.0.31"}))',
        '((TERMINAL, {"1.1.9", "1.1.10"}), (OPS, {"1.0.30", "1.0.31", "1.0.32", "1.0.33", "1.0.34", "1.0.35"}))',
    ),
]

for rel, old, new in edits:
    path = Path(rel)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print("SKIP", rel, old)
        continue
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("ok", rel)
print("done")
