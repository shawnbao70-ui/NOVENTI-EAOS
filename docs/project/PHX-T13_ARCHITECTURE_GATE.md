# PHX-T13 Smart Terminal Foundation Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted；实现已验收（见 PHX-T13_ACCEPTANCE）  
**归属：** Smart Terminal（独立受治理交互层）  
**规范源：** BOOK12、BOOK19、BOOK22、BOOK23、ADR-0021、ADR-0024、ADR-0028  
**退出门禁：** 不持有业务真相

## 1. 门禁目标

交付 Smart Terminal 最小垂直切片：Session、Intent、Plan Preview、Approval Presenter、Commit Controller，证明上下文不可提升、审批不平行、提交失败关闭。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | 独立交互层；实现于 `smart_terminal/` |
| Session | 仅派生自 ExecutionContext；禁止客户端提升 |
| Intent / Preview | 工作区状态；≠ 业务实体 |
| Approval UX | 读 Workflow；本地只存 approval_ref |
| Commit | Permission +（高影响）Workflow verify；回执非业务真相 |
| Device trust | untrusted → 拒绝高影响 Commit |
| Secrets | Intent / Preview 禁止秘密字段 |

## 3. Action / Resource Contract

- `terminal_session:open|read|close`
- `terminal_intent:compose|read`
- `terminal_preview:build|read`
- `terminal_approval:present|request`
- `terminal_commit:execute`

资源：

- `terminal_session:{id}`
- `terminal_intent:{id}`
- `terminal_preview:{id}`

## 4. 实现切片

### Slice A — Domain

- TerminalSession / Intent / PlanPreview / CommitReceipt
- OpenSession / ComposeIntent / BuildPreview

### Slice B — Approval + Commit

- RequestApproval / PresentApproval / Commit
- 过期预览与不匹配批准失败关闭

### Slice C — Persistence

- SQLAlchemy + Transactional facade + Alembic `0017`

### Slice D — Contracts

- OpenAPI / 状态机 / PostgreSQL / 七步自审

## 5. Exit Criteria

1. 客户端无法提升 Subject / Tenant。  
2. 跨租户会话/意图/预览不可见。  
3. Approval 状态以 Workflow 为准；陈旧/拒绝批准零 Commit。  
4. 高影响操作展示作用域并经双闸门。  
5. Terminal 不写入业务包真相；仅工作区与回执。  
6. OpenAPI / Data Model / Migration / Code 一致。  
7. PostgreSQL 与完整回归通过。

## 6. Explicit Defer

- 完整前端 Shell、Extension Host、Marketplace
- Accessibility / i18n 产品化验收矩阵
- Enterprise Brain / Digital Twin / FastAPI Router
