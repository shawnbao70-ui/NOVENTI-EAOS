# PHX-G142 Organization Get Enterprise Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**规范源：** ADR-0161  
**人工确认：** 仅薄接线既有 GET；无 Alembic/版本 bump  

## 1. 门禁目标

补齐 Terminal 对 `GET /v1/enterprises/{id}` 的薄运维控件。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| API | 既有 `GET /v1/enterprises/{enterprise_id}` |
| UI | Get enterprise |
| Docs | `api/README.md` Terminal 目录同步 G140–G142 |
| Out | 支付清算；Role→grant；WebAuthn；`0.2.1` |

## 3. Exit Criteria

1. ADR-0161 Accepted。  
2. Terminal + 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G142_ACCEPTANCE.md](PHX-G142_ACCEPTANCE.md)。
