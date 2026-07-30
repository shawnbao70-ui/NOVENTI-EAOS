# Numbering Collision Deepen — Index

## Module Index

| Module | Evidence strength | Primary question | Primary locus |
|--------|-------------------|------------------|---------------|
| [`generators_matrix.md`](generators_matrix.md) | Strong | 每类编号如何生成？ | Lifecycle/Quotation/Sales/Inventory/Sample services |
| [`uniqueness_constraints.md`](uniqueness_constraints.md) | Strong / strong negative | 哪些编号由 DB 唯一保护？ | DDL, migrations, indexes |
| [`concurrency_collision.md`](concurrency_collision.md) | Strong algorithmic risk | 双开/同秒/同源会如何碰撞？ | generator + insert boundaries |
| [`display_vs_authority.md`](display_vs_authority.md) | Strong | 编号是展示还是事务关系键？ | routes/FKs/search/print/ledger |

## Generator Summary

| Entity | Generator | DB unique | Collision disposition |
|--------|-----------|-----------|-----------------------|
| OPP | `OPP-YYYYMMDD-COUNT+1` | Yes | reject, no retry |
| REQ | `REQ-YYYYMMDD-COUNT+1` | Yes | reject, no retry |
| New Quote | `QTYYYYMMDD + global COUNT+1` | No observed | duplicate may persist |
| Copy/Sample Quote | `QT + timestamp(second)` | No observed | same-second duplicate |
| SO | `SO + quote_id` | No observed | app guard race |
| Sales DO | `DO + timestamp(second)` | No observed | same-second duplicate |
| Inventory DO | `DO + so_id` | No observed | repeated source duplicate |
| Sample | `SP + timestamp(second)` | No observed | same-second duplicate |

## Cross-pack Map

| This pack | Read-only cross-reference | Boundary |
|-----------|---------------------------|----------|
| all modules | `../document-ops/numbering.md` | 编号总览；本包深化碰撞与权威 |
| SO uniqueness | `../convert-atomicity-deepen/so_uniqueness.md` | one Quote→one SO guard |
| Quote/SO/DO | CRM/Sales/Delivery adjacent packs | 只读引用，不修改正文 |

## Coverage Check

| Module | Rules | Validations | Data semantics | Evidence rows | UNKNOWN + searched paths |
|--------|------:|------------:|---------------:|--------------:|-------------------------:|
| generators_matrix | 22 | 12 | 16 | 19 | 9 |
| uniqueness_constraints | 24 | 12 | 17 | 16 | 9 |
| concurrency_collision | 30 | 13 | 17 | 18 | 9 |
| display_vs_authority | 22 | 12 | 20 | 19 | 9 |

## Critical Risk Map

| Risk | Trigger | Outcome |
|------|---------|---------|
| Count collision + UNIQUE | concurrent/deleted OPP/REQ | request fails |
| Count collision no UNIQUE | concurrent/deleted Quote | duplicate number persists |
| Timestamp collision | same prefix within one second | duplicate Quote/DO/Sample |
| Source-ID collision | duplicate/concurrent Convert | duplicate SO/DO number |
| Index illusion | ordinary or wrong-column index | false confidence |
| Weak source reference | TC/AR/ledger store business number text | ambiguous trace |
| Print authority confusion | derived NDE number | phantom document identity |

## Package Boundary

本包仅新增本目录六份知识文档。未修改 document-ops、crm、sales、delivery 或其他邻包正文。
