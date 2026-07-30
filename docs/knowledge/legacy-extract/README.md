# Legacy Knowledge Extract

**Purpose:** Paraphrased business knowledge from permanently read-only Legacy `EZAM_CRM - 9.0` for EAOS rewrite.  
**Not:** Source extraction, SQL dumps, or premature business-module implementation.  
**Governing principles:** Constitution First · Knowledge Driven · Kernel First · AED v1.1  

## Packs

`Accepted` 只表示已经通过 Phoenix 接受链；`Extracted` 表示知识文档已形成，但尚未分配或通过新的 PHX-G 里程碑。

| Pack | Path | Status | Canonical scope |
|------|------|--------|-----------------|
| CRM | [crm/](crm/) | **Accepted** (PHX-G290) | Customer · Opportunity · Contract absence · Quotation |
| Sales | [sales/](sales/) | **Accepted** (PHX-G290) | Sales Order · quote convert · V18 approve |
| Finance | [finance/](finance/) | **Accepted** (PHX-G291) | Receipts · dual AR · AP · pricing · commission settlement |
| Delivery | [delivery/](delivery/) | **Accepted** (PHX-G292) | DO create · ship · complete · DO→AR |
| Operations | [ops/](ops/) | Extracted | Inventory · Procurement；Order/Delivery 仅作运营交界补充 |
| Sample | [sample/](sample/) | Extracted | Customer receipt · analysis · quotation handoff · honest dispatch gap |
| Requirement | [requirement/](requirement/) | Extracted | Business Requirement · Opportunity 1:N · downstream traceability |
| Master Data | [masterdata/](masterdata/) | Extracted | Product · Supplier · Production intent/runtime gap |
| Governance | [governance/](governance/) | Extracted | Approval · Documents · Customs registries and gaps |
| Follow-up | [followup/](followup/) | Extracted | Customer follow-up · Customer360 assembly · lifecycle gaps |
| Platform Observations | [platform-obs/](platform-obs/) | Extracted | Platform/System surface · Legacy identity/tenant observations · AI Employee metadata/runtime gap |
| UX | [ux/](ux/) | Extracted | UI shell/navigation · PWA · domain dashboards |
| Risk Catalog | [risk-catalog/](risk-catalog/) | Extracted | Dual writes · V14 residual paths · permission holes |
| Object360 | [object360/](object360/) | Extracted | Customer360 · Sample360 · history/audit observations |
| Document Operations | [document-ops/](document-ops/) | Extracted | Numbering · print/export · attachments |
| Locale Commerce | [locale-commerce/](locale-commerce/) | Extracted | Currency/FX · tax · locale/i18n |
| Fulfillment Deepen | [fulfillment-deepen/](fulfillment-deepen/) | Extracted | Reservation · partial delivery · returns/reversal · warehouse |
| Commercial Terms | [commercial-terms/](commercial-terms/) | Extracted | Payment terms · credit limit · discount rules · commercial Incoterms |
| Quality & Compliance | [quality-compliance/](quality-compliance/) | Extracted | Quality checks · nonconformance · compliance records · claim/RMA |
| Inventory Deepen | [inventory-deepen/](inventory-deepen/) | Extracted | Stock ledger · stocktake · transfer · safety stock |
| Delivery Deepen | [delivery-deepen/](delivery-deepen/) | Extracted | Packing · carrier/tracking · delivery exceptions · DO→AR handoff |
| Customer Deepen | [customer-deepen/](customer-deepen/) | Extracted | Hierarchy · contacts/roles · status lifecycle · AR balance view |
| Sample Deepen | [sample-deepen/](sample-deepen/) | Extracted | Intake · analysis · stocking · sample→quote |
| Quotation Deepen | [quotation-deepen/](quotation-deepen/) | Extracted | Lifecycle · approve · line pricing · convert gates |
| Order Chain | [order-chain/](order-chain/) | Extracted | SO convert · approve/open · SO→DO · payment view |
| Opportunity & Requirement Deepen | [opportunity-requirement-deepen/](opportunity-requirement-deepen/) | Extracted | Opportunity sources/lifecycle · requirement create/trace |
| Ship & Complete Deepen | [ship-complete-deepen/](ship-complete-deepen/) | Extracted | DO ship · complete · reopen · invoice/AR |
| Commission Ledger Deepen | [commission-ledger-deepen/](commission-ledger-deepen/) | Extracted | Commission on convert · rate source · TC states · Finance boundary |
| Sample Gate Deepen | [sample-gate-deepen/](sample-gate-deepen/) | Extracted | Custody · analysis completion · quality release · stocking gates |
| Sample–Quote Bridge Deepen | [sample-quote-bridge-deepen/](sample-quote-bridge-deepen/) | Extracted | Line selection · quote completeness · versioning · source trace |
| Quote Convert Policy Deepen | [quote-convert-policy-deepen/](quote-convert-policy-deepen/) | Extracted | State normalization · Approve vs Convert · concurrency · term propagation |
| Sample Release Policy Deepen | [sample-release-policy-deepen/](sample-release-policy-deepen/) | Extracted | Custody transfer · analysis completion fields · quality hold/release · pre-stock/quote gates |
| Quote Materialize Deepen | [quote-materialize-deepen/](quote-materialize-deepen/) | Extracted | Sample→line · empty-draft convert · completeness matrix · revise/resend |
| Convert Atomicity Deepen | [convert-atomicity-deepen/](convert-atomicity-deepen/) | Extracted | SO uniqueness · commission/lifecycle atomicity · term snapshot |
| Receipt / AR Reconcile Deepen | [receipt-ar-reconcile-deepen/](receipt-ar-reconcile-deepen/) | Extracted | SO receipt posting · AR lifecycle · dual balance views · reconciliation absence |
| Ship Idempotency Deepen | [ship-idempotency-deepen/](ship-idempotency-deepen/) | Extracted | Duplicate guard · posting conservation · reopen/reship trap · carrier/POD gap |
| Return & Reversal Policy Deepen | [return-reversal-policy-deepen/](return-reversal-policy-deepen/) | Extracted | Reopen vs return · inventory reverse paths · AR credit/cancel · end-to-end reversal |
| Credit Control Deepen | [credit-control-deepen/](credit-control-deepen/) | Extracted | Credit fields · pause/freeze · convert/ship gates · override/bypass |
| Partial Fulfillment Deepen | [partial-fulfillment-deepen/](partial-fulfillment-deepen/) | Extracted | Multi-DO · qty remaining · allocation/split · partial status drift |
| Numbering Collision Deepen | [numbering-collision-deepen/](numbering-collision-deepen/) | Extracted | Generators · uniqueness · concurrency collision · display vs authority |
| Procurement Receipt Deepen | [procurement-receipt-deepen/](procurement-receipt-deepen/) | Extracted | PO lifecycle gates · goods receipt posting · stock conservation · quantity control |
| AP Payment Deepen | [ap-payment-deepen/](ap-payment-deepen/) | Extracted | AP lifecycle · Treasury payment posting · PO/GR trace · reconciliation absence |
| Permission Surface Deepen | [permission-surface-deepen/](permission-surface-deepen/) | Extracted | UI vs server RBAC · DO route gaps · admin bypass · opt-in checks |
| PO Receive Control Deepen | [po-receive-control-deepen/](po-receive-control-deepen/) | Extracted | Mandatory approval · receipt header/lines · partial/short/over receipt · quality disposition |
| AP Settlement Deepen | [ap-settlement-deepen/](ap-settlement-deepen/) | Extracted | PO/GR/invoice match · payment allocation · partial clearing/write-off · supplier balance authority |
| Command Authorization Deepen | [command-authz-deepen/](command-authz-deepen/) | Extracted | Server route coverage · object/tenant scope · GET mutations · audited override |
| Tax Invoice Deepen | [tax-invoice-deepen/](tax-invoice-deepen/) | Extracted | Tax invoice entity · NDE vs AR invoice · doc tax calc · void/credit |
| FX / Revaluation Deepen | [fx-revaluation-deepen/](fx-revaluation-deepen/) | Extracted | FX rate source · multi-currency docs · revaluation job · cross-currency clearing |
| Approval Center Deepen | [approval-center-deepen/](approval-center-deepen/) | Extracted | Center runtime · V18 vs center · multi-step evidence · business hook gaps |
| Tax Filing Deepen | [tax-filing-deepen/](tax-filing-deepen/) | Extracted | Doc tax base/rate · filing linkage · AR/print/tax separation · credit-note accounting |
| FX Propagation Deepen | [fx-propagation-deepen/](fx-propagation-deepen/) | Extracted | Convert FX fields · receipt/payment FX · period revaluation · realized/unrealized FX |
| Approval Submit Hooks Deepen | [approval-submit-hooks-deepen/](approval-submit-hooks-deepen/) | Extracted | create_approval call sites · Quote/SO/Ship hooks · multi-step runtime · GET approve/reject |

