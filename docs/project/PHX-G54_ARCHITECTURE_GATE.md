# PHX-G54 VPA Foundation Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0073  
**人工确认：** 支付清算另批  

## 1. 门禁目标

为 Gateway Deployment 增加 opt-in VPA；默认关闭；与 HPA 互斥。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Default | `vpa.enabled=false`；`updateMode=Off` |
| API | `autoscaling.k8s.io/v1` |
| HPA | 同时启用 → Helm fail |
| Version | 保持 `0.2.0` |

## 3. Exit Criteria

1. ADR-0073 Accepted。  
2. VPA 模板 + VPA.md + 契约绿。  
3. 全量 contracts 绿；无 Alembic / 版本 bump。  

## 4. 验收

见 [PHX-G54_ACCEPTANCE.md](PHX-G54_ACCEPTANCE.md)；契约 `493 passed`。
