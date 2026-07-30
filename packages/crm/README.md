# noventi.crm — proposed package surface (design-only)

This directory holds a **non-runtime** package declaration for the CRM Customer + Contact Product Gate.

| Artifact | Role |
|---|---|
| `manifest.proposed.json` | Declarative discovery draft (`surfaces` / read `inspect` actions only) |

## Hard rules

- **Not** a Package Platform installable manifest. Do not rename to `manifest.json`, register, publish, or install without a separate explicit authorization.
- Declares **no** business write path (no create/update/archive/delete/merge/convert).
- `required_permissions` / `permission_action: read` are naming drafts for Gate review only — they do **not** register Permission Grants or accept a read API.
- `declared_events` stays empty until producer, schema, payload, and trusted Outbox emit are separately accepted.
- Accepted knowledge ≠ Gate Accept ≠ coding authorization. Gate Accept (design-only) does **not** authorize Customer/Contact CRUD, SQL, Alembic, services, or UI.

## Gate references

- `docs/decisions/ADR-0320-crm-customer-contact-product-boundary.md`
- `docs/project/CRM_CUSTOMER_CONTACT_ARCHITECTURE_GATE.md`
- `docs/project/CRM_CUSTOMER_CONTACT_ACCEPTANCE.md`
- `docs/project/CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md`
