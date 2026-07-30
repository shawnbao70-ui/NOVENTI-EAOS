# 样品质量 Hold、Release 与 Reject 状态机

## Scope与证据强度

本页核验样品域是否存在 hold/release/reject/quarantine/approve 状态及写入口，并判断它们是否阻断 Stocked 或 Quote。结论：样品只有追加评分和 New→Stocked；审批 Rejected、采购 Received、GTFIP planned 属平行域。基础边界见 [`../sample-gate-deepen/quality_release_gate.md`](../sample-gate-deepen/quality_release_gate.md)。

## 业务规则（稳定ID）

1. **QHR-R01** 新样品状态为 New，不等于 QC Pending。
2. **QHR-R02** samples 无 quality_status、hold_flag、release_by 或 reject_reason。
3. **QHR-R03** sample_quality_assessment 只保存五项分数、overall_grade 和 remark。
4. **QHR-R04** 评价采用追加 INSERT，不更新 samples.status。
5. **QHR-R05** overall_grade 是自由文本，无 Pass/Fail 受控枚举。
6. **QHR-R06** material quality_grade 与 overall_grade 不同步。
7. **QHR-R07** risk_level 是描述文本，不触发 hold/quarantine。
8. **QHR-R08** 样品质量评价路由无可见权限 gate。
9. **QHR-R09** `can_materialize` 不包含质量条件。
10. **QHR-R10** materialize 不读取任何样品质量字段。
11. **QHR-R11** 成功物化直接置 Stocked；Stocked 不等于 Released。
12. **QHR-R12** create_quote_from_sample 不读取质量评价或风险。
13. **QHR-R13** Quote Approve 检查报价状态和行项，不检查样品质量。
14. **QHR-R14** Quote→SO 转换不回查样品质量。
15. **QHR-R15** Approval 的 Approved/Rejected 是审批单据结果，不是样品质检状态。
16. **QHR-R16** Procurement 的 Received/PO Receipt 是收货结果，不是质量接受。
17. **QHR-R17** GTFIP 初始化 inspection_status=`planned`，与 Sample 数据面隔离。
18. **QHR-R18** GTFIP GET 可能以默认 85 生成 acceptable 文案，不是放行写入。
19. **QHR-R19** 未见 GTFIP inspection_status 的 failed/hold/released 更新命令。
20. **QHR-R20** QC workspace 的 defects/holds/releases KPI 为占位，不是事实台账。
21. **QHR-R21** Inventory 只有单一 stock_qty，无 available/inspection/blocked/quarantine 数量桶。
22. **QHR-R22** Object360 完成质检提示只是 next action，不执行门禁。
23. **QHR-R23** 样品域不存在从 Hold→Released 或 Rejected→Rework 的转换矩阵。
24. **QHR-R24** A-005 验证的是库存过账和报价链，不是质量放行。

## 流程

1. 样品以 New 创建。
2. 可选追加质量评价；主状态不变。
3. 可在无评价、任意 grade/risk 下绑定产品。
4. 满足非质量门禁即可 materialize 并置 Stocked。
5. 也可直接创建 Draft Quote，后续批准/转单仍不读取样品质量。
6. Approval、Procurement、GTFIP 各有相似词汇，但不回写样品质量状态。
7. 因此不存在可执行的样品 Hold/Release/Reject 状态机。

## 校验（强/弱/缺失）

