# Brand Center — Legacy Knowledge

**Evidence strength:** Strong for active `brand_profiles` view/edit/upload; Medium for downstream document application; V15.1 registry is additive and disabled by default  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块覆盖品牌主数据、公司身份、Logo/印章/签名/水印资产、主题与文档模板交界。

Legacy 存在两套不能合并理解的 Brand Center：

1. **活动主线**：`brand_profiles` + `/brand_center` + 企业品牌保存/上传服务；
2. **V15.1 并行基础层**：`platform_brand`、`company_profiles`、`brand_assets` registry/API，默认未启用，未取代 Legacy 主线。

平台商标来自固定配置，企业 Logo 来自公司品牌资料。文档引擎可读取活动品牌资料和公司 Logo，但页面文案声称“所有文档自动应用全部品牌元素”的范围强于可验证实现。

---

## 2. 业务规则

| ID | 规则描述 | 例外 / 缺口 |
|----|----------|-------------|
| BR-R1 | `/brand_center` 的活动列表读取 `brand_profiles` | V15.1 `company_profiles` 不主导该页面 |
| BR-R2 | 品牌以唯一 `brand_code` 标识，并区分 brand type | 类型包括 EZAM、UNI-MEMMINGER、CUSTOMER_OEM、DISTRIBUTOR_OEM |
| BR-R3 | 可标记一个默认品牌；保存新的默认项时先清除其他默认标记 | 并发一致性与唯一约束 UNKNOWN |
| BR-R4 | Super Admin、Admin、Company Administrator 或 Administrator 可保存/上传品牌 | 活动路由显式拒绝其他角色 |
| BR-R5 | 文本资料可维护公司名、联系方式、地址、税务、银行、币种、社交账号和强调色 | 字段级格式校验有限 |
| BR-R6 | 可上传 Logo、印章、签名、水印等品牌资产 | 允许字段由映射白名单限定 |
| BR-R7 | 上传文件需经过安全文件名、类型/内容校验；Logo 图片可缩放 | 文件清理和旧版本保留 UNKNOWN |
| BR-R8 | Tenant Logo 修改受 30 日最多两次的锁定策略约束 | 文本字段不受同一锁 |
| BR-R9 | 品牌变更记录 actor、IP、reason、旧值和新值 | 审计存储完整保留期 UNKNOWN |
| BR-R10 | 平台商标路径不能被当作公司 Logo；无合格公司 Logo 时回退默认图 | 平台/企业身份隔离 |
| BR-R11 | 活动品牌解析优先指定的 Active brand，否则默认 Active，再否则首个 Active | 没有活动项时回退默认字典 |
| BR-R12 | 品牌可配置 QR URL 类型：website、product、quotation、portal、tracking、custom | 实际 URL 依赖文档上下文 |
| BR-R13 | 文档模板可按 brand_code 过滤，并维护 Logo/QR/Barcode/Seal/Signature/Watermark/Footer 开关 | 模板设计器写入布局配置 |
| BR-R14 | V15.1 registry 可持久化平台、公司与资产 metadata | 默认 disabled，不等于生产切换 |
| BR-R15 | V15.1 asset 支持九类资产路径 | 报告明确无 V15.1 upload 实现 |
| BR-R16 | V15.1 启动读取会 seed 默认 registry/asset 数据 | Seed 不等于用户批准或业务启用 |
| BR-R17 | `brand_profiles` 与 `company_profiles` 没有可确认的同步/迁移 | 两边可能分叉 |
| BR-R18 | Brand Center 不自动建立 Marketing connector | 社交账号只是品牌 metadata |
| BR-R19 | OEM Ready 与“所有文档自动应用”的页面文案属于能力意图 | 全文档、Email、Login/Header 传播未获完整运行证据 |
| BR-R20 | 文档设计器可直接保存布局与元素开关 | 未复用品牌保存/上传的管理员校验，权限边界不对称 |

---

## 3. 流程

### 3.1 查看与编辑活动品牌

1. 打开 `/brand_center`，按默认标记和 brand_code 展示 `brand_profiles`。
2. 进入指定 brand_code 的编辑页。
3. 加载品牌资料、主题选项、品牌锁状态和最近审计。
4. 管理员提交允许字段。
5. 若设为默认，先清除其他默认标记。
6. 保存变更并记录审计。

### 3.2 上传品牌资产

1. 管理员选择品牌、资产字段和文件。
2. 校验角色、字段白名单、文件类型/内容和安全文件名。
3. Logo 类资产先检查修改频率锁。
4. 文件写入品牌上传目录；适用图片执行缩放。
5. 将 Web 路径写回 `brand_profiles`。
6. 记录资产变更审计。

### 3.3 文档品牌解析

1. 文档选择指定品牌，或解析默认 Active 品牌。
2. 解析公司 Logo，阻止平台商标冒充公司 Logo。
3. 生成 QR URL 时按品牌的 URL 类型读取文档上下文。
4. 文档模板按 brand_code 和 doc_type 选择布局开关。
5. 未找到资料时使用默认公司/平台配置。

