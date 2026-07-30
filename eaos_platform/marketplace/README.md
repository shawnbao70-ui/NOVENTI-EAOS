# Marketplace

Shared Platform Capability for signed package distribution (PHX-M16), Foundation commercial policy (PHX-M17 / ADR-0054), and package signature cryptography (PHX-M18 / ADR-0062).

## Technical lifecycle

`draft → submitted → approved|rejected → published → revoked` with signature and capability declaration. `AcquireListing` is a technical record, not a purchase contract.

## Package signature (M18)

| Mode | Env | `signature_ref` |
|------|-----|-----------------|
| `off` (default) | — | non-empty opaque ref (M16 compatible) |
| `hmac` | `EAOS_MARKETPLACE_SIGNING_HMAC_SECRET` | `v1:hmac-sha256:<hex>` |
| `ed25519` | `EAOS_MARKETPLACE_SIGNING_ED25519_PUBLIC_KEY_PEM` | `v1:ed25519:<urlsafe-b64>` |

Set `EAOS_MARKETPLACE_SIGNING_MODE` and optionally `EAOS_MARKETPLACE_SIGNING_REQUIRED=1` for fail-closed production.

## Foundation commercial policy (v1)

| Capability | Policy |
|------------|--------|
| Pricing | Fixed amount; currency ISO 4217 (default `CNY`) |
| Revenue share | Platform bps 0–5000 (default 2000) |
| Billing | Immediate invoice from current pricing (`issued`) |
| Dispute | Publisher-tenant open/resolve with audit |
| Payment clearing (PHX-G162) | Env-gated **internal** clearing record against an issued invoice; default OFF → Gateway 503 |

| Env | Effect |
|-----|--------|
| (default) | `POST …/payment-clearing` → 503 `GATEWAY_PAYMENT_CLEARING_DISABLED` |
| `EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED=true` | Internal audit-backed clearing; **no** external PSP |

Deferred (still `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED`): external PSP capture/refund, subscription metering, external arbitration.

See `docs/decisions/ADR-0054-marketplace-commercial-policy.md` and `ADR-0181-marketplace-payment-clearing.md`.
