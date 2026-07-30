# CRM Return Credit Note Summary

**TRACK-RET-CREDIT-NOTE COMPLETE / tip `0066_crm_return_credit_note_g337`**

PHX-G337 adds an explicit, permission-gated command that creates one draft AR
Credit Note from a restocked Return Authorization with an invoice lineage. The
RMA stores its auditable credit-note link and request key; restocking alone
does not create or issue a credit note.

Out of scope: credit-note issue, refund payout, GL, tax void coupling,
Cap→grant, and Brain/Twin commercial writes. PHX-G338 remains queued only.
