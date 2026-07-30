# 合规记录、证书与批次追溯（Compliance Records）— Legacy Knowledge

**Evidence strength:** Medium for document/requirement metadata; weak for certificate facts and batch traceability  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 中“合规”分散在五个不等价层面：

1. 样品需求中的 `certification_requirement` 文本；
2. NDE 的 Certificate / QC Report / Inspection Report 文档类型与模板；
3. Document Center 的元数据型附件、版本、分享、归档和历史注册表；
4. 打印数字签名中的 `certificate_no`；
5. 样品/报价/订单等需求链与库存流水中的来源备注。
6. GFIP/GTFIP 贸易订单的文档 checklist、`gfip_documents` 状态/验证位，以及 HS 推荐返回的证书名称。

这些元素不足以证明证书台账、证书有效期、产品-批次证书绑定或端到端 lot/serial traceability。GFIP/GTFIP 的“verified/ready”是贸易文档行状态，不是证书真实性、有效期或签发机构校验。库存主线没有 lot/batch/serial/expiry 字段；`batch_print_queue.batch_no` 是打印批次，不是产品批次。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / caveat |
|----|--------------------------|-------------------|
| CMP-R1 | 样品需求可保存认证要求文本 | 不拆分证书类型、标准、签发机构或有效期 |
| CMP-R2 | 认证要求与样品质量评价是独立记录 | 没有自动符合性判定 |
| CMP-R3 | NDE 注册 Certificate、QC Report、Inspection Report 和 Material Analysis Report | 文档类型目录不等于已生成合规事实 |
| CMP-R4 | Certificate 预览以 sample ID 查询样品并生成文档号候选 | 模板正文只显示 remark/签名，未装载测试结果或证书字段 |
| CMP-R5 | 若样品存在，Certificate 文档号可取 sample_no | 这不是独立证书唯一号 |
| CMP-R6 | Inspection Report 模板使用通用产品表和工作流块 | 未见规格、实测值、结论或检验员专用模型 |
| CMP-R7 | V13 文档类型字典包含 Certificate 与 Inspection Report | 是分类能力，不证明文件实例存在 |
| CMP-R8 | Document Center 附件、版本、分享、归档多为 `implemented=0` / `metadata_only` | 不能声称合规文档已受版本和保留控制 |
| CMP-R9 | Digital Signature 的 `certificate_no` 属于签名者/签名配置 | 不应解释为产品质量证书编号 |
| CMP-R10 | 样品可通过 requirement/opportunity 链连接到报价和销售订单 | 这是需求追溯，不是批次谱系 |
| CMP-R11 | `Sample Receipt` 以 `SAMPLE-{id}` 备注追到样品 | 只到样品记录，未到实物 lot/serial |
| CMP-R12 | `PO Receipt` 以 `PO-{id}` 备注追到采购单 | 只到 PO，未记录供应商批号/生产日期/证书 |
| CMP-R13 | 库存 ledger 记录产品、动作、数量、余额、备注和时间 | 不记录 warehouse lot、serial、expiry 或 document key |
| CMP-R14 | 产品/库存只有 SKU 级数量 | 同 SKU 多批次被汇总，无法执行批次召回 |
| CMP-R15 | 打印 `batch_no` 只用于批量打印队列 | 不得当成库存/生产批号 |
| CMP-R16 | 合规证书不得仅由空模板和品牌签名推定有效 | 缺少签发人、范围、依据、结果和有效期 |
| CMP-R17 | 国家/海关元数据可作为法域上下文 | 不自动证明产品符合当地法规 |
| CMP-R18 | 文档打印操作日志只证明 Print/Export 等操作 | 不证明证书审批、签发或撤销 |
| CMP-R19 | GFIP 文档核验把 `verified=1` 或 `status='ready'` 计为 complete | 这是行状态判定，不校验文件内容或证书有效性 |
| CMP-R20 | GFIP 的 `ready_to_ship` 仅取决于当前文档行是否 missing | 计算出的 Incoterm 附加要求未并入 missing 判定 |
| CMP-R21 | CIF/CFR 追加保险证书、DDP 追加进口申报和海关文件只形成列表 | 当前返回值未把该列表暴露为阻断结果 |
| CMP-R22 | GTFIP 文档目录包含 CO、检验证书、MSDS、CE、RoHS 与优惠原产地表单 | 类型枚举不证明实例存在或有效 |
| CMP-R23 | GTFIP auto-generate 只把三类核心出口文档行置 `ready/verified` | 不生成可核验文件内容；异常时仍返回生成名称 |
| CMP-R24 | GTFIP country-specific 选择把输入截成前两字符 | `CN` 可命中；`ASEAN`/`GENERAL` 映射按现逻辑不可达 |
| CMP-R25 | HS 推荐按描述关键词返回证书名称 | 规则型建议不是法规判定或证书签发 |
| CMP-R26 | HS 推荐会持久化税率、FTA、证书和备选编码 | 仍缺少人工核验、法源版本与证书实例绑定 |

