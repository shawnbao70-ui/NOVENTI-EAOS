# BOOK19 — EAOS 内核宪法 / Kernel Constitution

**仓库：** `NOVENTI-EAOS`  
**版本：** EAOS Charter v2.1  
**规范层级：** 专项宪法（受 BOOK00 / BOOK01 约束）  
**状态：** 生效

---

## 标题

EAOS 内核宪法

## 目的

确立 Kernel 为宪法级核心：公共能力边界、组件归属、身份/权限/流程/知识/事件与 AI Runtime 的不可妥协规则。

## 范围

内核宪政。约束 `kernel/`、`runtime/` 与一切依赖内核的包/API/UI。

## 当前状态

**规范正文生效**  
接口与实施状态由 Architecture / Project 文档维护，不写入宪法时态。

## 未来扩展

各内核组件的正式接口契约与验收标准。

---

## 第一编 — 内核理念

### 第 1.1 条

EAOS Kernel 是 NOVENTI 企业 AI 操作系统的宪法级核心。

### 第 1.2 条

所有业务模块均运行于 EAOS 内核之上。

### 第 1.3 条

内核提供公共能力，而不是业务功能。

### 第 1.4 条

业务模块不得重复实现内核能力。

---

## 第二编 — 内核架构

“EAOS Kernel”在本书中首先指 **Constitutional Kernel**：不可被任何技术分层绕过的平台公共能力与基本法集合。  
**Core Kernel** 是其中的可部署技术层。Platform Runtime 与 Shared Platform Capabilities 可以实现宪政能力，但不得削弱本书义务。

| 宪政能力归属 | 默认技术层 | 说明 |
|------|------|------|
| Identity Kernel | Core Kernel | 身份 |
| Organization Kernel | Core Kernel | 组织 |
| Permission Kernel | Core Kernel | 权限 |
| Workflow Kernel | Core Kernel | 流程 |
| Data Capability | Shared Platform Capability | 数据公共能力 |
| Knowledge Kernel | Shared Platform Capability | 知识服务由 Shared 层部署；Core Kernel 仅持有治理端口 |
| AI Runtime | Platform Runtime | AI 运行、规划与执行 |
| Message / Event / Integration Bus | Shared Platform Capability | 消息、事件与集成 |
| Plugin Runtime | Platform Runtime | 插件沙箱与生命周期 |
| Security / Audit / Monitoring | Cross-cutting Shared Capability | 强制控制与证据 |
| Configuration Center | Shared Platform Capability | 受审计配置 |

### 第 2.1 条

每项平台能力必须归属于唯一内核组件。

### 第 2.2 条

内核组件保持低耦合。

### 第 2.3 条

Constitutional Kernel 的能力归属不要求单体部署；任何技术拆分均必须保持唯一责任、版本化契约与不可绕过控制。

---

## 第三编 — 身份内核（Identity）

管理对象包括：Human、Enterprise、Organization、Department、AI Employee、Device、API、Application、Plugin。  
Role 与 Permission 可作为身份关联引用，但授权求值与权限真相唯一归属 Permission Kernel。

### 第 3.1 条

身份全球唯一。

### 第 3.2 条

身份不得重复。

---

## 第四编 — 权限内核（Permission）

控制对象包括：Users、AI、Applications、Plugins、API、Data、Knowledge、Workflow。

### 第 4.1 条

权限统一计算。

### 第 4.2 条

权限决策可审计。

---

## 第五编 — 流程内核（Workflow）

提供：Approval、Routing、Task、Automation、Escalation、Scheduling、Exception。

### 第 5.1 条

业务模块调用流程内核，不得私建平行审批引擎替代内核。

---

## 第六编 — AI Runtime

管理：AI Employees 关联的 Agents、AI Memory、Reasoning、Planning、Execution、Learning、Safety。

AI 主体分层如下：

1. AI Employee 是永久、受治理的劳动力身份。
2. Agent 是 AI Runtime 内的技术执行单元。
3. Digital Human 是 AI Employee 或 Agent 的可选人格化表现。
4. AI Assistant 是面向特定人或团队的协作角色。
5. Smart Terminal 是交互表面，不是 AI 主体。

### 第 6.1 条

所有 AI 必须运行于 AI Runtime。

### 第 6.2 条

AI Runtime 强制执行宪章规则（含授权边界与人工审批要求）。

---

## 第七编 — 事件总线（Event Bus）

所有业务行为生成事件。事件不可修改；事件支持受控回放。

---

## 第八编 — 消息总线（Message Bus）

默认异步；送达状态必须可追踪。

---

## 第九编 — 知识内核（Knowledge）

管理：Knowledge Graph、Enterprise Memory、Vector Database、Documents、Policies、AI Knowledge、Semantic Search。

“Knowledge Kernel”是宪政能力名称，不表示其必须部署于 Core Kernel；规范技术归属为 Shared Platform Capability，Core Kernel 仅定义不可绕过的授权、租户与 provenance 端口。

### 第 9.1 条

知识仅通过授权共享。

---

## 第十编 — 插件运行时（Plugin Runtime）

提供：Installation、Sandbox、Lifecycle、Permission、Version、Dependency。  
插件不得绕过权限与租户隔离。

---

## 第十一至十三编 — 配置 / 监控 / 稳定性

1. 配置变更必须可审计。  
2. 监控覆盖可用性、错误、延迟与安全信号。  
3. 内核稳定性优先于功能扩张；破坏性变更需 ADR 与版本化。  

---

## 第十四编 — 内核基本法

1. Kernel First — 平台能力优先于重复业务逻辑。  
2. 多租户隔离不可关闭。  
3. 无身份、无权限则无副作用。  
4. 审计不可被业务包或 AI 关闭。  
5. 遗留系统不得成为内核依赖。  
6. 公共契约版本化。  
7. 失败关闭（fail closed）适用于授权与租户隔离错误。  
8. 与 BOOK00 / BOOK01 冲突时，按宪法冲突裁决与修订程序处理。  
9. Constitutional Kernel 与 Core Kernel 的区分不得被用于绕过本编基本法。  

## 关联文档

- [BOOK00.md](BOOK00.md)
- [BOOK01.md](BOOK01.md)
- [BOOK22.md](BOOK22.md)
- [BOOK23.md](BOOK23.md)
- [../blueprint/KERNEL_BLUEPRINT.md](../blueprint/KERNEL_BLUEPRINT.md)
- [../architecture/KERNEL_INTERFACES.md](../architecture/KERNEL_INTERFACES.md)
- [../standards/CODING_STANDARD.md](../standards/CODING_STANDARD.md)
- [../decisions/ADR-0021-constitutional-platform-layering.md](../decisions/ADR-0021-constitutional-platform-layering.md)
