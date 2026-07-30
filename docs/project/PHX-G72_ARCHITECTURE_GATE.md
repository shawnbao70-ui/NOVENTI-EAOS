# PHX-G72 Service Mesh Traffic CRD Foundation Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0091  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Opt-in Istio VirtualService + DestinationRule；默认关；不装控制面。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `mesh.traffic.enabled` |
| Vendor | `istio` only |
| CRDs | VS + DR（ISTIO_MUTUAL） |
| Require | `mesh.enabled=true` |

## 3. Exit Criteria

1. ADR-0091 Accepted。  
2. 模板 + MESH.md + 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G72_ACCEPTANCE.md](PHX-G72_ACCEPTANCE.md)。
