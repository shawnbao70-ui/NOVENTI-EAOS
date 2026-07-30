# 样品保管、责任转移与位置证据

## Scope与证据强度

本页只回答样品收下后“由谁保管、在哪里、如何转移、是否可领用/归还”。收样日期、客户关联、图片和入库物化为强证据；`owner` 列与 `sample_logs` 为“结构存在但业务未接线”；责任转移、样品库位、领用/归还为缺失。

收样与入库主规则交叉引用 [`../sample-deepen/sample_intake.md`](../sample-deepen/sample_intake.md) 和 [`../sample-deepen/sample_stocking.md`](../sample-deepen/sample_stocking.md)，此处不重写。

## 业务规则（稳定ID）

1. **SC-R01** 收样创建只要求 customer_id，系统写 sample_no、服务器当天 receive_date 和 `New`。
2. **SC-R02** 创建后直接进入样品详情，不采集收样人、承运单、包裹数或接收地点。
3. **SC-R03** customer_id 表示样品来源客户，不等于当前保管人。
4. **SC-R04** schema upgrade 可为 samples 增 `owner` 列，Object360 对象也可读取该值。
5. **SC-R05** 当前 Sample 路由、service 和模板未提供 owner 写入或变更入口。
6. **SC-R06** owner 未证明引用用户、员工或销售员表，因此不能当作受控责任人。
7. **SC-R07** 样品主表未见 location、warehouse、bin、shelf 等物理库位字段。
8. **SC-R08** `inventory.location` 属产品库存余额，不是样品在分析/保管阶段的位置。
9. **SC-R09** 产品绑定只写 `samples.product_id`，不转移保管责任、不写 owner/location/log。
10. **SC-R10** `sample_logs` 表和 `create_sample_log` helper 存在，但活动收样、绑定、分析、入库路径未调用。
11. **SC-R11** 固定图片槽和 gallery 可保存样品外观证据，但不记录拍摄人、保管人或交接签名。
12. **SC-R12** materialize 把样品对应产品数量写入库存并将状态置 `Stocked`，不生成保管交接记录。
13. **SC-R13** `Stocked` 不表示样品实体已转交某仓管员或某库位。
14. **SC-R14** 未见 checkout、issue、borrow、return、handover 的样品级路由、表或状态。
15. **SC-R15** 未见样品责任转移的 from_holder、to_holder、时间、签名或原因字段。
16. **SC-R16** `sample_logs.operator` 可表达操作者意图，但因未接线不能充当实际 custody 审计链。
17. **SC-R17** core/sample metadata 只列主要样品/测量/图片表，未把 sample_logs 作为领域权威表。
18. **SC-R18** 财务 transfer records 和库存 transfer 词汇不能映射为样品保管转移。

## 流程

1. 用户登记客户来样，系统写 New 和 receive_date。
2. 用户可上传固定槽图片或 gallery 图片。
3. 用户可追加测量/分析记录；这些动作不改 owner 或位置。
4. 用户可把样品绑定目录产品；仍无责任转移。
5. 用户可 materialize 为库存数量并得到 Stocked。
6. 全路径未见保管人签收、库位上架、领用、归还或交接确认。
7. 因此 Legacy 的可证流程是“来样记录→分析资料→可选库存物化”，不是完整 custody chain。

## 校验（强/弱/缺失）

