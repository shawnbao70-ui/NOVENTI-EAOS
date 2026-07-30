# T2 / T3 Evidence Intake & Live Capture Board

**Document ID:** NRI-T2-T3-INTAKE  
**Version:** 1.1  
**Status:** Active standing intake board (docs-only; **not** live evidence)  
**Last Updated:** 2026-07-24  
**Milestone:** PHX-G163  
**Authority:** Research Track deepen under AED v1.1 / DAL-G003 + DAL-G004（**DAL-U034**）  
**Governing:** [RESEARCH_GOVERNANCE_CHARTER.md](RESEARCH_GOVERNANCE_CHARTER.md) · [RESEARCH_VALIDATION_RULES.md](RESEARCH_VALIDATION_RULES.md) · [RESEARCH_PROMOTION_RULES.md](RESEARCH_PROMOTION_RULES.md) · [DUAL_TRACK_GOVERNANCE.md](../project/DUAL_TRACK_GOVERNANCE.md) · [AUTONOMOUS_EXECUTION_DIRECTIVE.md](../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)  
**Companion:** [T2_T3_EVIDENCE_READINESS.md](T2_T3_EVIDENCE_READINESS.md)（**NRI-T2-T3-EVID**；floors）  
**Observation aid (≠ evidence):** [Sample knowledge pack](../knowledge/sample-pack/)（PHX-G293）— docs-only CRM→Delivery assembly for walkthrough framing; **does not** count as live T2/T3 Complete.

> **Honesty first.** This board prepares the **capture path** for live T2/T3.  
> Current inventory: **0 / 10** programs have registered live T2 or T3 **Complete** artifacts.  
> Intake / readiness ≠ live plant/executive evidence ≠ Board re-Promote ≠ Eng ingest.  
> Do **not** invent field/tenant dossiers or silently bump floors.  
> Sample knowledge pack (G293) is an observation aid only — never relabel as T2/T3 Complete.

---

## Purpose

After PHX-G155 (criteria + T1 floors) and PHX-G159 (Board Hold×10), the gated resume「继续Live T2/T3 证据升档」needs an operational **intake & verification path** — without claiming Completes that do not exist.

This board:

1. Distinguishes **T2 vs T3** bars for capture (normative for intake).  
2. Provides an **intake checklist** + [capture template](templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md).  
3. Holds a **Live Capture Registry** (status honesty).  
4. Defines the **verification gate** before any Current-floor flip on NRI-T2-T3-EVID.

**Does not** collect fake walkthroughs, invent observers, or promote packages.

---

## Aggregate honesty (as of 2026-07-23)

| Claim | Value |
|-------|-------|
| Programs with live T2 Complete | **0 / 10** |
| Programs with live T3 Complete | **0 / 10** |
| Current floors (RP-001…010) | All **T1** per [NRI-T2-T3-EVID](T2_T3_EVIDENCE_READINESS.md) |
| Board stance (AR) | **Hold×10**（PHX-G159）— Hold ≠ Promote ≠ Eng ingest |
| Repo inventory of live artifacts | **None found** under Evidence Packs (synthetic Complete only) |

---

## T2 vs T3 capture bar (intake normative)

| Dimension | **T2** (controlled pilot) | **T3** (production / multi-site / executive-attested) |
|-----------|---------------------------|------------------------------------------------------|
| Site / cohort | Named site, tenant, or controlled cohort | Production tenant **or** ≥2 sites **or** executive-attested operation |
| Window | Dated observation window (start/end or as_of) | Dated window + retention/provenance note |
| Observer | Named observer identity (real person; standing peer ok if present) | Named observer **plus** independent attestation or second witness preferred |
| Artifacts | Linked from program `EVIDENCE_PACK.md` with paths that exist | Same + retention path / export handle recorded |
| Mode label | `mode: live` and tier **T2** explicit | `mode: live` and tier **T3** explicit |
| Synthetic | Must **not** relabel synthetic as T2 | Must **not** relabel T1/T2 synthetic as T3 |
| Fail-closed | Brain execute / Twin authorize / Cap≠grant / Const/BP rewrite remain closed | Same |
| Eng / Board | Tier upgrade ≠ Board Promote ≠ Eng soft-queue ingest | Same |

**Minimum for any Complete row:** all cells in the chosen tier column must hold, and the verification checklist (§ Verification) must pass.

---

## Intake checklist (before filing a capture)

Use for every candidate live artifact. Copy into the [capture template](templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md).

