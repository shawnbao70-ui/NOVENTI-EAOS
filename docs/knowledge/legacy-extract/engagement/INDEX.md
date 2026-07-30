# Engagement Knowledge Extract — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| Marketing | [marketing.md](marketing.md) | Medium: distributor master strong; campaign/send loop weak | `apps/marketing/`, `v15/marketing/`, `/marketing_center` |
| Brand Center | [brand.md](brand.md) | Strong for Legacy profile/edit/upload; medium for document propagation | `apps/brand_center/`, `v15/enterprise_branding/`, `document/` |
| Service | [service.md](service.md) | Weak: planned API scaffold and shadow object; operational closure absent | `apps/service/`, `core/object360/technical_service/` |
| AI Advisory | [ai_advisory.md](ai_advisory.md) | Strong for metadata/static advisory boundaries; mixed for per-object heuristics | `apps/ai_decision_center/`, `core/ai_decision/`, AI templates |

## Cross-module map

| From | To | Observable meaning |
|------|----|--------------------|
| Marketing | Distributor | Partner/channel master maintenance is the strongest operational marketing path |
| Marketing | Customer / Communication | Hub navigates to CRM and communication workspaces; no automatic lead conversion is proven |
| Brand | Documents | Active Legacy brand profile can supply company identity, logos and QR choices to document context |
| Brand | Marketing | Social/contact fields are brand metadata; they do not establish connected campaign channels |
| Service | Customer / Product | TechnicalService360 declares associations, but active source joins and write workflows are incomplete |
| AI Advisory | Business workspaces | Advice may explain or navigate; business mutation remains owned by the target module and human controls |

## Critical honesty findings

1. `campaigns` has a schema and read API, but the Marketing hub deliberately reports zero live campaigns/leads and offers no production campaign CRUD/send engine.
2. Brand Center has two non-equivalent stores. Runtime HTML/edit/upload uses `brand_profiles`; the V15.1 registry tables are additive and disabled by default.
3. Service has no confirmed active ticket creation, assignment, SLA, escalation, warranty or closure workflow.
4. `/ai_decision_center` displays hard-coded scores/suggestions, while V15.1 decision registries persist `implemented=0` / `metadata_only`.
5. Advisory output never implies authority to execute business actions, authorize a digital twin, or grant capability.
