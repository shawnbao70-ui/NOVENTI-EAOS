# RP-008 Interview Plan

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Participants/interviewers assigned:** none  
**Protocol:** [INTERVIEW_PROTOCOL](../../../templates/INTERVIEW_PROTOCOL.md) · **Log:** [OBSERVATION_LOG](../../../templates/OBSERVATION_LOG.md)

## Purpose

Explain plant duties, safety/approval boundaries, OT events, degraded modes, and source-backed operational claims without distracting workers or requesting control access.

## Interviewee roles

1. Plant/process representative or cell owner.
2. Frontline operator/technician participating voluntarily.
3. Authorized safety stakeholder.
4. OT/MES/historian or terminal custodian.
5. Quality/maintenance/OEE evidence owner.

## Core questions

1. Walk through the last representative production/quality/maintenance event in scope.
2. Which duties belong to Human, AI, Robot, and Device actors at each step?
3. Which safety approvals, vetoes, and stop authorities govern the event?
4. How do terminal/OT/MES interactions behave in normal and degraded/offline modes?
5. Which workarounds, alarms, exceptions, or manual records occur?
6. How are OEE/quality/maintenance values calculated and contextualized by shift/product?
7. What prevents Brain/recommendation output from directly controlling machines?
8. How are incidents/near misses reported without retaliation or evidence loss?
9. What evidence would falsify claimed performance or safety improvement?
10. Which redacted safety, event, metric, and approval records can be reviewed?

## Taboo questions

1. Do not ask workers to reveal unsafe shortcuts, incidents, or individual performance outside protected procedures.
2. Do not request OT credentials, commands, vulnerabilities, recipes, or unrestricted production data.
3. Do not interview during unsafe/critical tasks or pressure continued participation.
4. Do not ask anyone to bypass safety, alter MES/machines, or approve Brain control.

## Output mapping

1. Event narrative → process/event observation timeline.
2. Actor-duty answers → Human/AI/Robot/Device matrix.
3. Safety answers → approval/veto/stop artifact map.
4. Degraded/workaround answers → exception and resilience log.
5. Metric answers → source/calculation/denominator trace.
6. Falsifier/reviewable-record answers → custody requests and gap updates.

## Bias and follow-up

Include frontline and safety perspectives, not only management/vendor narratives. Record observer effect, shift/product context, fear of retaliation, and unavailable incident evidence.

## Cross-reference and non-claim

- Plant safety/observation plan: [SITE_PLAN](SITE_PLAN.md)
- OT/worker/artifact custody: [CUSTODY_PLAN](CUSTODY_PLAN.md)
- Site/system permissions: [FIELD_KIT](FIELD_KIT.md)

RP-008 remains Open. Interviews alone do not establish plant evidence, machine authority, Complete, floor change, Promote, Eng work, or Const/BP change.
