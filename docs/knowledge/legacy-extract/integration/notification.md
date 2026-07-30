# 通知中心（Notification Center）— Legacy Knowledge

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Honesty summary:** V14 站内通知可运行；V15.1 是默认关闭的元数据层；HX/Smart 是演示或内存层

---

## 1. Scope 与证据强度

| 范围 | 结论 | 强度 |
|------|------|------|
| V14 `notifications` 页面与表 | 列表、详情、已读、删除、手工创建可运行 | Strong |
| V15.1 Notification Center | 模块、渠道、模板、规则、队列和历史元数据 | Medium/Scaffold |
| Human Experience 通知抽屉 | 使用 JSON 数据，包含演示种子 | Weak/Demo |
| Email / WhatsApp / SMS | 有名称、设置或日志，但未观察到真实网关发送 | Strong negative evidence |
| 业务单据自动触发 | 除文档消息桥外，未观察到报价/订单/库存/审批自动接线 | Strong negative evidence |

三套实现并行，不能把通知中心页面、渠道注册或队列状态等同于消息已真实外发。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外/缺口 |
|----|----------|----------|-----------|
| N-R1 | V14 通知表是当前站内收件箱权威 | List/Create/Read | V15.1 服务明确 defer legacy |
| N-R2 | 通知按 `target_user` 过滤，未读以 `status=Unread` 统计 | User inbox | 租户过滤是否一致为 UNKNOWN |
| N-R3 | 打开通知详情会自动标记已读并记录读取时间 | Detail | |
| N-R4 | 手动发送通知只允许 Admin/Manager；删除仅 Admin | Manual actions | 部分 API/演示层权限不同 |
| N-R5 | 新通知生成 NTF 编号，默认未读和 Normal 优先级 | Create | Legacy 存在重复创建函数定义 |
| N-R6 | V15.1 Notification Center 默认关闭，不替换 V14 | Bootstrap | |
| N-R7 | V15.1 渠道均登记为未实现；规则、订阅和队列为 metadata-only | Seed | 不得据此宣称可发送 |
| N-R8 | Email/WhatsApp 发送函数只写 Waiting 日志并返回，不调用外部提供商 | Channel action | |
| N-R9 | 队列处理把 Waiting 改为 Completed，但未观察到渠道发送 | Queue worker | Completed 不等于 Delivered |
| N-R10 | Browser 通知实际是写入站内通知表 | Browser action | 不是浏览器 Push 网关 |
| N-R11 | HX 铃铛读取 JSON 通知，不读取 V14 收件箱 | Header drawer | 首次访问可生成演示数据 |
| N-R12 | 消息中心 `messages` 与通知表是独立子系统 | Messaging | 无自动双写 |
| N-R13 | 文档中心发送动作可通过轻量桥写站内通知 | Document action | 是少数确认的跨模块触发 |
| N-R14 | 报价、订单、库存、审批、财务通知主要存在于模板、规则或演示种子 | Business events | 未观察到业务保存钩子 |
| N-R15 | Enterprise Notification Engine 当前固定把发送决策交还 Legacy | Engine call | |

---

## 3. 流程

### 3.1 V14 站内通知

手工/测试/文档消息桥 → 写 `notifications` 为 Unread → 用户列表/未读数 → 打开详情或显式标记 → Read → Admin 可删除。

### 3.2 外发渠道

请求 Email 或 WhatsApp → 写 `notification_logs` 为 Waiting → 返回成功样式结果。未观察到 SMTP、WhatsApp API、SMS 网关或可靠投递回执。

### 3.3 V15.1 元数据初始化

首次服务调用 → seed 通知模块、渠道、模板、订阅、规则、队列和历史元数据。此流程建立目录，不发送业务通知。

### 3.4 HX 抽屉

前端调用 Human Experience API → 读写本地 JSON → 展示未读、置顶、归档。该状态不与 V14 SQL 收件箱自动同步。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| N-V1 | V15.1 module/channel/template key 属于注册集合 | Medium | 只保护元数据层 |
| N-V2 | 手工通知 title/content/target_user 必填 | Hard | FastAPI 表单 |
| N-V3 | 手工发送角色限制 | Hard | Admin/Manager |
| N-V4 | 删除角色限制 | Hard | Admin |
| N-V5 | history limit 为 1–200 | Hard | API 参数约束 |
| N-V6 | priority 必须属于枚举 | Absent | V14 可保存任意字符串 |
| N-V7 | 渠道设置和用户偏好在发送前被执行 | Absent/Unknown | 未观察到消费逻辑 |
| N-V8 | 业务单据事件自动触发通知 | Absent | 模板/规则不等于接线 |
| N-V9 | 外发成功必须有提供商回执 | Absent | Waiting/Completed 可能只是本地状态 |
| N-V10 | 通知租户隔离 | Weak/Unknown | 有租户列迁移声明，查询是否全量过滤未确认 |
| N-V11 | V14/V15.1 同名表 schema 兼容 | Weak | repository 通过列检测跳过不兼容 seed |

