# PHX-G34 Gateway Marketplace Technical HTTP Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** marketplace.openapi.yaml、ADR-0048  
**退出门禁：** 薄适配；商业路径仍 fail-closed

## 1. 门禁目标

将 M16 技术 Marketplace 接到 Gateway HTTP，并保持商业 API 失败关闭。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Context | 租户面 `derive_tenant_context` |
| Authority | `MarketplaceService` |
| Commercial | `set_pricing` 等恒拒绝 |

## 3. Exit Criteria

1. 技术生命周期契约通过。  
2. pricing 提升拒绝 + 商业政策拒绝。  
3. G18–G32 仍绿；完整回归通过。  
4. 不宣称商业 Marketplace / OIDC / Terminal UI 已交付。

## 4. Explicit Defer

定价/分成/账单/争议政策；JWT/OIDC；完整 Terminal UI
