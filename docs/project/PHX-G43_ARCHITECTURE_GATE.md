# PHX-G43 Terminal Extension Worker Runtime Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**规范源：** ADR-0061  

## 1. 门禁目标

交付 Foundation 首方 Worker：与 G42 共享桥接 allowlist，映射到受治理 invoke。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Content | 仅首方 `demo-worker.js` |
| Bridge | 复用 `eaos.extension.invoke`；可选 `channel=worker` |
| Network | Worker 资产 CSP `connect-src 'none'` |
| Marketplace JS | 显式拒绝 / 延后 |

## 3. Exit Criteria

1. ADR-0061 Accepted。  
2. Worker 桥接拒绝提升字段。  
3. Gateway 服务 Worker 资产并带 CSP。  
4. 全量 contracts 绿；无 schema 变更。
