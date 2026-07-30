# RP-003 Tax / FX / Approval Field Card

**Program:** Capability First  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) · [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD **税票 · FX · 审批** as **capability claims vs runtime evidence**: whether “Tax Invoice,” “FX/Revaluation,” and “Approval Center” capabilities exist as callable, evidenced capabilities or as labels over AR/print, seed rates, and V18 confirms. Knowledge packages remain hypotheses; do **not** edit `docs/knowledge/**`. Cap≠grant remains closed.

## Tax / FX / approval observation points (RP-003 lens)

1. **Tax capability ≠ 税票主账:** Tax health/capability registry entries that do not bind a sales tax-invoice lifecycle.
2. **Finance workspace `/invoices` label ≠ tax authority:** route or module labels presented as tax-invoice capability without entity/DDL evidence.
3. **Locale Commerce currency capability ≠ FX conversion:** currency config / seed rates vs dated FX source and Convert propagation.
4. **Revaluation capability absence:** no revaluation job capability registered or runnable; dossiers must not invent one from Finance “close” prose.
5. **Approval Center capability ≠ V18 gate:** center hub/scaffold vs Type A Human Confirm consumed by Quote/SO/Convert/Ship.
6. **GET approve as capability smell:** approve/reject via GET treated as a “capability” without unsafe-method envelope.
7. **Cap≠grant:** tax/FX/approval capability scores never mint permission, filing authority, or FX posting rights.
8. **Brain/Twin non-capability:** HOLD AI advice presented as tax/FX/approval capability attestation.

## Scoring / HOLD

- Score claim→runtime binding, owner module, callable surface, and falsifiers for each tax/FX/approval capability label.
- Separate capability registry metadata from operational evidence (AR row, print PDF, rate seed, V18 confirm).
- HOLD when a capability card or health check is the only tax-invoice / FX / approval evidence.

## Required live evidence

1. Authorized capability registry / module inventory entries for tax, currency/FX, and approval with callable routes or attested gaps.
2. Runtime proof that tax capability does (or does not) create/void/credit a tax-invoice master distinct from AR/print.
3. Dated FX source + propagation evidence on Convert/SO/Receipt/AR (or attested non-propagation).
4. Approval Center create/submit hooks into commercial Type A paths—or attested non-consumption—plus GET vs POST method notes.
5. Cap≠grant attestation: capability score/list did not mint grants or filing authority.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-003 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, capability registry rewrite, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, Cap→grant, tax/FX posting, or approve execution.
4. No synthetic capability health output relabeled as live tax/FX/approval evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no capability mint, grant, tax, FX, or approval action.
