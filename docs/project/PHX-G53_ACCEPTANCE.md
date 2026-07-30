# PHX-G53 HPA Foundation Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**退出门禁：** opt-in HPA；默认关闭；启用时省略 Deployment.replicas；无 schema / 版本 bump  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0072 + Architecture Gate |
| B | `templates/hpa.yaml` + values `autoscaling.*` |
| C | Deployment replicas 条件渲染 |
| D | `HPA.md` + `test_ops_g53` + 七步自审 |

## 2. 核心不变量

- `autoscaling.enabled` 默认 `false`  
- API `autoscaling/v2`；不安装 metrics-server  
- 不交付 VPA / Mesh / 多区域  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`488 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0072 |
| Constitution Review | 通过；运维边界 |
| Cross-reference Review | 通过；G51/G52 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；版本仍 `0.2.0` |
| Gap Analysis | metrics-server 安装、KEDA、Mesh、多 IdP UI、支付清算另批；VPA 见 G54 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 安装 metrics-server / Prometheus Adapter  
- KEDA / Service Mesh（VPA 见 PHX-G54）  
- 多区域 / 多 IdP UI  

## 6. 证据索引

- [PHX-G53 Architecture Gate](PHX-G53_ARCHITECTURE_GATE.md)
- [ADR-0072](../decisions/ADR-0072-hpa-foundation.md)
- [HPA.md](../release/HPA.md)
