# API 标准

**仓库：** `NOVENTI-EAOS`  
**阶段：** PHX-003  
**版本：** 2.0

---

## 标题

EAOS API 标准

## 目的

统一 REST 命名、方法语义、版本、响应、分页/过滤/排序、认证授权与错误格式。

## 范围

标准文档。本阶段不实现 API。

## 当前状态

**已就绪 — PHX-003 基线**

## 未来扩展

完整错误码表、OpenAPI 产物位置、幂等键规范。

---

## REST Naming

- 资源名使用复数名词：`/v1/organizations`  
- 路径只用小写与连字符/嵌套资源，避免动词堆叠  
- 动作型操作使用受控子资源或标准动作约定（实现期细化）  

## HTTP Methods

| 方法 | 用途 |
|------|------|
| GET | 读取 |
| POST | 创建或受控动作 |
| PUT | 全量替换（慎用） |
| PATCH | 部分更新 |
| DELETE | 删除（优先软删语义） |

## Versioning

- URI 版本前缀：`/v1/...`  
- 破坏性变更递增主版本  
- 弃用必须公告与过渡期  

## Response Format

统一包络（概念）：

```text
data | error | meta
```

- 成功：`data` + 可选 `meta`  
- 失败：`error`（code、message、details、correlation_id）  

## Pagination

- 列表默认分页  
- 使用 `limit` / `cursor` 或 `page` / `page_size`（实现期锁定一种主策略）  
- 响应 `meta` 包含分页信息  

## Filtering

- 使用明确查询参数；禁止任意拼接原始 SQL 表达式  
- 过滤字段白名单化  

## Sorting

- `sort=field` 或 `sort=-field`  
- 排序字段白名单化  

## Authentication

- 所有非公开端点必须认证  
- 凭证不落日志  

## Authorization

- 认证之后必须经 Kernel 权限求值  
- 无权限返回统一错误，不泄露资源存在性细节（按安全策略）  

## Error Response

| 要素 | 要求 |
|------|------|
| code | 稳定机器可读码 |
| message | 人类可读 |
| correlation_id | 必填 |
| http status | 语义正确 |

## 关联文档

- [../blueprint/API_BLUEPRINT.md](../blueprint/API_BLUEPRINT.md)
- [EVENT_STANDARD.md](EVENT_STANDARD.md)
- [CODING_STANDARD.md](CODING_STANDARD.md)
