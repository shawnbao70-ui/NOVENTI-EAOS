# ADR-0348 — Finance Receipt PSP Port

**Status:** Accepted — system-generated governance artifact  
**Package:** `noventi.finance`  
**Evidence:** `FIN_RECEIPT_PSP_PORT_CODING_AUTHORIZATION_SUMMARY.md`

Receipt application remains draft-to-applied. A tenant may opt into PSP
verification through a versioned Finance-owned policy. When opted in,
`PspPort` is mandatory; its default implementation rejects the operation with
`CONFLICT` and “PSP port is unavailable”. No network adapter is provided.

The port result is persisted on the receipt only after a successful response.
Policy reads/writes remain tenant-scoped, permissioned, audited, and reject
client context override.
