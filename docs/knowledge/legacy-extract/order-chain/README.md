# Legacy Knowledge Extract — Order Chain Pack

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/order-chain/**`  
**Verified:** 2026-07-23

## Scope

本包深化 Quote→SO→Approve/Open→DO→Ship/Receipt 链中由销售订单承接的四个边界。它只陈述可观察业务规则、流程、校验、数据语义和诚实缺口；不把状态标签当作库存、会计或审批过账。

## Modules

- [SO Convert](so_convert.md) — 报价转订单、一报价一单保护与佣金/lifecycle 钩子
- [SO Approve → Open](so_approve_open.md) — V18 Type A Human Approved 与最低行门槛
- [SO → DO](so_to_do.md) — 建发货单、`Delivery Created` 与 Ship 才扣库存
- [SO Payment View](so_payment_view.md) — receipts 实时汇总、SO 镜像字段与 AR 并行边界
- 汇总见 [INDEX.md](INDEX.md)

## Evidence posture

- 活动 Sales conversion 对同 quote ID 做应用层防重，但未证实数据库唯一约束；转换不要求 Quote Sent/Won。
- 转换不冻结 quote version，也不复制 currency、exchange rate、payment/delivery term 等完整商业头。
- 佣金和 lifecycle 链接是 best-effort 钩子，失败不阻止 SO 建立。
- V18 SO Approve 的硬门只有 pending stage、至少一行和 Human Confirm；结果仅为 `Open`。
- `Delivery Created` 被 catch-all 归入 pending，因此可再次 Approve 回 `Open`。
- 建 DO 不校验 SO Open、重复 DO、行存在或库存，并且不扣库存；Ship 才做库存门和过账。
- SO 详情按 receipts 实时重算，列表读取持久镜像；convert 后余额镜像默认零，首笔收款前即可分叉；Receipt 不核销 `ar_records`。
- 多个写入口使用 GET，且 convert/create DO 的活动 router 缺少完整写权限门。

## Hard boundaries

- Quote→SO Convert 不等于 Quote Approve，也不等于佣金已可靠入账。
- SO `Open` 不等于已建 DO、已发货、已开票或已收款。
- SO `Delivery Created` 不等于库存预留、减少或出库。
- DO `Pending` 不等于可用库存已验证。
- SO `payment_status='Paid'` 不等于 `ar_records` 已 Closed。
- UI 隐藏按钮、确认框或 AI summary 不构成服务端授权和业务校验。
- 本包只交叉引用 `sales` 与 `finance` 现有知识，不重写其正文。