## Canonical ownership and deduplication

| Knowledge area | Canonical pack | Overlap handling |
|----------------|----------------|------------------|
| Customer / Opportunity / Quotation / Contract absence | [crm/](crm/) | Requirement, Sample and Governance link back at their boundaries |
| Customer follow-up | [followup/](followup/) | CRM owns the customer; Follow-up owns the attached records |
| Business requirement | [requirement/](requirement/) | CRM/Sample cite the relationship instead of redefining it |
| Sample | [sample/](sample/) | Inventory owns receipt posting; Sample owns sample semantics |
| Sales Order | [sales/](sales/) | [ops/order.md](ops/order.md) is an operations handoff view, not a second authority |
| Delivery Order | [delivery/](delivery/) | [ops/delivery.md](ops/delivery.md) is an operations handoff view, not a second authority |
| Inventory / Procurement | [ops/](ops/) | Master Data owns Product/Supplier meanings, not stock or purchase workflows |
| Receipts / AR / AP / pricing / settlement | [finance/](finance/) | Delivery only describes the DO→AR handoff |
| Product / Supplier / Production | [masterdata/](masterdata/) | Operations and Finance cite only their transactional boundaries |
| Approval / Documents / Customs | [governance/](governance/) | Local V18 confirmation remains a business gate, not centralized approval |
| Legacy platform / identity / AI employee observations | [platform-obs/](platform-obs/) | Records observable Legacy behavior only; it does not define EAOS Kernel, Identity or Brain |
| UI shell / PWA / dashboards | [ux/](ux/) | UI reachability and presentation cross-reference domain packs; they do not own business rules or authorization |
| Cross-cutting migration risks | [risk-catalog/](risk-catalog/) | Catalog entries link to canonical domain facts instead of copying their full rules |
| Customer360 / Sample360 / history and audit views | [object360/](object360/) | Aggregates CRM, Sample and Follow-up facts by reference; “360” is not a second object store or unified event authority |
| Numbering / print-export / attachments | [document-ops/](document-ops/) | Cross-references domain documents and Governance metadata; it owns operational document behavior, not business lifecycles |
| Currency / tax / locale-i18n | [locale-commerce/](locale-commerce/) | Finance owns postings and pricing; Locale Commerce owns display/configuration observations and their transactional gaps |
| Reservation / partial delivery / reversal / warehouse | [fulfillment-deepen/](fulfillment-deepen/) | Deepens negative evidence and fulfillment gaps; Sales, Delivery and Operations remain owners of observed transactions |
| Payment / credit / discount / Incoterms | [commercial-terms/](commercial-terms/) | Cross-references CRM, Sales, Finance and Governance; it owns commercial-term propagation and control gaps, not duplicate document lifecycles |
| Quality / nonconformance / compliance / RMA | [quality-compliance/](quality-compliance/) | Cross-references Sample, Procurement, Inventory, Delivery and Document Operations; labels and templates do not become quality facts |
| Stock ledger / stocktake / transfer / safety stock | [inventory-deepen/](inventory-deepen/) | Deepens [ops/inventory.md](ops/inventory.md); Operations remains owner of inventory postings |
| Packing / tracking / exceptions / DO→AR | [delivery-deepen/](delivery-deepen/) | Deepens Delivery and Finance handoffs without redefining DO, inventory or AR authorities |
| Customer hierarchy / contacts / status / AR view | [customer-deepen/](customer-deepen/) | Deepens CRM and Object360 observations; CRM remains owner of the customer master |
| Sample intake / analysis / stocking / quotation handoff | [sample-deepen/](sample-deepen/) | Deepens [sample/](sample/) and Object360; Sample remains owner of customer-received sample semantics |
| Quote lifecycle / approve / pricing / convert gates | [quotation-deepen/](quotation-deepen/) | Deepens [crm/quotation.md](crm/quotation.md), Pricing Advanced and Governance without becoming a second quote authority |
| SO convert / approve / fulfillment / payment view | [order-chain/](order-chain/) | Deepens [sales/](sales/), Delivery and Finance handoffs; Sales remains owner of the SO |
| Opportunity sources/lifecycle and requirement trace | [opportunity-requirement-deepen/](opportunity-requirement-deepen/) | Deepens CRM and Requirement; those packs remain canonical owners of the entities |
| Ship / complete / reopen / DO→AR actions | [ship-complete-deepen/](ship-complete-deepen/) | Deepens Delivery and Finance action semantics without redefining DO, inventory or AR ownership |
| Commission accrual / rates / TC ledger / payout gap | [commission-ledger-deepen/](commission-ledger-deepen/) | Deepens Sales conversion and Finance settlement boundaries; it does not create an accounting or payroll authority |
| Sample custody / analysis completion / quality release / stocking gates | [sample-gate-deepen/](sample-gate-deepen/) | Deepens Sample and Quality boundaries; Sample remains owner of sample semantics; Inventory remains owner of stock postings |
| Sample→Quote lines / completeness / versioning / source trace | [sample-quote-bridge-deepen/](sample-quote-bridge-deepen/) | Deepens Sample→Quote handoff without becoming a second quotation authority |
| Quote state normalization / Approve↔Convert / concurrency / term propagation | [quote-convert-policy-deepen/](quote-convert-policy-deepen/) | Deepens Quotation, Sales convert and Commercial Terms; it does not invent a unified commercial contract or approval center |
| Receipt posting / AR lifecycle / dual balances / reconciliation | [receipt-ar-reconcile-deepen/](receipt-ar-reconcile-deepen/) | Deepens Finance, Order Chain and Customer views; Finance remains owner of receipt and AR facts |
| Ship duplicate guard / conservation / reship / POD | [ship-idempotency-deepen/](ship-idempotency-deepen/) | Deepens Ship/Complete and Delivery evidence; Inventory remains owner of stock posting |
| Return / inventory reversal / credit-cancel policy | [return-reversal-policy-deepen/](return-reversal-policy-deepen/) | Deepens Fulfillment, Finance and Commission gaps without creating a return or accounting authority |
| Sample release / completion / hold gates before stock or quote | [sample-release-policy-deepen/](sample-release-policy-deepen/) | Deepens Sample Gate and Quality boundaries; Sample and Inventory remain posting authorities |
| Sample→Quote materialization / empty draft / revise | [quote-materialize-deepen/](quote-materialize-deepen/) | Deepens Sample–Quote Bridge and Quotation without becoming a second quote authority |
| Convert atomicity / uniqueness / term snapshot | [convert-atomicity-deepen/](convert-atomicity-deepen/) | Deepens Quote Convert Policy and Commission Ledger commit boundaries |
| Credit limit / pause / convert-ship gates / bypass | [credit-control-deepen/](credit-control-deepen/) | Deepens Commercial Terms credit observations; CRM remains customer master |
| Partial fulfillment / multi-DO / remaining qty | [partial-fulfillment-deepen/](partial-fulfillment-deepen/) | Deepens Fulfillment partial-delivery negative evidence |
| Document numbering generators / collision / authority | [numbering-collision-deepen/](numbering-collision-deepen/) | Deepens Document Ops numbering without becoming a domain lifecycle authority |
| PO approval / goods receipt / receipt quantity / stock posting | [procurement-receipt-deepen/](procurement-receipt-deepen/) | Deepens Procurement and Inventory handoff; Operations remains owner of inventory postings |
| AP creation / Treasury payment / PO-GR trace / clearing | [ap-payment-deepen/](ap-payment-deepen/) | Deepens Finance AP boundaries without treating bank movement as AP settlement |
| UI visibility / route authorization / privileged bypass | [permission-surface-deepen/](permission-surface-deepen/) | Deepens the permission risk catalog and identity observations; it does not define EAOS Identity |
| PO receive approval / GR structure / quantity variance / quality disposition | [po-receive-control-deepen/](po-receive-control-deepen/) | Deepens Procurement Receipt and Quality boundaries; Operations remains owner of inventory postings |
| Invoice-PO-GR match / payment allocation / clearing / supplier balance | [ap-settlement-deepen/](ap-settlement-deepen/) | Deepens AP Payment and Finance settlement gaps without creating a supplier subledger authority |
| Command route / object-tenant authorization / GET mutation / override audit | [command-authz-deepen/](command-authz-deepen/) | Deepens Permission Surface and Risk Catalog; it records Legacy enforcement gaps and does not define EAOS Identity |
| Sales tax invoice / NDE print / doc tax / void-credit | [tax-invoice-deepen/](tax-invoice-deepen/) | Deepens Finance invoice fragments and Locale Commerce tax; does not invent a tax-invoice authority |
| FX rate / multi-currency propagation / revaluation / FX clearing | [fx-revaluation-deepen/](fx-revaluation-deepen/) | Deepens Locale Commerce currency observations; Finance remains owner of postings |
| Approval Center runtime vs V18 local confirm / multi-step / business hooks | [approval-center-deepen/](approval-center-deepen/) | Deepens Governance approval; local Type A gates remain business-module authorities |
| Tax base/rate on docs / filing / AR-print-tax separation / credit-note books | [tax-filing-deepen/](tax-filing-deepen/) | Deepens Tax Invoice and Locale Commerce tax; does not invent filing or tax-invoice authority |
| Convert/receipt/payment FX propagation / period close / FX P&L | [fx-propagation-deepen/](fx-propagation-deepen/) | Deepens FX Revaluation; Finance remains owner of cash postings |
| Approval submit hooks / multi-step runtime / GET approve-reject | [approval-submit-hooks-deepen/](approval-submit-hooks-deepen/) | Deepens Approval Center and Command Authz; does not invent EAOS Workflow approval |

