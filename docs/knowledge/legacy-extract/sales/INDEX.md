# Sales Knowledge Extract — Index

**Verified:** 2026-07-23 · Source root `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| 销售订单 Sales Order | [sales_order.md](sales_order.md) | Strong — convert / approve / ownership | `apps/sales/`, `business_modules/sales.md` |

## Cross-pack links

| From | To | Meaning |
|------|----|---------|
| Quotation | Sales Order | `convert_so`; quote → `已确认` |
| Sales Order | Delivery | `create_do` → Delivery Created |
| Sales Order | Finance | Receipts drive payment_status |
| Opportunity / Requirement | Sales Order | Optional lifecycle link on convert |

## Pack rules

- Knowledge only — paraphrase; cite Legacy paths; never copy source.
- Writable home: `docs/knowledge/legacy-extract/sales/**` (plus pack README updates under `legacy-extract/`).
