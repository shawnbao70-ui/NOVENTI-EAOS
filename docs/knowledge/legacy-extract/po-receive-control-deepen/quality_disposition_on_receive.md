# 收货质检处置与直接入库

**Evidence strength:** Strong for direct usable stock；Strong-negative for incoming QC disposition  
**Verified:** 2026-07-23  
**Authority cross-ref:** [`../quality-compliance/quality_check.md`](../quality-compliance/quality_check.md)、[`../quality-compliance/nonconformance.md`](../quality-compliance/nonconformance.md)（质量权威；本页只判定与 PO Receive 是否汇合）

## Scope 与结论

本页核验 PO Receive 是否先检验、隔离或处置后再入库。结论：**直接增加单一可用库存**（`inventory.stock_qty` + `products.stock_qty` + `PO Receipt` ledger），无 inspection lot、quarantine 桶、hold/release、reject/RTV disposition。`Received` 证明过账完成，**不等于** QC Accepted。Sample 五维评分、GTFIP planned/默认分、QC workspace `—` KPI、NDE Inspection 壳均为平行或占位能力，**不构成**采购来料门禁。

## 业务规则（稳定 ID）

1. **QDR-R01** Receive 对每个有效行直接 `update_inventory_stock_qty` 增加可用量。
2. **QDR-R02** 同时 `apply_product_stock_delta` 并 `insert_inventory_ledger`（`PO Receipt`）。
3. **QDR-R03** PO `Received` 表示过账完成，不是 QC Accepted。
4. **QDR-R04** `PO Receipt` 表示库存移动，不是质量放行事件。
5. **QDR-R05** `inventory` DDL 仅 product_id / stock_qty / safe_stock / location — 无 available/inspection/quarantine/blocked 桶。
6. **QDR-R06** 无 inspection lot / batch 实体挂在 PO Receive。
7. **QDR-R07** 无 accepted / rejected / quarantine qty 拆分。
8. **QDR-R08** 无 hold / release 命令或状态机接在 Receive 后。
9. **QDR-R09** 无 reject / return-to-vendor 处置链接在来料。
10. **QDR-R10** DO Ship 从同一 `stock_qty` 扣减，无采购来料 QC release gate。
11. **QDR-R11** product Healthy / Low / Critical 是数量阈值状态，不是质量状态。
12. **QDR-R12** Sample `sample_quality_assessment` 与 PO Receive **数据隔离**。
13. **QDR-R13** Sample `materialize_sample` 不读取质量评价作为门。
14. **QDR-R14** Sample `Stocked` 也不等于 Released（库存动作）。
15. **QDR-R15** GTFIP `gtfip_quality` / planned 与 PO Receive **不连接**。
16. **QDR-R16** GTFIP 默认 85 分 /「可接受」文案不构成放行证据。
17. **QDR-R17** QC workspace KPI（inspections/defects/holds/releases）值为 `—` 占位。
18. **QDR-R18** NDE Inspection / QC Report 是文档外壳，不阻断库存。
19. **QDR-R19** Approval Center `Rejected` 不得映射为来料拒收。
20. **QDR-R20** 采购链未见 NCR / concession / rework / scrap 实体驱动 Receive。
21. **QDR-R21** Receive confirm 文案明确「Posts inventory + ledger」，无 QC 步骤。
22. **QDR-R22** A-004 / A-010 验收路径无质检步骤。

## 流程

1. Receive 验证 PO、行与重复过账。
2. 按 PO qty 直接写可用库存、产品镜像与 ledger。
3. PO 立即变 `Received`。
4. **无**检验批、待检库存或 disposition 步骤。
5. 后续 Ship 可直接消费同一库存。
6. Sample / GTFIP / QC workspace 是平行或占位能力，不构成补门。

```
PO Receive → usable stock_qty ↑ → Ship 可扣减
（无 Inspect → Quarantine → Disposition → Release 段）
```

## 校验（强 / 弱 / 缺失）

