# 附件上传、关联单据与权限交界

## Scope与证据强度

本页覆盖上传校验、产品/样品图片与文件、File Center、Knowledge 附件、品牌资源、静态读取、删除、租户和权限边界。

- **强证据：** 上传校验内核、活跃路由、服务、DDL、静态挂载和模板。
- **中证据：** 租户列、版本/分享/日志等表结构存在，但不能证明所有运行查询已接线。
- **弱证据：** Enterprise Attachment Engine 和统一附件模型仍是架构目标。
- **明确缺失：** customer/quotation 独立上传路由、统一 `attachments` 实体和规格所述 `/upload_document` 未在检索范围内落地。

## 业务规则

- **ATT-R01** 活跃上传统一调用安全校验器，并按 general、image、document、brand 分类使用扩展名白名单。
- **ATT-R02** 上传拒绝空文件、受阻脚本/可执行扩展名和超限文件；默认上限为 10MB，可由环境配置调整。
- **ATT-R03** 文件名会去路径并字符净化，但校验以扩展名和大小为主；未证明有 MIME 魔数或病毒扫描。
- **ATT-R04** 存储分裂为 `uploads/` 与 `static/uploads/`：产品、样品和品牌主要走前者，File Center/Knowledge 走后者。
- **ATT-R05** 产品主图、图库和产品文档使用不同字段/子表；删除产品会清主图与图库，但未完整清理产品文档记录和磁盘文件。
- **ATT-R06** 样品有三个固定图片槽及附加图库；清空固定槽只置空数据库字段，不删除磁盘文件。
- **ATT-R07** File Center 用 `file_library` 保存文件号、路径、模块名和来源 ID，可作为通用单据关联；关联合法性主要依赖调用方传参。
- **ATT-R08** Knowledge 附件在 `file_library` 之外增加文章关联；解除关联只删除链接，保留文件库记录和物理文件。
- **ATT-R09** 产品、样品和平台通用上传未见一致的服务端 RBAC；Knowledge 和品牌上传有较明确的权限检查。
- **ATT-R10** `/uploads` 是公开静态挂载；知道 URL 的读取者不经过逐文件会话或单据权限检查。
- **ATT-R11** 多数活跃上传未使用租户目录 helper，附件关联 SQL 也未证明按 tenant 过滤。
- **ATT-R12** 统一 Attachment Engine 返回 `DEFER_TO_LEGACY`，运行权威仍是多套 Legacy 存储和关联模型。
- **ATT-R13** Customer 和 Quotation 无独立上传链；Quotation 只消费产品图片。

## 流程

### 产品图片或文档

1. 客户端提交 multipart 文件到产品上传入口。
2. 系统按 image 或 document 类型校验并净化文件名。
3. 文件写入产品共享上传目录。
4. 图片写入产品图库关系；文档写入产品文件元数据。
5. 产品详情页通过静态 URL 展示或访问。

### 样品图片

1. 固定槽上传形成按样品和槽位命名的文件，并更新 `image1/2/3`。
2. 图库上传形成独立文件和 `sample_images` 行。
3. 固定槽删除仅清 DB 引用；图库删除路径可在权限通过后删除 DB 与磁盘。

### File Center / Knowledge

1. 通用上传经过 general 类型校验。
2. 系统生成文件号，写入 `static/uploads/`。
3. `file_library` 保存元数据及可选 `module_name/source_id`。
4. Knowledge 场景再写文章与文件的关系。
5. 下载读取文件并增加计数；解除 Knowledge 关系不回收共享文件。

## 校验

- **ATT-V01** 文件必须有允许的扩展名，不得属于受阻扩展名集合。
- **ATT-V02** 文件内容不能为空，大小不得超过配置上限。
- **ATT-V03** 文件名必须经过 basename 和安全字符处理。
- **ATT-V04** Knowledge 附件要求文章存在，并通过文章编辑/新增权限。
- **ATT-V05** 品牌上传还校验品牌资源字段和品牌修改权限。
- **ATT-V06** 产品/样品上传缺少一致的模块权限检查；不能仅凭 UI 隐藏按钮视为后端授权。
- **ATT-V07** File Center 下载、删除和平台上传未证明调用已有 `can_upload_file/can_delete_file` helper。
- **ATT-V08** 活跃路径未证明按租户隔离目录和 SQL；多租户部署不能依赖表上存在 tenant 列。
- **ATT-V09** 静态文件读取不复核来源单据、用户角色或租户。

## 数据含义

| 表/字段 | 含义 |
|---|---|
| `products.image_path` | 产品主图相对路径 |
| `product_images` | 产品附加图库 |
| `product_files` | 产品文档元数据；不等于 File Center 文件 |
| `samples.image1/2/3` | 样品三个固定图片槽 |
| `sample_images` | 样品附加图库 |
| `file_library` | 通用文件注册表，可带模块和来源 ID |
| `knowledge_files` | Knowledge 文章到文件库的链接 |
| `file_versions` | 文件版本结构；运行覆盖程度未完全证明 |
| `file_share` | 外部分享结构 |
| `file_download_logs` | 下载审计结构 |
| `message_attachments` | 消息到文件的关系表；上传入口未找到 |
| `receipts.attachment` | 收款记录中的文本附件字段，未证明属于统一文件库 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `Active` | 文件、分类或分享记录的默认有效状态 |
| `Other` | 样品图库默认图片类型 |
| `KNOWLEDGE` | Knowledge 文件分类代码 |
| `DEFER_TO_LEGACY` | 统一附件引擎不接管，回退 Legacy |
| `Permission Denied` | 权限拒绝结果；并非所有上传/读取路径都会触发 |

## 删除与风险

- 删除产品未完整清理 `product_files` 及其物理文件，存在 DB 和磁盘孤儿。
- 样品固定槽清空不删除磁盘；不同扩展名重传可能留下旧文件。
- Knowledge detach 保留共享文件，可能是刻意共享，也需要后续无引用回收策略。
- 双存储根增加备份、迁移和生命周期管理漏项风险。
- 公开静态 URL 与缺少逐文件 RBAC 会绕开来源单据权限。
- 多租户时，未过滤的对象 ID 与静态路径可能造成跨租户关联或读取风险。

## UNKNOWN

- `message_attachments` 的实际上传入口 **UNKNOWN**。已检索 `apps/**`、`v15/communication/**` 和 Legacy DDL。
- `file_uploads` 表及 `/upload_document` 路由 **UNKNOWN/代码中未落地**。已检索 Python 源与 `business_modules/documents.md`。
- 上传后的病毒扫描、MIME 内容识别 **UNKNOWN/未发现**。已检索 `core/security/**`。
- 产品单张图片/单份文档的独立删除 API **UNKNOWN**。已检索 product router 与 residual。
- File Center 上传 UI 的最终入口 **UNKNOWN**；模板中未见上传表单，但平台上传路由存在。
- 文件版本、分享和下载日志是否覆盖所有附件路径 **UNKNOWN**；表存在不等于产品/样品路径接线。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\core\security\uploads.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\security\config.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\security\csrf.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\runtime\tenant_context.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\attachment\`
- `H:\Workspace\EZAM_CRM - 9.0\app.py`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\business_pages.py`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\platform\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\document_center\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\brand_center\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v41_tenant_column_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V41_Tenant_Column_Audit_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\core\Enterprise_Attachment_Model.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\documents.md`
- `H:\Workspace\EZAM_CRM - 9.0\templates\product_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\file_center.html`
