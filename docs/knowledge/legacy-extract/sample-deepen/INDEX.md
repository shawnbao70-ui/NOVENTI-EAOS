# Sample Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| 收样创建 | [sample_intake.md](sample_intake.md) | 强 | 创建仅明确接收客户，生成 SP 时间戳编号、当天日期与 New |
| 客户绑定 | [sample_intake.md](sample_intake.md) | 强/缺口 | 保存 customer_id；未见数据库外键与服务端存在性校验 |
| 测量历史 | [sample_analysis.md](sample_analysis.md) | 强 | 每次新增测量，详情/Sample360只取最新一条 |
| 图片 | [sample_analysis.md](sample_analysis.md) | 强 | 固定三槽与多图表并存，删除权限不一致 |
| 分析块 | [sample_analysis.md](sample_analysis.md) | 强（数据）/弱（自动分析） | 材料、质量、需求、供应商数据由人工录入 |
| 产品绑定 | [sample_stocking.md](sample_stocking.md) | 强 | `samples.product_id` 为后加字段，入库前必须绑定 |
| 样品入库 | [sample_stocking.md](sample_stocking.md) | 强 | 库存、产品镜像、流水三写，状态变 Stocked |
| 入库幂等 | [sample_stocking.md](sample_stocking.md) | 强/应用层 | `Sample Receipt + SAMPLE-{id}` 查重 |
| 样品转报价 | [sample_to_quote.md](sample_to_quote.md) | 强 | 创建空行 Draft 报价，继承客户和商业头默认 |
| 生命周期追溯 | [sample_to_quote.md](sample_to_quote.md) | 中 | sample/requirement/opportunity 字段存在时才传播，失败可静默降级 |

## Reading order

1. [sample_intake.md](sample_intake.md)：明确样品主记录的最小创建事实。
2. [sample_analysis.md](sample_analysis.md)：区分人工录入、附件与自动分析。
3. [sample_stocking.md](sample_stocking.md)：理解样品如何成为库存。
4. [sample_to_quote.md](sample_to_quote.md)：理解样品如何成为报价来源。

## Shared vocabulary

- **Sample**：Legacy 主要表达客户来样，不等于向客户发出的样品。
- **New**：新收样状态。
- **Stocked**：已按 Sample Receipt 入库，不代表分析完成。
- **Measurement**：一条人工录入测量记录。
- **Material analysis / Quality assessment**：结构化人工录入块。
- **Materialize**：绑定产品后把指定正数量过账到库存。
- **Traceability**：样品、业务需求、商机和报价之间的可选关联。
