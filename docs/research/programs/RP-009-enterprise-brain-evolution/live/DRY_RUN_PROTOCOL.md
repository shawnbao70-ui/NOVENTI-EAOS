# RP-009 Dry-Run Protocol

**Mode:** synthetic  
**Tier:** T1 only  
**Registry effect:** none — RP-009 remains **Open**  

Purpose: rehearse advisory insight and anti-execution verification without live dossiers or production tools. Apply the [live/synthetic fence](../../../templates/LIVE_VS_SYNTHETIC_FENCE.md).

## Desktop exercise

1. Allocate `DR-YYYYMMDD-RP-009-##`; participants role-play domain, provenance, and boundary observers.
2. Generate a fictitious dossier with contradictory sources, confidence gaps, and simulated decisions.
3. Run Describe → Diagnose → Simulate → Recommend → Learn, never Act.
4. Build a synthetic claim-to-source graph and score explanation/decision quality.
5. Inject requests for mutating tools, workflow commit, grant, Twin authorization, and acceptance-on-behalf.
6. Verify every prohibited request fails closed and simulated side-effect count is zero.
7. Close as `Dry-run closed — T1` with adverse results and gaps retained.

## Fake-data boundary

- Use generated dossiers, sources, model outputs, tool calls, audits, and decisions.
- No production prompt/log, tenant data, credentials, real tool endpoint, personal data, or proprietary model artifact.
- Label all outputs `SYNTHETIC / NOT LIVE EVIDENCE`.

## Prohibited outcome

Passing synthetic anti-execution tests cannot be marked Complete or represented as proof of live/production behavior.

## Exit conditions

- Provenance, uncertainty, adverse-result, and `execution_authority: none` paths were exercised.
- Real data or reachable production tooling triggers immediate stop/isolation and separate authorized LC handling.
- Registry remains **0 Complete** and RP-009 remains **Open**.
