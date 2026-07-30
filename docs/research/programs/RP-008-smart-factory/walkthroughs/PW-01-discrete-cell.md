# PW-01 — Discrete Cell Overlay

**Research ID:** NRI-RP-008-PW-01  
**Program:** RP-008  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Enterprise ref:** SynMfg-Alpha discrete cell (WT-01 class)  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**Dossier hint:** [WT-01](../../RP-001-enterprise-discovery/walkthroughs/WT-01-mid-mfg-synthetic.md)  
**As Of:** 2026-07-21 · **Facilitator:** NRI-desk (synthetic)

---

## Record

```text
plant_overlay_version: syn-pw01-1.0
enterprise_ref: SynMfg-Alpha discrete-cell
as_of: 2026-07-21
cell_type: discrete_guarded
mes_kernelization: never
machine_control_from_brain: never
execution_authority: none
robot_without_safety_case: defect
```

## 1. Domain Scores (Research)

| Domain | Band / Note | Confidence | Gap? |
|--------|-------------|------------|------|
| SF-01 Plant Cap Overlay | Cap IDs CAP-OTS/QC/CHG usable; dept labels rejected | medium | Partial |
| SF-02 H/AI/R/D Mix | Human + assistive AI; robot proposed | medium | Partial |
| SF-03 Physical Risk | PR0→PR2 claim without completed safety case | high | **Yes — critical** |
| SF-04 Line-side Terminal | HQ tablet forced on line; glanceability poor | medium | **Yes** |
| SF-05 OT/Historian | Historian used as “knowledge truth” pressure | medium | **Yes** |
| SF-06 Robot Readiness | REC-ROBOT pressure; EEM HOLD not yet satisfied | high | **Yes — critical** |
| SF-07 Degraded Mode | Undefined if cloud link drops | medium | **Yes** |
| SF-08 Package Scope | Unsigned “cell AI” pack discussed | medium | **Yes** |

**Portfolio read:** Do **not** leave HOLD on REC-ROBOT until SF-03 ≥ PR2 with case + SF-06 readiness. Cap overlay OK; safety theater fails C-SF-02.

## 2. Cap Overlay Sketch (from CFM)

| capability_id | Cell outcome | PR hint | EEM hint |
|---------------|--------------|---------|----------|
| CAP-CHG | Changeover within takt | PR1 sim OK | HOLD Agentize (affinity A0) |
| CAP-QC | Containment | PR1 | Prefer Assist |
| CAP-OTS | Ship complete | — | Stabilize before robot scale |

## 3. Safety / Robot Checklist

| Check | Result |
|-------|--------|
| Safety case documented for proposed cell robot | **Missing** |
| PR band assigned before REC-ROBOT | Required — currently PR0 theater |
| Brain OEE insight may recommend HOLD | Allowed |
| Brain may command robot motion | **Forbidden** |
| MES scheduling logic in Core Kernel | **Forbidden** |

## 4. Hard Boundaries

`mes_kernelization: never`. `machine_control_from_brain: never`. `execution_authority: none`. Research Only.
