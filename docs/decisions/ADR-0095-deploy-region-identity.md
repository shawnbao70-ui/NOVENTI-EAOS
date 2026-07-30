# ADR-0095 — Deploy Region Identity Foundation

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G76  
**归属：** Platform Ops / Gateway status surface

## 背景

拓扑与网格已覆盖单主机参考部署。运维需可标注「本实例所属部署区域」，但不引入跨区域 failover / SaaS 多活（`RELEASE_MANIFEST` 非目标 `multi_region_production_saas`）。

## 决策

1. 可选环境变量 `EAOS_DEPLOY_REGION`（空 = 未标注单主机，合法默认）。  
2. Helm `region.id` 写入 Gateway env；可选 pod label `eaos.noventi.io/deploy-region`。  
3. Compose / `.env.example` 暴露同名变量。  
4. `GET /v1/release` 暴露 `deploy_region`（未设置时为 `null`；永不含密钥）。  
5. 非目标：跨区域 DB 复制、failover runbook、只读副本、跨 AZ 仲裁、多集群 mesh 联邦。  
6. 与租户 `region_policy_ref`（驻留/法域策略引用）分离；与 `EAOS_OIDC_REFRESH_KMS_REGION`（AWS KMS）分离。  
7. 无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 联邦策略矩阵 UI  
- 多区域生产 SaaS / failover / 只读副本  

## 关联

- [ADR-0068-production-topology-foundation.md](ADR-0068-production-topology-foundation.md)
- [../project/PHX-G76_ARCHITECTURE_GATE.md](../project/PHX-G76_ARCHITECTURE_GATE.md)
- [../release/REGION.md](../release/REGION.md)
