# 项目状态

**计划：** Project Phoenix  
**产品：** NOVENTI EAOS  
**仓库：** `NOVENTI-EAOS`  
**最后更新：** 2026-07-29

---

## 当前状态

**Eng tip（authoritative）：** Foundation package **`0.2.5`** · Alembic **`0092_finance_realized_fx_gl_bridge_g372`** · Batches M→T COMPLETE · CRM UI **G512–G525 COMPLETE**（through Return Authorization）· **FINAL STOP TRACK-G525**. Production remains **NO-GO** pending G469 evidence.

**Gate governance：** [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md) / [Phoenix Gate Framework](PHOENIX_GATE_FRAMEWORK.md) is the sole formal Gate standard. Framework Redesign **Approve** 2026-07-29 (process only). **Standing Coding Authorization Approved** 2026-07-29 for Gate-Accepted Business Packages — see [PHOENIX_GATE_STANDING_CODING_AUTHORIZATION.md](PHOENIX_GATE_STANDING_CODING_AUTHORIZATION.md). Architecture changes still require Decision Summary → Approve/Amend/Reject. Sequencing: next free contiguous PHX-G; queue empty until PO names next slice after G518.

**Historical tip freeze（not current）：** PHX-G293 Sample Knowledge Pack（ADR-0319；then package `0.2.1` / Alembic `0029`）— retained as history only.

**Prior tip：** PHX-G292 Delivery knowledge（DAL-U165）· PHX-G291 Finance · PHX-G290 CRM+Sales · PHX-G163 T2/T3 intake（0 Complete）

**Research context：** AED v1.1；AR Board **Hold** — [ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md)；T2/T3 floors **T1** — [T2_T3_EVIDENCE_READINESS.md](../research/T2_T3_EVIDENCE_READINESS.md)；intake — [T2_T3_EVIDENCE_INTAKE.md](../research/T2_T3_EVIDENCE_INTAKE.md)（PHX-G163；**0 Complete**）；HARD HOLDS：Brain/Twin/external PSP — [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md)  
**Layout：** `packages/*` = declarations；`noventi/*` = runtime — [RUNTIME_PACKAGE_LAYOUT.md](RUNTIME_PACKAGE_LAYOUT.md)


### 实现进展

| 组件 | 状态 |
|------|------|
| `kernel/shared` | 已实现（上下文/错误码/结果/审计） |
| `kernel/identity` | Session / Credential / Governor / Assignment / AI Profile 持久化已实现 |
| `kernel/organization` | Tenant / Enterprise / Unit / Membership 完整 L0–L2、并发与 PostgreSQL 门禁已通过 |
| `kernel/permission` | Policy / Scope / Delegation / Explain 完整 L0–L2、PostgreSQL 门禁已通过 |
| `kernel/workflow` | 定义版本 / 绑定 / SLA / 升级 / 补偿完整门禁已通过 |
| `eaos_platform/knowledge` | Entity / Link / Provenance / Retention / 授权检索已通过 |
| `kernel/event_bus` | Outbox / Lease / Retry / DLQ / Stats + Webhook（E21）+ HMAC（E22）已通过 |
| Persistence Ports | Repository / AuditLog / Unit of Work Protocol 已实现 |
| SQL Foundation | metadata / Alembic / Shared Audit + Identity 映射已实现 |
| SQL Unit of Work | Engine / Session Factory 与事务生命周期已实现 |
| SQL Repositories | Shared Audit / Identity 租户绑定适配器已实现 |
| Transactional Identity | Command + Repository + Audit 单事务接线已实现 |
| Identity Governance | Platform Identity Governor 显式授权已实现 |
| Transactional Organization | ORM + Repository + Audit 单事务接线已实现 |
| Transactional Permission | Grant / Decision + Audit 单事务接线已实现 |
| Transactional Workflow | State + Permission Decision + Audit 共享事务已实现 |
| Transactional Knowledge | Entity / Link / Provenance + Permission + Audit 共享事务已实现 |
| Transactional Event Bus | Outbox / Dispatch / DLQ / Stats + Permission + Audit 共享事务已实现 |
| Runtime Foundation | Inbound / Propagation / Snapshot / Executor / Observability 已实现 |
| `runtime/ai` | Agent Run / Tool / Memory / Approval Bridge 完整门禁已通过 |
| Transactional AI Runtime | Run / Tool / Memory + Workflow + Permission 共享事务已实现 |
| `smart_terminal` | Session / Intent / Preview / Approval + Complete UI + Extension Host（G39/G41–G44 SQL/iframe/Worker/CSP/验签）+ OIDC Login Product（G147）+ OIDC Bearer/Refresh/Logout（G40/G61）+ MFA/WebAuthn 产品姿态（G145）+ IdP Admin 探针/注册表薄操作（G55/G62）+ 声明角色 Admin（G91）+ 租户角色目录只读（G92）+ 角色状态探针（G93）+ permission evaluate（G94）+ effective-permissions 只读探针（G95）+ permission policy/grant 手工写入（G128）+ deprecate/delegate（G129；≠ Role→grant）+ Role→grant 产品姿态（G146）+ JWT/denylist 状态探针（G96）+ Event Bus 完整薄运维面（G97–G100）+ Marketplace 状态/listing/生命周期/技术 acquire 薄探针（G101–G103）+ Marketplace Foundation 商业薄探针（G141；pricing/invoice/dispute/revenue-share；支付清算 fail-closed）+ Workflow Terminal 运维面齐（G104–G107）+ Package Terminal 运维面齐（G108–G109）+ Knowledge Terminal 运维面齐（G110–G112）+ Twin Terminal 运维面齐（G113–G114；authorize fail-closed）+ Brain Terminal 运维面齐（G115–G116；execute fail-closed）+ AI Runtime Terminal 运维面齐（G117–G119；commit 无审批 fail-closed）+ Identity Terminal 运维面齐（G120–G121/G137–G138；含 credential/session revoke 与 AI/governor）+ Organization Terminal 运维面齐（G122–G127；含 enterprise / platform tenant lifecycle）已通过 |
| Transactional Smart Terminal | Workspace + Workflow + Permission 共享事务已实现 |
| `eaos_platform.package` | Manifest / Install / Surface·Action 完整门禁已通过 |
| Transactional Package | Manifest / Install + Permission 共享事务已实现 |
| `eaos_platform.twin` | Twin Snapshot / provenance / confidence 完整门禁已通过 |
| `eaos_platform.brain` | Advisory Insight；执行路径恒拒绝 |
| Transactional Twin / Brain | Twin + Brain + Permission 共享事务已实现 |
| `eaos_platform.marketplace` | 技术生命周期 + Foundation 商业 + 包签名密码学（M18）已通过 |
| Transactional Marketplace | Listing / Acquisition + Permission 共享事务已实现 |
| `eaos_sdk` / `api.adapters` | Release Train SDK 与契约适配目录已交付 |
| `api/gateway` | FastAPI 网关；G20–G48/G55–G57/G60–G63 + M17–M18（含 `/terminal/` + Extension CSP/验签 + 多发行方 JWKS/denylist/JWT + OIDC refresh/logout memory|sql + IdP registry memory|sql + Discovery/JWKS wire/registry write） |
| Domain Event Catalog | K07–K10 同事务 outbox 接线（含 DecisionRecorded / E20） |
| Release Manifest / Ops | Compat + Runbook + Checklist + 拓扑/Compose/Helm/Ingress/HPA/VPA/KEDA/Mesh+PA/VS/DR/Authz（G49–G54/G58–G59/G71–G73）已交付 |
| 跨域契约 | Organization ↔ Permission、Workflow ↔ Permission |
| Identity ↔ Organization L2 | Membership Eligibility + AI 改派共享事务已实现 |
| Identity API Contract | OpenAPI 3.1 + 状态机规范已实现 |
| Constitution Convergence | BOOK00–22 首轮审查、BOOK19/22 收敛、AI taxonomy 完成 |
| Smart Terminal Constitution | BOOK23 与首版 Blueprint 已生成 |
| 契约测试 | **781 passed**；PostgreSQL 集成需本地实例（Alembic `0029`） |
| FastAPI | 已以可选 extra `api` 引入最小网关（PHX-G18） |
| 遗留仓库 | 未改动 |

### 运行

```bash
cd H:\Workspace\NOVENTI-EAOS
pip install -e ".[dev,persistence,api]"
pytest
```

## 里程碑清单

