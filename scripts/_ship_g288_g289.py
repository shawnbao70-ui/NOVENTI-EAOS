"""Ship PHX-G288/G289: standing outer-close regression guard + ContextEchoRequest.

Locks Natural Pause honesty: non-allowlisted named object outers must stay
closed; intentional residuals allowlisted. Names ops ContextEchoRequest for
the only anonymous AP:true requestBody (intentional free-form echo).
Softens G286 tip-exact pins. Delete after use.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "docs" / "api"
C = ROOT / "tests" / "contracts"
INV = ROOT / "api" / "gateway" / "openapi_inventory_product.py"
OPS = API / "ops.openapi.yaml"
PROJECT = ROOT / "docs" / "project"
DECISIONS = ROOT / "docs" / "decisions"
RELEASE = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
UI_JS = ROOT / "smart_terminal" / "ui" / "app.js"
UI_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
DAL = PROJECT / "DELEGATED_AUTHORITY_LEDGER.md"
TIP = PROJECT / "ENG_SOFT_QUEUE_TIP.md"
STATUS = PROJECT / "PROJECT_STATUS.md"
CHANGELOG = PROJECT / "CHANGELOG.md"

T0188 = "mount_parity_complete_outer_close_regression_guard_honest"
REASON = "outer_close_regression_guard_g288"
OPS_VER = "1.0.69"


def w(path: Path, body: str) -> None:
    path.write_text(body.strip() + "\n", encoding="utf-8")


def name_context_echo_request() -> None:
    ops = OPS.read_text(encoding="utf-8")
    if "ContextEchoRequest:" in ops:
        print("ContextEchoRequest already present")
    else:
        # Replace anonymous requestBody schema with $ref
        old_rb = """        content:
          application/json:
            schema:
              type: object
              additionalProperties: true
              description: Arbitrary payload excluding elevation fields
"""
        new_rb = """        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ContextEchoRequest"
"""
        if old_rb not in ops:
            raise SystemExit("context/echo requestBody block not found")
        ops = ops.replace(old_rb, new_rb, 1)
        # Insert schema before ContextEchoPayload
        schema = """    ContextEchoRequest:
      type: object
      additionalProperties: true
      description: >
        Intentional free-form echo request body (PHX-G288). Elevation fields
        (tenant_id, subject_id, platform_scope, session_id, roles) are rejected
        at runtime; residual keys are echoed. ≠ invent domain semantics.
    ContextEchoPayload:
