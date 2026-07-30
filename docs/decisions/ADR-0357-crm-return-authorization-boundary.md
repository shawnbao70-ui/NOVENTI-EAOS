# ADR-0357 — CRM Return Authorization Shell Boundary

**状态：** Accepted（PHX-G325 / RET1）  
**日期：** 2026-07-26  
**里程碑：** PHX-G325  
**归属：** Business Package / CRM（非 Inventory 写路径；非 Finance 冲销）  
**授权源：** [Coding Authorization](../project/CRM_RETURN_AUTHORIZATION_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

Legacy 无运行级 RMA 授权链。EAOS RET1 仅建立 documentary Return Authorization，挂靠已发运 DO，可选关联同谱系 AR 发票；不回补库存、不自动红冲。

## 决策

1. 资源 `pkg.crm.return_authorization`；实体仅 `draft`；create + get。  
2. 前置：DO 已 shipped（I1）；若带 `invoice_id` 则须同租户且商业谱系一致，状态 `issued|voided`，fail closed。  
3. `unique(tenant, delivery_order_id)` 与 `unique(tenant, idempotency_key)`。  
4. Commercial hold 不阻断 RET1 create（Accept）。  
5. RET2 入库回补、自动 Credit Note、PSP 退款、Brain/Twin Out。

## 关联

- [ADR-0338](ADR-0338-inventory-do-ship-ledger-boundary.md)  
- [Coding Authorization](../project/CRM_RETURN_AUTHORIZATION_CODING_AUTHORIZATION_SUMMARY.md)  
- [POST_CRM_VERTICAL_ROADMAP](../project/POST_CRM_VERTICAL_ROADMAP.md)
