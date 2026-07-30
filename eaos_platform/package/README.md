# Package Platform

Shared Platform Capability for Business / Industry Package manifests, tenant installation, and surface/action contract resolution (PHX-B14).

## Ownership

- Owns: Manifest catalog, installation state, declared surface/action contracts.
- Does **not** own: Kernel truth, Permission evaluation, Workflow approval, business entity persistence inside industry packages.

## Exit gate

**不分叉 Kernel** — packages consume platform capabilities; reserved resource types and `kernel.*` keys are rejected.

## Related

- `docs/decisions/ADR-0029-business-package-platform.md`
- `docs/project/PHX-B14_ARCHITECTURE_GATE.md`
- Sample artifact: `packages/sample_ops/`
