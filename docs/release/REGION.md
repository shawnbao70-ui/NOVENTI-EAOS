# Deploy Region Identity (PHX-G76)

可选部署区域身份标签。标注「本实例属于哪一部署区域」，**不是**多区域生产 SaaS / failover。

## 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `EAOS_DEPLOY_REGION` | 空 | 小写 DNS-label 风格（`a-z0-9.-`，≤63）；空 = 未标注 |

## 观测

`GET /v1/release` → `data.deploy_region`（未设置时为 `null`）。

## Helm

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set region.id=ap-east-1 \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

- `region.id` → Gateway `EAOS_DEPLOY_REGION`
- `region.labelPods=true`（默认）时写入 pod label `eaos.noventi.io/deploy-region`

## Compose

在 `deploy/docker/.env` 设置 `EAOS_DEPLOY_REGION=...`（见 `.env.example`）。

## Non-goals

- 跨区域 failover / 只读副本 / 跨 AZ 仲裁  
- 多集群 mesh 联邦  
- 租户 `region_policy_ref`（驻留策略）  
- Marketplace 支付清算  

规范： [ADR-0095](../decisions/ADR-0095-deploy-region-identity.md)
