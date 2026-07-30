# 合同（Contract）— Legacy Knowledge

**Evidence strength:** Weak — **not a first-class CRM business module** in EZAM_CRM 9.0  
**What exists:** Document Center module key / label `contract`  
**What does not exist (re-verified 2026-07-23):** `apps/contract/`, contract CRUD routes, `contracts` business table, contract status machine, contract templates under CRM  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope & evidence strength

Honest extraction finding:

- `contract` is registered as one of many **document module types** alongside quotation, sales_order, invoice, etc.
- Document Center is described as content/file authority (upload, version, archive, share) — not commercial contract lifecycle.
- Document Center defaults to **disabled** (`DOCUMENT_CENTER_ENABLED_BY_DEFAULT = False`).
- Registry entries mark `enforced: False` — metadata descriptors, not workflow engines.
- No HTML templates named for commercial contracts were found under `templates/`.
- Business lifecycle stages list Customer → Opportunity → Requirement → Quotation → Sales Order … and **do not include Contract**.
- Constitution / EAOS docs inside Legacy mention “contracts” in governance language (tenant responsibility, AI cannot independently contract). That is platform policy text, **not** CRM contract operations.

Therefore this file records **absence + document-type semantics**, so EAOS does not invent a false “Legacy Contract module” during rewrite.

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 | EAOS 重写备注 |
|----|----------|----------|------|---------------|
| K-R1 | Contract is a document module key, not a revenue-chain stage | Document module registry seed | — | If EAOS needs Contract CRM, design greenfield; do not “extract” nonexistent CRUD |
| K-R2 | Document modules are metadata descriptors; registry marks `enforced: false` | Module resolve/list | Does not replace legacy document management | Capability registry ≠ business workflow |
| K-R3 | Document Center default may be disabled | Feature flag constant | Installations may enable later | Treat as optional content service |
| K-R4 | Contract documents would share generic document features: upload, download, preview, version, archive, restore, favorite, tag, sharing, history | Document feature list | No contract-specific feature overrides found | Reuse document capability; add commercial fields separately |
| K-R5 | Attachment type vocabulary is generic (image, pdf, office, zip, cad, video, audio, other) | Attachment typing | No “signed contract” subtype | EAOS may add legal artifact types |
| K-R6 | Platform governance text: tenants own commercial contracts; AI must not independently enter contracts | Constitution books (policy) | Not implemented as CRM gate | Encode as Human Authorization policy when Contract capability is built |
| K-R7 | No observed link from Quote Won / SO Confirmed → Contract creation | Revenue chain handlers | — | Any quote→contract automation is new product design |
| K-R8 | Category `legal` may host legal files including contracts, but is not exclusive to contracts | Document categories | — | Do not equate legal category with Contract CRM |
| K-R9 | GTFIP lists trade doc types `sales_contract` / `purchase_contract`, but GFIP ship-ready required docs do **not** include them | GTFIP document catalog vs GFIP REQUIRED_DOCUMENTS | LC AI may mention “Per sales contract” as comparison text only | Trade-doc enum ≠ CRM Contract aggregate |
| K-R10 | Enterprise-completeness lifecycle may label a conceptual `contract` step between negotiation and sales_order; GTFIP/GFIP runtime stage chains skip it | Completeness review constants | Sales app does not implement that stage | Treat as narrative completeness tag, not executable CRM flow |
| K-R11 | AI/workforce placeholders exist (`review_contract` task, `contract_review` skill, demo `contract_expiration` risk) | Digital employees / risk engine | Demo / non-DB-driven | Do not migrate placeholders as operational Contract CRM |

---

## 3. 流程

### 3.1 Observed (document-generic only)

Conceptual Document Center flows that would apply if a file were filed under module `contract`:

1. Upload / register document metadata  
2. Categorize / folder / tag  
3. Version  
4. Share / preview / download  
5. Archive / restore  
6. History events (`document_uploaded`, `…_shared`, `version_created`, etc.)

### 3.2 Not observed (commercial contract CRM)

- Draft → Legal review → Countersign → Active → Amend → Expire / Terminate  
- Contract line items / SLA / payment schedule entity  
- Binding to customer / opportunity / quote / order with commercial status  
- E-sign or seal workflow dedicated to contracts  
- Permission slug `contract` under CRM apps

### 3.3 Suggested EAOS greenfield framing (notes only — not Legacy fact)

If EAOS introduces Contract later, likely attachments:

- Customer (party)  
- Quote / Order (commercial basis)  
- Document versions (PDF artifacts)  
- Human authorization for execution (aligns with governance text)

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| K-V1 | Module key must be one of `DOCUMENT_MODULES` to resolve in registry | Soft metadata | Unknown keys return empty resolve |
| K-V2 | No contract-specific field validation found | N/A | — |
| K-V3 | No contract permission slug (`contract`) found in CRM apps | N/A | Documents module uses `document` slug in boundary docs |

---

## 5. 数据含义

| Concept | Meaning in Legacy |
|---------|-------------------|
| `contract` (module_key) | Label “Contract” in document module registry — classifies documents belonging to the contract content domain |
| Document registry tables | Generic document metadata/version/share/archive stores — not contract commercial masters (`document_registry`, categories, folders, tags, attachments, versions, sharing, archives, history) |
| Category `legal` | One of document categories; may host legal files including contracts, but not exclusive |
| Absence of `contracts` business entity | No extracted master for contract number, parties, value, effective dates, status |
| `sales_contract` / `purchase_contract` | GTFIP trade-document type strings — not GFIP required ship docs, not CRM masters |
| Completeness lifecycle `contract` id | Conceptual trade-lifecycle label only |
| AI `review_contract` / risk `contract_expiration` | Task/risk placeholders — not persisted contract records |

**Implication for data migration:** there is no reliable Legacy contract master to migrate as CRM records; at best, miscellaneous files tagged under document module `contract` if any were uploaded in a given tenant DB.

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `core/document/types.py` | `DOCUMENT_MODULES` includes `contract`; feature/history enums; Document Center default flag |
| `core/document/document.py` | Registry label `"contract": "Contract"`; `enforced: False` |
| `core/document/validator.py` | Module key membership check |
| `business_modules/documents.md` | Documents module purpose — content authority, not CRM contract ops |
| `v15/business_lifecycle/constants.py` | Lifecycle stages omit Contract |
| `business_modules/crm.md` | CRM owned scope — no contract ownership |
| `business_modules/README.md` | Module index — no Contract business module entry |
| `docs/constitution/volume-02-eaos/BOOK01.md` / `BOOK03.md` / `BOOK06.md` | Governance statements about tenant contracts & AI authority (policy only) |
| `v15/gtfip/engines/documents.py` | Trade doc types including sales/purchase contract |
| `v15/gfip/repository.py` / `v15/gfip/documents.py` | Ship-ready required docs omit contract types |
| `v15/enterprise_completeness/review.py` | Conceptual BUSINESS_LIFECYCLE step `contract` |
| `v15/enterprise_intelligence/risk_engine.py` | Demo contract_expiration risk |
| `v15/digital_employees/tasks.py` | `review_contract` task type |

**Negative search note (2026-07-23):** no `apps/contract`, no CRM SQL entity named contracts; Customer/Quote/Sales app code has no contract linkage. Document Center + GTFIP type names + completeness/AI placeholders are the only hits.

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
