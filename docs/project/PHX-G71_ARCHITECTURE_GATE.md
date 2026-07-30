# PHX-G71 Service Mesh Policy CRD Foundation Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0090  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Opt-in Istio PeerAuthentication；默认关；不装控制面。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `mesh.policy.enabled` |
| Vendor | `istio` only（Foundation） |
| CRD | PeerAuthentication STRICT（可覆盖） |
| Require | `mesh.enabled=true` |

## 3. Exit Criteria

1. ADR-0090 Accepted。  
2. 模板 + MESH.md + 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G71_ACCEPTANCE.md](PHX-G71_ACCEPTANCE.md)。
