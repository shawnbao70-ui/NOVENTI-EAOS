# Fulfillment Deepen — Index

**Source root:** `H:\Workspace\EZAM_CRM - 9.0`（只读） · **Verified:** 2026-07-23

| Topic | File | Runtime conclusion | Evidence strength |
|---|---|---|---|
| Reservation | [reservation.md](reservation.md) | 库存只有 on-hand/safety/location；DO 创建不占库，Ship 才校验并扣减 | Strong negative（预留缺失） |
| Partial delivery | [partial_delivery.md](partial_delivery.md) | 一个 DO 复制整张 SO 全部行；可重复建 DO，但无累计已发/剩余控制 | Strong（整单 Ship）/ Missing（部分履约） |
| Returns / reversal / reopen | [returns_reversal.md](returns_reversal.md) | DO reopen 仅改状态，不回补库存；退货/RMA/credit-note 运行闭环缺失 | Strong（重开）/ Strong negative（反向闭环） |
| Warehouse | [warehouse.md](warehouse.md) | 运行库存以每产品一行加自由文本 location 表达；warehouse/bin 主数据仅规范或 metadata | Strong（扁平库存）/ Missing（仓库组织） |

## Required search coverage

- `apps/inventory/**`
- `apps/sales/**`
- `templates/inventory*`、`templates/sales_order*`、`templates/delivery_order*`、仓库/退货相关模板检索
- `business_modules/inventory.md`、`sales.md`、`shipment.md`
- `docs/reports/Business_Strong_A002/A003/A009/A018*`
- `docs/reports/V151E_Volume010*`、`V18_SO_DO_Invoice_TypeA_Report.md`、`V18_P5_Recognize_Gate_Report.md`
- `runtime/v14/legacy_support.py` 与相关 schema/callsites

## Existing-pack references

- 库存与交付既有知识：[../ops/](../ops/)、[../delivery/](../delivery/)
- 销售订单既有知识：[../sales/](../sales/)

本包不重写上述正文，只补足履约深水区的负证据、边界和风险。
