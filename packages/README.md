# packages/

Industry packages, business packages, and Marketplace-ready **declarations**.

## Purpose

Extend EAOS without forking Kernel or violating tenant/permission boundaries.

## Status

PHX-B14 Foundation: Package Platform lives in `eaos_platform.package`.  
Declarative package artifacts live here under `<package_key>/`.

**Layout truth（PHX-G411）：** `packages/*` = declarations only；runtime implementations live under `noventi/*`.  
See [`../docs/project/RUNTIME_PACKAGE_LAYOUT.md`](../docs/project/RUNTIME_PACKAGE_LAYOUT.md).

## Sample

- [`sample_ops/`](sample_ops/) — `noventi.sample.ops` industry package manifest for PHX-B14 contracts.
- [`sample_product/`](sample_product/) — `noventi.sample.product` business package for Terminal Product surface projection (PHX-G165).
- [`crm/`](crm/) — proposed CRM declaration（≠ `noventi.crm` runtime）.
