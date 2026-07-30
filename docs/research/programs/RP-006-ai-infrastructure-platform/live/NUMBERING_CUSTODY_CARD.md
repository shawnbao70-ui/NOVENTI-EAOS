# RP-006 Numbering Custody Card

**Program:** AI Infrastructure Platform  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)  
**Knowledge map (read-only):** `docs/knowledge/legacy-extract/numbering-collision-deepen/**`

## Field objective

Observe, score, and HOLD document-number identity, uniqueness, collision, and custody through the **telemetry/jobs** lens — observe infra sequence/telemetry gaps—without enabling mint/execute. Do not edit `docs/knowledge/**` or treat knowledge-pack conclusions as live facts.

## Numbering / identity observation points

1. Absence of centralized sequence service / clock source
2. Missing collision metrics, alerts, or dead-letter for number fails
3. Lack of idempotency keys tied to number mint attempts
4. Log gaps when unique violation has no retry
5. Multi-instance race risk for COUNT+1 and timestamp generators
6. Custody hash linking number mint to subsequent business writes

## Scoring / HOLD (RP-006)

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
