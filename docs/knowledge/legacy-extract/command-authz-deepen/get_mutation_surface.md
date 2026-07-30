# GET 写操作表面（GET Mutation Surface）

**Evidence strength:** Strong for listed route declarations and sampled side effects  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页编目以 GET 执行 INSERT/UPDATE/DELETE 或业务状态推进的 surface。即使 route 有 RBAC，GET 仍绕过 Legacy CSRF middleware，可能被预取、链接嵌入、爬虫、历史重放或跨站请求触发。交叉引用 `ship-complete-deepen/do_complete.md`、`do_reopen.md`，不重写其权威业务正文。

## 2. GET Mutation Inventory

| Domain | Path | Server gate | Side effect | Intent/idempotency |
|---|---|---|---|---|
| Approval | `/approve/{id}` | none | approve record | confirm UI only; weak |
| Approval | `/reject/{id}` | none | reject record | confirm UI only; weak |
| Approval | `/approve_record/{id}` | none | approval status/result/time | none |
| Approval | `/reject_record/{id}` | none | rejection state | none |
| Quote | `/quote_status/{id}/{status}` | none | change quote status | enum only |
| Quote | `/delete_quote_item/{item}/{quote}` | Quotes edit/delete local | delete line/reprice | browser link |
| Quote | `/delete_quote_template/{id}` | none | delete template | browser link |
| Quote | `/copy_quote/{id}` | none | create Draft copy + lines | every call creates |
| Quote | `/create_quote_from_sample/{id}` | none | create Draft quote | every call creates |
| Sales | `/convert_so/{quote}` | none | create SO + commission attempt | app duplicate guard |
| Sales | `/so_status/{id}/{status}` | Sales Orders edit | change status | Open redirected Type A |
| Sales | `/create_do/{so}` | none | create DO + SO status | no dedupe |
| Inventory | `/convert_do/{so}` | Sales Orders edit in service | create DO | no dedupe |
| Inventory | `/delete_inventory/{id}` | Inventory delete | delete zero-stock record | stock guard |
| Delivery | `/do_ship/{id}` | redirects only | no direct write canonical | Type A target |
| Delivery | `/complete_do/{id}` | Delivery Orders edit | DO/SO→Delivered | stage idempotency |
| Delivery | `/reopen_do/{id}` | Delivery Orders edit | DO→Pending, SO→Open | stage check |
| Finance | `/create_receipt/{so}` | Receipts add | receipt record/update mirrors | amount logic |
| Finance | `/create_purchase_invoice/{purchase}` | none | invoice/AP facts | duplicate policy weak |
| Finance | `/approve_expense/{expense}` | none | approve expense | hardcoded BOSS |
| Finance | `/create_ar/{do}` | none on alias | canonical 303 to Type A invoice page; no direct write | redirect-only |
| Finance residual | `/clear_followups` | none | delete follow-up rows | query-driven |
| Procurement | `/receive_purchase/{id}` | Purchases edit | receipt/inventory state | browser link |
| Procurement | `/delete_purchase/{id}` | Purchases delete | delete purchase | local guards |
| Customer | `/delete_customer/{id}` | Customers delete | delete customer | browser confirm |
| Product | `/delete_product/{id}` | Products delete | delete product | dependencies vary |
| Supplier | `/delete_supplier/{id}` | Suppliers delete | delete supplier | dependencies vary |
| Identity | `/delete_role/{id}` | Roles delete + business guards | delete role | protected/in-use guard |
| Identity | `/delete_user/{id}` | none | delete user | none |
| Sample | `/delete_sample_image_slot/{sample}/{slot}` | sampled gate/partial | remove image reference/file | weak |
| Sample | `/materialize_sample/{sample}` | Samples edit | inventory/product/ledger materialization | app guards |
| Product | `/delete_product_application/{id}` | none | delete product application | weak |
| Platform | `/delete_tree_node/{id}` | residual local/none | delete org/tree node | weak |
| Platform | `/delete_ip_whitelist/{id}` | residual local/none | delete security entry | weak |
| Platform | `/delete_ip_blacklist/{id}` | residual local/none | delete security entry | weak |
| Tenant Center | `/delete_organization_user/{id}` | local/UNKNOWN | delete membership | weak |
| Tenant Center | `/delete_license/{id}` | local/UNKNOWN | delete license metadata | weak |