| ID | 里程碑 | 状态 |
|----|--------|------|
| PHX-000～003 | 仓库/宪法/蓝图/标准 | **完成** |
| PHX-004 | Kernel Foundation | **完成** |
| PHX-005 | Runtime Foundation | **完成** |
| PHX-006 | Identity Kernel（完整） | **完成（人工批准）** |
| PHX-G01 | Constitutional Convergence | **完成** |
| PHX-G02 | Smart Terminal Constitution | **完成；二次审查 Fully Compliant** |
| PHX-A03 | Architecture Realignment | **完成；唯一 ownership 门禁通过** |
| PHX-K07 | Organization Kernel | **完成；Fully Accepted** |
| PHX-K08 | Permission Kernel | **完成；Fully Accepted** |
| PHX-K09 | Workflow Kernel | **完成；Fully Accepted** |
| PHX-K10 | Knowledge Shared Capability | **完成；Fully Accepted** |
| PHX-P11 | Platform Runtime & Event | **完成；Fully Accepted** |
| PHX-A12 | AI Runtime & Agent | **完成；Fully Accepted** |
| PHX-T13 | Smart Terminal Foundation | **完成；Fully Accepted** |
| PHX-B14 | Business Package Platform | **完成；Fully Accepted** |
| PHX-E15 | Enterprise Brain & Twin | **完成；Fully Accepted** |
| PHX-M16 | Marketplace Technical Foundation | **技术完成；商业/法律门禁仍开放** |
| PHX-R17 | EAOS Release Train | **完成；Fully Accepted（Foundation 0.2.0；carried by 0.2.1）** |
| PHX-G18 | API Gateway Foundation | **完成；Fully Accepted** |
| PHX-E19 | Domain Event Catalog Wiring | **完成；Fully Accepted** |
| PHX-G20 | Gateway Identity HTTP Surface | **完成；Fully Accepted** |
| PHX-G21 | Gateway Organization HTTP Surface | **完成；Fully Accepted** |
| PHX-G22 | Gateway Permission HTTP Surface | **完成；Fully Accepted** |
| PHX-G23 | Gateway Workflow HTTP Surface | **完成；Fully Accepted** |
| PHX-G24 | Gateway Knowledge HTTP Surface | **完成；Fully Accepted** |
| PHX-G25 | Gateway Platform Tenant Lifecycle | **完成；Fully Accepted** |
| PHX-G26 | Gateway Event Bus HTTP Surface | **完成；Fully Accepted** |
| PHX-G27 | Gateway Package Platform HTTP Surface | **完成；Fully Accepted** |
| PHX-G28 | Gateway Twin & Brain HTTP Surface | **完成；Fully Accepted** |
| PHX-G29 | Gateway AI Runtime HTTP Surface | **完成；Fully Accepted** |
| PHX-G30 | Gateway Smart Terminal HTTP Surface | **完成；Fully Accepted** |
| PHX-G31 | Gateway Domain Route Completions | **完成；Fully Accepted** |
| PHX-G32 | Gateway Organization Route Completions | **完成；Fully Accepted** |
| PHX-G34 | Gateway Marketplace Technical HTTP | **完成；技术 Fully Accepted；商业仍开放** |
| PHX-G35 | Smart Terminal Operator Shell | **完成；技术壳 Fully Accepted** |
| PHX-E20 | Permission DecisionRecorded Wiring | **完成；Fully Accepted** |
| PHX-E21 | Event Webhook Transport | **完成；Fully Accepted** |
| PHX-G36 | Complete Terminal UI | **完成；Fully Accepted** |
| PHX-G37 | JWT/OIDC Trusted Context | **完成；Fully Accepted（HS256）** |
| PHX-M17 | Marketplace Commercial Policy | **完成；Fully Accepted（Foundation v1）** |
| PHX-G38 | JWT JWKS / RS256 | **完成；Fully Accepted** |
| PHX-E22 | Event Webhook HMAC | **完成；Fully Accepted** |
| PHX-G39 | Terminal Extension Host | **完成；Fully Accepted（Foundation）** |
| PHX-G40 | OIDC Authorization Code Login | **完成；Fully Accepted（Foundation）** |
| PHX-G41 | Terminal Extension SQL Persistence | **完成；Fully Accepted（Foundation）** |
| PHX-G42 | Terminal Extension iframe + CSP | **完成；Fully Accepted（Foundation）** |
| PHX-G43 | Terminal Extension Worker Runtime | **完成；Fully Accepted（Foundation）** |
| PHX-M18 | Marketplace Package Signature Cryptography | **完成；Fully Accepted（Foundation）** |
| PHX-G44 | Terminal Extension Signature Cryptography | **完成；Fully Accepted（Foundation）** |
| PHX-G45 | JWT Multi-Issuer JWKS | **完成；Fully Accepted（Foundation）** |
| PHX-G46 | JWT Denylist | **完成；Fully Accepted（Foundation）** |
| PHX-G47 | OIDC IdP Discovery | **完成；Fully Accepted（Foundation）** |
| PHX-G48 | OIDC Discovery → JWKS Wire | **完成；Fully Accepted（Foundation）** |
| PHX-G49 | Production Deploy Topology | **完成；Fully Accepted（Foundation）** |
| PHX-G50 | Docker Compose Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G51 | Kubernetes Helm Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G52 | Ingress / TLS Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G53 | HPA Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G54 | VPA Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G55 | Multi-IdP Status UI | **完成；Fully Accepted（Foundation）** |
| PHX-G56 | Multi-IdP Write Registry | **完成；Fully Accepted（Foundation）** |
| PHX-G57 | IdP Registry SQL Adapter | **完成；Fully Accepted（Foundation）** |
| PHX-G58 | KEDA Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G59 | Service Mesh Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G60 | OIDC Discovery → Registry Writeback | **完成；Fully Accepted（Foundation）** |
| PHX-G61 | OIDC Refresh + RP-Logout | **完成；Fully Accepted（Foundation）** |
| PHX-G62 | Platform IdP Registry Terminal Ops | **完成；Fully Accepted（Foundation）** |
| PHX-G63 | OIDC Refresh Binding SQL Adapter | **完成；Fully Accepted（Foundation）** |
| PHX-G64 | OIDC Refresh Token Field Encryption | **完成；Fully Accepted（Foundation）** |
| PHX-G65 | OIDC Refresh Fernet Key Rotation | **完成；Fully Accepted（Foundation）** |
| PHX-G66 | Tenant IdP Federation Binding | **完成；Fully Accepted（Foundation）** |
| PHX-G67 | Tenant IdP Federation SQL Adapter | **完成；Fully Accepted（Foundation）** |
| PHX-G68 | JWT Tenant IdP Federation Enforcement | **完成；Fully Accepted（Foundation）** |
| PHX-G69 | Tenant IdP Federation Terminal Ops | **完成；Fully Accepted（Foundation）** |
| PHX-G70 | OIDC Refresh Re-encrypt On Read | **完成；Fully Accepted（Foundation）** |
| PHX-G71 | Service Mesh Policy CRD Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G72 | Service Mesh Traffic CRD Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G73 | Service Mesh AuthorizationPolicy Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G74 | OIDC Refresh Fernet Key Provider | **完成；Fully Accepted（Foundation）** |
| PHX-G75 | OIDC Refresh KMS Key Provider | **完成；Fully Accepted（Foundation）** |
| PHX-G76 | Deploy Region Identity Foundation | **完成；Fully Accepted（Foundation）** |
| PHX-G77 | Tenant IdP Federation Policy Matrix | **完成；Fully Accepted（Foundation）** |
| PHX-G78 | Tenant IdP Federation Issuer Priority | **完成；Fully Accepted（Foundation）** |
| PHX-G79 | OIDC Required Claims Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G80 | OIDC amr/acr Auth Context Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G81 | OIDC Claim→Role JWT Mint Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G82 | JWT eaos_roles → ExecutionContext Roles Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G83 | Opt-in Context Roles Evaluate Grant Map Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G84 | OIDC Multi-Provider Login Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G85 | OIDC Per-Provider Refresh Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G86 | OIDC Provider End-Session Catalog Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G87 | OIDC Authorize ACR/Prompt Step-Up Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G88 | Opt-in EAOS Roles Catalog Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G89 | OIDC MFA Enrollment URL Gate | **完成；Fully Accepted（Foundation）** |
| PHX-G90 | Declared EAOS Roles Catalog SQL Store | **完成；Fully Accepted（Foundation）** |
| PHX-G91 | Terminal Platform Roles Admin Thin Ops | **完成；Fully Accepted（Foundation）** |
| PHX-G92 | Terminal Tenant Roles Catalog Read | **完成；Fully Accepted（Foundation）** |
| PHX-G93 | Permission Roles Status Observability | **完成；Fully Accepted（Foundation）** |
| PHX-G94 | Terminal Permission Evaluate Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G95 | Terminal Effective Permissions Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G96 | JWT Denylist Status Observability | **完成；Fully Accepted（Foundation）** |
| PHX-G97 | Terminal Event Bus Stats Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G98 | Terminal Event Dispatch Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G99 | Terminal Event Enqueue/Publish Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G100 | Terminal Event Subscribe/Replay Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G101 | Marketplace Status + Listing Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G102 | Marketplace Listing Lifecycle Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G103 | Marketplace Acquire Technical Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G104 | Workflow Status / Definition / Instance Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G105 | Workflow Task Approve / Reject Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G106 | Workflow Signal / Cancel Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G107 | Workflow Compensate / Escalate Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G108 | Package Status / Manifest / Surfaces Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G109 | Package Publish / Install / Disable / Resolve Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G110 | Knowledge Status / Entity Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G111 | Knowledge Archive / Share / Search Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G112 | Knowledge Link / Provenance Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G113 | Twin Status / Snapshot Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G114 | Twin Authorize Fail-Closed Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G115 | Brain Status / Insight Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G116 | Brain Execute Fail-Closed Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G117 | AI Runtime Status / Run Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G118 | AI Tools / Memory Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G119 | AI Approval / Commit Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G120 | Identity Status / Subject Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G121 | Identity Credential / Session Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G122 | Organization Status / Tenant / Enterprise Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G123 | Organization Unit / Membership Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G124 | Organization Lifecycle Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G125 | Organization Membership Transfer / End Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G126 | Organization Enterprise Lifecycle Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G127 | Platform Tenant Lifecycle Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G128 | Permission Policy / Grant Manual Write Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G129 | Permission Deprecate / Delegate Thin Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G130 | OpenAPI Foundation Status Catalog | **完成；Fully Accepted（Foundation）** |
| PHX-G131 | Auth OpenAPI Status Catalog | **完成；Fully Accepted（Foundation）** |
| PHX-G132 | OIDC Login / Callback OpenAPI | **完成；Fully Accepted（Foundation）** |
| PHX-G133 | OIDC Refresh / Logout OpenAPI | **完成；Fully Accepted（Foundation）** |
| PHX-G134 | OIDC MFA Enrollment OpenAPI | **完成；Fully Accepted（Foundation）** |
| PHX-G135 | Platform OpenAPI Catalog | **完成；Fully Accepted（Foundation）** |
| PHX-G136 | Permission Roles List OpenAPI | **完成；Fully Accepted（Foundation）** |
| PHX-G137 | Identity Credential/Session Revoke Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G138 | Identity AI Employee / Governor Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G139 | Gateway Ops OpenAPI Catalog | **完成；Fully Accepted（Foundation）** |
| PHX-G140 | Terminal Ops Echo + Workflow Deprecate | **完成；Fully Accepted（Foundation）** |
| PHX-G141 | Marketplace Commercial Terminal Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G142 | Organization Get Enterprise Probe | **完成；Fully Accepted（Foundation）** |
| PHX-G143 | Dual-Track Governance Formalization | **完成；Fully Accepted（Foundation）** |
| PHX-G144 | Foundation 0.2.1 Release Train | **完成；Fully Accepted（Foundation 0.2.1）** |
| PHX-G145 | WebAuthn / MFA Product Posture (thin) | **完成；Fully Accepted（Foundation）** |
| PHX-G146 | Role→grant Product Posture (thin) | **完成；Fully Accepted（Foundation）** |
| PHX-G147 | OIDC Login Product Surface (thin) | **完成；Fully Accepted（Foundation）** |
| PHX-G148 | OpenAPI Inventory Product Posture (thin) | **完成；Fully Accepted（Foundation）** |
| PHX-G149 | Eng Soft-Queue Tip Hygiene (docs-only) | **完成；Fully Accepted（Foundation）** |
| PHX-G150 | Autonomous Execution Directive (docs-only) | **完成；Fully Accepted（Foundation）** |
| PHX-G151 | WebAuthn Ceremony Stub Deepen | **完成；Fully Accepted（Foundation）** |
| PHX-G152 | AR Board Queue + Manifest Hygiene | **完成；Fully Accepted（Foundation；docs-only）** |
| PHX-G153 | Ops / Compatibility / Checklist Hygiene | **完成；Fully Accepted（Foundation；docs-only）** |
| PHX-G154 | WebAuthn Ceremony Stub Observability | **完成；Fully Accepted（Foundation）** |
| PHX-G155 | T2 / T3 Evidence Readiness Board | **完成；Fully Accepted（Foundation；docs-only）** |
| PHX-G156 | Role→grant Auto-Write Stub Deepen | **完成；Fully Accepted（Foundation）** |
| PHX-G157 | Ops / Checklist Hygiene After G156 | **完成；Fully Accepted（Foundation；docs-only）** |
| PHX-G158 | Autonomous Soft-Queue Natural Pause | **完成；Fully Accepted（Foundation；docs-only；Pause）** |
| PHX-G159 | Generation-1 Architecture Review Board Hold | **完成；Fully Accepted（Research；docs-only；Hold×10）** |
| PHX-G160 | WebAuthn Env-Gated Live Mint | **完成；Fully Accepted（Foundation；default OFF；attestation crypto Out）** |
| PHX-G161 | Role→grant Env-Gated Live Mint | **完成；Fully Accepted（Foundation；default OFF）** |
| PHX-G162 | Marketplace Payment Clearing | **完成；Fully Accepted（Foundation；Eng `4`；default OFF）** |
| PHX-G163 | T2 / T3 Evidence Intake & Live Capture | **完成；Fully Accepted（Research；docs-only；0 Complete）** |
| PHX-G164 | OpenAPI Semantic Deepen (T-0188) | **完成；Fully Accepted（Foundation；mount complete；semantic partial）** |
| PHX-G169 | Signed Extension Host Productization | **完成；Fully Accepted（Foundation；allowlisted signed bundles only）** |

