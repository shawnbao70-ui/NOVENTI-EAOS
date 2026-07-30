# PHX-G52 Ingress / TLS Foundation Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**退出门禁：** opt-in Ingress + TLS 声明；默认关闭；契约锁定；无 schema / 版本 bump  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0071 + Architecture Gate |
| B | `templates/ingress.yaml` + values `ingress.*` |
| C | `INGRESS.md` + Runbook / Helm 交叉引用 |
| D | `test_ops_g52` + 七步自审 |

## 2. 核心不变量

- `ingress.enabled` 默认 `false`  
- TLS Secret 或 cert-manager 注解；不安装 Controller/Operator  
- 不替代 Gateway JWT 边界  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`483 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0071 |
| Constitution Review | 通过；运维边界 |
| Cross-reference Review | 通过；G51 Helm 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；版本仍 `0.2.0` |
| Gap Analysis | Controller 安装、Mesh、多区域、多 IdP UI、支付清算另批；HPA 见 G53 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 安装 Ingress Controller / cert-manager  
- Service Mesh / 多区域（HPA 见 PHX-G53）  
- 多 IdP 联邦管理 UI  

## 6. 证据索引

- [PHX-G52 Architecture Gate](PHX-G52_ARCHITECTURE_GATE.md)
- [ADR-0071](../decisions/ADR-0071-ingress-tls-foundation.md)
- [INGRESS.md](../release/INGRESS.md)
