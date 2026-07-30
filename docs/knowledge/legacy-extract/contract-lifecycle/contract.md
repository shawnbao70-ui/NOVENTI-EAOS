# 商业合同生命周期（Commercial Contract Lifecycle）— Legacy Knowledge

**Evidence strength:** Missing（商业合同实体与运营生命周期）/ Strong（通用文档分类）/ Weak（概念阶段、贸易文档类型、AI/风险占位）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件核查客户商业合同从草拟、审查、签署、生效、履约、变更、续签到到期/终止的证据，以及与客户、商机、报价、订单的链接。

结论：未找到商业合同主表、专属应用包、路由、页面、权限 slug 或状态机。可确认的仅有：

- Document Center 中 `contract` 通用文档 module key；
- GTFIP 的 `sales_contract` / `purchase_contract` 文档类型字符串；
- 完整性审查中的概念阶段 `contract`；
- AI `review_contract` 任务类型和固定 contract-expiration 风险卡片。

这些证据均不能证明商业合同生命周期已运营。已查路径见第 7 节；缺失项统一为 `UNKNOWN`。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| CONTRACT-LC-RULE-001 | `contract` 是 Document Center 的 module key，用于给通用文档元数据归类 | registry descriptor 标记 `enforced: false` | Strong |
| CONTRACT-LC-RULE-002 | 归入 contract 的文档可继承通用上传、下载、预览、版本、归档、恢复、收藏、标签、分享与历史能力 | 未见合同专属覆盖 | Strong |
| CONTRACT-LC-RULE-003 | Document Center 默认关闭 | 部署可另行启用；不证明具体合同文件存在 | Strong |
| CONTRACT-LC-RULE-004 | `legal` 是通用文档类别之一，可容纳法律文件但不专属于合同 | 不能用类别推导合同实体 | Strong |
| CONTRACT-LC-RULE-005 | GTFIP 文档目录列出 `sales_contract` 与 `purchase_contract` | 类型列表本身未生成、验证或关联合同主记录 | Weak |
| CONTRACT-LC-RULE-006 | 完整性审查把 Contract 放在 Negotiation 与 Sales Order 之间 | 需求驱动 lifecycle 与实际销售链均未接入此阶段 | Weak |
| CONTRACT-LC-RULE-007 | AI task center 可创建 `review_contract` 类型任务并分派给 document employee | 任务 input/output 无合同 schema 约束 | Weak |
| CONTRACT-LC-RULE-008 | 风险引擎固定发出“2 customer contracts renew within 30 days”卡片 | 不读取合同表或日期，是演示文案 | Weak |
| CONTRACT-LC-RULE-009 | 报价赢单/确认后自动生成合同为 `UNKNOWN` | 报价与销售转换路径未见合同调用 | Missing |
| CONTRACT-LC-RULE-010 | 合同审查、会签、签署授权、生效与用印规则为 `UNKNOWN` | 未见合同 workflow 或审批绑定 | Missing |
| CONTRACT-LC-RULE-011 | 合同变更、版本的商业效力、续签、到期、终止规则为 `UNKNOWN` | 通用 document version/archive 不等同商业状态 | Missing |
| CONTRACT-LC-RULE-012 | 合同与客户、商机、报价、销售订单的一致性和基数为 `UNKNOWN` | 无合同 FK/链接实体证据 | Missing |
| CONTRACT-LC-RULE-013 | 宪章文字要求 AI 不可独立缔约、租户对商业合同负责 | 属治理政策，不是 Legacy 合同运行门禁 | Medium policy evidence |

## 3. 流程

### 3.1 有证据的通用文档流程

若文件被归到 module key `contract`，通用能力可表达：

1. 注册/上传文档元数据与附件。
2. 放入类别、文件夹并添加标签。
3. 创建通用文档版本。
4. 预览、下载或分享。
5. 归档或恢复。
6. 记录通用文档历史事件。

该流程只管理内容文件，不产生合同金额、相对方、有效期或履约义务。

