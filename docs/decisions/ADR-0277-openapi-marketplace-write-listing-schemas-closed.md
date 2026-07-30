# ADR-0277 — OpenAPI Marketplace Write/Listing Schemas Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G258  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U131**

## 决策

CreateListing/AttachSignature/Review/SetPricing/OpenDispute/ResolveDispute/
SetRevenueShare Request + MarketplaceListing → `additionalProperties: false`；
live consume/emit keys only。marketplace patch bump；ops **1.0.54**；
inventory PHX-G258。不 invent catalog/PSP。