1. **QDR-V01（强）** Receive 需 `Purchases.edit`。
2. **QDR-V02（强）** PO 存在、open、有行且未重复过账。
3. **QDR-V03（强）** inventory 行必须存在。
4. **QDR-V04（缺失）** 无来料检验完成门。
5. **QDR-V05（缺失）** 无合格/拒收数量守恒。
6. **QDR-V06（缺失）** 无隔离量不可用校验。
7. **QDR-V07（缺失）** 无 hold/release 授权。
8. **QDR-V08（缺失）** 无 disposition 枚举（accept/reject/rework/scrap/RTV）。
9. **QDR-V09（缺失）** 无 NCR / RTV 关联强制。
10. **QDR-V10（缺失）** 无 lot/batch 追溯门。
11. **QDR-V11（缺失）** Ship 无 QC release gate（来料侧）。
12. **QDR-V12（缺失）** Sample materialize 无 quality gate。
13. **QDR-V13（缺失）** GTFIP 状态不控制 PO Receive。
14. **QDR-V14（缺失）** 并发 Receive 无唯一/锁。
15. **QDR-V15（缺失）** location 文本无「隔离区」语义校验。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `inventory.stock_qty` | **全部可用的**单一库存量 |
| `products.stock_qty` | 产品库存镜像 |
| `inventory.location` | 库位文本；无隔离语义强制 |
| `PO Receipt` | 采购入库交易类型 |
| `PO-{id}` | 来源 / 幂等 remark |
| `Received` | 收货过账完成 |
| inspection_qty | **未建模** |
| accepted_qty | **未建模** |
| rejected_qty | **未建模** |
| quarantine_qty | **未建模** |
| quality hold / release | **未建模** |
| lot / batch（来料） | **未建模** |
| `sample_quality_assessment` | 样品评分，非 PO QC |
| `Stocked`（Sample） | 样品已入库 ≠ 放行 |
| `gtfip_quality` | 贸易质量槽，与 PO 隔离 |
| QC workspace KPI | 占位展示（`—`） |
| `stock_status` Healthy/Low/Critical | 数量阈值派生 |

## 状态词汇

| 词汇 | 判断 |
|---|---|
| Received / Stocked | 库存动作，**不是**质量放行 |
| Inspected / Accepted | PO 链**未实现** |
| Quarantined / Held | **未实现** |
| Released / Rejected / RTV | **未实现** |
| Planned | GTFIP 平行域状态 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| QDR-E01 | Receive 三写无 QC 分支 | 强 | `apps/procurement/services.py` |
| QDR-E02 | Inventory 单一 `stock_qty` DDL | 强 | `runtime/v14/legacy_support.py` |
| QDR-E03 | Receive 确认文案直写库存 | 强 | `templates/purchase_detail.html`、`purchase360.html` |
| QDR-E04 | Ship / Adjust 消费同一 stock_qty | 强 | `apps/inventory/services.py`、`repository.py` |
| QDR-E05 | Sample materialize 不读 QC 门 | 强 | `apps/sample/services.py`（`materialize_sample`） |
| QDR-E06 | GTFIP planned / 默认分 | 中 | `v15/gtfip/`、quality engine 命名面 |
| QDR-E07 | QC workspace KPI 占位 `—` | 强 | `v15/ux/todays_work.py`、`v15/ux/registry.py` |
| QDR-E08 | NDE 注册报告但无库存 gate | 中 | `document/nde_engine.py`；quality-compliance 权威 |
| QDR-E09 | A-004/A-010 无质检步骤 | 强 | `docs/reports/Business_Strong_A004_Purchase_Report.md`、`Business_Strong_A010_Purchase_Ops_Report.md` |
| QDR-E10 | quality-compliance：来料检验弱/缺失 | 强（邻包） | `../quality-compliance/quality_check.md` |

## UNKNOWN + 已查路径

1. **隐藏来料检验单是否存在 UNKNOWN。** 已查：Procurement/Inventory/templates/schema DDL。
2. **外部系统是否在 Receive 前检验 UNKNOWN。** 已查：integrations 命名面、business_modules、reports。
3. **供应商退货是否线下处理 UNKNOWN。** 已查：purchase return/RTV 命名面、Inventory Adjust。
4. **GTFIP planned 后续写入口 UNKNOWN。** 已查：`v15/gtfip/` routes/services/reports 命名面。
5. **质量报告是否触发 NCR UNKNOWN。** 已查：NDE、templates、quality apps 命名面；邻包 nonconformance。
6. **生产库是否私加质量库存桶 UNKNOWN。** 已查：公开 DDL/migrations；未查 live DB。
7. **lot/batch 是否外部维护 UNKNOWN。** 已查：Product/Inventory/print batch 命名面。
8. **Draft 直收是否默认代表线下验收 UNKNOWN。** 已查：UI 文案、docs/reports、A-004。
9. **多租户下质量隔离设计 UNKNOWN。** 已查：tenant schema、inventory queries。
10. **`core/` 是否有隐藏 QC gate UNKNOWN。** 已查：`core/` 检索超时边界；procurement receive 调用链未见。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ux\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- 邻包：`docs/knowledge/legacy-extract/quality-compliance/`