---

## 3. Process

### 3.1 样品认证要求

1. 在样品需求中人工填写 `certification_requirement`。
2. 系统以文本形式保存，并在取最新 requirement 时可被读取。
3. 未观察到把要求拆为标准条款、任务、证书请求或验收条件。
4. 未观察到要求满足后自动更新样品或报价状态。

### 3.2 Certificate / Inspection 文档表面

1. 打印入口按文档模块与 source ID 解析文档类型。
2. Certificate 路径尝试读取样品及产品名称/代码。
3. NDE 构建通用文档 context 并选择 Certificate 模板。
4. Certificate 模板仅提供 remark、签名和返回链接；Inspection 模板只提供产品表、时间线。
5. 打印操作可写文档操作日志；未见正式签发、版本冻结或撤销。

### 3.3 当前可达的来源追溯

1. 样品可关联 requirement/opportunity/product。
2. 样品物化生成 `Sample Receipt`，remark 指向 sample ID。
3. 采购收货生成 `PO Receipt`，remark 指向 PO ID。
4. 库存按 SKU 汇总，并可查看 ledger 时间线。
5. 出库可形成 DO Ship 记录，但没有 lot/serial 分配，因此无法由成品反查具体来料批。

### 3.4 缺失的合规闭环

未观察到：证书申请 → 文件上传/校验 → 产品/供应商/批次绑定 → 审批签发 → 生效/到期 → 提醒 → 暂停/撤销 → 归档 → 出货随附与召回。

### 3.5 GFIP/GTFIP 贸易文档旁路

