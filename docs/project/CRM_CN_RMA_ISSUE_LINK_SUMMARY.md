# CRM CN ↔ RMA Issue Link Summary — PHX-G343

**Status:** TRACK-CN-RMA-ISSUE-LINK COMPLETE — implemented under the approved
coding authorization and ADR-0375.

Finance validates a linked RMA through the explicit `RmaCreditNoteLinkPort`
before issuing its credit note. The linked RMA must be restocked and reference
the same AR invoice as the credit note; otherwise issue fails closed with a
conflict. Credit notes without an RMA link retain the compatible issue path.

On a successful linked issue, the RMA records `credit_note_issued_at`; Alembic
tip is `0070_crm_cn_rma_issue_link_g343`. Restock never creates or issues a
credit note, and no refund, payment, tax-credit, Brain, or Twin behavior is
added.
