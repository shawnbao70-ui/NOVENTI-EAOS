# 报价版本、修订与重发

**Evidence strength:** Strong for schema/read capability and Copy Quote; strong negative for active version-write/re-send workflow

## Scope 与关键结论

Legacy 存在 `quote_versions` 表、读取 helper、dashboard count 和 history facade，但全库活动 Python 路径未见向该表 INSERT/UPDATE。打印上下文固定 `version="1.0"`、`revision=""`。实际“修订”主要表现为 Draft 原地改行，或 Copy Quote 新建独立 Draft；两者都未形成 version row。Sent/Negotiating 后的正式修订、版本批准、差异比较和重发未证实。

## 业务规则

| ID | 规则 |
|---|---|
| QVR-R01 | `quote_versions` 结构保存 quote_id、version_no、quote_no、total、remark、creator、time。 |
| QVR-R02 | `get_quote_versions` 只按 quote_id 倒序读取。 |
| QVR-R03 | `quote_history()` 只是当前 quote + versions 的组合，不生成历史。 |
| QVR-R04 | Quote Center/Dashboard 可统计 version 总数，但不证明版本被活动流程写入。 |
| QVR-R05 | 未发现 quotation service/repository 向 `quote_versions` 插入。 |
| QVR-R06 | Draft Approve 页面可原地修改 qty/price，并覆盖当前 quote item。 |
| QVR-R07 | Save Draft 写操作日志但不创建 version snapshot。 |
| QVR-R08 | Approve 把同一报价 Draft→Sent，不冻结或复制版本。 |
| QVR-R09 | Copy Quote 生成新 quote id、quote no 和 Draft。 |
| QVR-R10 | Copy 沿用旧行 qty/cost/profit_rate/price/amount 快照。 |
| QVR-R11 | Copy 不建立 parent_quote_id/version_of 关系。 |
| QVR-R12 | Copy 不写 `quote_versions`，因此是独立报价而非版本号递增。 |
| QVR-R13 | 打印/NDE 统一传 version 1.0、空 revision，与 version table 未联动。 |
| QVR-R14 | 状态菜单可直接把 Sent/Negotiating 改回 Draft 等值，未形成修订事件。 |
| QVR-R15 | 未观察到 Resend/重新发送命令、发送次数、收件人或送达记录。 |
| QVR-R16 | `quote_print_history` 记录打印，不等于版本/发送历史。 |
| QVR-R17 | Operation log 记录 Save Draft/Approve，但不保存字段级前后差异。 |
| QVR-R18 | 数据库升级曾增加 `quotes.send_time`，但活动 quotation 服务未观察到读写该字段。 |
| QVR-R19 | Copy Quote 不继承 sample/requirement/opportunity 追溯字段，不能视为保留来源链的 revision。 |

## Copy、Version、Revision、Resend 对照

