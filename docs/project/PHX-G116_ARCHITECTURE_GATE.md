# PHX-G116 Brain Execute Fail-Closed Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Brain  
**规范源：** ADR-0135  
**人工确认：** 不打开 execute 执行权；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Brain execute 做 fail-closed 薄探针；Brain Terminal 运维面齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Execute brain insight（expect 403） |
| API | 仅调用既有 execute；恒 403 |
| Out | 打开执行权；支付清算；Role→grant |

## 3. Exit Criteria

1. ADR-0135 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G116_ACCEPTANCE.md](PHX-G116_ACCEPTANCE.md)。