Dedup rule: define a business fact once in its canonical pack; overlapping packs keep only the boundary, evidence difference, or honest contradiction and link to the canonical document. An overlap never creates a second status authority.

## Cross-pack contradictions

| Contradiction | Canonical references | Honest interpretation |
|---------------|----------------------|-----------------------|
| Chinese/English status families coexist | [crm/](crm/) · [sales/](sales/) · [delivery/](delivery/) | Quote `已确认` is not safely equivalent to `Won`; SO/DO values must not be inferred as one normalized state machine |
| Quote→SO and SO→DO each have duplicate paths | [sales/](sales/) · [delivery/](delivery/) | Paths differ in trace links, numbering, permissions and status side effects; neither difference is hidden by the root index |
| Commercial Contract is absent; `contract` also appears as a document label | [crm/contract.md](crm/contract.md) · [governance/](governance/) | A metadata label does not prove a contract entity, CRUD surface or lifecycle |
| Sample dispatch and Production execution are not evidenced | [sample/](sample/) · [masterdata/](masterdata/) | Receiving/analysis and module intent must not be promoted into outbound sample or production runtime claims |
| Financial and inventory facts have parallel stores | [finance/](finance/) · [ops/](ops/) | SO receipts vs DO-originated AR, and Inventory vs Product stock mirror, remain reconciliation risks |
| Local Human Approved gates differ from Approval Center | [governance/](governance/) | A V18 confirmation point is not evidence of centralized, multi-step approval |
| Legacy login/role/tenant behavior differs from EAOS Identity | [platform-obs/identity_obs.md](platform-obs/identity_obs.md) · [risk-catalog/permission_holes.md](risk-catalog/permission_holes.md) | Session roles, privileged bypasses, opt-in checks and default-tenant dual reads are observations, not an EAOS Identity inheritance model |
| AI Employee registry differs from controlled execution | [platform-obs/ai_employee.md](platform-obs/ai_employee.md) | Employee/task metadata and adjacent workforce APIs do not prove an execution, approval or business-write loop; AI Employee ≠ Brain execute |
| Navigation visibility differs from authorization | [ux/ui_shell.md](ux/ui_shell.md) · [risk-catalog/permission_holes.md](risk-catalog/permission_holes.md) | A hidden or visible menu item neither denies nor grants direct route access |
| Platform/Center registration differs from runtime capability | [platform-obs/platform.md](platform-obs/platform.md) · [risk-catalog/v14_residual.md](risk-catalog/v14_residual.md) | Mounted routes, seeded metadata and health output do not prove enabled, isolated or complete business capability |
| Risk evidence differs from confirmed production divergence | [risk-catalog/dual_write.md](risk-catalog/dual_write.md) | Active dual-write paths are confirmed; actual production data drift remains UNKNOWN without read-only reconciliation |
| “360” aggregation differs from a unified object/event model | [object360/](object360/) | Customer360 and Sample360 assemble parallel reads; history, timeline, object logs and platform audit are not interchangeable |
| A print button or stored path differs from a governed document | [document-ops/](document-ops/) · [governance/documents.md](governance/documents.md) | Preview, export, generated files, attachments and Document Center metadata have distinct evidence and permission boundaries |
| Business numbering has multiple generators and guarantees | [document-ops/numbering.md](document-ops/numbering.md) · [sales/](sales/) · [delivery/](delivery/) | Display formats and application checks do not establish one collision-safe, transactional numbering authority |
| Currency configuration differs from governed FX conversion | [locale-commerce/currency.md](locale-commerce/currency.md) · [finance/](finance/) | Currency-bearing records and manual rates do not prove dated FX sourcing, revaluation or cross-currency clearing |
| Tax metadata differs from transactional tax calculation | [locale-commerce/tax.md](locale-commerce/tax.md) | Tax settings and standalone records do not establish document tax bases, effective rates, jurisdiction or posting |
| Localized labels differ from canonical business values | [locale-commerce/locale_i18n.md](locale-commerce/locale_i18n.md) | Language and formatting must not change persisted statuses, currency, tax, permissions or relationships |
| Multiple DOs differ from controlled partial fulfillment | [fulfillment-deepen/partial_delivery.md](fulfillment-deepen/partial_delivery.md) · [delivery/](delivery/) | Structural duplication is possible, but cumulative shipped/remaining quantities and allocation rules are absent |
| Reopen/Adjust differ from return or reversal | [fulfillment-deepen/returns_reversal.md](fulfillment-deepen/returns_reversal.md) · [quality-compliance/claim_rma.md](quality-compliance/claim_rma.md) | Status-only reopen and generic inventory adjustment do not establish RMA, receipt, disposition, credit or auditable reversal |
| Commercial fields differ from enforced commercial controls | [commercial-terms/](commercial-terms/) | Payment text is lost downstream, credit limits are not enforced, margin pricing is not discounting, and Incoterms do not propagate through the main chain |
| Receipt/stock status differs from quality acceptance | [quality-compliance/](quality-compliance/) · [ops/](ops/) | `Received`, `Stocked`, `PO Receipt` and `Sample Receipt` prove inventory movement, not inspection, release or compliance |
| Quality/document labels differ from controlled evidence | [quality-compliance/](quality-compliance/) · [document-ops/](document-ops/) | QC/Inspection/Certificate templates, placeholder KPIs and default scores do not prove inspection results, certificate validity or nonconformance closure |
| Inventory balance, product mirror and ledger snapshots differ | [inventory-deepen/stock_ledger.md](inventory-deepen/stock_ledger.md) · [risk-catalog/dual_write.md](risk-catalog/dual_write.md) | Active posting paths update parallel facts; a ledger balance snapshot is not proof that all current mirrors reconcile |
| Cycle Count and Transfer labels differ from controlled stocktake/transfer documents | [inventory-deepen/stocktake.md](inventory-deepen/stocktake.md) · [inventory-deepen/transfer.md](inventory-deepen/transfer.md) | Generic delta adjustments and one-sided move labels do not prove count approval, source/destination conservation or in-transit custody |
| Packing/Delivered labels differ from carrier and POD evidence | [delivery-deepen/](delivery-deepen/) · [sample/pod.md](sample/pod.md) | Derived packing output and delivery status do not establish package entities, external tracking events, consignee acceptance or proof of delivery |
| DO “Invoice” differs from tax invoice and reconciled AR | [delivery-deepen/do_ar_handoff.md](delivery-deepen/do_ar_handoff.md) · [finance/](finance/) | DO→AR creates an accrual path; it does not establish tax invoicing, receipt allocation or duplicate-safe reconciliation |
| Customer labels and views differ from governed customer structure | [customer-deepen/](customer-deepen/) · [crm/](crm/) | Flat master data, one overwritable contact, editable statuses and two AR views do not prove hierarchy, decision roles, freezes or one reconciled balance |
| Sample `New`/`Stocked` differs from analysis or quality completion | [sample-deepen/](sample-deepen/) · [quality-compliance/](quality-compliance/) | Intake, manual analysis and inventory materialization are separate; stocking does not prove analysis, inspection or release |
| Quote Approve differs from Quote→SO Convert | [quotation-deepen/](quotation-deepen/) · [order-chain/so_convert.md](order-chain/so_convert.md) | Approve is a local Draft→Sent gate, while conversion can proceed without Sent/Won/central approval and writes `已确认` |
| Quote pricing snapshots differ from governed price/term propagation | [quotation-deepen/quote_lines_pricing.md](quotation-deepen/quote_lines_pricing.md) · [pricing-advanced/](pricing-advanced/) · [commercial-terms/](commercial-terms/) | Cost/price snapshots survive selectively; discount, tax, FX and commercial terms do not form one complete downstream contract |
| One-quote-one-SO guard differs from transactional idempotency | [order-chain/so_convert.md](order-chain/so_convert.md) | Read-before-write protection, best-effort commission and lifecycle hooks do not prove concurrent uniqueness or atomic side effects |
| SO `Open`/`Delivery Created`/`Paid` differ from fulfillment and AR facts | [order-chain/](order-chain/) · [delivery/](delivery/) · [finance/](finance/) | Labels can drift from DO creation, inventory Ship, receipt mirrors and `ar_records`; none is a substitute for reconciled chain state |
| Opportunity lifecycle vocabulary differs from executable transitions | [opportunity-requirement-deepen/opportunity_lifecycle.md](opportunity-requirement-deepen/opportunity_lifecycle.md) | Declared `open/qualified/converted/closed` values and AI opportunity surfaces do not prove persisted transition commands |
| Requirement trace differs from consistent lineage | [opportunity-requirement-deepen/requirement_trace.md](opportunity-requirement-deepen/requirement_trace.md) · [requirement/](requirement/) | Cached counts, direct fields and link rows can drift; conditional writes and swallowed failures allow successful business actions with incomplete trace |
| Ship, Complete and Reopen are not symmetric postings | [ship-complete-deepen/](ship-complete-deepen/) | Ship posts inventory; Complete advances DO/SO only; Reopen rolls statuses back without restoring stock, reversing ledger entries or cancelling AR |
| DO Post AR differs from shipped, unique or tax-invoiced value | [ship-complete-deepen/do_invoice_ar.md](ship-complete-deepen/do_invoice_ar.md) · [finance/](finance/) | Unshipped and duplicate conditions are warnings, and the resulting AR row is neither proof of shipment nor a tax invoice |
| Commission accrual differs from approved payable or payout | [commission-ledger-deepen/](commission-ledger-deepen/) | Best-effort Pending TC rows use SO total and salesperson-level rates; disconnected rules, receipts and Finance paths do not establish approval, expense, payroll or payment |
| Sample custody / analysis / quality release differ from stocking | [sample-gate-deepen/](sample-gate-deepen/) · [quality-compliance/](quality-compliance/) | Incomplete analysis and absent release/hold still allow bind, stock and quote; `Stocked`/`Received` are inventory facts, not quality acceptance |
| Sample→Quote header differs from line-complete commercial draft | [sample-quote-bridge-deepen/](sample-quote-bridge-deepen/) | Draft quotes can be created with zero lines; `sample.product_id` does not auto-materialize quote items; Convert completeness is weaker than Approve |
| Quote version table differs from executable revise/resend | [sample-quote-bridge-deepen/quote_versioning.md](sample-quote-bridge-deepen/quote_versioning.md) | Readable `quote_versions` and Copy-as-new-Draft do not prove an active versioning or Sent-revise workflow |
| Quote status families differ from a single Approve→Convert policy | [quote-convert-policy-deepen/](quote-convert-policy-deepen/) · [quotation-deepen/](quotation-deepen/) | `Sent`/`Won`/`已确认` are not safely equivalent; Convert does not require Sent or central approval |
| Convert success differs from atomic side effects | [quote-convert-policy-deepen/convert_concurrency.md](quote-convert-policy-deepen/convert_concurrency.md) · [commission-ledger-deepen/](commission-ledger-deepen/) | Read-before-write one-quote-one-SO, best-effort TC and lifecycle links can leave SO without commission or complete lineage under concurrency/partial failure |
| Quote commercial fields differ from Convert-propagated contract | [quote-convert-policy-deepen/commercial_term_propagation.md](quote-convert-policy-deepen/commercial_term_propagation.md) · [commercial-terms/](commercial-terms/) | Amount/line snapshots may move; payment text, credit, FX, discount semantics and Incoterms do not form one downstream commercial contract |
| Receipt differs from AR allocation/reconciliation | [finance/ar_receipt_reconciliation.md](finance/ar_receipt_reconciliation.md) · [order-chain/so_payment_view.md](order-chain/so_payment_view.md) | SO Receipt may change payment views while DO-originated `ar_records` remains Unpaid; neither status proves allocation or a reconciled balance |
| Sample owner/log fields differ from executable custody transfer | [sample-release-policy-deepen/custody_transfer.md](sample-release-policy-deepen/custody_transfer.md) · [sample-gate-deepen/sample_custody.md](sample-gate-deepen/sample_custody.md) | Optional owner, logs and inventory location do not prove holder/location transfer, checkout/return, signature or chain-of-custody |
| Analysis presence differs from completion and release policy | [sample-release-policy-deepen/analysis_completion_fields.md](sample-release-policy-deepen/analysis_completion_fields.md) · [sample-release-policy-deepen/quality_hold_release.md](sample-release-policy-deepen/quality_hold_release.md) | Child-row existence and shadow stages do not establish one completion field or hold/release/reject gate before stock or quote |
| Sample product binding differs from quote-line materialization | [quote-materialize-deepen/sample_product_to_line.md](quote-materialize-deepen/sample_product_to_line.md) | `sample.product_id` supports sample stocking but does not automatically create `quote_items`; Sample→Quote can remain an empty Draft |
| Approve completeness differs from Convert completeness | [quote-materialize-deepen/convert_completeness_matrix.md](quote-materialize-deepen/convert_completeness_matrix.md) · [quote-convert-policy-deepen/approve_convert_policy.md](quote-convert-policy-deepen/approve_convert_policy.md) | Approve requires Draft, lines and human confirmation; Convert can create an empty SO without those gates |
| Copy/direct mutation differs from controlled revise/resend | [quote-materialize-deepen/revise_resend.md](quote-materialize-deepen/revise_resend.md) | Copy-as-new-Draft, status overwrite and mutable Sent lines do not establish revision identity, resend history, voiding or immutable publication |
| Shared connection differs from end-to-end Convert atomicity | [convert-atomicity-deepen/](convert-atomicity-deepen/) | SO/TC/items may normally share a pre-commit connection, but swallowed commission errors and post-commit lineage hooks allow missing TC, partial trace and term-loss outcomes |
| Receipt posting differs from AR settlement | [receipt-ar-reconcile-deepen/](receipt-ar-reconcile-deepen/) | Receipt creation and SO mirror updates do not allocate, reduce, close or reconcile DO-originated `ar_records`; Customer360 and Statement can retain different balances |
| Ship application guard differs from database idempotency | [ship-idempotency-deepen/ship_duplicate_guard.md](ship-idempotency-deepen/ship_duplicate_guard.md) | A read-before-write lookup on `DO Ship + DO-{do_no}` has no observed unique key, posting-attempt identity, lock or concurrency-safe insert |
| Successful Ship differs from proven posting conservation | [ship-idempotency-deepen/ship_posting_conservation.md](ship-idempotency-deepen/ship_posting_conservation.md) · [risk-catalog/dual_write.md](risk-catalog/dual_write.md) | Inventory, product mirror and ledger are sequential writes; normal arithmetic does not prove rollback, concurrency safety or persistent reconciliation |
| Reopen differs from return, unship or reship authorization | [ship-idempotency-deepen/reopen_reship_trap.md](ship-idempotency-deepen/reopen_reship_trap.md) · [return-reversal-policy-deepen/reopen_vs_return.md](return-reversal-policy-deepen/reopen_vs_return.md) | Reopen changes statuses but preserves stock and the original guard ledger, so it neither reverses shipment nor authorizes a controlled second Ship |
| Manual positive adjustment differs from linked inventory reversal | [return-reversal-policy-deepen/inventory_reverse_paths.md](return-reversal-policy-deepen/inventory_reverse_paths.md) | A free-text quantity adjustment can compensate stock but does not reference or reverse the original Ship posting, RMA or idempotency key |
| Credit Note/AR labels differ from financial reversal | [return-reversal-policy-deepen/ar_credit_cancel.md](return-reversal-policy-deepen/ar_credit_cancel.md) | Printable Credit Note and status vocabulary do not establish Receipt void/refund, AR credit/cancel, payment-mirror recompute or commission reversal |
| Credit fields differ from convert/ship enforcement | [credit-control-deepen/](credit-control-deepen/) · [commercial-terms/credit_limit.md](commercial-terms/credit_limit.md) | `credit_limit` / labels drive risk display at most; Quote/SO/DO/Ship do not gate on credit, overdue or freeze |
| Pause/invalid customer labels differ from hard holds | [credit-control-deepen/status_pause_freeze.md](credit-control-deepen/status_pause_freeze.md) | Editable text statuses are not freeze/blacklist/credit-hold state machines |
| Multi-DO creation differs from controlled partial fulfillment | [partial-fulfillment-deepen/](partial-fulfillment-deepen/) · [fulfillment-deepen/partial_delivery.md](fulfillment-deepen/partial_delivery.md) | Repeated full-line DO copies are allowed without remaining-qty, allocation, warehouse or batch selection |
| Any DO Complete/Reopen differs from SO partial aggregate truth | [partial-fulfillment-deepen/status_on_partial.md](partial-fulfillment-deepen/status_on_partial.md) | A single DO status write can overwrite SO fulfillment state without cumulative shipped evidence |
| Number generators differ from collision-safe authority | [numbering-collision-deepen/](numbering-collision-deepen/) · [document-ops/numbering.md](document-ops/numbering.md) | COUNT+1 / timestamp schemes and uneven unique keys do not prove concurrent-safe, shared-sequence document identity |
| PO `Approve` differs from receipt eligibility | [procurement-receipt-deepen/po_lifecycle_gates.md](procurement-receipt-deepen/po_lifecycle_gates.md) | Receive accepts the open family, including Draft/Pending; an approval button and Human Confirm do not establish a mandatory pre-receipt gate |
| PO `Received` differs from complete, quantity-controlled receipt | [procurement-receipt-deepen/po_qty_control.md](procurement-receipt-deepen/po_qty_control.md) · [procurement-receipt-deepen/goods_receipt_posting.md](procurement-receipt-deepen/goods_receipt_posting.md) | Full planned quantities are reused as receipt quantities; invalid rows can be skipped and no partial, rejected, short or over-receipt model proves line completion |
| Receipt stock arithmetic differs from proven atomic conservation | [procurement-receipt-deepen/receipt_to_stock.md](procurement-receipt-deepen/receipt_to_stock.md) · [risk-catalog/dual_write.md](risk-catalog/dual_write.md) | Inventory, product mirror and ledger writes share a connection but lack full preflight, explicit rollback and reconciliation evidence under failure or concurrency |
| Treasury payment differs from AP allocation and clearing | [ap-payment-deepen/](ap-payment-deepen/) · [finance/ap_payment_clearing.md](finance/ap_payment_clearing.md) | Payment rows and bank-balance movement do not update, allocate or reconcile `ap_records`, purchase invoices or supplier balances |
| UI visibility or an available checker differs from enforced authorization | [permission-surface-deepen/](permission-surface-deepen/) · [risk-catalog/permission_holes.md](risk-catalog/permission_holes.md) | Permission calls are route-by-route opt-in; hidden buttons, browser confirmation, CSRF treatment and Admin bypass do not supply command-, object- or tenant-level authorization |
| Receipt-table DDL differs from an active GR header/line authority | [po-receive-control-deepen/receipt_header_lines.md](po-receive-control-deepen/receipt_header_lines.md) · [procurement-receipt-deepen/goods_receipt_posting.md](procurement-receipt-deepen/goods_receipt_posting.md) | Active Receive posts PO lines directly to stock and a text-linked ledger; an unused `purchase_receipts` table does not establish structured receipt custody or line trace |
| PO receipt differs from quality disposition and usable-stock release | [po-receive-control-deepen/quality_disposition_on_receive.md](po-receive-control-deepen/quality_disposition_on_receive.md) · [quality-compliance/](quality-compliance/) | Receive immediately increases one available-stock fact; labels for inspection or quality do not prove quarantine, accept/reject, release or RTV control |
| PO→Invoice and PO→ledger links differ from three-way match | [ap-settlement-deepen/invoice_po_gr_match.md](ap-settlement-deepen/invoice_po_gr_match.md) | Invoice/AP copy the PO header amount without receipt-line, quantity, price, tolerance or variance matching; structural links alone are not reconciliation |
| AP and payment views differ from a supplier balance authority | [ap-settlement-deepen/](ap-settlement-deepen/) · [ap-payment-deepen/](ap-payment-deepen/) | AP balances remain unchanged by supplier payments; no allocation, partial clearing, write-off or reconciled supplier subledger unifies liability and cash facts |
| Module permission differs from object- and tenant-scoped command authorization | [command-authz-deepen/server_route_coverage.md](command-authz-deepen/server_route_coverage.md) · [command-authz-deepen/object_tenant_scope.md](command-authz-deepen/object_tenant_scope.md) | Per-route opt-in checks and list filters do not prove that the mutated object belongs to the authorized owner or tenant |
| GET mutation or privileged bypass differs from intentional, audited override | [command-authz-deepen/get_mutation_surface.md](command-authz-deepen/get_mutation_surface.md) · [command-authz-deepen/audited_override.md](command-authz-deepen/audited_override.md) | GET writes bypass unsafe-method CSRF semantics, while role short-circuits generally lack explicit reason, scope, approval and durable override decisions |
| DO “Invoice” / NDE print differs from a sales tax-invoice master | [tax-invoice-deepen/](tax-invoice-deepen/) · [ship-complete-deepen/do_invoice_ar.md](ship-complete-deepen/do_invoice_ar.md) | Post AR and printable NDE artifacts do not create, calculate, void or credit a tax invoice entity |
| Currency fields differ from governed FX conversion and revaluation | [fx-revaluation-deepen/](fx-revaluation-deepen/) · [locale-commerce/currency.md](locale-commerce/currency.md) | Seed rates and quote snapshots do not prove effective-dated FX, Convert propagation, period revaluation or cross-currency clearing |
| Approval Center hub differs from V18 business release gates | [approval-center-deepen/](approval-center-deepen/) · [governance/approval.md](governance/approval.md) | Center approve/reject (including GET writes) and workflow scaffolds are not consumed by Quote/SO/Convert/Ship Type A confirms |
| Tax dictionary/settings differ from document tax calculation and filing | [tax-filing-deepen/](tax-filing-deepen/) · [locale-commerce/tax.md](locale-commerce/tax.md) | `tax_settings` / Tax Center records are not read by Quote/SO/DO/AR paths as tax engines or filing periods |
| AR accrual, NDE print and tax-invoice master remain three separate facts | [tax-filing-deepen/ar_print_separation.md](tax-filing-deepen/ar_print_separation.md) · [tax-invoice-deepen/](tax-invoice-deepen/) | Post AR, printable Invoice and absent sales tax-invoice master must not be collapsed |
| Credit Note template differs from AR credit posting | [tax-filing-deepen/credit_note_accounting.md](tax-filing-deepen/credit_note_accounting.md) · [return-reversal-policy-deepen/ar_credit_cancel.md](return-reversal-policy-deepen/ar_credit_cancel.md) | Printable/template credit notes do not reverse `ar_records` or receipts |
| Quote FX snapshot differs from SO/DO/receipt/payment FX propagation | [fx-propagation-deepen/](fx-propagation-deepen/) · [fx-revaluation-deepen/](fx-revaluation-deepen/) | Convert and downstream cash paths do not persist quote currency/rate; receipts may hardcode USD |
| `create_approval` definition differs from business-chain submit hooks | [approval-submit-hooks-deepen/](approval-submit-hooks-deepen/) · [approval-center-deepen/](approval-center-deepen/) | No active apps handler calls `create_approval`; Quote/SO/Convert/Ship do not create central approval rows |
| Center GET approve/reject differs from CSRF-safe intentional override | [approval-submit-hooks-deepen/get_approve_reject_surface.md](approval-submit-hooks-deepen/get_approve_reject_surface.md) · [command-authz-deepen/get_mutation_surface.md](command-authz-deepen/get_mutation_surface.md) | GET mutations are treated as SAFE by CSRF middleware and are not audited override commands |

