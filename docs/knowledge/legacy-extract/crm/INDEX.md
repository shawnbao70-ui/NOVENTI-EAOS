# CRM Knowledge Extract — Index

**Verified:** 2026-07-23 · Source root `H:\Workspace\EZAM_CRM - 9.0` (read-only) · Writes only under this folder

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| 客户 Customer | [customer.md](customer.md) | Strong — extracted domain + page services | `apps/customer/`, `core/customer/`, `business_modules/crm.md` |
| 商机 Opportunity | [opportunity.md](opportunity.md) | Medium — lifecycle entity + AI stub mining | `v15/business_lifecycle/`, customer opportunity mining |
| 合同 Contract | [contract.md](contract.md) | Weak — document type label only | `core/document/types.py`, Document Center registry |
| 报价 Quotation | [quotation.md](quotation.md) | Strong — extracted domain + approve / convert | `apps/quotation/`, `core/quotation/`, Sales convert path |

## Cross-module links (conceptual)

| From | To | Meaning |
|------|----|---------|
| Customer | Quotes / SO / Receipts / Samples / Followups | Customer360 assembly & AR balance (SO − receipts) |
| Opportunity | Requirement | Opportunity owns requirement count; create req from opp |
| Requirement | Quote | Optional link at quote create; traceability fields |
| Quote | Sales Order | Convert creates SO; quote status becomes `已确认` |
| Contract | (none operational) | Registry module key only — no CRM contract CRUD found |

## Pack rules

- Parent packs (`ops/`, `finance/`) are out of scope for this folder.
- Status vocabulary mixes **English** and **Chinese** in Legacy; EAOS rewrite should normalize deliberately (document the Legacy mix, do not silently pick one).
- Knowledge only — paraphrase rules/flows/checks/semantics; never copy Legacy source into this pack.
