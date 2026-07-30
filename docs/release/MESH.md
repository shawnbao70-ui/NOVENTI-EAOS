# EAOS Service Mesh — Phoenix Foundation

**Version:** 0.2.1  
**Prior Foundation baseline:** `0.2.0`（PHX-R17）  
**Milestone:** PHX-G59 / PHX-G71 / PHX-G72 / PHX-G73  
**Normative:** ADR-0078 / ADR-0090 / ADR-0091 / ADR-0092  
**Chart:** [HELM.md](HELM.md) · `deploy/helm/eaos`

## 1. Scope

Opt-in sidecar 注入 + 可选 Istio 安全/流量/授权 CRD。默认全部关闭。

| Item | Foundation behavior |
|------|---------------------|
| Inject | Pod labels/annotations；可选 Service annotations |
| Policy | Opt-in `PeerAuthentication`（STRICT） |
| Traffic | Opt-in `VirtualService` + `DestinationRule`（ISTIO_MUTUAL） |
| Authz | Opt-in `AuthorizationPolicy`（ALLOW 已认证 principals） |
| Control plane | **不**安装；集群需已有 Istio CRDs |

## 2. Enable Mesh inject

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME \
  --set mesh.enabled=true
```

Linkerd 注入示例（无 Foundation 策略/流量/授权 CRD）：

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set mesh.enabled=true \
  --set mesh.injectLabelKey=linkerd.io/inject \
  --set mesh.injectLabelValue=enabled \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 3. Enable Istio PeerAuthentication (PHX-G71)

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set mesh.enabled=true \
  --set mesh.policy.enabled=true \
  --set mesh.policy.mtlsMode=STRICT \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 4. Enable Istio VirtualService + DestinationRule (PHX-G72)

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set mesh.enabled=true \
  --set mesh.traffic.enabled=true \
  --set mesh.traffic.tlsMode=ISTIO_MUTUAL \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

可选：`--set mesh.traffic.host=eaos-gateway.default.svc.cluster.local`

## 5. Enable Istio AuthorizationPolicy (PHX-G73)

允许任一已认证 mesh 主体访问 Gateway（不替代应用 JWT）：

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set mesh.enabled=true \
  --set mesh.authz.enabled=true \
  --set mesh.authz.vendor=istio \
  --set mesh.authz.action=ALLOW \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

可选限制 paths（默认 `*`）：

```bash
--set mesh.authz.paths="{/v1/*,/terminal/*}"
```

`mesh.authz.enabled=true` without `mesh.enabled` → Helm fail-closed。  
`vendor` 非 `istio` → Helm fail-closed。

应用侧身份门禁仍依赖 `EAOS_REQUIRE_JWT` 等。

## 6. Notes

- Ingress（G52）与 Mesh 可并存。  
- Marketplace 支付清算仍 fail-closed。  

## 7. Explicit non-goals

- 安装 Istio / Linkerd / 其他控制面或 CNI  
- JWT claim / 租户细粒度授权规则  
- Linkerd 策略/流量 CRD  
- 多区域  
- 包版本 bump 至 `0.2.1+`