## 下一步

### Engineering Track

1. **Operating directive：** [AUTONOMOUS_EXECUTION_DIRECTIVE.md](AUTONOMOUS_EXECUTION_DIRECTIVE.md)（AED v1.1 / PHX-G150）— 最高价值选择 under HARD HOLDS  
2. **Tip board：** [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md)（**G160** WebAuthn live mint；**G164** OpenAPI semantic deepen；G161/G162 PO slices；Held Brain/Twin/external PSP / attestation crypto；Resume = live T2–T3 / further semantic / external PSP / Promote+ADR；board hygiene **DAL-U010** / PHX-G149）  
3. **下一刀需授权：** live T2/T3 工件 **或** WebAuthn attestation crypto PO **或** 进一步 semantic deepen **或** external PSP PO  
4. External PSP / arbitration（仍 Held after G162 internal record）  
5. 多区域生产 SaaS/failover 仍非目标  
6. 基线已 `0.2.1`；OpenAPI mount parity 完成（G164）；Alembic 仍 `0029`  

### Research Track (NRI)

1. **Wave 1 peers（均已 Pass → WP content Accepted）：**  
   - RP-001 **臻宇** → [PEER](../research/programs/RP-001-enterprise-discovery/PEER_REVIEW_PACKAGE.md) · [Evidence Pack](../research/programs/RP-001-enterprise-discovery/EVIDENCE_PACK.md) · [WHITE_PAPER-RP-001](../research/programs/RP-001-enterprise-discovery/WHITE_PAPER-RP-001.md) Accepted · **[AR Candidate NRI-ARC-RP-001](../research/programs/RP-001-enterprise-discovery/ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md)**（Board Decision — Hold；PHX-G159；≠ Eng ingest）  
   - RP-005 **包锦昱**（legal）→ [PEER](../research/programs/RP-005-ai-workforce-transformation/PEER_REVIEW_PACKAGE.md) · RI-01/RI-02 · [WHITE_PAPER-RP-005](../research/programs/RP-005-ai-workforce-transformation/WHITE_PAPER-RP-005.md) Accepted · **[AR Candidate NRI-ARC-RP-005](../research/programs/RP-005-ai-workforce-transformation/ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md)**（Board Decision — Hold；PHX-G159；≠ Eng ingest）  
   - RP-007 **牟蓉** → [PEER](../research/programs/RP-007-enterprise-evolution-engine/PEER_REVIEW_PACKAGE.md) · [WHITE_PAPER-RP-007](../research/programs/RP-007-enterprise-evolution-engine/WHITE_PAPER-RP-007.md) Accepted · **[AR Candidate NRI-ARC-RP-007](../research/programs/RP-007-enterprise-evolution-engine/ARCHITECTURE_REVIEW_CANDIDATE-RP-007.md)**（Board Decision — Hold；PHX-G159；≠ Eng ingest）  
2. **Peer Pass ≠ WP 内容 Acceptance ≠ Architecture Review ≠ Eng 队列**；拒绝 `<name>` 占位 — [WAVE1_PEER_ASSIGNMENT](../research/WAVE1_PEER_ASSIGNMENT.md)  
3. **Wave 2：** RP-002 / RP-003（CG-01…02）/ RP-004（NA-01…02）/ RP-009（AE-01…03）Pass → WP content Accepted（[WHITE_PAPER-RP-002](../research/programs/RP-002-enterprise-dna/WHITE_PAPER-RP-002.md) · [WHITE_PAPER-RP-003](../research/programs/RP-003-capability-first/WHITE_PAPER-RP-003.md) · [WHITE_PAPER-RP-004](../research/programs/RP-004-organization-neutrality/WHITE_PAPER-RP-004.md) · [WHITE_PAPER-RP-009](../research/programs/RP-009-enterprise-brain-evolution/WHITE_PAPER-RP-009.md)；WP Draft frozen as Accepted）— [WAVE2_PEER_ASSIGNMENT](../research/WAVE2_PEER_ASSIGNMENT.md)；RP-002 **[AR Candidate NRI-ARC-RP-002](../research/programs/RP-002-enterprise-dna/ARCHITECTURE_REVIEW_CANDIDATE-RP-002.md)**（Board Decision — Hold；PHX-G159；DNA≠grant）；RP-009 **[AR Candidate NRI-ARC-RP-009](../research/programs/RP-009-enterprise-brain-evolution/ARCHITECTURE_REVIEW_CANDIDATE-RP-009.md)**（Board Decision — Hold；PHX-G159；`execution_authority: none`；IC-06；ADR-0030）；RP-003 **[AR Candidate NRI-ARC-RP-003](../research/programs/RP-003-capability-first/ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md)**（Board Decision — Hold；PHX-G159；Cap≠Org；Capability ≠ Permission；`auto_grant_minted: never`）；RP-004 **[AR Candidate NRI-ARC-RP-004](../research/programs/RP-004-organization-neutrality/ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md)**（Board Decision — Hold；PHX-G159；Structure ≠ Permission；`org_shape_grant: never`）  
4. **Wave 3：** RP-006 AIRM + GP-01…02 peer **臻宇** Pass → [WHITE_PAPER-RP-006](../research/programs/RP-006-ai-infrastructure-platform/WHITE_PAPER-RP-006.md) Accepted · **[AR Candidate NRI-ARC-RP-006](../research/programs/RP-006-ai-infrastructure-platform/ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md)**（Board Decision — Hold；PHX-G159；`kernel_bypass: never`）；RP-008 SFSM + PW-01…02 peer **臻宇** Pass → [WHITE_PAPER-RP-008](../research/programs/RP-008-smart-factory/WHITE_PAPER-RP-008.md) Accepted · **[AR Candidate NRI-ARC-RP-008](../research/programs/RP-008-smart-factory/ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md)**（Board Decision — Hold；PHX-G159；`mes_kernelization: never`；`machine_control_from_brain: never`）；RP-010 FEOM + SA-01…02 peer **臻宇** Pass → [WHITE_PAPER-RP-010](../research/programs/RP-010-future-enterprise-operating-model/WHITE_PAPER-RP-010.md) Accepted · **[AR Candidate NRI-ARC-RP-010](../research/programs/RP-010-future-enterprise-operating-model/ARCHITECTURE_REVIEW_CANDIDATE-RP-010.md)**（Board Decision — Hold；PHX-G159；`constitution_rewrite: never`；`execution_authority: none`；synthesis not rewrite）— [WAVE3_PEER_ASSIGNMENT](../research/WAVE3_PEER_ASSIGNMENT.md)  
5. **G1 Peer Gate：** WP content Accepted（10）；Generation-1 peer gates closed — [GENERATION1_PEER_GATE](../research/GENERATION1_PEER_GATE.md)  
6. **Research tip（G2）：** G1 complete；AR Candidates RP-001…010 Board Decision — Hold — [ARCHITECTURE_REVIEW_BOARD_QUEUE](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md)；T2/T3 readiness — [T2_T3_EVIDENCE_READINESS](../research/T2_T3_EVIDENCE_READINESS.md)（floors **T1**；0 live Complete；PHX-G155）；intake — [T2_T3_EVIDENCE_INTAKE](../research/T2_T3_EVIDENCE_INTAKE.md)（**NRI-T2-T3-INTAKE**；PHX-G163 / DAL-U034；0 Complete）；Next = real live artifacts then floor flip（not invent；Hold ≠ Eng）— [GENERATION2_TIP_BOARD](../research/GENERATION2_TIP_BOARD.md)  
7. Brain execute / Twin authorize / Role→grant auto-write / 支付清算仍 fail-closed 或 Explicit Defer  
8. 操作手册：[DUAL_TRACK_GOVERNANCE.md](DUAL_TRACK_GOVERNANCE.md) · AED：[AUTONOMOUS_EXECUTION_DIRECTIVE.md](AUTONOMOUS_EXECUTION_DIRECTIVE.md)  
9. **CA 审批授权窗口：** 2026-07-21…**2026-07-27**（Research + Eng `1`–`3` when logged；不含 Eng `4` / 虚构未知 peer；Role→grant **live mint** 仍需 **explicit PO**；**soft-queue Pause G158**）— [DELEGATED_AUTHORITY_LEDGER.md](DELEGATED_AUTHORITY_LEDGER.md)（**DAL-G003** + **DAL-G004**；U001–U030）  
10. **持续自主开发：** 已开启至 2026-07-27；按 AED 选最高价值；每次使用记入 DAL Usage Log  
11. **Eng tip：** [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md)（PHX-G149）

