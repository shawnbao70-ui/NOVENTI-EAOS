# PHX-G42 Terminal Extension iframe + CSP Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**规范源：** ADR-0060  

## 1. 门禁目标

交付 Foundation iframe 呈现面：首方演示面板、严格 CSP、postMessage 桥接到既有受治理 invoke。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Smart Terminal；无业务真相 |
| Content | 仅首方 `/terminal/extensions/*` |
| Sandbox | iframe `allow-scripts`；无 `allow-same-origin` |
| Bridge | allowlist → `invoke_extension_action` |
| Worker / CDN | 显式延后 |

## 3. Exit Criteria

1. ADR-0060 Accepted。  
2. CSP 头覆盖 extension 面板路径。  
3. 桥接拒绝提升字段与未知消息类型。  
4. 全量 contracts 绿；无任意 Marketplace JS 执行。
