# Smart Terminal Blueprint

**文档 ID：** BP-SMART-TERMINAL  
**版本：** 1.0  
**宪法依据：** BOOK23  
**计划里程碑：** PHX-T13  
**状态：** PHX-T13 + G36 UI + G39–G44 Extension Host（SQL + 首方 iframe/Worker + CSP + 可选验签）+ G40 OIDC Login Foundation Fully Accepted（CDN 第三方包 / 多发行方 JWKS 仍另批）

## Ownership

Smart Terminal 是独立受治理交互层。

| 能力 | 所有权 |
|---|---|
| Terminal Shell、布局、交互会话呈现 | Smart Terminal |
| Subject / Credential / Session | Identity Kernel |
| Tenant / Membership | Organization Kernel |
| Authorization Decision | Permission Kernel |
| Approval / Routing | Workflow Kernel |
| Execution Context / Guard | Platform Runtime |
| Agent plan / tools / memory | AI Runtime |
| Knowledge / provenance | Knowledge Kernel |
| Package actions / surfaces | Business Package |
| Extension distribution | Marketplace |
| Insight / recommendation | Enterprise Brain |
| Twin simulation/state | Digital Twin capability |

## Logical Components

```text
Smart Terminal Shell
├─ Session & Tenant Indicator
├─ Human / AI Identity Presenter
├─ Intent Composer
├─ Plan & Impact Preview
├─ Permission / Approval Presenter
├─ Commit Controller
├─ Result & Provenance Viewer
├─ Audit / Event Timeline
└─ Sandboxed Extension Host
```

## Command Lifecycle

```text
Intent
  → trusted context resolution
  → Agent/API plan
  → impact preview
  → Permission.Evaluate
  → Workflow approval when required
  → Runtime guarded commit
  → authoritative result verification
  → immutable audit/event correlation
```

Preview and Commit are separate operations. Any change to action, resource, scope or plan version invalidates prior approval.

## Trust Boundaries

1. Browser/desktop/mobile clients are untrusted context sources.
2. Security context is derived at an authenticated gateway.
3. Extensions are untrusted until signed, declared and sandboxed.
4. AI output is untrusted until validated against policy, provenance and approval.
5. Enterprise Brain output is advisory.
6. Digital Twin simulation is not execution authorization.

## Surface Model

- **Operator Workbench:** daily operational composition
- **AI Collaboration:** intent, plan, evidence and result
- **Admin Console:** governed platform/tenant administration
- **Package Surface:** declared domain-specific projection
- **Approval Surface:** Workflow-backed decision boundary

Smart Terminal is the shared shell and governance model across these surfaces, not a replacement for their domain intent.

## Required Contracts Before Implementation

1. Terminal Session Context
2. Action / Command Manifest
3. Plan Preview and Impact
4. Permission Decision Presentation
5. Approval Binding
6. Commit Result and Idempotency
7. Provenance View
8. Extension Manifest and Sandbox
9. Audit/Event Correlation
10. Accessibility and Localization

## Non-goals

- Business rule engine
- Direct database client
- Permission or approval evaluator
- Agent runtime
- Enterprise knowledge store
- Marketplace registry
- Enterprise Brain execution gateway

## Acceptance Gates

- Context elevation is impossible from client input.
- Cross-tenant history/cache/memory isolation is tested.
- Rejected or stale approval produces zero commit.
- High-impact operations always show scope and impact.
- Extensions cannot hide governance controls.
- Result state is verified against authoritative APIs.
- Accessibility, i18n, offline degradation and secret redaction pass contracts.

## Related

- [../constitution/BOOK23.md](../constitution/BOOK23.md)
- [../constitution/BOOK19.md](../constitution/BOOK19.md)
- [UI_BLUEPRINT.md](UI_BLUEPRINT.md)
- [API_BLUEPRINT.md](API_BLUEPRINT.md)
- [RUNTIME_BLUEPRINT.md](RUNTIME_BLUEPRINT.md)
- [AI_BLUEPRINT.md](AI_BLUEPRINT.md)
- [PACKAGE_BLUEPRINT.md](PACKAGE_BLUEPRINT.md)
- [../decisions/ADR-0021-constitutional-platform-layering.md](../decisions/ADR-0021-constitutional-platform-layering.md)
