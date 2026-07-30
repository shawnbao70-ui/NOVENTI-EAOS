# PHX-G49 Production Deploy Topology Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**退出门禁：** 单主机拓扑 + Runbook 扩展 + 契约锁定；无 schema / 版本 bump  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0068 + Architecture Gate |
| B | `docs/release/PRODUCTION_TOPOLOGY.md` |
| C | `OPERATIONS_RUNBOOK.md` / Checklist 扩展 |
| D | `test_ops_g49` + 七步自审 |

## 2. 核心不变量

- 参考拓扑 = 单主机 Gateway + PostgreSQL  
- 生产基线：`REQUIRE_JWT=1`、关闭开发头  
- 不交付 Compose/K8s；不 bump `0.2.0`  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`466 passed`（`tests/contracts`；以实测为准）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0068 |
| Constitution Review | 通过；运维边界不侵入 Kernel |
| Cross-reference Review | 通过；R17 runbook 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；版本仍 `0.2.0` |
| Gap Analysis | K8s/Helm、多区域、多 IdP UI、支付清算另批；Compose 见 G50 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Kubernetes / Helm（Compose Foundation 见 PHX-G50）  
- 多区域 failover  
- 多 IdP 联邦管理 UI  

## 6. 证据索引

- [PHX-G49 Architecture Gate](PHX-G49_ARCHITECTURE_GATE.md)
- [ADR-0068](../decisions/ADR-0068-production-deploy-topology.md)
- [PRODUCTION_TOPOLOGY.md](../release/PRODUCTION_TOPOLOGY.md)
