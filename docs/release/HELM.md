# EAOS Helm Chart — Phoenix Foundation

**Version:** 0.2.3  
**Milestones:** PHX-G51 · PHX-G52 · PHX-G53 · PHX-G54 · PHX-G58 · PHX-G59 · PHX-G144 · **PHX-G409**（version parity）  
**Prior Foundation baseline:** `0.2.1`（chart）· `0.2.0`（PHX-R17）  
**Normative:** ADR-0070 · ADR-0071 · ADR-0072 · ADR-0073 · ADR-0077 · ADR-0078  
**Topology:** [PRODUCTION_TOPOLOGY.md](PRODUCTION_TOPOLOGY.md) · Compose: [COMPOSE.md](COMPOSE.md) · Ingress: [INGRESS.md](INGRESS.md) · HPA: [HPA.md](HPA.md) · VPA: [VPA.md](VPA.md) · KEDA: [KEDA.md](KEDA.md) · Mesh: [MESH.md](MESH.md)

## 1. What this maps

| Helm resource | Topology role |
|---------------|---------------|
| `*-gateway` Deployment + Service | uvicorn Gateway + `/terminal/`（镜像 entrypoint 含 migrate） |
| `*-postgres` StatefulSet + Service（可选） | PostgreSQL |
| `*-secrets` Secret | `EAOS_DATABASE_URL` / `EAOS_JWT_SECRET` / DB password |
| Ingress（可选，默认关） | 外部 HTTP(S) → Gateway（PHX-G52） |
| HPA（可选，默认关） | Gateway CPU 水平扩缩（PHX-G53） |
| VPA（可选，默认关） | Gateway 资源建议/写回；与 HPA 互斥（PHX-G54） |
| KEDA ScaledObject（可选，默认关） | Gateway 事件/资源扩缩；与 HPA/VPA 互斥（PHX-G58） |
| Mesh 注入（可选，默认关） | Gateway Pod/Service 标签与注解；不渲染网格 CRD（PHX-G59） |

## 2. Artifacts

| Path | Purpose |
|------|---------|
| `deploy/helm/eaos/Chart.yaml` | Chart metadata `0.2.3`（aligned to package / RELEASE_MANIFEST） |
| `deploy/helm/eaos/values.yaml` | Defaults + secret placeholders |
| `deploy/helm/eaos/templates/*` | Gateway / Postgres / Secret / Ingress / HPA / VPA / KEDA / Mesh labels + opt-in PA / VS / DR / Authz |

## 3. Quick start

```bash
# 1) Build image from G50 Dockerfile and load/push to your registry
docker build -f deploy/docker/Dockerfile -t noventi/eaos-gateway:0.2.3 .

# 2) Create values overlay (do not commit secrets)
# secrets.jwtSecret / secrets.postgresPassword must be replaced

helm upgrade --install eaos deploy/helm/eaos \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME \
  --set image.repository=noventi/eaos-gateway \
  --set image.tag=0.2.3

kubectl port-forward svc/eaos-eaos-gateway 8000:8000
curl http://127.0.0.1:8000/v1/health
```

External database:

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set postgres.enabled=false \
  --set gateway.databaseUrl='postgresql+psycopg://...' \
  --set secrets.jwtSecret=REPLACE_ME
```

## 4. Security baseline

- `EAOS_REQUIRE_JWT=1`、`EAOS_ALLOW_DEV_CONTEXT_HEADERS=0`（values 默认）  
- 密钥仅经 Secret / `--set` / private values 文件  
- Marketplace 支付清算仍 fail-closed  

## 5. Ingress / TLS (PHX-G52)

默认关闭。启用与 TLS / cert-manager 注解见 [INGRESS.md](INGRESS.md)。

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=eaos.example.local \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 6. HPA (PHX-G53)

默认关闭。启用见 [HPA.md](HPA.md)。

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set autoscaling.enabled=true \
  --set resources.requests.cpu=100m \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 7. VPA (PHX-G54)

默认关闭；与 HPA 互斥。见 [VPA.md](VPA.md)。

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set vpa.enabled=true \
  --set vpa.updateMode=Off \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 8. KEDA (PHX-G58)

默认关闭；与 HPA / VPA 互斥。见 [KEDA.md](KEDA.md)。

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set keda.enabled=true \
  --set resources.requests.cpu=100m \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 9. Service Mesh (PHX-G59 / PHX-G71–G73)

默认关闭。启用 sidecar 注入与可选 Istio PeerAuthentication / VS / DR / AuthorizationPolicy 见 [MESH.md](MESH.md)。

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set mesh.enabled=true \
  --set mesh.policy.enabled=true \
  --set mesh.traffic.enabled=true \
  --set mesh.authz.enabled=true \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 10. Deploy Region (PHX-G76)

可选部署区域身份标签（默认空）。见 [REGION.md](REGION.md)。

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set region.id=ap-east-1 \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 11. Explicit non-goals

- 安装 Ingress Controller / cert-manager / metrics-server / VPA components / KEDA operator / Mesh 控制面  
- JWT claim 细粒度规则 / 权重分流 / Linkerd 策略 CRD  
- 多区域生产 SaaS / failover / 只读副本（区域标签见 G76，非本非目标）  
- 公有镜像仓库与托管 CI  
- 多 IdP 管理 UI  
- 包版本 bump 超出当前 Foundation baseline（chart/appVersion/image.tag 必须与 `RELEASE_MANIFEST` / `pyproject` 对齐；当前 `0.2.3`）
