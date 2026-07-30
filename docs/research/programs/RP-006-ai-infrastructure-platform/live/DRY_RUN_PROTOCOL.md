# RP-006 Dry-Run Protocol

**Mode:** synthetic  
**Tier:** T1 only  
**Registry effect:** none — RP-006 remains **Open**  

Purpose: rehearse AI-infrastructure readiness assessment without access to a live environment. Apply the [live/synthetic fence](../../../templates/LIVE_VS_SYNTHETIC_FENCE.md).

## Desktop exercise

1. Allocate `DR-YYYYMMDD-RP-006-##`; use unassigned role labels.
2. Generate a fictitious cloud/hybrid topology, identity model, tool/model chain, approval bridge, and telemetry set.
3. Score ID-01…08 against I0–I4 and trace every result to generated fixtures.
4. Inject isolation, provenance, degraded-mode, audit, cost, and OT/edge gaps.
5. Rehearse unavailable-evidence handling without treating absence as control failure.
6. Verify no active probing, production access, Kernel bypass, or configuration action is implied.
7. Close as `Dry-run closed — T1` with gaps and owners.

## Fake-data boundary

- Use non-routable hosts, fake tenants/accounts, generated logs, and dummy identifiers/secrets.
- Never copy real topology, credentials, keys, vulnerabilities, model artifacts, logs, or security reports.
- Mark diagrams and profiles `SYNTHETIC / NOT LIVE EVIDENCE`.

## Prohibited outcome

No readiness score or simulated control record may be marked Complete or upgraded to T2/T3 through review or technical realism.

## Exit conditions

- Scoring, evidence availability, security disclosure, and fail-closed boundaries were rehearsed.
- Discovery of real security/environment data triggers stop, isolation, and approved handling before any separate LC intake.
- Registry remains **0 Complete** and RP-006 remains **Open**.
