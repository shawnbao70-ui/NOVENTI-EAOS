# 业务包蓝图

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-PACKAGE  
**阶段：** PHX-002  
**版本：** 2.0

---

## 标题

EAOS 业务包蓝图

## 目的

定义行业包、业务包与市场包如何在不违反 Kernel、Runtime 与宪法边界的前提下扩展 EAOS。

## 范围

**范围内：** 包类型与生命周期、对 Kernel/平台服务的依赖规则、隔离与版本意图、市场就绪原则。  
**范围外：** 在包内实现具体 ERP 模块、将遗留 ERP 重建为包架构、绕过 Kernel 权限或租户隔离。

## 当前状态

**PHX-B14 Foundation Fully Accepted**（市场分发 → PHX-M16）

## 未来扩展

多版本并存产品化、行业包分类认证、Marketplace 签名分发；商业化/许可钩子属商业决策，需人类批准。

---

## 包原则

1. 包消费平台能力，不分叉 Kernel  
2. 业务知识可来自遗留资产；架构不得来自遗留  
3. 包可版本化且可隔离  
4. 市场包必须声明权限与事件契约  
5. 优先复用平台服务，避免包内重复逻辑  

## 包类型（概念）

| 类型 | 说明 |
|------|------|
| Industry Package | 行业能力集合 |
| Business Package | 领域业务能力 |
| AI Package | 智能体/技能扩展 |
| Integration Package | 外部系统连接（经平台边界） |

## 关联文档

- [BLUEPRINT_INDEX.md](BLUEPRINT_INDEX.md)
- [KERNEL_BLUEPRINT.md](KERNEL_BLUEPRINT.md)
- [RUNTIME_BLUEPRINT.md](RUNTIME_BLUEPRINT.md)
- [API_BLUEPRINT.md](API_BLUEPRINT.md)
- [UI_BLUEPRINT.md](UI_BLUEPRINT.md)
- [../standards/PROJECT_STRUCTURE.md](../standards/PROJECT_STRUCTURE.md)
