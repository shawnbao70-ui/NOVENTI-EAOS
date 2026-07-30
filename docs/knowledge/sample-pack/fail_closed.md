# Fail-closed notes (Brain / Twin / adjacent holds)

**Governing tip:** [ENG_SOFT_QUEUE_TIP.md](../../project/ENG_SOFT_QUEUE_TIP.md) Held table · DAL-U228 Brain/Twin wire honesty

| Hold | Stance for this pack |
|------|----------------------|
| Brain execute | **Closed.** Sample pack is docs-only assembly; do not call `/brain/.../execute` or invent success DTOs. |
| Twin authorize | **Closed.** Do not treat pack content as Twin authorize input or grant material. |
| Cap→grant invent | **Closed.** Knowledge ≠ Capability ≠ Permission. |
| External PSP | **Closed.** Finance extract AP/payment observations ≠ payment rails. |
| CRM/Sales/Finance/Delivery CRUD | **Closed.** G290–G293 are Knowledge milestones only. |

## Runtime honesty

If Gateway exposes Brain insight / Twin snapshot GET (read postures), those remain separate from this pack. Execute/authorize stay fail-closed (403 / no success response model per Foundation harden). Opening them requires explicit PO + numbered slice — not 「继续」 alone.

## Package / Alembic

Stay `0.2.1` / `0029`. No new schema for sample pack acceptance.
