# PHX-G36 Complete Terminal UI Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（实现已验收）  
**归属：** Smart Terminal  
**规范源：** BOOK23、SMART_TERMINAL_BLUEPRINT、ADR-0052  
**退出门禁：** 多表面壳；完整生命周期；零业务规则宿主

## 1. 门禁目标

将 G35 技术壳升为完整 Terminal UI：Operator / Approval / Admin / AI Collaboration 表面。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Host | `smart_terminal/ui` + `/terminal/` |
| Truth | Kernel / Workflow via Gateway |
| Extension | 延后 |
| Auth | 仍受信头；OIDC 另里程碑 |

## 3. Exit Criteria

1. 四表面可切换；Operator 含 get/close/preview refresh。  
2. Approval 表面可 request/present。  
3. Admin 只读 health/release/adapters/context。  
4. 契约证明无上下文提升；G35 资产仍服务。  
5. 不宣称 Extension Host / OIDC / 商业 Marketplace 已交付。

## 4. Explicit Defer

Extension Host；OIDC 登录页；Marketplace 商业；完整 a11y/i18n 矩阵
