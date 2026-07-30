# ADR-0417 — Terminal Extension Signature + Invoke Honesty

**状态：** Accepted（PHX-G396 / PHX-G397）  
**日期：** 2026-07-27  

## 决策

1. Activate 要求签名；unsigned → fail-closed。
2. Invoke 保持 sandboxed；`executed=false`；无 grant → fail-closed。
3. Terminal 不持有业务真相；无 Alembic。