| # | Check | Pass? |
|---|-------|-------|
| I1 | Target RP ID in RP-001…010 | |
| I2 | Claimed tier is **T2** or **T3** (not T1 synthetic) | |
| I3 | Named site/tenant/cohort recorded | |
| I4 | Dated observation window recorded | |
| I5 | Observer identity recorded (no invented peers) | |
| I6 | Repository artifact path(s) resolve; each external handle has custodian, access check, and retention location | |
| I7 | `mode: live` (or equivalent) on the artifact | |
| I8 | Program invariants preserved (program-specific; see pack) | |
| I9 | No Brain execute / Twin authorize / Cap→grant / Const rewrite implied | |
| I10 | Submitter affirms: **not** a relabel of synthetic Input Freeze alone | |

If any of I1–I10 fail → **do not** register Complete; leave registry **Open** or **Rejected-incomplete**.

---

## Verification checklist (before floor flip)

NRI-T2-T3-EVID **Current floor** may flip for one RP only through the two-phase transaction below. Phase A evaluates evidence without changing either board; Phase B commits the paired registry/floor records.

| # | Gate | Required |
|---|------|----------|
| V1 | **Phase A:** Intake I1–I10 and claimed-tier qualification Pass for ≥1 live artifact | Yes |
| V2 | **Phase A:** Capture instance, artifact manifest, resolvable evidence, and Evidence Pack link verified | Yes |
| V5 | **Phase A:** DAL Usage Log row for the tier-upgrade exercise identified/recorded | Yes |
| V6 | **Phase A:** **No** silent Board re-Promote; **no** Eng invent from tier alone | Yes |
| V7 | **Phase A:** Package / Alembic and Const/BP posture unchanged unless separately authorized | Yes |
| V3 | **Phase B:** Registry row → **Complete** with capture ID, tier, verification date, and references | Yes |
| V4 | **Phase B:** Readiness Change Log append + floor cell update for that RP only | Yes |

**Forbidden:** marking Complete from paper criteria alone; inventing observer names; claiming T3 from a single synthetic re-label.

V3 and V4 are commit confirmations, not prerequisites for Phase A. They must be applied as one registration transaction. If only one edit lands, revert it or visibly mark both records pending correction; never leave a Complete/floor mismatch.

---

## Live Capture Registry

Status values:

- **Open** — no real candidate registered; planning/readiness alone stays Open.
- **In-progress** — a real Capture ID exists, but required metadata/artifacts or verification are incomplete.
- **Complete** — registrar verified live evidence and completed V3+V4; submitters cannot self-assign it.
- **Rejected-incomplete** — a submitted candidate failed one or more gates; reasons and decision trail are retained.

An RP row summarizes the highest registered state for that program. Multiple candidates are distinguished in the Candidate Submission Register below; one rejected candidate does not erase another in-progress candidate.

| RP | Program | Target wave hint | Live T2 | Live T3 | Status | Artifact paths |
|----|---------|------------------|---------|---------|--------|----------------|
| RP-001 | Enterprise Discovery | Wave 1 | — | — | **Open** | none |
| RP-002 | Enterprise DNA | Wave 2 | — | — | **Open** | none |
| RP-003 | Capability First | Wave 2 | — | — | **Open** | none |
| RP-004 | Organization Neutrality | Wave 2 | — | — | **Open** | none |
| RP-005 | AI Workforce | Wave 1 | — | — | **Open** | none |
| RP-006 | AI Infrastructure | Wave 3 | — | — | **Open** | none |
| RP-007 | Evolution Engine | Wave 1 | — | — | **Open** | none |
| RP-008 | Smart Factory | Wave 3 | — | — | **Open** | none |
| RP-009 | Brain Evolution | Wave 2 | — | — | **Open** | none |
| RP-010 | Future EOM | Wave 3 | — | — | **Open** | none |

**Aggregate:** **0 Complete** · **10 Open** · **0 In-progress**.

Wave hint is scheduling guidance only; sponsors/Board own field work. This board does not invent site visits.

---

## Candidate Submission Register

Append a row only after a real Capture ID and real operating context are supplied. Do not add placeholders for hoped-for visits. Artifact references may be repository paths or non-secret external handles; restricted payloads remain in their controlled source.

| Capture ID | RP | Claimed tier | Operating context | Window / as_of | Observer | Capture form | Artifact IDs / handles | Submitted (UTC) | Registrar | Decision | Decision date | Missing gates / notes |
|------------|----|--------------|-------------------|----------------|----------|--------------|------------------------|-----------------|-----------|----------|---------------|-----------------------|
| _No real submissions registered_ | — | — | — | — | — | — | — | — | — | — | — | — |

