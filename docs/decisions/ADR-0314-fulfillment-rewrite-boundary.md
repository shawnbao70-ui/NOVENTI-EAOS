# ADR-0314 — Fulfillment (SO→DO→Ship) Rewrite Boundary

**状态：** Accepted（边界决策；非产品实现授权）  
**日期：** 2026-07-23  
**里程碑：** 未分配（产品切片须另开 Gate；本 ADR 不自开 PHX-G）  
**归属：** Knowledge Driven → future Delivery / Inventory Package Surface  
**授权：** DAL-G003 / DAL-G004（CA Accept 重写边界）；仍不得凭本文件打开 CRUD / Kernel / Alembic

## 背景

Legacy 知识抽取表明：一 SO 可重复创建全量行 DO、无已发/剩余量守恒；Ship 幂等为应用层读后写且无 DB 唯一键；库存/产品镜像/台账三写无证明的事务守恒；Complete→Reopen 只改状态不冲库存且挡住合法重发；Reopen≠退货/RMA；承运/POD 未接入生产 DO 状态机。MASTER_PLAN 禁止过早业务模块；本 ADR 只固定 **EAOS 重写边界**。

主要证据包（只读）：

- `docs/knowledge/legacy-extract/partial-fulfillment-deepen/**`
- `docs/knowledge/legacy-extract/ship-idempotency-deepen/**`
- `docs/knowledge/legacy-extract/return-reversal-policy-deepen/**`
- `docs/knowledge/legacy-extract/ship-complete-deepen/**`
- `docs/knowledge/legacy-extract/fulfillment-deepen/**`
- 根索引矛盾表（Multi-DO、Ship guard、Reopen vs return）

## 决策

1. **Legacy 履约行为不得原样继承为 EAOS 默认策略**（含「每次 DO 复制全量 SO 行」「单 DO 状态覆盖 SO」）。  
2. **数量守恒为硬门禁**：创建/发运必须基于已承诺、已分配、已发、剩余量；禁止无剩余量控制的重复全量 DO；超发须显式 override 命令（有审计），不得静默允许。  
3. **SO 履约状态须由累计发运证据聚合**，不得由任一 DO Complete/Reopen 直接覆盖为唯一真相。  
4. **Ship 命令身份与幂等** 须由事务权威保证（唯一约束 / 命令键 / 发运身份），不得仅依赖读后写；并发第二次 Ship 必须可判定为冲突或幂等重放，而非幽灵双扣。  
5. **库存扣减、产品镜像、台账（及后续 AR 挂钩）须同事务或明确补偿**；成功路径须可证明守恒，失败须可观察，不得「部分成功且无回滚」。  
6. **Reopen / Unship / Return / Reship 分离建模**：  
   - Reopen（状态回退）≠ 库存冲销 ≠ 授权二次 Ship；  
   - 退货/RMA 为独立能力（库存回补、可选 AR 贷项、佣金影响另契约）；  
   - 受控重发须新发运身份或显式解除原幂等键的审计命令。  
7. **承运/跟踪/POD** 若进入产品面，须挂钩发运身份；Complete 不得仅等于「人手确认」而无可引用证据策略（策略可配置，但须显式）。  
8. **本 ADR 不打开** DO/Ship/库存产品 CRUD、Terminal 真业务面、Alembic、Brain execute、Twin authorize。

## 后果

- 后续 Delivery/Inventory Package Surface 必须以数量守恒与发运身份为本输入。  
- Smart Terminal 演示移交不构成本 ADR 的实现。  
- Research 可将多 DO 超发、Reopen 重发陷阱作为 live 采集主题；intake Complete 不因本提案改变。

## 非目标

- 不规定仓/批/序列号具体 schema  
- 不选择 WMS 集成形态  
- 不规定退货会计科目与税票红冲（见税/财务后续 ADR）  
- 不分配产品 PHX-G；业务 CRUD 须另开 Gate（本 ADR 仅为重写边界）

## 关联

- [ADR-0312](ADR-0312-quote-convert-rewrite-boundary.md) Convert 边界（Accepted）  
- [ADR-0313](ADR-0313-command-authz-rewrite-boundary.md) 命令鉴权（Accepted；Ship/Reopen 写命令适用）  
- [ADR-0311](ADR-0311-legacy-knowledge-extract-delivery.md) Knowledge Delivery  
- [legacy-extract README](../knowledge/legacy-extract/README.md)  
- Gap review canvas: `legacy-extract-gap-review`
