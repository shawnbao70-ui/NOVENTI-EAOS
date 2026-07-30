# 架构蓝图索引

**计划：** Project Phoenix  
**产品：** NOVENTI Enterprise AI Operating System (EAOS)  
**版本：** 3.0  
**阶段：** PHX-A03 — Architecture Realignment  
**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-INDEX

---

## 标题

EAOS 架构蓝图索引

## 目的

作为 `NOVENTI-EAOS` 内全部架构蓝图的权威导航与阅读顺序定义，并建立与宪法、标准、治理文档的交叉引用。

## 范围

**范围内：**

- 蓝图目录与依赖顺序
- 跨文档引用
- 与 EAOS 宪法（BOOK00–BOOK23）的对齐关系
- 与开发标准、项目治理的对齐关系

**范围外：**

- 业务逻辑实现
- API / 数据库 schema 创建
- 继承遗留 ERP 架构

## 当前状态

**重对齐完成 — PHX-A03**

蓝图文档已从占位结构扩展为可执行的架构基线描述。接口契约与实现仍属后续里程碑。

## 未来扩展

- 各蓝图的接口契约明细
- 架构决策（ADR）逐域链接
- 宪法书目 → 蓝图可追溯矩阵持续维护
- 各里程碑 architecture ownership 验收清单

---

## 真理源优先级

1. EAOS 宪法（BOOK00–BOOK23）
2. 架构蓝图（本目录）
3. 开发标准
4. 已批准的架构决策
5. 项目文档
6. 遗留业务资产（只读知识）

---

## 蓝图目录

| 顺序 | 文档 | 职责 |
|------:|------|------|
| 1 | [KERNEL_BLUEPRINT.md](KERNEL_BLUEPRINT.md) | 内核能力与不可妥协边界 |
| 2 | [RUNTIME_BLUEPRINT.md](RUNTIME_BLUEPRINT.md) | 运行时执行模型 |
| 3 | [EVENT_BLUEPRINT.md](EVENT_BLUEPRINT.md) | 事件驱动架构 |
| 4 | [KNOWLEDGE_BLUEPRINT.md](KNOWLEDGE_BLUEPRINT.md) | 知识图谱与企业记忆 |
| 5 | [AI_BLUEPRINT.md](AI_BLUEPRINT.md) | AI 运行时、智能体与数字劳动力 |
| 6 | [PACKAGE_BLUEPRINT.md](PACKAGE_BLUEPRINT.md) | 行业与业务包 |
| 7 | [API_BLUEPRINT.md](API_BLUEPRINT.md) | 内外部 API 面 |
| 8 | [UI_BLUEPRINT.md](UI_BLUEPRINT.md) | 操作界面与体验模型 |
| 9 | [SMART_TERMINAL_BLUEPRINT.md](SMART_TERMINAL_BLUEPRINT.md) | 受治理的人类–AI 交互层 |

---

## 阅读顺序

1. 宪法 BOOK00–BOOK01、BOOK19、BOOK22、BOOK23
2. [../architecture/VISION.md](../architecture/VISION.md)
3. 本索引
4. Kernel → Runtime → Event → Knowledge → AI → Package → API → UI → Smart Terminal
5. `docs/standards/` 开发标准

---

## 关联治理文档

| 文档 | 路径 |
|------|------|
| 主计划 | [../project/MASTER_PLAN.md](../project/MASTER_PLAN.md) |
| 项目状态 | [../project/PROJECT_STATUS.md](../project/PROJECT_STATUS.md) |
| 路线图 | [../project/ROADMAP.md](../project/ROADMAP.md) |
| Phoenix Roadmap v3 | [../project/PHOENIX_ROADMAP_V3.md](../project/PHOENIX_ROADMAP_V3.md) |
| Constitutional / Platform Layering ADR | [../decisions/ADR-0021-constitutional-platform-layering.md](../decisions/ADR-0021-constitutional-platform-layering.md) |
| 愿景 | [../architecture/VISION.md](../architecture/VISION.md) |
| EAOS 架构 | [../architecture/EAOS_ARCHITECTURE.md](../architecture/EAOS_ARCHITECTURE.md) |
| 系统原则 | [../architecture/SYSTEM_PRINCIPLES.md](../architecture/SYSTEM_PRINCIPLES.md) |
| 编码标准 | [../standards/CODING_STANDARD.md](../standards/CODING_STANDARD.md) |
| 宪法目录 | [../constitution/README.md](../constitution/README.md) |

---

## 变更控制

凡改变 Kernel 边界、多租户身份、权限模型或 AI 人工审批边界的蓝图变更，须经架构方向评审（可触发人类批准暂停条件）。
