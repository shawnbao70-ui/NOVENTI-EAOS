# ADR-0021 — Constitutional Kernel 与技术分层

**状态：** 已接受（人工批准）  
**日期：** 2026-07-18

## 背景

BOOK19、EAOS Architecture 与 Kernel Blueprint 对 Kernel 使用了不同粒度，导致宪政能力归属与部署边界混淆。

## 决策

1. **Constitutional Kernel** 是不可绕过的平台公共能力与基本法集合。
2. **Core Kernel** 是可部署技术层，当前包含 Identity、Organization、Permission、Workflow。Knowledge 归属 Shared Platform Capability；Core Kernel 仅持有其治理端口，PHX-K10 可决定部署形态但不得改变该所有权。
3. AI Runtime、Event/Message/Integration Bus、Plugin Runtime、Security、Audit、Monitoring 与 Configuration 是 Constitutional Kernel 能力，但可由 Platform Runtime 或 Shared Platform Capability 实现。
4. 技术拆分不得关闭或削弱 BOOK19 的隔离、权限、审计、身份与失败关闭义务。
5. Smart Terminal 是独立受治理交互层，不属于 Constitutional Kernel 或 Core Kernel。

## AI 主体分类

- AI Employee：永久、受治理的劳动力身份
- Agent：AI Runtime 内执行单元
- Digital Human：AI Employee/Agent 的可选人格化表现
- AI Assistant：面向特定人或团队的协作角色

## 后果

- BOOK19 增加双层解释。
- BOOK22 增加规范术语。
- EAOS Architecture 与后续 Blueprint 必须使用相同 ownership map。
