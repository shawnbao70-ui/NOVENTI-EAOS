# 文档中心（Document Center）— Legacy Knowledge

**Evidence strength:** Medium for registries and schema; weak for document execution  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Documents 被边界文档定义为跨模块内容权威，目标范围包括存储、模板、生成、附件、预览和文档 AI。V15.1 可确认的是一套**默认关闭、元数据优先**的 Document Center 基础，提供模块、分类、文件夹、标签、附件类型、版本、分享、归档、历史等注册信息和框架页面。

该基础明确“不替代 Legacy 文档管理”。以下名称虽然存在，但不能据此推定执行能力：

- 上传、下载、预览、版本、回滚、归档、恢复、分享等是特性目录；
- Attachment、Version、Sharing、Archive 注册项均标为未实现或 metadata-only；
- NDE/打印引擎仍独立负责报价、订单、发票、交付等业务文档输出；
- `contract` 仅是 Document Center 的模块标签，不是商业合同业务模块。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 / UNKNOWN | EAOS 重写备注 |
|----|----------|----------|----------------|----------------|
| DOC-R1 | 文档记录必须归属预定义模块键 | 验证文档元数据 | 模块键只分类内容，不证明对应业务模块存在 | 将分类与业务聚合分开 |
| DOC-R2 | 文档模块覆盖报价、销售单、采购单、发票、收款、交付单、装箱单、合同、客户、供应商、产品、样品、财务、审批、海关等 | 注册中心初始化 | 所有模块 `enforced=false` | 注册目录不是执行约束 |
| DOC-R3 | Document Center 默认关闭，Legacy 文档功能继续作为权威 | 系统启动/框架页 | 哪些租户启用 UNKNOWN；检索 `core/document/types.py`、`apps/document_center/` | 显式管理启用状态 |
| DOC-R4 | 文档分类包括业务、财务、仓库、人事、工程、法务、行政和自定义 | 分类注册 | 分类没有业务专属状态机 | 分类仅用于组织 |
| DOC-R5 | 文件夹意图支持层级、路径、所有者和权限 | 文件夹注册 | 仅元数据，权限执行 UNKNOWN | 不声称已实现 ACL |
| DOC-R6 | 附件类型目录支持图片、PDF、办公文件、ZIP、CAD、视频、音频和其他文件 | 附件注册 | 注册器明确无上传或预览实现 | 存储能力需另证 |
| DOC-R7 | 版本目录描述版本号、历史、回滚和最新版本 | 版本注册 | 明确无回滚执行 | 版本不可仅靠标志实现 |
| DOC-R8 | 分享目录区分内部团队、客户门户和供应商门户 | 分享注册 | 明确无实际分享引擎 | 外部分享需授权、有效期和撤销 |
| DOC-R9 | 归档目录预置财务、人事和通用归档 | 归档注册 | 明确无归档执行 | 归档需保留策略和不可篡改性 |
| DOC-R10 | 历史事件词汇覆盖上传、下载、预览、归档、恢复、分享和版本创建 | 历史注册 | 事件存在不证明所有动作实际产生日志 | 审计应随真实命令原子写入 |
| DOC-R11 | `contract` 标签只表示“合同内容域的文档” | 模块分类 | 未发现合同 CRUD、商业主表、审批状态机、签署或续期流程 | 合同能力如需建设属于新设计 |
| DOC-R12 | `legal` 分类可能容纳合同文件，但不等于合同主数据 | 文件分类 | 法务分类可包含其他文件 | 不从目录反推合同实体 |
| DOC-R13 | Invoice、Quote、SO、DO 等可由 NDE/打印层输出 | 业务文档预览/打印 | 该输出不自动写 Document Center 版本或归档 | 文档生成与内容治理需建立桥接 |
| DOC-R14 | 文档审批被列为 Approval 的消费者 | 文档发布 | 实际文档发布 gate UNKNOWN；检索 `business_modules/approval.md`、`apps/document_center/` 未见闭环 | 发布状态必须由审批结果驱动 |
| DOC-R15 | Document AI 是独立辅助面 | 文档 AI 页面/API | OCR、分类、摘要到正式文档元数据的承诺 UNKNOWN | AI 输出必须标来源与人工确认 |
| DOC-R16 | 宪章要求商业单据具有永久编号 | 业务单据建立 | V15.1 registry 不负责业务编号 | 编号属于业务事实，文档版本需引用 |
| DOC-R17 | 宪章要求商业单据归档而非物理删除 | 生命周期结束 | V15.1 Archive 只有元数据，无执行 | 删除策略不得违背保留要求 |
| DOC-R18 | Live NDE 是业务打印/呈现引擎，V15.1 Print Center 与 Document Center 是并列且默认关闭的元数据中心 | 打印/文档治理 | 三层能力名称易混淆 | 分别记录内容、打印与生命周期责任 |
| DOC-R19 | Document history 遇到未知事件类型时会降级为 uploaded 事件 | 写历史 | 会掩盖真实未知动作 | 未知事件应拒绝或保留原值 |

