# EAOS Horizontal Pod Autoscaler — Phoenix Foundation

**Version:** 0.2.1  
**Prior Foundation baseline:** `0.2.0`（PHX-R17）  
**Milestone:** PHX-G53  
**Normative:** ADR-0072  
**Chart:** [HELM.md](HELM.md) · `deploy/helm/eaos`

## 1. Scope

Opt-in HPA 对 Gateway Deployment 做 CPU（可选 Memory）水平扩缩。默认 `autoscaling.enabled=false`（固定 `replicaCount`）。

| Item | Foundation behavior |
|------|---------------------|
| API | `autoscaling/v2` HorizontalPodAutoscaler |
| Target | Gateway Deployment only |
| Metrics | CPU utilization；可选 Memory |
| metrics-server | **不**安装；集群需已有 |

启用 HPA 时 Deployment **不**设置 `spec.replicas`。

## 2. Enable HPA

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=1 \
  --set autoscaling.maxReplicas=3 \
  --set autoscaling.targetCPUUtilizationPercentage=70 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=256Mi
```

CPU 目标需要容器 `resources.requests.cpu`（否则利用率无法计算）。

## 3. Notes

- Alembic migrate 在入口执行；PostgreSQL advisory lock 下并发 upgrade 通常可接受。多副本生产仍建议稳定外部 DB。  
- 捆绑 Postgres StatefulSet **不**随 HPA 扩缩。  
- Marketplace 支付清算仍 fail-closed。  

## 4. Mutual exclusion with VPA / KEDA

Do **not** enable HPA together with VPA（见 [VPA.md](VPA.md) / PHX-G54）或 KEDA（见 [KEDA.md](KEDA.md) / PHX-G58）。Chart 在冲突时 `fail`。

## 5. Explicit non-goals

- 安装 metrics-server / Prometheus Adapter / KEDA operator  
- Service Mesh 控制面（声明见 [MESH.md](MESH.md)）  
- 多区域  
- 多 IdP UI  
- 包版本 bump 至 `0.2.1+`
