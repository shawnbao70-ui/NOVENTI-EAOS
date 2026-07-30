# RP-007 Interview Plan

**Program:** Enterprise Evolution Engine  
**Status:** **Open** · **0 Complete**  
**Participants/interviewers assigned:** none  
**Protocol:** [INTERVIEW_PROTOCOL](../../../templates/INTERVIEW_PROTOCOL.md) · **Log:** [OBSERVATION_LOG](../../../templates/OBSERVATION_LOG.md)

## Purpose

Understand trigger reasoning, recommendation usefulness, HOLD behavior, simulation limits, and human decisions while preserving `execution_authority=none`.

## Interviewee roles

1. Enterprise decision representative who reviewed recommendations.
2. Dossier/source owner supplying frozen inputs.
3. Evolution analysis/facilitation role.
4. Independent usefulness scorer or challenge reviewer.
5. Boundary/audit representative verifying zero side effects.

## Core questions

1. Walk through the last evaluation from frozen input to human decision.
2. Which evidence and thresholds triggered each recommendation or HOLD?
3. Which counter-evidence or freshness gap changed the outcome?
4. How did explanation/simulation communicate assumptions and uncertainty?
5. Which recommendation was accepted, deferred, rejected, or returned for evidence, and why?
6. Describe a should-HOLD case and any pressure to recommend action.
7. How was usefulness compared with the declared checklist baseline?
8. What systems/tools were reachable, and how was zero execution verified?
9. What outcome evidence would falsify or recalibrate the recommendation?
10. Which frozen inputs, ledgers, simulations, decisions, and audits are retrievable?

## Taboo questions

1. Do not ask participants to execute, approve, or accept recommendations on behalf of others.
2. Do not solicit confidential strategy/workforce data beyond approved minimum.
3. Do not frame HOLD, dissent, defer, or rejection as failure.
4. Do not ask interview responses to authorize Brain execute, Twin authorize, grants, or Eng work.

## Output mapping

1. Evaluation narrative → dated recommendation lifecycle log.
2. Trigger/counter-evidence answers → trigger-source/falsifier matrix.
3. Simulation answers → assumptions/limitations artifact map.
4. Human decision answers → immutable accept/defer/reject/HOLD record.
5. Usefulness answers → blind scoring evidence.
6. Reachability/audit answers → zero-side-effect custody request.

## Bias and follow-up

Interview decision reviewers separately from recommendation authors; preserve should-HOLD and rejected cases. Validate recollection against immutable input, ledger, decision, and audit artifacts.

## Cross-reference and non-claim

- Advisory observation/exit rules: [SITE_PLAN](SITE_PLAN.md)
- Dossier/ledger/audit custody: [CUSTODY_PLAN](CUSTODY_PLAN.md)
- Required fields/permissions: [FIELD_KIT](FIELD_KIT.md)

RP-007 remains Open. Interviews alone never create execution authority, Complete, floor change, Promote, Eng work, or Const/BP change.
