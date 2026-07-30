# Quote Convert Policy Deepen — Index

## Module Index

| Module | Evidence strength | Primary question | Primary Legacy locus |
|--------|-------------------|------------------|----------------------|
| [`quote_state_normalization.md`](quote_state_normalization.md) | Strong / strong negative | Sent、Won、已确认能否安全归一？ | `apps/quotation/`, `apps/sales/`, quote templates |
| [`approve_convert_policy.md`](approve_convert_policy.md) | Strong / strong negative | Approve、Convert 和中央审批是否同一 gate？ | quotation/sales/approval routers and services |
| [`convert_concurrency.md`](convert_concurrency.md) | Strong for sequence; negative for constraints | 一报价一 SO 在并发下是否成立？ | Sales repository/service, runtime schema, bootstrap |
| [`commercial_term_propagation.md`](commercial_term_propagation.md) | Strong / strong negative | 哪些商务条款随 Convert 传播？ | quotation/sales/finance repositories and NDE |

## Cross-pack Map

| This pack | Read-only cross-reference | Boundary |
|-----------|---------------------------|----------|
| quote state | `../quotation-deepen/quote_lifecycle.md` | 基线生命周期；本包专注归一风险 |
| approve/convert | `../quotation-deepen/quote_approve.md`, `../governance/approval.md` | Type A 与中心审批不可混同 |
| convert policy | `../order-chain/so_convert.md`, `../order-chain/so_approve_open.md` | Quote Convert 与 SO Approve 分离 |
| concurrency | `../commission-ledger-deepen/commission_on_convert.md` | TC 是可部分失败的副作用 |
| payment/credit | `../commercial-terms/payment_terms.md`, `credit_limit.md` | 条款存在于 Quote/Customer，但不进 Convert gate |
| discount/FX | `../commercial-terms/discount_rules.md`, `../pricing-advanced/currency_price.md` | 净价格传播；折扣/汇率语义不传播 |
| Incoterms | `../commercial-terms/commercial_incoterms.md` | 主商业链无可传播字段 |

## Coverage Check

| Module | Rules | Validations | Data semantics | Evidence rows | UNKNOWN with searched paths |
|--------|------:|------------:|---------------:|--------------:|----------------------------:|
| quote_state_normalization | 23 | 12 | 17 | 17 | 9 |
| approve_convert_policy | 22 | 15 | 16 | 16 | 9 |
| convert_concurrency | 22 | 12 | 15 | 15 | 9 |
| commercial_term_propagation | 24 | 14 | 18 | 18 | 9 |

## Policy Truth Table

| Fact | Legacy enforcement | Honest interpretation |
|------|--------------------|-----------------------|
| Draft→Sent | Type A checks Draft, rows, human confirm | Local human publication |
| Sent→Convert | No dependency | Sent is not a Convert prerequisite |
| Central Approved→Convert | No observed linkage | Approval Center is not the release gate |
| one Quote→one SO | Application read-before-write | Sequential guard, not proven concurrent uniqueness |
| Quote→SO commercial terms | Amount/line snapshot only | Full commercial contract does not propagate |
| Convert→commission | Best-effort within pre-commit sequence | SO can exist without TC |
| Convert→lifecycle | Best-effort post-commit | SO can exist without chain link |

## Critical Migration Risks

1. 直接翻译 `已确认` 为 Won 会污染 KPI；翻译为 Sent 会伪造审批。
2. 将 UI button 权限当作 Convert 服务端授权会保留直链越权。
3. 将先查后插当作并发幂等会在双请求下产生重复 SO/佣金。
4. 将 quote ID 追溯当作条款快照会掩盖付款、FX、信用和贸易条件的传播缺失。
5. 以 redirect 成功表面判断完整转换会漏掉 TC 和 lifecycle 的部分失败。

## Package Boundary

本索引及四份正文只登记只读证据。未修改 quotation、order-chain、commission、commercial-terms、sales、crm、governance 或其他邻包。
