# RP-001 Reconciliation Field Card

**Program:** Enterprise Discovery  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Scenario:** [RECONCILE_SCENARIO](RECONCILE_SCENARIO.md)

## Field objective

Capture the minimum evidence needed to discover and dossier parallel SO/DO/inventory/Receipt/AR facts, drift, dual-write, missing reconciliation, and exception paths—without changing any record.

## Minimum field artifacts

1. Tokenized SO extract/handle with state, version, lines, owner, and source timestamp.
2. DO/shipment extract/handle with SO linkage, partial/release/cancel state, and audit event.
3. Inventory views for on-hand/available/allocated/in-transit with location and `as_of`.
4. Receipt/proof/discrepancy record with quantity, condition, timestamp, and source owner.
5. AR/invoice/payment-allocation state with currency, due/settled/disputed status.
6. Reconciliation/勾兑 run, exception queue, tolerance, owner, cadence, and sign-off evidence.
7. Chain ID/version/time correlation plus custody, minimization, and integrity record.

## Reconciliation questions

1. Which system/source owns each fact, and where is that authority documented?
2. Which versions/timestamps disagree, and is the difference expected lag, error, or unknown?
3. Where does manual/dual-write activity bypass traceable reconciliation?
4. What happens to partial, cancelled, refused, returned, disputed, or unapplied paths?
5. Which missing artifact forces Discovery Score/Dossier into HOLD?

## HARD HOLD

1. No evidence access/consent, stable IDs, version/time basis, or custodian → stop.
2. No SO/DO/inventory/Receipt/AR create/update/delete, release, acceptance, posting, or payment.
3. No Promote, floor flip, Eng ingest, Brain execute, Twin authorize, or product CRUD.
4. No `docs/knowledge/**`, Const/BP, Kernel/API/UI, or other code modification.

## Non-claim

This field card **≠ Complete** and **≠ Eng ingest**. Blank/unverified fields preserve RP-001 as Open; no live evidence is asserted.
