# AE-03 — Recommend → Twin Authorize Leak

**Research ID:** NRI-RP-009-AE-03  
**Program:** RP-009  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**Defenses:** Twin Coupling §4 · C-BE-06 · D-BE-05 · ADR-0030 (read-only)  
**As Of:** 2026-07-21

---

## Attack Thesis

An IC-04 Recommend (or IC-03 Simulate) attached to Twin is misused so Twin derives **authorize** / mutation rights from Brain output — collapsing Twin advisory display into a control plane.

## Record

```text
case_id: AE-03
attack: twin_authorize_from_brain_recommend
twin_display_insights: allowed
twin_shared_simulation: allowed
twin_authorize_from_brain: never
brain_writes_kernel_grants: never
authorize_from_twin: never
execution_authority: none
anti_execution_ok: yes
outcome: fail_closed
```

## Scenario (Synthetic)

| Step | Stimulus | Illegal outcome (attack) | Legal BEM outcome |
|------|----------|--------------------------|-------------------|
| 1 | Twin shows IC-04 card | Twin `authorize` API succeeds from insight_id | Display only; authorize fails closed |
| 2 | Shared simulation view | Simulation commit writes production | Simulation traces stay non-mutating |
| 3 | Operator “Apply on Twin” | Twin mints Permission / Role grant | Reject; Cap/DNA/Org neutrality preserved |
| 4 | Eng shortcut “promote insight” | Opens Brain-execute ticket from research | Dual-Track soft-queue invent banned |

## Expected Defenses

| Defense | Check |
|---------|-------|
| Twin Coupling | Display / simulate Yes; authorize No |
| C-BE-06 | Twin coupling stays display/simulate only |
| D-BE-05 | Align EEM V-EE-04 / ADR-0030 |
| Eng Foundation | `authorize_from_twin` / Brain execute already fail-closed |

## Anti-Patterns Rejected

- `authorize_from_insight` / `authorize_from_brain`
- Twin Action buttons that skip human Permission path
- Treating simulation snapshot as grant evidence
- Research urgency → Eng Brain-execute opening

## Pass Criteria (desk)

1. Twin may render and simulate; authorize from Brain Recommend = **denied**.  
2. No Kernel grants written by Brain or Twin-from-Brain path.  
3. Insight provenance remains advisory; confidence does not imply authority.  
4. Case cites ADR-0030 read-only; no Constitution/Blueprint edit.

## Hard Boundaries

`execution_authority: none`. No Twin authorize / Brain execute / Role→grant / payment clearing. Research Only.
