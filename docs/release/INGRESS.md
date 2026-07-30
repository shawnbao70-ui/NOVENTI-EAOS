# EAOS Ingress / TLS — Phoenix Foundation

**Version:** 0.2.1  
**Prior Foundation baseline:** `0.2.0`（PHX-R17）  
**Milestone:** PHX-G52  
**Normative:** ADR-0071  
**Chart:** [HELM.md](HELM.md) · `deploy/helm/eaos`

## 1. Scope

Opt-in Kubernetes Ingress 将外部 HTTP(S) 流量路由到 Gateway Service。默认 `ingress.enabled=false`（ClusterIP + port-forward 仍可用）。

| Item | Foundation behavior |
|------|---------------------|
| API | `networking.k8s.io/v1` Ingress |
| Path | `/` Prefix → Gateway Service |
| TLS | `ingress.tls[].secretName` 或 cert-manager 注解 |
| Controllers | **不**安装；集群需已有 Ingress Controller |

## 2. Enable Ingress

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=eaos.example.local
```

## 3. TLS options

### 3.1 Manual TLS Secret

```bash
kubectl create secret tls eaos-tls --cert=tls.crt --key=tls.key

helm upgrade --install eaos deploy/helm/eaos \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=eaos.example.local \
  --set ingress.tls[0].secretName=eaos-tls \
  --set ingress.tls[0].hosts[0]=eaos.example.local \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

### 3.2 cert-manager annotations (Operator not bundled)

Prerequisite: cert-manager + ClusterIssuer already installed in the cluster.

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=eaos.example.local \
  --set ingress.certManager.enabled=true \
  --set ingress.certManager.clusterIssuer=letsencrypt-prod \
  --set ingress.tls[0].secretName=eaos-tls \
  --set ingress.tls[0].hosts[0]=eaos.example.local \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

Template writes annotation `cert-manager.io/cluster-issuer` when `ingress.certManager.enabled=true`.

## 4. Security notes

- Gateway 仍要求 `EAOS_REQUIRE_JWT=1`；Ingress 不替代认证边界。  
- 勿将真实证书私钥提交入库。  
- Marketplace 支付清算仍 fail-closed。  

## 5. Explicit non-goals

- 安装 Ingress Controller / cert-manager  
- Service Mesh 控制面安装（声明式注入见 [MESH.md](MESH.md) / PHX-G59）  
- HPA（见 [HPA.md](HPA.md) / PHX-G53）；多区域仍延后  
- 多 IdP UI  
- 包版本 bump 至 `0.2.1+`
