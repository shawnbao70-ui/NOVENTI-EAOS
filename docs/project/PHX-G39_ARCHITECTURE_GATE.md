# PHX-G39 Terminal Extension Host Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation Host）  
**归属：** Smart Terminal  
**规范源：** ADR-0057  

## 1. 门禁目标

交付 Foundation Extension Host：清单注册、签名门槛、沙箱拒绝特权能力、受治理 invoke。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Smart Terminal；无业务真相 |
| Runtime | 无任意代码执行（本切片） |
| Sandbox | 禁止能力 + 拒网络 |
| UI | Extensions 表面呈现 |

## 3. Exit Criteria

1. ADR-0057 Accepted。  
2. 未签名不可激活；禁止能力拒绝。  
3. Gateway + UI + 契约绿。  
4. 无 schema 变更（进程内登记）。
