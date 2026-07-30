# ADR-0070 — Kubernetes Helm Foundation (Single-Replica)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G51  
**归属：** Platform Release / Operations boundary

## 背景

G49/G50 已交付单主机拓扑与 Compose 参考。需最小 Helm chart 将同一拓扑映射到 Kubernetes，作为后续生产编排基线，而非多区域或 Operator 产品化。

## 决策

1. 交付路径：`deploy/helm/eaos/`（Chart + values + templates）。  
2. 工作负载：单副本 Gateway Deployment；可选捆绑 Postgres（StatefulSet + PVC），也可指向外部 `EAOS_DATABASE_URL`。  
3. 密钥经 Kubernetes Secret（由 values 注入）；不提交真实密钥；安全基线与 G49 一致。  
4. 契约断言 chart 文件存在、`Chart.yaml`/`values.yaml` 可解析、模板含关键资源与 env；不强制集群 `helm install`。  
5. 不 bump 包版本（仍 `0.2.0`）；无 Alembic 变更；不交付 Ingress Controller / Operator / 多区域。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Ingress / TLS Foundation（见 ADR-0071 / PHX-G52）；Service Mesh 仍延后  
- HPA（见 ADR-0072 / PHX-G53）；多区域 failover 仍延后  
- 公有镜像仓库推送与托管 CI  
- 多 IdP 联邦管理 UI  

## 关联

- [ADR-0068-production-deploy-topology.md](ADR-0068-production-deploy-topology.md)
- [ADR-0069-docker-compose-foundation.md](ADR-0069-docker-compose-foundation.md)
- [ADR-0071-ingress-tls-foundation.md](ADR-0071-ingress-tls-foundation.md)
- [../project/PHX-G51_ARCHITECTURE_GATE.md](../project/PHX-G51_ARCHITECTURE_GATE.md)
- [../release/HELM.md](../release/HELM.md)
