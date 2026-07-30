# Sent 后修订、重发与作废路径

**Evidence strength:** Strong negative for governed revise/resend/void workflows  
**结论：** 未证实 Sent 后存在受控修订、重发或作废闭环。Approve UI 在非 Draft 时将 qty/price 设为只读并隐藏 Save/Approve；但 Quote360 仍按权限显示 Add Products 和删除行，相关 service 没有状态 gate。另有构造 POST 可利用：Approve service 在状态 gate **之前**应用 line patches，且 `action=draft` 完全不检查状态。因此 Sent 内容并未冻结。用户也可直接回退状态或 Copy 为独立 Draft；这些路径都不创建 version/revision 关系。`quote_versions` 只有结构/读取证据，`send_time` 只有结构证据；无 Resend 事件、收件人/渠道/送达审计，也无 Void/Cancelled 专用动作。

## 路径判定

| 目标 | 可观察路径 | 真实性判定 |
|---|---|---|
| Draft 原地修订 | Approve 页 Save Draft / 行 patch | 有，但仅 Draft |
| Sent 原地修订 | 正常 Approve UI | UI 只读、隐藏动作 |
| Sent 增删行 | Quote360 Add Products / delete line | **正常 UI 可达**；仅权限门、无状态门 |
| Sent 构造 POST | line patches + `action=draft`/`approve` | **可先改行**；不是受控 revision |
| Sent→Draft | 通用 status redirect | 有，但只是覆盖状态 |
| Copy as revision | Copy Quote→新 Draft | 可作为人工替代，但无父子/version link |
| Version snapshot | `quote_versions` | 表和读取有；活动写入未证实 |
| Revision number | print/NDE revision | 固定空值 |
| Resend | resend command/event | 未发现 |
| Send timestamp | `quotes.send_time` | schema 槽位存在；活动读写未发现 |
| Print again | print history | 有；打印不等于发送 |
| Void/Cancel | 专用状态/动作 | 未发现 |
| Lost | 通用 status 可选值 | 不是受控作废证明 |

## 业务规则

