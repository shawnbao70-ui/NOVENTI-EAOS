# ADR-0351 — Finance GL Chart + Journal Shell Boundary

**状态：** Accepted（design + coding boundary for PHX-G319 / GL1）  
**日期：** 2026-07-26  
**里程碑：** PHX-G319  
**归属：** Business Package / Finance（非 Kernel）  
**授权源：** [Coding Authorization Summary](../project/FIN_GL_CHART_JOURNAL_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

Post-CRM 队列在税票端口之后进入总账竖切。既有 AR/税票/收款壳明确将 GL/CoA/journal 列为 Out。GL1 建立最小可记账基础：科目表与平衡分录，不打开期间关闭、桥接、FX 或银行对账。

## 决策

1. **GlAccount** 是租户内科目主数据：opaque id、tenant-scoped code、name、type∈{asset,liability,equity,revenue,expense}、status∈{active,archived}。  
2. **JournalEntry** 生命周期 `draft → posted`；posted 不可逆；至少两行；debit 合计 = credit 合计；行引用同租户 active（或已绑定）科目。  
3. 资源类型：`pkg.finance.gl_account`、`pkg.finance.journal_entry`。  
4. HTTP：`/v1/finance/gl-accounts`、`/v1/finance/journal-entries`（含 post）。  
5. GL2–GL5、Brain/Twin、实网税局均 Out。

## 后果

- Finance Package 获得可审计的最小总账写路径，但不构成完整会计引擎。  
- 期间、桥接、FX、银行对账须各自独立里程碑。

## 非目标

- 会计期间 / close、多账簿、自动过账桥、FX 重估、银行对账  
- Legacy GL 表结构或插件继承

## 关联

- [POST_CRM_VERTICAL_ROADMAP](../project/POST_CRM_VERTICAL_ROADMAP.md)  
- [Coding Authorization](../project/FIN_GL_CHART_JOURNAL_CODING_AUTHORIZATION_SUMMARY.md)  
- [ADR-0315](ADR-0315-ar-ap-reconcile-rewrite-boundary.md)（不打开 GL 引擎的前置 defer）