---

## 5. 数据含义

### 5.1 V14 运行表

| Entity | Meaning |
|--------|---------|
| `notifications` | 用户站内通知、来源、优先级和读取状态 |
| `notification_logs` | 渠道尝试日志，不证明外发完成 |
| `notification_templates` | 登录、报价、订单、付款等模板 |
| `notification_settings` | 系统、邮件、WhatsApp、Browser 开关 |
| `notification_queue` | 本地待处理条目 |
| `messages` | 独立站内消息 |
| `user_settings` 通知字段 | 用户偏好；是否接入发送为 UNKNOWN |

`source_module` / `source_no` 可表达业务单据来源，但实际自动写入很少。

### 5.2 V15.1 元数据

模块、渠道、模板类型、订阅、规则、队列目录和事件历史是“能力目录”，不是投递事实。渠道包括站内、Email、SMS、WhatsApp、Push、Webhook 等，但默认均未实现。

### 5.3 HX JSON

保存分类、标题、正文、已读、归档、置顶和时间。它是体验层数据，不是 SQL 通知权威。

---

## 6. 状态词汇

| Value / family | Meaning | Layer |
|----------------|---------|-------|
| Unread / Read | 站内通知未读/已读 | V14 |
| Normal | 默认优先级 | V14 |
| Waiting / Retry / Success / Failed | 渠道日志状态 | V14；Success 来源稀少 |
| Waiting / Completed | 队列本地状态 | V14；不等于发送成功 |
| metadata_only | 未实现的规则/订阅/队列 | V15.1 |
| active / completed | 注册和历史元数据状态 | V15.1 |
| draft / queued / sent / failed / cancelled | Enterprise Engine 模型词汇 | 未接运行主链 |
| approval / sales / warehouse / logistics / ai 等 | HX 分类 | Demo/UX |

---

## 7. UNKNOWN 与核查范围

| UNKNOWN | 已核查路径/范围 |
|---------|-----------------|
| 报价、SO、PO、DO、库存和 Approval 是否自动触发通知 | `apps/**`、`v15/**` 全库检索通知创建调用；未发现稳定业务钩子 |
| `auto_notify` 设置是否被执行 | Approval 设置 seed 与全库 `auto_notify` 消费检索；未发现 |
| Email/SMS/WhatsApp 真实发送提供商 | `apps/notification_center/**`、`core/integration/**`、provider registry；均无已实现网关 |
| 用户通知偏好是否影响发送 | `user_settings` DDL 与全库字段引用；未发现发送前判断 |
| 队列是否有生产调度器调用 | notification queue、scheduler 注册检索；未确认运行任务 |
| V14 重复 `create_notification` 最终生效签名 | `runtime/v14/legacy_support.py` 两处定义；需运行时加载顺序 |
| V14/V15.1 同名表在实际数据库的 schema | 静态 DDL 与 repository 列检测；未连接运行数据库 |
| 通知查询租户条件 | V41 列迁移与各查询路径；未确认所有入口一致过滤 |

---

## 8. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/notification_center/v14_residual.py` | V14 页面、手工通知、已读与删除 | Strong |
| `runtime/v14/legacy_support.py` | V14 通知表、函数、设置和渠道桩 | Strong |
| `apps/notification_center/services.py` / `repository.py` | V15.1 seed 与 Legacy 权威声明 | Strong |
| `apps/notification_center/routes.py` | V15.1 API | Strong |
| `core/notification/` | 元数据注册和 defer engine | Medium |
| `database/v151_notification_center_schema.py` | V15.1 表结构 | Strong static |
| `v15/communication/notifications.py` | 站内通知轻量桥 | Strong |
| `v15/human_experience/notifications.py` | JSON 抽屉与演示种子 | Strong for demo boundary |
| `v15/notifications/smart_notification.py` | Smart 内存模型 | Medium |
| `templates/notification_center.html` | V14 列表 UI | Medium |
| `templates/notifications.html` / `notification_dashboard.html` | 占位中心 UI | Weak |
| `core/ui/header/notifications.html` | Header 铃铛容器 | Medium |
| `docs/reports/V151_Volume009_Notification_Center_Report.md` | V15.1 additive/legacy 不变 | Strong historical |
| `docs/core/Enterprise_Notification_Model.md` | Engine 叠加边界 | Medium |
| `docs/reports/SMART_NOTIFICATION.md` | Smart 路线图 | Intent |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
