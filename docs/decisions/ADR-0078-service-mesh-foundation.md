# ADR-0078 — Service Mesh Foundation

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G59  
**归属：** Platform Release / Operations boundary

## 背景

G52 交付 Ingress；G58 交付 KEDA。需可选、厂商无关的 Service Mesh 接入声明（sidecar 注入标签/注解），不安装控制面，不绑定单一网格产品。

## 决策

1. 在 `deploy/helm/eaos` 增加 `mesh` values（默认 `enabled: false`）。  
2. 启用时仅向 Gateway Pod（及可选 Service）合并可配置 `podLabels` / `podAnnotations` / `serviceAnnotations`；默认提供可覆盖的 sidecar 注入标签键值（Istio 风格默认，可改为 Linkerd 等）。  
3. G59 **不**渲染网格 CRD；可选 PeerAuthentication 见 ADR-0090（G71）。  
4. 文档：`docs/release/MESH.md`；契约断言；不安装 Istio/Linkerd/其他控制面。  
5. 不 bump 包版本（仍 `0.2.0`）；无 Alembic；支付清算另批。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 安装 Mesh 控制面 / CNI  
- 网格流量 CRD（VS/DR）— PeerAuthentication 见 ADR-0090  
- 多区域  

## 关联

- [ADR-0071-ingress-tls-foundation.md](ADR-0071-ingress-tls-foundation.md)
- [ADR-0077-keda-foundation.md](ADR-0077-keda-foundation.md)
- [../project/PHX-G59_ARCHITECTURE_GATE.md](../project/PHX-G59_ARCHITECTURE_GATE.md)
- [../release/MESH.md](../release/MESH.md)
