# PHX-M16 Marketplace Technical Foundation Acceptance

**日期：** 2026-07-18  
**状态：** Technically Fully Accepted  
**商业/法律门禁：** **仍开放**（定价/分成/账单/争议未批准、未实现）  
**归属：** Shared Platform Capability / Marketplace  
**退出门禁（本切片）：** 签名可验证引用、可审核、可撤销；商业 API 失败关闭

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | Listing / Signature / Review |
| B | Publish / Revoke / Acquire；商业 API deny |
| C | SQLAlchemy + TransactionalMarketplace + Alembic `0020` |
| D | OpenAPI / 状态机 / PostgreSQL / 七步自审 |

## 2. 核心不变量

- 无签名不可提交/发布
- 未批准不可发布；撤销后不可新获取
- 能力声明必填
- `set_pricing` / `create_invoice` / `open_dispute` / `set_revenue_share` → `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED`
- Acquire ≠ 购买合同

## 3. 自动化证据

- 本地完整回归：`294 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`（`tests/integration`）
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0031；落点 `eaos_platform.marketplace` |
| Constitution Review | 通过；BOOK08 技术条款；商业条款未抢跑 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 技术阻断项关闭；商业/法律显式开放 |
| Second-pass Review | Technically Fully Accepted |

## 5. Explicit Defer（需另一次人工批准）

- 定价模型、货币、试用、优惠
- 分成比例、计量单价、账单与税务
- 争议解决与法律责任归属
- 支付网关、Extension 沙箱执行引擎

## 6. 证据索引

- [PHX-M16 Architecture Gate](PHX-M16_ARCHITECTURE_GATE.md)
- [ADR-0031](../decisions/ADR-0031-marketplace-technical-boundary.md)
- [Marketplace Interface](../architecture/MARKETPLACE_INTERFACE.md)
- [Marketplace OpenAPI](../api/marketplace.openapi.yaml)
