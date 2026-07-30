# PHX-G51 Kubernetes Helm Foundation Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0070  
**人工确认：** 支付清算另批  

## 1. 门禁目标

交付映射 G49 拓扑的最小 Helm chart（单副本 Gateway + 可选 Postgres）。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Layout | `deploy/helm/eaos/` |
| Workloads | Gateway Deployment；可选 Postgres StatefulSet |
| Ingress | 本切片不交付 |
| Version | 保持 `0.2.0` |

## 3. Exit Criteria

1. ADR-0070 Accepted。  
2. Chart + HELM.md + 契约绿。  
3. 全量 contracts 绿；无 Alembic / 版本 bump。  

## 4. 验收

见 [PHX-G51_ACCEPTANCE.md](PHX-G51_ACCEPTANCE.md)；契约 `478 passed`。
