# Event Catalog + Terminal Read Projection G386 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G386  
**Authorization:** `EVENT_CATALOG_TERMINAL_CODING_AUTHORIZATION_SUMMARY.md`  
**ADR:** [ADR-0410](../decisions/ADR-0410-event-catalog-terminal-read-projection.md)

- No Alembic revision; tip remains `0092_finance_realized_fx_gl_bridge_g372`.
- `GET /v1/events/catalog` projects four wired commercial events.
- Terminal `btnAdminEventCatalog` / `adminEventCatalog` read projection.
- Contracts: `tests/contracts/test_api_gateway_g386_event_catalog_terminal.py`.
- No catalog write invent; no Marketplace PSP; no host installs.

**TRACK-EVENT-CATALOG-TERMINAL COMPLETE / TRACK-G386 COMPLETE**

Tip verified: `0092_finance_realized_fx_gl_bridge_g372`  
Next: PHX-G387 (Baseline hygiene) IN QUEUE.
