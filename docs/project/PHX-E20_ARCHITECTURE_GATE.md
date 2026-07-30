# PHX-E20 Permission DecisionRecorded Wiring Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Permission Kernel + Shared Event Capability  
**规范源：** PERMISSION_EVENTS、ADR-0050  
**退出门禁：** Evaluate 成功与 outbox enqueue 同路径；摘要 payload

## 1. 门禁目标

将 `permission.decision.recorded` 接到域生产者 outbox，闭合 E19 目录缺口。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Emitter | `DomainEventEmitter.enqueue_fact` |
| Cardinality | 全量接线；订阅方自担幂等 |
| Payload | 摘要 only |

## 3. Exit Criteria

1. Evaluate 成功时写入 pending outbox（当 emitter 注入）。  
2. 目录契约将 `permission.decision.recorded` 纳入已接线集合。  
3. G18–G35 / E19 仍绿；完整回归通过。  
4. 不宣称 Broker / OIDC / 商业 Marketplace。

## 4. Explicit Defer

外部 Broker；采样治理；JWT/OIDC；商业 Marketplace
