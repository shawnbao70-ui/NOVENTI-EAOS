# PHX-M17 Marketplace Commercial Policy Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation 政策 v1）  
**归属：** Marketplace Platform  
**退出门禁：** ADR-0054；商业 API 按政策；Acquire ≠ 合同；契约绿

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0054 + Architecture Gate |
| B | `policy.py` + 定价/发票/分成/争议领域模型与仓储 |
| C | Service + Transactional + Alembic `0022` |
| D | Gateway 商业路由 + OpenAPI 1.1 |
| E | 契约测试 + 七步自审 |

## 2. 核心不变量

- Acquire 仍为技术获取记录  
- 支付清算 / 外部仲裁仍 `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED`  
- Body 不可提升安全上下文  
- 争议裁决权：发布方租户 + 审计  

## 3. 自动化证据

- 本地完整回归：`412 passed`（`tests/contracts`）  
- Alembic head：`0022_marketplace_m17_commercial`  
- PostgreSQL：需本地实例升级 head 后验证  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0054 |
| Constitution Review | 通过；BOOK08 商业变更经批准 |
| Cross-reference Review | 通过；M16/G34 技术路径仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；Manifest head 同步 |
| Gap Analysis | 支付/订阅/外部仲裁显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 支付网关与自动退款  
- 订阅/用量计量、税务与优惠  
- 平台面 Governor 强制改判、外部仲裁  

## 6. 证据索引

- [PHX-M17 Architecture Gate](PHX-M17_ARCHITECTURE_GATE.md)
- [ADR-0054](../decisions/ADR-0054-marketplace-commercial-policy.md)
- [ADR-0031](../decisions/ADR-0031-marketplace-technical-boundary.md)
