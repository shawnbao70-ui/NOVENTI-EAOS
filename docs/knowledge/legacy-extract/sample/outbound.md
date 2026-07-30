# 样品出库 / 发样 / 派送（Sample Outbound）— Legacy Knowledge

**Evidence strength:** Missing（样品出库与客户派送）/ Strong（样品收货入库）/ Weak（需求侧 `sample_sent` 词汇与概念链）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件只核查样品从企业库存发给客户的出库、派送、承运和交付规则。必须与以下邻近证据分开：

- `Sample Receipt`：样品绑定产品后增加企业库存，是入库。
- `sample_sent`：业务需求状态词汇，未找到样品发运写入逻辑。
- Delivery Order Ship：销售订单商品发货，未找到样品引用。

未发现样品 outbound/dispatch/shipment 实体、路由、服务、库存扣减、运单或交付关联。相应能力均为 `UNKNOWN`。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| SAMPLE-OUT-RULE-001 | Legacy 样品核心方向是客户来样登记，创建写收样日期与 `New` | 不表示向客户发样 | Strong |
| SAMPLE-OUT-RULE-002 | `materialize_sample` 写 `Sample Receipt` 台账并增加库存，成功后状态 `Stocked` | 明确是 inbound，不是 outbound | Strong |
| SAMPLE-OUT-RULE-003 | 销售 Delivery Order ship 会扣减订单商品库存 | DO 由 Sales Order 创建，未见 `sample_id` | Strong adjacent evidence |
| SAMPLE-OUT-RULE-004 | 需求状态集合包含 `sample_pending`、`sample_sent` | 未找到触发 `sample_sent` 的处理器 | Weak |
| SAMPLE-OUT-RULE-005 | Sample360 关系图可关联客户、供应商、报价、订单 | 未装配 delivery/shipment 节点 | Weak/negative |
| SAMPLE-OUT-RULE-006 | 样品出库单编号、发样数量、发样原因与经手人为 `UNKNOWN` | 无样品 outbound schema | Missing |
| SAMPLE-OUT-RULE-007 | 发样审批、库存预留、可用量与重复发样规则为 `UNKNOWN` | 无发样服务 | Missing |
| SAMPLE-OUT-RULE-008 | 承运商、运单号、派送方式、运费、地址与预计到达为 `UNKNOWN` | 无样品物流字段 | Missing |
| SAMPLE-OUT-RULE-009 | 发样后扣库存并写独立幂等台账为 `UNKNOWN` | 只找到 Sample Receipt 入库幂等键 | Missing |
| SAMPLE-OUT-RULE-010 | 发样与客户、需求、商机、报价、Delivery Order 的关系基数为 `UNKNOWN` | 无 outbound 关系实体 | Missing |

## 3. 流程

### 3.1 已实现但方向相反的样品入库

`客户来样 → New → 绑定目录产品 → Sample Receipt → 库存增加 → Stocked`

该流程不能作为发样流程复用或反向解释。

### 3.2 普通销售发货（邻接，不属于样品）

`Quotation → Sales Order → Delivery Order → Ship（扣库存）→ Complete`

Delivery Order 从销售订单及其行生成；已查实现未见 sample id、sample outbound type 或样品专属分支。

### 3.3 样品发出流程

`申请发样 → 审批 → 预留/拣样 → 出库 → 交承运 → 在途 → 送达`

整条流程为 `UNKNOWN`。需求词汇 `sample_sent` 不能补足单据、库存、权限和物流证据。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| SAMPLE-OUT-VAL-001 | Sample Receipt 要求样品存在、已绑产品、数量 > 0 且未重复入库 | 强（inbound） | 不适用于发样 |
| SAMPLE-OUT-VAL-002 | Delivery Order ship 要求开放状态、库存充足且台账未重复 | 强（普通销售） | 未连接 sample |
| SAMPLE-OUT-VAL-003 | 发样必须关联有效样品与客户 | 缺失 | `UNKNOWN` |
| SAMPLE-OUT-VAL-004 | 发样数量 > 0 且不超过可用库存 | 缺失 | `UNKNOWN` |
| SAMPLE-OUT-VAL-005 | 发样需要审批和出库权限 | 缺失 | `UNKNOWN` |
| SAMPLE-OUT-VAL-006 | 运单号唯一、承运与地址完整 | 缺失 | `UNKNOWN` |
| SAMPLE-OUT-VAL-007 | 重复提交与重复扣库幂等 | 缺失 | `UNKNOWN` |
| SAMPLE-OUT-VAL-008 | 发样成功自动把需求改为 `sample_sent` | 缺失 | 未找到写入路径 |

## 5. 数据含义

| 概念 | 可确认含义 |
|---|---|
| `samples.customer_id` | 来样所属客户，不证明收件客户 |
| `samples.product_id` | 入库前绑定的目录产品 |
| `Sample Receipt` | 库存台账入库类型 |
| `SAMPLE-{id}` | Sample Receipt 的幂等备注 |
| `Stocked` | 样品已物化为库存，不表示已发出 |
| `sample_sent` | `business_requirements.status` 候选值，不是样品发运记录 |
| Delivery Order / inventory ship ledger | 销售商品履约数据；未见样品引用 |

未找到的数据：sample outbound header/items、收件客户/联系人/地址、发样数量、批次、仓库、承运商、tracking no、dispatch/delivery 时间、费用、审批、库存台账引用。全部 `UNKNOWN`。

## 6. 状态词汇

| 状态 | 所属语境 | 结论 |
|---|---|---|
| `New` | samples | 新收样品 |
| `Stocked` | samples | 已入企业库存 |
| `sample_pending` | business_requirements | 等待样品的需求词汇 |
| `sample_sent` | business_requirements | 声明式“样品已发”；无发运实现 |
| Pending / Shipped / Delivered | Delivery Order | 普通销售交付状态，不得套用于样品 |
| Requested / Approved / Picked / Dispatched / In Transit / Delivered / Returned | — | `UNKNOWN`；未找到样品 outbound 枚举 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\sample_relationship.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\sample_integration.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\constants.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\workflow.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A005_Sample_Quote_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A017_Sample_Ops_Report.md`

**Negative search:** 已检索 sample + outbound/dispatch/ship/shipment/delivery/tracking/carrier/waybill/发样/派送/出库，以及 Delivery Order、库存台账和需求状态写入路径；未找到样品发运实现。
