# PHX-G52 Ingress / TLS Foundation Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0071  
**人工确认：** 支付清算另批  

## 1. 门禁目标

为 Helm chart 增加 opt-in Ingress + TLS 声明；默认关闭。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Default | `ingress.enabled=false` |
| API | `networking.k8s.io/v1` |
| cert-manager | 仅注解；不安装 Operator |
| Version | 保持 `0.2.0` |

## 3. Exit Criteria

1. ADR-0071 Accepted。  
2. Ingress 模板 + INGRESS.md + 契约绿。  
3. 全量 contracts 绿；无 Alembic / 版本 bump。  

## 4. 验收

见 [PHX-G52_ACCEPTANCE.md](PHX-G52_ACCEPTANCE.md)；契约 `483 passed`。