## Phase-15 depth spot check

| Track | Required outputs | Rules / validations / evidence | Result |
|-------|------------------|--------------------------------|--------|
| A — Credit Control Deepen | README + INDEX + 4 bodies | Per body: 22–24 / 12–18 / 10–12 | PASS |
| B — Partial Fulfillment Deepen | README + INDEX + 4 bodies | Per body: 19–20 / 12–14 / 11–12 | PASS |
| C — Numbering Collision Deepen | README + INDEX + 4 bodies | Per body: 22–30 / 12–13 / 16–19 | PASS |
| D — Research dual-write fields | 10 × `DUAL_WRITE_FIELD_CARD.md` | Present; intake remains **0 Complete** | PASS |

## Phase-16 depth spot check

| Track | Required outputs | Rules / validations / evidence | Result |
|-------|------------------|--------------------------------|--------|
| A — Procurement Receipt Deepen | README + INDEX + 4 bodies | Lifecycle, receipt posting, stock conservation and quantity-control coverage present | PASS |
| B — AP Payment Deepen | README + INDEX + 4 bodies | AP lifecycle, payment posting, PO/GR trace and reconciliation-gap coverage present | PASS |
| C — Permission Surface Deepen | README + INDEX + 4 bodies | Per body: rules ≥20, validations =12, evidence rows ≥16, UNKNOWN rows =9 | PASS |

