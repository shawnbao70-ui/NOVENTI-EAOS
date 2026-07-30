# RP-003 Numbering Custody Card

**Program:** Capability First  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)  
**Knowledge map (read-only):** `docs/knowledge/legacy-extract/numbering-collision-deepen/**`

## Field objective

Observe, score, and HOLD document-number identity, uniqueness, collision, and custody through the **Cap≠Org mapping** lens — map numbering as a capability (generate/unique/retry/authority), not a department form. Do not edit `docs/knowledge/**` or treat knowledge-pack conclusions as live facts.

## Numbering / identity observation points

1. Generate capability without uniqueness capability
2. Uniqueness capability present for OPP/REQ but absent for Quote/SO/DO
3. Retry/disposition capability after unique violation
4. Shared-sequence capability across commercial documents
5. Authority-key capability vs display-format capability
6. Cross-module DO numbering as duplicated local capabilities

## Scoring / HOLD (RP-003)

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
