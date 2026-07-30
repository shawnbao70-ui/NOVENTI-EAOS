# 样品质检放行与状态边界

## Scope与证据强度

本页只判断质量评价是否构成样品入库/报价前置放行。样品五维评分、追加写、物化不读评分为强证据；release/reject/hold/quarantine 状态机缺失。通用质量边界交叉引用 [`../quality-compliance/quality_check.md`](../quality-compliance/quality_check.md)，不复制其来料与成品质检全景。

## 业务规则（稳定ID）

1. **QRG-R01** 新样品写 `New`，该词只表示已登记，不等于待检状态。
2. **QRG-R02** 质量数据存于 sample_quality_assessment，包含外观、精度、强度、耐久、包装五项评分。
3. **QRG-R03** overall_grade 和 remark 由人工提交并原样保存。
4. **QRG-R04** 每次保存追加一行；Sample360 服务读取 id 最新的一条作为当前评价。
5. **QRG-R05** 未见五项分数自动计算 overall_grade 的公式。
6. **QRG-R06** overall_grade 是自由文本，没有 Pass/Fail/A/B 受控枚举证据。
7. **QRG-R07** material analysis 的 quality_grade 与 quality assessment 的 overall_grade 是不同表字段，不自动同步。
8. **QRG-R08** material risk_level 不触发 hold、reject 或 quarantine。
9. **QRG-R09** 保存质量评价的路由未见 Samples.edit 等服务端权限门。
10. **QRG-R10** materialize 不读取 quality assessment、quality_grade、risk_level 或 certification requirement。
11. **QRG-R11** `can_materialize` 只检查 product_id 与是否已有 Sample Receipt。
12. **QRG-R12** 物化成功写 Sample Receipt 并把样品状态置 `Stocked`。
13. **QRG-R13** Stocked 只表示库存过账，不能解释为 Quality Released/Accepted。
14. **QRG-R14** `Received` 是采购收货后的 PO 状态，不是样品质量放行。
15. **QRG-R15** `Sample Receipt` 是库存流水类型，不是检验结果。
16. **QRG-R16** create_quote_from_sample 不检查质量评价，未质检样品可转 Draft 报价。
17. **QRG-R17** Object360 的完成质检建议是软提示，不阻断入库或报价。
18. **QRG-R18** GTFIP quality 的 planned/AQL/默认分数属于贸易订单旁路，与 sample_quality_assessment 数据面隔离。
19. **QRG-R19** 样品域未见 release、reject、hold、quarantine、rework 状态或审批链。
20. **QRG-R20** 列表 KPI 只统计 New/Stocked/其他，不区分已检、合格、拒收。

## 流程

1. 样品以 New 登记。
2. 可选调用质量评价 POST，追加五项评分、overall_grade、remark。
3. 该写入不改变 samples.status。
4. 用户可不评价而先绑定产品。
5. 用户可不评价而 materialize；成功后库存三写并置 Stocked。
6. 用户也可不评价而创建 Draft 报价。
7. Procurement 的 Received/PO Receipt 是平行收货流程，不参与样品质量判定。
8. 当前没有从评分到 release/reject 的系统动作。

## 校验（强/弱/缺失）