| ID | 规则 |
|---|---|
| RRS-R01 | Draft 可在 Approve 页面原地 patch qty/price。 |
| RRS-R02 | Save Draft 覆盖当前行并记 operation log，不创建版本快照。 |
| RRS-R03 | Approve 只接受 Draft，成功后把同一 Quote 改为 Sent。 |
| RRS-R04 | 正常 UI 对非 Draft 行设 readonly，并不显示 Save/Approve 动作。 |
| RRS-R05 | 通用 status action 可直接覆盖 Quote 状态，包括回到 Draft。 |
| RRS-R06 | 状态回退不创建 revision_no、原因、差异或审批记录。 |
| RRS-R07 | Copy Quote 创建新 id、新 quote_no、Draft。 |
| RRS-R08 | Copy 复制旧行价格快照，但不写 parent/version relation。 |
| RRS-R09 | Copy 不继承 sample/requirement/opportunity FK，不能视为完整修订链。 |
| RRS-R10 | `quote_versions` 可被读取/统计，但未发现活动写路径。 |
| RRS-R11 | Print/NDE 使用固定 `version="1.0"` 与空 revision。 |
| RRS-R12 | `quote_print_history` 记录打印，不证明发送、重发或客户收件。 |
| RRS-R13 | `quotes.send_time` 已有 schema patch，但 quotation 活动路径未读写。 |
| RRS-R14 | 未见 Resend command、发送次数、渠道、收件人或送达状态。 |
| RRS-R15 | 未见 Void/Cancelled 专用状态转换、原因或反向副作用。 |
| RRS-R16 | 把状态改 Lost 只是通用覆盖，不能等同经过治理的作废。 |
| RRS-R17 | 已 Convert 的 Quote 可再改状态的边界未形成状态机保护。 |
| RRS-R18 | operation log 是动作级记录，不保存字段级 before/after。 |
| RRS-R19 | Service 在检查 `status == Draft` 之前就应用 line patches。 |
| RRS-R20 | `action=draft` 更新并重算后直接返回，不执行 Draft 状态检查。 |
| RRS-R21 | 构造非 Draft 的 `action=approve` 请求也会先修改行，之后才返回 draft-only 错误。 |
| RRS-R22 | Quote360 的 Add Products tab 与删除按钮不按 Quote 状态隐藏。 |
| RRS-R23 | `add_quote_item` / `delete_quote_item` 只做权限检查，不验证 Draft。 |
| RRS-R24 | Sent 后增删行会重算头总额，但不写 version snapshot 或修订审计。 |
| RRS-R25 | Canonical Copy 与 status GET routes 未见显式服务端权限检查；模板可见性不能替代 route gate。 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| RRS-V01 | 正常 UI 仅 Draft 可编辑/显示动作 | UI hard |
| RRS-V02 | Sent 修改必须新建 revision | Missing |
| RRS-V03 | Revision 必须关联 parent/version | Missing |
| RRS-V04 | Revision 必须保存完整行快照 | Missing |
| RRS-V05 | Revision 生效前必须重新审批 | Missing |
| RRS-V06 | 状态回退必须填写原因 | Missing |
| RRS-V07 | Resend 必须记录收件人/渠道/时间 | Missing |
| RRS-V08 | Resend 必须绑定确切 version | Missing |
| RRS-V09 | Void 必须检查未 Convert/未履约 | Missing |
| RRS-V10 | Void 必须执行下游撤销 | Missing |
| RRS-V11 | Copy 必须保留来源追溯 | Missing |
| RRS-V12 | 并发编辑必须 optimistic version check | Missing |
| RRS-V13 | version_no 唯一/递增 | UNKNOWN |
| RRS-V14 | send_time 在成功发送后写入 | Missing |
| RRS-V15 | POST line patch 必须在状态 gate 之后 | Missing；当前次序相反 |
| RRS-V16 | Save Draft service 必须验证当前 Draft | Missing |
| RRS-V17 | Add/delete line 必须验证当前 Draft | Missing |
| RRS-V18 | Sent 内容不可变 | Missing；Quote360 正常 UI 可增删行 |
| RRS-V19 | Copy/status 服务端 RBAC 与 POST/CSRF | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `Draft` | 可在专用页编辑/保存/Approve 的状态 |
| `Sent` | Approve 后状态；不证明电子发送已发生 |
| `Negotiating` | 可选状态值；非 revision 实体 |
| `Won/Lost` | 业务结果状态；Lost 不等于受控 Void |
| `已确认` | Convert 后中文状态，增加状态混用 |
| `quote_versions` | 版本头摘要表；活动生产者未知 |
| `version_no` | 文本版本槽位；生成规则未知 |
| print version `1.0` | 固定展示值，不是表记录解析结果 |
| print revision `""` | 空修订展示槽位 |
| `quotes.send_time` | 未被活动路径使用的发送时间槽位 |
| `quote_print_history` | 打印审计，而非 resend 审计 |
| operation log | Save Draft/Approve 等动作记录 |
| Copy Quote | 新独立 Quote，不是受控 revision |
| status redirect | 直接状态覆盖能力 |
| parent/revision FK | 当前 Quote 模型中未证实的关系 |
| void reason | 未建模/未证实字段 |
| readonly | 正常浏览器交互限制，不是服务端不可变约束 |
| line patch | 在状态检查前执行的 qty/price 原地更新 |
| Quote360 line mutation | 不受状态约束的行新增/删除与 total 重算 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| RRS-E01 | Approve 只允许 Draft | 强 | `apps/quotation/services.py::apply_approve_action` |
| RRS-E02 | Draft 行原地更新，无 snapshot | 强 | `apps/quotation/services.py`、`repository.py` |
| RRS-E03 | 通用 status handler 可覆盖状态 | 强 | `apps/quotation/services.py::update_quote_status_redirect` |
| RRS-E04 | Copy 创建新 Draft 并复制行 | 强 | `apps/quotation/services.py::copy_quote` |
| RRS-E05 | Copy 无 parent/version/source FK 继承 | 强负向 | `apps/quotation/services.py`、`repository.py` |
| RRS-E06 | quote_versions DDL 存在 | 强结构 | `runtime/v14/legacy_support.py` |
| RRS-E07 | versions helper/history 只读 | 强 | `apps/quotation/utils.py`、`history.py` |
| RRS-E08 | quotation 活动路径未见 versions insert/update | 强负向 | `apps/quotation/**` |
| RRS-E09 | print 固定 version 1.0/revision 空 | 强 | `apps/quotation/services.py`、`apps/print_center/v14_residual.py` |
| RRS-E10 | send_time 仅见 schema patch，未见活动使用 | 强负向 | `database/upgrade_patch.py`、`apps/quotation/**` |
| RRS-E11 | Quote templates 无 resend/revision/void 控件 | 强负向 | `templates/quote_detail.html`、`quote_approve.html`、`quotes.html` |
| RRS-E12 | print history 与发送事件模型分离 | 强 | `apps/quotation/**`、print center |
| RRS-E13 | 非 Draft UI 行 readonly 且隐藏 action footer | 强 | `templates/quote_approve.html` |
| RRS-E14 | POST service 先 patch/recompute，再处理 draft/approve 与状态 | 强 | `apps/quotation/services.py::apply_approve_action` |
| RRS-E15 | POST route 依赖 edit 权限，但不预先限制 Quote 状态 | 强 | `apps/quotation/router.py::quote_approve_post` |
| RRS-E16 | Quote360 Add Products 与 delete 控件没有 Draft 条件 | 强 | `templates/quote_detail.html` |
| RRS-E17 | add/delete routes 仅检查 edit/delete 权限 | 强 | `apps/quotation/router.py::add_quote_item`、`delete_quote_item` |
| RRS-E18 | add/delete services 不读 Quote 状态并重算 total | 强 | `apps/quotation/services.py::add_quote_item`、`delete_quote_item` |
| RRS-E19 | Copy/status canonical GET routes 未调用 permission checker | 强 | `apps/quotation/router.py::copy_quote`、`quote_status` |

