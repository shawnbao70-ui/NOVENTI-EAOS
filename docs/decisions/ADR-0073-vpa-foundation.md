# ADR-0073 — Vertical Pod Autoscaler Foundation

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G54  
**归属：** Platform Release / Operations boundary

## 背景

G53 交付 opt-in HPA。需可选 VPA 声明以建议/调整 Gateway 资源请求，且与 HPA 互斥，避免同一工作负载双控制器冲突。

## 决策

1. 在 `deploy/helm/eaos` 增加 `vpa` values（默认 `enabled: false`）。  
2. 模板：`autoscaling.k8s.io/v1` VerticalPodAutoscaler，目标 Gateway Deployment。  
3. 默认 `updateMode: Off`（仅推荐，不写回）；可配置 `Initial` / `Auto`。  
4. **互斥：** `autoscaling.enabled` 与 `vpa.enabled` 同时为 true 时 Helm `fail`（fail-closed）。  
5. 文档：`docs/release/VPA.md`；契约断言；不安装 VPA recommender/updater。  
6. 不 bump 包版本（仍 `0.2.0`）；无 Alembic；不交付 Service Mesh / KEDA / 多区域。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 安装 VPA components / metrics-server  
- Service Mesh / KEDA  
- 多区域 / 多 IdP UI  

## 关联

- [ADR-0072-hpa-foundation.md](ADR-0072-hpa-foundation.md)
- [../project/PHX-G54_ARCHITECTURE_GATE.md](../project/PHX-G54_ARCHITECTURE_GATE.md)
- [../release/VPA.md](../release/VPA.md)
