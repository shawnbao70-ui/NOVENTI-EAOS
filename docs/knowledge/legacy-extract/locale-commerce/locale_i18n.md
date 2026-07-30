# 语言、地区与本地化（Locale / i18n）— Legacy Knowledge

**Evidence strength:** Strong for locale infrastructure; mixed for application-wide coverage  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 同时存在 V14 `i18n/` 与 V15 `core/i18n/` 两套相邻机制，并有 `/locales/` 目录中的多层词典：

- **强证据**：locale 规范化、请求解析、session 切换、英文回退、RTL 标记、日期/数字/币种显示工具。
- **中等证据**：模板 helper、报价模板语言/币种筛选、多语言打印元数据。
- **缺口证据**：审计显示大量硬编码字符串、翻译键缺失、部分模板无默认回退、非英语业务词典回退英文。
- **业务边界**：本地化改变标签和格式，不应改变持久化状态、金额、权限、税码或业务关系。

V15 声明 16 个 supported locales；V14 `language_settings` 默认只登记 5 种，`print_languages` 也只预置 5 种。支持清单、设置清单、实际词典完整度并不等价。

---

## 2. 业务规则

| ID | 规则描述 | 证据 / 缺口 |
|----|----------|-------------|
| LOC-R1 | Locale 接受 BCP-47 风格与别名，`_` 会规范为 `-` | 未识别值回退英文，可能掩盖配置错误 |
| LOC-R2 | V15 请求优先级为 query `lang` → 用户/session → 公司 → 浏览器 → English | 另一 V14 manager 另有 explicit/query/user/company/default 入口 |
| LOC-R3 | 语言切换同时更新 session 的 locale、user_locale、语言显示名和 preferred_language | `persist_user` 名称存在，但当前实现只见 session 写入，未证实数据库持久化 |
| LOC-R4 | `/locale/switch/{code}` 与 `/i18n/switch/{code}` 切换后重定向 | `next` 仅接受以 `/` 开头的路径 |
| LOC-R5 | 阿拉伯语标记为 RTL，其余已声明语言为 LTR | CSS/模板是否在所有页面完整遵守 RTL 未证实 |
| LOC-R6 | locale 控制 UI 文本、日期和数字格式；country 是币种、税务、地址、纸张等独立维度 | 不能仅由语言推断交易国家 |
| LOC-R7 | V15 locale loader 先加载英文，再叠加目标语言的 legacy、regional、structured 和 business 词典 | 多个 overlay 的后加载值覆盖前值 |
| LOC-R8 | 非中英文 business terminology 当前映射到英文词典 | 页面壳可翻译，不等于业务术语已本地化 |
| LOC-R9 | 缺失普通键可 humanize；缺失 `ui.*` 键返回空串以便模板 default 生效 | 没有 `default` 的调用可能显示空白 |
| LOC-R10 | V14 引擎按 common/menu/document/db namespace 加载，并对缺失目标语言键回退英文 | 若目标 locale 完全无文件，也整体回退英文 |
| LOC-R11 | 翻译插值只替换已提供的命名占位符；未知占位符保留 | 未见复杂复数/性别规则 |
| LOC-R12 | `ngettext` 仅按 count 是否为 1 选择单/复数键 | 不满足多种语言的复杂复数规则 |
| LOC-R13 | 日期 formatter 对可解析日期应用 locale 格式；非法值原样返回 | 不做时区转换 |
| LOC-R14 | 数字 formatter 只为少数 locale 定义分隔符，其余使用默认英文标点 | 声明支持不等于数字格式完整 |
| LOC-R15 | 币种 formatter 本地化符号/代码位置，不执行汇率换算 | 国家参数当前没有可观察到的额外分支 |
| LOC-R16 | 报价模板以 language 与 currency 共同筛选活动模板 | 语言值有 `English` 与 locale code 两种词汇，可能匹配失败 |
| LOC-R17 | 业务状态应保存 canonical value，模板只翻译显示标签 | Legacy 中仍有中英文/显示名/代码混用风险 |
| LOC-R18 | 语言切换不得改变业务逻辑、数据库关系或权限 | switcher 明示此边界，但全系统硬编码分支未完全审计 |

---

## 3. 流程

### 3.1 请求 locale 解析

1. 从 query、session 用户偏好、公司语言和浏览器语言中按优先级选择候选。
2. 将别名与区域写法规范为支持的 locale。
3. 不支持或空值回退英文。
4. 生成 locale、来源、RTL、日期格式和数字分隔符上下文。
5. 模板通过 `_`、`t`、formatter 与 switcher context 展示本地化内容。

### 3.2 语言切换

1. 用户访问 locale switch 路由。
2. 系统规范化 locale 并更新 session。
3. 系统回到受限的站内 `next` 路径。
4. 后续请求重新构建模板本地化上下文。
5. 未证实用户偏好被写入持久化用户主数据。

### 3.3 翻译查找与回退

1. 先加载英文基线。
2. 按目标 locale 叠加 legacy flat、regional、structured 与 business 文件。
3. translator 按原键、`ui.` 前缀和部分 snake-case 变体查找。
4. 缺失 UI 键返回空串，依赖模板 `default`；普通键可转为可读英文尾词。
5. placeholder label 或禁用品牌词会退回 default/原消息。

### 3.4 表单与状态

1. 表单标签、按钮、表头可翻译。
2. 选项的提交值通常仍是 `Draft`、`Sent`、`Pending`、`Active` 等英文 canonical value。
3. 模板比较 canonical value 后显示翻译标签。
4. 若数据库保存了翻译后的值或另一套显示名，筛选、统计和状态徽标可能失效。

### 3.5 UNKNOWN