### 3.4 V15.1 并行 registry

1. 确保三张 additive 表存在。
2. 从 core registry seed 平台、默认公司和资产 metadata。
3. API 只读返回 health、platform、company、registry、assets。
4. **流程终止**：未切换 Legacy HTML 主线，也无该层 Logo 上传或自动 Header/Login 集成。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| BR-V1 | 保存/上传需活动服务认可的管理员角色或 Super Admin | Hard |
| BR-V2 | brand_code 唯一 | Database-level |
| BR-V3 | 上传字段必须在允许映射中 | Hard |
| BR-V4 | 上传文件需安全文件名和品牌类型校验 | Hard |
| BR-V5 | Tenant Logo 不得超过两次/30日 | Hard when state available |
| BR-V6 | 平台商标不得作为公司 Logo | Hard at resolver |
| BR-V7 | 公司名非空 | Strong in V15.1 schema；Legacy 字段约束较弱 |
| BR-V8 | Email、URL、税号、银行号格式 | UNKNOWN | 已检索活动保存服务和 validators |
| BR-V9 | 只能存在一个默认品牌 | Service behavior only | 无数据库 partial unique 证据 |
| BR-V10 | 删除品牌/资产的规则 | UNKNOWN | 未见活动删除流程 |
| BR-V11 | 品牌生效需审批/发布 | Missing | 保存后直接更新活动资料 |
| BR-V12 | V15.1 registry 写 API 的授权 | Not exposed | 当前 API 只读 |
| BR-V13 | Brand 与文档模板引用完整性 | UNKNOWN | 未见 FK/删除保护 |
| BR-V14 | 文档设计器保存需品牌管理员权限 | Missing in observed handler |

---

## 5. 数据含义

| Entity | 含义 |
|--------|------|
| `brand_profiles` | 活动 Legacy 公司/OEM 品牌主数据；当前 HTML 主线权威 |
| `document_template_designs` | 按品牌和文档类型保存布局及元素开关 |
| `platform_brand` | V15.1 平台品牌并行表；默认未启用 |
| `company_profiles` | V15.1 公司品牌并行表，不等于 Legacy `brand_profiles` |
| `brand_assets` | V15.1 资产路径 metadata |
| `brand_state.json` | Legacy Logo 修改次数与锁状态 |
| `brand_theme.json` | Legacy 主题设置 |
| `brand_audit.json` | Legacy 品牌变更审计 |
| `config/branding.py` | 固定平台身份、版本、商标和颜色配置 |
| `logo_path` | 公司 Logo 路径，不应指向平台商标 |
| `seal_path` / `signature_path` / `watermark_path` | 文档视觉资产路径 |
| `is_default` | Legacy 默认公司/OEM 品牌选择 |
| `status` | 是否允许被活动品牌解析器选中 |

V15.1 支持的资产类型为 Platform Logo、Company Logo、Dark Logo、Light Logo、Print Logo、Favicon、Login Background、Watermark、Email Logo；支持类型不证明每种资产已经传播到对应表面。

---

## 6. 状态词汇

| Status | 使用位置 | 含义 |
|--------|----------|------|
| `Active` | Legacy `brand_profiles` | 可被活动解析器选择 |
| `active` | V15.1 三表 | 默认 metadata 状态 |
| `editable` | Brand lock | 当前允许 Logo 修改 |
| `locked` / lock notification | Brand lock | 达到修改频率限制 |
| `enabled_by_default=False` | V15.1 layer | 并行层默认不接管生产 |
| `fixed` | Software brand panel | 平台商标固定，不是公司可编辑资产 |

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `apps/brand_center/v14_residual.py` | 活动页面、保存、上传和文档模板流程 |
| `templates/brand_center.html` | 品牌列表、OEM 与文档传播文案 |
| `templates/brand/enterprise_brand_edit.html` | 编辑字段、主题、资产和锁状态 |
| `runtime/v14/legacy_support.py` | `brand_profiles` / template DDL 与活动品牌解析 |
| `v15/enterprise_branding/service.py` | 权限、保存、上传、审计和 Logo lock |
| `v15/enterprise_branding/theme_store.py` / `audit.py` | JSON 主题与审计存储 |
| `config/ui_framework_v11.py` | Logo 修改锁状态存储 |
| `document/platform_brand.py` | 平台/公司 Logo 隔离和回退 |
| `document/nde_engine.py` | 文档上下文与品牌交界 |
| `config/branding.py` | 固定平台商标与身份 |
| `apps/brand_center/services.py` / `repository.py` | V15.1 seed 和并行持久化 |
| `apps/brand_center/routes.py` | V15.1 只读 API |
| `database/v151_brand_center_schema.py` | additive 三表语义 |
| `docs/reports/V151_Volume002A_Brand_Center_Report.md` | 默认未启用与已知限制 |
| `apps/brand_center/` / `v15/enterprise_branding/` / `document/` | UNKNOWN 检索范围 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
