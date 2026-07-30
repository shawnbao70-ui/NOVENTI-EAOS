from __future__ import annotations

import re
from pathlib import Path

FILES = [
    "tests/contracts/test_api_gateway_g185_openapi_auth_permission_product_posture_schema.py",
    "tests/contracts/test_api_gateway_g192_openapi_identity_org_knowledge_status_parity.py",
    "tests/contracts/test_api_gateway_g178_openapi_identity_org_status_honesty.py",
    "tests/contracts/test_api_gateway_g179_openapi_permission_workflow_status_honesty.py",
    "tests/contracts/test_api_gateway_g202_openapi_errorbody_details_inventory.py",
]

PATTERNS = [
    (
        re.compile(
            r'assert\s*\(\s*\n\s*posture\["t0188_status"\]\s*\n\s*in \{[^}]+\}\s*\n\s*\)',
            re.M,
        ),
        'assert posture["t0188_status"].startswith("mount_parity_complete")',
    ),
    (
        re.compile(
            r'assert\s+posture\["t0188_status"\]\s*\n\s*in \{[^}]+\}',
            re.M,
        ),
        'assert posture["t0188_status"].startswith("mount_parity_complete")',
    ),
    (
        re.compile(
            r'assert\s+props\["t0188_status"\]\["const"\] in \{[^}]+\}',
            re.M,
        ),
        'assert props["t0188_status"]["const"].startswith("mount_parity_complete")',
    ),
    (
        re.compile(
            r'assert\s+props\["t0188_status"\]\.get\("const"\) in \{[^}]+\}',
            re.M,
        ),
        'assert str(props["t0188_status"].get("const","")).startswith("mount_parity_complete")',
    ),
]

for rel in FILES:
    path = Path(rel)
    text = path.read_text(encoding="utf-8")
    orig = text
    for pat, repl in PATTERNS:
        text = pat.sub(repl, text)
    if rel.endswith("g202_openapi_errorbody_details_inventory.py"):
        text = text.replace(
            '"auth.openapi.yaml": {"1.3.14", "1.3.15"},',
            '"auth.openapi.yaml": {"1.3.14", "1.3.15", "1.3.16", "1.3.17"},',
        )
    path.write_text(text, encoding="utf-8")
    print(rel, "changed" if text != orig else "noop")

# Also sweep remaining multiline t0188 across all g* contracts
root = Path("tests/contracts")
pat = re.compile(
    r'assert\s+posture\["t0188_status"\]\s*\n\s*in \{[^}]+\}',
    re.M,
)
pat2 = re.compile(
    r'assert\s*\(\s*\n\s*posture\["t0188_status"\]\s*\n\s*in \{[^}]+\}\s*\n\s*\)',
    re.M,
)
pat3 = re.compile(
    r'assert\s+props\["t0188_status"\]\["const"\] in \{[^}]+\}',
    re.M,
)
for path in root.glob("test_api_gateway_g*.py"):
    text = path.read_text(encoding="utf-8")
    new = pat.sub(
        'assert posture["t0188_status"].startswith("mount_parity_complete")', text
    )
    new = pat2.sub(
        'assert posture["t0188_status"].startswith("mount_parity_complete")', new
    )
    new = pat3.sub(
        'assert props["t0188_status"]["const"].startswith("mount_parity_complete")',
        new,
    )
    if new != text:
        path.write_text(new, encoding="utf-8")
        print("sweep", path.name)
print("done")
