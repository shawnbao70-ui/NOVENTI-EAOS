# Project Directory Tree

**Repository:** `NOVENTI-EAOS`  
**Generated:** 2026-07-18  
**Milestone:** PHX-000 historical snapshot

---

## Title

Complete EAOS Project Directory Tree

## Purpose

Preserve the initialized PHX-000 tree as a historical snapshot.

## Scope

Documentation and directory initialization at PHX-000 only. This is not the current authoritative tree; PHX-004 later added `alembic/`, Kernel domain modules, persistence infrastructure, and contract/integration tests.

## Current Status

Historical snapshot; superseded by the live repository and [PROJECT_STATUS.md](PROJECT_STATUS.md).

## Tree

```text
NOVENTI-EAOS/
├── README.md
├── api/
│   └── README.md
├── docs/
│   ├── README.md
│   ├── architecture/
│   │   ├── README.md
│   │   ├── EAOS_ARCHITECTURE.md
│   │   ├── SYSTEM_PRINCIPLES.md
│   │   └── VISION.md
│   ├── blueprint/
│   │   ├── README.md
│   │   ├── AI_BLUEPRINT.md
│   │   ├── API_BLUEPRINT.md
│   │   ├── BLUEPRINT_INDEX.md
│   │   ├── EVENT_BLUEPRINT.md
│   │   ├── KERNEL_BLUEPRINT.md
│   │   ├── KNOWLEDGE_BLUEPRINT.md
│   │   ├── PACKAGE_BLUEPRINT.md
│   │   ├── RUNTIME_BLUEPRINT.md
│   │   └── UI_BLUEPRINT.md
│   ├── constitution/
│   │   └── README.md
│   ├── decisions/
│   │   └── README.md
│   ├── project/
│   │   ├── README.md
│   │   ├── ARCHITECTURE_DECISIONS.md
│   │   ├── CHANGELOG.md
│   │   ├── DIRECTORY_TREE.md
│   │   ├── IMPLEMENTATION_LOG.md
│   │   ├── MASTER_PLAN.md
│   │   ├── MIGRATION_STATUS.md
│   │   ├── PROJECT_STATUS.md
│   │   ├── ROADMAP.md
│   │   └── TASKS.md
│   └── standards/
│       ├── README.md
│       ├── AI_STANDARD.md
│       ├── API_STANDARD.md
│       ├── CODING_STANDARD.md
│       ├── DATABASE_STANDARD.md
│       ├── EVENT_STANDARD.md
│       ├── GIT_WORKFLOW.md
│       ├── NAMING_STANDARD.md
│       └── PROJECT_STRUCTURE.md
├── kernel/
│   └── README.md
├── packages/
│   └── README.md
├── platform/
│   └── README.md
├── runtime/
│   └── README.md
├── scripts/
│   └── README.md
├── sdk/
│   └── README.md
├── tests/
│   └── README.md
├── tools/
│   └── README.md
└── ui/
    └── README.md
```

## Future Expansion

Regenerate after each milestone that adds directories or major document sets.
