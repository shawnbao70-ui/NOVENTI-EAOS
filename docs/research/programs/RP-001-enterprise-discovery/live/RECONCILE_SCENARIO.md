# RP-001 Reconciliation Observation Scenario

**Program:** Enterprise Discovery  
**Status:** **Open** · **0 Complete**  
**Assigned live context / observer:** none / none  

## Mapping theme

Observe how parallel facts for **SO (Sales Order), DO (Delivery Order), inventory, Receipt, and AR (Accounts Receivable)** are sourced, timestamped, reconciled, scored for evidence quality, and held when inconsistent. RP-001 may discover and dossier these facts; it must not create, correct, post, release, settle, or execute them.

| Fact family | Discovery observation | Score / hold treatment |
|-------------|-----------------------|------------------------|
| SO | Identity, version, lines, quantity, price/terms, state, owner, source time | Score provenance/completeness; HOLD if basis/version conflicts |
| DO | SO linkage, allocation/release/shipment states, partials/cancellation | HOLD if linkage or release evidence is absent |
| Inventory | On-hand/available/allocated/in-transit and location/as-of | Score clock/scope; HOLD on unexplained negative or stale views |
| Receipt | Delivery/receipt identity, quantity/condition/time and discrepancy | HOLD if acknowledgment/proof is missing or accept-on-behalf is implied |
| AR | Invoice/receivable/payment-allocation state, currency, due/settled time | HOLD on unmatched, duplicated, disputed, or inaccessible evidence |

## RP-001 model treatment

1. **Sense** registers source owners, system views, timestamps, and evidence handles.
2. **Structure** maps SO→DO→inventory→Receipt→AR links without treating one system as universal truth.
3. **Score** rates freshness, provenance, completeness, contradiction, and coverage.
4. **Dossier** preserves parallel facts, unresolved differences, and chronology.
5. **Advise/HOLD** identifies evidence gaps only; no record mutation or operational recommendation is executed.

## Observable reconciliation checkpoints

1. SO quantity/state differs between order source, fulfillment source, and reporting extract.
2. DO is created, split, superseded, cancelled, or released without a stable SO/version link.
3. Inventory on-hand, available, allocated, and in-transit views use different clocks or location scope.
4. Shipment/DO indicates completion while Receipt is absent, partial, refused, damaged, or timestamp-shifted.
5. Receipt exists but invoice/AR trigger is missing, duplicated, delayed, or linked to the wrong version.
6. AR open/paid/disputed state conflicts with payment allocation or settlement evidence.
7. Dual-write/manual spreadsheet/interface retry changes one fact family without corresponding audit evidence.
8. No reconciliation/勾兑 process, owner, frequency, tolerance, exception queue, or sign-off can be observed.
9. Exception paths—partial fulfillment, return, credit/debit, cancellation, chargeback—break end-to-end correlation.

## Required live evidence

1. Dated, authorized, tokenized SO/DO/inventory/Receipt/AR extracts or controlled handles.
2. Source-system/version/owner and clock/as-of inventory for every fact family.
3. Stable chain identifiers, parent-child/version links, and transformation/correlation rules.
4. Reconciliation/勾兑 run, exception queue, tolerance, ownership, and audit/sign-off evidence.
5. At least one naturally occurring drift/partial/dispute/return path with chronology.
6. Real source-custodian/observer attestations corroborated by system artifacts.
7. Access, minimization, custody, integrity, retention, contradictions, and falsifiers.

Until all applicable evidence is supplied and intake verification passes, RP-001 remains **Open / 0 Complete**.

## HARD HOLD / prohibited zones

- No Board Promote, readiness-floor change, or Eng soft-queue ingest.
- No Const/BP or `docs/knowledge/**` modification.
- No Kernel/API/UI/product code change and no product CRUD opening.
- No Brain execute, Twin authorize, Role/Capability→grant, or acceptance-on-behalf.
- No Legacy record correction, reconciliation posting, shipment release, AR adjustment, or payment action.
- No Terminal demo may be relabeled as a live reconciliation capture.

## Explicit non-claims

This file is an observation design, **not Complete** and **not Eng soft-queue ingest**. It records what a future authorized capture must observe/score/hold; it authorizes no execution.
