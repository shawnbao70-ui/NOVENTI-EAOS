# RP-008 Dry-Run Protocol

**Mode:** synthetic  
**Tier:** T1 only  
**Registry effect:** none — RP-008 remains **Open**  

Purpose: rehearse a plant-overlay walkthrough without entering a site or touching OT/MES. Apply the [live/synthetic fence](../../../templates/LIVE_VS_SYNTHETIC_FENCE.md).

## Desktop exercise

1. Allocate `DR-YYYYMMDD-RP-008-##`; role-play plant, safety, OT, and observer functions.
2. Generate a fictitious cell/line, event flow, Human/AI/Robot/Device duties, and PR0–PR4 risks.
3. Apply SF-01…08 and inject safety vetoes, degraded/offline conditions, and exception events.
4. Rehearse source-backed OEE/quality/maintenance calculations using generated metrics.
5. Test observation stop rules and safety escalation as tabletop actions only.
6. Verify no MES kernelization, machine command, production connection, or Brain control.
7. Close as `Dry-run closed — T1` with gaps and owners.

## Fake-data boundary

- Use invented plants, workers, equipment, recipes, events, incidents, and performance values.
- No production photo, historian/MES export, OT topology, safety case, credential, or identifiable worker data.
- Mark all diagrams and logs `SYNTHETIC / NOT LIVE EVIDENCE`.

## Prohibited outcome

No tabletop walkthrough may be marked Complete or upgraded because a real engineer/safety specialist participated.

## Exit conditions

- SF/risk, safety-stop, degraded-mode, and no-control boundaries were rehearsed.
- Any real plant/OT evidence triggers stop/isolation and a separately approved LC process.
- Registry remains **0 Complete** and RP-008 remains **Open**.
