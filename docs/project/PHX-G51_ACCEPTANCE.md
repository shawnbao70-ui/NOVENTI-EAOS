# PHX-G51 Kubernetes Helm Foundation Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**退出门禁：** `deploy/helm/eaos` 映射 G49 拓扑；契约锁定；无 schema / 版本 bump  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0070 + Architecture Gate |
| B | Helm Chart（Gateway Deployment + 可选 Postgres） |
| C | `HELM.md` + Runbook / Topology 交叉引用 |
| D | `test_ops_g51` + 七步自审 |

## 2. 核心不变量

- 单副本 Gateway；可选捆绑 Postgres  
- 安全基线与 G49 一致；密钥经 Secret  
- 不交付 Ingress/HPA/多区域；不 bump `0.2.0`  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`478 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0070 |
| Constitution Review | 通过；运维边界 |
| Cross-reference Review | 通过；G49/G50 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；版本仍 `0.2.0` |
| Gap Analysis | Controller 安装、Mesh、多区域、多 IdP UI、支付清算另批；Ingress 声明见 G52 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 安装 Ingress Controller / cert-manager（声明见 PHX-G52）  
- Service Mesh / HPA / 多副本 / 多区域  
- 多 IdP 联邦管理 UI  

## 6. 证据索引

- [PHX-G51 Architecture Gate](PHX-G51_ARCHITECTURE_GATE.md)
- [ADR-0070](../decisions/ADR-0070-helm-foundation.md)
- [HELM.md](../release/HELM.md)
