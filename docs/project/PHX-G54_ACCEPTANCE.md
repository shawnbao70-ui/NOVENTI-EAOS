# PHX-G54 VPA Foundation Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**退出门禁：** opt-in VPA；默认关闭；与 HPA 互斥 fail-closed；无 schema / 版本 bump  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0073 + Architecture Gate |
| B | `templates/vpa.yaml` + values `vpa.*` |
| C | HPA/VPA 互斥 Helm fail |
| D | `VPA.md` + `test_ops_g54` + 七步自审 |

## 2. 核心不变量

- `vpa.enabled` 默认 `false`；`updateMode` 默认 `Off`  
- 与 `autoscaling.enabled` 互斥  
- 不安装 VPA components  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`493 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0073 |
| Constitution Review | 通过；运维边界 |
| Cross-reference Review | 通过；G53 HPA 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；版本仍 `0.2.0` |
| Gap Analysis | VPA 组件安装、Mesh/KEDA、支付清算另批；多 IdP 只读 UI 见 G55 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 安装 VPA recommender/updater  
- Service Mesh / KEDA  
- 多区域（多 IdP 只读 UI 见 PHX-G55）  

## 6. 证据索引

- [PHX-G54 Architecture Gate](PHX-G54_ARCHITECTURE_GATE.md)
- [ADR-0073](../decisions/ADR-0073-vpa-foundation.md)
- [VPA.md](../release/VPA.md)
