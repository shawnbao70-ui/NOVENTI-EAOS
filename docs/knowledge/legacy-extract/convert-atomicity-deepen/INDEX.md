# Convert Atomicity Deepen — Index

## Module Index

| Module | Evidence strength | Primary question | Primary locus |
|--------|-------------------|------------------|---------------|
| [`so_uniqueness.md`](so_uniqueness.md) | Strong / strong negative | 一报价一 SO 是否由 DB/lock 保证？ | Sales repository, runtime DDL, bootstrap |
| [`commission_atomicity.md`](commission_atomicity.md) | Strong for normal commit; mixed for exception cleanup | TC 与 SO 是否同成同败？ | Sales service/repository, TC schema |
| [`lifecycle_hook_atomicity.md`](lifecycle_hook_atomicity.md) | Strong for post-commit behavior | 链接失败是否阻断 Convert？ | Sales service, business lifecycle workflow |
| [`term_snapshot_on_convert.md`](term_snapshot_on_convert.md) | Strong / strong negative | Convert 冻结哪些商务条款？ | Quotation/Sales/Finance schemas and NDE |

## Atomicity Layers

| Layer | Commit / guard | Failure visibility | Honest result |
|-------|----------------|--------------------|---------------|
| One Quote→one SO | SELECT-by-quote before INSERT | redirect only | 顺序防重；并发唯一未证 |
| SO + TC + items + quote status | quote status repository commit | TC exception swallowed | 正常同批；业务上允许无 TC SO |
| lifecycle SO fields | post-main `_safe_update` commit | outer exception swallowed | 失败不撤销 Convert |
| requirement downstream | separate `_safe_update` commit | may stop later steps | 可部分链接 |
| requirement_links | optional relation write | inner exception swallowed | 可缺 relation row |
| commercial terms | selected fields copied | no missing-term warning | 金额结果快照，不是合同快照 |

## Cross-pack Map

| This pack | Read-only cross-reference | Boundary |
|-----------|---------------------------|----------|
| uniqueness | `../quote-convert-policy-deepen/convert_concurrency.md` | 并发基线；本包聚焦 DB/lock |
| commission | `../commission-ledger-deepen/commission_on_convert.md` | 费率/台账基线；本包聚焦 commit/rollback |
| lifecycle | `../order-chain/so_convert.md` | Convert 主链；本包聚焦 post-commit hook |
| term snapshot | `../quote-convert-policy-deepen/commercial_term_propagation.md` | 传播基线；本包提供快照字段矩阵 |
| payment/credit/discount/incoterm | `../commercial-terms/` | 各条款权威知识，不在本包重写 |

## Coverage Check

| Module | Rules | Validations | Data semantics | Evidence rows | UNKNOWN + searched paths |
|--------|------:|------------:|---------------:|--------------:|-------------------------:|
| so_uniqueness | 24 | 12 | 17 | 20 | 9 |
| commission_atomicity | 24 | 12 | 22 | 17 | 9 |
| lifecycle_hook_atomicity | 20 | 12 | 18 | 15 | 9 |
| term_snapshot_on_convert | 27 | 14 | 20 | 21 | 10 |

## Critical Failure Shapes

| Shape | Observable facts | Missing facts |
|-------|------------------|---------------|
| Duplicate conversion | two SO rows/lines, possibly two TC | no duplicate state/repair workflow |
| Missing commission | SO/items/quote committed, no TC | no durable commission failure event |
| Partial lifecycle | SO committed; some trace fields/links missing | no completion marker/retry |
| Term-loss conversion | totals/lines copied; quote_id present | no currency/payment/credit/tax/incoterm snapshot |
| Pre-commit exception | request failure before quote commit | explicit rollback/final connection cleanup UNKNOWN |

## Package Boundary

本包仅新增本目录六份知识文档。未修改 commission-ledger-deepen、quote-convert-policy-deepen、commercial-terms、order-chain 或其他邻包正文。
