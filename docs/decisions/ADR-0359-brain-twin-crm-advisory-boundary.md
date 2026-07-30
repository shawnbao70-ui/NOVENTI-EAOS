# ADR-0359 — Brain/Twin CRM Advisory Projection Boundary

**状态：** Accepted（PHX-G327 / Z3）  
**日期：** 2026-07-26  
**里程碑：** PHX-G327  
**归属：** Business Package / CRM（只读投影；非执行授权）  
**授权源：** [Coding Authorization](../project/BRAIN_TWIN_CRM_ADVISORY_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

Z1 已交付 Customer360 只读组装。平台 Brain/Twin 执行面必须保持关闭。Z3 仅把既有 Twin/Brain **advisory** 记录挂到客户只读投影，不打开 execute/authorize。

## 决策

1. HTTP：`GET /v1/crm/customers/{id}/advisory`；不写入 `/360`。  
2. Envelope 仅含引用/摘要/`execution_authority="none"`；无命令字段。  
3. Brain `execute` 与 Twin `authorize` 保持 fail-closed 403；本切片不得改为成功。  
4. 无新 Alembic 表（OD-01 Defer）；live assemble。  
5. 不推荐佣金/Cap→grant；不驱动 SO/DO/发票/收款写路径。

## 关联

- Customer360 / Z1 artifacts  
- [Coding Authorization](../project/BRAIN_TWIN_CRM_ADVISORY_CODING_AUTHORIZATION_SUMMARY.md)  
- [POST_CRM_VERTICAL_ROADMAP](../project/POST_CRM_VERTICAL_ROADMAP.md)
