# Runtime vs Declaration Package Layout（PHX-G411）

## Cross-index

| Path | Role | Examples |
|------|------|----------|
| `packages/*` | **Declarations only** — manifests / sample package artifacts for Package Platform | `packages/crm/`, `packages/sample_ops/`, `packages/sample_product/` |
| `noventi/*` | **Runtime implementations** — importable business packages used by gateway/SQL | `noventi.crm`, `noventi.finance`, `noventi.purchase`, `noventi.inventory` |
| `eaos_platform/package` | Package Platform runtime（registry/resolve） | Foundation Package surface |
| `docs/api/*.openapi.yaml` | HTTP contracts | marketplace, finance, crm, … |

## Rules

1. Design-only / proposed package keys live under `packages/` and must not be mistaken for importable runtime.
2. Gateway and Docker image must ship `noventi/`（PHX-G407）.
3. Do not invent Industry host-install runtime from a declaration under `packages/`.
4. Tip / package version authority remains `POST_CRM_VERTICAL_ROADMAP.md` + `RELEASE_MANIFEST.yaml` header + `tests/contracts/_baseline.py`.
