# Commercial Contract Lifecycle — Index

**Source root:** `H:\Workspace\EZAM_CRM - 9.0`（只读） · **Verified:** 2026-07-23

| Topic | File | Evidence strength |
|---|---|---|
| 商业合同实体、阶段、审批、生效、续签、终止与商业链链接 | [contract.md](contract.md) | Missing：运营合同主数据/生命周期；Strong：通用文档标签；Weak：贸易文档词汇、概念阶段、AI/风险占位 |

## Evidence layers

1. **运营业务实体：** 未找到 `contracts` 主表、合同应用包、商业路由或状态机。
2. **通用文档：** Document Center 注册 `contract` module key，可使用通用上传、版本、归档、分享等能力。
3. **贸易文档词汇：** GTFIP 列出 `sales_contract`、`purchase_contract`，但未形成合同主数据或 ship-ready 必备规则。
4. **概念/演示：** 完整性审查有 contract 阶段；AI task/risk 有 review/expiration 文案，均不能提升为业务事实。

## Conclusion

Legacy 没有可抽取的商业合同生命周期。EAOS 若建设该能力，应视为新领域设计，而非继承 Legacy 架构或虚构迁移规则。
