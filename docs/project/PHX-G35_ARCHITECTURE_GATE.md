# PHX-G35 Smart Terminal Operator Shell Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Smart Terminal  
**规范源：** BOOK23、SMART_TERMINAL_BLUEPRINT、ADR-0049  
**退出门禁：** 壳为 API 消费者；零业务规则宿主

## 1. 门禁目标

交付最小 Operator Shell，挂载于 Gateway，走完低影响命令生命周期。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | `smart_terminal/ui`；非 Kernel |
| Transport | 仅调用 `/v1/terminal/*` |
| Context | 头派生；体不可提升 |
| Truth | Permission / Workflow 仍归 Kernel |

## 3. Exit Criteria

1. `/terminal/` 可服务壳资源。  
2. 契约证明无上下文提升字段进入 API body 构造。  
3. G18–G34 仍绿；完整回归通过。  
4. 不宣称完整产品 UI / OIDC / 商业 Marketplace / Extension Host。

## 4. Explicit Defer

品牌 UX 产品化；Extension Host；a11y/i18n 矩阵；JWT/OIDC
