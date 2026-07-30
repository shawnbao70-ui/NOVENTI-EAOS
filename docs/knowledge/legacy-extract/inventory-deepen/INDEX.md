# Inventory Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| 现存量权威 | [stock_ledger.md](stock_ledger.md) | 强 | 运行操作写 `inventory.stock_qty`，并镜像产品库存 |
| 库存流水 | [stock_ledger.md](stock_ledger.md) | 强 | 流水保存变动量、过账后结余、类型、备注和时间 |
| PO/DO 过账 | [stock_ledger.md](stock_ledger.md) | 强 | 收货/发货动作才改变库存，建单不改变 |
| 盘点 | [stocktake.md](stocktake.md) | 强（调整）/缺失（盘点单） | Cycle Count 是手工调整类型，不是完整盘点流程 |
| 盈亏调整 | [stocktake.md](stocktake.md) | 强 | 以差异 delta 过账，零差异和负余额被拒绝 |
| 调拨 | [transfer.md](transfer.md) | 强（单边 Move）/缺失（双边单据） | Transfer In/Out 仅为同一库存行增减标签 |
| 库位 | [transfer.md](transfer.md) | 强 | `location` 为自由文本且维护不写流水 |
| 安全库存 | [safety_stock.md](safety_stock.md) | 强 | `stock_qty <= safe_stock` 即低库存 |
| 补货建议 | [safety_stock.md](safety_stock.md) | 强 | 建议数量形成 Draft PO，批准和收货分离 |
| 预测补货 | [safety_stock.md](safety_stock.md) | 缺失 | 未考虑需求、在途、预留、提前期或 EOQ |

## Shared vocabulary

- **过账**：同时改变库存、产品镜像并追加流水的业务动作。
- **现存量**：`inventory.stock_qty`。
- **镜像量**：`products.stock_qty`，供旧产品路径读取。
- **流水结余**：`inventory_ledger.balance_qty`，是该次过账后的余额快照。
- **盘点差异**：实盘量减账面量；Legacy 输入的是差异量而非实盘量。
- **Transfer 标签**：单边调整的 `trans_type`，不等于调拨单。
- **安全库存**：低库存比较阈值，不是自动采购承诺。
