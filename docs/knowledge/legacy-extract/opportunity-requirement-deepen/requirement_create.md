# 需求创建、商机 1:N 与 requirement_count

## Scope与证据强度

本页聚焦 `business_requirements` 的两个人工创建入口：Requirement Center 独立创建，以及 Opportunity Detail 继承商机/客户创建。插入、编号、默认值和计数递增为强证据；计数修复、删除回减、并发一致性和父子客户一致性证据缺失。

## 业务规则（稳定ID）

1. **RC-R01** 需求主表是 `business_requirements`，一条需求最多直接引用一个 `opportunity_id`。
2. **RC-R02** 一个商机可被多条需求引用，形成 Opportunity 1:N Requirement。
3. **RC-R03** 独立入口 `POST /business/requirements/create` 与从商机详情提交使用同一路由。
4. **RC-R04** HTTP 创建要求 title；repository 对非 HTTP 调用以 `Untitled Requirement` 回退。
5. **RC-R05** 未提交编号时生成 `REQ-YYYYMMDD-NNNN`，NNNN 是全需求表 `COUNT(*) + 1`。
6. **RC-R06** 独立 quick-create 可不填商机；`opportunity_id=0` 转成 NULL。
7. **RC-R07** 从商机详情创建时以 hidden 字段携带 opportunity.id 与 opportunity.customer_id。
8. **RC-R08** 系统不从 opportunity_id 服务端重新读取客户；客户端提交的 customer_id 被直接采用。
9. **RC-R09** 来源默认 `manual_entry`，需求类型默认 `general_product_inquiry`，状态默认 `new`。
10. **RC-R10** salesperson 取 session username，priority 默认 normal，AI 分析状态默认 pending。
11. **RC-R11** 新需求的 sample_id、quote_id、sales_order_id 默认空。
12. **RC-R12** 若 `opportunity_id` 为真，插入后对父商机 `requirement_count = COALESCE(count,0)+1`。
13. **RC-R13** 需求插入和父计数更新在同一 repository 方法末尾提交，但没有显式 BEGIN/ROLLBACK。
14. **RC-R14** 若 opportunity_id 不存在，schema 外键声明是否阻止插入取决于 SQLite foreign_keys 运行配置；父计数 UPDATE 可影响 0 行。
15. **RC-R15** 未见需求删除路由，因此也未见 `requirement_count` 回减或重算。
16. **RC-R16** 商机详情展示真实查询出的关联需求列表长度；中心显示缓存 `requirement_count`，两者可能不一致。
17. **RC-R17** Requirement Center 创建要求 Quotes.add，查看要求 Quotes.view；从商机页面发起仍落到 Quotes.add。
18. **RC-R18** 路由暴露完整来源/类型常量；Opportunity Detail 的简化表单只给四种 requirement_type，source 使用路由默认。
19. **RC-R19** status 在创建后不会因仅有描述或来源而自动进入 analyzing。
20. **RC-R20** schema repair 只以 `business_opportunities` 是否存在决定是否执行整套 DDL；若商机表存在而需求表缺失，constructor 不会主动补建需求表。
21. **RC-R21** 创建只写 `new`；后续人工触发产品匹配成功时，若当前状态不在 matched/quoted/closed/cancelled，可自动推进到 `matched`，但不会反向改变商机状态。

## 流程

### 从 Requirement Center

1. 以 Quotes.view 打开中心。
2. 填标题、可选客户 ID、来源、类型和描述。
3. 以 Quotes.add 提交；不带商机。
4. 生成 REQ 编号并插入 new/pending 需求。
5. 303 重定向 Requirement360。

### 从 Opportunity Detail

1. 以 Customers.view 打开商机详情。
2. 表单 hidden 继承商机 id 与当前 customer_id。
3. 用户填标题、四选一类型和描述。
4. 提交仍要求 Quotes.add。
5. 插入需求后父商机缓存计数 +1，统一提交。
6. 返回 Requirement360；商机详情下次查询会列出该子需求。

## 校验（强/弱/缺失）

