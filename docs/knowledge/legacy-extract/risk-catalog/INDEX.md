# Risk Catalog — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Catalog | File | Evidence strength | Primary concern |
|---------|------|-------------------|-----------------|
| 双写 / 并行事实源 | [dual_write.md](dual_write.md) | Strong | 镜像漂移、顺序多写、双轨台账、无对账 |
| V14 Residual | [v14_residual.md](v14_residual.md) | Strong for structure; runtime mount health partly UNKNOWN | owner 顺序、全局注入、直 SQL、迁移标签误读 |
| 权限空洞 | [permission_holes.md](permission_holes.md) | Strong for listed routes | GET 写操作、无 route gate、UI-only confirm、IDOR |

## Priority map

| Priority | Risk IDs | Reason |
|----------|----------|--------|
| Critical | DW-001, DW-003, VR-001, PH-001, PH-002, PH-004, PH-006 | 金额/库存/审批/高影响业务对象可产生不一致或越权 |
| High | DW-002, DW-004, DW-005, DW-006, VR-002, VR-003, VR-004, VR-006, PH-003, PH-005, PH-007, PH-008 | 业务状态、owner、并发、路由可用性和审计可能漂移 |
| Medium | DW-007, DW-008, VR-005 | 元数据双轨与历史标签误读 |

## Cross-pack references

- Inventory mirrors and DO workflows: [../ops/inventory.md](../ops/inventory.md), [../ops/order.md](../ops/order.md), [../ops/delivery.md](../ops/delivery.md)
- AR/AP reconciliation: [../finance/ar_receipt_reconciliation.md](../finance/ar_receipt_reconciliation.md), [../finance/ap_payment_clearing.md](../finance/ap_payment_clearing.md)
- Approval and Human Approved boundaries: [../governance/approval.md](../governance/approval.md)
- Brand parallel stores: [../engagement/brand.md](../engagement/brand.md)