1. **QHR-V01（弱/类型）** 五项 score 需可转 float。
2. **QHR-V02（缺失）** 未限制评分上下限。
3. **QHR-V03（缺失）** overall_grade 无枚举。
4. **QHR-V04（缺失）** 写评价前未统一验证样品存在。
5. **QHR-V05（缺失）** 无检验员、时间、方法和签名。
6. **QHR-V06（缺失）** 物化前不要求评价存在。
7. **QHR-V07（缺失）** 物化前不要求 grade 合格。
8. **QHR-V08（缺失）** 转报价前不要求 release。
9. **QHR-V09（缺失）** risk_level 高风险不阻断。
10. **QHR-V10（缺失）** 无 Hold→Release 授权和合法转移校验。
11. **QHR-V11（缺失）** 无 Rejected 样品退回/报废/复检校验。
12. **QHR-V12（缺失）** Stocked 后无质量冲销。
13. **QHR-V13（强/非质量）** materialize 强制 Samples.edit 和应用层幂等。
14. **QHR-V14（语义守卫）** Approval Rejected、PO Received、GTFIP planned 不得当作样品质量结论。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.status=New` | 样品已登记 |
| `samples.status=Stocked` | Sample Receipt 已过账 |
| `sample_quality_assessment` | 人工五维评分记录 |
| 五项 `*_score` | 无范围定义的人工分数 |
| `overall_grade` | 自由文本综合等级 |
| `quality_grade` | 材料分析等级 |
| `risk_level` | 材料风险描述 |
| `quality_score` | 供应商候选评分 |
| `Sample Receipt` | 样品库存增加事件 |
| `can_materialize` | 产品已绑且未物化 |
| `approval_status=Rejected` | 审批拒绝 |
| `Received` | 采购已收货 |
| `PO Receipt` | 采购入库事件 |
| `inspection_status=planned` | GTFIP 质检计划槽位 |
| GTFIP `quality_score` | 可为空并由 GET 回退 85 |
| `stock_qty` | 未拆分质量状态的库存数量 |
| defects/holds/releases KPI | QC workspace 占位符 |
| `Draft` | 无质量 release 也可创建的报价状态 |

## 状态词汇

| 词汇 | 域与边界 |
|---|---|
| New | Sample 登记 |
| Stocked | Sample 库存过账 |
| Hold / Quarantine / Released | Sample 未实现 |
| Rejected | Approval 域词汇 |
| Received | Procurement 域词汇 |
| planned | GTFIP 贸易质检词汇 |
| acceptable | GET 分析文案，不是持久放行 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| QHR-E01 | New、质量追加写、Stocked 主路径 | 强 | `apps/sample/services.py` |
| QHR-E02 | 质量 POST 无 gate，materialize 有 Samples.edit | 强 | `apps/sample/router.py` |
| QHR-E03 | 评价 DDL 无放行/检验员字段 | 强 | `runtime/v14/legacy_support.py` |
| QHR-E04 | can_materialize 与物化不读质量 | 强 | `apps/sample/services.py`、`repository.py` |
| QHR-E05 | 转报价不查质量 | 强 | `apps/quotation/services.py` |
| QHR-E06 | PO Receive 直接写 Received/PO Receipt | 强（边界） | `apps/procurement/services.py` |
| QHR-E07 | Approval Rejected 写审批表 | 强（边界） | `apps/approval/services.py` |
| QHR-E08 | GTFIP 只证实 planned 初始化和 GET 默认分 | 中/边界 | `v15/gtfip/repository.py`、`engines/quality.py` |
| QHR-E09 | QC KPI 为占位 | 强 | `v15/ux/todays_work.py` |
| QHR-E10 | Object360 质检提示不 enforce | 中 | `core/object360/sample/sample_lifecycle.py` |
| QHR-E11 | A-005 gate 不含 QC | 强 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |

## UNKNOWN + 已查路径

1. **overall_grade 合法词汇和阈值 UNKNOWN。** 已查路径：DDL、services、templates、locales。
2. **历史质量评价 UI 是否存在 UNKNOWN。** 已查路径：templates/sample*、backups、v14 residual。
3. **Stocked 后质量失败的冲销流程 UNKNOWN。** 已查路径：Sample、Inventory、returns/reversal。
4. **外部实验室放行接口 UNKNOWN。** 已查路径：integrations、v15/core、business_modules。
5. **GTFIP sample_approval 是否桥接 Sample Center UNKNOWN。** 已查路径：gtfip lifecycle、apps/sample、reports。
6. **认证要求是否应阻断物化 UNKNOWN。** 已查路径：sample_requirements、materialize、quality-compliance。
7. **GFIP quality inspection 是否有部署外写入口 UNKNOWN。** 已查路径：gfip lifecycle/dashboard、routes、reports。
8. **hold/release 是否需要库存隔离桶 UNKNOWN。** 已查路径：inventory schema、services、quality docs。
9. **bind 在 Stocked 后是否允许换绑 UNKNOWN。** 已查路径：bind service、Sample360 UI、status checks。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\approval\`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