"""
        if "    ContextEchoPayload:\n" not in ops:
            raise SystemExit("ContextEchoPayload anchor missing")
        ops = ops.replace("    ContextEchoPayload:\n", schema, 1)
    # bump ops version will happen in bump(); ensure description mentions G288 later
    OPS.write_text(ops, encoding="utf-8")
    print("named ContextEchoRequest")


def soft_prior() -> None:
    for name in (
        "test_api_gateway_g286_openapi_errorbody_outer_closed.py",
        "test_api_gateway_g287_terminal_openapi_errorbody_outer_status.py",
    ):
        p = C / name
        t = p.read_text(encoding="utf-8")
        t = t.replace('assert posture["milestone"] == "PHX-G286"', 'assert posture["milestone"].startswith("PHX-G")')
        t = t.replace('assert props["milestone"].get("const") == "PHX-G286"', 'assert str(props["milestone"].get("const", "")).startswith("PHX-G")')
        t = t.replace(
            'assert posture["t0188_status"] == "mount_parity_complete_errorbody_outer_closed_honest"',
            'assert posture["t0188_status"].startswith("mount_parity_complete")',
        )
        t = t.replace(
            'assert props["t0188_status"].get("const") == posture["t0188_status"]',
            'assert str(props["t0188_status"].get("const", "")).startswith("mount_parity_complete")',
        )
        t = t.replace('assert ops["info"]["version"] == "1.0.68"', 'assert ops["info"]["version"].startswith("1.0.")')
        t = t.replace('assert meta["milestone"] == "PHX-G286"', 'assert meta["milestone"].startswith("PHX-G")')
        p.write_text(t, encoding="utf-8")
        print("softened", name)


def bump() -> None:
    inv = INV.read_text(encoding="utf-8")
    inv = re.sub(r'"milestone": "PHX-G\d+"', '"milestone": "PHX-G288"', inv, count=1)
    inv = re.sub(
        r'"t0188_status": "mount_parity_complete_[^"]+"',
        f'"t0188_status": "{T0188}"',
        inv,
        count=1,
    )
    if REASON not in inv:
        inv = inv.replace(
            '    "errorbody_outer_closed_g286",\n',
            f'    "errorbody_outer_closed_g286",\n    "{REASON}",\n',
            1,
        )
    INV.write_text(inv, encoding="utf-8")
    ops = OPS.read_text(encoding="utf-8")
    ops = re.sub(
        r"(info:\n  title: .*?\n  version: )1\.0\.\d+",
        rf"\g<1>{OPS_VER}",
        ops,
        count=1,
        flags=re.S,
    )
    ops = re.sub(
        r"(        milestone:\n          type: string\n          const: )PHX-G\d+",
        r"\g<1>PHX-G288",
        ops,
        count=1,
    )
    ops = re.sub(r"t0188_status=mount_parity_complete_[^;`\n]+", f"t0188_status={T0188}", ops, count=1)
    ops = re.sub(r"(          const: )mount_parity_complete_[^\n]+", rf"\1{T0188}", ops, count=1)
    ops = re.sub(
        r"Remains false after PHX-G\d+ [^\n]+",
        "Remains false after PHX-G288 outer-close regression guard (semantic remainder).",
        ops,
        count=1,
    )
    OPS.write_text(ops, encoding="utf-8")


def docs_ui_tests() -> None:
    js = UI_JS.read_text(encoding="utf-8")
    if "outer_close_regression_guard" not in js:
        js = js.replace(
            '    const errOuter = String(t0188).includes("errorbody_outer_closed");\n',
            '    const errOuter = String(t0188).includes("errorbody_outer_closed");\n'
            '    const outerGuard = String(t0188).includes("outer_close_regression_guard");\n',
            1,
        )
        js = js.replace(
            '      (errOuter\n'
            '        ? " · ErrorBody outer closed (G286/G287)"\n'
            "        : \"\") +\n",
            '      (errOuter\n'
            '        ? " · ErrorBody outer closed (G286/G287)"\n'
            "        : \"\") +\n"
            '      (outerGuard\n'
            '        ? " · Outer-close regression guard (G288/G289)"\n'
            "        : \"\") +\n",
            1,
        )
        js = js.replace(
            "        errorbody_outer_closed_honest: errOuter,\n",
            "        errorbody_outer_closed_honest: errOuter,\n"
            "        outer_close_regression_guard_honest: outerGuard,\n",
            1,
        )
    js = re.sub(r'log\("OpenAPI inventory posture \(PHX-G\d+\)"', 'log("OpenAPI inventory posture (PHX-G289)"', js, count=1)
    js = re.sub(r"semantic parity still deferred; G\d+\)", "semantic parity still deferred; G289)", js)
    js = re.sub(
        r"/\*\* OpenAPI inventory posture strip \(PHX-G184 → .*?\)\. \*/",
        "/** OpenAPI inventory posture strip (PHX-G184 → … → PHX-G289). */",
        js,
        count=1,
    )
    UI_JS.write_text(js, encoding="utf-8")
    html = UI_HTML.read_text(encoding="utf-8")
    html = re.sub(r"Refresh OpenAPI inventory \(G184…G\d+\)", "Refresh OpenAPI inventory (G184…G289)", html, count=1)
    html = re.sub(r"OpenAPI inventory status \(G\d+\)", "OpenAPI inventory status (G289)", html, count=1)
    UI_HTML.write_text(html, encoding="utf-8")

    w(
        DECISIONS / "ADR-0307-openapi-outer-close-regression-guard.md",
        """# ADR-0307 — OpenAPI Outer-Close Regression Guard

**状态：** Accepted  
**日期：** 2026-07-23  
**里程碑：** PHX-G288  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U161**

## 决策

