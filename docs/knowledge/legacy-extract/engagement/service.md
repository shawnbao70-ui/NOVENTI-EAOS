# Service / After-sales — Legacy Knowledge

**Evidence strength:** Weak — planned service scaffold and TechnicalService360 shadow exist; active after-sales transaction lifecycle is not confirmed  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块覆盖 `apps/service` 及 `core/object360/technical_service` 所表达的售后/技术服务意图。

可确认内容：

- Service app README 明示为 Program 7 planned；
- API scaffold 提供 health、records、workspace；
- repository 假定主表为 `tickets`；
- TechnicalService360 可把已有 case/ticket/record 转为只读 shadow 视图，声明安装、维护、维修、检查、拜访、知识、文档、AI 和 Dashboard 分区；
- Service Report 是 NDE 支持的文档类型。

未确认内容：

- `tickets` 的活动 DDL、创建/编辑/指派/关闭入口；
- SLA、优先级、保修、备件、工时、现场服务、升级、客户签收、费用与退换货闭环；
- Service Report 的活动业务数据生成流程。

因此不能把 Object360 的结构化展示当成售后系统已经运行。

---

## 2. 业务规则

| ID | 规则描述 | 证据 / 缺口 |
|----|----------|-------------|
| SRV-R1 | Service app 的目标是客户服务工作区：ticket、SLA、AI-assisted response | README 标为 planned |
| SRV-R2 | Canonical repository 把 `tickets` 视为主表 | 在 V14 主 DDL 中未发现该表 |
| SRV-R3 | Records API 最多返回指定 limit 的原始 ticket 行及总数 | 只有只读列表 |
| SRV-R4 | Workspace API 只返回 metadata 和迁移说明 | 不提供业务动作 |
| SRV-R5 | Service detail context 尝试按 case_id 从最多 500 行寻找记录 | 未找到时会退回第一条记录，存在错配风险 |
| SRV-R6 | TechnicalService360 可接受 `technical_service`、`case`、`ticket` 或 `record` 作为输入别名 | 兼容层，不是来源系统 |
| SRV-R7 | 技术服务对象语义字段为 id、case_no、case_title、customer_id、status、service_type、remark | 属于 object adapter |
| SRV-R8 | 生命周期 current stage 直接取对象 status 的小写值 | 不执行状态转换 |
| SRV-R9 | Shadow 生命周期至少生成 `registered`；存在关联记录时增加 `linked` | 展示事件，不是审计事实 |
| SRV-R10 | 关系视图可从 items、purchases、products、samples、suppliers、related 生成 association | 依赖调用方预先提供上下文，不主动查询真实关系 |
| SRV-R11 | TechnicalService360 AI 只生成固定格式摘要和通用建议，且标记 shadow/no gateway invoke | 不得视为诊断结论 |
| SRV-R12 | Service Report 被列入可打印文档类型 | 模板仅继承通用 NDE，活动出单入口 UNKNOWN |
| SRV-R13 | 安装、维护、维修、检查、客户拜访是架构 section | 未发现对应活动子表或写流程 |
| SRV-R14 | 客户、产品、采购、样品、供应商是预期业务交界 | 来源关联、责任归属与一致性 UNKNOWN |
| SRV-R15 | 售后不得因 AI 建议自动修改 ticket、保修、库存或财务事实 | 人工责任硬边界 |

---

## 3. 流程

### 3.1 可观察的只读 API 流程

1. 调用 Service health，返回表名和记录数。
2. 调用 records，尝试从 `tickets` 读取有限条记录。
3. 调用 workspace，返回 planned workspace metadata。
4. 未观察到从这些 API 创建或推进服务单。

### 3.2 TechnicalService360 shadow 流程

1. 调用方提供已有 service/case/ticket/record。
2. 兼容层规范化基本字段和对象引用。
3. 以现有 status 生成只读 lifecycle stage。
4. 从调用上下文中已有的关联列表生成关系边。
5. 生成固定摘要、通用建议、知识/search/dashboard 视图。
6. 把 shadow bundle 附加到页面 context。
7. 不写回服务事实，不调用推理网关。

### 3.3 缺失的售后闭环

未观察到以下活动流程：