## 3. Business Rules

| ID | Rule |
|---|---|
| GMS-R01 | Legacy CSRF 将 GET 归类为 safe method。 |
| GMS-R02 | 有 module RBAC 的 GET mutation 仍不是安全 command。 |
| GMS-R03 | browser `confirm()` 可被直链绕过。 |
| GMS-R04 | Approval decisions 是无 RBAC 的 GET writes。 |
| GMS-R05 | Quote/SO status URL 把目标状态编码在 path。 |
| GMS-R06 | Convert SO 和 Create DO 是 GET create operations。 |
| GMS-R07 | `/create_do` 无 server gate且无 source dedupe。 |
| GMS-R08 | `/convert_do` 有 service gate但仍无 POST intent。 |
| GMS-R09 | canonical `/do_ship` 只重定向 Type A，不直接扣库存。 |
| GMS-R10 | Complete 是 GET status command，不是 Ship。 |
| GMS-R11 | Complete 有 stage guard，可防重复结果但不能消除 GET 风险。 |
| GMS-R12 | Reopen 是 status-only GET，不反向库存/AR。 |
| GMS-R13 | Receipt、Purchase Receive、Purchase Invoice 可由 GET 建财务/库存事实。 |
| GMS-R14 | GET delete 广泛存在于 master/identity/config domains。 |
| GMS-R15 | batch Complete 逐条 fetch GET，不形成批次事务。 |
| GMS-R16 | GET 请求可能被浏览器预取、缓存重放或跨站触发。 |
| GMS-R17 | SameSite cookie/headers 不替代 command method 与 CSRF。 |
| GMS-R18 | route winner 可使 residual 直接写实现失效或重新暴露。 |
| GMS-R19 | 幂等业务结果不等于请求具有授权意图。 |
| GMS-R20 | EAOS 必须把所有 listed write 转成 explicit POST/DELETE command。 |
| GMS-R21 | canonical `/create_ar` 与 `/do_ship` 是 redirect-only GET，不能误列为 direct write。 |
| GMS-R22 | Copy Quote/Create Quote from Sample 每次请求可创建新记录，重放不是幂等。 |

## 4. Process

1. 用户或第三方资源触发 GET URL。
2. CSRF middleware 因 SAFE_METHODS 直接放行。
3. route 若有 checker则执行；若无则 permission matrix 不参与。
4. handler/service 直接写库并 redirect。
5. 浏览器历史、重试或批量 fetch 可再次触发；是否重复取决于各业务 guard。

## 5. Validation

| ID | Validation | Legacy |
|---|---|---|
| GMS-V01 | GET must be side-effect free | Violated |
| GMS-V02 | command uses POST/DELETE | Missing broadly |
| GMS-V03 | CSRF token required | Skipped for GET |
| GMS-V04 | authenticated principal required | Missing/inconsistent |
| GMS-V05 | server RBAC required | Missing/inconsistent |
| GMS-V06 | object/tenant scope required | Missing/inconsistent |
| GMS-V07 | source state required | Strong only selected actions |
| GMS-V08 | idempotency/replay protection | Partial |
| GMS-V09 | Human Confirm for sensitive writes | Selected Type A only |
| GMS-V10 | audit actor/reason required | Missing/inconsistent |
| GMS-V11 | batch all-or-nothing | Missing |
| GMS-V12 | residual/canonical same semantics | Missing |

## 6. Data Semantics

