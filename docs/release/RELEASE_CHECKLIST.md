# Foundation `0.2.5` Release Checklist

**Version:** 0.2.5  
**Prior Foundation baseline:** `0.2.4`（PHX-G461；historical `0.2.3` / G404）  
**Train:** PHX-G509 · Batches M→T G464–G511

---

## Pre-cut

- [ ] `docs/release/RELEASE_MANIFEST.yaml` version = package version (`0.2.5`)
- [ ] Alembic head matches Manifest (`0092_finance_realized_fx_gl_bridge_g372`)
- [ ] Manifest `milestones` includes PHX-G145…G164 as `fully_accepted` when documenting current Foundation tip
- [ ] All OpenAPI paths in Manifest exist and parse as OpenAPI 3.1
- [ ] `eaos_sdk` imports cleanly
- [ ] `api.adapters` catalog equals Manifest openapi list
- [ ] Inventory posture：`route_mount_parity_complete=true`；`full_openapi_http_complete=false`（PHX-G164）
- [ ] Required PR contracts green within ≤10 min：`python scripts/run_contract_shard.py pr_required`（PHX-G408）
- [ ] Full `pytest tests/contracts` green on nightly / parallel（publish DURATION_SECONDS；do not hide latency）
- [ ] `pytest tests/integration` green (dedicated PostgreSQL)
- [ ] Marketplace external PSP capture / external arbitration still fail-closed（G162 opens internal record only）
- [ ] WebAuthn ceremony default → 503；live mint only when `EAOS_WEBAUTHN_REGISTRATION_ENABLED` + RP（PHX-G160；`attestation_crypto_verified=false`）
- [ ] Role→grant default → 503；live mint only when `EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED` + map（PHX-G161；Cap≠grant）
- [ ] Payment clearing default → 503；internal record only when env ON（PHX-G162；≠ external PSP）
- [ ] Brain execute / Twin authorize remain fail-closed
- [ ] `docs/release/PRODUCTION_TOPOLOGY.md` present (PHX-G49 single-host baseline)
- [ ] Operations runbook includes production start + topology link + G151/G154/G156/G157/G160/G161/G164 fences
- [ ] Compatibility policy notes Foundation baseline `0.2.5` at tip `0092`（G509 cut；prior `0.2.4` / G461）
- [ ] `docs/release/V2_0_READINESS_CHECKLIST.md` present（PHX-G405；readiness only；≠ V2.0 package cut）
- [ ] `deploy/docker/compose.yaml` + `docs/release/COMPOSE.md` present (PHX-G50)
- [ ] `deploy/helm/eaos` + `docs/release/HELM.md` present (PHX-G51)
- [ ] Ingress template + `docs/release/INGRESS.md` present (PHX-G52)
- [ ] HPA template + `docs/release/HPA.md` present (PHX-G53)
- [ ] VPA template + `docs/release/VPA.md` present (PHX-G54)
- [ ] Seven-step review completed in relevant Acceptance docs（at least `PHX-G144_ACCEPTANCE.md`；current tip `PHX-G160_ACCEPTANCE.md` / `PHX-G164_ACCEPTANCE.md` as applicable）
- [ ] Deploy region docs present (`docs/release/REGION.md`, PHX-G76) when using `region.id` / `EAOS_DEPLOY_REGION`
- [ ] Explicit non-goals reviewed (external PSP payment capture / multi-region SaaS failover / public registry / Compose-K8s / WebAuthn attestation crypto / always-on Role→grant or payment clearing or WebAuthn mint without env / Brain execute / Twin authorize / full OpenAPI semantic parity)
- [ ] Human branch-protection evidence recorded (`BRANCH_PROTECTION.md`)
- [ ] Candidate revision has green CI `docker-smoke` history
- [ ] Fresh `integration_critical` green on dedicated `eaos_test*` PostgreSQL
- [ ] `PRODUCTION_GO_DECISION_G469.md` records GO (current Batch M decision is **NO-GO**)
