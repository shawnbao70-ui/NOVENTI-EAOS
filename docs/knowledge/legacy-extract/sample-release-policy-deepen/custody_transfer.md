# 样品持有人与库位转移的可执行证据

## Scope与证据强度

本页不再描述一般保管事实，而是核验“能否执行一次样品持有人或库位转移”。结论：`owner` 和 `sample_logs` 仅有结构，样品域无 transfer/handover/checkout/return 命令；库存 Transfer 只调整产品数量。基础事实交叉引用 [`../sample-gate-deepen/sample_custody.md`](../sample-gate-deepen/sample_custody.md)。

## 业务规则（稳定ID）

1. **CT-R01** 收样写 customer_id、receive_date 和 New，不写 holder 或 location。
2. **CT-R02** customer_id 是来样客户，不是内部持有人。
3. **CT-R03** `samples.owner` 列可由升级补丁增加。
4. **CT-R04** Sample Object360 可读取 owner，但没有更新动作。
5. **CT-R05** apps/sample 的 INSERT/UPDATE 未写 owner。
6. **CT-R06** owner 没有用户/员工外键或受控值域。
7. **CT-R07** samples 无 holder、warehouse、location、bin、shelf 字段。
8. **CT-R08** sample_logs 表和 helper 存在，但业务路径未调用。
9. **CT-R09** sample_logs 未形成转移前持有人、转移后持有人、签收或原因结构。
10. **CT-R10** bind_sample_product 只改 product_id，不是 custody transfer。
11. **CT-R11** materialize 只做库存过账并置 Stocked，不记录实物交接。
12. **CT-R12** inventory.location 是 SKU 库存元数据，不是样品库位。
13. **CT-R13** update_inventory_meta 可改产品位置，但不引用 sample_id。
14. **CT-R14** Inventory `Transfer In/Out` 是数量调整标签，不是样品对象移动。
15. **CT-R15** 未见 sample checkout、borrow、issue、return、handover 路由或表。
16. **CT-R16** 图片可作为外观资料，但无拍摄人、交接人或签名语义。
17. **CT-R17** Stocked 不证明样品实体已交仓管或上架。
18. **CT-R18** 财务 transfer records 与样品责任转移无关。

## 流程

1. 收样后只形成 New 样品记录。
2. 可上传图片、追加分析、绑定产品。
3. 系统没有“从 A 持有人转给 B”的命令。
4. 系统没有“从位置 X 移到位置 Y”的样品命令。
5. materialize 把产品数量记入库存，但不创建交接记录。
6. 库存位置/Transfer 操作作用于 SKU 库存行。
7. 因此无法从 Legacy 执行并审计完整样品 custody transfer。

## 校验（强/弱/缺失）

1. **CT-V01（强/HTTP）** 收样 customer_id 为表单必填。
2. **CT-V02（缺失）** 创建不校验内部接收人。
3. **CT-V03（缺失）** owner 无必填、格式或员工引用。
4. **CT-V04（缺失）** 转移无 from/to holder。
5. **CT-V05（缺失）** 转移无双方确认、签名、时间和原因。
6. **CT-V06（缺失）** 样品库位无仓库/bin 存在性校验。
7. **CT-V07（缺失）** 领用/归还无期限、数量、损坏校验。
8. **CT-V08（缺失）** custody 动作不强制写 sample_logs。
9. **CT-V09（缺失）** materialize 不要求 owner/location。
10. **CT-V10（强/产品域）** Inventory Move 可要求 human_confirm，但不校验样品。
11. **CT-V11（缺失）** Transfer In/Out 没有成对移动校验。
12. **CT-V12（缺失）** owner/location 变化没有权限或审计门禁。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.id` | 样品对象标识 |
| `sample_no` | 样品业务编号 |
| `customer_id` | 来源客户 |
| `receive_date` | 登记接收日 |
| `status=New` | 新建登记 |
| `owner` | 可选文本列，无活动写路径 |
| `holder` | 未建模 |
| `product_id` | 目录产品绑定 |
| `sample_logs.action` | 设计上的动作文本 |
| `sample_logs.remark` | 设计上的说明 |
| `sample_logs.operator` | 设计上的操作者 |
| `inventory.location` | SKU 库存位置 |
| `Transfer In/Out` | SKU 数量调整类型 |
| `Sample Receipt` | 样品物化库存事件 |
| `SAMPLE-{id}` | 样品入库溯源文本 |
| `Stocked` | 已库存过账，不是责任转移完成 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| New | 新建样品 |
| Stocked | 已过账库存 |
| Owner | 无执行写路径的字段意图 |
| Holder | 未实现 |
| Checked out / Returned | 未实现 |
| Handover | 未实现 |
| Transfer In/Out | 产品库存调整 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| CT-E01 | 收样最小 INSERT 不含 owner/location | 强 | `apps/sample/services.py` |
| CT-E02 | Sample router 无 custody 命令 | 强（缺失证据） | `apps/sample/router.py` |
| CT-E03 | owner 是升级字段 | 强（结构） | `database/upgrade_patch.py` |
| CT-E04 | sample_logs 表与 helper 未接线 | 强/未接线 | `runtime/v14/legacy_support.py`、`apps/sample/utils.py` |
| CT-E05 | Sample 模板无 holder/location/handover UI | 强 | `templates/samples.html`、`sample_detail.html`、`sample360.html` |
| CT-E06 | Object360 只读 owner | 中 | `core/object360/sample/sample_object.py` |
| CT-E07 | Inventory location/Move 作用于库存行 | 强（边界） | `apps/inventory/services.py`、`repository.py` |
| CT-E08 | materialize 不写 custody | 强 | `apps/sample/services.py`、`repository.py` |
| CT-E09 | A-017 只证明人工过账确认 | 强 | `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **owner 的写入者和写入时点 UNKNOWN。** 已查路径：apps/sample、templates、upgrade_patch、Object360。
2. **owner 是用户名、员工 ID 还是自由文本 UNKNOWN。** 已查路径：schema、users/employees、Sample services。
3. **外部仓储系统是否维护样品库位 UNKNOWN。** 已查路径：integrations、inventory、business_modules、reports。
4. **未挂载 residual 是否含 custody 命令 UNKNOWN。** 已查路径：apps/sample/v14_residual、runtime/v14、bootstrap。
5. **sample_logs 是否被部署外 hook 调用 UNKNOWN。** 已查路径：全库调用、scripts、legacy bridge。
6. **图片是否承担交接凭证语义 UNKNOWN。** 已查路径：upload、图片表、模板和打印报告。
7. **Stocked 后实物样品的保存/销毁政策 UNKNOWN。** 已查路径：materialize、outbound、returns、approval。
8. **custody tenant 隔离和跨组织转移 UNKNOWN。** 已查路径：sample_logs、samples/inventory tenant 字段。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample*`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\database\upgrade_patch.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
