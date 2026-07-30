# RP-007 Numbering Custody Card

**Program:** Enterprise Evolution Engine  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)  
**Knowledge map (read-only):** `docs/knowledge/legacy-extract/numbering-collision-deepen/**`

## Field objective

Observe, score, and HOLD document-number identity, uniqueness, collision, and custody through the **evolution proposals** lens — HOLD evolution proposals that assume numbers are already collision-safe authority. Do not edit `docs/knowledge/**` or treat knowledge-pack conclusions as live facts.

## Numbering / identity observation points

1. Proposal to key all analytics on display numbers without uniqueness evidence
2. Proposal to merge dual DO generators without disposition rules
3. Proposal to drop DB unique on OPP/REQ without replacement
4. Proposal for AI auto-renumber as recovery
5. Proposal treating SO+quote_id as globally unique under concurrency
6. Any promote path that ignores numbering-collision deepen findings → HOLD

## Scoring / HOLD (RP-007)

- Score generator family, uniqueness evidence, collision disposition, and authority vs display use.
- Dossier parallel numbers/IDs explicitly; label “not observed” versus “did not occur.”
- HOLD any claim that a display number is a collision-safe transactional authority without custody evidence.

## Required live evidence

1. Authorized dated/tokenized examples of each major generator family (OPP/REQ/Quote/SO/DO/Sample as applicable).
2. DDL/index or equivalent uniqueness proof — or documented absence — per number class.
3. Concurrent/same-second collision or near-miss artifacts with disposition outcome.
4. Print/search/FK/ledger usage showing whether the number is authority or display.
5. Real source-custodian accounts corroborated by artifacts.
6. Custody, minimization, integrity, retention, contradictions, and falsifiers.

Missing evidence keeps this RP **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, Kernel/API/UI, or product code change.
3. No Brain execute, Twin authorize, product CRUD, renumber writes, or acceptance-on-behalf.
4. No synthetic/demo numbering collision relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no number mint, renumber, or identity repair.