## Phase-17 depth spot check

| Track | Required outputs | Rules / validations / evidence | Result |
|-------|------------------|--------------------------------|--------|
| A — PO Receive Control Deepen | README + INDEX + 4 bodies | Per body meets rules ≥8, validations ≥6, data semantics ≥8, evidence ≥6 and UNKNOWN+paths ≥5 | PASS |
| B — AP Settlement Deepen | README + INDEX + 4 bodies | Per body meets rules ≥8, validations ≥6, data semantics ≥8, evidence ≥6 and UNKNOWN+paths ≥5 | PASS |
| C — Command Authorization Deepen | README + INDEX + 4 bodies | Per body: rules 22–25, validations =12, data semantics 16–20, evidence 22–24, UNKNOWN rows =9 | PASS |
| D — Research authorization exceptions | 10 × `AUTHZ_EXCEPTION_CARD.md` | Present; ≥6 observations, ≥5 live-evidence needs and ≥3 HARD HOLD each; intake remains **0 Complete** | PASS |

## Phase-18 depth spot check

| Track | Required outputs | Rules / validations / evidence | Result |
|-------|------------------|--------------------------------|--------|
| A — Tax Invoice Deepen | README + INDEX + 4 bodies | Per body: 16–18 / 12 / 10–12 | PASS |
| B — FX / Revaluation Deepen | README + INDEX + 4 bodies | Per body: 15–18 / 10–12 / 10–12 | PASS |
| C — Approval Center Deepen | README + INDEX + 4 bodies | Per body: 14–16 / 10–12 / 10–12 | PASS |
| D — Research approval boundaries | 10 × `APPROVAL_BOUNDARY_CARD.md` | Present; intake remains **0 Complete** | PASS |

