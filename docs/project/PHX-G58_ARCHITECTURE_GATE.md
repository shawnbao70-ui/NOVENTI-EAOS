# PHX-G58 KEDA Foundation Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0077  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Opt-in KEDA ScaledObject；默认关；与 HPA/VPA 互斥；不安装 operator。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `keda.enabled`（默认 false） |
| API | `keda.sh/v1alpha1` ScaledObject |
| Target | Gateway Deployment |
| Mutex | vs `autoscaling` / `vpa` → Helm `fail` |
| Operator | 集群自备；chart 不捆绑 |

## 3. Exit Criteria

1. ADR-0077 Accepted。  
2. 模板 + `KEDA.md` + 契约绿；包版本仍 `0.2.0`。  
3. 全量 contracts 绿。  

见 [PHX-G58_ACCEPTANCE.md](PHX-G58_ACCEPTANCE.md)。
