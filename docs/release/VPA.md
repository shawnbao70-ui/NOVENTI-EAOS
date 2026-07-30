# EAOS Vertical Pod Autoscaler — Phoenix Foundation

**Version:** 0.2.1  
**Prior Foundation baseline:** `0.2.0`（PHX-R17）  
**Milestone:** PHX-G54  
**Normative:** ADR-0073  
**Chart:** [HELM.md](HELM.md) · HPA: [HPA.md](HPA.md)

## 1. Scope

Opt-in VPA 针对 Gateway Deployment 的 CPU/Memory 请求建议（或写回）。默认 `vpa.enabled=false`。

| Item | Foundation behavior |
|------|---------------------|
| API | `autoscaling.k8s.io/v1` VerticalPodAutoscaler |
| Target | Gateway Deployment only |
| Default mode | `Off`（仅推荐） |
| VPA components | **不**安装；集群需已有 |
| HPA | **互斥** — 同时启用 → Helm fail |

## 2. Enable VPA (recommend-only)

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME \
  --set vpa.enabled=true \
  --set vpa.updateMode=Off
```

`Auto` / `Initial` 会改写 Pod 资源；生产前确认 VPA updater 已部署且已关闭 HPA：

```bash
# Do NOT combine with --set autoscaling.enabled=true
helm upgrade --install eaos deploy/helm/eaos \
  --set vpa.enabled=true \
  --set vpa.updateMode=Initial \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 3. Mutual exclusion

| HPA (`autoscaling`) | VPA | KEDA | Result |
|---------------------|-----|------|--------|
| false | false | false | 固定 `replicaCount` + 手工 resources |
| true | false | false | HPA 管理副本数 |
| false | true | false | VPA 管理/建议资源 |
| false | false | true | KEDA 管理副本数（[KEDA.md](KEDA.md)） |
| 任意两个及以上 enabled | | | **Helm fail**（G54/G58） |

## 4. Explicit non-goals

- 安装 VPA recommender/updater/admission  
- Service Mesh 控制面（声明见 [MESH.md](MESH.md)）  
- 多区域  
- 多 IdP UI  
- 包版本 bump 至 `0.2.1+`  
- Marketplace 支付清算