---

## 3. 流程

### 3.1 V15.1 注册初始化

1. 初始化文档模块、分类、文件夹、标签、附件、版本、分享、归档和历史注册数据。
2. 若数据库注册表为空，则持久化元数据。
3. 框架页面和 API 列出注册项及健康状态。
4. **流程在元数据层结束**；不替代既有上传、预览或业务文档生成。

### 3.2 概念性文档生命周期

Legacy 特性目录描述以下概念顺序：

1. 上传或登记文档；
2. 归属模块、分类、文件夹和标签；
3. 下载或预览；
4. 建立新版本并识别最新版本；
5. 分享给内部或外部范围；
6. 归档或恢复；
7. 记录历史事件。

除元数据登记外，上述执行步骤在 V15.1 Document Center 中多数为 **UNKNOWN / 未实现**。

### 3.3 业务文档输出边界

1. 报价、销售订单、交付单、发票或形式发票从业务上下文组装打印数据。
2. NDE/打印层选择对应文档版式并预览/打印。
3. 是否自动形成 `document_registry` 记录、版本、分享或归档：**UNKNOWN**。已检索 `document/nde_engine.py` 与 `apps/document_center/`，未观察到可靠自动桥接。

### 3.4 合同诚实边界

1. Document Center 注册 `contract` 模块键。
2. 文件可在概念上归入合同内容域或 legal 分类。
3. 未观察到合同起草、法审、签署、生效、变更、到期或终止流程。
4. 因此只能迁移合同相关文件（若实例数据存在），不能据标签生成合同业务记录。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| DOC-V1 | 文档元数据必须有 `module_key` | Hard in validator |
| DOC-V2 | `module_key` 必须属于预定义模块目录 | Hard in validator |
| DOC-V3 | 分类键必须属于预定义分类 | Registry validation | 自定义分类如何落地 UNKNOWN |
| DOC-V4 | 附件类型必须属于预定义类型 | Registry validation |
| DOC-V5 | 文件大小、扩展名、MIME、病毒扫描 | UNKNOWN | `core/document/attachment.py` 明确无上传实现 |
| DOC-V6 | 文件夹所有者/权限强制执行 | UNKNOWN | 仅特性元数据 |
| DOC-V7 | 版本号唯一、最新版本唯一 | UNKNOWN | 注册器无执行 |
| DOC-V8 | 回滚权限与审计 | Not implemented |
| DOC-V9 | 外部分享授权、有效期、撤销 | Not implemented |
| DOC-V10 | 归档保留期、法律冻结、恢复权限 | Not implemented |
| DOC-V11 | 文档发布必须审批通过 | UNKNOWN | 边界声明有依赖，活动闭环未见 |
| DOC-V12 | `contract` 文档必须关联合同主记录 | Not possible from observed model | 无合同主记录证据 |
| DOC-V13 | 商业单据永久编号不可重复或重用 | Required by constitution; runtime UNKNOWN | Center validator 不检查业务编号 |
| DOC-V14 | 归档记录不得物理删除 | Required by constitution; V15.1 execution missing |
| DOC-V15 | 历史事件必须准确反映实际动作 | Weak | 未知事件会降级为 uploaded |

---

## 5. 数据含义

### 5.1 Document Center 元数据实体

