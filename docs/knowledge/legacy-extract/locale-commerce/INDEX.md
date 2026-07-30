# Locale Commerce Knowledge Extract — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence strength | Primary Legacy locus |
|--------|------|-------------------|----------------------|
| Currency / FX | [currency.md](currency.md) | Medium for stored currencies and quote headers; weak for governed FX lifecycle | `currency_settings`, quote defaults, treasury accounts, pricing calculator |
| Tax | [tax.md](tax.md) | Medium for tax dictionaries/registry; weak for transactional tax calculation | `tax_settings`, `tax_records`, `/tax_center` |
| Locale / i18n | [locale_i18n.md](locale_i18n.md) | Strong for locale resolution/translation infrastructure; mixed for page coverage | `core/i18n/`, `i18n/`, locale files and print-language metadata |

## Cross-module map

| From | To | Observable meaning |
|------|----|--------------------|
| Currency | Finance / Pricing | Quote and account records carry currency; the pricing calculator accepts an ungoverned exchange-rate input |
| Currency | Brand / Country | Brand and country profiles can supply defaults, but do not prove an authoritative live FX source |
| Tax | Finance / Pricing | Tax dictionaries and tax records coexist with pricing, but no reliable tax-inclusive/exclusive price pipeline is evidenced |
| Locale | Currency / Tax | Locale controls labels and display punctuation; country may suggest currency/tax context, while stored commercial facts remain unchanged |
| Locale | Documents | Quote templates and print-language metadata select language/currency presentation independently of transaction calculation |

## Critical honesty findings

1. Seeded exchange rates are configuration values without observed provider, effective date, quotation direction, approval, history or automatic refresh.
2. Quote defaults can reuse the previous quote's exchange rate; this is a convenience copy, not proof that the copied rate remains commercially valid.
3. Treasury account balances are summed without currency conversion on overview pages, so a cross-currency total is not a valid consolidated amount.
4. `tax_settings` contains country/rate metadata, while `/tax_center` lists manually shaped `tax_records`; no key binds a tax record to a tax setting.
5. The active tax example is inserted through a GET endpoint and does not calculate tax from taxable base, line items or pricing.
6. Locale infrastructure supports many languages and English fallback, but audits still report hard-coded strings, incomplete catalogs and untranslated business terminology.
7. Business status values remain canonical English in many tables/templates; translated labels are presentation only, and mixed persisted values remain a migration risk.