| 概念 | Legacy 运行事实 |
|---|---|
| Save Draft | 原地覆盖行，日志记录 |
| Approve | 同一报价 Draft→Sent |
| Copy Quote | 新建独立 Draft、新编号、复制快照 |
| Quote Version | 表/读取能力存在；写路径未证实 |
| Revision | NDE 字段为空；无报价修订号工作流 |
| Resend | 未见活动命令或发送事件 |
| Print History | 打印审计，不是发送/版本审计 |

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| QVR-V01 | 读取 versions 按 quote_id 过滤 | Hard query |
| QVR-V02 | version_no 必填/唯一 | Missing |
| QVR-V03 | 每次改价必须创建 snapshot | Missing |
| QVR-V04 | Sent 后修改必须新 revision | Missing |
| QVR-V05 | Copy 必须关联 parent quote | Missing |
| QVR-V06 | 版本总额必须与当时行一致 | Missing |
| QVR-V07 | 版本必须记录完整行快照 | Missing；表只有头摘要 |
| QVR-V08 | revision 必须审批后生效 | Missing |
| QVR-V09 | 重发必须记录渠道/收件人/时间 | Missing |
| QVR-V10 | 并发修改必须版本检查 | Missing |
| QVR-V11 | 打印版本必须来自活动 version | Missing；固定 1.0 |
| QVR-V12 | 版本记录不可修改/删除 | UNKNOWN |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quote_versions.id` | 版本摘要记录 id |
| `quote_id` | 版本所属报价 |
| `version_no` | 文本版本号槽位；生成规则未知 |
| `quote_no` | 版本时报价号快照 |
| `total_amount` | 版本时头总额快照 |
| `remark` | 版本说明槽位 |
| `created_by` | 版本创建人槽位 |
| `create_time` | 版本创建时间槽位 |
| current quote/items | Draft 原地编辑的当前事实 |
| Copy Quote | 独立新 quote id，不是 version row |
| `version="1.0"` | NDE/打印固定展示值 |
| `revision=""` | 打印上下文空修订值 |
| `quote_print_history` | 打印操作历史 |
| operation log | Save Draft/Approve 动作记录 |
| resend | 未建模的发送动作 |
| `quotes.send_time` | 结构存在但活动发送/重发路径未使用的时间槽位 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| QVR-E01 | quote_versions DDL 字段 | 强 | `runtime/v14/legacy_support.py` |
| QVR-E02 | versions 只读 helper | 强 | `apps/quotation/utils.py::get_quote_versions` |
| QVR-E03 | history facade 只组合当前记录和 versions | 强 | `apps/quotation/history.py` |
| QVR-E04 | 全库未见 quote_versions INSERT/UPDATE | 强负向 | `apps/quotation/**`、全库 Python 检索 |
| QVR-E05 | Draft qty/price 原地更新 | 强 | `apps/quotation/services.py`、`repository.py` |
| QVR-E06 | Copy 新 Draft 并复制行快照 | 强 | `apps/quotation/services.py::copy_quote` |
| QVR-E07 | 打印固定 version/revision | 强 | `apps/quotation/services.py`、`apps/print_center/v14_residual.py` |
| QVR-E08 | Dashboard 仅统计 versions | 强 | `apps/quotation/utils.py` |
| QVR-E09 | Quote Detail 模板无 versions/re-send 操作 | 强负向 | `templates/quote_detail.html`、`quotes.html` |
| QVR-E10 | send_time 仅见 schema patch、未见 quotation 调用 | 强负向 | `database/upgrade_patch.py`、`apps/quotation/**` |

## UNKNOWN + 已查路径

1. **quote_versions 由哪个活动入口写入 UNKNOWN。** 已查：apps/quotation、runtime bridge、templates、reports、scripts。
2. **version_no 生成和唯一规则 UNKNOWN。** 已查：DDL、utils、Quotation service/repository。
3. **版本是否应包含行快照而非只有头摘要 UNKNOWN。** 已查：quote_versions DDL、quote_items、document engine。
4. **Sent 后正式修订/重报价流程 UNKNOWN。** 已查：Approve、status、copy、history、templates。
5. **重新发送报价的渠道、收件人和送达日志 UNKNOWN。** 已查：Quotation、communication/message/email、print history。
6. **Copy Quote 是否在业务上充当 revision UNKNOWN。** 已查：copy service、UI、version schema、reports。
7. **版本删除/篡改权限及保留期 UNKNOWN。** 已查：Quotation routes/repository、governance/docs。
8. **NDE 固定 1.0 是否只是展示占位 UNKNOWN。** 已查：NDE engine、print center、Quotation print service。

## 交叉引用

- 报价状态：[`../quotation-deepen/quote_lifecycle.md`](../quotation-deepen/quote_lifecycle.md)
- 报价改价：[`../quotation-deepen/quote_lines_pricing.md`](../quotation-deepen/quote_lines_pricing.md)
- 源追溯：[`source_traceability.md`](source_traceability.md)
