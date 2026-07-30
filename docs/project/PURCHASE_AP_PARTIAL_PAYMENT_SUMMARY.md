# Purchase AP Partial Payment Summary

**TRACK-AP-PARTIAL-PAYMENT COMPLETE / tip `0068_purchase_ap_partial_payment_g341`**

PHX-G341 persists the authoritative AP bill `paid_amount`, supports multiple
idempotent partial payment applies through paid settlement, rejects over-apply,
and exposes paid and remaining amounts on AP bill reads. PSP, GL, AR, Brain,
and Twin scope remains unchanged.
