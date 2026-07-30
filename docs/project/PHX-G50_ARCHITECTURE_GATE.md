# PHX-G50 Docker Compose Foundation Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**规范源：** ADR-0069  
**人工确认：** 支付清算另批  

## 1. 门禁目标

交付映射 G49 单主机拓扑的最小 Docker Compose 参考实现。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Layout | `deploy/docker/` |
| Services | `db` + `gateway` |
| K8s | 本切片不交付 |
| Version | 保持 `0.2.0` |

## 3. Exit Criteria

1. ADR-0069 Accepted。  
2. Compose 可描述 db+gateway；文档与契约绿。  
3. 全量 contracts 绿；无 Alembic / 版本 bump。  

## 4. 验收

见 [PHX-G50_ACCEPTANCE.md](PHX-G50_ACCEPTANCE.md)；契约 `472 passed`。
