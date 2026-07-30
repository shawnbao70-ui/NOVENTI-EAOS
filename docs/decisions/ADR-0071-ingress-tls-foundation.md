# ADR-0071 — Kubernetes Ingress / TLS Foundation

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G52  
**归属：** Platform Release / Operations boundary

## 背景

G51 Helm 以 ClusterIP + port-forward 暴露 Gateway。生产需可选 Ingress 与 TLS 声明，但不在本切片安装 Ingress Controller 或 cert-manager。

## 决策

1. 在 `deploy/helm/eaos` 增加 opt-in `ingress` values（默认 `enabled: false`）。  
2. 模板：`networking.k8s.io/v1` Ingress，将 `/`（Prefix）路由至 Gateway Service。  
3. TLS：支持 `ingress.tls` 引用既有 Secret；可选 `ingress.certManager` 注解（`cert-manager.io/cluster-issuer`），不捆绑 cert-manager 安装。  
4. 文档：`docs/release/INGRESS.md`；契约断言模板/values/文档；不强制集群 apply。  
5. 不 bump 包版本（仍 `0.2.0`）；无 Alembic；不交付 Service Mesh / 多区域。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 安装 Ingress Controller / cert-manager Operator  
- Service Mesh / mTLS 网格  
- HPA Foundation（见 ADR-0072 / PHX-G53）；多区域仍延后  
- 多 IdP 联邦管理 UI  

## 关联

- [ADR-0070-helm-foundation.md](ADR-0070-helm-foundation.md)
- [ADR-0072-hpa-foundation.md](ADR-0072-hpa-foundation.md)
- [../project/PHX-G52_ARCHITECTURE_GATE.md](../project/PHX-G52_ARCHITECTURE_GATE.md)
- [../release/INGRESS.md](../release/INGRESS.md)
