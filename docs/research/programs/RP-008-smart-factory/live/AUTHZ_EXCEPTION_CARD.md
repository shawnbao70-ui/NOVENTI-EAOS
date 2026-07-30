# RP-008 Authorization Exception Card

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Observe, score, and HOLD authorization exceptions spanning enterprise, plant, warehouse, device, operator, integration, and safety contexts. Observation must not send commands to production or operational technology.

## Authorization / bypass observation points

1. Distinguish enterprise, plant, warehouse, line, machine, device, and operator scopes.
2. Observe authorization for inventory, receiving, shipment, adjustment, quality, and production-adjacent intents.
3. Trace shared terminals, kiosk sessions, device identities, service accounts, and shift handovers.
4. Record maintenance, vendor-support, emergency, safety, and offline-mode bypass procedures.
5. Compare HMI/UI visibility and physical access with server, gateway, and device command authorization.
6. Observe network loss, stale session, cached role, replay, duplicate command, and reconciliation handling.
7. Capture denial, safe-state behavior, alarm, audit actor, override expiry, and post-event review.

## Scoring / HOLD

- Score principal/device identity, site scope, safety gate, command locus, override custody, and fail-safe outcome.
- Dossier IT and OT facts separately, including clocks and custody boundaries.
- HOLD whenever physical presence, visible controls, or a shared terminal is treated as authorization.

## Required live evidence

1. Authorized redacted identity-and-scope map for sampled IT/OT actors and devices.
2. Allow/deny decision traces from non-invasive existing logs for relevant commands.
3. Shared-terminal, shift-handover, device credential, and session-lifecycle artifacts.
4. Maintenance/vendor/emergency/offline override procedure with real review records, or documented absence.
5. Safe-state, alarm, audit, replay/idempotency, and no-side-effect denial evidence.
6. Site custodian corroboration, safety approval, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-008 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, operational opening, or Eng ingest.
2. No Const/BP, `docs/knowledge/**`, OT/IT configuration, Identity, gateway, API/UI, or code change.
3. No Brain execute, Twin authorize, CRUD, machine/device command, credential use, safety bypass, or penetration test.
4. No synthetic factory trace relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no plant, warehouse, device, machine, safety, or production action.
