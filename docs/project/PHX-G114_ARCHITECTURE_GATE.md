# PHX-G114 Twin Authorize Fail-Closed Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Twin  
**规范源：** ADR-0133  
**人工确认：** 不打开 authorize 执行权；Brain Terminal 另批；支付清算另批；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Twin authorize 做 fail-closed 薄探针；Twin Terminal 运维面齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Authorize from twin（expect 403） |
| API | 仅调用既有 authorize；恒 403 |
| Out | 打开执行权；Brain Terminal；支付清算 |

## 3. Exit Criteria

1. ADR-0133 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G114_ACCEPTANCE.md](PHX-G114_ACCEPTANCE.md)。
