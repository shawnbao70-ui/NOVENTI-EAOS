# Quotation Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| 报价状态机 | [quote_lifecycle.md](quote_lifecycle.md) | 强（可写值）/弱（转换约束） | 五个英文状态可被直接设置，转 SO 又写入中文 `已确认` |
| Draft 创建 | [quote_lifecycle.md](quote_lifecycle.md) | 强 | 普通创建、引导创建、样品转报价均以 Draft 起步 |
| Quote Approve | [quote_approve.md](quote_approve.md) | 强 | Draft、有行、人工确认后转 Sent |
| 中心审批关系 | [quote_approve.md](quote_approve.md) | 强负向 | Quote Approve 未建立或消费 Approval Center 记录 |
| 转 SO 前置门 | [quote_convert_gates.md](quote_convert_gates.md) | 强 | 只硬校验报价存在和未转过；不要求 Sent/Won/Approved |
| 双转单路径 | [quote_convert_gates.md](quote_convert_gates.md) | 强 | Sales 路径有生命周期链接；Quotation 残留路径没有 |
| 转单字段快照 | [quote_convert_gates.md](quote_convert_gates.md) | 强 | 复制客户、业务员、日期、总额及行的产品/数量/单价/金额 |
| 报价行计价 | [quote_lines_pricing.md](quote_lines_pricing.md) | 强 | 新增行按成本和目标毛利率反推单价 |
| Approve 改价 | [quote_lines_pricing.md](quote_lines_pricing.md) | 强 | Draft 可改数量/单价，并按保存成本重算 |
| 折扣/税/FX | [quote_lines_pricing.md](quote_lines_pricing.md) | 缺失/弱 | 报价主链未形成完整折扣、税和换算执行链 |

## Reading order

1. [quote_lifecycle.md](quote_lifecycle.md)：先理解实际存储状态与中英混用。
2. [quote_approve.md](quote_approve.md)：再区分本地人工发布和横向中心审批。
3. [quote_convert_gates.md](quote_convert_gates.md)：确认转 SO 的真实门槛与双路径风险。
4. [quote_lines_pricing.md](quote_lines_pricing.md)：最后定位行项目和计价责任边界。

## Shared vocabulary

- **Quote Approve**：报价本地 Type A 确认面；成功结果是 `Sent`。
- **Human Approved**：用户在动作页显式确认的来源标记，不天然等于中心审批。
- **状态动作**：只写报价状态，不创建销售订单。
- **Convert SO**：创建销售订单并复制商业快照的独立动作。
- **`已确认`**：转单成功后写回报价的中文状态，不属于五值英文状态列表。
- **双路径**：`apps/sales/services.py` 主路径与 `apps/quotation/quote_pages.py` 残留实现。
- **行快照**：报价行持久化的产品、数量、成本、毛利、单价和金额。