## Phase-19 depth spot check

| Track | Required outputs | Rules / validations / evidence | Result |
|-------|------------------|--------------------------------|--------|
| A — Tax Filing Deepen | README + INDEX + 4 bodies | Per body: 16–17 / 12 / 9–11 | PASS |
| B — FX Propagation Deepen | README + INDEX + 4 bodies | Per body: 18 / 12 / 12 | PASS |
| C — Approval Submit Hooks Deepen | README + INDEX + 4 bodies | Per body: 16 / 12 / 12 | PASS |
| D — Research tax/FX/approval cards | 10 × `TAX_FX_APPROVAL_FIELD_CARD.md` | Present; intake remains **0 Complete** | PASS |

## Hard boundaries

| Do | Do not |
|----|--------|
| Paraphrase rules / flows / checks / semantics | Copy Legacy source or trees |
| Cite read-only Legacy paths | Modify anything under `EZAM_CRM*` |
| Note gaps honestly | Inherit Legacy architecture as EAOS truth |
| Write only under `docs/knowledge/legacy-extract/**` | Open Brain execute / Twin authorize / premature CRM CRUD |

This Phase-19 merge opens no product/business CRUD, Terminal product surface or AI execution; changes no code, tip, `PROJECT_STATUS` or `CHANGELOG`; changes no Research `Complete` state; and allocates no PHX-G milestone.

