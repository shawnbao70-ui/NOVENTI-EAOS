# Delivery Deepen Knowledge Index

| 模块 | 文件 | 深化边界 |
|---|---|---|
| 装箱与箱单 | [packing.md](packing.md) | Packing List、真实箱实体、重量体积、关务与打印派生 |
| 承运商与跟踪 | [carrier_tracking.md](carrier_tracking.md) | 承运商、运单号、ETA、状态事件、POD 与外部跟踪缺口 |
| 发货异常与重开 | [delivery_exceptions.md](delivery_exceptions.md) | 拦截、取消、冲销、重开及库存/SO/AR 一致性 |
| DO→AR/Invoice | [do_ar_handoff.md](do_ar_handoff.md) | 应收应计、V18 人审、Legacy 双路径、金额与打印交界 |

## 与既有知识包关系

- 本包仅深化观察，不修改 Delivery、Ops、Finance 或 fulfillment-deepen 正文。
- AR 应计与税务发票严格分层；页面名为 Invoice 不自动证明税务开票。
- `UNKNOWN` 均附已检索路径，不用平行 GFIP/GTFIP 能力补写主链事实。
