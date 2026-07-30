# Sample Knowledge Pack

**Purpose:** One charter-safe assembly of Accepted Legacy Knowledge Extract conclusions (CRM + Sales + Finance + Delivery) for Terminal demo walkthrough and Research observation — not a product module.  
**Milestone:** PHX-G293 · ADR-0319 · DAL-U229  
**Package / Alembic:** stay `0.2.1` / `0029`  
**Date:** 2026-07-24

## What this is

A thin **sample pack** that cross-links PHX-G290…G292 extract packs into a single reading path:

| Upstream | Milestone | Path |
|----------|-----------|------|
| CRM + Sales | PHX-G290 | [`../legacy-extract/crm/`](../legacy-extract/crm/) · [`../legacy-extract/sales/`](../legacy-extract/sales/) |
| Finance | PHX-G291 | [`../legacy-extract/finance/`](../legacy-extract/finance/) |
| Delivery | PHX-G292 | [`../legacy-extract/delivery/`](../legacy-extract/delivery/) |

Authoritative business facts remain in those extract packs. This pack only **assembles, indexes, and states boundaries** for demo / research use.

## Contents

| File | Role |
|------|------|
| [INDEX.md](INDEX.md) | Linked extract modules (CRM→Sales→Delivery→Finance) |
| [assembled_chain.md](assembled_chain.md) | Cross-linked revenue-chain conclusions |
| [usage.md](usage.md) | Terminal demo + Research observation usage |
| [fail_closed.md](fail_closed.md) | Brain execute / Twin authorize holds |

## Boundaries (≠ CRUD)

- **Does not** invent CRM / Sales / Finance / Delivery product CRUD or Kernel/Runtime business modules.
- **Does not** open Brain execute, Twin authorize, Cap→grant invent, or external PSP.
- **Does not** Promote Research AR Candidates or rewrite Const/BP as product truth.
- **Does not** replace or re-accept deepen packs under `legacy-extract/*-deepen/` — those stay Extracted until their own gate.
- **Does not** mean Legacy “客户来样” (`legacy-extract/sample/`); that domain remains a separate extract. This pack’s “Sample” means **sample assembly for demo/research**.

## Exit

ADR + Architecture Gate + Acceptance + tip/status/DAL/Manifest; contract `test_docs_g293_sample_knowledge_pack.py`; package `0.2.1`; Alembic `0029`.
