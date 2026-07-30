# ADR-0060 — Terminal Extension iframe Runtime + CSP (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G42  
**归属：** Smart Terminal（独立受治理交互层）

## 背景

G39/G41 已交付声明式 Extension Host 与 SQL 持久化，但 UI 仍无沙箱呈现面。BOOK23 要求扩展在沙箱中运行且不得隐藏审批或提升上下文。

## 决策

1. Foundation 仅托管**首方**静态演示面板（`/terminal/extensions/*`），不加载 Marketplace 上传的任意 JS。  
2. Extensions 表面使用 `sandbox` iframe（`allow-scripts`，不含 `allow-same-origin`）加载演示面板。  
3. Gateway 对 `/terminal/extensions/` 响应附加严格 CSP（禁 `connect-src` 网络、限制 `frame-ancestors`）。  
4. iframe → 父页仅允许 `eaos.extension.invoke` 类 postMessage；父页映射为既有 `invoke_extension_action`；拒绝上下文提升字段。  
5. invoke 仍为声明审计路径：`executed` 恒为 `false`；扩展非业务真相源。  
6. 桥接策略在 `smart_terminal.extension_runtime` 固化，供契约测试。

## Explicit Defer

- Marketplace 包 / CDN 加载与任意上传脚本执行  
- Marketplace 签名密码学校验（Foundation 见 ADR-0062 / PHX-M18）  
- 完整多面板 CSP 产品矩阵与跨域包联邦  
- Extension Worker（Foundation 见 ADR-0061 / PHX-G43）  

## 关联

- [ADR-0057-terminal-extension-host.md](ADR-0057-terminal-extension-host.md)
- [../project/PHX-G42_ARCHITECTURE_GATE.md](../project/PHX-G42_ARCHITECTURE_GATE.md)
