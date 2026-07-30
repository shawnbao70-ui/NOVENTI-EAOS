# Commercial Chain Observation Protocol

**Template ID:** NRI-TPL-COMMERCIAL-CHAIN  
**Version:** 1.0  
**Status:** Live observation protocol — not transaction authority and not Complete  
**Last Updated:** 2026-07-23  
**Governing:** [SITE_ACCESS_PACK.md](SITE_ACCESS_PACK.md) · [FIELD_CAPTURE_KIT.md](FIELD_CAPTURE_KIT.md) · [INTERVIEW_PROTOCOL.md](INTERVIEW_PROTOCOL.md) · [OBSERVATION_LOG.md](OBSERVATION_LOG.md) · [CHAIN_OF_CUSTODY.md](CHAIN_OF_CUSTODY.md)

> Observe the existing sample → quotation → order → shipment → receipt/payment chain. Research personnel must never create, approve, release, alter, acknowledge, invoice, settle, refund, or accept a commercial transaction. Observing the chain is not evidence verification or Complete.

## 1. Protocol identity and scope

| Field | Required value |
|-------|----------------|
| Chain observation ID | `CCO-LC-YYYYMMDD-RP-00N-##` |
| LC ID / RP / claimed tier | |
| Named enterprise/site/tenant | |
| Product/sample/customer scope | Tokenized/minimum necessary |
| Observation window + timezone | |
| In-scope chain stages | Sample / quote / order / shipment / receipt / invoice / payment |
| Explicit exclusions | |
| Observer / escort / custodians | Real assigned identities only |
| Access / consent / custody refs | |

## 2. Purpose and research boundary

State the question being tested, why an end-to-end chain is necessary, and which RP claims it can support or challenge. The protocol is observational:

- Read-only or escorted views only.
- No synthetic record may be mixed into live chain evidence.
- No customer/vendor contact on behalf of the enterprise.
- No operational action, approval, override, posting, fulfillment, collection, or payment.
- No Brain execute, Twin authorize, role/capability→grant, or Terminal product opening.

## 3. Chain actors and systems

| Stage | Business role(s) | System(s) | Accountable owner | Approval/control | Evidence generated |
|-------|------------------|-----------|-------------------|------------------|-------------------|
| Sample/request | | | | | |
| Quotation | | | | | |
| Order/acceptance | | | | | |
| Fulfillment/shipment | | | | | |
| Delivery/receipt | | | | | |
| Invoice/receivable | | | | | |
| Payment/clearing | | | | | |

Roles are descriptions, not assigned interviewees or observers. Record real identities only under approved need.

## 4. Pre-observation gate

- [ ] A real existing chain instance is selected by the enterprise; Research did not initiate it.
- [ ] Scope tokens replace unnecessary customer, person, address, price, bank, tax, and product-sensitive fields.
- [ ] Read-only/escorted access and exact systems/screens/exports are approved.
- [ ] Commercial, customer, payment, tax, trade, privacy, security, and recording controls are documented.
- [ ] Observer cannot submit/approve buttons, API calls, workflow tasks, messages, or payments.
- [ ] Incident, suspected fraud, sanctions/export-control, safety, and security escalation routes are known.
- [ ] Source clocks, identifiers, versions, and chain-correlation method are established.

## 5. Stage A — sample/request

Observe:

1. Trigger and channel for sample/request.
2. Product/specification/version and quantity at minimum granularity.
3. Customer/account eligibility or consent control without copying unnecessary identity.
4. Ownership, approval, inventory/availability, and exception handling.
5. Record/identifier created and evidence retained.

Do not create a sample, promise availability, or contact a customer.

## 6. Stage B — quotation

Observe:

1. Inputs from sample/request and product/customer context.
2. Price, currency, tax, validity, terms, discounts, and approval rules.
3. Versioning, supersession, negotiation, and exception path.
4. Separation of draft, approved, sent, accepted, expired, and rejected states.
5. Quote artifact, audit event, and customer communication evidence.

Do not calculate/approve a real price or send/accept a quote.

## 7. Stage C — order/acceptance

Observe:

1. Conversion/link from quote or approved alternate basis.
2. Customer acceptance, contract/terms, credit/compliance, and authority checks.
3. Product, quantity, price, currency, tax, dates, and delivery terms reconciliation.
4. Duplicate, change, cancellation, backorder, and exception controls.
5. Order record, approvals, version, and audit evidence.

Do not place, confirm, approve, change, or cancel an order.

## 8. Stage D — fulfillment/shipment

Observe:

1. Release criteria, allocation/pick/pack, lot/serial/specification controls.
2. Warehouse/plant/logistics roles and segregation of duties.
3. Safety, trade/export, carrier, address, and document checks.
4. Partial shipment, substitution, damage, hold, and cancellation paths.
5. Shipment/despatch record, tracking, timestamps, and chain link.