1. 贸易订单创建时拥有预定义文档行。
2. checklist 按海运/空运排除 AWB 或 B/L，并给出打印预览 URL。
3. 核验以行的 `status`/`verified` 判断 complete/missing；未读取证书内容、签发机构或有效期。
4. GTFIP auto-generate 可直接标记商业发票、装箱单、原产地证为 ready/verified。
5. HS 推荐可给出证书名称和 FTA 表单提示，但不能替代合规人员确认。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CMP-V1 | 认证要求必须使用受控标准代码 | Missing | 自由文本 |
| CMP-V2 | Certificate 必须有独立唯一证书号 | Missing | 可复用 sample_no |
| CMP-V3 | 证书必须有签发机构、签发日、有效期 | Missing | 专用字段不存在 |
| CMP-V4 | 证书必须绑定产品和适用批次/序列 | Missing | 无 lot/serial |
| CMP-V5 | 证书文件需 MIME/大小/恶意内容校验 | Not proven in Document Center | 注册层 metadata-only |
| CMP-V6 | 证书版本只能有一个 latest 且不可篡改 | Not enforced | `document_versions` 无强约束且 implemented=0 |
| CMP-V7 | 到期/撤销证书不得用于出货 | Missing | 无 expiry/revoked 与 ship gate |
| CMP-V8 | 检验报告必须含规格、实测、判定与签名 | Missing | 通用模板不足 |
| CMP-V9 | 批次 ID 必须在收货、库存和出库间保持 | Not modeled | SKU 汇总库存 |
| CMP-V10 | 流水来源备注必须引用真实存在的 source | Weak | 字符串约定，无外键 |
| CMP-V11 | 文档操作日志不能替代签发审计 | Semantic guard | Print/Export 与 Approve/Issue 不同 |
| CMP-V12 | 数字签名证书号不得混作产品证书 | Semantic guard | 数据主体不同 |
| CMP-V13 | 法域/国家必须与适用合规规则匹配 | Missing | country metadata 未驱动证书规则 |
| CMP-V14 | 召回必须能定位受影响库存和客户 | Impossible from observed model | 缺少 lot/serial genealogy |
| CMP-V15 | Incoterm 附加文档必须进入 missing/ready-to-ship 判定 | Missing | `required_extra` 未参与结果 |
| CMP-V16 | `verified=1` 前必须校验实际文件、签发方和有效期 | Missing | 只见状态位 |
| CMP-V17 | auto-generate 失败不得报告已生成 | Weak | RuntimeError fallback 仍返回三类名称 |
| CMP-V18 | 国家/区域表单选择必须覆盖 ASEAN/GENERAL | Violated risk | 两字符截断使现有键不可达 |
| CMP-V19 | HS 推荐必须经权威税则版本和人员复核 | Missing | 关键词启发式、固定税率/证书 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `sample_requirements.certification_requirement` | 客户/市场对认证的自由文本要求 |
| `sample_id` | 样品记录引用；可作当前 Certificate source |
| `sample_no` | 样品编号；Certificate 路径可能把它当文档号 |
| `NDE_DOCUMENT_TYPES.Certificate` | 可选打印文档类型 |
| `Inspection Report` | 通用报告版式类型，不是检验记录实体 |
| `QC Report` | NDE 类型目录项，未见专用活动模板映射 |
| `digital_signatures.certificate_no` | 签名配置中的证书号 |
| `document_attachments` | Document Center 附件元数据；默认未实现 |
| `document_versions` | 版本元数据；默认未实现 |
| `document_archives` | 归档元数据；metadata-only |
| `document_history` | 文档事件元数据，不等同业务签发审计 |
| `requirement_id/opportunity_id` | 需求来源链字段 |
| `inventory_ledger.trans_type` | 库存动作类型 |
| `inventory_ledger.remark` | 约定式来源引用，如 `PO-{id}` / `SAMPLE-{id}` |
| `inventory_ledger.create_time` | 库存动作时间 |
| `inventory.stock_qty` | SKU 汇总现存量 |
| `batch_print_queue.batch_no` | 批量打印作业号，非产品批次 |
| `gfip_documents.status` | 贸易文档行阶段；`ready` 被视为 complete |
| `gfip_documents.verified` | 贸易文档验证位；不证明证书真实性 |
| `ready_to_ship` | 当前文档行均 complete 的派生布尔值；未完整纳入 Incoterm 附加项 |
| `GTFIP_DOCUMENT_TYPES` | 贸易文档类型目录，含 CE/RoHS/MSDS/检验证书等 |
| `COUNTRY_FORMS` | 国家/区域到优惠表单的静态映射；部分键按当前截断逻辑不可达 |
| HS `required_certificates` | 描述关键词规则返回的证书建议列表 |
| lot / serial / expiry | 库存和收发主线中 UNKNOWN / 未建模 |

---

## 6. State Vocabulary