Allowed Decision values are **In-progress**, **Verified-Complete**, and **Rejected-incomplete**. The italic sentinel row is not evidence and is replaced only when a real submission arrives.

### Registration rules

1. Allocate `LC-YYYYMMDD-RP-00N-##`; copy the template under that RP’s `live/` directory. A copied form starts **Draft**.
2. Change the candidate to **In-progress** only when its Capture ID, named operating context, observation date/window, observer, and at least one real artifact reference exist.
3. Before submission, complete tier qualification, artifact manifest, observations, gaps/exceptions, and submitter attestations. Missing required fields remain visible.
4. On **Submitted**, append/update exactly one candidate row and record immutable references where available (hash, export ID, version, or a reason none applies).
5. Registrar checks identity/context, temporal fit, artifact accessibility, provenance/retention, tier bar, program invariants, and synthetic/live separation. Accessibility at registration time is required; a bare URL is insufficient.
6. Failed Phase A becomes **Rejected-incomplete** or returns to **In-progress**, with failed gates recorded. Resubmission preserves the prior decision trail.
7. After Phase A Pass, commit V3+V4 together: set the RP summary and candidate to Complete/Verified-Complete, then flip only that RP’s readiness floor and append both Change Logs.
8. Do not copy secrets, personal data, tenant payloads, or restricted raw exports into repository Markdown. Register metadata, redaction state, custodian, and controlled retrieval handle instead.

### T3-specific registration note

T3 includes all T2 requirements plus production/multi-site/executive-attested context and retention/provenance. Record which T3 route applies. Executive attestation is supporting evidence, not a substitute for dated operational artifacts; any witness exception must be explicit and registrar-reviewed.

---

## How to register a future Complete (process)

1. Run intake checklist; create a Capture ID and fill [LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md).  
2. Register repository artifacts or controlled external handles in the manifest; record provenance, custodian, retention, access, and redaction.  
3. Update program `EVIDENCE_PACK.md` with honest tier + capture/artifact links.  
4. Append/update the Candidate Submission Register; keep it **In-progress** until Phase A passes.  
5. Record the DAL Usage Log row and registrar preflight result.  
6. Commit V3+V4 together: registry/candidate Complete plus that RP’s readiness floor and both Change Logs.  
7. Do **not** treat the tier registration as Board Promote or Eng ingest.

---

## Hard non-outcomes

- Claim T2/T3 Complete without registered live artifacts  
- Relabel synthetic WT/RI/GP/TT/PW/AE/SA instances as live  
- Self-certify Architecture Review Board re-Promote from intake alone  
- Open Eng soft-queue from Research tip / tier upgrade alone  
- Brain execute / Twin authorize / Cap→grant / MES Kernel fork / Const rewrite  
- Invent unknown peer / observer names  
- Eng Explicit Defer `4` payment clearing  
- Collide with concurrent Eng numbered slices (WebAuthn / Role→grant) by rewriting product code in this milestone  

---

## Authority

| Field | Value |
|-------|-------|
| Grant | **DAL-G003** + **DAL-G004**（through 2026-07-27；AED v1.1） |
| Usage | **DAL-U034**（PHX-G163） |
| Package / Alembic | Stay `0.2.1` / `0029`（docs-only；no product opening） |
| ID note | Eng occupies PHX-G161/G162；Research intake uses **PHX-G163** |

---

## Pointers

| Doc | Role |
|-----|------|
| [T2_T3_EVIDENCE_READINESS.md](T2_T3_EVIDENCE_READINESS.md) | Floor inventory（NRI-T2-T3-EVID） |
| [templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) | Per-capture intake form |
| [ARCHITECTURE_REVIEW_BOARD_QUEUE.md](ARCHITECTURE_REVIEW_BOARD_QUEUE.md) | AR Board Hold×10 |
| [GENERATION2_TIP_BOARD.md](GENERATION2_TIP_BOARD.md) | Research tip |
| [../project/ENG_SOFT_QUEUE_TIP.md](../project/ENG_SOFT_QUEUE_TIP.md) | Engineering tip（separate） |
| [../project/PHX-G163_ACCEPTANCE.md](../project/PHX-G163_ACCEPTANCE.md) | This milestone Acceptance |
| Sample pack | [RP-001 EVIDENCE_PACK](programs/RP-001-enterprise-discovery/EVIDENCE_PACK.md)（T1 synthetic；live planned） |

---

## Next steps (after this milestone)

