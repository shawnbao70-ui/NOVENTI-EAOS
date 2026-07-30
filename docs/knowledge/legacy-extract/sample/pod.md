# 样品签收 / POD / 回执（Sample Proof of Delivery）— Legacy Knowledge

**Evidence strength:** Missing（样品 POD 持久化与流程）/ Strong（普通 Delivery Order 明示未采集 POD）/ Weak（打印回执空白模板）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件核查样品送达后的签收人、签收时间、签名/盖章、照片、异常与回执证据。

未找到样品 outbound，因此也未找到样品 POD 实体、采集入口、附件关联或签收状态。邻接证据包括：

- Delivery Order 页面明确写明本卷未采集 POD/e-sign，并把 Complete 当作 delivery confirm；
- NDE 打印引擎有 Delivery Order 的空白 Receipt Confirmation 区块，可展示 received by/date/time/signature；
- 上述打印字段来自渲染 extra context，未证明数据库持久化，更未连接样品。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| SAMPLE-POD-RULE-001 | 样品图片是样品本体/分析附件 | 未找到 image_type 或关系将其定义为交付证明 | Strong negative boundary |
| SAMPLE-POD-RULE-002 | Delivery Order 页面将 Complete 视为 delivery confirm，并诚实标注 POD/e-sign 未采集 | 这是普通交付页面，不是样品 | Strong adjacent evidence |
| SAMPLE-POD-RULE-003 | NDE 的 Delivery Order 打印可呈现 Received By、Position、Company、Receive Date/Time、Signature 与盖章空位 | 空值时输出横线；未证明采集或存储 | Weak |
| SAMPLE-POD-RULE-004 | NDE 还可接受 delivered/received workflow time 与 customer/electronic signature 的额外上下文 | 通用渲染模型，不是样品 POD schema | Weak |
| SAMPLE-POD-RULE-005 | 样品 POD 必须关联哪次发样为 `UNKNOWN` | 无 outbound id | Missing |
| SAMPLE-POD-RULE-006 | 签收人、时间、签名、照片、GPS、备注的采集与存储为 `UNKNOWN` | 无样品 POD 表/字段 | Missing |
| SAMPLE-POD-RULE-007 | 拒收、短缺、破损、部分签收及重新派送规则为 `UNKNOWN` | 无异常状态机 | Missing |
| SAMPLE-POD-RULE-008 | POD 后自动推进需求到 `feedback_received` 为 `UNKNOWN` | 未找到 POD 或反馈写入逻辑 | Missing |
| SAMPLE-POD-RULE-009 | POD 的权限、不可抵赖、哈希、审计与保留期为 `UNKNOWN` | 通用文档 hash/历史不等于签收证明 | Missing |

## 3. 流程

### 3.1 普通 Delivery Order 的现状（邻接）

1. Delivery Order 执行 Ship。
2. 完成动作把交付标为 Complete/Delivered。
3. 页面将 Complete 当作 delivery confirmation。
4. 页面明确 POD / e-sign 未采集。
5. 打印模板可留出人工签收栏，但未找到回填持久化链。

### 3.2 样品 POD 流程

`样品派送到达 → 收件人核验 → 签名/盖章/照片 → 异常记录 → POD 固化 → 需求反馈`

整条流程为 `UNKNOWN`。不存在可确认的样品派送记录作为 POD 父实体。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| SAMPLE-POD-VAL-001 | POD 必须对应已发出的样品派送 | 缺失 | 无 outbound 记录 |
| SAMPLE-POD-VAL-002 | 签收人、签收时间至少一项必填 | 缺失 | `UNKNOWN` |
| SAMPLE-POD-VAL-003 | 签名/图片文件类型和大小安全校验 | 缺失（POD） | 样品图片上传校验不能自动套用 |
| SAMPLE-POD-VAL-004 | 重复签收、撤回与更正控制 | 缺失 | `UNKNOWN` |
| SAMPLE-POD-VAL-005 | 签收时间不得早于发出时间 | 缺失 | 两端时间均无样品证据 |
| SAMPLE-POD-VAL-006 | 异常签收必须记录原因与责任人 | 缺失 | `UNKNOWN` |
| SAMPLE-POD-VAL-007 | POD 查看/提交权限与客户身份认证 | 缺失 | `UNKNOWN` |
| SAMPLE-POD-VAL-008 | Delivery Order Complete 等同法定 POD | 弱/不成立 | 页面只是业务确认替代，并明确未采集 POD |

## 5. 数据含义

| 概念 | Legacy 中可确认的含义 |
|---|---|
| `samples` / `sample_images` | 样品档案及样品图片，不是交付回执 |
| Delivery Order Complete | 普通销售交付完成标签，被页面用作 delivery confirm |
| NDE receipt block | 打印呈现模型；可留签收人、职位、公司、日期、时间、签名和盖章位置 |
| NDE signatures/workflow extras | 调用方可传入的渲染上下文字段，非已确认数据库字段 |
| financial `receipts` | 收款记录，与 Proof of Delivery 无关 |

未找到的数据：sample_dispatch_id、pod_no、recipient identity、received_at、signature asset、stamp、photo evidence、GPS、device/IP、condition、exception code、accepted quantity、audit hash。全部 `UNKNOWN`。

## 6. 状态词汇

| 词汇 | 所属语境 | 结论 |
|---|---|---|
| Complete / Delivered | Delivery Order | 普通交付完成，不是样品 POD |
| Signed | Delivery Order 页面时间线标签 | 页面同时声明 POD/e-sign 未采集 |
| Receipt Confirmation | NDE 打印区块 | 空白确认栏，不是持久化状态 |
| `feedback_received` | business_requirements | 需求状态词汇；未与 POD 接线 |
| Pending Signature / Signed / Rejected / Partial / Disputed | — | `UNKNOWN`；未找到样品 POD 枚举 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\print\blocks\16_receipt_confirmation.html`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\documents\delivery_order.html`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\sample_integration.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\sample_relationship.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\constants.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\requirement360.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`

**Negative search:** 已检索 sample + POD/proof of delivery/signature/signed/received_by/receipt/acknowledgement/签收/回执/签名/盖章，以及样品、Delivery Order、NDE、附件和需求反馈路径；未找到样品 POD 持久化或流程。
