# Marketplace 状态机

**文档 ID：** SM-MKT-001  
**版本：** 1.0  
**阶段：** PHX-M16

## Listing

```text
draft ──attach_signature──► draft
draft ──submit────────────► submitted
submitted ──approve───────► approved
submitted ──reject────────► rejected
rejected ──submit─────────► submitted
approved ──publish────────► published
published|approved ──revoke──► revoked
```

## Acquisition

技术获取记录；无商业结算状态机。
