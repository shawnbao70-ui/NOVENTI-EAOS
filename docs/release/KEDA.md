# EAOS KEDA ScaledObject — Phoenix Foundation

**Version:** 0.2.1  
**Prior Foundation baseline:** `0.2.0`（PHX-R17）  
**Milestone:** PHX-G58  
**Normative:** ADR-0077  
**Chart:** [HELM.md](HELM.md) · `deploy/helm/eaos`

## 1. Scope

Opt-in KEDA `ScaledObject` 对 Gateway Deployment 做 CPU（可选 Memory）扩缩。默认 `keda.enabled=false`（固定 `replicaCount`）。

| Item | Foundation behavior |
|------|---------------------|
| API | `keda.sh/v1alpha1` ScaledObject |
| Target | Gateway Deployment only |
| Triggers | CPU Utilization；可选 Memory |
| KEDA operator | **不**安装；集群需已有 CRDs |

启用 KEDA 时 Deployment **不**设置 `spec.replicas`。

## 2. Enable KEDA

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME \
  --set keda.enabled=true \
  --set keda.minReplicaCount=1 \
  --set keda.maxReplicaCount=3 \
  --set keda.cpu.targetUtilizationPercentage=70 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=256Mi
```

CPU 触发需要容器 `resources.requests.cpu`（否则利用率无法计算）。

## 3. Notes

- 捆绑 Postgres StatefulSet **不**随 KEDA 扩缩。  
- Marketplace 支付清算仍 fail-closed。  

## 4. Mutual exclusion with HPA / VPA

Do **not** enable KEDA together with HPA 或 VPA（见 [HPA.md](HPA.md) / [VPA.md](VPA.md)）。Chart 在冲突时 `fail`。

## 5. Explicit non-goals

- 安装 KEDA operator / CRDs / metrics-server  
- Service Mesh 控制面安装（声明式注入见 [MESH.md](MESH.md) / PHX-G59）  
- 多区域  
- 包版本 bump 至 `0.2.1+`