1. **QRG-V01（弱/类型）** 五项评分需可转换为 float。
2. **QRG-V02（缺失）** 未限制评分为 0–10 或 0–100。
3. **QRG-V03（缺失）** overall_grade 无受控枚举。
4. **QRG-V04（缺失）** 写评价前未统一验证样品存在。
5. **QRG-V05（缺失）** 未要求检验员、检验时间、方法、仪器或签名。
6. **QRG-V06（缺失）** 未定义一条当前有效评价及旧版本作废规则。
7. **QRG-V07（缺失）** 物化前不要求评价存在。
8. **QRG-V08（缺失）** 物化前不要求 overall_grade 合格。
9. **QRG-V09（缺失）** 转报价前不要求质量放行。
10. **QRG-V10（缺失）** risk_level 高风险不触发阻断。
11. **QRG-V11（缺失）** Stocked 不要求 release 人/时间。
12. **QRG-V12（强/非质量）** 物化只强制 product、qty、幂等、库存行和 Samples.edit。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `sample_quality_assessment` | 样品人工质量评分记录 |
| `appearance_score` | 外观评分 |
| `precision_score` | 精度评分 |
| `strength_score` | 强度评分 |
| `durability_score` | 耐久评分 |
| `packaging_score` | 包装评分 |
| `overall_grade` | 人工综合等级，自由文本 |
| `remark` | 质量说明文本 |
| `sample_material_analysis.quality_grade` | 材料分析等级，独立于 overall_grade |
| `risk_level` | 材料风险描述，不形成 hold |
| `sample_supplier_matching.quality_score` | 候选供应商评分，不是样品放行 |
| `New` | 样品初始登记状态 |
| `Stocked` | Sample Receipt 已过账 |
| `Sample Receipt` | 样品库存增加流水 |
| `Received` | 采购单已收货 |
| `PO Receipt` | 采购库存收货流水 |
| `can_materialize` | 产品已绑定且未入库，不含质量条件 |
| `inspection_status=planned` | GTFIP 贸易质检旁路状态 |

## 状态词汇

| 词汇 | 含义/边界 |
|---|---|
| New | 样品已登记；不是 QC Pending |
| Stocked | 样品已库存物化；不是 Released |
| Received | 采购已收货；不是 QC Accepted |
| Released / Accepted | 样品域未实现 |
| Rejected / Hold / Quarantine | 样品域未实现 |
| planned | GTFIP 质检默认阶段，非样品状态 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| QRG-E01 | 新样品 New、评价追加写、物化 Stocked | 强 | `apps/sample/services.py` |
| QRG-E02 | 质量评价路由无 edit gate，对比物化有 gate | 强 | `apps/sample/router.py` |
| QRG-E03 | 评价表字段无检验员/放行字段 | 强 | `runtime/v14/legacy_support.py` |
| QRG-E04 | Sample360 不以质量评价控制 materialize | 强 | `templates/sample360.html` |
| QRG-E05 | 幂等依据 Sample Receipt + remark | 强 | `apps/sample/repository.py` |
| QRG-E06 | A-005 验证库存链而非 QC gate | 强 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |
| QRG-E07 | A-017 证明人工确认，不证明质量批准 | 强 | `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` |
| QRG-E08 | Object360 只给质检建议 | 中 | `core/object360/sample/sample_lifecycle.py` |
| QRG-E09 | GTFIP quality 与样品表隔离 | 中/边界 | `v15/gtfip/engines/quality.py`、`repository.py` |
| QRG-E10 | 通用质量页确认 Stocked/Received 非质量结论 | 强（交叉） | `docs/knowledge/legacy-extract/quality-compliance/quality_check.md` |

## UNKNOWN + 已查路径

1. **overall_grade 合法词汇及合格阈值 UNKNOWN。** 已查路径：assessment DDL、services、templates、locales。
2. **评分范围、权重和公式 UNKNOWN。** 已查路径：save route、DDL、quality docs/reports。
3. **质量评价 UI 是否在历史分支存在 UNKNOWN。** 已查路径：templates/sample*、备份、material_analysis 页面。
4. **Stocked 后能否因质检失败冲销 UNKNOWN。** 已查路径：apps/sample、apps/inventory、returns/reversal。
5. **是否存在外部实验室放行接口 UNKNOWN。** 已查路径：integrations、v15/core、business_modules。
6. **GTFIP quality 是否计划阻断样品链 UNKNOWN。** 已查路径：gtfip、sample、inventory 与 reports。
7. **认证要求是否应成为物化门禁 UNKNOWN。** 已查路径：sample_requirements、materialize、quality-compliance。
8. **质检员身份、签名和审计保存位置 UNKNOWN。** 已查路径：quality表、sample_logs、approval/audit。
9. **Received/New/Stocked 是否有统一跨域状态词典 UNKNOWN。** 已查路径：Sample、Procurement、Inventory schema/services。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample*`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