- 用户语言偏好是否写入 users/profile 表并跨设备保留：**UNKNOWN**。检索 `preferred_language` 的数据库更新与登录读取。
- 公司默认语言的权威来源：**UNKNOWN**。检索 `company_locale/company_language` session 注入与 `DEFAULT_LANGUAGE` 设置消费方。
- 所有状态字段是否已限定 canonical 英文值：**UNKNOWN**。检索各表状态 distinct values、中文状态写入及翻译后值写入。
- 时区、夏令时和时间戳展示是否统一：**UNKNOWN**。检索 timezone 设置的消费路径和 datetime formatter。
- 打印语言元数据是否真实驱动字体、纸张、日期和币种格式：**UNKNOWN**。检索 `print_languages` 消费方及文档渲染链。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| LOC-V1 | Locale 必须规范为支持清单值 | Soft | 未识别值静默回退英文，而非拒绝 |
| LOC-V2 | 翻译 JSON 必须为有效 UTF-8/JSON | Loader soft-fail | 审计样本通过 UTF-8，但读取错误会退为空 |
| LOC-V3 | 模板翻译调用应提供 default | Incomplete | 健康报告仍发现大量无 `default` 调用 |
| LOC-V4 | 翻译键必须存在 | Incomplete | 报告仍有缺失键和 namespace 缺口 |
| LOC-V5 | Locale 文件不得有重复键 | Incomplete | 报告发现至少一个重复键 |
| LOC-V6 | 状态提交值不得使用翻译标签 | Convention only | 未见全局枚举/数据库约束 |
| LOC-V7 | 查询和统计应基于 canonical status | Mixed | 模板多比较英文值，但历史数据一致性未证实 |
| LOC-V8 | RTL 页面布局完整 | Partial | 有 RTL 标记/CSS，缺少全页面证据 |
| LOC-V9 | 数字与日期解析不能依赖显示格式 | Not evidenced | formatter 主要做输出 |
| LOC-V10 | 时区统一应用 | Missing / partial | 审计明确指出不统一 |
| LOC-V11 | `next` 重定向限制站内路径 | Present | 只接受以 `/` 开头，否则回首页 |
| LOC-V12 | 语言与国家不能互相替代 | Explicit intent | country localization 明示二者独立 |

---

## 5. 数据含义

| Concept / Field | Legacy 含义 |
|-----------------|-------------|
| `locale` / `user_locale` | 规范化后的 UI 语言候选，保存在 session |
| `language`（session） | 语言原生显示名；与 locale code 不是同一语义 |
| `preferred_language` | switcher 写入 session 的偏好键；数据库持久化未证实 |
| `company_locale/company_language` | 请求解析中的公司默认候选；权威来源未确认 |
| `language_settings` | V14 活动语言登记表，不代表翻译完整度 |
| `print_languages` | 打印字体、日期、币种格式和纸张元数据 |
| `quote_templates.language` | 模板筛选值；可能是显示名而非 locale code |
| `country` | 商业/法域维度，不等于 UI 语言 |
| translation key | 稳定显示键；不应作为业务状态值 |
| translated label | 用户可见文本；不可作为权限、状态或关联键 |
| `RTL` | 文本/布局方向属性，不改变业务事实 |
| date/number/currency formatter | 展示层转换，底层值应保持规范格式 |

---

## 6. 状态词汇

| Value / family | Meaning / localization caveat |
|----------------|-------------------------------|
| `en`, `zh-CN`, `zh-TW`, `id`, `vi`, `th`, `ja`, `ko`, `hi`, `bn`, `ar`, `es`, `pt`, `ru`, `fr`, `de` | V15 声明的 locale codes；各语言内容完整度不一致 |
| `en_US`, `zh_CN` 等 | 文件 stem/session 历史写法；需要规范化后比较 |
| `English`, `Chinese`, `Indonesian` 等 | 显示名或 V14 配置值，不应与 locale code 混作键 |
| `rtl` / `ltr` | 页面方向 |
| `explicit`, `query`, `user`, `company`, `browser`, `default` | locale 决策来源词汇 |
| `Active` | 语言、打印语言或模板处于活动配置状态 |
| `Draft`, `Sent`, `Negotiating`, `Won`, `Lost` | 报价 canonical 状态；翻译只应用于显示 |
| `Pending`, `Completed` | 常见流程状态；不同模块未必共享同一状态机 |
| 中文状态词 / 本地化标签 | 若被持久化为业务值，会与英文比较、统计和路由产生不一致 |

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `core/i18n/language_manager.py` | 支持语言、别名、RTL、日期和数字格式 |
| `core/i18n/language_detector.py` | 请求 locale 优先级与来源 |
| `core/i18n/language_switcher.py` | session 切换、模板 context 与 formatter |
| `core/i18n/locale_loader.py` | 英文基线及多层词典叠加 |
| `core/i18n/translator.py` | 查找、缺失键、default、插值及复数边界 |
| `core/i18n/formatter.py` | 日期、数字、币种展示 |
| `core/i18n/country_localization.py` | 语言与国家维度分离 |
| `i18n/locale_manager.py` | V14 locale 决策模型 |
| `i18n/translation_engine.py` | V14 namespace 与英文回退 |
| `apps/platform/v15_platform_pages.py` | 活动语言切换路由 |
| `core/runtime/session_integration.py` | 登录后 session locale 绑定 |
| `runtime/v14/legacy_support.py` | 语言设置、打印语言和模板 language/currency 数据 |
| `templates/quotes.html` | canonical 报价状态值与翻译显示的交界 |
| `docs/reports/V15_I18N_HEALTH_REPORT.md` | 缺失键、无 default 调用、重复键等实测缺口 |
| `docs/reports/audit/07_I18N_AUDIT.md` | 硬编码、覆盖率、时区与地区逻辑审计 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