| Concept | Meaning |
|---|---|
| safe method | CSRF-exempt HTTP method, not proof of no side effect |
| GET mutation | state change performed through GET |
| browser confirm | client prompt without server proof |
| Human Confirm | submitted server intent in selected Type A |
| prefetch | automatic retrieval that may trigger write |
| replay | repeated URL request |
| idempotent result | repeated call leaves same state |
| idempotency key | absent command identity in most routes |
| status URL | target state embedded in path |
| create URL | GET inserting a record |
| delete URL | GET deleting a record |
| redirect-after-write | response pattern that does not secure write |
| redirect-only alias | GET 只导航到 Type A，不直接写库 |
| canonical alias | standard route winner |
| residual route | fallback implementation |
| Complete | status transition after Ship |
| Reopen | status rollback without inventory reversal |
| Ship alias | GET redirect to POST confirmation in canonical flow |

## 7. State Vocabulary

| Term | Meaning |
|---|---|
| direct write | GET handler performs mutation |
| redirect-only | GET only navigates to confirmation |
| guarded GET | RBAC/state checked but method unsafe |
| unguarded GET | no server permission |
| status-only | changes lifecycle labels without reversing facts |

## 8. UNKNOWN + 已查路径

| UNKNOWN | 已查路径 |
|---|---|
| production proxy blocks GET mutations | deployment/config/docs |
| browser prefetch policy | templates/headers/proxy |
| every residual GET runtime reachability | bootstrap/route reports |
| all listed local gates under alternate owner | routers/residuals |
| external clients bookmarking these URLs | static code unavailable |
| operation logs for every GET mutation | services/audit/log searches |
| database constraints preventing every replay | schemas/migrations |
| SameSite/HTTPS production cookie config | security config/deployment |
| cache-control behavior on command redirects | middleware/routes |
| which GET mutation aliases remain broken vs live | `docs/reports/Broken_Route_Report.md`, routers/residuals |
| residual_loader order vs canonical winner for GET writes | `runtime/v14/residual_loader.py`, bootstrap |

## 9. Evidence Table

| Read-only path | Evidence |
|---|---|
| `core/security/csrf.py` | GET in SAFE_METHODS |
| `apps/approval/router.py` | approval GET writes |
| `apps/approval/v14_residual.py` | record decision aliases |
| `apps/quotation/router.py` | status/delete/create-from-sample |
| `apps/sales/router.py` | convert/status/create DO |
| `apps/inventory/router.py` | delete/convert/ship alias/complete/reopen |
| `apps/inventory/services.py` | Complete/Reopen effects and gates |
| `apps/finance/router.py` | receipt/invoice/expense/AR |
| `apps/finance/v14_residual.py` | clear followups |
| `apps/procurement/router.py` | receive/delete purchase |
| `apps/customer/router.py` | GET customer delete |
| `apps/product/router.py` | GET product delete |
| `apps/supplier/router.py` | GET supplier delete |
| `core/auth/routes.py` | role/user GET delete contrast |
| `apps/sample/router.py` | image slot delete |
| `apps/sample/router.py` / `services.py` | sample materialization |
| `apps/quotation/router.py` / `services.py` | copy quote and sample conversion |
| `apps/platform/v14_residual.py` | platform/security delete aliases |
| `apps/tenant_center/v14_residual.py` | membership/license deletes |
| `templates/delivery_orders.html` | batch Complete fetch |
| `docs/knowledge/legacy-extract/ship-complete-deepen/do_complete.md` | Complete authority cross-reference |
| `docs/knowledge/legacy-extract/ship-complete-deepen/do_reopen.md` | Reopen authority cross-reference |
| `docs/knowledge/legacy-extract/risk-catalog/permission_holes.md` | PH-007 cross-reference |
| `docs/reports/Broken_Route_Report.md` | broken/orphan route inventory may re-expose GET aliases |
| `docs/reports/ROUTE_OWNER_REPORT.md` | owner of mutating GET paths under standard registration |
| `runtime/v14/residual_loader.py` | residual route loading path for duplicate GET writers |
| `templates/delivery_orders.html` / approval templates | confirm()/batch fetch are client-only intent |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
