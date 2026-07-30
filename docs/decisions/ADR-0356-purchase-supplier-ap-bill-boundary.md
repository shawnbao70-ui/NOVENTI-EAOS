# ADR-0356 — Purchase Supplier + AP Bill Draft Boundary

**状态：** Accepted（PHX-G324 / AP1）  
**日期：** 2026-07-26  
**里程碑：** PHX-G324  
**归属：** Business Package / Purchase（非 Kernel；非 CRM Customer）  
**授权源：** [Coding Authorization](../project/PURCHASE_SUPPLIER_AP_BILL_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

Post-CRM / GL 队列已空。采购竖切以 Supplier + 应付账单草稿头为最小入口。Legacy `ap_records` 与付款未勾兑；ADR-0315 禁止把付款等同 AP 清算。本切片只建主数据与 draft bill，不开支付/匹配/过账。

## 决策

1. **Package** `noventi.purchase`，DB schema `purchase`；资源 `pkg.purchase.supplier`、`pkg.purchase.ap_bill`。  
2. **Supplier** 不是 CRM Customer；tenant-scoped code/name/status。  
3. **AP Bill** 仅 `draft`；无行项目（AP2）；不 issue/post。  
4. HTTP：`/v1/purchase/suppliers`、`/v1/purchase/ap-bills`。  
5. AP2–AP5、付款、PSP、GL、税、Brain/Twin Out。

## 关联

- [ADR-0315](ADR-0315-ar-ap-reconcile-rewrite-boundary.md)  
- [Coding Authorization](../project/PURCHASE_SUPPLIER_AP_BILL_CODING_AUTHORIZATION_SUMMARY.md)  
- [POST_CRM_VERTICAL_ROADMAP](../project/POST_CRM_VERTICAL_ROADMAP.md)
