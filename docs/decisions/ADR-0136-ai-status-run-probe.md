# ADR-0136 — AI Runtime Status / Run Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G117  
**归属：** Smart Terminal / AI Runtime

## 背景

G29 已交付 AI Runtime HTTP（runs/tools/memory/approvals/commits）。运维仍缺 Terminal 内对状态与 run create/get 的薄调用面。

## 决策

1. 新增只读 `GET /v1/ai/status`（`writable=false`；声明 `ai_subject_required`、`commit_requires_approval` 与支持面）。  
2. Terminal Admin 增加 AI Runtime status、Create AI run、Get AI run。  
3. Create/Get 经 trusted header 使用 `X-EAOS-Subject-Type: ai_employee`（可选 `subjectType` 参数）；禁止 body 上下文提升。  
4. tools / memory / approvals / commits Terminal 探针另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- AI tools / memory Terminal 薄探针（见 G118）  
- AI approvals / commits Terminal 薄探针  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  
- Role→Policy 绑定  

## 关联

- [ADR-0135-brain-execute-fail-closed-probe.md](ADR-0135-brain-execute-fail-closed-probe.md)
- [../project/PHX-G117_ARCHITECTURE_GATE.md](../project/PHX-G117_ARCHITECTURE_GATE.md)