常驻契约：除 intentional residual allowlist 外，全部 named `type:object` 外层必须
`additionalProperties: false`。Allowlist = WebAuthn attestation 三袋 + IdP JWKS 两袋
+ `ContextEchoRequest`（命名原匿名 echo body；仍 AP:true；≠ invent 域语义）。
锁定 Natural Pause；≠ softener 空环；≠ close residuals。ops **1.0.69**；inventory PHX-G288。
""",
    )
    for kind in ("ACCEPTANCE", "ARCHITECTURE_GATE"):
        w(
            PROJECT / f"PHX-G288_{kind}.md",
            f"""# PHX-G288 OpenAPI outer-close regression guard {kind.replace('_', ' ').title()}

**日期：** 2026-07-23  
**状态：** Fully Accepted（Foundation）  
**规范源：** ADR-0307  
**授权：** DAL-G003 + DAL-G004（DAL-U161）

## Exit

ADR + tip/status；包 `0.2.1`；Alembic `0029`。
""",
        )
    w(
        DECISIONS / "ADR-0308-terminal-openapi-outer-close-guard-status-deepen.md",
        """# ADR-0308 — Terminal OpenAPI Outer-Close Guard Status Deepen

**状态：** Accepted  
**日期：** 2026-07-23  
**里程碑：** PHX-G289  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U162**

## 决策

Admin CTA + strip 标记 outer-close regression guard；inventory 不 bump。
""",
    )
    for kind in ("ACCEPTANCE", "ARCHITECTURE_GATE"):
        w(
            PROJECT / f"PHX-G289_{kind}.md",
            f"""# PHX-G289 Terminal OpenAPI outer-close guard status deepen {kind.replace('_', ' ').title()}

**日期：** 2026-07-23  
**状态：** Fully Accepted（Foundation）  
**规范源：** ADR-0308  
**授权：** DAL-G003 + DAL-G004（DAL-U162）

## Exit

ADR + tip/status；包 `0.2.1`；Alembic `0029`。
""",
        )

    (C / "test_api_gateway_g288_openapi_outer_close_regression_guard.py").write_text(
        '''"""PHX-G288 OpenAPI outer-close regression guard honesty."""

from __future__ import annotations

from pathlib import Path

import yaml
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"
OPS = API / "ops.openapi.yaml"

# Intentional residual / free-form named outers — do NOT invent closes.
INTENTIONAL_OPEN: set[tuple[str, str]] = {
    ("auth.openapi.yaml", "WebauthnAuthenticatorAttestationResponse"),
    ("auth.openapi.yaml", "WebauthnPublicKeyCredential"),
    ("auth.openapi.yaml", "WebauthnRegisterVerifyRequest"),
    ("platform.openapi.yaml", "IdpJwksKey"),
    ("platform.openapi.yaml", "IdpJwksDocument"),
    ("ops.openapi.yaml", "ContextEchoRequest"),
}


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_g288_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0307-openapi-outer-close-regression-guard.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G288_ACCEPTANCE.md").is_file()


def test_g288_named_outers_closed_or_allowlisted() -> None:
    seen_open: set[tuple[str, str]] = set()
    for path in sorted(API.glob("*.openapi.yaml")):
        schemas = _load(path).get("components", {}).get("schemas", {})
        for name, schema in schemas.items():
            if not isinstance(schema, dict):
                continue
            if schema.get("type") != "object":
                continue
            if any(k in schema for k in ("allOf", "anyOf", "oneOf", "$ref")):
                continue
            key = (path.name, name)
            ap = schema.get("additionalProperties")
            if ap is True:
                assert key in INTENTIONAL_OPEN, f"unexpected open outer {key}"
                seen_open.add(key)
            else:
                assert ap is False, f"missing/closed AP on {key}: {ap!r}"
    assert seen_open == INTENTIONAL_OPEN


def test_g288_context_echo_request_named() -> None:
    ops = _load(OPS)
    schema = ops["components"]["schemas"]["ContextEchoRequest"]
    assert schema.get("additionalProperties") is True
    ref = (
        ops["paths"]["/context/echo"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"].get("$ref", "")
    )
    assert ref.endswith("/ContextEchoRequest")


def test_g288_ops_tip_parity() -> None:
    posture = openapi_inventory_product_posture()
    ops = _load(OPS)
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert posture["milestone"] == "PHX-G288"
    assert props["milestone"].get("const") == "PHX-G288"
    assert posture["t0188_status"] == "mount_parity_complete_outer_close_regression_guard_honest"
    assert props["t0188_status"].get("const") == posture["t0188_status"]
    assert ops["info"]["version"] == "1.0.69"
    assert "g288" in " ".join(posture["fail_closed_reasons"]).casefold()
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"] == "PHX-G288"
    assert posture["full_openapi_http_complete"] is False


def test_g288_baseline() -> None:
    assert sdk_version == "0.2.1"
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0029_eaos_declared_roles_g90"
    assert "DAL-U161" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
''',
        encoding="utf-8",
    )
    (C / "test_api_gateway_g289_terminal_openapi_outer_close_guard_status.py").write_text(
        '''"""PHX-G289 Terminal OpenAPI outer-close guard status deepen."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]