| Value / flag | Meaning / caveat |
|--------------|------------------|
| `active` / `Active` | 文档模块、签名等配置活动；不证明证书有效 |
| `implemented=0` | 附件/版本/归档能力没有执行实现 |
| `metadata_only` | 只保存注册元数据 |
| `is_latest=1` | 概念上的最新版本标记，未见唯一约束 |
| `completed` | Document history 默认事件状态，不等于合规审查完成 |
| `CERTIFICATE` | 文档类型代码 |
| `INSPECTION_REPORT` | 文档类型代码 |
| `QC_REPORT` | NDE 文档类型代码 |
| `PO Receipt` / `Sample Receipt` / `DO Ship` | 库存来源动作，不是合规状态 |
| `pending` / `ready` | GFIP 文档行阶段，不等于证书 Pending/Valid |
| `verified=1` | GFIP 行级完成标志，不等于外部机构验真 |
| `Valid`, `Expired`, `Suspended`, `Revoked` | 期待的证书状态；活动模型未发现 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 是否存在正式证书实例表及唯一证书号 | full-repo certificate/COA/COC/MSDS search；Document Center schemas；runtime DDL |
| 是否上传和验证证书原文件 | `apps/document_center/**`, `core/document/**`, upload services, governance documents knowledge |
| 是否记录证书签发机构、生效/到期/撤销 | certificate templates、NDE context、document metadata schema、expiry/revoked search |
| 是否存在库存 lot/batch/serial | `apps/inventory/**`, procurement receipt, runtime DDL, full-repo lot/batch/serial search |
| 是否存在供应商批次与制造批次映射 | `apps/procurement/**`, supplier paths, purchase templates, inventory ledger |
| 是否支持由出货追溯到来料批/客户召回 | delivery/ship services, inventory ledger, lifecycle schema and templates |
| Inspection/QC Report 的结果数据来源 | `document/nde_engine.py`, inspection templates, sample quality tables, print reports |
| 样品认证要求如何被验证为满足 | `apps/sample/**`, sample templates, quote conversion, approval paths |
| 海关/国家规则是否强制证书 | customs paths、country templates、business_modules、governance/customs knowledge |
| GFIP/GTFIP `verified` 是否有文件内容校验器 | `v15/gfip/documents.py`, `v15/gfip/repository.py`, `v15/gtfip/engines/documents.py`；未发现 |
| HS 证书建议由谁复核、基于何版税则 | `v15/gtfip/engines/hs_code.py`, customs/HS paths；未发现审批或法源版本 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `runtime/v14/legacy_support.py` | `certification_requirement`、数字签名 certificate_no、文档类型和库存结构 |
| `apps/sample/services.py` | 样品要求写入及质量/物化链 |
| `apps/sample/router.py` | 认证要求表单入口 |
| `database/business_lifecycle_schema.py` | requirement/opportunity 到 sample/quote/SO 的来源链 |
| `templates/includes/business/lifecycle_traceability.html` | 业务记录上下游展示，不是 lot genealogy |
| `apps/sample/repository.py` | `SAMPLE-{id}` 幂等来源引用 |
| `apps/procurement/services.py` | `PO-{id}` 收货来源与 SKU 入库 |
| `apps/inventory/repository.py` | ledger 字段与 SKU 汇总库存，缺少 lot/serial |
| `document/nde_engine.py` | Certificate/Inspection/QC 类型与 sample-based Certificate context |
| `templates/documents/certificate.html` | Certificate 通用空壳 |
| `templates/documents/inspection_report.html` | Inspection 通用产品表/时间线壳 |
| `database/v151_document_center_schema.py` | 附件、版本、分享、归档为未实现/metadata-only |
| `apps/document_center/repository.py` | Document Center 元数据与历史 |
| `business_modules/documents.md` | 文档权威边界和已知风险 |
| `docs/reports/V41_Print_Report_Document_Matrix.md` | 活动业务文档矩阵未证明质量证书闭环 |
| `docs/reports/V151E_Volume011_Supplier_Procurement_Business_Chain_Extraction_Report.md` | Sample/Procurement 提取范围与已知限制 |
| `v15/gfip/documents.py` | 文档 checklist、行状态核验及 Incoterm 附加要求缺口 |
| `v15/gfip/repository.py` | `gfip_documents` 状态/验证字段与订单文档初始化 |
| `v15/gtfip/engines/documents.py` | 扩展贸易文档目录、国家表单映射和三类自动标记 |
| `v15/gtfip/engines/hs_code.py` | 关键词式 HS、FTA 和证书建议及持久化 |
| `docs/knowledge/legacy-extract/governance/documents.md` | Document Center 元数据边界交叉引用 |
| `docs/knowledge/legacy-extract/governance/customs.md` | 国家/海关交界交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为当前 EAOS 交叉引用）。