1. **SC-V01（强/HTTP）** 创建表单要求 customer_id。
2. **SC-V02（弱/未接线）** validate_sample 检查 customer_id，但创建服务未以它形成统一门禁。
3. **SC-V03（缺失）** 未验证客户存在、Active 或与当前租户一致。
4. **SC-V04（缺失）** 收样创建未见 Samples.add 服务端权限门。
5. **SC-V05（强）** 图片上传走 image 文件安全校验。
6. **SC-V06（缺失）** owner 无必填、格式、员工引用或权限校验。
7. **SC-V07（缺失）** 责任转移无双方确认、时间和原因校验。
8. **SC-V08（缺失）** 样品位置无仓库/库位存在性校验。
9. **SC-V09（缺失）** 领用数量、归还期限、逾期和损坏状态未建模。
10. **SC-V10（缺失）** sample_logs 未被强制写入每个 custody 相关动作。
11. **SC-V11（缺失）** materialize 不要求 owner/location 已填。
12. **SC-V12（缺失）** Stocked 后无保管交接或实物去向校验。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.id` | 样品内部标识 |
| `sample_no` | SP 时间戳业务编号 |
| `customer_id` | 来样客户，不是持有人 |
| `receive_date` | 系统登记接收日 |
| `status=New` | 新建登记标签 |
| `owner` | 可选迁移列；实际写入与引用规则未证实 |
| `product_id` | 样品到目录产品绑定，不是保管关系 |
| `image1/2/3` | 三个固定图片文件名 |
| `sample_images.image_path` | gallery 图片路径 |
| `sample_images.image_type` | 图片分类文本 |
| `sample_logs.action` | 设计上的样品动作 |
| `sample_logs.remark` | 设计上的动作说明 |
| `sample_logs.operator` | 设计上的操作者文本 |
| `sample_logs.created_at` | 设计上的日志时间 |
| `inventory.location` | 产品库存位置，不能作为样品库位 |
| `Sample Receipt` | 样品物化库存事件 |
| `SAMPLE-{id}` | 物化流水的样品溯源备注 |
| `Stocked` | 已过账库存，不是 custody release |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| New | 已登记来样 |
| Stocked | 已执行 Sample Receipt |
| Received | 采购域状态，不是样品 custody 状态 |
| Owner | 可选字段意图，未形成持有人流程 |
| Checked out / Returned | 未实现词汇 |
| Handover | 未实现责任转移 |
| Location / Bin | 样品域未建模 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SC-E01 | 最小收样写 customer/New/receive_date | 强 | `apps/sample/services.py` |
| SC-E02 | Sample 路由无 holder/location/checkout | 强（缺失证据） | `apps/sample/router.py` |
| SC-E03 | 产品绑定、物化幂等和状态更新 | 强 | `apps/sample/repository.py` |
| SC-E04 | owner 列为升级补丁字段 | 强（结构） | `database/upgrade_patch.py` |
| SC-E05 | sample_logs 表存在 | 强（结构） | `runtime/v14/legacy_support.py` |
| SC-E06 | create_sample_log helper 存在但无业务调用 | 强/未接线 | `apps/sample/utils.py` |
| SC-E07 | Sample360 无持有人/位置/交接表单 | 强 | `templates/sample360.html` |
| SC-E08 | 详情页图片是主要实物证据 | 强 | `templates/sample_detail.html` |
| SC-E09 | inventory.location 属库存元数据 | 强（边界） | `apps/inventory/repository.py`、`router.py` |
| SC-E10 | Object360 可读取 owner 但无 custody 边 | 中 | `core/object360/sample/sample_object.py`、`sample_lifecycle.py` |
| SC-E11 | A-017 只证明人工物化确认 | 强 | `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **owner 由谁、在何时写入 UNKNOWN。** 已查路径：apps/sample、templates/sample*、upgrade_patch、Object360。
2. **owner 值是用户名、员工 ID 还是自由文本 UNKNOWN。** 已查路径：schema、用户/员工表、Sample service。
3. **样品物理库位是否保存在仓库外部系统 UNKNOWN。** 已查路径：samples DDL、inventory location、business_modules、reports。
4. **责任转移/领用/归还是否有未纳入当前路由的旧实现 UNKNOWN。** 已查路径：apps/sample、apps/inventory、v14 residual、templates。
5. **create_sample_log 是否由部署外 hook 调用 UNKNOWN。** 已查路径：全库调用、legacy bridge、scripts。
6. **图片是否承担交接凭证法律语义 UNKNOWN。** 已查路径：图片 DDL、上传服务、模板和报告。
7. **Stocked 后实物样品是否仍需保留 UNKNOWN。** 已查路径：materialize、sample status、inventory、outbound/returns。
8. **custody 是否需要 tenant/company 隔离 UNKNOWN。** 已查路径：sample_logs tenant 分支、samples/inventory repository。
9. **丢失、损坏、销毁状态及审批 UNKNOWN。** 已查路径：Sample/Approval/Quality 路由、business_modules。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample*`
- `H:\Workspace\EZAM_CRM - 9.0\core\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\database\upgrade_patch.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
