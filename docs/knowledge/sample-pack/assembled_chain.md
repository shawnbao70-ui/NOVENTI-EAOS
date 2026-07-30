# Assembled revenue-chain conclusions

**Source of truth:** PHX-G290…G292 extract packs (paraphrased here for demo/research reading).  
**Not:** Product lifecycle or EAOS CRUD semantics.

## Chain map (observation)

```
Customer → Opportunity / Requirement (optional)
        → Quotation (Draft → optional Approve/Sent)
        → Convert SO (Quote 已确认 + SO pending; commission best-effort)
        → [optional SO Approve: Open]
        → Create DO → Ship (inventory) → Complete
        → DO→AR (accrual, not tax invoice)  ‖  SO→Receipt (separate; dual AR)
```

Contract is **not** a first-class CRM stage ([crm/contract.md](../legacy-extract/crm/contract.md)).

## Cross-linked conclusions

| Topic | Conclusion (from extracts) | Canonical pack |
|-------|----------------------------|----------------|
| Quote status mix | Legacy mixes Chinese/English status vocabulary; Convert sets quote `已确认` | CRM Quotation |
| Convert ≠ approval center | Sent / central approval are not Convert prerequisites | CRM + Sales |
| Commission | Best-effort TC ledger Pending on convert; not atomic with SO | Sales + Finance settlement |
| Create DO | SO→DO does not deduct stock; dual create paths / permission gaps recorded | Delivery |
| Ship / Complete | Ship posts inventory; Complete advances DO+SO; Reopen does not reverse stock/AR | Delivery |
| Dual AR | Order−receipts view vs delivery AR ledger are parallel / not auto-reconciled | Finance |
| DO Invoice | Receivable accrual path — not tax or commercial invoice | Finance + Delivery |
| AP / payment | Purchase invoice creates AP; payment does not auto-clear AP | Finance |

Full narrative: [legacy-extract README — revenue chain](../legacy-extract/README.md).

## Honesty holds for demo

- Do not narrate a single closed Quote→Cash ledger — extracts document fragmentation.
- Do not treat DO→AR as e-invoice / tax filing.
- Do not invent Contract CRUD because the registry key exists.
- Do not collapse dual AR into one “truth” without a future Gate + evidence.
