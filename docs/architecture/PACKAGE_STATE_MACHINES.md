# Package Platform 状态机

**文档 ID：** SM-PKG-001  
**版本：** 1.0  
**阶段：** PHX-B14

## Manifest

```text
draft ──publish──► published ──deprecate──► deprecated
```

## Installation

```text
installed ──disable──► disabled
```

仅 `published` 可进入 `installed`。`disabled` 后 surface/action 对解析不可见。

## Resolve

Resolve 不是独立状态机；成功条件：

1. 租户存在 `installed` 安装  
2. action 在对应 manifest 中声明  
3. Permission 允许 `package_action:resolve` 与业务 `permission_action`
