# Enterprise DNA Model

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-002-EDNA  
**Program:** RP-002 Enterprise DNA  
**Version:** 1.0  
**Status:** Research Draft  
**Reviewer:** 臻宇（peer Pass — WP Draft Allowed）  
**Approval:** Pending — WP content Acceptance separate  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**White Paper:** [WHITE_PAPER-RP-002.md](WHITE_PAPER-RP-002.md) （Draft）  
**Upstream:** [RP-001 EDF §3.2](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
**Consumers:** RP-007 EEM (constraint features); RP-005 (scale limits)

---

## Abstract

The Enterprise DNA Model (EDNA) deepens RP-001’s eight DNA axes into a measurable, versioned constraint vector. DNA predicts **which evolution paths are plausible**, not which software to buy. DNA is never an authorization input and never grants Permission.

## 1. Design Principles

1. **Stable ≠ frozen** — DNA refreshes on a slow cadence; not quarterly vanity scores.  
2. **Constraint, not culture quiz** — axes must constrain REC-* advice.  
3. **Orthogonal enough** — axes may correlate but must not collapse to one “maturity” score.  
4. **Evidence-linked** — each axis score cites dossier evidence tiers.  
5. **Non-authorizing** — DNA must not feed Runtime grants or Twin authorize.  
6. **Discovery-first** — DNA records attach to Discovery Dossiers (RP-001).  
7. **Falsifiable** — instability across retest invalidates predictive claims.  
8. **Dual-Track safe** — research construct until promoted.

## 2. Axis Catalog (Canonical Eight)

| Axis ID | Name | Question | Score Band (research) | High-Score Constraint Example |
|---------|------|----------|-----------------------|-------------------------------|
| DX-01 | Decision Gravity | Where do consequential decisions settle? | Centralized ↔ Distributed | High central → Hold swarm autonomy |
| DX-02 | Exception Density | How often standard process fails? | Low ↔ Extreme | High → Hold naive REC-AUTO/Agentize |
| DX-03 | Formality Preference | Rules vs improvisation? | Improvisational ↔ Highly formal | High formality → tolerate rigid workflow |
| DX-04 | Knowledge Stickiness | Dependence on key persons? | Low ↔ Extreme | High → Cap AI workforce scale (RP-005) |
| DX-05 | Asset Intensity | Capex / physical ops weight? | Light ↔ Heavy | Heavy → robot paths need RC5 case |
| DX-06 | Compliance Reflex | Default posture to controls? | Permissive ↔ Strict | Strict → heavier approval design |
| DX-07 | Partner Embeddedness | Ecosystem dependence? | Low ↔ High | High → Marketplace/package caution |
| DX-08 | Change Absorption | History absorbing platform change? | Fragile ↔ Proven | Low → raise REC-HOLD pressure |

**Scoring:** Ordinal `1–5` plus narrative + evidence refs + confidence. No single composite “DNA IQ.”

## 3. Measurement Method (Wave 2 Research)

| Step | Activity | Output |
|------|----------|--------|
| 1 | Seed from RP-001 DNA workshop | Axis draft scores |
| 2 | Evidence tagging (T1–T3) | Per-axis evidence log |
| 3 | Dual-rater pass (target) | Inter-rater notes |
| 4 | Constraint translation | REC-* veto/hold hints for RP-007 |
| 5 | Retest at +90 days (pilot) | Stability deltas |

### 3.1 Anti-Patterns

| Anti-Pattern | Reject |
|--------------|--------|
| Personality quiz without ops evidence | Yes |
| Using DNA as promotion/HR score | Yes |
| Collapsing eight axes to one maturity number | Yes |
| Feeding DNA into Permission evaluate | Yes |
| Claiming T3 stability from one synthetic pass | Yes |

## 4. Record Schema (Conceptual)

```text
dna_record_version:
enterprise_ref: (dossier_id)
as_of:
rater_ids: []
axes:
  - axis_id: DX-0N
    score: 1..5
    narrative:
    evidence_refs: []
    confidence: low|medium|high
constraint_hints: [{rec_class, hold|prefer|caution, rationale}]
retest_of: (optional prior dna_record_version)
```

## 5. Linkage to Wave 1

| Wave 1 Artifact | DNA Use |
|-----------------|---------|
| WT-01 SynMfg-Alpha | High DX-02/DX-04; Compliance strong (DX-06) |
| WT-02 SynSvc-Beta | High DX-03/DX-04/DX-07; license theater stress |
| WT-03 S2 vs S5 | DX-08 differs (untested vs proven absorption) |
| RI-01 / RI-02 | Stickiness & Exception Density bound fusion |
| EEM TT-01…03 | HOLD/Robot defer explainable via DNA constraints |

## 6. Validation Rules (Program-Specific Draft)

| ID | Rule |
|----|------|
| V-DNA-01 | All eight axes defined with score bands + constraint examples |
| V-DNA-02 | Explicit non-authorization (not Permission/Twin input) |
| V-DNA-03 | Measurement method includes retest plan |
| V-DNA-04 | Linkage to RP-001 dossiers and RP-007 constraint hints |
| V-DNA-05 | Falsifiers include instability and culture-quiz collapse |

## 7. Falsifiers

1. Axes fail test-retest beyond agreed delta.  
2. Facilitators cannot distinguish DNA from Growth Stage theater.  
3. Constraint hints do not change RP-007 HOLD rates vs no-DNA baseline.  
4. Enterprises weaponize DNA for HR discrimination.  
5. Orthogonal claim fails (all axes move in lockstep always).

## 8. Cross-Layer Impact (Potential)

| Layer | Impact |
|-------|--------|
| Twin/Brain | Advisory constraint features later |
| Kernel | Descriptive metadata only — never authz |
| Terminal | Facilitator worksheets |
| Marketplace | Industry DNA baselines later |
| Constitution/Blueprint | Candidates only; no edits now |

## 9. Promotion Stance

Current: **Research Draft v1.0**  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
Scorecards: **SC-01…03 Synthetic Complete** — [scorecards/](scorecards/)  
Industry/Risk: **Draft** — [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) · [RISK_ANALYSIS.md](RISK_ANALYSIS.md)  
Peer **臻宇** Pass recorded; White Paper Draft open — [WHITE_PAPER-RP-002.md](WHITE_PAPER-RP-002.md).  
WP content Acceptance still Pending. Architecture Review only after Dual-Track Architecture path. Remain Asset OK.  
Do **not** use DNA as authorization input.

## Related Documents

- [RP-002 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables](DELIVERABLES-RP-002.md)  
- [Scorecards](scorecards/README.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [Risk Analysis](RISK_ANALYSIS.md)  
- [Peer Review Package](PEER_REVIEW_PACKAGE.md)  
- [EDF](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
- [EEM](../RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md)  