1. Sponsors schedule real Wave-1 live captures（RP-001 / 005 / 007 preferred）using the template.  
2. On first verified artifact: run verification checklist → registry Complete → readiness floor flip for that RP only.  
3. Board may revisit Hold after honest T2/T3 Completes — **separate** from Eng ingest.  
4. Eng product invent remains on its own gates（mint-PO / Promote+ADR / Eng `4` PO）.

---

## Change Log

| Date | Note |
|------|------|
| 2026-07-23 | Phase-19 / D — added `live/TAX_FX_APPROVAL_FIELD_CARD.md` for RP-001…010 covering 税票主账缺席、AR/打印分离、FX 不传播/无重估、Approval Center vs V18、GET 审批；≥6 RP-lens observation points、≥5 live-evidence requirements、≥3 HARD HOLDs each；knowledge mapped as hypotheses only；no live evidence fabricated；all cards ≠ Complete / ≠ Eng soft-queue ingest；aggregate **0 Complete**；no Promote / floor / Const-BP / knowledge / code / Brain-Twin / product CRUD change |
| 2026-07-23 | Phase-18 / D — added `live/APPROVAL_BOUNDARY_CARD.md` for RP-001…010 covering V18 Human Confirm vs Approval Center、Approve≠Convert、GET confirm、multi-step gaps、Brain/Twin fences；≥6 RP-lens observation points、≥5 live-evidence requirements、≥3 HARD HOLDs each；knowledge mapped as hypotheses only；no live evidence fabricated；all cards ≠ Complete / ≠ Eng soft-queue ingest；aggregate **0 Complete**；no Promote / floor / Const-BP / knowledge / code / Brain-Twin / product CRUD change |
| 2026-07-23 | Phase-17 / D — added `live/AUTHZ_EXCEPTION_CARD.md` for RP-001…010 with ≥6 authorization/bypass observation points, ≥5 live-evidence requirements, and ≥3 HARD HOLDs each；no access attempt, bypass, observer, or live evidence fabricated；all cards ≠ Complete / ≠ Eng ingest；aggregate **0 Complete**；no Promote / floor / Const-BP / knowledge / code / Brain-Twin / product CRUD change |
| 2026-07-23 | Phase-16 / D — added `live/NUMBERING_CUSTODY_CARD.md` for RP-001…010 to observe/score/HOLD document-number identity, uniqueness, collision disposition, and authority-vs-display custody；maps read-only to numbering-collision-deepen；knowledge unchanged；all cards ≠ Complete / ≠ Eng ingest；aggregate **0 Complete**；no Promote / floor / code / Brain-Twin / product CRUD change |
| 2026-07-23 | Phase-15 / D — added `live/DUAL_WRITE_FIELD_CARD.md` for RP-001…010 to observe/score/HOLD dual-write and parallel facts (inventory mirrors, Receipt vs AR, status drift, ghost Ship after Reopen, numbering collisions)；knowledge unchanged；all cards ≠ Complete / ≠ Eng ingest；aggregate **0 Complete**；no Promote / floor / code / Brain-Twin / product CRUD change |
| 2026-07-23 | Phase-14 / D — added `live/EXCEPTION_PATH_CARD.md` for RP-001…010 covering empty-line Convert, SO without TC, Reopen without inventory impact, Receipt≠AR, dual-write drift, missing reconciliation, and negative paths；knowledge conclusions remain hypotheses and `docs/knowledge/**` unchanged；all cards explicitly ≠ Complete / ≠ Eng soft-queue ingest；all rows **Open**；aggregate **0 Complete**；no Promote / floor / code / Brain-Twin / product CRUD change |
| 2026-07-23 | Phase-13 / D — added `live/RECONCILE_FIELD_CARD.md` for RP-001…010 with ≥5 minimum field artifacts, ≥4 reconciliation questions, and ≥3 HARD HOLDs each；no live evidence/observers fabricated；all cards explicitly ≠ Complete / ≠ Eng ingest；all rows **Open**；aggregate **0 Complete**；no Promote / floor / knowledge / Const/BP / code change |
| 2026-07-23 | Phase-12 / D — added `live/RECONCILE_SCENARIO.md` for RP-001…010 to observe/score/HOLD parallel SO/DO/inventory/Receipt/AR facts, drift, dual-write, missing reconciliation, and exception paths；no live evidence fabricated；all scenarios explicitly ≠ Complete / ≠ Eng soft-queue ingest；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP / knowledge / Kernel/API/UI/product CRUD change；Brain execute / Twin authorize remain closed |
| 2026-07-23 | Phase-11 / D — added research-only [EAOS_REWRITE_CANDIDATE](templates/EAOS_REWRITE_CANDIDATE.md), [TERMINAL_DEMO_GAP](templates/TERMINAL_DEMO_GAP.md), and tailored `live/REWRITE_NOTE.md` for RP-001…010 with ≥4 RP mappings, ≥3 rewrite candidates, ≥3 HARD HOLDs, ≥4 live-evidence needs, and CHAIN_SCENARIO cross-link each；no live evidence fabricated；no product/Smart Terminal/package or knowledge/Const/BP modification；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng change |
| 2026-07-23 | Phase-10 / D — added full [COMMERCIAL_CHAIN_OBSERVATION](templates/COMMERCIAL_CHAIN_OBSERVATION.md), research-only [TERMINAL_SCENARIO_CARD](templates/TERMINAL_SCENARIO_CARD.md), and tailored `live/CHAIN_SCENARIO.md` for RP-001…010 with ≥6 chain observations, ≥4 RP mappings, ≥3 HARD HOLDs, ≥5 artifacts, and SITE_PLAN/INTERVIEW_PLAN cross-links each；no live evidence/observers fabricated；Brain execute / Twin authorize remain closed；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP change |
| 2026-07-23 | Phase-9 / D — added full [INTERVIEW_PROTOCOL](templates/INTERVIEW_PROTOCOL.md), [OBSERVATION_LOG](templates/OBSERVATION_LOG.md), and tailored `live/INTERVIEW_PLAN.md` for RP-001…010 with ≥4 interviewee roles, ≥8 core questions, ≥3 taboo questions, ≥5 output mappings, and SITE_PLAN/CUSTODY_PLAN cross-links each；no interviewees/observers invented；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP change |
| 2026-07-23 | Phase-8 / D — added full [DATA_MINIMIZATION_PACK](templates/DATA_MINIMIZATION_PACK.md), [CHAIN_OF_CUSTODY](templates/CHAIN_OF_CUSTODY.md), and tailored `live/CUSTODY_PLAN.md` for RP-001…010 with ≥5 custody nodes, ≥4 roles, ≥3 retention rules, ≥3 leakage responses, and SITE_PLAN/FIELD_KIT cross-links each；no observers invented；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP change |
| 2026-07-23 | Phase-7 / D — added full [SITE_ACCESS_PACK](templates/SITE_ACCESS_PACK.md), T2/T3 [ARTIFACT_ACCEPTANCE_RUBRIC](templates/ARTIFACT_ACCEPTANCE_RUBRIC.md), and tailored `live/SITE_PLAN.md` for RP-001…010 with ≥6 observations, ≥6 artifacts, ≥4 dependencies, ≥4 risks/ethics items, and ≥3 exits each；no observers invented；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP change |
| 2026-07-23 | Phase-6 / D — added [FIELD_CAPTURE_KIT](templates/FIELD_CAPTURE_KIT.md) and tailored `live/FIELD_KIT.md` for RP-001…010 covering who / when / system-context / artifacts / permissions；kits are preparation only；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP change |
| 2026-07-23 | Phase-5 / D — added [T2_T3_EVIDENCE_GAP_MATRIX](T2_T3_EVIDENCE_GAP_MATRIX.md) and per-RP `live/GAP.md` for RP-001…010；all lack registered live artifacts, real observers, and authorized contexts；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP change |
| 2026-07-23 | Phase-4 / D — RP-001…010 each received `live/DRY_RUN_PROTOCOL.md`; added [LIVE_VS_SYNTHETIC_FENCE](templates/LIVE_VS_SYNTHETIC_FENCE.md) to keep dry runs **T1 synthetic** and prohibit relabeling；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP change |
| 2026-07-23 | Phase-3 / D — RP-001…010 each received `live/OBSERVER_CHECKLIST.md` covering observer roles, access, minimum artifacts, and ethics/confidentiality；observers remain unassigned until real participation；all rows **Open**；aggregate **0 Complete**；no floor / Promote / Eng / Const/BP change |
| 2026-07-23 | Phase-2 / D — RP-001…010 each received `live/README.md` capture-preparation guidance；all ten registry rows remain **Open**；aggregate remains **0 Complete**；no observer invented, no readiness-floor flip, Board Promote, Eng invent, or Const/BP change |
| 2026-07-23 | Intake deepen — capture lifecycle, tier qualification, artifact manifest, candidate register, and two-phase V3/V4 commit added；still **0 Complete**；no floor upgrade / Promote / Eng invent |
| 2026-07-22 | NRI-T2-T3-INTAKE opened — intake + verification path；**0 Complete** honesty；no floor upgrade（PHX-G163 / DAL-U034） |

**END OF NRI-T2-T3-INTAKE**
