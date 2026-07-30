# TT-03 — Robot Path Held on Safety / Exception Density

**Research ID:** NRI-RP-007-TT-03  
**Program:** RP-007  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**Inputs:** WT-01 · RI-02 · INPUT_FREEZE

---

## Record

```text
test_id: TT-03
inputs: {rp001_ref: WT-01 SynMfg-Alpha, rp005_ref: RI-02}
triggers_fired: [T-ROBOT-opportunity-partial, T-HOLD-04-adjacent, T-HOLD-safety]
recs:
  - class: REC-HOLD
    statement: Do not scale unsupervised robot cells on changeover-heavy lines; keep vision/inspection assist only.
    execution_authority: none
    human_owner_role: Plant Manager + EHS Officer
  - class: REC-AI
    statement: Allow assistive SPC/vision advise under Quality Release human sign-off.
    execution_authority: none
    human_owner_role: Quality Release Authority
  - class: REC-ROBOT
    statement: Defer new robotized changeover cells until Exception Density and certified RC5 path improve.
    execution_authority: none
    human_owner_role: Process Owner
    vetoes: [uncertified RC5, interlock bypass]
hold_present: yes
explainable_from_evidence: yes
anti_execution_ok: yes
```

## Evidence Refs

| Ref | Finding |
|-----|---------|
| WT-01 DNA | High Exception Density on changeovers; Knowledge Stickiness |
| WT-01 Potential | Moderate — compliance helps; stickiness caps scale |
| RI-02 | Unsupervised robot without interlocks **Refuse**; AI interlock bypass **Refuse** |

## Expected Outcome Class

Dominant **REC-HOLD** + deferred **REC-ROBOT** (not “deploy now”).  
Positive path limited to assistive inspection (REC-AI), not physical autonomy expansion.

## Hard Boundaries

Safety path remains human/certified. No Twin authorize / Brain execute.
