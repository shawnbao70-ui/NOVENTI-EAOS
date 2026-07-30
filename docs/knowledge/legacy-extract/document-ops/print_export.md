# 打印、导出与 PDF

## Scope与证据强度

本页覆盖业务单据打印预览、浏览器打印、报表导出、CSV/Excel 标签、PDF、水印及打印权限。

- **强证据：** 运行路由、NDE 组装器、单据模板、权限检查和 A-008 等门禁相互印证。
- **中证据：** Print Center、Data Hub、打印队列及历史表具备注册表或元数据，但不主导文件生成。
- **弱证据：** 占位页面、未接线模板、导出适配器和设计文档。
- **明确缺失：** 检索范围内没有服务端 PDF、Word 或真正 XLSX 生成链。

## 业务规则

- **PX-R01** 打印入口要求登录；未登录用户转至登录页面。
- **PX-R02** 模块打印许可接受 `can_print`，也接受 `can_view`；管理员角色可绕过模块检查。因此“可查看即可能打印”是当前实现，不应理解为严格的导出隔离。
- **PX-R03** 业务打印的权威路径是 NDE HTML 预览；用户再通过浏览器打印，可在浏览器侧另存为 PDF。
- **PX-R04** Quote、SO、PO、DO、装箱单、形式发票、收款单和客户对账单存在可追踪的页面或引擎链。Invoice/AR、Certificate 虽有引擎分支，但未证明存在同等 UI 入口。
- **PX-R05** 装箱单号由 DO 号派生，形式发票号由 Quote 号派生，客户对账单号由客户标识派生；这些是打印语境编号，不必然等于持久化业务主键。
- **PX-R06** 不支持的模块或不存在的来源可落到通用占位预览，而非稳定返回“单据不存在”；占位页不得作为成功生成证明。
- **PX-R07** “Export Excel”实际上导出浏览器当前表格的 CSV Blob，不是 XLSX。
- **PX-R08** Report Export 只记录导出历史并返回报表页，未生成或返回文件。
- **PX-R09** V15 Print Center、Data Hub 导出注册表及水印注册表是元数据/框架层；Legacy NDE 仍是运行权威。
- **PX-R10** 水印取决于品牌与模板开关；未发现业务状态自动映射到文本水印的完整运行链。
- **PX-R11** 打印预览操作可以写入文档操作审计，但浏览器最终是否打印、取消或保存为 PDF，不受服务端可靠确认。

## 流程

### 业务单据打印

1. 用户从业务列表或详情页进入 Quote 专用打印路由，或通用模块打印预览路由。
2. 系统检查登录状态和模块打印/查看权限。
3. 系统读取品牌、文档模板配置及来源业务数据。
4. NDE 将来源数据转换为统一打印语境，并选择 `templates/documents` 下的模板。
5. 服务端返回 HTML 预览；用户调用浏览器打印。
6. 系统记录预览/打印类操作；浏览器侧输出不是服务端文件资产。

### 表格 CSV 导出

1. 用户在企业表格点击标为 Excel 的导出入口。
2. 客户端读取当前 DOM 表格。
3. 浏览器生成 CSV Blob 并下载。
4. 服务端没有生成 XLSX，也没有可证明的集中导出审计。

### Report Export

1. 用户请求导出报表。
2. 服务端读取报表模板并新增历史记录。
3. 请求重定向回报表页面；检索范围内无文件响应。

## 校验

- **PX-V01** 打印 module 必须属于 NDE 支持集合；未知 module 不能生成业务模板。
- **PX-V02** 来源记录、品牌和模板需能解析；来源不可用时当前路径可能返回占位页，因此调用方还需区分业务预览与占位响应。
- **PX-V03** 无模块打印或查看许可时返回权限拒绝。
- **PX-V04** A-008 门禁覆盖装箱单、形式发票和对账单的引擎、模板、UI 与固定链接约束。
- **PX-V05** 业务门禁覆盖 Quote、SO、DO、PO、Receipt 等预览链接，但门禁通过不证明浏览器最终产生文件。
- **PX-V06** V15 打印校验器只验证模块 key；不等同于文件生成、内容完整性或打印设备验证。
- **PX-V07** 未发现 PDF/XLSX 生成依赖；任何声称“服务端 PDF/Excel 已落地”的需求都应先检索 HTTP 二进制响应和部署依赖。

## 数据含义

| 数据/概念 | 含义 |
|---|---|
| `nde` | 打印模板消费的统一单据语境，不是独立业务单据 |
| `PrintPreview` / `Print` | 文档操作审计中的预览/打印操作；不证明物理输出完成 |
| `print_templates` | 打印模板注册或配置，不等于模板已接入运行链 |
| `report_history` | 报表导出动作历史；不等于存在导出文件 |
| `show_watermark` / 品牌水印路径 | 模板与品牌共同决定的视觉开关 |
| `landscape` | 预览的横向打印偏好 |
| CSV | 客户端表格文本导出；UI 可能称为 Excel |
| `PL-{do_no}` / `PI-{quote_no}` / `STMT-{customer_id}` | 打印语境中的派生编号 |

## 状态词汇

| 状态 | 解释 |
|---|---|
| `Draft` / `Open` / `Paid` | 打印语境显示的业务状态；Receipt 预览中的 Paid 可能是固定值 |
| `Submitted` / `Approved` / `Rejected` / `Cancelled` / `Closed` | 文档平台定义的审批词汇；不代表所有打印单据使用统一状态机 |
| `Active` | 打印模板 API 的可用过滤状态 |
| `ready` | 打印适配器可用，不表示 PDF/Excel 可用 |
| `not_implemented` / `unsupported` | 文件导出适配器未实现或格式不支持 |
| `print_started` / `print_completed` | V15 历史元数据词汇；非 Legacy NDE 主链的权威完成信号 |

## UNKNOWN

- `/print_quote` 在打印中心残留路由与报价模块存在同路径注册；实际优先级 **UNKNOWN**。需在运行实例导出路由表，检索 `apps/print_center/v14_residual.py` 与 `apps/quotation/router.py` 的挂载顺序。
- 业务状态到文本水印的自动映射 **UNKNOWN/未证明接线**。已检索 `document/`、`core/printing/`、`templates/documents/`。
- Certificate 和 Invoice/AR 的最终 UI 入口 **UNKNOWN**。已检索业务模板和 `print_preview` 链接；引擎支持不能替代入口证据。
- 浏览器打印成功、取消或另存为 PDF 的可靠回执 **UNKNOWN**。需检索前端打印事件采集和运行审计数据。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_v1_framework.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\v14_platform.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\print_center\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\platform\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\report_center\`
- `H:\Workspace\EZAM_CRM - 9.0\core\permission\checker.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\printing\`
- `H:\Workspace\EZAM_CRM - 9.0\core\datahub\exporter.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\documents\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\print\`
- `H:\Workspace\EZAM_CRM - 9.0\static\v11\enterprise-table.js`
- `H:\Workspace\EZAM_CRM - 9.0\scripts\business_strong_a008_print_gate.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V41_Print_Report_Document_Matrix.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V14_CODE_AUDIT_REPORT.md`
