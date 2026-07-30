# V14 Residual 路由风险编目

**Evidence strength:** Strong for loader, mount and source structure; deployed import/mount outcome is UNKNOWN without runtime status  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

`v14_residual` 不是已停用的历史备份。当前架构会自动发现 `apps/*/v14_residual.py`，绑定 V14 全局对象和 Legacy helper，过滤已被先前路由占用的 method+path，再挂载剩余路由。

仓库当前可见 28 个 residual 模块。部分 residual 又作为 attach shell 挂入后续拆出的页面/API 路由。标签 `V14_RESIDUAL_STATUS="extracted"` 表示代码已从 `app.py` 搬出，不表示业务语义已进入 canonical Service/Repository，也不表示 residual 已不运行。

静态代码可以确认挂载算法和残留内容，但以下事项为 **UNKNOWN**：

- 特定部署中 28 个模块是否全部导入成功；
- `mount_v14_residual_routers()` 返回的 errors/skipped 数；
- 实际 route table 中每个重复 path 的赢家；
- 历史报告所述 syntax/import 问题是否仍影响当前部署。

检索路径：`bootstrap/v14_residual.py`、`runtime/v14/`、`apps/*/v14_residual.py`、runtime/cutover/residual reports。

---

## 2. 风险目录

| 风险ID | 触发条件 | 影响 | 缓解备注（EAOS） |
|--------|----------|------|------------------|
| VR-001 | Canonical router 与 residual 或两个 residual 声明相同 method+path | 挂载顺序决定赢家；后挂路由被静默跳过，修复可能未生效或不同部署行为不同 | 构建期生成唯一 route owner manifest；重复 method+path 直接失败，不以 skip 继续 |
| VR-002 | residual 或 decomposition attach 模块通过 globals/`legacy_support` 注入任意 helper/常量 | 模块表面 owner 与真实业务 owner分离；隐式跨域依赖、同名覆盖和全局副作用难追踪 | 每个业务命令显式依赖最小 service port；禁止 namespace 注入 |
| VR-003 | residual-authoritative 路由直接使用共享 cursor/conn、execute、session helper 或文件系统 | 活动路径绕过 canonical Service/Repository、权限、事务、审计和租户边界 | 优先迁移无 canonical 竞争的活动 residual；写操作必须经过统一 application service |
| VR-004 | canonical 与 residual/attach 保留同一业务动作的不同实现；canonical 挂载失败时旧实现可能接管 | 正常挂载时旧副本多被 skip，但故障/回退时会暴露不同编号、校验、权限和副作用 | 每个 command 只保留一个实现；旧 URL 仅做无副作用 redirect 到 canonical confirmation |
| VR-005 | 运维或迁移人员把 `extracted`、PASS、Fixed Link 或 `app.py=0 routes` 理解为 residual 已消除 | 低估活动 Legacy 行为；错误删除 helper/表；迁移基于过时报告 | 状态拆分为 moved、mounted、canonicalized、retired；以运行 route owner dump 为准 |
| VR-006 | residual 导入失败、attach 漏挂、全路由被 skip，或顶层 bootstrap 失败但继续 | 模块可不在 mounted 也不在 errors；应用部分启动但路由缺失；故障延迟到用户访问 | 对必需 residual/固定链接 fail closed；发布前核对 mounted/errors/skipped 与路由契约 |

---

## 3. 风险明细

### VR-001 — 路由赢家取决于顺序

- **触发条件：** 已挂载 route table 中存在相同 method+path；或 residual 自动发现顺序中前一个模块已占用路径。
- **影响：** 后续 router 的 route 被过滤，不报业务级冲突。相同 URL 可能继续调用旧语义，而维护者误以为新 router 已接管。
- **证据：** loader 以现有 keys 和按 slug 排序的 residual 顺序过滤冲突；历史 Route Ownership Registry 也记录 `/workflow_center`、`/brand_center`、`/ai_decision_center` 等重复 owner。
- **缓解备注（EAOS）：** route registry 必须同时记录 command owner、permission policy、service 和 schema version。

### VR-002 — Legacy namespace 注入

- **触发条件：** residual import 后执行 `activate_residual_namespace()`，或拆出的 attach 模块自行 hydrate globals/legacy_support。
- **影响：** `legacy_support` 中几乎所有 callable 和常量被写入调用模块；代码看似本地函数，实际可能读取别域全局表、模板或状态。
- **证据：** `runtime/v14/residual_loader.py` 明确遍历并注入非模块值。
- **缓解备注（EAOS）：** 禁止通过全局注入维持兼容；用明确 facade，并对每个 facade 标记只读/写入和事务 owner。

### VR-003 — 活动 residual 绕过 canonical 层

- **触发条件：** 无 business router 竞争的 residual-authoritative handler 直接执行 SQL 或调用共享 `execute`，例如 Distributor 删除、Document Designer 保存、系统/集成对象删除。
- **影响：** 与已抽出的 service/repository 规则不同步；route gate、对象授权、审计和事务可能缺失。
- **证据：** 多个 residual 文件仍包含直接查询/更新/删除；V14 Residual Inventory 明示 business handlers frozen。已被 canonical method+path 占用的 duplicate 通常会被过滤，不应误报为正常 happy path。
- **缓解备注（EAOS）：** “move-only” 只能用于短期兼容，不能作为风险已消除的完成条件。

### VR-004 — 多入口业务语义