## UNKNOWN + 已查路径

1. **quote_versions 是否由未接入当前 router 的外部程序写入 UNKNOWN。** 已查：`apps/quotation/**`、runtime、scripts、reports。
2. **Sent 后标准修订应回退 Draft 还是创建子 Quote UNKNOWN。** 已查：status、copy、history、templates、business_modules。
3. **Copy Quote 在业务口径中是否被当作 revision UNKNOWN。** 已查：copy service/repository、UI、version schema、reports。
4. **报价实际通过何种渠道发送给客户 UNKNOWN。** 已查：quotation、email/message/communication、templates、reports。
5. **send_time 由何路径写入 UNKNOWN。** 已查：schema patch、Quotation 全模块、jobs/scripts。
6. **Void 是否应映射 Lost 或独立 Cancelled UNKNOWN。** 已查：status handlers、i18n、templates、reports。
7. **已 Convert/有 SO 的 Quote 作废应如何反向处理 UNKNOWN。** 已查：Sales convert/cancel、Quotation status、lifecycle。
8. **operation log 的保留期与防篡改能力 UNKNOWN。** 已查：operation log helper、governance、DDL。
9. **version_no 的生成、唯一性和并发规则 UNKNOWN。** 已查：DDL、utils、history、repository。
10. **是否有上游代理阻止构造非 Draft POST UNKNOWN。** 已查：Quotation router/service、template、middleware。

## 交叉引用

- 版本权威：[`../sample-quote-bridge-deepen/quote_versioning.md`](../sample-quote-bridge-deepen/quote_versioning.md)
- Quote 状态：[`../quotation-deepen/quote_lifecycle.md`](../quotation-deepen/quote_lifecycle.md)
- Quote Approve：[`../quotation-deepen/quote_approve.md`](../quotation-deepen/quote_approve.md)
- 来源追溯：[`../sample-quote-bridge-deepen/source_traceability.md`](../sample-quote-bridge-deepen/source_traceability.md)
