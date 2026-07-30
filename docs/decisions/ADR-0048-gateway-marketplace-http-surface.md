# ADR-0048 — Gateway Marketplace Technical HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G34  
**归属：** Platform API Gateway

## 背景

PHX-M16 已交付 Marketplace 技术生命周期与商业 fail-closed。OpenAPI 契约存在，但 Gateway 仅有 pricing stub，主路径未薄适配。

## 决策

### 1. 本切片交付（技术面）

| 区域 | 路由 |
|------|------|
| Listing | POST create；GET；signature / submit / review / publish / revoke |
| Acquire | POST acquire（技术获取，非购买合同） |
| Commercial | POST pricing → `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED` |

### 2. 边界不变

- `derive_tenant_context` + `reject_context_override`
- 业务语义仍归 `eaos_platform.marketplace`
- 定价 / 账单 / 分成 / 争议仍需另批人类批准，不在本切片开放

### 3. Explicit Defer

- Marketplace 商业政策产品化
- JWT/OIDC；完整 Terminal UI

## 关联

- [ADR-0031-marketplace-technical-boundary.md](ADR-0031-marketplace-technical-boundary.md)
- [../project/PHX-G34_ARCHITECTURE_GATE.md](../project/PHX-G34_ARCHITECTURE_GATE.md)
