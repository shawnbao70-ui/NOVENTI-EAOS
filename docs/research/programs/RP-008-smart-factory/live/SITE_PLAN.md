# RP-008 Site Plan

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Assigned observer/plant/window:** none / none / none  
**Access basis:** [SITE_ACCESS_PACK](../../../templates/SITE_ACCESS_PACK.md) · **Evidence review:** [ARTIFACT_ACCEPTANCE_RUBRIC](../../../templates/ARTIFACT_ACCEPTANCE_RUBRIC.md)

## Objective and boundary

Observe SF-01…08 and PR0–PR4 in a named plant/cell without interfering with production, safety, OT, MES, or machine control. Smart Factory remains an overlay, not a Kernel fork.

## Target observation points

1. Human/AI/Robot/Device duties and handoffs are observable at the selected cell/line.
2. Physical risks, safety vetoes, stop authority, and residual human responsibility are explicit.
3. Line-side terminal interactions support approvals and degraded/offline operation.
4. OT events cross IT/OT boundaries with source, timestamp, and failure handling.
5. OEE/quality/maintenance claims trace to authorized metrics and calculation rules.
6. Exceptions, manual workarounds, alarm burden, and shadow automation are recorded safely.
7. Simulation/approval precedes any proposed line or robot change.
8. No Brain insight or recommendation reaches direct machine command.

## Required artifacts

1. Dated plant/cell/shift scope, induction, escort, and walkthrough record.
2. SF-01…08 domain and PR0–PR4 risk assessment.
3. Process/event-flow map and Human/AI/Robot/Device duty matrix.
4. Safety case, approval, veto, stop, and incident/near-miss references.
5. Terminal, degraded/offline, and reconnection observations.
6. Redacted OT/MES/historian event references.
7. Source-backed OEE/quality/maintenance extracts and calculation notes.
8. Provenance, integrity, access, retention, redaction, gaps, and falsifier manifest.

## Dependency systems / contexts

1. Plant safety management/permit and incident context.
2. MES or production execution reference, read-only only.
3. Historian/SCADA/OT event source under supervised access.
4. Line-side terminal/HMI context.
5. Quality/maintenance/OEE source systems.
6. Robot/device controller context by observation only, no command access.

## Access and run sequence

1. Complete induction, PPE, escort, zone, shift, recording, OT, and stop-rule approvals.
2. Confirm observer remains outside control loops and production tasks.
3. Observe normal/degraded conditions only as safely available; never induce faults.
4. Exit zone, revoke access, reconcile artifacts, and report safety/security concerns locally.

## Risks / ethics

1. Injury or production disruption; safety authority may stop immediately.
2. Worker surveillance/performance attribution; avoid identities and individual evaluation.
3. OT topology/vulnerability/recipe leakage; keep controlled and minimized.
4. Observation affecting operator attention or work sequence; use escort-approved positioning.
5. Metrics misread without shift/product context; preserve denominator and calculation notes.
6. Research advice becoming machine command or MES change; fail closed.

## Exit conditions

1. Stop on any safety instruction, alarm, incident, near miss, escort loss, or zone violation.
2. Stop if observation/export could affect production, OT availability, machine state, or operator attention.
3. Stop if consent/access/recording permission is absent or revoked.
4. Return incomplete if safety, event, metric, or provenance evidence cannot be handled safely.
5. RP-008 remains Open; a plant visit or rubric score alone never marks Complete.
