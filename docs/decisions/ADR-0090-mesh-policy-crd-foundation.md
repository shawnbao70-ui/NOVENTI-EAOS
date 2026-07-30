# ADR-0090 — Service Mesh Policy CRD Foundation

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G71  
**归属：** Platform Release / Operations boundary

## 背景

G59 仅交付 sidecar 注入标签。需可选、最小网格安全策略 CRD（mTLS PeerAuthentication），仍不安装控制面。

## 决策

1. `mesh.policy.enabled`（默认 `false`）；启用时要求 `mesh.enabled=true`。  
2. Foundation 仅支持 `mesh.policy.vendor=istio`；渲染 `security.istio.io/v1beta1` `PeerAuthentication`，selector 对齐 Gateway Pod 标签，`mtls.mode` 默认 `STRICT`（可覆盖）。  
3. **不**渲染 AuthorizationPolicy；VS/DR 见 ADR-0091；**不**安装 Istio 控制面。  
4. 文档更新 `MESH.md`；契约断言；包版本仍 `0.2.0`。  
5. Linkerd / 其他厂商策略 CRD、多区域、支付清算另批。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 安装 Mesh 控制面 / CNI  
- AuthorizationPolicy / Linkerd 策略  
- 多区域 / 外部 KMS  

## 关联

- [ADR-0078-service-mesh-foundation.md](ADR-0078-service-mesh-foundation.md)
- [../project/PHX-G71_ARCHITECTURE_GATE.md](../project/PHX-G71_ARCHITECTURE_GATE.md)
- [../release/MESH.md](../release/MESH.md)
