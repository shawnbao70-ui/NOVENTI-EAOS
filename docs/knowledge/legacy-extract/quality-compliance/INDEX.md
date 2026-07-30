# Quality & Compliance Knowledge Extract — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| Quality Check | [quality_check.md](quality_check.md) | Medium for sample scoring; weak GTFIP trade-QC surface; absent for incoming/final release | `apps/sample/`, `v15/gtfip/`, PO Receive, inventory ledger |
| Nonconformance | [nonconformance.md](nonconformance.md) | Absent for NCR/concession/quarantine lifecycle | sample risk text, inventory quantity/location, negative full-repo search |
| Compliance Records | [compliance_records.md](compliance_records.md) | Medium for requirement/trade-document metadata; weak for certificate and lot traceability | NDE, Document Center, GFIP/GTFIP, sample requirements, inventory ledger |
| Claim / RMA | [claim_rma.md](claim_rma.md) | Weak/planned; no operational RMA | `apps/service/`, TechnicalService360 shadow, complaint graph/demo, customer-service placeholders |

## Cross-module map

| From | To | Observable meaning |
|------|----|--------------------|
| Sample Quality | Inventory | Sample can be materialized without reading quality assessment |
| Procurement | Inventory | Open PO can be received directly to SKU stock without inspection lot |
| Quality | Documents | QC/Inspection/Certificate names exist as print types, but no dedicated quality fact producer is proven |
| Compliance | Sample | Certification requirement is free text and is not a quality gate |
| Compliance | Inventory | PO/Sample source remarks provide document-level provenance, not lot/serial genealogy |
| Claim / RMA | Service | Service is planned/read-only shadow; no claim or return command chain |
| Complaint | Business Graph | Complaint is a graph object vocabulary; visible sample complaint is demo data |
| Nonconformance | Inventory | No quarantine bucket or hold/release execution exists |
| GTFIP Quality | Nonconformance | Default `planned`/85/checklist surface does not create NCR, hold or release |
| GTFIP Documents | Compliance | Row-level `ready/verified` does not validate certificate content, issuer or expiry |
| DO Reopen | Claim / RMA | Status-only reopen and generic Inventory Adjust do not form a return authorization/receipt chain |

## Coverage and hard-threshold check

| Body | Rules | Validations | Data semantics | Evidence rows | UNKNOWN with searched paths |
|------|------:|------------:|---------------:|--------------:|----------------------------:|
| `quality_check.md` | 20 | 15 | 20 | 22 | 9 |
| `nonconformance.md` | 18 | 14 | 17 | 19 | 9 |
| `compliance_records.md` | 26 | 19 | 24 | 22 | 11 |
| `claim_rma.md` | 22 | 17 | 19 | 20 | 10 |

## Critical honesty findings

1. The sample quality table is an append-only scoring surface, not a specification-driven inspection plan.
2. Current Sample360 receives the latest quality record in context but does not use it to gate inventory materialization.
3. Purchase receiving posts ordered positive quantities straight to inventory; received, accepted and rejected quantities are not separated.
4. Inventory is aggregated by SKU and has no observed lot, serial, expiry, quality-status or quarantine quantity.
5. No operational NCR, concession, deviation, quarantine, rework, scrap or MRB lifecycle was found.
6. Certificate and Inspection Report templates are generic NDE shells; the Certificate path may reuse a sample number as document number.
7. Document Center version/archive capabilities are metadata-only and cannot establish regulated retention.
8. Service, complaint and return surfaces are planned, demo or placeholder; no RMA authorization/receipt/disposition/refund closure exists.
9. GTFIP quality defaults and GFIP/GTFIP document status flags are operational surfaces, but neither proves inspection release or certificate validity.
10. DO Reopen is status-only; restoring stock through generic adjustment does not create a controlled sales-return or RMA reversal.

## Search coverage

Required areas inspected:

- `apps/inventory/**`
- `apps/sample/**`
- `apps/service/**`
- `apps/procurement/**`
- related `templates/**`
- `business_modules/**`
- `docs/reports/**`
- full-repo keyword families: quality/QC/inspection, RMA/claim/complaint/return/warranty, NCR/nonconformance/concession/deviation/quarantine/rework/scrap, certificate/COA/COC/MSDS, lot/batch/serial/traceability.
