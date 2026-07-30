# ADR-0420 — Remediation Contract Tip Helper Boundary

**状态：** Accepted（PHX-G406）  
**日期：** 2026-07-27  
**里程碑：** PHX-G406  
**授权源：** [Coding Authorization](../project/REMEDIATION_P0_TIP_HELPER_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 契约测试的现行 tip / package 只从一个 helper 读取：Alembic `ScriptDirectory` head +
   `RELEASE_MANIFEST.yaml`（二者必须一致）。  
2. 历史契约不得再把冻结 revision（如 `0049_…`）断言为 `get_current_head()`；
   可断言 revision 存在或为祖先。  
3. 本切片无 Alembic、无包版本 bump、无功能里程碑。  
4. REPAIR FREEZE：功能 G 冻结至 G0+G1 绿。
