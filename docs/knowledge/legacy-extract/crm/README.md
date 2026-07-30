# Legacy Knowledge Extract — CRM Pack

**Source system:** `H:\Workspace\EZAM_CRM - 9.0` (also referenced as `EZAM_CRM-9.0`)  
**Mode:** Read-only knowledge extraction — **not** source extraction  
**Writable home:** only `NOVENTI-EAOS/docs/knowledge/legacy-extract/crm/**`  
**Date:** 2026-07-23 (re-verified against live Legacy root)  
**Milestone:** PHX-G290 / ADR-0309（pack Accepted）

---

## Purpose

Capture business rules, processes, validations, and data meanings from EZAM_CRM 9.0 so EAOS can rewrite CRM capabilities under the new architecture.

## Hard boundaries

| Do | Do not |
|----|--------|
| Paraphrase rules / flows / checks / field semantics | Copy Legacy source code, SQL dumps, or directory trees |
| Cite read-only source paths | Modify anything under `EZAM_CRM*` |
| Note gaps and contradictions honestly | Inherit Legacy architecture, menus, or frameworks |
| Write only under this `crm/` folder | Change `kernel/`, `api/`, `ui/`, Eng tip boards, or other packs |

## Entry format (per module)

Each module file uses:

1. **Scope & evidence strength**
2. **业务规则** — rule, trigger, exception, EAOS rewrite note
3. **流程** — lifecycle steps (conceptual)
4. **校验** — gates / permissions / required fields
5. **数据含义** — entities, statuses, key fields (semantics only)
6. **只读来源路径** — paths under Legacy, for audit

## Modules in this pack

See [INDEX.md](INDEX.md).

| Module | File |
|--------|------|
| 客户 | [customer.md](customer.md) |
| 商机 | [opportunity.md](opportunity.md) |
| 合同 | [contract.md](contract.md) |
| 报价 | [quotation.md](quotation.md) |

## Revenue-chain position (Legacy)

Conceptual upstream chain observed in Legacy lifecycle constants:

`Customer → Opportunity → Requirement → (Sample) → Quotation → Sales Order → …`

Contract is **not** a first-class stage in that chain; see [contract.md](contract.md).
