# RP-006 Interview Plan

**Program:** AI Infrastructure Platform  
**Status:** **Open** · **0 Complete**  
**Participants/interviewers assigned:** none  
**Protocol:** [INTERVIEW_PROTOCOL](../../../templates/INTERVIEW_PROTOCOL.md) · **Log:** [OBSERVATION_LOG](../../../templates/OBSERVATION_LOG.md)

## Purpose

Locate operational evidence and explain AI-infrastructure controls/gaps across ID-01…08 without requesting secrets, active probing, or configuration change.

## Interviewee roles

1. Environment/platform owner or custodian.
2. Identity/security/governance representative.
3. AI Runtime/model/tool platform operator.
4. Observability/SRE/FinOps representative.
5. OT/edge specialist where hybrid/plant scope applies.

## Core questions

1. Walk through a recent model/tool request from identity to execution/audit.
2. How are tenant isolation and least privilege established and evidenced?
3. Where do approval bridges fail closed, and what logs prove it?
4. How are model/tool versions, signatures, provenance, and revocation handled?
5. Which observability records connect request, decision, tool, cost, failure, and owner?
6. How are data/memory retention, deletion, and region constraints enforced?
7. What happens during edge/OT disconnection, degraded mode, or service failure?
8. Which known gap reflects missing evidence versus a failed control?
9. What would falsify the current readiness-band assessment?
10. Which redacted exports/IDs can a registrar review without exposing secrets or vulnerabilities?

## Taboo questions

1. Do not ask for passwords, keys, tokens, vulnerability exploitation, or detailed unrestricted topology.
2. Do not request active scans, production commands, test traffic, or configuration changes.
3. Do not ask respondents to approve operational readiness, deployment, or Eng work.
4. Do not imply infrastructure access bypasses Kernel, Permission, Workflow, or AI Runtime.

## Output mapping

1. Request-path answers → topology/control-flow trace.
2. Identity/isolation answers → criterion/source evidence map.
3. Approval/audit answers → fail-closed artifact request.
4. Supply-chain answers → model/tool provenance record.
5. Degraded-mode/gap answers → readiness gap and falsifier log.
6. Safe-export answers → custody manifest and registrar retrieval test.

## Bias and follow-up

Balance platform owners with security, operators, and users of evidence. Treat confidence claims as statements until matched to redacted logs/configuration/registry evidence.

## Cross-reference and non-claim

- Environment observation/stop rules: [SITE_PLAN](SITE_PLAN.md)
- Security-sensitive custody: [CUSTODY_PLAN](CUSTODY_PLAN.md)
- Minimum access/artifact fields: [FIELD_KIT](FIELD_KIT.md)

RP-006 remains Open. Interviews alone do not approve infrastructure, mark Complete, flip a floor, Promote, create Eng work, alter packages, or change Const/BP.
