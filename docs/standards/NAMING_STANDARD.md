# 命名标准

**仓库：** `NOVENTI-EAOS`  
**阶段：** PHX-003  
**版本：** 2.0

---

## 标题

EAOS 命名标准

## 目的

统一模块、服务、事件、API、数据实体与 AI 智能体命名，降低认知成本与集成摩擦。

## 范围

跨平台层命名约定。

## 当前状态

**已就绪 — PHX-003 基线**

## 未来扩展

完整词典与禁用词表。

---

## 总则

- 使用清晰领域语言；避免遗留系统内部黑话作为平台规范名  
- 同一概念全球唯一术语  
- 英文标识符用于代码与 API；中文可用于文档标题与说明  

## 代码与模块

| 对象 | 约定 |
|------|------|
| 包/模块 | snake_case |
| 类 | PascalCase |
| 函数/变量 | snake_case |
| 常量 | UPPER_SNAKE_CASE |

## API 资源

- 复数名词、小写  
- 路径稳定，不反映内部表名细节  

## 事件

- 形式：`domain.entity.action`（例：`identity.user.created`）  
- 过去分词/完成态表达已发生事实  

## 数据实体

- 表/集合：复数 snake_case  
- 与领域术语一致，不与包私有缩写冲突  

## AI 智能体

- 形式：`agent.<domain>.<role>` 或文档中的可读显示名 + 稳定技术 ID  
- 显示名可变；技术 ID 稳定  

## 包

- `pkg.<industry_or_domain>.<name>`（实现期锁定清单字段）  

## 关联文档

- [CODING_STANDARD.md](CODING_STANDARD.md)
- [EVENT_STANDARD.md](EVENT_STANDARD.md)
- [AI_STANDARD.md](AI_STANDARD.md)
