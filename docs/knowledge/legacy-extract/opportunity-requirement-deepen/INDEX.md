# 商机—需求深化索引

## 文档导航

| 文档 | 深化主题 | 稳定 ID |
|---|---|---|
| [`opportunity_sources.md`](opportunity_sources.md) | 来源词汇、人工创建、OPP 编号、客户与负责人 | `OS-*` |
| [`opportunity_lifecycle.md`](opportunity_lifecycle.md) | 声明链、状态筛选、状态写入缺口 | `OL-*` |
| [`requirement_create.md`](requirement_create.md) | REQ 编号、商机 1:N、缓存计数 | `RC-*` |
| [`requirement_trace.md`](requirement_trace.md) | 样品/报价/订单追溯与静默降级 | `RT-*` |

## 权威与边界

| 主题 | 权威入口/交叉引用 | 本包处理 |
|---|---|---|
| 商机总体定义 | [`../crm/opportunity.md`](../crm/opportunity.md) | 不重写，只深化创建和状态实现 |
| 样品转报价 | [`../sample-deepen/sample_to_quote.md`](../sample-deepen/sample_to_quote.md) | 只描述 requirement/opportunity 传播边界 |
| 样品主流程 | [`../sample/sample.md`](../sample/sample.md) | 不改收样、测量、入库规则 |
| 报价主流程 | 既有报价与定价知识包 | 不展开报价行和计价 |

## 核心证据索引

| 路径 | 证据主题 |
|---|---|
| `v15/business_lifecycle/constants.py` | 声明生命周期、来源/类型/状态词汇 |
| `v15/business_lifecycle/routes.py` | 页面、创建入口与权限 |
| `v15/business_lifecycle/repository.py` | 编号、默认值、插入、计数和状态更新 primitive |
| `v15/business_lifecycle/workflow.py` | 样品/报价/订单追溯传播 |
| `v15/business_lifecycle/requirement360.py` | 需求聚合查询、时间线和降级 |
| `v15/business_lifecycle/context360.py` | 跨对象生命周期投影 |
| `database/business_lifecycle_schema.py` | 表、唯一键、外键、索引和扩展列 |
| `templates/business/*.html` | 创建字段、显示字段和人工 CTA |
| `apps/quotation/` | requirement 直转报价及 sample 转报价调用点 |
| `apps/sample/` | 样品侧实际缺少 requirement 绑定入口的证据 |

## 主要结论

1. 持久化商机与“机会挖掘/AI 洞察”是不同能力，后两者未证明自动建商机。
2. OPP/REQ 编号按“全表行数 + 1”生成，虽有唯一约束，但并发和删除后碰撞未被处理。
3. 商机默认 `open`，但未见可执行商机状态更新路由；声明的 `qualified/converted/closed` 不是已实现状态机。
4. 一个商机可关联多条需求；`requirement_count` 是创建时递增的缓存，不是查询时实时 `COUNT`。
5. 需求创建与商机计数更新同一提交，但无显式事务/回滚边界，且独立创建可绕开商机关联。
6. 追溯同时依赖头字段、下游反向字段和 `requirement_links`，三者可能漂移。
7. workflow 对缺表/缺列采用条件写和异常吞掉，业务动作可成功而追溯不完整。