## Opportunity / sample / quote / fulfillment chain map (Legacy observed)

`Customer → Opportunity (default open) → Requirement (1:N; cached count) → Sample intake`

Sample side (gates are weak / often absent):

`Sample → [optional analysis / quality scores] → bind product → Sample Receipt / Stocked`  
`Sample → Draft Quotation (often zero lines; product not auto-lined) → optional Approve(Sent)`

Commercial continuation:

`Draft Quote → [optional Quote Approve: Sent] → Convert SO → Quote 已确认 + SO pending`  
(`Sent` / central approval are not Convert prerequisites; commercial terms mostly do not propagate.)

Conversion side effects are not one atomic chain:

- Main result: `Quote → SO`
- Best-effort trace: `Requirement / Opportunity / Quote → SO links`
- Best-effort commission: `SO total × salesperson-level rate → TC ledger Pending`

Fulfillment continuation:

`SO pending → [optional SO Approve: Open] → Create DO → Ship (inventory posting) → Complete (DO + SO Delivered)`

`Complete → Reopen` changes statuses only; it does not reverse inventory or AR. `DO → Post AR` is a separate, warning-only-gated path and can precede Ship. `SO → Receipt` remains separate and does not close TC commission or allocate `ar_records`.

Contract is **not** a first-class CRM stage (see [crm/contract.md](crm/contract.md)). Inventory/Procurement are operational side chains; Governance is an overlay, not an extra revenue-chain stage.

