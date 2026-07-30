# Command Authorization Deepen — INDEX

**Verified:** 2026-07-23  
**Legacy root:** `H:\Workspace\EZAM_CRM - 9.0\`

## Module Index

| Module | Evidence | Primary locus | Main conclusion |
|---|---|---|---|
| [server_route_coverage.md](server_route_coverage.md) | Strong | domain routers/services | sensitive writes range from strong Type A to unguarded commands |
| [object_tenant_scope.md](object_tenant_scope.md) | Strong | repositories/tenant helper | module permission and list filters do not ensure object/tenant scope |
| [get_mutation_surface.md](get_mutation_surface.md) | Strong | GET route inventory/CSRF | GET writes are cross-domain and structurally bypass CSRF |
| [audited_override.md](audited_override.md) | Strong | checker/audit/Brand | central privileged bypass is not an audited override |

## Cross-pack Map

| This pack | Authority referenced | Relationship |
|---|---|---|
| all modules | `../permission-surface-deepen/` | deepens route opt-in, admin bypass and UI/server mismatch |
| coverage/GET | `../risk-catalog/permission_holes.md` | operational matrix for PH-001–008 |
| GET Complete/Reopen | `../ship-complete-deepen/do_complete.md`, `do_reopen.md` | reuses authoritative lifecycle facts |
| tenant scope | `../platform-obs/identity_obs.md` | applies observed tenant dual-read semantics |
| override | `../permission-surface-deepen/admin_bypass_matrix.md` | separates privileged allow from audited override |

## Command Authorization Dimensions

| Dimension | Legacy posture |
|---|---|
| Principal | absent on request-less routes |
| Module/action RBAC | per-handler/service opt-in |
| Object owner | inconsistent; list filters do not propagate |
| Tenant | opt-in dual-read helper |
| Source state | strong on selected Type A/Delivery actions |
| Intent | Human Confirm selected; browser confirm otherwise |
| CSRF | global unsafe-method coverage; GET excluded |
| Idempotency | selected business guards only |
| Audit | command-specific; bypass not marked |
| Override | role-string short-circuit, generally unaudited |

## Critical Conclusions

1. Server route coverage must be evaluated per command, not per module/menu.
2. Object and tenant authorization must be embedded in repository reads/writes; a passed module permission is insufficient.
3. GET mutation is an authorization-intent defect even when role and state checks exist.
4. An audit record can document an action while the action remains unauthorized.
5. Privileged bypass, no-gate access and explicit audited override are three different semantics.
6. EAOS command enforcement must default-deny before domain side effects and produce a durable decision/audit context.

## Coverage Check

| File | Rules | Validations | Data semantics | Evidence rows | UNKNOWN rows | Result |
|---|---:|---:|---:|---:|---:|---|
| `server_route_coverage.md` | 25 | 12 | 16 | 28 | 11 | PASS |
| `object_tenant_scope.md` | 23 | 12 | 18 | 26 | 11 | PASS |
| `get_mutation_surface.md` | 22 | 12 | 18 | 28 | 11 | PASS |
| `audited_override.md` | 25 | 12 | 20 | 25 | 9 | PASS |

Required threshold (“同 A”): rules ≥8, validations ≥6, data semantics ≥8, evidence rows ≥6, UNKNOWN+searched paths ≥5.

## Read-only Source Families

- `core/{permission,auth,security,database,runtime}/**`
- `apps/{approval,quotation,sales,inventory,finance,customer,product,supplier,procurement,sample,platform,tenant_center}/**`
- `v15/enterprise_branding/**`
- `templates/**`
- `bootstrap/**`
- `database/**`
- `docs/reports/**`

## Write Boundary

Only `docs/knowledge/legacy-extract/command-authz-deepen/**` is created or modified by Phase-17.
