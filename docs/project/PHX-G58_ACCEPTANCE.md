# PHX-G58 KEDA Foundation Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**退出门禁：** opt-in ScaledObject；默认关；与 HPA/VPA 互斥；不安装 operator；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0077 + Architecture Gate |
| B | Helm `keda` values + `keda-scaledobject.yaml` |
| C | `KEDA.md` + HELM/HPA/VPA/Runbook 交叉链接 |
| D | 契约 `test_ops_g58` |

## 2. 核心不变量

- 默认 `keda.enabled=false`  
- 与 HPA / VPA 互斥 → Helm `fail`  
- 启用时省略 Deployment `replicas`  
- 不捆绑 KEDA operator  

## 3. 自动化证据

- 本地完整回归：`510 passed`（`tests/contracts`）  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0077 |
| Constitution Review | 通过；Release/Ops 边界 |
| Cross-reference Review | 通过；G53/G54 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0` |
| Gap Analysis | Service Mesh、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 安装 KEDA operator / CRDs  
- Service Mesh / mTLS / 多区域  

## 6. 证据索引

- [PHX-G58 Architecture Gate](PHX-G58_ARCHITECTURE_GATE.md)
- [ADR-0077](../decisions/ADR-0077-keda-foundation.md)
- [KEDA.md](../release/KEDA.md)
