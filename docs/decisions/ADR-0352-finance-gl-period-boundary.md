# ADR-0352 — Finance GL Period + Close Boundary

**状态：** Accepted（design + coding boundary for PHX-G320 / GL2）  
**日期：** 2026-07-26  
**里程碑：** PHX-G320  
**归属：** Business Package / Finance（非 Kernel）  
**授权源：** [Coding Authorization Summary](../project/FIN_GL_PERIOD_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

GL1 交付了科目表与平衡分录，但无会计期间。Legacy 知识显示期间关账为强缺口；EAOS 须新建期间模型，不得从佣金期间或“close authority”叙述继承。

## 决策

1. **GlPeriod** 是租户内会计期间：opaque id、code、start/end（含端点规则在实现中固定）、status∈{open,closed}。  
2. **Close** 仅 `open → closed`，需 human_confirm，不可逆；本切片不提供 reopen。  
3. **JournalEntry** 必须绑定 period；`post` 在 period 缺失或 closed 时 fail closed。  
4. 资源类型：`pkg.finance.gl_period`。  
5. GL3–GL5、FX 重估、银行对账、Brain/Twin 均 Out。

## 后果

- 过账受期间约束；关账后不得向该期间继续过账。  
- 结转分录/年结/重估留待后续切片。

## 非目标

- 软重开、多账簿、自动结转、FX 重估、银行对账、桥接过账

## 关联

- [ADR-0351](ADR-0351-finance-gl-chart-journal-boundary.md)  
- [Coding Authorization](../project/FIN_GL_PERIOD_CODING_AUTHORIZATION_SUMMARY.md)  
- [POST_CRM_VERTICAL_ROADMAP](../project/POST_CRM_VERTICAL_ROADMAP.md)