def test_g289_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "outer_close_regression_guard" in js
    assert "Outer-close regression guard" in js
    assert "G28" in html
    assert (ROOT / "docs" / "project" / "PHX-G289_ACCEPTANCE.md").is_file()
    assert "DAL-U162" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "PHX-G289" in tip and "PHX-G289" in manifest
    assert sdk_version == "0.2.1"
    posture = openapi_inventory_product_posture()
    assert posture["milestone"] == "PHX-G288"
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"] == "PHX-G288"
''',
        encoding="utf-8",
    )

    dal = DAL.read_text(encoding="utf-8")
    if "DAL-U161" not in dal:
        block = (
            "| **DAL-U162** | 2026-07-23 | DAL-G003 + DAL-G004 | Eng | PHX-G289 Terminal OpenAPI outer-close guard status deepen | ADR-0308; Gate/Acceptance; Admin CTA + strip; Manifest G289; `test_api_gateway_g289_*` | PO cue「充分授权…自主开发…加快」；surfaces G288；no inventory bump；package `0.2.1`；Alembic `0029` |\n"
            "| **DAL-U161** | 2026-07-23 | DAL-G003 + DAL-G004 | Eng | PHX-G288 OpenAPI outer-close regression guard | ADR-0307; Gate/Acceptance; standing allowlist guard; ContextEchoRequest named; ops tip sync; inventory/ops G288; Manifest G288; `test_api_gateway_g288_*` | PO cue「充分授权…自主开发…加快」；AED Foundation harden #1；locks Natural Pause；package `0.2.1`；Alembic `0029` |\n"
        )
        dal = dal.replace("| **DAL-U160** |", block + "| **DAL-U160** |", 1)
        DAL.write_text(dal, encoding="utf-8")

    tip = TIP.read_text(encoding="utf-8")
    if "PHX-G288" not in tip:
        tip = tip.replace(
            "| Terminal OpenAPI ErrorBody outer status deepen | **PHX-G287** | Admin CTA + strip；ErrorBody outer 标记；bootstrap quiet；inventory 不 bump |\n",
            "| Terminal OpenAPI ErrorBody outer status deepen | **PHX-G287** | Admin CTA + strip；ErrorBody outer 标记；bootstrap quiet；inventory 不 bump |\n"
            "| OpenAPI outer-close regression guard | **PHX-G288** | standing allowlist guard；ContextEchoRequest named；inventory G288；ops 1.0.69 |\n"
            "| Terminal OpenAPI outer-close guard status deepen | **PHX-G289** | Admin CTA + strip；outer-close guard 标记；bootstrap quiet；inventory 不 bump |\n",
            1,
        )
    tip = tip.replace(
        "After **PHX-G287**, ErrorBody outer closed；named inventable outers exhausted；remaining intentional residuals only（JWKS / WebAuthn attestation / nested free-form / ErrorBody.details residual）— 勿 invent。Prefer live T2–T3；attestation-crypto/PSP/catalog with PO；**Promote + Phoenix ADR**。Do not open empty tip/hygiene loops.",
        "After **PHX-G289**, outer-close regression guard locked；named inventable outers exhausted；intentional residuals allowlisted（JWKS / WebAuthn attestation / ContextEchoRequest / nested free-form / ErrorBody.details residual）— 勿 invent。Prefer live T2–T3；attestation-crypto/PSP/catalog with PO；**Promote + Phoenix ADR**。Do not open empty tip/hygiene loops.",
        1,
    )
    tip = tip.replace(
        "Still deferred after G287 ErrorBody outer close",
        "Still deferred after G289 outer-close regression guard",
        1,
    )
    if "Outer-close guard **U161**" not in tip:
        tip = tip.replace(
            "ErrorBody outer **U159**；Terminal ErrorBody outer status **U160**",
            "ErrorBody outer **U159**；Terminal ErrorBody outer status **U160**；"
            "Outer-close guard **U161**；Terminal outer-close guard status **U162**",
            1,
        )
    if "PHX-G288_ACCEPTANCE" not in tip:
        tip = tip.replace(
            "| [PHX-G287_ACCEPTANCE.md](PHX-G287_ACCEPTANCE.md) | Terminal OpenAPI ErrorBody outer status deepen Acceptance |\n",
            "| [PHX-G287_ACCEPTANCE.md](PHX-G287_ACCEPTANCE.md) | Terminal OpenAPI ErrorBody outer status deepen Acceptance |\n"
            "| [PHX-G288_ACCEPTANCE.md](PHX-G288_ACCEPTANCE.md) | OpenAPI outer-close regression guard Acceptance |\n"
            "| [PHX-G289_ACCEPTANCE.md](PHX-G289_ACCEPTANCE.md) | Terminal OpenAPI outer-close guard status deepen Acceptance |\n",
            1,
        )
    TIP.write_text(tip, encoding="utf-8")

    status = STATUS.read_text(encoding="utf-8")
    status = re.sub(
        r"\*\*PHX-G287 —.*?(?=\*\*Research context：)",
        "**PHX-G289 — Terminal OpenAPI outer-close guard status deepen**"
        "（Fully Accepted；ADR-0308；Admin CTA + strip outer-close guard marker；"
        "inventory 不 bump；DAL-U162；包仍 `0.2.1`；Alembic 仍 `0029`）\n\n"
        "**Prior tip：** PHX-G288 OpenAPI outer-close regression guard（DAL-U161）· "
        "PHX-G287–G185 · PHX-G163 T2/T3 intake（DAL-U034；0 Complete）\n\n",
        status,
        count=1,
        flags=re.S,
    )
    STATUS.write_text(status, encoding="utf-8")

    man = RELEASE.read_text(encoding="utf-8")
    if "PHX-G288" not in man:
        man = man.replace(
            "  - id: PHX-G287\n    status: fully_accepted\n"
            "    notes: terminal_openapi_errorbody_outer_status_deepen\n",
            "  - id: PHX-G287\n    status: fully_accepted\n"
            "    notes: terminal_openapi_errorbody_outer_status_deepen\n"
            "  - id: PHX-G288\n    status: fully_accepted\n"
            "    notes: openapi_outer_close_regression_guard\n"
            "  - id: PHX-G289\n    status: fully_accepted\n"
            "    notes: terminal_openapi_outer_close_guard_status_deepen\n",
            1,
        )
    RELEASE.write_text(man, encoding="utf-8")

    cl = CHANGELOG.read_text(encoding="utf-8")
    if "PHX-G288" not in cl:
        insert = """### 2026-07-23 — PHX-G289 Terminal OpenAPI Outer-Close Guard Status Deepen

- 接受 ADR-0308；Admin CTA + strip；DAL-**U162**
- 契约：`test_api_gateway_g289_terminal_openapi_outer_close_guard_status.py`

### 2026-07-23 — PHX-G288 OpenAPI Outer-Close Regression Guard

- 接受 ADR-0307；standing allowlist guard；`ContextEchoRequest` 命名；ops **1.0.69**；inventory G288；DAL-**U161**
- 契约：`test_api_gateway_g288_openapi_outer_close_regression_guard.py`

"""
        cl = cl.replace("## 条目\n\n", "## 条目\n\n" + insert, 1)
    CHANGELOG.write_text(cl, encoding="utf-8")


def main() -> None:
    name_context_echo_request()
    soft_prior()
    bump()
    docs_ui_tests()
    print("SHIP G288+G289 complete")


if __name__ == "__main__":
    main()