1. 客户/销售订单/交付创建服务请求；
2. 分类、优先级和 SLA 计算；
3. 指派工程师和预约；
4. 安装、检查、维修、备件领用和工时登记；
5. 保修资格判定和费用审批；
6. 升级、客户确认、结案和满意度；
7. Service Report 归档与后续知识沉淀。

**UNKNOWN 路径：** 已检索 `apps/service/`、`core/object360/technical_service/`、V14 runtime DDL、service/technical templates 和 NDE。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| SRV-V1 | records limit 范围 | UNKNOWN | 无业务范围限制证据 |
| SRV-V2 | case_id 必须唯一命中 | Missing | detail fallback 可能返回第一条 |
| SRV-V3 | ticket/case 必须存在 | Weak | repository 安全读取可能退化为空 |
| SRV-V4 | customer_id 必须对应客户 | Missing / UNKNOWN |
| SRV-V5 | product/serial/交付必须可追溯 | Missing |
| SRV-V6 | 状态转换必须合法 | Missing | shadow 只接受任意 status |
| SRV-V7 | SLA 截止时间和升级 | Not implemented |
| SRV-V8 | 保修范围与期限 | Not implemented |
| SRV-V9 | 备件库存和费用变更需授权 | Not implemented |
| SRV-V10 | 关闭需解决方案、客户确认或签收 | Not implemented |
| SRV-V11 | Service Report 必须关联真实 case | UNKNOWN |
| SRV-V12 | AI 建议必须标明 shadow/来源且不可写回 | Hard boundary in TechnicalService360 design |
| SRV-V13 | Service API 权限 | UNKNOWN | thin routes 未见业务 permission gate |

---

## 5. 数据含义

| Entity / field | 含义 |
|----------------|------|
| `tickets` | Service repository 期望的主表；活动 DDL UNKNOWN |
| `technical_service` | Object360 规范化对象名，不证明存在同名主表 |
| `case_no` | 技术服务案例编号语义 |
| `case_title` | 案例标题 |
| `customer_id` | 预期客户关联 |
| `service_type` | 安装/维护/维修等服务分类意图 |
| `status` | 原始对象状态；shadow 直接映射为 lifecycle stage |
| `remark` | 非结构化说明 |
| association edge | 从调用上下文临时派生的展示关系，不是持久化关系 |
| Service Report | NDE 文档类型；业务来源和签署闭环 UNKNOWN |

---

## 6. 状态词汇

| Status | 使用位置 | 含义 |
|--------|----------|------|
| `active` / `Active` | DTO 默认 / object fallback | 通用活动占位，不是成熟服务状态 |
| `Open` | 兼容测试 fixture | 开放案例示例 |
| `registered` | Shadow lifecycle event | 对象已载入视图 |
| `linked` | Shadow lifecycle event | 调用上下文包含关联列表 |
| `shadow` | Object360 bundles | 只读派生视图 |
| `planned` | Service README | 业务工作区未完成 |

Assigned、In Progress、Waiting Customer、Resolved、Closed、Cancelled、Escalated、Warranty Approved 等状态机均 UNKNOWN。

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `apps/service/README.md` | Planned 范围声明 |
| `apps/service/routes.py` | health/records/workspace 只读 API |
| `apps/service/service.py` | 列表、health 和 detail context |
| `apps/service/repository.py` | `tickets` 主表假设 |
| `apps/service/schemas.py` | 通用 DTO 默认状态 |
| `apps/service/workspace.py` | Workspace metadata |
| `core/object360/technical_service/runtime.py` | Shadow bundle 附加 |
| `core/object360/technical_service/technical_service_record.py` | 基本字段语义 |
| `core/object360/technical_service/technical_service_registry.py` | 预期服务分区 |
| `core/object360/technical_service/technical_service_lifecycle.py` | 只读生命周期派生 |
| `core/object360/technical_service/technical_service_relationship.py` | 上下文关联派生 |
| `core/object360/technical_service/technical_service_ai.py` | 固定 shadow 建议、无 gateway invoke |
| `document/nde_engine.py` | Service Report 文档类型 |
| `templates/print/service_report_document.html` | 通用打印模板继承 |
| `runtime/v14/legacy_support.py` | 未发现 ticket/technical_service 主表的检索范围 |
| `apps/service/` / `core/object360/technical_service/` / service templates | UNKNOWN 检索范围 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
