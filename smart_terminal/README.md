# Smart Terminal

Independent governed interaction layer for human–AI collaboration (PHX-T13).

## Ownership

- Owns: Terminal Session shell state, Intent drafts, Plan Preview snapshots, approval references, commit receipts.
- Does **not** own: Identity, Permission decisions, Workflow approval truth, Knowledge, business entities, AI Runtime execution.

## Exit gate

**不持有业务真相** — workspace state only; Approval always read from Workflow.

## Package

| Module | Role |
|--------|------|
| `models.py` | Session / Intent / Preview / Receipt |
| `repository.py` | In-memory workspace repository |
| `service.py` | OpenSession → Intent → Preview → Approval → Commit |
| `ui/` | Complete Terminal UI + Extensions iframe/Worker（G36/G39/G42/G43；经 Gateway `/terminal/` 挂载） |
| `extension_runtime.py` | iframe/Worker 桥接 allowlist + Extension 面板 CSP 策略（G42/G43） |
| `signing.py` | Extension activate HMAC/Ed25519 验签策略（G44） |

## Complete Terminal UI

七表面静态壳（Operator / Product / Ops / Approval / Admin / AI / Extensions），消费 Gateway，不宿主业务规则。Product / Ops 为 Package Surface 演示面，可移交 Operator 走 Intent → Preview → Commit。Extension Host：登记/沙箱 invoke + 首方 iframe/Worker（CSP / 桥接）；不执行 Marketplace 任意脚本。本地：

```bash
# Default gateway is fail-closed (no eligibility / grants) — health works, Operator flow does not.
uvicorn api.gateway.app:app --reload
# open http://127.0.0.1:8000/terminal/

# Local Operator click-through (AllowAll + terminal grants; paste printed Subject/Tenant):
uvicorn api.gateway.demo:app --reload --port 8001
# open http://127.0.0.1:8001/terminal/
# Product: http://127.0.0.1:8001/terminal/#product  （含「样品流程（演示）」）
# Ops:     http://127.0.0.1:8001/terminal/#ops      （含「订单流程（演示）」）
# Flow: Open session → Compose intent → Build preview (High impact off) → Commit preview
# Note: order.approve.compose is high-impact (Workflow). Demo handoff ≠ Legacy CRUD.
```

## Related

- `docs/decisions/ADR-0028-smart-terminal-boundary.md`
- `docs/decisions/ADR-0049-terminal-operator-shell.md`
- `docs/decisions/ADR-0052-complete-terminal-ui.md`
- `docs/project/PHX-T13_ARCHITECTURE_GATE.md`
- `docs/project/PHX-G35_ARCHITECTURE_GATE.md`
- `docs/project/PHX-G36_ARCHITECTURE_GATE.md`
- `docs/blueprint/SMART_TERMINAL_BLUEPRINT.md`
