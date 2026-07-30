# PHX-G50 Docker Compose Foundation Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**退出门禁：** `deploy/docker` Compose 映射 G49 拓扑；契约锁定；无 schema / 版本 bump  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0069 + Architecture Gate |
| B | `Dockerfile` / `compose.yaml` / `entrypoint.py` / `.env.example` |
| C | `COMPOSE.md` + Runbook / Topology 交叉引用 |
| D | `test_ops_g50` + 七步自审 |

## 2. 核心不变量

- 服务 = `db` + `gateway`（migrate → uvicorn）  
- 安全基线与 G49 一致；密钥不入库  
- 不交付 K8s/Helm；不 bump `0.2.0`  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`472 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0069 |
| Constitution Review | 通过；运维边界 |
| Cross-reference Review | 通过；G49 拓扑仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；版本仍 `0.2.0` |
| Gap Analysis | Ingress、多区域、多 IdP UI、支付清算另批；Helm 见 G51 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 公有镜像仓库推送（Helm Foundation 见 PHX-G51）  
- 多区域 / 多副本  
- 多 IdP 联邦管理 UI  

## 6. 证据索引

- [PHX-G50 Architecture Gate](PHX-G50_ARCHITECTURE_GATE.md)
- [ADR-0069](../decisions/ADR-0069-docker-compose-foundation.md)
- [COMPOSE.md](../release/COMPOSE.md)
