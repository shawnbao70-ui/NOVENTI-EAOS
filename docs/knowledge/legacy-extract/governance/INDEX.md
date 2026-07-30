# Governance Knowledge Extract — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| 审批中心 | [approval.md](approval.md) | Medium — record actions strong; cross-module release gates fragmented | `apps/approval/`, V18 business services |
| 文档中心 | [documents.md](documents.md) | Medium for metadata; weak for execution | `core/document/`, `apps/document_center/` |
| 海关与贸易中心 | [customs.md](customs.md) | Medium for metadata; weak for operational workflow | `core/customs/`, `apps/customs_center/` |

## Cross-module governance map

| Governance capability | Consumer / boundary | Observed meaning |
|-----------------------|---------------------|------------------|
| Approval record | Generic source module / source number | Pending queue with approve/reject history |
| Human Approved | Quote, SO, PO, DO ship, DO→AR, AR reminder | Local confirmation gate; generally does not create Approval Center record |
| Document module key | Quote, order, invoice, receipt, contract, customs, etc. | Content-domain metadata classification |
| Document generation | Quote/SO/DO/Invoice/PI | NDE/print capability remains separate from Document Center metadata |
| Customs registry | Incoterm, country, shipping, HS, declarations, trade documents | Metadata catalog; `implemented=false` |

## Critical honesty findings

1. Generic approval actions can update records, but observed routes do not consistently prove approver authorization or Pending-only enforcement.
2. V18 Human Approved surfaces are local business gates, not evidence of centralized multi-step approval workflow.
3. Workflow registry advertises single/multi/sequential/parallel/conditional approval types as unimplemented metadata.
4. Document and Customs centers are disabled by default and explicitly preserve Legacy runtime as authoritative.
5. `contract` is only a document module key; no commercial contract lifecycle was found.
6. Incoterms, country rules and transport registrations are catalogs, not executable trade rules.
