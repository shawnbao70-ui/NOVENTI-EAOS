# ADR-0091 — Service Mesh Traffic CRD Foundation

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G72  
**归属：** Platform Release / Operations boundary

## 背景

G71 交付 opt-in PeerAuthentication。需最小 in-mesh 流量声明（VirtualService + DestinationRule），仍不安装控制面。

## 决策

1. `mesh.traffic.enabled`（默认 `false`）；启用时要求 `mesh.enabled=true`。  
2. Foundation 仅支持 `mesh.traffic.vendor=istio`；渲染 `networking.istio.io/v1beta1`：  
   - `VirtualService`：host 默认 Gateway Service 短名；HTTP 路由到 Gateway port。  
   - `DestinationRule`：同 host；`trafficPolicy.tls.mode` 默认 `ISTIO_MUTUAL`（可覆盖）。  
3. **不**渲染 Gateway API；AuthorizationPolicy 见 ADR-0092；**不**安装 Istio。  
4. 文档更新 `MESH.md`；契约断言；包版本仍 `0.2.0`。  
5. 多 host/权重分流、Linkerd、多区域、支付清算另批。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Istio Gateway / Ingress 绑定  
- 权重分流 / 多子集 / Linkerd  
- 外部 KMS / 多区域  

## 关联

- [ADR-0090-mesh-policy-crd-foundation.md](ADR-0090-mesh-policy-crd-foundation.md)
- [../project/PHX-G72_ARCHITECTURE_GATE.md](../project/PHX-G72_ARCHITECTURE_GATE.md)
- [../release/MESH.md](../release/MESH.md)
