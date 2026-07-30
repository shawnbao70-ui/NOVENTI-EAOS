# platform/

Shared platform capabilities for EAOS（结构说明占位目录）。

## Purpose

跨 Kernel / Runtime / Packages / API / UI 的 Shared 能力层说明根。

## Implementation note

Python 导入根使用 `eaos_platform/`（避免与标准库 `platform` 冲突）。

当前已实现：

- `eaos_platform.knowledge` — PHX-K10 Knowledge Shared Capability

本目录本身不作为 Python package 导入根。

## Status

PHX-K10 Knowledge 垂直切片已交付；其余 Shared 能力按里程碑推进。
