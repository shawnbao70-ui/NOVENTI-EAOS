# CRM Vertical Roadmap（Architect-owned sequencing）

**状态：** Active · Product Owner delegated sequencing 2026-07-24  
**框架：** ADR-0321（Decision Summary → design Approve → Gate 制品 → Coding Auth → 实现）  
**里程碑策略：** 一律 next free contiguous PHX-G；不跳号；不并行第二里程碑  
**主机软件：** 未经 PO 另批，不得安装/修改

## 已完成

| Slice | Milestone | Outcome |
|---|---|---|
| C1 Customer + Contact | PHX-G294 | COMPLETE |
| C2 Opportunity | PHX-G295 | COMPLETE |
| C3 Requirement | PHX-G296 | COMPLETE |
| C4 Quote draft shell | PHX-G297 | COMPLETE |
| C5 Quote Convert instruction | PHX-G298 | COMPLETE |
| C6 Sales Order shell | PHX-G299 | COMPLETE |
| C7 Quote lines | PHX-G300 | COMPLETE |
| C8 SO confirmation | PHX-G301 | COMPLETE |
| C9 Delivery Order shell | PHX-G302 | COMPLETE |
| C10 AR Invoice shell | PHX-G303 | COMPLETE |
| C11 Commercial Hold gate | PHX-G304 | COMPLETE |
| C12 Confirm Approval hook | PHX-G305 | COMPLETE |
| C13 Quote Issue (local publish) | PHX-G306 | COMPLETE |
| C14 Delivery Order Release (status-only) | PHX-G307 | COMPLETE |
| C15 AR Invoice Issue (local, no posting) | PHX-G308 | COMPLETE |
| C16 AR Invoice Void (local, no credit/GL) | PHX-G309 | COMPLETE |

## Wave A / B / C / D / E / E′ / F / F′ — 已收口

- Wave A：C6 / G299  
- Wave B：C8 / G301  
- Wave C：C10 / G303  
- Wave D：C12 / G305（Alembic `0041_crm_confirm_approval_hook_g305`）  
- Wave E：C13 / G306（Alembic `0042_crm_quote_issue_g306`）  
- Wave E′：C14 / G307（Alembic `0043_crm_delivery_order_release_g307`）  
- Wave F：C15 / G308（Alembic `0044_crm_ar_invoice_issue_g308`）  
- Wave F′：C16 / G309（Alembic `0045_crm_ar_invoice_void_g309`）  

## CRM VERTICAL WAVE STOP（C1–C16）

Declared CRM vertical slices C1–C16 are complete. **C17+ 未声明** — requires a new PO wave
(e.g. Finance receipt/posting, WMS ship). Do not self-open.

Out still hard: depth Finance/GL/PSP, WMS inventory ship, Brain/Twin, full credit
engine, Approval Center product expansion, AR posting/tax/receipt/credit note.

## Wave R / I / N / Z pointer（post-CRM）

Post-CRM sequencing（含 Z2 及之后队列）以
[`POST_CRM_VERTICAL_ROADMAP.md`](POST_CRM_VERTICAL_ROADMAP.md) 为唯一真源。
F1→I1→N1→Z1 COMPLETE；**下一步 = Z2 Coding Auth（PHX-G314 / 0049）**。
CRM C17+ remains closed.

## PO 委托含义

- 阶段顺序与 In/Out 由本文件裁定。  
- 每阶段仍走 ADR-0321；design Gate 与 Coding Authorization 必须使用两个
  独立 Summary 和两个独立决策。即使同一对话中连续审批，也不得合并状态；
  PO 仅回复 Approve / Amend / Reject，里程碑须在 Coding Summary 审批前列明。  
- 「完成」默认指当前 Wave 的 STOP 行。
