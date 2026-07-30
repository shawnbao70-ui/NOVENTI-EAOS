# PHX-G59 Service Mesh Foundation Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0078  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Opt-in、厂商无关的 Mesh 注入标签/注解；默认关；不安装控制面；不渲染网格 CRD。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `mesh.enabled`（默认 false） |
| Surface | Pod/Service labels + annotations |
| Defaults | 可覆盖的 sidecar inject 标签（Istio 风格默认） |
| mTLS | 集群/网格侧；chart 不声明 PeerAuthentication |
| Controllers | 不捆绑 |

## 3. Exit Criteria

1. ADR-0078 Accepted。  
2. 模板接线 + `MESH.md` + 契约绿；包版本仍 `0.2.0`。  
3. 全量 contracts 绿。  

见 [PHX-G59_ACCEPTANCE.md](PHX-G59_ACCEPTANCE.md)。
