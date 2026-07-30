# UI 蓝图

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-UI  
**阶段：** PHX-002  
**版本：** 2.0

---

## 标题

EAOS UI 蓝图

## 目的

定义 Smart Terminal 内的人类与数字员工操作表面：工作台、AI 协作、管理台与包扩展点。

## 范围

**范围内：** UI 相对 Smart Terminal Shell、API/Kernel 的边界、企业操作者体验原则、包 UI 扩展模型、无障碍与多租户全局考量。  
**范围外：** 需人类批准的重大品牌/UX 产品决策、本阶段 HTML/模板实现、将遗留屏幕继承为架构。

## 当前状态

**基线已建立 — PHX-002**  
UI 实现须遵循 Architecture → Standards → Interfaces，在平台 API 与 Kernel 契约存在后再推进。

## 未来扩展

工作台外壳契约、AI 副驾驶界面规则、包 UI 贡献模型、设计令牌（产品关键时需 UX 批准）、移动与多端策略。

---

## UI 原则

1. UI 是 API 与 Kernel 能力的消费者，不是业务规则宿主  
2. 主操作面保持单一构图意图  
3. AI 辅助集成、受权限约束且可审计  
4. 包 UI 不得破坏租户或权限边界  
5. 重大 UX 方向变更须暂停等待人类批准  

## 表面类型（概念）

| 表面 | 用途 |
|------|------|
| Operator Workbench | 人类日常运营 |
| AI Collaboration | 与数字员工协作 |
| Admin Console | 租户与平台管理 |
| Package Surfaces | 包贡献的领域界面 |

以上表面由 Smart Terminal 提供统一治理壳；UI surface 不拥有身份、权限、审批或业务真相。

## 关联文档

- [BLUEPRINT_INDEX.md](BLUEPRINT_INDEX.md)
- [API_BLUEPRINT.md](API_BLUEPRINT.md)
- [AI_BLUEPRINT.md](AI_BLUEPRINT.md)
- [PACKAGE_BLUEPRINT.md](PACKAGE_BLUEPRINT.md)
- [SMART_TERMINAL_BLUEPRINT.md](SMART_TERMINAL_BLUEPRINT.md)
- [../constitution/BOOK12.md](../constitution/BOOK12.md)
- [../constitution/BOOK23.md](../constitution/BOOK23.md)
