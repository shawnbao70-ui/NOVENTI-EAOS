# ADR-0077 — KEDA Foundation

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G58  
**归属：** Platform Release / Operations boundary

## 背景

G53/G54 交付 opt-in HPA/VPA。需可选 KEDA `ScaledObject` 声明以事件/资源触发扩缩 Gateway，且不与 HPA/VPA 双控同一副本数。

## 决策

1. 在 `deploy/helm/eaos` 增加 `keda` values（默认 `enabled: false`）。  
2. 模板：`keda.sh/v1alpha1` ScaledObject，目标 Gateway Deployment；默认 CPU Utilization trigger。  
3. 启用 KEDA 时 Deployment **省略** `spec.replicas`（与 HPA 同型）。  
4. **互斥：** `keda.enabled` 与 `autoscaling.enabled` 或 `vpa.enabled` 同时为 true 时 Helm `fail`。  
5. 文档：`docs/release/KEDA.md`；契约断言；**不**安装 KEDA operator / CRDs。  
6. 不 bump 包版本（仍 `0.2.0`）；无 Alembic；Service Mesh 另切片。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 安装 KEDA operator / CRDs / metrics-server  
- Service Mesh / mTLS  
- 多区域 / 队列触发器产品化（Foundation 仅声明 CPU；可配置扩展）  

## 关联

- [ADR-0072-hpa-foundation.md](ADR-0072-hpa-foundation.md)
- [ADR-0073-vpa-foundation.md](ADR-0073-vpa-foundation.md)
- [../project/PHX-G58_ARCHITECTURE_GATE.md](../project/PHX-G58_ARCHITECTURE_GATE.md)
- [../release/KEDA.md](../release/KEDA.md)