- **触发条件：** canonical business router 未挂载/导入失败，或 residual-only 固定链接本就没有 canonical page owner。
- **影响示例：**
  - `/create_do`、`/create_ar`、`/so_status`、`/convert_so` 的 residual 副本与 canonical 语义不同，正常挂载时多为 latent；
  - `/permission_center`、`/notification_center`、`/brand_center`、`/integration_center`、`/ai_decision_center` 和主页等仍有 residual-authoritative 表面；
  - Approval 主/备用批准路径的历史写入不同；
  - Brand profile save 有管理员 gate，但同 residual 内 Document Designer save 无同等 gate。
- **缓解备注（EAOS）：** 兼容 URL 只可映射到同一个 command，不可保留第二套实现。

### VR-005 — 状态标签误导

- **触发条件：** 只看 `app.py` 无 decorators、`V14_RESIDUAL_STATUS="extracted"` 或 decomposition PASS。
- **影响：** 把“搬到 apps 下”误当作“领域服务化”；忽略 28 个活动 residual 与 12k+ 行 Frozen handler。
- **证据：** App.py Elimination Report 同时报告 0 个 app.py route、28 个 residual，并记录历史 known issue；Residual Inventory 明确 handlers remain frozen。
- **缓解备注（EAOS）：** 退出标准必须是业务行为、权限、事务和审计等价验证，不能只看文件位置。

### VR-006 — 部分挂载/静默缺路由

- **触发条件：** import 抛错、router 为空、attach 失败、全部 path 被过滤，或 enterprise bootstrap 异常被顶层捕获。
- **影响：** mount 函数把 import 错误收集后继续；全部 path 被 skip 的模块既不 mounted 也不 errors；skipped 数未见 fail-closed 消费。
- **证据强度：** Loader behavior confirmed；当前部署返回值 UNKNOWN。
- **缓解备注（EAOS）：** 启动 manifest 应列出每个 expected route 的唯一 owner，并将 unexpected error/skip 设为发布阻断。

---

## 4. 对业务语义的具体影响

| Domain | Residual influence | Risk |
|--------|--------------------|------|
| Sales / Delivery | 旧 convert/create/status 实现仍作为 latent 副本；canonical 缺失时可能接管 | 回退语义与正常语义不同 |
| Finance | residual attach、legacy handler 与 canonical Finance service 混合 | 页面看似统一，posting/reconciliation 仍分散 |
| Approval | 主 router 与 residual/备用 record action 语义不同 | 批准历史、审批人和业务释放不一致 |
| Marketing | Campaign API scaffold 与 residual Distributor CRUD 分属不同 owner | “Marketing”能力边界被目录结构误导 |
| Brand / Documents | 品牌保存、上传、模板设计同驻 residual，但权限策略不同 | 横向文档配置可绕开品牌管理 gate |
| Service | residual 文件存在并不证明 ticket 服务已实现 | 路由存在性被误读为业务成熟度 |

---

## 5. 缓解顺序（EAOS）

1. 生成实际运行 route owner 快照：method、path、module、permission、command。
2. 对写路由按资金/库存/审批/删除优先级排序。
3. 为每个动作选定 canonical service；记录旧路径行为差异。
4. 将 residual 写入口改成同一 command 的兼容桥；验证等价后退休。
5. 删除 namespace 注入前，显式枚举每个 residual 依赖。
6. 发布门检查 expected routes、零意外 duplicate、零 import error、零未授权写入口。

---

## 6. 只读来源路径

| Path | Risk IDs | Why cited |
|------|----------|-----------|
| `bootstrap/v14_residual.py` | VR-001, VR-006 | 自动发现、过滤、挂载和错误收集 |
| `runtime/v14/residual_loader.py` / attach 模块 `_hydrate_runtime_ns` | VR-002 | Legacy namespace 注入及二次扩散 |
| `runtime/v14/globals.py` | VR-002, VR-003 | 共享 cursor/conn/templates/global dependencies |
| `runtime/v14/legacy_support.py` | VR-002, VR-003, VR-004 | 大型共享 helper 与业务语义来源 |
| `core/runtime/enterprise_runtime.py` | VR-005 | residual owner/status 和目标执行链 |
| `apps/*/v14_residual.py` | VR-003, VR-004, VR-006 | 28 个活动 residual 表面 |
| `apps/finance/legacy_handlers.py` / `apps/inventory/legacy_handlers.py` / `apps/sample/legacy_handlers.py` | VR-003 | 仍活动的 legacy delegation |
| `docs/reports/V14_Residual_Inventory.md` | VR-005 | 模块数、规模和 frozen handlers |
| `docs/reports/Residual_Decomposition_Vol001_Report.md` … `Vol030_Report.md` | VR-004, VR-005 | move-only decomposition 与 attach shells |
| `docs/reports/Apppy_Elimination_Report.md` | VR-005, VR-006 | 0 app.py routes 与历史 known issue 并存 |
| `docs/reports/Route_Ownership_Registry.md` | VR-001, VR-004, VR-005 | 历史重复 owner；其中 app.py winner 表述已过时，只作迁移对照 |
| `docs/reports/Service_Recovery_Report.md` | VR-003 | canonical services 与 legacy handlers 并存 |
| `scripts/v170_phase2_app_elimination.py` / residual decomposition gates | VR-005, VR-006 | 文件/route 数门禁及其边界 |

**UNKNOWN 检索/验证路径：** 运行时 `v14_residual_status()`、mount 返回的 `errors` / `skipped_duplicate_paths`、FastAPI 实际 route table；本波未启动 Legacy 或修改运行状态。

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
