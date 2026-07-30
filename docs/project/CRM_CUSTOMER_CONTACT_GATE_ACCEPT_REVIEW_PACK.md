# RETIRED — Phase G CRM Customer + Contact Gate Accept Review Pack

**日期：** 2026-07-26  
**阶段：** G（人审准备包）  
**状态：** **RETIRED — historical evidence only**（原 `TRACK-G COMPLETE` 记录保留）  
**框架：** [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md) · [PHOENIX_GATE_FRAMEWORK](PHOENIX_GATE_FRAMEWORK.md)  
**本文件记录人审结果；不新开实现切片、不注册 runtime manifest。**

> 2026-07-28 起，本文件不得再作为活跃 PO 工作流、审批入口、Checklist
> 或签名表。下列勾选、回复模板和签名均为 2026-07-26 历史证据，不要求
> Product Owner 再填写。所有后续 Gate 仅使用九字段 Decision Summary；
> OD/RC/Approval/Signature/Evidence 由 Generator 自动生成。

---

## 0. 历史人审记录

本节保留 2026-07-26 Product Owner 对 **Customer + Contact 设计边界**
的复核结果；它不是当前操作要求，也不允许据此再次驱动状态。

```text
Accepted knowledge ≠ Gate Accept ≠ Coding Authorization
```

---

## 1. 评审对象索引

| 产物 | 路径 | 仓库当前状态行 |
|---|---|---|
| Decision Summary（PO 表单） | [CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md](CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md) | Approved — design boundary only；coding = None |
| ADR | [ADR-0320](../decisions/ADR-0320-crm-customer-contact-product-boundary.md) | Accepted（design boundary only；coding = None） |
| Architecture Gate | [CRM_CUSTOMER_CONTACT_ARCHITECTURE_GATE.md](CRM_CUSTOMER_CONTACT_ARCHITECTURE_GATE.md) | Gate Accepted（design-only；coding = None） |
| Acceptance | [CRM_CUSTOMER_CONTACT_ACCEPTANCE.md](CRM_CUSTOMER_CONTACT_ACCEPTANCE.md) | Gate Accepted（design-only）；实现授权 None |
| Proposed manifest | [packages/crm/manifest.proposed.json](../../packages/crm/manifest.proposed.json) | 非运行时；只读 inspect；`declared_events: []` |
| Coding Auth（**独立第二决策**） | [CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md](CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md) | 另有 Approve + **PHX-G294**（不在本包内“顺带接受”） |

---

## 2. 已完成的历史人工确认

| # | 事实 | 2026-07-26 历史选择 |
|---|---|---|
| G-1 | Design Gate 是否仍认可为 **Gate Accepted（design boundary only）**？ | [x] **Reaffirm** · [ ] Amend · [ ] Reject |
| G-2 | Coding authorization 在 **设计文书** 上是否继续保持 **None**（与 Gate Accept 分离）？ | [x] **Yes** · [ ] No（说明） |
| G-3 | C1 Coding Auth + PHX-G294 是否作为 **独立** 已批记录保留？ | [x] **Affirm coding auth** · [ ] Hold/void · [ ] N/A |
| G-4 | `manifest.proposed.json` 是否仍 **禁止** 注册/发布/安装/改名 runtime？ | [x] **Yes** |

**说明：** 设计文书写 `coding = None` / `milestone 未分配`，与 Coding Auth Summary 的 PHX-G294 **并存是框架预期**（第二决策）。人审须明确不要把两者混成一次批准。

---

## 3. Open Decisions（OD-01..OD-11）

| ID | Disposition | 编码前是否还需控制细节？ | 人审备注 |
|---|---|---|---|
| OD-01 | Accept proposed — 单一 lifecycle；archive 优先；词汇/restore 另约 | 是（最小状态集） | |
| OD-02 | Amend — opaque ID + tenant-scoped code/name；分群等 Defer | 是（ID/code）；Defer 项 n/a | |
| OD-03 | Accept proposed — Contact 子实体 + optional primary；细则另约 | 是 | |
| OD-04 | Defer — 渠道唯一性/去重 | n/a（本 Gate 关闭） | |
| OD-05 | Defer — 外联/同意基础 | n/a（关闭） | |
| OD-06 | Amend — owner 仅责任引用；territory Defer | 是（owner）；territory n/a | |
| OD-07 | Amend — resource-scoped default-deny；action/scope/masking 另约 | 是 | |
| OD-08 | Amend — Contact PII deny/mask/audit；具体策略另约 | 是（Privacy） | |
| OD-09 | Accept proposed — DSAR/驻留/跨境/法务例外路径；不法域发明 | 是（Compliance） | |
| OD-10 | Defer — runtime events | n/a | |
| OD-11 | Defer — 高影响/Workflow 分类 | n/a | |

