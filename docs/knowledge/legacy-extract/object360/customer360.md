# Customer360 装配观察 — Legacy Knowledge

**Evidence strength:** Strong（客户详情查询与页面区块）/ Medium（并行 Object360 context）/ Missing（统一事件、附件和跨对象治理）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件覆盖 `/customers/{customer_id}` 的 Customer360 页面装配、字段/区块、关联集合、实时统计和并行 runtime context。跟进规则见 [../followup/followup.md](../followup/followup.md)，客户与商机边界见 [../crm/](../crm/)；此处只记录装配交界。

Legacy renderer 是页面权威。Legacy 没有独立 `/customer360/{id}`：canonical 入口是 `/customers/{id}`，旧 `/customer/{id}` 仅重定向。`core/object360/customer` 会复用详情查询结果生成并行 context，但当前模板未引用该 key、失败也被隔离，且附件仍明确依赖旧详情面；不得据此推导统一对象平台已经接管。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 证据强度 |
|---|---|---|
| CUSTOMER360-RULE-001 | Customer360 以单个客户记录为中心；客户不存在时返回 not found | Strong |
| CUSTOMER360-RULE-002 | 主装配同时读取跟进、报价、销售订单、收款及交付单；各集合仍由所属业务表持有 | Strong |
| CUSTOMER360-RULE-003 | 摘要实时计算报价数/额、订单数/额、收款额、跟进数及应收余额；余额 = 销售订单总额 − 收款总额 | Strong |
| CUSTOMER360-RULE-004 | 页面包含 Basic、Contacts、Followups、Demand、Quotes、Sales Orders、Delivery、Receipts、AR、Credit、AI、Timeline 十二个区块 | Strong |
| CUSTOMER360-RULE-005 | Demand 区由 lifecycle enrichment 注入商机和业务需求；注入异常被吞并，不阻断旧页面 | Strong |
| CUSTOMER360-RULE-006 | Timeline 依次展示跟进、报价、销售订单，不做跨类型按事件时间归并 | Strong |
| CUSTOMER360-RULE-007 | Quote/SO/Delivery/Receipt 行链接回各自详情；Customer360 是交叉入口，不取得单据状态所有权 | Strong |
| CUSTOMER360-RULE-008 | Credit 标签以页面阈值从余额派生；它是展示规则，不是持久化信用审批结论 | Strong |
| CUSTOMER360-RULE-009 | 并行 runtime context 派生 identity、timeline、knowledge、search、AI summary 与 relationship graph，不额外查询数据库 | Medium |
| CUSTOMER360-RULE-010 | 并行 timeline 由旧集合重建；AI recommendation 标记 `gateway_invoked=false`，不是 AI 执行证据 | Strong |
| CUSTOMER360-RULE-011 | attachment context 固定计数为 0，并声明等待 File Center wiring | Strong negative |
| CUSTOMER360-RULE-012 | Customer360 对所有区块的统一分页、时间口径、租户隔离和字段级权限为 `UNKNOWN` | Missing |
| CUSTOMER360-RULE-013 | 并行 integration bridges 均 defer 给 Legacy，且 `_customer360_runtime` 未被详情模板消费 | Strong negative |
| CUSTOMER360-RULE-014 | Registry 声明 19 个 section，但 related products/samples、附件/文档/图片和 relationship graph 未在当前页面形成同名运行区块 | Strong negative |
| CUSTOMER360-RULE-015 | 首屏 health：余额 >100,000 为 Credit Watch，>10,000 为 Needs Follow-up；Credit tab warning 则使用 >30,000，两个阈值体系并不一致 | Strong |
| CUSTOMER360-RULE-016 | 页面 win rate = 销售订单笔数 / 报价笔数，不是 CRM closed-won 转化率 | Strong |
| CUSTOMER360-RULE-017 | Contacts 区只展示 customer 行内联系人字段，未装配独立 contacts 集合 | Strong |

## 3. 流程

1. 请求 `/customers/{customer_id}`。
2. 服务读取客户；不存在则停止并返回 404 内容。
3. Repository 分别查询跟进、报价、订单、收款、交付和各类统计。
4. 服务计算余额，并尝试注入商机/需求 lifecycle context。
5. 服务尝试从同一 context 构造并行 Customer360 runtime bundle；失败不影响旧页面。
6. 页面渲染十二个业务区块及跨模块详情链接。
7. Followups 区可提交新增跟进；其校验和缺口以 followup 知识包为准。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| CUSTOMER360-VAL-001 | 路径 `customer_id` 为整数且客户必须存在 | 强 | 不存在返回 not found |
| CUSTOMER360-VAL-002 | 报价空态的新建入口按 `Quotes.add` 控制 | 强（局部） | 不代表整个页面统一授权 |
| CUSTOMER360-VAL-003 | Customer360 详情读取权限 | 缺失/不一致 | 未见与客户列表相同的 owner/tenant 门禁 |
| CUSTOMER360-VAL-004 | 各关联行确属当前客户 | 强（查询） | 交付通过所属销售订单关联客户 |
| CUSTOMER360-VAL-005 | lifecycle/Object360 enrich 结果完整性 | 弱 | 异常被捕获并静默降级 |
| CUSTOMER360-VAL-006 | 余额币种一致 | 缺失 | 页面 runtime 摘要固定展示 USD，未见跨币种归一 |
| CUSTOMER360-VAL-007 | Timeline 全局顺序、去重和不可变性 | 缺失 | 只是多个集合拼接 |
| CUSTOMER360-VAL-008 | 附件、文档、图片计数 | 缺失 | runtime context 固定为 0 |

## 5. 数据含义

| 数据/区块 | 业务含义 |
|---|---|
| Basic | 客户代码、公司、类型、等级、状态、来源、owner、备注及聚合计数 |
| Contacts | 主联系人、电话、邮箱、国家/地区等客户字段；未见独立联系人集合装配 |
| Followups | 客户附属沟通记录和新增入口 |
| Demand | 客户关联商机与业务需求，由 lifecycle enrichment 注入 |
| Quotes / Sales Orders | 客户商业转换单据及各自状态 |
| Delivery / Receipts | 经销售订单关联的交付、直接按客户关联的收款 |
| AR | 销售总额、收款总额及差额 |
| Credit | 基于 AR 余额阈值的页面标签 |
| Timeline | 展示型集合拼接，不是持久事件流 |
| `_customer360_runtime` | 并行派生 context；旧 renderer 仍权威 |

## 6. 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| Healthy Customer / Needs Follow-up / Credit Watch | 服务按 AR 余额派生的 health 标签 |
| normal / moderate / high AR | Credit tab 按 30,000 / 100,000 余额阈值显示的表象；与首屏 10,000 阈值不同 |
| A / B / C / D | 按销售总额派生的 credit band，不是外部征信等级 |
| clear / partial / unpaid | 按余额与已收款派生的 collection 表象 |
| Draft 等报价状态 | 来源于报价，不属于 Customer360 状态 |
| 销售订单、交付状态 | 来源于各自业务对象 |
| runtime / skipped | 并行 runtime bundle 模式，不是客户生命周期状态 |
| Customer360 统一状态 | `UNKNOWN`；已查页面、service、runtime context，未见独立状态机 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\history.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\customer_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\includes\v18\customer360_first.html`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\enrich.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\context360.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\customer\runtime.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\customer\runtime_context.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\customer\customer_object.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\customer\customer_integration.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\customer\customer_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\scripts\v170_final_canonical_cleanup.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\runtime\Customer360_Runtime_Context.md`
