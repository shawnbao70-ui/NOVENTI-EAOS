# ADR-0168 — Engineering Soft-Queue Tip Board

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G149  
**归属：** Phoenix Governance / Engineering Track  
**授权：** DAL-G003 charter-safe continuous autonomy（DAL-U010）

## 背景

Eng Explicit Defer `1`–`3` thin slices（PHX-G144–G146）与 OIDC / OpenAPI product surfaces（PHX-G147–G148）已 Fully Accepted。TASKS 仍残留与已验收门禁矛盾的「延后」行（T-0199 Identity AI·Governor；T-0204 平台租户 HTTP）。Engineering Track 缺少与 Research `GENERATION1_PEER_GATE` 对称的 **soft-queue tip board**，易在 `继续` 时误开产品面。

## 决策

1. 新增薄 tip 文档 `docs/project/ENG_SOFT_QUEUE_TIP.md`，固定 Done / Held / Next（optional deepenings only；no invent）。  
2. 关闭与 Fully Accepted 矛盾的 TASKS 行：T-0199 完成（G138 及相关）；T-0204 完成（G25 / G127）。  
3. PHX-G149 为 **docs-only** Fully Accepted；无代码、无 Alembic、包仍 `0.2.1`。  
4. **不**打开 Eng `4` 支付清算、Brain execute、Twin authorize、WebAuthn ceremony、Role→grant auto-write mint。

## Explicit Out（本切片不开口）

- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- Live WebAuthn ceremony  
- Role→grant auto-write / mint  
- 全量 OpenAPI HTTP parity  
- 新 Alembic / 包版本 bump  

## 后果

- Engineering tip 可读：`ENG_SOFT_QUEUE_TIP.md`；PROJECT_STATUS / ROADMAP / Dual-Track 指向该板。  
- 下一 Eng 产品发明仅限 **optional deepening**，且须编号切片 + DAL Usage Log。

## 关联

- [../project/ENG_SOFT_QUEUE_TIP.md](../project/ENG_SOFT_QUEUE_TIP.md)  
- [../project/PHX-G149_ARCHITECTURE_GATE.md](../project/PHX-G149_ARCHITECTURE_GATE.md)  
- [../project/PHX-G149_ACCEPTANCE.md](../project/PHX-G149_ACCEPTANCE.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
- [ADR-0162-dual-track-governance.md](ADR-0162-dual-track-governance.md)  