| Entity | 含义 |
|--------|------|
| `document_registry` | 文档模块/记录注册元数据，不等同文件内容仓库 |
| `document_categories` | 文档分类 |
| `document_folders` | 文件夹和层级意图 |
| `document_tags` | 标签 |
| `document_attachments` | 附件元数据 |
| `document_versions` | 版本元数据 |
| `document_sharing` | 分享元数据 |
| `document_archives` | 归档元数据 |
| `document_history` | 文档事件历史 |

### 5.2 模块键语义

`quotation`、`sales_order`、`purchase_order`、`invoice`、`receipt`、`delivery_order`、`packing_list`、`contract`、`customer`、`supplier`、`product`、`sample`、`finance`、`approval`、`implementation`、`customs`、`shipping`、`warehouse`、`hr`、`general_documents` 都是内容归属标签。

### 5.3 合同字段的诚实解释

| Concept | Legacy 可证实含义 |
|---------|-------------------|
| `contract` module key | “Contract”文档内容域标签 |
| `legal` category | 可容纳法律文件的通用分类 |
| 合同业务主表 | UNKNOWN / 未发现 |
| 合同状态 | UNKNOWN / 未发现 |
| 合同审批链 | UNKNOWN / 未发现 |
| 合同签署/印章 | UNKNOWN / 未发现 |

已检索 `core/document/types.py`、`core/document/document.py`、`business_modules/`、`apps/` 中合同命名；可确认的是标签与少量设计/AI占位，不足以证明商业合同模块。

### 5.4 特性标志

`implemented=false`、`metadata_only` 或 `enforced=false` 表示目录可被发现，但不应解读为可执行生产能力。

---

## 6. 状态词汇

| Status / flag | 使用位置 | 含义 |
|---------------|----------|------|
| `implemented=false` | 附件、版本等注册项 | 尚无执行实现 |
| `metadata_only` | 分享、归档等条目 | 仅元数据 |
| `enforced=false` | 文档模块注册 | 不强制替代 Legacy 行为 |
| `is_latest` | 示例版本元数据 | 概念上的最新版本标记 |
| enabled by default = false | Document Center | 默认不启用 |

文档事件词汇包括 uploaded、downloaded、previewed、archived、restored、shared、version_created；它们是规范词汇，不保证每个动作已有运行链路。

### 三层运行含义

| Layer | Legacy 含义 |
|-------|-------------|
| Legacy NDE / file / print | 实际业务文档预览、打印与文件能力 |
| V15.1 Print Center | 默认关闭的打印元数据注册中心 |
| V15.1 Document Center | 默认关闭的文档生命周期元数据注册中心 |

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `business_modules/documents.md` | Documents 边界、消费者、权限与风险 |
| `core/document/types.py` | 模块、分类、特性、附件、版本和历史词汇 |
| `core/document/document.py` | 模块标签、`contract` 标签与 `enforced=false` |
| `core/document/validator.py` | 模块/分类/附件校验 |
| `core/document/attachment.py` | 附件仅元数据、无上传/预览实现 |
| `core/document/version.py` | 版本与回滚仅元数据 |
| `core/document/sharing.py` | 内外部分享仅元数据 |
| `core/document/archive.py` | 归档仅元数据 |
| `apps/document_center/` | 注册 facade、框架页面、仓储和健康 |
| `database/v151_document_center_schema.py` | 九个 Document Center 元数据表 |
| `docs/reports/V151_Volume008_Document_Center_Report.md` | 默认关闭、元数据基础和已知限制 |
| `document/nde_engine.py` | 业务文档组装/打印与中心注册边界 |
| `core/document/history.py` | 未知事件类型降级行为 |
| `docs/constitution/volume-02-eaos/BOOK07.md` | 商业单据永久编号与归档不删除原则 |
| `docs/reports/V151_Volume006_Print_Center_Report.md` | Print Center 与 Document Center 的并列边界 |
| `docs/reports/V41_Print_Report_Document_Matrix.md` | Live 打印入口与 Invoice 非独立 Hub 原则 |
| `business_modules/approval.md` | Documents 作为审批消费者的边界声明 |
| `core/document/types.py` / `business_modules/` / `apps/` | 合同业务 UNKNOWN 的检索范围 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
