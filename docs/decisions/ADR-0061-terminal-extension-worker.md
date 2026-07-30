# ADR-0061 — Terminal Extension Worker Runtime (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G43  
**归属：** Smart Terminal（独立受治理交互层）

## 背景

G42 交付首方 iframe + CSP + postMessage 桥接。仍缺独立于 DOM 的 Worker 运行时切片；BOOK23 要求扩展沙箱化且不得提升上下文。

## 决策

1. Foundation 仅托管**首方** Worker 脚本（`/terminal/extensions/demo-worker.js`），不加载 Marketplace 任意包。  
2. 宿主页以 `new Worker(first-party URL)` 启动；Worker → 宿主仅允许与 G42 相同的 `eaos.extension.invoke` 桥接消息（可选 `channel: "worker"`）。  
3. 宿主将桥接映射为既有 `invoke_extension_action`；拒绝上下文提升字段；`executed` 恒为 `false`。  
4. Worker 资产仍走 `/terminal/extensions/` CSP（禁 `connect-src`）。  
5. 策略扩展落在 `smart_terminal.extension_runtime`；无 schema 变更。

## Explicit Defer

- Marketplace / CDN 第三方 Worker 包加载  
- SharedWorker / ServiceWorker 产品矩阵  
- Marketplace 签名密码学校验（Foundation 见 ADR-0062 / PHX-M18）  
- 完整多源 CSP / 跨域包联邦  

## 关联

- [ADR-0060-terminal-extension-iframe-csp.md](ADR-0060-terminal-extension-iframe-csp.md)
- [../project/PHX-G43_ARCHITECTURE_GATE.md](../project/PHX-G43_ARCHITECTURE_GATE.md)