**C1 边界提醒：** 若人工 Affirm coding auth，须另声明：哪些 OD 细节可进 C1 最小切片，哪些仍关闭。本准备包 **不** 裁定该列表。

---

## 4. Rejection Conditions（RC-01..RC-09）

Acceptance 记录：`RC-01..RC-09: all False`。

| ID | 若为真则拒 | 当前 attestation | 人审复核 |
|---|---|---|---|
| RC-01 | Accepted knowledge 当产品模型 | False | [x] |
| RC-02 | Tenant/Permission fail-closed 缺失 | False | [x] |
| RC-03 | owner/role/resolve/UI 当授权 | False | [x] |
| RC-04 | Legacy owner filter 短路对象所有权 | False | [x] |
| RC-05 | Contact privacy/retention 无责任路径 | False | [x] |
| RC-06 | 继承 Legacy ID/覆盖/GET 变异/Admin/硬级联 | False | [x] |
| RC-07 | Gate 夹带实现/Alembic/runtime manifest | False | [x] |
| RC-08 | 台账/version/migration 暗示 Accept | False | [x] |
| RC-09 | Gate Accept 写成运行/编码授权 | False | [x] |

任一项人审改为 True → **不得** Reaffirm；走 Amend/Reject。

---

## 5. 待签 / 待确认责任人

| 角色 | 责任 | 签名区 |
|---|---|---|
| **Product Owner** | Reaffirm / Amend / Reject 设计边界；另决 coding auth（见 G-3） | **Shawn / 2026-07-26** |
| **Architecture**（建议） | Package≠Kernel、Tenant/Permission、Legacy non-inheritance、manifest 非运行时 | （单 PO 场景未另签；建议复核位保留） |
| **Privacy / Compliance**（建议，若触及 Contact 持久化） | OD-08 / OD-09 控制路径可接受且细节未静默发明 | （单 PO 场景未另签；建议复核位保留） |

单 PO 场景：可仅 PO 签署，Architecture/Privacy 列为建议复核位（与框架「单 PO Approve 投影」一致）。

---

## 6. 必需证据清单（勾选）

- [x] Approved Authorization Summary（PO Approve 2026-07-24；Phase G Reaffirm 2026-07-26）
- [x] OD-01..11 dispositions 与 Summary 一致
- [x] Package / Kernel 边界已审
- [x] Constitution BOOK02 / 06 / 11 / 19 / 23 + Package Blueprint 对齐
- [x] Tenant / Permission fail-closed 原则接受（细节矩阵可 Defer，不得由实现猜测）
- [x] Contact PII / retention 治理路径接受（具体策略可 Defer）
- [x] 审计原则接受；runtime event Defer；manifest `declared_events` 为空
- [x] Knowledge traceability：ADR-0309 / Legacy extract ≠ 产品模型
- [x] Proposed manifest 仅发现草案；未注册/发布/安装
- [x] 显式记录：design-only Gate Accept ≠ 编码；C1 coding 仅由独立 Coding Auth + Affirm 覆盖

---

## 7. 已退役的人审回复模板（historical only）

```text
【阶段 G · 人审结果】
Design Gate: Reaffirm | Amend: <…> | Reject
Coding Auth (PHX-G294): Affirm | Hold/Void | Out of scope this review
Evidence exceptions: <none | list>
Signer: Product Owner — <name/handle> — <date>
```

### Recorded human decision（2026-07-26）

```text
【阶段 G · 人审结果】
Design Gate: Reaffirm
Coding Auth (PHX-G294): Affirm
Evidence exceptions: none
Signer: Product Owner — Shawn — 2026-07-26
```

---

## 8. 本阶段禁区（代理与人审共用）

- 自行把状态改写为可编码 / runtime Accept
- SQL / Alembic / API / 服务 / UI / Customer CRUD
- 注册或安装 `manifest.proposed.json`
- 自开实现里程碑或并行第二里程碑
- Brain execute / Twin authorize / Cap→grant
- 拷贝 Legacy 源码 / SQL / 表 / 路由 / 角色模型
- 用 CHANGELOG / tip / release / migration head 暗示授权

---

## 9. 出口

**TRACK-G COMPLETE**

| 决策 | 结果 |
|---|---|
| Design Gate | **Reaffirm** — Gate Accepted（design boundary only） |
| Design-surface coding auth | 仍为 **None**（Gate Accept ≠ 可编码） |
| Independent C1 Coding Auth | **Affirm** — PHX-G294（见 Coding Authorization Summary） |
| Evidence exceptions | none |
| Signer | Product Owner — Shawn — 2026-07-26 |

下一动作（另对话）：按产品队列推进（如 Tax2）或在已 Affirm 的 C1 边界内维护既有切片；**本对话不自开新实现里程碑**。
