# NOVENTI Enterprise AI Operating System (EAOS)

**Program:** Project Phoenix  
**Version:** 2.0  
**Repository:** `NOVENTI-EAOS`  
**Status:** Phoenix Foundation `0.2.0` + G18–G46 Gateway/Terminal/Extension SQL/iframe+Worker+CSP/验签/多发行方 JWKS/denylist/JWT/OIDC + M17–M18 Marketplace + E19–E22 Events/HMAC

---

## Mission

Build NOVENTI as a next-generation Enterprise AI Operating System (EAOS).

This repository is the **only writable development workspace** for EAOS.

## Source of Truth Priority

1. EAOS Constitution (BOOK00–BOOK23)
2. Architecture Blueprint
3. Development Standards
4. Approved Architecture Decisions
5. Project Documentation
6. Legacy Business Assets (read-only knowledge only)

## Repository Layout

| Directory | Purpose |
|-----------|---------|
| `docs/` | Constitution, blueprints, standards, architecture, decisions, project governance |
| `kernel/` | EAOS Kernel Foundation 与 SQLAlchemy 持久化 |
| `platform/` | Shared platform capabilities |
| `runtime/` | Runtime execution layer |
| `packages/` | Industry and business packages |
| `api/` | Contract adapters + minimal FastAPI gateway (`api/gateway`) |
| `sdk/` | `eaos_sdk` client surface (PHX-R17) |
| `ui/` | Operating surfaces |
| `tests/` | Test suites |
| `tools/` | Developer and platform tools |
| `scripts/` | Automation scripts |

## Legacy Boundary

| Repository | Role |
|------------|------|
| `H:\Workspace\NOVENTI-EAOS` | **ONLY** writable EAOS development repository |
| `H:\Workspace\EZAM_CRM-9.0` / `EZAM_CRM - 9.0` | Permanently **READ-ONLY** Legacy asset repository |

Legacy may be referenced only for business rules, processes, industry knowledge, calculation logic, validation rules, business documents, and data models. Legacy architecture, technical debt, folder structure, and old framework design must not be inherited.

## Current Phase

**PHX-R17 Complete** — EAOS Phoenix Foundation `0.2.0` released in-repo.

See [docs/project/PROJECT_STATUS.md](docs/project/PROJECT_STATUS.md) and [docs/release/RELEASE_MANIFEST.yaml](docs/release/RELEASE_MANIFEST.yaml).

## Quick Start

```bash
cd H:\Workspace\NOVENTI-EAOS
pip install -e ".[dev,persistence]"
pytest
```

## Development Order

Constitution → Ownership Classification → Blueprint → Standards → ADR → Interfaces → Data Models → Implementation → Testing → Documentation → Review → Release / Optimization
