# RP-006 Tax / FX / Approval Field Card

**Program:** AI Infrastructure Platform  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) · [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD **platform / infra surfaces** that host or expose **税票 · FX · 审批** paths—API gateways, schedulers, document engines, currency services, and approval hubs—without treating platform availability as tax-invoice, FX revaluation, or Approval Center completeness. Themes: **税票主账缺席**, **AR/打印分离**, **FX 不传播 / 无重估**, **Approval Center vs V18**, **GET 审批**. Knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`.

## Tax / FX / approval observation points (RP-006 lens)

1. **Document/NDE platform ≠ 税票主账:** print/render pipelines that emit Invoice PDFs without a tax-invoice store.
2. **AR API vs print API separation:** platform routes that share “invoice” naming across Post AR and NDE print.
3. **Currency service ≠ FX platform:** seed/static rates, missing effective-dated FX API, no Convert propagation hooks.
4. **Scheduler ≠ revaluation job:** generic queue/scheduler docs without FX revalue task definitions or GL postings.
5. **Approval Center hub hosting ≠ business hooks:** platform center runtime not consumed by Quote/SO/Convert/Ship Type A confirms.
6. **GET mutation surfaces on infra routes:** approve/reject/confirm via GET bypassing CSRF/unsafe-method semantics.
7. **Platform health ≠ tax/FX/approval Complete:** green checks on currency/tax/approval modules without lifecycle evidence.
8. **Brain/Twin / platform fence:** infra telemetry or Twin mirrors must not authorize tax release, FX revalue, or approve.

## Scoring / HOLD

- Score platform route/schema presence vs business lifecycle completeness; separate hosting from authority.
- Dossier API method, idempotency, and dual-name (“invoice”) collisions.
- HOLD when platform uptime or OpenAPI tags are presented as tax-invoice / FX / Approval Center live evidence.

## Required live evidence

1. Authorized redacted route/OpenAPI/schema inventory for invoice/tax, currency/FX, and approval endpoints with methods.
2. Evidence that NDE/print and Post AR hit distinct stores/effects (or documenting illegal coupling).
3. FX rate source interface evidence (effective dating) and Convert/SO/AR propagation traces—or attested gaps.
4. Scheduler/job inventory proving presence/absence of revaluation; Approval Center hook inventory vs V18 confirms.
5. GET vs POST mutation inventory for approve/confirm-adjacent platform routes.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-006 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, platform config, Kernel/API/UI, gateway, scheduler, or code change.
3. No Brain execute, Twin authorize, product CRUD, tax/FX posting, approve execution, or infra write probes that mutate business state.
4. No synthetic platform dump relabeled as live tax/FX/approval evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no platform change, tax, FX, or approval action.