### 3.2 商业合同生命周期

`Draft → Review → Approved → Signed → Effective → Performing → Amended/Renewed → Expired/Terminated`

整条流程为 `UNKNOWN`。未找到阶段枚举、转换处理器、前置条件、审批矩阵、电子签章、提醒任务或履约联动。

### 3.3 商业链交界

`Customer / Opportunity / Quotation → Contract → Sales Order` 仅在完整性审查中有 Contract 概念位置；真实需求驱动链为 `… → Quotation → Sales Order`，没有 Contract。不得把概念清单当作可执行编排。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| CONTRACT-LC-VAL-001 | Document module key 必须属于 `DOCUMENT_MODULES` | 强（元数据） | 只校验分类键 |
| CONTRACT-LC-VAL-002 | 通用附件类型属于 image/pdf/office/zip/cad/video/audio/other | 弱/元数据 | 未见合同专属格式要求 |
| CONTRACT-LC-VAL-003 | 合同编号唯一、相对方存在、金额/币种有效 | 缺失 | `UNKNOWN` |
| CONTRACT-LC-VAL-004 | 生效日不晚于到期日 | 缺失 | 无日期字段 |
| CONTRACT-LC-VAL-005 | 签署前法务/商业/授权审批完成 | 缺失 | 无合同审批接线 |
| CONTRACT-LC-VAL-006 | 续签/到期提醒来自真实合同日期 | 缺失 | 风险卡片为固定文案 |
| CONTRACT-LC-VAL-007 | 合同必须关联报价或订单且商业条款一致 | 缺失 | 无关系与对账 |
| CONTRACT-LC-VAL-008 | AI review 不能自行签约 | 政策/非运行门禁 | 未找到合同动作可供硬拦截 |

## 5. 数据含义

| 概念 | Legacy 中可确认的含义 |
|---|---|
| `contract` | Document Center 通用模块分类键和标签 |
| `legal` | 通用文档类别，不是合同状态或主表 |
| Document registry/attachments/versions/sharing/archives/history | 内容管理记录，不是商业合同聚合 |
| `sales_contract` / `purchase_contract` | 国际贸易文档类型词汇 |
| completeness `contract` | 审查清单中的概念阶段 |
| `review_contract` | AI task 类型，可承载非结构化输入/输出 |
| `contract_expiration` | 风险类别；当前卡片未由合同数据计算 |

未找到的数据语义：合同编号、合同类型、甲乙方、客户/供应商、商机/报价/订单引用、签署人、金额、币种、签署/生效/到期/终止日期、履约义务、付款计划、附件法律版本、续签来源。全部 `UNKNOWN`。

## 6. 状态词汇

| 词汇 | 证据层 | 结论 |
|---|---|---|
| `contract` | 文档 module / 概念 lifecycle id | 不是业务状态 |
| `sales_contract` / `purchase_contract` | GTFIP doc type | 文档类型，不是状态 |
| Pending / In Progress / Completed / Failed / Cancelled | AI task status | 仅适用于 review task，不适用于合同 |
| contract expiration | 风险类别 | 固定风险文案，不证明到期状态 |
| Draft / In Review / Approved / Signed / Active / Expired / Terminated | — | `UNKNOWN`；未找到合同枚举 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\core\document\types.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\document\document.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\document\validator.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\document\metadata.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\documents.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\crm.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\README.md`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\engines\documents.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gfip\documents.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gfip\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\enterprise_completeness\review.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\enterprise_intelligence\risk_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\digital_employees\tasks.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\workforce\employee.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\constants.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\constitution\volume-02-eaos\BOOK01.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\constitution\volume-02-eaos\BOOK03.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\constitution\volume-02-eaos\BOOK06.md`

**Negative search:** 已检索 `apps/contract*`、`templates/*contract*`、`CREATE TABLE ... contract*`、contract route/service/repository/status/approval/effective/expiry/renewal/termination，以及客户、商机、报价、订单中的 contract 引用；未找到商业合同运营实现。