## Acceptance boundary

PHX-G290–G292 Accepted domain extracts; **PHX-G293** Accepted the cross-pack [Sample knowledge pack](../sample-pack/) (assembly for Terminal demo / Research — ≠ Legacy「客户来样」`sample/`). Remaining Extracted packs do not implicitly allocate PHX-G294+; a later grouped acceptance must first choose scope and add its own gate, acceptance record, ADR and contract checks.

## Rewrite boundary ADRs (Accepted — boundary only)

Gap review after Phase-19; CA Accept under DAL-G003/G004 on 2026-07-23. **Accepted ≠ product Gate ≠ CRM CRUD.**

| Pri | ADR | Title |
|-----|-----|-------|
| P0 | [0312](../../decisions/ADR-0312-quote-convert-rewrite-boundary.md) | Quote→SO Convert Rewrite Boundary |
| P0 | [0313](../../decisions/ADR-0313-command-authz-rewrite-boundary.md) | Command Authorization Rewrite Boundary |
| P1 | [0314](../../decisions/ADR-0314-fulfillment-rewrite-boundary.md) | Fulfillment (SO→DO→Ship) Rewrite Boundary |
| P1 | [0315](../../decisions/ADR-0315-ar-ap-reconcile-rewrite-boundary.md) | AR/AP Reconcile Rewrite Boundary |
| P2 | [0316](../../decisions/ADR-0316-tax-invoice-rewrite-boundary.md) | Tax Invoice Rewrite Boundary |
| P2 | [0317](../../decisions/ADR-0317-fx-propagation-rewrite-boundary.md) | FX Propagation & Revaluation Rewrite Boundary |
| P2 | [0318](../../decisions/ADR-0318-approval-wiring-rewrite-boundary.md) | Approval Wiring Rewrite Boundary |

**Stop condition for deepen:** no Phase-20 same-style packs by default. Next product work needs an explicit Gate + Package Surface slice per Accepted boundary (still no premature CRM CRUD). Foundation may harden toward ADR-0313 without inventing business modules.

## Next knowledge candidates

1. Live tax/FX/approval/dual-write field artifacts for T2/T3 (keep intake **0 Complete** until real evidence).
2. First product Gate candidate: Package/Terminal command-authz alignment with ADR-0313 (declarative surfaces only).
3. Optional narrow extract only when a Gate review finds a concrete evidence hole.