1. **RC-V01（强/HTTP）** title 为必填 Form，模板有 required。
2. **RC-V02（弱/UI）** customer_id 数字且 min=0；服务端只做 int 转换。
3. **RC-V03（缺失）** 未验证 customer_id 存在、Active 或可见。
4. **RC-V04（缺失）** 未验证 opportunity_id 存在。
5. **RC-V05（缺失）** 未验证 requirement.customer_id 与 opportunity.customer_id 一致。
6. **RC-V06（弱/UI）** Center 的来源和类型来自常量下拉。
7. **RC-V07（缺失）** 服务端不检查来源/类型是否属于常量。
8. **RC-V08（强/DB）** requirement_code 有唯一约束。
9. **RC-V09（缺失）** COUNT+1 编号没有并发锁、重试或删除后碰撞处理。
10. **RC-V10（强/权限）** 创建受 Quotes.add，查看受 Quotes.view。
11. **RC-V11（缺失）** 插入与计数无显式事务开始/异常回滚；原子性依赖连接默认事务行为。
12. **RC-V12（缺失）** 未见缓存计数与实时子记录数校验/修复。
13. **RC-V13（缺失）** 未见标题长度、纯空白、描述长度校验。
14. **RC-V14（缺失）** 未见同客户/同商机重复需求检测。
15. **RC-V15（弱/能力探针）** 页面在需求表缺失时可显示空列表，但创建不会在“仅缺需求表”的不一致 schema 上完成修复。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `business_requirements.id` | 需求内部主键 |
| `requirement_code` | REQ 日期+全表序号，人读唯一编号 |
| `opportunity_id` | 可空父商机；形成 1:N |
| `customer_id` | 可空需求客户；不由服务端从父商机强制派生 |
| `title` | 需求标题，HTTP 创建必填 |
| `description` | 自由文本需求描述 |
| `source_type` | 需求进入渠道，默认 manual_entry |
| `requirement_type` | 需求形态，默认 general_product_inquiry |
| `status` | 创建默认 new |
| `salesperson` | 创建 session username 快照 |
| `priority` | 默认 normal |
| `sample_id` | 单值样品快捷指针，创建时空 |
| `quote_id` | 单值报价快捷指针，创建时空 |
| `sales_order_id` | 单值订单快捷指针，创建时空 |
| `ai_analysis_status` | AI 分析进度，默认 pending |
| `requirement_count` | 商机头上的派生缓存，创建关联需求时 +1 |
| `created_at/updated_at` | UTC 字符串时间；父商机 updated_at 随计数更新 |
| `manual_entry` | 独立人工创建默认来源 |
| `new` | 需求初始状态 |
| `pending` | AI 分析初始状态，不是需求业务状态 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| new | 新需求默认状态 |
| pending | ai_analysis_status 默认值 |
| normal | 默认优先级 |
| linked | opportunity_id 非空的关系语义，不是持久状态 |
| standalone | opportunity_id 为空的需求，不是持久状态 |
| requirement_count | 缓存数量，不是状态 |
| analyzing | 常量中的后续需求状态；创建不会自动进入 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| RC-E01 | 创建路由字段、默认、权限和跳转 | 强 | `v15/business_lifecycle/routes.py` |
| RC-E02 | REQ 编号、插入、父计数 +1 和 commit | 强 | `v15/business_lifecycle/repository.py` |
| RC-E03 | 需求表字段、父商机 FK 和索引 | 强 | `database/business_lifecycle_schema.py` |
| RC-E04 | Center 独立创建不暴露 opportunity_id | 强 | `templates/business/requirement_center.html` |
| RC-E05 | Opportunity Detail hidden 继承商机/客户 | 强 | `templates/business/opportunity_detail.html` |
| RC-E06 | 商机中心显示缓存 requirement_count | 强 | `templates/business/opportunity_center.html` |
| RC-E07 | 商机详情显示实时 list_requirements 结果长度 | 强 | `v15/business_lifecycle/routes.py`、`templates/business/opportunity_detail.html` |
| RC-E08 | 来源、类型、状态词汇由 constants 声明 | 强（声明） | `v15/business_lifecycle/constants.py` |
| RC-E09 | Requirement360 建立创建后聚合视图 | 强 | `v15/business_lifecycle/requirement360.py` |
| RC-E10 | 既有商机页确认商机→需求是主要子流程 | 强（交叉） | `docs/knowledge/legacy-extract/crm/opportunity.md` |
| RC-E11 | repair gate 只检查商机表；架构报告当时未找到目标数据库 | 强/报告限制 | `database/business_lifecycle_schema.py`、`docs/reports/V15_BUSINESS_ARCHITECTURE_REPORT.md` |
| RC-E12 | 产品匹配是已找到的需求后续自动状态写入口 | 强 | `v15/business_lifecycle/product_matching.py` |

## UNKNOWN + 已查路径

1. **SQLite 生产连接是否始终启用 foreign_keys UNKNOWN。** 已查路径：business lifecycle schema、数据库连接/bootstrap 与报告。
2. **父商机不存在时创建需求会失败还是留下孤儿 UNKNOWN。** 已查路径：route、repository、schema；依赖 foreign_keys 运行设置。
3. **需求插入成功而父计数更新失败时是否自动回滚 UNKNOWN。** 已查路径：repository commit、连接事务配置、异常处理。
4. **历史删除/导入是否已造成 requirement_count 漂移 UNKNOWN。** 已查路径：需求 CRUD/删除、导入、计数修复脚本与报告。
5. **需求应否强制绑定客户或商机 UNKNOWN。** 已查路径：两个创建模板、routes、schema、business_modules。
6. **父商机与需求客户不一致是否是允许的转交场景 UNKNOWN。** 已查路径：hidden 字段、repository、Requirement360 和报告。
7. **REQ 编号删除后碰撞的实际处理 UNKNOWN。** 已查路径：next_code、唯一约束、异常处理。
8. **需求来源/类型是否允许租户自定义 UNKNOWN。** 已查路径：constants、schema、settings、templates。
9. **requirement_count 是否有离线重算作业 UNKNOWN。** 已查路径：v15 lifecycle、apps/customer、business_modules、docs/reports。
10. **需求独立创建后能否补绑商机 UNKNOWN。** 已查路径：routes、repository、Requirement360 和 templates。
11. **部分迁移环境中“商机表存在、需求表缺失”是否实际发生 UNKNOWN。** 已查路径：schema repair、Patch022/启动初始化与 readiness/architecture reports。
12. **除 matched 外的需求状态由谁推进 UNKNOWN。** 已查路径：constants、routes、repository、product_matching、sample/quotation workflow。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\`
- `H:\Workspace\EZAM_CRM - 9.0\database\business_lifecycle_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\requirement_center.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\opportunity_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\requirement360.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
