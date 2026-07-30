# PHX-G53 HPA Foundation Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0072  
**人工确认：** 支付清算另批  

## 1. 门禁目标

为 Gateway Deployment 增加 opt-in HPA；默认关闭。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Default | `autoscaling.enabled=false` |
| API | `autoscaling/v2` |
| Replicas | HPA 启用时省略 Deployment.replicas |
| Version | 保持 `0.2.0` |

## 3. Exit Criteria

1. ADR-0072 Accepted。  
2. HPA 模板 + HPA.md + 契约绿。  
3. 全量 contracts 绿；无 Alembic / 版本 bump。  

## 4. 验收

见 [PHX-G53_ACCEPTANCE.md](PHX-G53_ACCEPTANCE.md)；契约 `488 passed`。
