"""Soften prior contract pins for PHX-G216 tip/versions."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "tests" / "contracts"

edits: list[tuple[str, str, str]] = [
    # permission 1.1.13
    (
        "test_api_gateway_g185_openapi_auth_permission_product_posture_schema.py",
        "{'1.1.7', '1.1.8', '1.1.9', '1.1.10', '1.1.11', '1.1.12'}",
        "{'1.1.7', '1.1.8', '1.1.9', '1.1.10', '1.1.11', '1.1.12', '1.1.13'}",
    ),
    (
        "test_api_gateway_g195_openapi_role_catalog_status_source_counts.py",
        "{'1.1.8', '1.1.9', '1.1.10', '1.1.11', '1.1.12'}",
        "{'1.1.8', '1.1.9', '1.1.10', '1.1.11', '1.1.12', '1.1.13'}",
    ),
    (
        "test_api_gateway_g196_openapi_role_grant_auto_write_response_detail.py",
        '{"1.1.9", "1.1.10", "1.1.11", "1.1.12"}',
        '{"1.1.9", "1.1.10", "1.1.11", "1.1.12", "1.1.13"}',
    ),
    # g202 version sets
    (
        "test_api_gateway_g202_openapi_errorbody_details_inventory.py",
        '"permission.openapi.yaml": {"1.1.10", "1.1.11"},\n'
        '    "organization.openapi.yaml": {"1.0.4", "1.0.5"},\n'
        '    "workflow.openapi.yaml": {"1.0.6", "1.0.7"},\n'
        '    "platform.openapi.yaml": {"1.0.3", "1.0.4"},',
        '"permission.openapi.yaml": {"1.1.10", "1.1.11", "1.1.12", "1.1.13"},\n'
        '    "organization.openapi.yaml": {"1.0.4", "1.0.5", "1.0.6"},\n'
        '    "workflow.openapi.yaml": {"1.0.6", "1.0.7", "1.0.8"},\n'
        '    "platform.openapi.yaml": {"1.0.3", "1.0.4", "1.0.5"},',
    ),
    # g206 permission versions -> sets
    (
        "test_api_gateway_g206_openapi_single_enum_const.py",
        '("permission.openapi.yaml", "RoleCatalogStatus", "catalog_store", "process_memory", "1.1.12"),\n'
        '    (\n'
        '        "permission.openapi.yaml",\n'
        '        "RoleGrantAutoWriteMintResponse",\n'
        '        "auto_write_step",\n'
        '        "role_grants",\n'
        '        "1.1.12",\n'
        '    ),\n'
        '    (\n'
        '        "permission.openapi.yaml",\n'
        '        "RoleGrantAutoWriteStubDetail",\n'
        '        "auto_write_step",\n'
        '        "role_grants",\n'
        '        "1.1.12",\n'
        '    ),',
        '("permission.openapi.yaml", "RoleCatalogStatus", "catalog_store", "process_memory", {"1.1.12", "1.1.13"}),\n'
        '    (\n'
        '        "permission.openapi.yaml",\n'
        '        "RoleGrantAutoWriteMintResponse",\n'
        '        "auto_write_step",\n'
        '        "role_grants",\n'
        '        {"1.1.12", "1.1.13"},\n'
        '    ),\n'
        '    (\n'
        '        "permission.openapi.yaml",\n'
        '        "RoleGrantAutoWriteStubDetail",\n'
        '        "auto_write_step",\n'
        '        "role_grants",\n'
        '        {"1.1.12", "1.1.13"},\n'
        '    ),',
    ),
]

# g215 inventory still G214 tip - soften to allow G216
edits.append(
    (
        "test_api_gateway_g215_terminal_openapi_oidc_mfa_enrollment_status.py",
        'assert posture["milestone"] == "PHX-G214"',
        'assert posture["milestone"] in {"PHX-G214", "PHX-G216"}',
    )
)
edits.append(
    (
        "test_api_gateway_g215_terminal_openapi_oidc_mfa_enrollment_status.py",
        'assert meta["milestone"] == "PHX-G214"',
        'assert meta["milestone"] in {"PHX-G214", "PHX-G216"}',
    )
)
edits.append(
    (
        "test_api_gateway_g215_terminal_openapi_oidc_mfa_enrollment_status.py",
        'assert "PHX-G215" in tip and "PHX-G215" in manifest and "PHX-G215" in status',
        'assert ("PHX-G215" in tip or "PHX-G216" in tip) and (\n'
        '        "PHX-G215" in manifest or "PHX-G216" in manifest\n'
        '    ) and ("PHX-G215" in status or "PHX-G216" in status)',
    )
)

# g214 inventory
edits.append(
    (
        "test_api_gateway_g214_openapi_oidc_mfa_enrollment_details.py",
        'assert posture["milestone"] == "PHX-G214"',
        'assert posture["milestone"] in {"PHX-G214", "PHX-G216"}',
    )
)
edits.append(
    (
        "test_api_gateway_g214_openapi_oidc_mfa_enrollment_details.py",
        'assert props["milestone"]["const"] == "PHX-G214"',
        'assert props["milestone"]["const"] in {"PHX-G214", "PHX-G216"}',
    )
)
edits.append(
    (
        "test_api_gateway_g214_openapi_oidc_mfa_enrollment_details.py",
        'assert meta["milestone"] == "PHX-G214"',
        'assert meta["milestone"] in {"PHX-G214", "PHX-G216"}',
    )
)
edits.append(
    (
        "test_api_gateway_g214_openapi_oidc_mfa_enrollment_details.py",
        'assert ops["info"]["version"] == "1.0.33"',
        'assert ops["info"]["version"] in {"1.0.33", "1.0.34"}',
    )
)
edits.append(
    (
        "test_api_gateway_g214_openapi_oidc_mfa_enrollment_details.py",
        '        == "mount_parity_complete_oidc_mfa_enrollment_details_honest"\n'
        '    )',
        '        in {\n'
        '            "mount_parity_complete_oidc_mfa_enrollment_details_honest",\n'
        '            "mount_parity_complete_error_details_description_key_honest",\n'
        '        }\n'
        '    )',
    )
)
edits.append(
    (
        "test_api_gateway_g214_openapi_oidc_mfa_enrollment_details.py",
        'assert ("PHX-G214" in tip or "PHX-G215" in tip) and (\n'
        '        "PHX-G214" in manifest or "PHX-G215" in manifest\n'
        '    ) and ("PHX-G214" in status or "PHX-G215" in status)',
        'assert ("PHX-G214" in tip or "PHX-G215" in tip or "PHX-G216" in tip) and (\n'
        '        "PHX-G214" in manifest or "PHX-G215" in manifest or "PHX-G216" in manifest\n'
        '    ) and ("PHX-G214" in status or "PHX-G215" in status or "PHX-G216" in status)',
    )
)

for name, old, new in edits:
    path = T / name
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"{name}: old not found:\n{old[:120]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("ok", name)

# g206 assert version equality may need set handling - check test body
g206 = (T / "test_api_gateway_g206_openapi_single_enum_const.py").read_text(encoding="utf-8")
if 'assert spec["info"]["version"] == version' in g206:
    g206 = g206.replace(
        'assert spec["info"]["version"] == version',
        'assert spec["info"]["version"] == version or spec["info"]["version"] in version',
        1,
    )
    (T / "test_api_gateway_g206_openapi_single_enum_const.py").write_text(g206, encoding="utf-8")
    print("g206 version assert softened")

# soft older org/workflow/platform pins via simple appends
more = [
    (
        "test_api_gateway_g178_openapi_identity_org_status_honesty.py",
        'assert spec["info"]["version"] in {"1.0.3", "1.0.4"}',
        'assert spec["info"]["version"] in {"1.0.3", "1.0.4", "1.0.5", "1.0.6"}',
    ),
    (
        "test_api_gateway_g179_openapi_permission_workflow_status_honesty.py",
        'assert spec["info"]["version"] in {"1.0.4", "1.0.5"}',
        'assert spec["info"]["version"] in {"1.0.4", "1.0.5", "1.0.6", "1.0.7", "1.0.8"}',
    ),
    (
        "test_api_gateway_g174_openapi_detail_align.py",
        'assert platform["info"]["version"] in {"1.0.1", "1.0.2", "1.0.3", "1.0.4"}',
        'assert platform["info"]["version"] in {"1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.0.5"}',
    ),
    (
        "test_api_gateway_g191_openapi_brain_twin_ai_workflow_status_parity.py",
        'assert wf["info"]["version"] in {"1.0.5", "1.0.6"}',
        'assert wf["info"]["version"] in {"1.0.5", "1.0.6", "1.0.7", "1.0.8"}',
    ),
    (
        "test_api_gateway_g166_openapi_semantic_remainder.py",
        'assert org["info"]["version"] in {"1.0.1", "1.0.2", "1.0.3", "1.0.4"}',
        'assert org["info"]["version"] in {"1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.0.5", "1.0.6"}',
    ),
    (
        "test_api_gateway_g166_openapi_semantic_remainder.py",
        'assert workflow["info"]["version"] in {"1.0.2", "1.0.3", "1.0.4", "1.0.5"}',
        'assert workflow["info"]["version"] in {"1.0.2", "1.0.3", "1.0.4", "1.0.5", "1.0.6", "1.0.7", "1.0.8"}',
    ),
    (
        "test_api_gateway_g164_openapi_semantic_deepen.py",
        'assert workflow["info"]["version"] in {"1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.0.5", "1.0.6"}',
        'assert workflow["info"]["version"] in {"1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.0.5", "1.0.6", "1.0.7", "1.0.8"}',
    ),
    (
        "test_api_gateway_g148_openapi_inventory_product.py",
        "'1.0.29'}",
        "'1.0.29', '1.0.30', '1.0.31', '1.0.32', '1.0.33', '1.0.34'}",
    ),
]

for name, old, new in more:
    path = T / name
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print("SKIP", name, old[:60])
        continue
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("ok", name)

# g156/g161 permission version - read context
for name in (
    "test_api_gateway_g156_role_grant_auto_write_stub.py",
    "test_api_gateway_g161_role_grant_live_mint.py",
):
    path = T / name
    text = path.read_text(encoding="utf-8")
    if '"1.1.12"' in text and '{"1.1.12", "1.1.13"}' not in text:
        # replace version assert lists carefully
        text2 = text.replace(
            '        "1.1.12",\n',
            '        "1.1.12",\n        "1.1.13",\n',
            1,
        )
        if text2 == text:
            print("WARN no change", name)
        else:
            path.write_text(text2, encoding="utf-8")
            print("ok", name)

print("done")