Do not release inventory, instruct warehouse/carrier, or alter shipment data.

## 9. Stage E — delivery/receipt

Observe:

1. Delivery event, proof of delivery/receipt, quantity/condition, and timestamp.
2. Discrepancy, refusal, damage, short/over delivery, and return path.
3. Customer communication and accountable acceptance boundaries.
4. Link from shipment to receipt and downstream billing trigger.
5. Retention and dispute evidence.

Do not acknowledge receipt, sign, accept on behalf, or resolve a dispute.

## 10. Stage F — invoice/receivable

Observe:

1. Billing trigger and reconciliation to order/shipment/receipt.
2. Invoice number/version, tax/currency/terms, and approval/exception controls.
3. Credit/debit note, dispute, duplicate, cancellation, and adjustment path.
4. Receivable posting and segregation of duties.
5. Invoice/audit artifacts and customer communication evidence.

Do not issue/post/void an invoice or approve financial adjustments.

## 11. Stage G — payment/clearing

Observe:

1. Payment instruction origin and authorized channels.
2. Bank/provider reference, amount/currency/date matching, and allocation.
3. Sanctions/fraud/AML/security controls where applicable and legally observable.
4. Partial/over/under payment, failed payment, chargeback, refund, and unapplied cash paths.
5. Settlement/clearing confirmation, receivable closure, reconciliation, and audit trail.

Never request, initiate, approve, redirect, settle, refund, or clear funds. Never collect bank credentials or unrestricted account data.

## 12. End-to-end correlation and timing

| Stage | Tokenized business ID | Source system | Event timestamp / clock | Parent/child link | State/version | Artifact IDs |
|-------|-----------------------|---------------|-------------------------|-------------------|---------------|--------------|
| Sample | | | | | | |
| Quote | | | | | | |
| Order | | | | | | |
| Shipment | | | | | | |
| Receipt | | | | | | |
| Invoice | | | | | | |
| Payment | | | | | | |

Record clock skew, batch posting, asynchronous events, timezone conversion, retries, and manual bridging. Do not assume correlation from matching amounts/names alone.

## 13. Minimum artifact package

1. Dated observation log with direct/statement/inference separation.
2. Tokenized chain identifier map held by the authorized custodian.
3. Stage-state/version extracts or controlled handles.
4. Approval/control/audit events for high-impact transitions.
5. Exception/reversal/dispute evidence where observed.
6. End-to-end correlation and timing matrix.
7. Data-minimization, access, consent, custody, integrity, and retention records.
8. Contradictions, absent evidence, sampling limits, and falsifiers.

## 14. Exceptions and negative-path sampling

Do not induce failure. If naturally available and authorized, observe at least one:

- Quote expiry/revision/rejection.
- Order hold/change/cancellation/backorder.
- Partial/damaged/refused shipment or return.
- Invoice dispute/credit/debit adjustment.
- Failed/partial/unapplied/chargeback/refund payment.

Record whether the negative path was directly observed, historically evidenced, stated only, or unavailable.

## 15. Bias and ethics

- A “happy path” selected by a sponsor is not representative without declared sampling limits.
- Customer/vendor/worker identities and commercial terms are minimized and tokenized.
- Observer presence may change behavior; record escort, visibility, and prepared demonstrations.
- Fraud/sanctions/security disclosures follow approved channels and are not explored beyond necessity.
- Interview statements do not substitute for transaction/audit artifacts.
- Commercial success, revenue, or payment does not imply model correctness or product readiness.

## 16. Hard stops

Stop if:

1. Research is asked to perform, approve, release, accept, contact, sign, post, or pay.
2. Customer/vendor consent, site/system access, or transaction confidentiality basis is missing/revoked.
3. Credentials, payment secrets, bank data, unrestricted PII, fraud/security issues, or out-of-scope records appear.
4. Source IDs, timestamps, state versions, or chain links cannot be distinguished reliably.
5. Safety, production, legal, export-control, sanctions, tax, or financial-integrity risk emerges.
6. Anyone requests Registry Complete, floor flip, Promote, Eng opening, Brain execute, Twin authorize, or Const/BP change from the observation.

## 17. Reconciliation and closure

- [ ] No commercial action was performed by Research.
- [ ] All observed stages and unavailable stages are explicit.
- [ ] Stage IDs/timestamps/versions reconcile or conflicts are logged.
- [ ] Artifact IDs reconcile with custody records; restricted items remain controlled.
- [ ] Access/accounts are revoked and temporary extracts disposed.
- [ ] Exceptions, bias, missing roles, absent evidence, and falsifiers are recorded.

**Protocol outcome:** Not run / Stopped / Observed with gaps / Submitted for intake review  

Observed with gaps is not Complete. This protocol cannot itself verify T2/T3, flip a floor, Promote, open Eng work, authorize Brain/Twin/grants, or change Const/BP.