### 当前环境限制

已在当前用户目录部署隔离 PostgreSQL 17（端口 55432），并配置专用 `eaos_test`。官方系统安装器仍曾出现无响应，不作为验收实例；便携实例已通过全部集成契约。

## 关联

- [../../kernel/identity/README.md](../../kernel/identity/README.md)
- [../../kernel/organization/README.md](../../kernel/organization/README.md)
- [../../kernel/permission/README.md](../../kernel/permission/README.md)
- [../../kernel/workflow/README.md](../../kernel/workflow/README.md)
- [../../eaos_platform/knowledge/README.md](../../eaos_platform/knowledge/README.md)
- [../../kernel/event_bus/README.md](../../kernel/event_bus/README.md)
- [../../smart_terminal/README.md](../../smart_terminal/README.md)
- [../../runtime/ai/README.md](../../runtime/ai/README.md)
- [../../eaos_platform/package/README.md](../../eaos_platform/package/README.md)
- [../../eaos_platform/twin/README.md](../../eaos_platform/twin/README.md)
- [../../eaos_platform/brain/README.md](../../eaos_platform/brain/README.md)
- [../../eaos_platform/marketplace/README.md](../../eaos_platform/marketplace/README.md)
- [../../sdk/README.md](../../sdk/README.md)
- [../../api/README.md](../../api/README.md)
- [PHX-G18_ACCEPTANCE.md](PHX-G18_ACCEPTANCE.md)
- [PHX-E19_ACCEPTANCE.md](PHX-E19_ACCEPTANCE.md)
- [PHX-G20_ACCEPTANCE.md](PHX-G20_ACCEPTANCE.md)
- [PHX-G21_ACCEPTANCE.md](PHX-G21_ACCEPTANCE.md)
- [PHX-G22_ACCEPTANCE.md](PHX-G22_ACCEPTANCE.md)
- [PHX-G23_ACCEPTANCE.md](PHX-G23_ACCEPTANCE.md)
- [PHX-G24_ACCEPTANCE.md](PHX-G24_ACCEPTANCE.md)
- [PHX-G25_ACCEPTANCE.md](PHX-G25_ACCEPTANCE.md)
- [PHX-G26_ACCEPTANCE.md](PHX-G26_ACCEPTANCE.md)
- [PHX-G27_ACCEPTANCE.md](PHX-G27_ACCEPTANCE.md)
- [PHX-G28_ACCEPTANCE.md](PHX-G28_ACCEPTANCE.md)
- [PHX-G29_ACCEPTANCE.md](PHX-G29_ACCEPTANCE.md)
- [PHX-G30_ACCEPTANCE.md](PHX-G30_ACCEPTANCE.md)
- [PHX-G31_ACCEPTANCE.md](PHX-G31_ACCEPTANCE.md)
- [PHX-G32_ACCEPTANCE.md](PHX-G32_ACCEPTANCE.md)
- [PHX-G34_ACCEPTANCE.md](PHX-G34_ACCEPTANCE.md)
- [PHX-G35_ACCEPTANCE.md](PHX-G35_ACCEPTANCE.md)
- [PHX-G36_ACCEPTANCE.md](PHX-G36_ACCEPTANCE.md)
- [PHX-G37_ACCEPTANCE.md](PHX-G37_ACCEPTANCE.md)
- [PHX-G37_ARCHITECTURE_GATE.md](PHX-G37_ARCHITECTURE_GATE.md)
- [PHX-M17_ACCEPTANCE.md](PHX-M17_ACCEPTANCE.md)
- [PHX-M17_ARCHITECTURE_GATE.md](PHX-M17_ARCHITECTURE_GATE.md)
- [PHX-G38_ACCEPTANCE.md](PHX-G38_ACCEPTANCE.md)
- [PHX-G38_ARCHITECTURE_GATE.md](PHX-G38_ARCHITECTURE_GATE.md)
- [PHX-E22_ACCEPTANCE.md](PHX-E22_ACCEPTANCE.md)
- [PHX-E22_ARCHITECTURE_GATE.md](PHX-E22_ARCHITECTURE_GATE.md)
- [PHX-G39_ACCEPTANCE.md](PHX-G39_ACCEPTANCE.md)
- [PHX-G39_ARCHITECTURE_GATE.md](PHX-G39_ARCHITECTURE_GATE.md)
- [PHX-G40_ACCEPTANCE.md](PHX-G40_ACCEPTANCE.md)
- [PHX-G40_ARCHITECTURE_GATE.md](PHX-G40_ARCHITECTURE_GATE.md)
- [PHX-G41_ACCEPTANCE.md](PHX-G41_ACCEPTANCE.md)
- [PHX-G41_ARCHITECTURE_GATE.md](PHX-G41_ARCHITECTURE_GATE.md)
- [PHX-G42_ACCEPTANCE.md](PHX-G42_ACCEPTANCE.md)
- [PHX-G42_ARCHITECTURE_GATE.md](PHX-G42_ARCHITECTURE_GATE.md)
- [PHX-G43_ACCEPTANCE.md](PHX-G43_ACCEPTANCE.md)
- [PHX-G43_ARCHITECTURE_GATE.md](PHX-G43_ARCHITECTURE_GATE.md)
- [PHX-M18_ACCEPTANCE.md](PHX-M18_ACCEPTANCE.md)
- [PHX-M18_ARCHITECTURE_GATE.md](PHX-M18_ARCHITECTURE_GATE.md)
- [PHX-G44_ACCEPTANCE.md](PHX-G44_ACCEPTANCE.md)
- [PHX-G44_ARCHITECTURE_GATE.md](PHX-G44_ARCHITECTURE_GATE.md)
- [PHX-G45_ACCEPTANCE.md](PHX-G45_ACCEPTANCE.md)
- [PHX-G45_ARCHITECTURE_GATE.md](PHX-G45_ARCHITECTURE_GATE.md)
- [PHX-G46_ACCEPTANCE.md](PHX-G46_ACCEPTANCE.md)
- [PHX-G46_ARCHITECTURE_GATE.md](PHX-G46_ARCHITECTURE_GATE.md)
- [PHX-G47_ACCEPTANCE.md](PHX-G47_ACCEPTANCE.md)
- [PHX-G47_ARCHITECTURE_GATE.md](PHX-G47_ARCHITECTURE_GATE.md)
- [PHX-G48_ACCEPTANCE.md](PHX-G48_ACCEPTANCE.md)
- [PHX-G48_ARCHITECTURE_GATE.md](PHX-G48_ARCHITECTURE_GATE.md)
- [PHX-G49_ACCEPTANCE.md](PHX-G49_ACCEPTANCE.md)
- [PHX-G49_ARCHITECTURE_GATE.md](PHX-G49_ARCHITECTURE_GATE.md)
- [PHX-G50_ACCEPTANCE.md](PHX-G50_ACCEPTANCE.md)
- [PHX-G50_ARCHITECTURE_GATE.md](PHX-G50_ARCHITECTURE_GATE.md)
- [PHX-G51_ACCEPTANCE.md](PHX-G51_ACCEPTANCE.md)
- [PHX-G51_ARCHITECTURE_GATE.md](PHX-G51_ARCHITECTURE_GATE.md)
- [PHX-G52_ACCEPTANCE.md](PHX-G52_ACCEPTANCE.md)
- [PHX-G52_ARCHITECTURE_GATE.md](PHX-G52_ARCHITECTURE_GATE.md)
- [PHX-G53_ACCEPTANCE.md](PHX-G53_ACCEPTANCE.md)
- [PHX-G53_ARCHITECTURE_GATE.md](PHX-G53_ARCHITECTURE_GATE.md)
- [PHX-G54_ACCEPTANCE.md](PHX-G54_ACCEPTANCE.md)
- [PHX-G54_ARCHITECTURE_GATE.md](PHX-G54_ARCHITECTURE_GATE.md)
- [PHX-G55_ACCEPTANCE.md](PHX-G55_ACCEPTANCE.md)
- [PHX-G55_ARCHITECTURE_GATE.md](PHX-G55_ARCHITECTURE_GATE.md)
- [PHX-G56_ACCEPTANCE.md](PHX-G56_ACCEPTANCE.md)
- [PHX-G56_ARCHITECTURE_GATE.md](PHX-G56_ARCHITECTURE_GATE.md)
- [PHX-G57_ACCEPTANCE.md](PHX-G57_ACCEPTANCE.md)
- [PHX-G57_ARCHITECTURE_GATE.md](PHX-G57_ARCHITECTURE_GATE.md)
- [PHX-G58_ACCEPTANCE.md](PHX-G58_ACCEPTANCE.md)
- [PHX-G58_ARCHITECTURE_GATE.md](PHX-G58_ARCHITECTURE_GATE.md)
- [PHX-G59_ACCEPTANCE.md](PHX-G59_ACCEPTANCE.md)
- [PHX-G59_ARCHITECTURE_GATE.md](PHX-G59_ARCHITECTURE_GATE.md)
- [PHX-G60_ACCEPTANCE.md](PHX-G60_ACCEPTANCE.md)
- [PHX-G60_ARCHITECTURE_GATE.md](PHX-G60_ARCHITECTURE_GATE.md)
- [PHX-G61_ACCEPTANCE.md](PHX-G61_ACCEPTANCE.md)
- [PHX-G61_ARCHITECTURE_GATE.md](PHX-G61_ARCHITECTURE_GATE.md)
- [PHX-G62_ACCEPTANCE.md](PHX-G62_ACCEPTANCE.md)
- [PHX-G62_ARCHITECTURE_GATE.md](PHX-G62_ARCHITECTURE_GATE.md)
- [PHX-G63_ACCEPTANCE.md](PHX-G63_ACCEPTANCE.md)
- [PHX-G63_ARCHITECTURE_GATE.md](PHX-G63_ARCHITECTURE_GATE.md)
- [PHX-G64_ACCEPTANCE.md](PHX-G64_ACCEPTANCE.md)
- [PHX-G64_ARCHITECTURE_GATE.md](PHX-G64_ARCHITECTURE_GATE.md)
- [PHX-G65_ACCEPTANCE.md](PHX-G65_ACCEPTANCE.md)
- [PHX-G65_ARCHITECTURE_GATE.md](PHX-G65_ARCHITECTURE_GATE.md)
- [PHX-G66_ACCEPTANCE.md](PHX-G66_ACCEPTANCE.md)
- [PHX-G66_ARCHITECTURE_GATE.md](PHX-G66_ARCHITECTURE_GATE.md)
- [PHX-G67_ACCEPTANCE.md](PHX-G67_ACCEPTANCE.md)
- [PHX-G67_ARCHITECTURE_GATE.md](PHX-G67_ARCHITECTURE_GATE.md)
- [PHX-G68_ACCEPTANCE.md](PHX-G68_ACCEPTANCE.md)
- [PHX-G68_ARCHITECTURE_GATE.md](PHX-G68_ARCHITECTURE_GATE.md)
- [PHX-G69_ACCEPTANCE.md](PHX-G69_ACCEPTANCE.md)
- [PHX-G69_ARCHITECTURE_GATE.md](PHX-G69_ARCHITECTURE_GATE.md)
- [PHX-G70_ACCEPTANCE.md](PHX-G70_ACCEPTANCE.md)
- [PHX-G70_ARCHITECTURE_GATE.md](PHX-G70_ARCHITECTURE_GATE.md)
- [PHX-G71_ACCEPTANCE.md](PHX-G71_ACCEPTANCE.md)
- [PHX-G71_ARCHITECTURE_GATE.md](PHX-G71_ARCHITECTURE_GATE.md)
- [PHX-G72_ACCEPTANCE.md](PHX-G72_ACCEPTANCE.md)
- [PHX-G72_ARCHITECTURE_GATE.md](PHX-G72_ARCHITECTURE_GATE.md)
- [PHX-G73_ACCEPTANCE.md](PHX-G73_ACCEPTANCE.md)
- [PHX-G73_ARCHITECTURE_GATE.md](PHX-G73_ARCHITECTURE_GATE.md)
- [PHX-G74_ACCEPTANCE.md](PHX-G74_ACCEPTANCE.md)
- [PHX-G74_ARCHITECTURE_GATE.md](PHX-G74_ARCHITECTURE_GATE.md)
- [PHX-G75_ACCEPTANCE.md](PHX-G75_ACCEPTANCE.md)
- [PHX-G75_ARCHITECTURE_GATE.md](PHX-G75_ARCHITECTURE_GATE.md)
- [PHX-G76_ACCEPTANCE.md](PHX-G76_ACCEPTANCE.md)
- [PHX-G76_ARCHITECTURE_GATE.md](PHX-G76_ARCHITECTURE_GATE.md)
- [PHX-G77_ACCEPTANCE.md](PHX-G77_ACCEPTANCE.md)
- [PHX-G77_ARCHITECTURE_GATE.md](PHX-G77_ARCHITECTURE_GATE.md)
- [PHX-G78_ACCEPTANCE.md](PHX-G78_ACCEPTANCE.md)
- [PHX-G78_ARCHITECTURE_GATE.md](PHX-G78_ARCHITECTURE_GATE.md)
- [PHX-G79_ACCEPTANCE.md](PHX-G79_ACCEPTANCE.md)
- [PHX-G79_ARCHITECTURE_GATE.md](PHX-G79_ARCHITECTURE_GATE.md)
- [PHX-G80_ACCEPTANCE.md](PHX-G80_ACCEPTANCE.md)
- [PHX-G80_ARCHITECTURE_GATE.md](PHX-G80_ARCHITECTURE_GATE.md)
- [PHX-G81_ACCEPTANCE.md](PHX-G81_ACCEPTANCE.md)
- [PHX-G81_ARCHITECTURE_GATE.md](PHX-G81_ARCHITECTURE_GATE.md)
- [PHX-G82_ACCEPTANCE.md](PHX-G82_ACCEPTANCE.md)
- [PHX-G82_ARCHITECTURE_GATE.md](PHX-G82_ARCHITECTURE_GATE.md)
- [PHX-G83_ACCEPTANCE.md](PHX-G83_ACCEPTANCE.md)
- [PHX-G83_ARCHITECTURE_GATE.md](PHX-G83_ARCHITECTURE_GATE.md)
- [PHX-G84_ACCEPTANCE.md](PHX-G84_ACCEPTANCE.md)
- [PHX-G84_ARCHITECTURE_GATE.md](PHX-G84_ARCHITECTURE_GATE.md)
- [PHX-G85_ACCEPTANCE.md](PHX-G85_ACCEPTANCE.md)
- [PHX-G85_ARCHITECTURE_GATE.md](PHX-G85_ARCHITECTURE_GATE.md)
- [PHX-G86_ACCEPTANCE.md](PHX-G86_ACCEPTANCE.md)
- [PHX-G86_ARCHITECTURE_GATE.md](PHX-G86_ARCHITECTURE_GATE.md)
- [PHX-G87_ACCEPTANCE.md](PHX-G87_ACCEPTANCE.md)
- [PHX-G87_ARCHITECTURE_GATE.md](PHX-G87_ARCHITECTURE_GATE.md)
- [PHX-G88_ACCEPTANCE.md](PHX-G88_ACCEPTANCE.md)
- [PHX-G88_ARCHITECTURE_GATE.md](PHX-G88_ARCHITECTURE_GATE.md)
- [PHX-G89_ACCEPTANCE.md](PHX-G89_ACCEPTANCE.md)
- [PHX-G89_ARCHITECTURE_GATE.md](PHX-G89_ARCHITECTURE_GATE.md)
- [PHX-G90_ACCEPTANCE.md](PHX-G90_ACCEPTANCE.md)
- [PHX-G90_ARCHITECTURE_GATE.md](PHX-G90_ARCHITECTURE_GATE.md)
- [PHX-G91_ACCEPTANCE.md](PHX-G91_ACCEPTANCE.md)
- [PHX-G91_ARCHITECTURE_GATE.md](PHX-G91_ARCHITECTURE_GATE.md)
- [PHX-G92_ACCEPTANCE.md](PHX-G92_ACCEPTANCE.md)
- [PHX-G92_ARCHITECTURE_GATE.md](PHX-G92_ARCHITECTURE_GATE.md)
- [PHX-G93_ACCEPTANCE.md](PHX-G93_ACCEPTANCE.md)
- [PHX-G93_ARCHITECTURE_GATE.md](PHX-G93_ARCHITECTURE_GATE.md)
- [PHX-G94_ACCEPTANCE.md](PHX-G94_ACCEPTANCE.md)
- [PHX-G94_ARCHITECTURE_GATE.md](PHX-G94_ARCHITECTURE_GATE.md)
- [PHX-G95_ACCEPTANCE.md](PHX-G95_ACCEPTANCE.md)
- [PHX-G95_ARCHITECTURE_GATE.md](PHX-G95_ARCHITECTURE_GATE.md)
- [PHX-G96_ACCEPTANCE.md](PHX-G96_ACCEPTANCE.md)
- [PHX-G96_ARCHITECTURE_GATE.md](PHX-G96_ARCHITECTURE_GATE.md)
- [PHX-G97_ACCEPTANCE.md](PHX-G97_ACCEPTANCE.md)
- [PHX-G97_ARCHITECTURE_GATE.md](PHX-G97_ARCHITECTURE_GATE.md)
- [PHX-G98_ACCEPTANCE.md](PHX-G98_ACCEPTANCE.md)
- [PHX-G98_ARCHITECTURE_GATE.md](PHX-G98_ARCHITECTURE_GATE.md)
- [PHX-G99_ACCEPTANCE.md](PHX-G99_ACCEPTANCE.md)
- [PHX-G99_ARCHITECTURE_GATE.md](PHX-G99_ARCHITECTURE_GATE.md)
- [PHX-G100_ACCEPTANCE.md](PHX-G100_ACCEPTANCE.md)
- [PHX-G100_ARCHITECTURE_GATE.md](PHX-G100_ARCHITECTURE_GATE.md)
- [PHX-G101_ACCEPTANCE.md](PHX-G101_ACCEPTANCE.md)
- [PHX-G101_ARCHITECTURE_GATE.md](PHX-G101_ARCHITECTURE_GATE.md)
- [PHX-G102_ACCEPTANCE.md](PHX-G102_ACCEPTANCE.md)
- [PHX-G102_ARCHITECTURE_GATE.md](PHX-G102_ARCHITECTURE_GATE.md)
- [PHX-G103_ACCEPTANCE.md](PHX-G103_ACCEPTANCE.md)
- [PHX-G103_ARCHITECTURE_GATE.md](PHX-G103_ARCHITECTURE_GATE.md)
- [PHX-G104_ACCEPTANCE.md](PHX-G104_ACCEPTANCE.md)
- [PHX-G104_ARCHITECTURE_GATE.md](PHX-G104_ARCHITECTURE_GATE.md)
- [PHX-G105_ACCEPTANCE.md](PHX-G105_ACCEPTANCE.md)
- [PHX-G105_ARCHITECTURE_GATE.md](PHX-G105_ARCHITECTURE_GATE.md)
- [PHX-G106_ACCEPTANCE.md](PHX-G106_ACCEPTANCE.md)
- [PHX-G106_ARCHITECTURE_GATE.md](PHX-G106_ARCHITECTURE_GATE.md)
- [PHX-G107_ACCEPTANCE.md](PHX-G107_ACCEPTANCE.md)
- [PHX-G107_ARCHITECTURE_GATE.md](PHX-G107_ARCHITECTURE_GATE.md)
- [PHX-G108_ACCEPTANCE.md](PHX-G108_ACCEPTANCE.md)
- [PHX-G108_ARCHITECTURE_GATE.md](PHX-G108_ARCHITECTURE_GATE.md)
- [PHX-G109_ACCEPTANCE.md](PHX-G109_ACCEPTANCE.md)
- [PHX-G109_ARCHITECTURE_GATE.md](PHX-G109_ARCHITECTURE_GATE.md)
- [PHX-G110_ACCEPTANCE.md](PHX-G110_ACCEPTANCE.md)
- [PHX-G110_ARCHITECTURE_GATE.md](PHX-G110_ARCHITECTURE_GATE.md)
- [PHX-G111_ACCEPTANCE.md](PHX-G111_ACCEPTANCE.md)
- [PHX-G111_ARCHITECTURE_GATE.md](PHX-G111_ARCHITECTURE_GATE.md)
- [PHX-G112_ACCEPTANCE.md](PHX-G112_ACCEPTANCE.md)
- [PHX-G112_ARCHITECTURE_GATE.md](PHX-G112_ARCHITECTURE_GATE.md)
- [PHX-G113_ACCEPTANCE.md](PHX-G113_ACCEPTANCE.md)
- [PHX-G113_ARCHITECTURE_GATE.md](PHX-G113_ARCHITECTURE_GATE.md)
- [PHX-G114_ACCEPTANCE.md](PHX-G114_ACCEPTANCE.md)
- [PHX-G114_ARCHITECTURE_GATE.md](PHX-G114_ARCHITECTURE_GATE.md)
- [PHX-G115_ACCEPTANCE.md](PHX-G115_ACCEPTANCE.md)
- [PHX-G115_ARCHITECTURE_GATE.md](PHX-G115_ARCHITECTURE_GATE.md)
- [PHX-G116_ACCEPTANCE.md](PHX-G116_ACCEPTANCE.md)
- [PHX-G116_ARCHITECTURE_GATE.md](PHX-G116_ARCHITECTURE_GATE.md)
- [PHX-G117_ACCEPTANCE.md](PHX-G117_ACCEPTANCE.md)
- [PHX-G117_ARCHITECTURE_GATE.md](PHX-G117_ARCHITECTURE_GATE.md)
- [PHX-G118_ACCEPTANCE.md](PHX-G118_ACCEPTANCE.md)
- [PHX-G118_ARCHITECTURE_GATE.md](PHX-G118_ARCHITECTURE_GATE.md)
- [PHX-G119_ACCEPTANCE.md](PHX-G119_ACCEPTANCE.md)
- [PHX-G119_ARCHITECTURE_GATE.md](PHX-G119_ARCHITECTURE_GATE.md)
- [PHX-G120_ACCEPTANCE.md](PHX-G120_ACCEPTANCE.md)
- [PHX-G120_ARCHITECTURE_GATE.md](PHX-G120_ARCHITECTURE_GATE.md)
- [PHX-G121_ACCEPTANCE.md](PHX-G121_ACCEPTANCE.md)
- [PHX-G121_ARCHITECTURE_GATE.md](PHX-G121_ARCHITECTURE_GATE.md)
- [PHX-G122_ACCEPTANCE.md](PHX-G122_ACCEPTANCE.md)
- [PHX-G122_ARCHITECTURE_GATE.md](PHX-G122_ARCHITECTURE_GATE.md)
- [PHX-G123_ACCEPTANCE.md](PHX-G123_ACCEPTANCE.md)
- [PHX-G123_ARCHITECTURE_GATE.md](PHX-G123_ARCHITECTURE_GATE.md)
- [PHX-G124_ACCEPTANCE.md](PHX-G124_ACCEPTANCE.md)
- [PHX-G124_ARCHITECTURE_GATE.md](PHX-G124_ARCHITECTURE_GATE.md)
- [PHX-G125_ACCEPTANCE.md](PHX-G125_ACCEPTANCE.md)
- [PHX-G125_ARCHITECTURE_GATE.md](PHX-G125_ARCHITECTURE_GATE.md)
- [PHX-G126_ACCEPTANCE.md](PHX-G126_ACCEPTANCE.md)
- [PHX-G126_ARCHITECTURE_GATE.md](PHX-G126_ARCHITECTURE_GATE.md)
- [PHX-G127_ACCEPTANCE.md](PHX-G127_ACCEPTANCE.md)
- [PHX-G127_ARCHITECTURE_GATE.md](PHX-G127_ARCHITECTURE_GATE.md)
- [PHX-G128_ACCEPTANCE.md](PHX-G128_ACCEPTANCE.md)
- [PHX-G128_ARCHITECTURE_GATE.md](PHX-G128_ARCHITECTURE_GATE.md)
- [PHX-G129_ACCEPTANCE.md](PHX-G129_ACCEPTANCE.md)
- [PHX-G129_ARCHITECTURE_GATE.md](PHX-G129_ARCHITECTURE_GATE.md)
- [PHX-G130_ACCEPTANCE.md](PHX-G130_ACCEPTANCE.md)
- [PHX-G130_ARCHITECTURE_GATE.md](PHX-G130_ARCHITECTURE_GATE.md)
- [PHX-G131_ACCEPTANCE.md](PHX-G131_ACCEPTANCE.md)
- [PHX-G131_ARCHITECTURE_GATE.md](PHX-G131_ARCHITECTURE_GATE.md)
- [PHX-G132_ACCEPTANCE.md](PHX-G132_ACCEPTANCE.md)
- [PHX-G132_ARCHITECTURE_GATE.md](PHX-G132_ARCHITECTURE_GATE.md)
- [PHX-G133_ACCEPTANCE.md](PHX-G133_ACCEPTANCE.md)
- [PHX-G133_ARCHITECTURE_GATE.md](PHX-G133_ARCHITECTURE_GATE.md)
- [PHX-G134_ACCEPTANCE.md](PHX-G134_ACCEPTANCE.md)
- [PHX-G134_ARCHITECTURE_GATE.md](PHX-G134_ARCHITECTURE_GATE.md)
- [PHX-G135_ACCEPTANCE.md](PHX-G135_ACCEPTANCE.md)
- [PHX-G135_ARCHITECTURE_GATE.md](PHX-G135_ARCHITECTURE_GATE.md)
- [PHX-G136_ACCEPTANCE.md](PHX-G136_ACCEPTANCE.md)
- [PHX-G136_ARCHITECTURE_GATE.md](PHX-G136_ARCHITECTURE_GATE.md)
- [PHX-G137_ACCEPTANCE.md](PHX-G137_ACCEPTANCE.md)
- [PHX-G137_ARCHITECTURE_GATE.md](PHX-G137_ARCHITECTURE_GATE.md)
- [PHX-G138_ACCEPTANCE.md](PHX-G138_ACCEPTANCE.md)
- [PHX-G138_ARCHITECTURE_GATE.md](PHX-G138_ARCHITECTURE_GATE.md)
- [PHX-G139_ACCEPTANCE.md](PHX-G139_ACCEPTANCE.md)
- [PHX-G139_ARCHITECTURE_GATE.md](PHX-G139_ARCHITECTURE_GATE.md)
- [PHX-G140_ACCEPTANCE.md](PHX-G140_ACCEPTANCE.md)
- [PHX-G140_ARCHITECTURE_GATE.md](PHX-G140_ARCHITECTURE_GATE.md)
- [PHX-G141_ACCEPTANCE.md](PHX-G141_ACCEPTANCE.md)
- [PHX-G141_ARCHITECTURE_GATE.md](PHX-G141_ARCHITECTURE_GATE.md)
- [PHX-G142_ACCEPTANCE.md](PHX-G142_ACCEPTANCE.md)
- [PHX-G142_ARCHITECTURE_GATE.md](PHX-G142_ARCHITECTURE_GATE.md)
- [PHX-G143_ACCEPTANCE.md](PHX-G143_ACCEPTANCE.md)
- [PHX-G143_ARCHITECTURE_GATE.md](PHX-G143_ARCHITECTURE_GATE.md)
- [PHX-G144_ACCEPTANCE.md](PHX-G144_ACCEPTANCE.md)
- [PHX-G144_ARCHITECTURE_GATE.md](PHX-G144_ARCHITECTURE_GATE.md)
- [PHX-G145_ACCEPTANCE.md](PHX-G145_ACCEPTANCE.md)
- [PHX-G145_ARCHITECTURE_GATE.md](PHX-G145_ARCHITECTURE_GATE.md)
- [PHX-G146_ACCEPTANCE.md](PHX-G146_ACCEPTANCE.md)
- [PHX-G146_ARCHITECTURE_GATE.md](PHX-G146_ARCHITECTURE_GATE.md)
- [PHX-G147_ACCEPTANCE.md](PHX-G147_ACCEPTANCE.md)
- [PHX-G147_ARCHITECTURE_GATE.md](PHX-G147_ARCHITECTURE_GATE.md)
- [PHX-G148_ACCEPTANCE.md](PHX-G148_ACCEPTANCE.md)
- [PHX-G148_ARCHITECTURE_GATE.md](PHX-G148_ARCHITECTURE_GATE.md)
- [PHX-G149_ACCEPTANCE.md](PHX-G149_ACCEPTANCE.md)
- [PHX-G149_ARCHITECTURE_GATE.md](PHX-G149_ARCHITECTURE_GATE.md)
- [PHX-G164_ACCEPTANCE.md](PHX-G164_ACCEPTANCE.md)
- [PHX-G164_ARCHITECTURE_GATE.md](PHX-G164_ARCHITECTURE_GATE.md)
- [PHX-G160_ACCEPTANCE.md](PHX-G160_ACCEPTANCE.md)
- [PHX-G160_ARCHITECTURE_GATE.md](PHX-G160_ARCHITECTURE_GATE.md)
- [PHX-G163_ACCEPTANCE.md](PHX-G163_ACCEPTANCE.md)
- [PHX-G163_ARCHITECTURE_GATE.md](PHX-G163_ARCHITECTURE_GATE.md)
- [PHX-G162_ACCEPTANCE.md](PHX-G162_ACCEPTANCE.md)
- [PHX-G162_ARCHITECTURE_GATE.md](PHX-G162_ARCHITECTURE_GATE.md)
- [PHX-G161_ACCEPTANCE.md](PHX-G161_ACCEPTANCE.md)
- [PHX-G161_ARCHITECTURE_GATE.md](PHX-G161_ARCHITECTURE_GATE.md)
- [PHX-G159_ACCEPTANCE.md](PHX-G159_ACCEPTANCE.md)
- [PHX-G159_ARCHITECTURE_GATE.md](PHX-G159_ARCHITECTURE_GATE.md)
- [PHX-G158_ACCEPTANCE.md](PHX-G158_ACCEPTANCE.md)
- [PHX-G158_ARCHITECTURE_GATE.md](PHX-G158_ARCHITECTURE_GATE.md)
- [PHX-G157_ACCEPTANCE.md](PHX-G157_ACCEPTANCE.md)
- [PHX-G157_ARCHITECTURE_GATE.md](PHX-G157_ARCHITECTURE_GATE.md)
- [PHX-G156_ACCEPTANCE.md](PHX-G156_ACCEPTANCE.md)
- [PHX-G156_ARCHITECTURE_GATE.md](PHX-G156_ARCHITECTURE_GATE.md)
- [PHX-G155_ACCEPTANCE.md](PHX-G155_ACCEPTANCE.md)
- [PHX-G155_ARCHITECTURE_GATE.md](PHX-G155_ARCHITECTURE_GATE.md)
- [PHX-G154_ACCEPTANCE.md](PHX-G154_ACCEPTANCE.md)
- [PHX-G154_ARCHITECTURE_GATE.md](PHX-G154_ARCHITECTURE_GATE.md)
- [PHX-G153_ACCEPTANCE.md](PHX-G153_ACCEPTANCE.md)
- [PHX-G153_ARCHITECTURE_GATE.md](PHX-G153_ARCHITECTURE_GATE.md)
- [PHX-G152_ACCEPTANCE.md](PHX-G152_ACCEPTANCE.md)
- [PHX-G152_ARCHITECTURE_GATE.md](PHX-G152_ARCHITECTURE_GATE.md)
- [PHX-G151_ACCEPTANCE.md](PHX-G151_ACCEPTANCE.md)
- [PHX-G151_ARCHITECTURE_GATE.md](PHX-G151_ARCHITECTURE_GATE.md)
- [PHX-G150_ACCEPTANCE.md](PHX-G150_ACCEPTANCE.md)
- [PHX-G150_ARCHITECTURE_GATE.md](PHX-G150_ARCHITECTURE_GATE.md)
- [AUTONOMOUS_EXECUTION_DIRECTIVE.md](AUTONOMOUS_EXECUTION_DIRECTIVE.md)
- [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md)
- [DUAL_TRACK_GOVERNANCE.md](DUAL_TRACK_GOVERNANCE.md)
- [../decisions/ADR-0162-dual-track-governance.md](../decisions/ADR-0162-dual-track-governance.md)
- [../decisions/ADR-0169-autonomous-execution-directive.md](../decisions/ADR-0169-autonomous-execution-directive.md)
- [../decisions/ADR-0170-webauthn-ceremony-stub-deepen.md](../decisions/ADR-0170-webauthn-ceremony-stub-deepen.md)
- [../decisions/ADR-0171-architecture-review-board-queue-and-release-hygiene.md](../decisions/ADR-0171-architecture-review-board-queue-and-release-hygiene.md)
- [../decisions/ADR-0172-foundation-ops-compatibility-checklist-hygiene.md](../decisions/ADR-0172-foundation-ops-compatibility-checklist-hygiene.md)
- [../decisions/ADR-0173-webauthn-ceremony-stub-observability.md](../decisions/ADR-0173-webauthn-ceremony-stub-observability.md)
- [../decisions/ADR-0174-t2-t3-evidence-readiness-board.md](../decisions/ADR-0174-t2-t3-evidence-readiness-board.md)
- [../decisions/ADR-0175-role-grant-auto-write-stub-deepen.md](../decisions/ADR-0175-role-grant-auto-write-stub-deepen.md)
- [../decisions/ADR-0176-foundation-ops-checklist-hygiene-after-g156.md](../decisions/ADR-0176-foundation-ops-checklist-hygiene-after-g156.md)
- [../decisions/ADR-0177-autonomous-soft-queue-natural-pause.md](../decisions/ADR-0177-autonomous-soft-queue-natural-pause.md)
- [../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md)
- [../research/T2_T3_EVIDENCE_READINESS.md](../research/T2_T3_EVIDENCE_READINESS.md)
- [../release/OPERATIONS_RUNBOOK.md](../release/OPERATIONS_RUNBOOK.md)
- [../release/COMPATIBILITY.md](../release/COMPATIBILITY.md)
- [../release/RELEASE_CHECKLIST.md](../release/RELEASE_CHECKLIST.md)
- [../research/README.md](../research/README.md)
- [../release/PRODUCTION_TOPOLOGY.md](../release/PRODUCTION_TOPOLOGY.md)
- [../release/COMPOSE.md](../release/COMPOSE.md)
- [../release/HELM.md](../release/HELM.md)
- [../release/INGRESS.md](../release/INGRESS.md)
- [../release/HPA.md](../release/HPA.md)
- [../release/VPA.md](../release/VPA.md)
- [../release/KEDA.md](../release/KEDA.md)
- [../release/MESH.md](../release/MESH.md)
- [../decisions/ADR-0056-event-webhook-hmac.md](../decisions/ADR-0056-event-webhook-hmac.md)
- [../decisions/ADR-0057-terminal-extension-host.md](../decisions/ADR-0057-terminal-extension-host.md)
- [../decisions/ADR-0058-oidc-authorization-code-login.md](../decisions/ADR-0058-oidc-authorization-code-login.md)
- [../decisions/ADR-0059-terminal-extension-sql.md](../decisions/ADR-0059-terminal-extension-sql.md)
- [../decisions/ADR-0060-terminal-extension-iframe-csp.md](../decisions/ADR-0060-terminal-extension-iframe-csp.md)
- [../decisions/ADR-0061-terminal-extension-worker.md](../decisions/ADR-0061-terminal-extension-worker.md)
- [../decisions/ADR-0062-marketplace-package-signature.md](../decisions/ADR-0062-marketplace-package-signature.md)
- [../decisions/ADR-0063-terminal-extension-signature.md](../decisions/ADR-0063-terminal-extension-signature.md)
- [../decisions/ADR-0064-jwt-multi-issuer-jwks.md](../decisions/ADR-0064-jwt-multi-issuer-jwks.md)
- [../decisions/ADR-0065-jwt-denylist.md](../decisions/ADR-0065-jwt-denylist.md)
- [../decisions/ADR-0066-oidc-discovery.md](../decisions/ADR-0066-oidc-discovery.md)
- [../decisions/ADR-0067-oidc-discovery-jwks-wire.md](../decisions/ADR-0067-oidc-discovery-jwks-wire.md)
- [../decisions/ADR-0068-production-deploy-topology.md](../decisions/ADR-0068-production-deploy-topology.md)
- [../decisions/ADR-0069-docker-compose-foundation.md](../decisions/ADR-0069-docker-compose-foundation.md)
- [../decisions/ADR-0070-helm-foundation.md](../decisions/ADR-0070-helm-foundation.md)
- [../decisions/ADR-0071-ingress-tls-foundation.md](../decisions/ADR-0071-ingress-tls-foundation.md)
- [../decisions/ADR-0072-hpa-foundation.md](../decisions/ADR-0072-hpa-foundation.md)
- [../decisions/ADR-0073-vpa-foundation.md](../decisions/ADR-0073-vpa-foundation.md)
- [../decisions/ADR-0074-multi-idp-status-ui.md](../decisions/ADR-0074-multi-idp-status-ui.md)
- [../decisions/ADR-0075-multi-idp-write-registry.md](../decisions/ADR-0075-multi-idp-write-registry.md)
- [../decisions/ADR-0076-idp-registry-sql.md](../decisions/ADR-0076-idp-registry-sql.md)
- [../decisions/ADR-0077-keda-foundation.md](../decisions/ADR-0077-keda-foundation.md)
- [../decisions/ADR-0078-service-mesh-foundation.md](../decisions/ADR-0078-service-mesh-foundation.md)
- [../decisions/ADR-0090-mesh-policy-crd-foundation.md](../decisions/ADR-0090-mesh-policy-crd-foundation.md)
- [../decisions/ADR-0091-mesh-traffic-crd-foundation.md](../decisions/ADR-0091-mesh-traffic-crd-foundation.md)
- [../decisions/ADR-0092-mesh-authz-crd-foundation.md](../decisions/ADR-0092-mesh-authz-crd-foundation.md)
- [../decisions/ADR-0079-oidc-discovery-registry-write.md](../decisions/ADR-0079-oidc-discovery-registry-write.md)
- [../decisions/ADR-0080-oidc-refresh-rp-logout.md](../decisions/ADR-0080-oidc-refresh-rp-logout.md)
- [../decisions/ADR-0081-platform-idp-registry-terminal-ops.md](../decisions/ADR-0081-platform-idp-registry-terminal-ops.md)
- [../decisions/ADR-0082-oidc-refresh-sql.md](../decisions/ADR-0082-oidc-refresh-sql.md)
- [../decisions/ADR-0109-eaos-declared-roles-sql.md](../decisions/ADR-0109-eaos-declared-roles-sql.md)
- [../decisions/ADR-0110-terminal-roles-admin.md](../decisions/ADR-0110-terminal-roles-admin.md)
- [../decisions/ADR-0111-terminal-tenant-roles-catalog-read.md](../decisions/ADR-0111-terminal-tenant-roles-catalog-read.md)
- [../decisions/ADR-0112-permission-roles-status.md](../decisions/ADR-0112-permission-roles-status.md)
- [../decisions/ADR-0113-terminal-permission-evaluate.md](../decisions/ADR-0113-terminal-permission-evaluate.md)
- [../decisions/ADR-0114-terminal-effective-permissions.md](../decisions/ADR-0114-terminal-effective-permissions.md)
- [../decisions/ADR-0115-jwt-denylist-status.md](../decisions/ADR-0115-jwt-denylist-status.md)
- [../decisions/ADR-0116-terminal-event-bus-stats.md](../decisions/ADR-0116-terminal-event-bus-stats.md)
- [../decisions/ADR-0117-terminal-event-dispatch.md](../decisions/ADR-0117-terminal-event-dispatch.md)
- [../decisions/ADR-0118-terminal-event-enqueue-publish.md](../decisions/ADR-0118-terminal-event-enqueue-publish.md)
- [../decisions/ADR-0119-terminal-event-subscribe-replay.md](../decisions/ADR-0119-terminal-event-subscribe-replay.md)
- [../decisions/ADR-0120-marketplace-status-listing-probe.md](../decisions/ADR-0120-marketplace-status-listing-probe.md)
- [../decisions/ADR-0121-marketplace-listing-lifecycle-probe.md](../decisions/ADR-0121-marketplace-listing-lifecycle-probe.md)
- [../decisions/ADR-0122-marketplace-acquire-probe.md](../decisions/ADR-0122-marketplace-acquire-probe.md)
- [../decisions/ADR-0123-workflow-status-definition-instance-probe.md](../decisions/ADR-0123-workflow-status-definition-instance-probe.md)
- [../decisions/ADR-0124-workflow-task-approve-reject-probe.md](../decisions/ADR-0124-workflow-task-approve-reject-probe.md)
- [../decisions/ADR-0125-workflow-signal-cancel-probe.md](../decisions/ADR-0125-workflow-signal-cancel-probe.md)
- [../decisions/ADR-0126-workflow-compensate-escalate-probe.md](../decisions/ADR-0126-workflow-compensate-escalate-probe.md)
- [../decisions/ADR-0127-package-status-manifest-surfaces-probe.md](../decisions/ADR-0127-package-status-manifest-surfaces-probe.md)
- [../decisions/ADR-0128-package-publish-install-resolve-probe.md](../decisions/ADR-0128-package-publish-install-resolve-probe.md)
- [../decisions/ADR-0129-knowledge-status-entity-probe.md](../decisions/ADR-0129-knowledge-status-entity-probe.md)
- [../decisions/ADR-0130-knowledge-archive-share-search-probe.md](../decisions/ADR-0130-knowledge-archive-share-search-probe.md)
- [../decisions/ADR-0131-knowledge-link-provenance-probe.md](../decisions/ADR-0131-knowledge-link-provenance-probe.md)
- [../decisions/ADR-0132-twin-status-snapshot-probe.md](../decisions/ADR-0132-twin-status-snapshot-probe.md)
- [../decisions/ADR-0133-twin-authorize-fail-closed-probe.md](../decisions/ADR-0133-twin-authorize-fail-closed-probe.md)
- [../decisions/ADR-0134-brain-status-insight-probe.md](../decisions/ADR-0134-brain-status-insight-probe.md)
- [../decisions/ADR-0135-brain-execute-fail-closed-probe.md](../decisions/ADR-0135-brain-execute-fail-closed-probe.md)
- [../decisions/ADR-0136-ai-status-run-probe.md](../decisions/ADR-0136-ai-status-run-probe.md)
- [../decisions/ADR-0137-ai-tools-memory-probe.md](../decisions/ADR-0137-ai-tools-memory-probe.md)
- [../decisions/ADR-0138-ai-approval-commit-probe.md](../decisions/ADR-0138-ai-approval-commit-probe.md)
- [../decisions/ADR-0139-identity-status-subject-probe.md](../decisions/ADR-0139-identity-status-subject-probe.md)
- [../decisions/ADR-0140-identity-credential-session-probe.md](../decisions/ADR-0140-identity-credential-session-probe.md)
- [../decisions/ADR-0141-organization-status-tenant-enterprise-probe.md](../decisions/ADR-0141-organization-status-tenant-enterprise-probe.md)
- [../decisions/ADR-0142-organization-unit-membership-probe.md](../decisions/ADR-0142-organization-unit-membership-probe.md)
- [../decisions/ADR-0143-organization-lifecycle-probe.md](../decisions/ADR-0143-organization-lifecycle-probe.md)
- [../decisions/ADR-0144-organization-membership-transfer-end-probe.md](../decisions/ADR-0144-organization-membership-transfer-end-probe.md)
- [../decisions/ADR-0145-organization-enterprise-lifecycle-probe.md](../decisions/ADR-0145-organization-enterprise-lifecycle-probe.md)
- [../decisions/ADR-0146-platform-tenant-lifecycle-probe.md](../decisions/ADR-0146-platform-tenant-lifecycle-probe.md)
- [../decisions/ADR-0147-permission-policy-grant-write-probe.md](../decisions/ADR-0147-permission-policy-grant-write-probe.md)
- [../decisions/ADR-0148-permission-deprecate-delegate-probe.md](../decisions/ADR-0148-permission-deprecate-delegate-probe.md)
- [../decisions/ADR-0149-openapi-foundation-status-catalog.md](../decisions/ADR-0149-openapi-foundation-status-catalog.md)
- [../decisions/ADR-0150-auth-openapi-status-catalog.md](../decisions/ADR-0150-auth-openapi-status-catalog.md)
- [../decisions/ADR-0151-oidc-login-callback-openapi.md](../decisions/ADR-0151-oidc-login-callback-openapi.md)
- [../decisions/ADR-0152-oidc-refresh-logout-openapi.md](../decisions/ADR-0152-oidc-refresh-logout-openapi.md)
- [../decisions/ADR-0153-oidc-mfa-enrollment-openapi.md](../decisions/ADR-0153-oidc-mfa-enrollment-openapi.md)
- [../decisions/ADR-0154-platform-openapi-catalog.md](../decisions/ADR-0154-platform-openapi-catalog.md)
- [../decisions/ADR-0155-permission-roles-list-openapi.md](../decisions/ADR-0155-permission-roles-list-openapi.md)
- [../decisions/ADR-0156-identity-credential-session-revoke-probe.md](../decisions/ADR-0156-identity-credential-session-revoke-probe.md)
- [../decisions/ADR-0157-identity-ai-governor-probe.md](../decisions/ADR-0157-identity-ai-governor-probe.md)
- [../decisions/ADR-0158-gateway-ops-openapi-catalog.md](../decisions/ADR-0158-gateway-ops-openapi-catalog.md)
- [../decisions/ADR-0159-terminal-ops-echo-workflow-deprecate.md](../decisions/ADR-0159-terminal-ops-echo-workflow-deprecate.md)
- [../decisions/ADR-0160-marketplace-commercial-terminal-probe.md](../decisions/ADR-0160-marketplace-commercial-terminal-probe.md)
- [../decisions/ADR-0161-organization-get-enterprise-probe.md](../decisions/ADR-0161-organization-get-enterprise-probe.md)
- [../decisions/ADR-0052-complete-terminal-ui.md](../decisions/ADR-0052-complete-terminal-ui.md)
- [../decisions/ADR-0053-jwt-oidc-trusted-context.md](../decisions/ADR-0053-jwt-oidc-trusted-context.md)
- [../decisions/ADR-0054-marketplace-commercial-policy.md](../decisions/ADR-0054-marketplace-commercial-policy.md)
- [../decisions/ADR-0055-jwt-jwks-rs256.md](../decisions/ADR-0055-jwt-jwks-rs256.md)
- [PHX-E20_ACCEPTANCE.md](PHX-E20_ACCEPTANCE.md)
- [PHX-E21_ACCEPTANCE.md](PHX-E21_ACCEPTANCE.md)
- [../decisions/ADR-0033-api-gateway-boundary.md](../decisions/ADR-0033-api-gateway-boundary.md)
- [../decisions/ADR-0050-permission-decision-recorded-wiring.md](../decisions/ADR-0050-permission-decision-recorded-wiring.md)
- [../decisions/ADR-0051-event-webhook-transport.md](../decisions/ADR-0051-event-webhook-transport.md)
- [../decisions/ADR-0049-terminal-operator-shell.md](../decisions/ADR-0049-terminal-operator-shell.md)
- [../decisions/ADR-0046-gateway-domain-route-completions.md](../decisions/ADR-0046-gateway-domain-route-completions.md)
- [../decisions/ADR-0047-gateway-organization-route-completions.md](../decisions/ADR-0047-gateway-organization-route-completions.md)
- [../decisions/ADR-0048-gateway-marketplace-http-surface.md](../decisions/ADR-0048-gateway-marketplace-http-surface.md)
- [../decisions/ADR-0040-gateway-platform-tenant-http.md](../decisions/ADR-0040-gateway-platform-tenant-http.md)
- [../decisions/ADR-0041-gateway-event-http-surface.md](../decisions/ADR-0041-gateway-event-http-surface.md)
- [../decisions/ADR-0042-gateway-package-http-surface.md](../decisions/ADR-0042-gateway-package-http-surface.md)
- [../decisions/ADR-0043-gateway-twin-brain-http-surface.md](../decisions/ADR-0043-gateway-twin-brain-http-surface.md)
- [../decisions/ADR-0044-gateway-ai-runtime-http-surface.md](../decisions/ADR-0044-gateway-ai-runtime-http-surface.md)
- [../decisions/ADR-0045-gateway-terminal-http-surface.md](../decisions/ADR-0045-gateway-terminal-http-surface.md)
- [../decisions/ADR-0034-domain-event-catalog-wiring.md](../decisions/ADR-0034-domain-event-catalog-wiring.md)
- [../decisions/ADR-0035-gateway-identity-http-surface.md](../decisions/ADR-0035-gateway-identity-http-surface.md)
- [../decisions/ADR-0036-gateway-organization-http-surface.md](../decisions/ADR-0036-gateway-organization-http-surface.md)
- [../decisions/ADR-0037-gateway-permission-http-surface.md](../decisions/ADR-0037-gateway-permission-http-surface.md)
- [../decisions/ADR-0038-gateway-workflow-http-surface.md](../decisions/ADR-0038-gateway-workflow-http-surface.md)
- [../decisions/ADR-0039-gateway-knowledge-http-surface.md](../decisions/ADR-0039-gateway-knowledge-http-surface.md)
- [../release/RELEASE_MANIFEST.yaml](../release/RELEASE_MANIFEST.yaml)
- [../../packages/README.md](../../packages/README.md)
- [../decisions/ADR-0010-inmemory-foundation-slice.md](../decisions/ADR-0010-inmemory-foundation-slice.md)
- [../decisions/ADR-0011-event-delivery-persistence.md](../decisions/ADR-0011-event-delivery-persistence.md)
- [../decisions/ADR-0012-kernel-database-orm.md](../decisions/ADR-0012-kernel-database-orm.md)
- [../architecture/PERSISTENCE_PORTS.md](../architecture/PERSISTENCE_PORTS.md)
- [PHX-004_ACCEPTANCE.md](PHX-004_ACCEPTANCE.md)
