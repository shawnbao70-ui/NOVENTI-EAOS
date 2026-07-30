# ADR-0007 — 多租户隔离（Tenant Isolation）

**状态：** 已接受  
**日期：** 2026-07-18  
**仓库：** `NOVENTI-EAOS`

---

## 上下文

EAOS 为全球多租户平台。隔离失效将导致数据泄露与宪法级违约。

## 决策

1. **默认隔离：** 一切租户作用域数据与操作必须绑定 `tenant_id`。  
2. **失败关闭：** 缺少租户上下文的副作用调用必须拒绝。  
3. **求值贯通：** API、Kernel、Event、Knowledge、AI Runtime 均强制租户校验。  
4. **禁止隐式跨租户：** 包括缓存、搜索索引、事件订阅与 AI 记忆。  
5. **平台运营例外：** 仅在法律要求或严重安全处置且可审计时，由受控平台治理通道执行（对齐 BOOK01 治理条款）。  

## 后果

- 数据模型标准要求业务实体含 `tenant_id`  
- 查询默认带租户谓词  
- 测试必须包含跨租户负面用例  
- 详见 [../constitution/BOOK02.md](../constitution/BOOK02.md)、[../constitution/BOOK05.md](../constitution/BOOK05.md)
