# ADR-0177 — Autonomous Soft-Queue Natural Pause

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G158  
**归属：** Phoenix Governance / Dual-Track operating tip  
**授权：** DAL-G003 + DAL-G004（AED v1.1）；Usage **DAL-U030**

## 背景

在 PHX-G144…G157 之后，Eng Explicit Defer `1`–`3` thin/stub deepen、Foundation 卫生、Research AR queue 与 T2/T3 readiness（地板 T1）均已齐。OpenAPI↔Gateway 挂载已无「缺几条只读路由」可薄切。继续「继续」若再 invent tip/hygiene/空 posture，违反 AED soft-invent 纪律并降低架构质量。

## 决策

1. 正式记录 **Autonomous Soft-Queue Natural Pause**（PHX-G158）：无新 Gateway/Kernel 产品开口。  
2. 更新 `ENG_SOFT_QUEUE_TIP.md` / `PROJECT_STATUS.md`：Next = **gated**（Board / live T2–T3 / mint-with-PO / Eng `4` PO / 审慎大切片 OpenAPI）。  
3. 「继续」在 Pause 期间 **不** 自动 invent 新产品面；仅在 HARD HOLDS 被明确打开或 Board/现场证据到达后恢复自主切片。  
4. 包仍 **`0.2.1`**；Alembic 仍 **`0029`**；docs-only。

## Explicit Out（本切片不开口）

- Live WebAuthn mint / Role→grant live mint  
- Eng `4` 支付清算  
- Brain execute / Twin authorize  
- AR Board self-certify / Const/BP rewrite  
- 全量 OpenAPI 语义大切片（未获审慎授权前）  
- 空 hygiene invent 循环  

## 后果

- Tip 可读：自主 soft-queue 已暂停；恢复条件明确。  
- 下一「继续」若无新授权 → 重复 Pause 报告，不 invent。

## 关联

- [../project/ENG_SOFT_QUEUE_TIP.md](../project/ENG_SOFT_QUEUE_TIP.md)  
- [../project/PHX-G158_ARCHITECTURE_GATE.md](../project/PHX-G158_ARCHITECTURE_GATE.md)  
- [../project/PHX-G158_ACCEPTANCE.md](../project/PHX-G158_ACCEPTANCE.md)  
- [ADR-0169-autonomous-execution-directive.md](ADR-0169-autonomous-execution-directive.md)  
- [../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md](../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)  
