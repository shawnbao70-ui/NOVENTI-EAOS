# ADR-0072 — Horizontal Pod Autoscaler Foundation

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G53  
**归属：** Platform Release / Operations boundary

## 背景

G51/G52 交付单副本 Gateway 与可选 Ingress。需 opt-in HPA 声明以支持 CPU 水平扩缩，但不引入 Service Mesh 或多区域。

## 决策

1. 在 `deploy/helm/eaos` 增加 `autoscaling` values（默认 `enabled: false`）。  
2. 模板：`autoscaling/v2` HorizontalPodAutoscaler，目标为 Gateway Deployment；默认指标 CPU。  
3. `autoscaling.enabled=true` 时 Deployment **省略** `spec.replicas`（由 HPA 管理）；否则沿用 `replicaCount`。  
4. 文档：`docs/release/HPA.md`；契约断言模板/values；不强制 metrics-server 安装。  
5. 不 bump 包版本（仍 `0.2.0`）；无 Alembic；不交付 Service Mesh / 多区域。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 安装 metrics-server / Prometheus Adapter  
- VPA Foundation（见 ADR-0073 / PHX-G54）；KEDA / Service Mesh 仍延后  
- 多区域 / 多 IdP UI  

## 关联

- [ADR-0070-helm-foundation.md](ADR-0070-helm-foundation.md)
- [ADR-0071-ingress-tls-foundation.md](ADR-0071-ingress-tls-foundation.md)
- [ADR-0073-vpa-foundation.md](ADR-0073-vpa-foundation.md)
- [../project/PHX-G53_ARCHITECTURE_GATE.md](../project/PHX-G53_ARCHITECTURE_GATE.md)
- [../release/HPA.md](../release/HPA.md)
