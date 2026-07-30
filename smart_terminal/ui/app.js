/**
 * NOVENTI Smart Terminal Complete UI (PHX-G36 / G42).
 * Presentation-only — consumes Gateway; never hosts business rules.
 */

export const FORBIDDEN_BODY_KEYS = Object.freeze([
  "tenant_id",
  "subject_id",
  "platform_scope",
  "session_id",
]);

export const EXTENSION_DEMO_PANEL_SRC = "/terminal/extensions/demo-panel.html";
export const EXTENSION_DEMO_WORKER_SRC = "/terminal/extensions/demo-worker.js";

export const ALLOWED_BRIDGE_MESSAGE_TYPES = Object.freeze([
  "eaos.extension.invoke",
]);

export const ALLOWED_BRIDGE_CHANNELS = Object.freeze(["iframe", "worker"]);

export const SURFACES = Object.freeze([
  "operator",
  "product",
  "crm",
  "ops",
  "approval",
  "admin",
  "ai",
  "extensions",
]);

/** Presentation-only demo catalog (not a business truth store). */
export const DEMO_PRODUCTS = Object.freeze([
  {
    id: "prd-atlas-core",
    name: "Atlas Core",
    sku: "ATL-CORE-01",
    status: "active",
    summary: "企业运营底座能力包：会话、意图与受治理提交。",
    action: "product.offer.review",
    resourceRef: "product:atl-core-01",
    impactSummary: "Review Atlas Core product offer (read-only demo handoff)",
  },
  {
    id: "prd-harbor-ops",
    name: "Harbor Ops",
    sku: "HBR-OPS-02",
    status: "pilot",
    summary: "履约与班次运营包：简报编排与高影响发布闸门。",
    action: "product.offer.review",
    resourceRef: "product:hbr-ops-02",
    impactSummary: "Review Harbor Ops product offer (read-only demo handoff)",
  },
  {
    id: "prd-signal-ai",
    name: "Signal AI Assist",
    sku: "SGL-AI-03",
    status: "draft",
    summary: "AI 协作辅助面：计划预览与证据呈现（advisory）。",
    action: "product.offer.review",
    resourceRef: "product:sgl-ai-03",
    impactSummary: "Review Signal AI Assist product offer (read-only demo handoff)",
  },
]);

/** Presentation-only ops queue aligned with noventi.sample.ops. */
export const DEMO_OPS_ITEMS = Object.freeze([
  {
    id: "ops-shift-am",
    title: "早班履约核对",
    focus: "fulfillment",
    body: "核对今日未关闭履约单，并生成班次简报。",
    action: "ops.brief.compose",
    resourceRef: "pkg.ops.brief:shift-am",
    highImpact: false,
  },
  {
    id: "ops-escalation",
    title: "异常升级发布",
    focus: "escalation",
    body: "将阻塞订单升级为租户级运营通告（高影响）。",
    action: "ops.brief.publish",
    resourceRef: "pkg.ops.brief:escalation",
    highImpact: true,
  },
  {
    id: "ops-capacity",
    title: "产能负荷观察",
    focus: "capacity",
    body: "汇总本周产能负荷，仅生成只读运营简报。",
    action: "ops.brief.compose",
    resourceRef: "pkg.ops.brief:capacity",
    highImpact: false,
  },
]);

/**
 * Knowledge-aligned Sample flow demo steps (Terminal presentation only).
 * Source narrative: docs/knowledge/legacy-extract/sample/
 */
export const DEMO_SAMPLE_FLOW = Object.freeze([
  {
    id: "sample-intake",
    title: "1. 收样建档",
    body: "选择客户，生成 SP 编号，收样日期当天，状态 New。",
    action: "sample.intake.compose",
    resourceRef: "pkg.sample.flow:intake",
    highImpact: false,
    knowledgeRefs: ["SAMPLE-RULE-001", "SAMPLE-RULE-002"],
  },
  {
    id: "sample-analysis",
    title: "2. 样品分析",
    body: "记录尺寸/材质等测量与 Sample360 分析块（需求/材料/质量/供应商匹配）。",
    action: "sample.analysis.compose",
    resourceRef: "pkg.sample.flow:analysis",
    highImpact: false,
    knowledgeRefs: ["SAMPLE-RULE-003", "SAMPLE-RULE-004"],
  },
  {
    id: "sample-stock",
    title: "3. 入库物化",
    body: "绑定目录产品后入库：台账类型 Sample Receipt，状态 Stocked（收货入库≠发样）。",
    action: "sample.stock.compose",
    resourceRef: "pkg.sample.flow:stock",
    highImpact: false,
    knowledgeRefs: ["SAMPLE-RULE-005", "SAMPLE-RULE-006", "SAMPLE-RULE-007"],
  },
  {
    id: "sample-quote",
    title: "4. 转报价",
    body: "从样品创建 Draft 报价，沿用客户与追溯字段（requirement/opportunity）。",
    action: "sample.quote.handoff",
    resourceRef: "pkg.sample.flow:quote",
    highImpact: false,
    knowledgeRefs: ["SAMPLE-RULE-008", "SAMPLE-RULE-009"],
  },
]);

/**
 * Knowledge-aligned Order flow demo steps (Terminal presentation only).
 * Source narrative: docs/knowledge/legacy-extract/sales/ + delivery/ + order-chain/
 */
export const DEMO_ORDER_FLOW = Object.freeze([
  {
    id: "order-convert",
    title: "1. 报价转订单",
    body: "一报价一单；复制客户/行项目；报价状态→已确认；可选佣金钩子。",
    action: "order.convert.compose",
    resourceRef: "pkg.order.flow:convert",
    highImpact: false,
    knowledgeRefs: ["SO-R1", "SO-R3", "SO-R5", "SO-R7"],
  },
  {
    id: "order-approve",
    title: "2. 订单批准 Open",
    body: "V18 Human Approved：pending + ≥1 行 → 状态 Open（高影响，需 Workflow）。",
    action: "order.approve.compose",
    resourceRef: "pkg.order.flow:approve",
    highImpact: true,
    knowledgeRefs: ["SO-R10", "SO-R11"],
  },
  {
    id: "order-do",
    title: "3. 创建发货单",
    body: "建 DO + 明细；SO→Delivery Created；创建时不扣库存（Ship 才扣）。",
    action: "order.do.create",
    resourceRef: "pkg.order.flow:do",
    highImpact: false,
    knowledgeRefs: ["SO-R12"],
  },
  {
    id: "order-fulfill",
    title: "4. 履约核对",
    body: "Ship / Complete / DO→AR 交界只读核对；承运跟踪可诚实缺口。",
    action: "order.fulfill.compose",
    resourceRef: "pkg.order.flow:fulfill",
    highImpact: false,
    knowledgeRefs: ["SO-R13"],
  },
]);

/** Default action_key per declared surface_key (Package Surface projection). */
export const SURFACE_DEFAULT_ACTIONS = Object.freeze({
  "product.catalog": "product.offer.review",
  "product.sample": "sample.intake.compose",
  "ops.workbench": "ops.brief.compose",
  "ops.order": "order.convert.compose",
});

export const TERMINAL_PATHS = Object.freeze({
  sessions: "/v1/terminal/sessions",
  session: (id) => `/v1/terminal/sessions/${id}`,
  intents: "/v1/terminal/intents",
  intent: (id) => `/v1/terminal/intents/${id}`,
  previews: "/v1/terminal/previews",
  preview: (id) => `/v1/terminal/previews/${id}`,
  approvals: (id) => `/v1/terminal/previews/${id}/approvals`,
  commit: (id) => `/v1/terminal/previews/${id}/commits`,
  extensions: "/v1/terminal/extensions",
  extensionActivate: (id) => `/v1/terminal/extensions/${id}/activate`,
  extensionRevoke: (id) => `/v1/terminal/extensions/${id}/revoke`,
  extensionActions: (id) => `/v1/terminal/extensions/${id}/actions`,
  health: "/v1/health",
  release: "/v1/release",
  adapters: "/v1/adapters",
  context: "/v1/context",
  contextEcho: "/v1/context/echo",
  crmCustomers: "/v1/crm/customers",
  crmCustomer: (id) => `/v1/crm/customers/${id}`,
  crmCustomer360: (id) => `/v1/crm/customers/${id}/360`,
  crmCustomerArchive: (id) => `/v1/crm/customers/${id}/archive`,
  crmContacts: (customerId) => `/v1/crm/customers/${customerId}/contacts`,
  crmContact: (customerId, contactId) =>
    `/v1/crm/customers/${customerId}/contacts/${contactId}`,
  crmContactArchive: (customerId, contactId) =>
    `/v1/crm/customers/${customerId}/contacts/${contactId}/archive`,
  crmOpportunities: "/v1/crm/opportunities",
  crmOpportunity: (id) => `/v1/crm/opportunities/${id}`,
  crmOpportunityArchive: (id) => `/v1/crm/opportunities/${id}/archive`,
  crmRequirements: "/v1/crm/requirements",
  crmRequirement: (id) => `/v1/crm/requirements/${id}`,
  crmRequirementArchive: (id) => `/v1/crm/requirements/${id}/archive`,
  crmQuotes: "/v1/crm/quotes",
  crmQuote: (id) => `/v1/crm/quotes/${id}`,
  crmQuoteArchive: (id) => `/v1/crm/quotes/${id}/archive`,
  crmQuoteLines: (quoteId) => `/v1/crm/quotes/${quoteId}/lines`,
  crmQuoteLine: (quoteId, lineId) =>
    `/v1/crm/quotes/${quoteId}/lines/${lineId}`,
  crmQuoteLineArchive: (quoteId, lineId) =>
    `/v1/crm/quotes/${quoteId}/lines/${lineId}/archive`,
  crmQuoteIssue: (id) => `/v1/crm/quotes/${id}/issue`,
  crmQuoteConvert: (id) => `/v1/crm/quotes/${id}/convert`,
  crmConversion: (id) => `/v1/crm/conversions/${id}`,
  crmConversionSalesOrder: (id) => `/v1/crm/conversions/${id}/sales-order`,
  crmSalesOrders: "/v1/crm/sales-orders",
  crmSalesOrder: (id) => `/v1/crm/sales-orders/${id}`,
  crmSalesOrderLines: (id) => `/v1/crm/sales-orders/${id}/lines`,
  crmSalesOrderConfirm: (id) => `/v1/crm/sales-orders/${id}/confirm`,
  crmSalesOrderDeliveryOrder: (id) =>
    `/v1/crm/sales-orders/${id}/delivery-order`,
  crmDeliveryOrder: (id) => `/v1/crm/delivery-orders/${id}`,
  crmDeliveryOrderRelease: (id) => `/v1/crm/delivery-orders/${id}/release`,
  crmDeliveryOrderArInvoice: (id) =>
    `/v1/crm/delivery-orders/${id}/ar-invoice`,
  crmArInvoice: (id) => `/v1/crm/ar-invoices/${id}`,
  crmArInvoiceIssue: (id) => `/v1/crm/ar-invoices/${id}/issue`,
  crmArInvoiceVoid: (id) => `/v1/crm/ar-invoices/${id}/void`,
  crmDeliveryOrderReturnAuthorization: (id) =>
    `/v1/crm/delivery-orders/${id}/return-authorizations`,
  crmReturnAuthorization: (id) => `/v1/crm/return-authorizations/${id}`,
  idpStatus: "/v1/auth/idp/status",
  jwtStatus: "/v1/auth/jwt/status",
  marketplaceStatus: "/v1/marketplace/status",
  marketplaceListings: "/v1/marketplace/listings",
  marketplaceListing: (id) => `/v1/marketplace/listings/${id}`,
  marketplaceListingSignature: (id) => `/v1/marketplace/listings/${id}/signature`,
  marketplaceListingSubmit: (id) => `/v1/marketplace/listings/${id}/submit`,
  marketplaceListingReview: (id) => `/v1/marketplace/listings/${id}/review`,
  marketplaceListingPublish: (id) => `/v1/marketplace/listings/${id}/publish`,
  marketplaceListingAcquire: (id) => `/v1/marketplace/listings/${id}/acquire`,
  marketplaceListingHostAcquire: (id) =>
    `/v1/marketplace/listings/${id}/host-acquire`,
  marketplaceListingRevoke: (id) => `/v1/marketplace/listings/${id}/revoke`,
  marketplaceListingPricing: (id) => `/v1/marketplace/listings/${id}/pricing`,
  marketplaceListingInvoices: (id) => `/v1/marketplace/listings/${id}/invoices`,
  marketplaceListingPaymentClearing: (id) =>
    `/v1/marketplace/listings/${id}/payment-clearing`,
  marketplaceListingDisputes: (id) => `/v1/marketplace/listings/${id}/disputes`,
  marketplaceListingRevenueShare: (id) =>
    `/v1/marketplace/listings/${id}/revenue-share`,
  marketplaceDisputeResolve: (id) => `/v1/marketplace/disputes/${id}/resolve`,
  workflowStatus: "/v1/workflow/status",
  workflowDefinitions: "/v1/workflow/definitions",
  workflowDefinitionDeprecation: (id) =>
    `/v1/workflow/definitions/${id}/deprecation`,
  workflowInstances: "/v1/workflow/instances",
  workflowInstance: (id) => `/v1/workflow/instances/${id}`,
  workflowTasks: "/v1/workflow/tasks",
  workflowTaskApproval: (instanceId, taskId) =>
    `/v1/workflow/instances/${instanceId}/tasks/${taskId}/approval`,
  workflowTaskRejection: (instanceId, taskId) =>
    `/v1/workflow/instances/${instanceId}/tasks/${taskId}/rejection`,
  workflowInstanceSignal: (id) => `/v1/workflow/instances/${id}/signals`,
  workflowInstanceCancel: (id) => `/v1/workflow/instances/${id}/cancellation`,
  workflowInstanceCompensate: (id) => `/v1/workflow/instances/${id}/compensation`,
  workflowTaskEscalation: (instanceId, taskId) =>
    `/v1/workflow/instances/${instanceId}/tasks/${taskId}/escalation`,
  packageStatus: "/v1/packages/status",
  terminalStatus: "/v1/terminal/status",
  eventStatus: "/v1/events/status",
  eventCatalog: "/v1/events/catalog",
  financeStatus: "/v1/finance/status",
  platformDigitalEmployeeStatus: "/v1/platform/digital-employee/status",
  platformIndustryPackageStatus: "/v1/platform/industry-package/status",
  platformAiWorkforceStatus: "/v1/platform/ai-workforce/status",
  packageManifests: "/v1/packages/manifests",
  packageManifest: (id) => `/v1/packages/manifests/${id}`,
  packageManifestPublish: (id) => `/v1/packages/manifests/${id}/publish`,
  packageInstallations: "/v1/packages/installations",
  packageInstallationDisable: (id) => `/v1/packages/installations/${id}/disable`,
  packageSurfaces: "/v1/packages/surfaces",
  packageActionResolve: "/v1/packages/actions/resolve",
  demoBootstrap: "/v1/demo/bootstrap",
  knowledgeStatus: "/v1/knowledge/status",
  knowledgeEntities: "/v1/knowledge/entities",
  knowledgeEntity: (id) => `/v1/knowledge/entities/${id}`,
  knowledgeEntityArchive: (id) => `/v1/knowledge/entities/${id}/archive`,
  knowledgeEntityShare: (id) => `/v1/knowledge/entities/${id}/share`,
  knowledgeSearch: "/v1/knowledge/search",
  knowledgeLinks: "/v1/knowledge/links",
  knowledgeProvenance: (kind, id) => `/v1/knowledge/provenance/${kind}/${id}`,
  twinStatus: "/v1/twin/status",
  twinSnapshots: "/v1/twin/snapshots",
  twinSnapshot: (id) => `/v1/twin/snapshots/${id}`,
  twinAuthorize: (id) => `/v1/twin/snapshots/${id}/authorize`,
  brainStatus: "/v1/brain/status",
  brainInsights: "/v1/brain/insights",
  brainInsight: (id) => `/v1/brain/insights/${id}`,
  brainExecute: (id) => `/v1/brain/insights/${id}/execute`,
  aiStatus: "/v1/ai/status",
  aiRuns: "/v1/ai/runs",
  aiRun: (id) => `/v1/ai/runs/${id}`,
  aiTools: "/v1/ai/tools",
  aiToolInvocations: (runId) => `/v1/ai/runs/${runId}/tools/invocations`,
  aiMemory: (runId) => `/v1/ai/runs/${runId}/memory`,
  aiMemoryKey: (runId, key) => `/v1/ai/runs/${runId}/memory/${key}`,
  aiApprovals: (runId) => `/v1/ai/runs/${runId}/approvals`,
  aiCommits: (runId) => `/v1/ai/runs/${runId}/commits`,
  identityStatus: "/v1/identity/status",
  identitySubjects: "/v1/identity/subjects",
  identitySubject: (id) => `/v1/identity/subjects/${id}`,
  identityCredentials: "/v1/identity/credentials",
  identityCredentialValidation: (id) =>
    `/v1/identity/credentials/${id}/validation`,
  identityCredentialRevocation: (id) =>
    `/v1/identity/credentials/${id}/revocation`,
  identitySessions: "/v1/identity/sessions",
  identitySessionValidation: (id) => `/v1/identity/sessions/${id}/validation`,
  identitySessionRevocation: (id) => `/v1/identity/sessions/${id}/revocation`,
  identityPlatformGovernors: "/v1/identity/platform-governors",
  identityPlatformGovernorRevocation: (id) =>
    `/v1/identity/platform-governors/${id}/revocation`,
  identityAiEmployees: "/v1/identity/ai-employees",
  identityAiProfile: (id) => `/v1/identity/ai-employees/${id}/profile`,
  identityAiAssignments: (id) => `/v1/identity/ai-employees/${id}/assignments`,
  identityAiReassignments: (id) =>
    `/v1/identity/ai-employees/${id}/reassignments`,
  organizationStatus: "/v1/organization/status",
  organizationTenant: (id) => `/v1/tenants/${id}`,
  organizationEnterprises: "/v1/enterprises",
  organizationEnterprise: (id) => `/v1/enterprises/${id}`,
  organizationEnterpriseSuspension: (id) => `/v1/enterprises/${id}/suspension`,
  organizationEnterpriseEnd: (id) => `/v1/enterprises/${id}`,
  organizationUnits: "/v1/organization-units",
  organizationUnitTree: "/v1/organization-units/tree",
  organizationMemberships: "/v1/memberships",
  organizationUnitStatus: (id) => `/v1/organization-units/${id}/status`,
  organizationMembershipSuspension: (id) => `/v1/memberships/${id}/suspension`,
  organizationMembershipUnit: (id) => `/v1/memberships/${id}/unit`,
  organizationMembershipEnd: (id) => `/v1/memberships/${id}`,
  platformTenants: "/v1/platform/tenants",
  platformTenantSuspension: (id) => `/v1/platform/tenants/${id}/suspension`,
  eventStats: "/v1/events/stats",
  eventDeadLetters: "/v1/events/dead-letters",
  eventDeadLetterReplay: (id) => `/v1/events/dead-letters/${id}/replay`,
  eventDispatch: "/v1/events/dispatch",
  eventById: (id) => `/v1/events/${id}`,
  eventPublish: "/v1/events",
  eventOutbox: "/v1/events/outbox",
  eventSubscriptions: "/v1/events/subscriptions",
  eventReplay: (id) => `/v1/events/${id}/replay`,
  oidcRefresh: "/v1/auth/oidc/refresh",
  oidcLogout: "/v1/auth/oidc/logout",
  oidcProviders: "/v1/auth/oidc/providers",
  oidcStatus: "/v1/auth/oidc/status",
  oidcMfaEnrollment: "/v1/auth/oidc/mfa-enrollment",
  idpIssuers: "/v1/platform/idp/issuers",
  idpIssuerDisable: (id) => `/v1/platform/idp/issuers/${id}/disable`,
  platformRoles: "/v1/platform/roles",
  platformRoleDisable: (id) => `/v1/platform/roles/${id}/disable`,
  tenantRoles: "/v1/permission/roles",
  rolesStatus: "/v1/permission/roles/status",
  evaluations: "/v1/permission/evaluations",
  permissionPolicies: "/v1/permission/policies",
  permissionPolicyActivation: (id) => `/v1/permission/policies/${id}/activation`,
  permissionPolicyDeprecation: (id) => `/v1/permission/policies/${id}/deprecation`,
  permissionGrants: "/v1/permission/grants",
  permissionGrantRevocation: (id) => `/v1/permission/grants/${id}/revocation`,
  permissionGrantDelegations: (id) => `/v1/permission/grants/${id}/delegations`,
  decisionExplanation: (id) => `/v1/permission/decisions/${id}/explanation`,
  effectivePermissions: (subjectId) =>
    `/v1/permission/principals/${subjectId}/effective-permissions`,
  idpDiscoverySync: "/v1/platform/idp/discovery/sync",
  fedMatrix: "/v1/platform/idp/federation/matrix",
  fedBindings: (tenantId) =>
    `/v1/platform/idp/federation/tenants/${tenantId}/bindings`,
  fedUnbind: (bindingId) =>
    `/v1/platform/idp/federation/bindings/${bindingId}/unbind`,
  fedPriority: (bindingId) =>
    `/v1/platform/idp/federation/bindings/${bindingId}/priority`,
});

const state = {
  surface: "operator",
  sessionId: null,
  intentId: null,
  previewId: null,
  receipt: null,
  approval: null,
  extensionId: null,
  accessToken: null,
  extensionFrameMounted: false,
  extensionWorker: null,
  selectedProductId: null,
  selectedOpsId: null,
  selectedProductSurfaceKey: null,
  selectedOpsSurfaceKey: null,
  selectedSampleFlowId: null,
  selectedOrderFlowId: null,
  packageSurfaces: [],
  packageSurfacesSource: "fixture",
  extensionKeyHint: "noventi.demo.panel",
  extensionHydrated: false,
  hostActions: [],
  demoListingId: null,
  crmCustomers: [],
  crmContacts: [],
  crmCustomerCursor: null,
  crmContactCursor: null,
  selectedCrmCustomerId: null,
  selectedCrmContactId: null,
  selectedCrmCustomer: null,
  selectedCrmContact: null,
  selectedCrmCustomer360: null,
  crmPermissionGrants: [],
  crmPermissionsLoaded: false,
  crmArchiveTarget: null,
  crmOpportunities: [],
  crmOpportunityCursor: null,
  selectedCrmOpportunityId: null,
  selectedCrmOpportunity: null,
  crmRequirements: [],
  crmRequirementCursor: null,
  selectedCrmRequirementId: null,
  selectedCrmRequirement: null,
  crmQuotes: [],
  crmQuoteCursor: null,
  selectedCrmQuoteId: null,
  selectedCrmQuote: null,
  crmQuoteLines: [],
  selectedCrmQuoteLineId: null,
  selectedCrmQuoteLine: null,
  selectedCrmConversion: null,
  selectedCrmConvertSalesOrder: null,
  crmSalesOrders: [],
  crmSalesOrderCursor: null,
  selectedCrmSalesOrderId: null,
  selectedCrmSalesOrder: null,
  crmSalesOrderLines: [],
  selectedCrmSalesOrderLineId: null,
  selectedCrmSalesOrderLine: null,
  selectedCrmDeliveryOrder: null,
  selectedCrmArInvoice: null,
  selectedCrmReturnAuthorization: null,
  crmLoaded: false,
};

function $(id) {
  return document.getElementById(id);
}

function log(message, payload) {
  const line =
    payload === undefined
      ? message
      : `${message}\n${JSON.stringify(payload, null, 2)}`;
  const node = $("log");
  node.textContent = `${node.textContent}${line}\n\n`;
}

function setStep(step) {
  const order = ["session", "intent", "preview", "approval", "commit", "receipt"];
  const active = order.indexOf(step);
  document.querySelectorAll("#lifecycleSteps li").forEach((el) => {
    const idx = order.indexOf(el.dataset.step);
    el.classList.toggle("is-active", idx === active);
    el.classList.toggle("is-done", idx >= 0 && idx < active);
  });
}

function updateSessionIndicator() {
  const field = document.querySelector('#sessionIndicator [data-field="session"]');
  if (field) {
    field.textContent = state.sessionId || "—";
  }
}

function setEnabled(id, enabled) {
  const node = $(id);
  if (node) {
    node.disabled = !enabled;
  }
}

function syncButtons() {
  const hasSession = Boolean(state.sessionId);
  const hasIntent = Boolean(state.intentId);
  const hasPreview = Boolean(state.previewId);
  setEnabled("btnComposeIntent", hasSession);
  setEnabled("btnRefreshSession", hasSession);
  setEnabled("btnCloseSession", hasSession);
  setEnabled("btnRefreshIntent", hasIntent);
  setEnabled("btnBuildPreview", hasIntent);
  setEnabled("btnRefreshPreview", hasPreview);
  setEnabled("btnCommit", hasPreview);
  setEnabled("btnRequestApproval", hasPreview);
  setEnabled("btnPresentApproval", hasPreview);
  setEnabled("btnAiCompose", hasSession);
  updateSessionIndicator();
}

function switchSurface(name) {
  if (!SURFACES.includes(name)) {
    return;
  }
  state.surface = name;
  document.querySelectorAll(".surface-tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.surface === name);
  });
  document.querySelectorAll("[data-surface-panel]").forEach((panel) => {
    const active = panel.dataset.surfacePanel === name;
    panel.classList.toggle("is-active", active);
    panel.hidden = !active;
  });
  if (typeof history !== "undefined" && typeof location !== "undefined") {
    const nextHash = `#${name}`;
    if (location.hash !== nextHash) {
      history.replaceState(null, "", nextHash);
    }
  }
  if (name === "extensions") {
    loadExtHostPathReadiness({ quiet: true }).catch((err) => {
      log("Host-path readiness skipped", { message: String(err.message || err) });
    });
    hydrateSignedExtensionHost().catch((err) => {
      log("Extension hydrate skipped", { message: String(err.message || err) });
    });
  }
  if (name === "crm" && !state.crmLoaded) {
    loadCrmPermissions()
      .catch(() => {})
      .then(() =>
        Promise.all([
          loadCrmCustomers(),
          loadCrmOpportunities(),
          loadCrmRequirements(),
          loadCrmQuotes(),
          loadCrmSalesOrders(),
        ]),
      )
      .catch((err) => {
        log("CRM customer load failed", { message: String(err.message || err) });
      });
  }
}

function handoffToOperator({
  intentText,
  action,
  resourceRef,
  planVersion = "v1",
  scope = "tenant",
  impactSummary,
  highImpact = false,
}) {
  if ($("intentText")) {
    $("intentText").value = intentText;
  }
  if ($("action")) {
    $("action").value = action;
  }
  if ($("resourceRef")) {
    $("resourceRef").value = resourceRef;
  }
  if ($("planVersion")) {
    $("planVersion").value = planVersion;
  }
  if ($("scope")) {
    $("scope").value = scope;
  }
  if ($("impactSummary")) {
    $("impactSummary").value = impactSummary;
  }
  if ($("highImpact")) {
    $("highImpact").checked = Boolean(highImpact);
  }
  switchSurface("operator");
  log("Handoff to Operator", {
    action,
    resourceRef,
    highImpact: Boolean(highImpact),
  });
}

function surfacesForPrefix(prefix) {
  return (state.packageSurfaces || []).filter((item) =>
    String(item.surface_key || "")
      .toLowerCase()
      .startsWith(prefix),
  );
}

function crmCan(resourceType, action, resourceId = null) {
  if (!state.crmPermissionsLoaded) {
    return false;
  }
  return state.crmPermissionGrants.some((grant) => {
    if (
      grant?.effect !== "allow" ||
      grant?.resource_type !== resourceType ||
      !Array.isArray(grant?.actions) ||
      !grant.actions.includes(action)
    ) {
      return false;
    }
    if (grant.resource_id) {
      return Boolean(resourceId) && String(grant.resource_id) === String(resourceId);
    }
    return true;
  });
}

function syncCrmWriteControls() {
  const canCreateCustomer = crmCan("pkg.crm.customer", "create");
  const canEditCustomer = crmCan(
    "pkg.crm.customer",
    "update",
    state.selectedCrmCustomerId,
  );
  const canArchiveCustomer = crmCan(
    "pkg.crm.customer",
    "archive",
    state.selectedCrmCustomerId,
  );
  const canCreateContact =
    Boolean(state.selectedCrmCustomerId) && crmCan("pkg.crm.contact", "create");
  const canEditContact = crmCan(
    "pkg.crm.contact",
    "update",
    state.selectedCrmContactId,
  );
  const canArchiveContact = crmCan(
    "pkg.crm.contact",
    "archive",
    state.selectedCrmContactId,
  );
  const canCreateOpportunity =
    state.crmCustomers.length > 0 && crmCan("pkg.crm.opportunity", "create");
  const canEditOpportunity = crmCan(
    "pkg.crm.opportunity",
    "update",
    state.selectedCrmOpportunityId,
  );
  const canArchiveOpportunity = crmCan(
    "pkg.crm.opportunity",
    "archive",
    state.selectedCrmOpportunityId,
  );
  const canCreateRequirement =
    state.crmOpportunities.length > 0 &&
    crmCan("pkg.crm.requirement", "create");
  const canEditRequirement = crmCan(
    "pkg.crm.requirement",
    "update",
    state.selectedCrmRequirementId,
  );
  const canArchiveRequirement = crmCan(
    "pkg.crm.requirement",
    "archive",
    state.selectedCrmRequirementId,
  );
  const canCreateQuote =
    state.crmRequirements.length > 0 && crmCan("pkg.crm.quote", "create");
  const canEditQuote = crmCan(
    "pkg.crm.quote",
    "update",
    state.selectedCrmQuoteId,
  );
  const canArchiveQuote = crmCan(
    "pkg.crm.quote",
    "archive",
    state.selectedCrmQuoteId,
  );
  const canCreateQuoteLine =
    Boolean(state.selectedCrmQuoteId) &&
    crmCan("pkg.crm.quote_line", "create", state.selectedCrmQuoteId);
  const canEditQuoteLine = crmCan(
    "pkg.crm.quote_line",
    "update",
    state.selectedCrmQuoteLineId,
  );
  const canArchiveQuoteLine = crmCan(
    "pkg.crm.quote_line",
    "archive",
    state.selectedCrmQuoteLineId,
  );
  const canIssueQuote =
    state.selectedCrmQuote?.status === "draft" &&
    crmCan("pkg.crm.quote", "issue", state.selectedCrmQuoteId);
  const canConvertQuote =
    state.selectedCrmQuote?.status === "issued" &&
    crmCan("pkg.crm.quote_conversion", "convert", state.selectedCrmQuoteId);
  const canCreateSalesOrderShell =
    state.selectedCrmConversion?.status === "ready" &&
    !state.selectedCrmConvertSalesOrder &&
    crmCan(
      "pkg.crm.sales_order",
      "create",
      state.selectedCrmConversion.id,
    );
  const canConfirmSalesOrder =
    state.selectedCrmSalesOrder?.status === "created" &&
    crmCan(
      "pkg.crm.sales_order",
      "confirm",
      state.selectedCrmSalesOrderId,
    );
  const canCreateDeliveryOrder =
    (state.selectedCrmSalesOrder?.status === "confirmed" ||
      state.selectedCrmSalesOrder?.status === "partially_shipped") &&
    crmCan(
      "pkg.crm.delivery_order",
      "create",
      state.selectedCrmSalesOrderId,
    );
  const canReleaseDeliveryOrder =
    state.selectedCrmDeliveryOrder?.status === "draft" &&
    crmCan(
      "pkg.crm.delivery_order",
      "release",
      state.selectedCrmDeliveryOrder.id,
    );
  const canCreateArInvoice =
    state.selectedCrmDeliveryOrder?.status === "released" &&
    crmCan(
      "pkg.crm.ar_invoice",
      "create",
      state.selectedCrmDeliveryOrder.id,
    );
  const canIssueArInvoice =
    state.selectedCrmArInvoice?.status === "draft" &&
    crmCan("pkg.crm.ar_invoice", "issue", state.selectedCrmArInvoice.id);
  const canVoidArInvoice =
    state.selectedCrmArInvoice?.status === "issued" &&
    crmCan("pkg.crm.ar_invoice", "void", state.selectedCrmArInvoice.id);
  const canCreateReturnAuthorization =
    state.selectedCrmDeliveryOrder?.status === "shipped" &&
    crmCan(
      "pkg.crm.return_authorization",
      "create",
      state.selectedCrmDeliveryOrder.id,
    );

  $("btnCrmNewCustomer").hidden = !canCreateCustomer;
  $("btnCrmEditCustomer").hidden = !canEditCustomer;
  $("btnCrmArchiveCustomer").hidden = !canArchiveCustomer;
  $("btnCrmNewContact").hidden = !canCreateContact;
  $("crmCustomerWriteControls").hidden = !(
    canEditCustomer ||
    canArchiveCustomer ||
    canCreateContact
  );
  $("btnCrmEditContact").hidden = !canEditContact;
  $("btnCrmArchiveContact").hidden = !canArchiveContact;
  $("crmContactWriteControls").hidden = !(canEditContact || canArchiveContact);
  $("btnCrmNewOpportunity").hidden = !canCreateOpportunity;
  $("btnCrmEditOpportunity").hidden = !canEditOpportunity;
  $("btnCrmArchiveOpportunity").hidden = !canArchiveOpportunity;
  $("crmOpportunityWriteControls").hidden = !(
    canEditOpportunity || canArchiveOpportunity
  );
  $("btnCrmNewRequirement").hidden = !canCreateRequirement;
  $("btnCrmEditRequirement").hidden = !canEditRequirement;
  $("btnCrmArchiveRequirement").hidden = !canArchiveRequirement;
  $("crmRequirementWriteControls").hidden = !(
    canEditRequirement || canArchiveRequirement
  );
  $("btnCrmNewQuote").hidden = !canCreateQuote;
  $("btnCrmEditQuote").hidden = !canEditQuote;
  $("btnCrmArchiveQuote").hidden = !canArchiveQuote;
  $("btnCrmIssueQuote").hidden = !canIssueQuote;
  $("btnCrmConvertQuote").hidden = !canConvertQuote;
  $("crmQuoteWriteControls").hidden = !(
    canEditQuote ||
    canArchiveQuote ||
    canIssueQuote ||
    canConvertQuote
  );
  $("btnCrmNewQuoteLine").hidden = !canCreateQuoteLine;
  $("btnCrmEditQuoteLine").hidden = !canEditQuoteLine;
  $("btnCrmArchiveQuoteLine").hidden = !canArchiveQuoteLine;
  $("crmQuoteLineWriteControls").hidden = !(
    canEditQuoteLine || canArchiveQuoteLine
  );
  $("btnCrmCreateSalesOrder").hidden = !canCreateSalesOrderShell;
  $("crmConversionWriteControls").hidden = !canCreateSalesOrderShell;
  $("btnCrmConfirmSalesOrder").hidden = !canConfirmSalesOrder;
  $("btnCrmCreateDeliveryOrder").hidden = !canCreateDeliveryOrder;
  $("crmSalesOrderWriteControls").hidden = !(
    canConfirmSalesOrder || canCreateDeliveryOrder
  );
  $("btnCrmReleaseDeliveryOrder").hidden = !canReleaseDeliveryOrder;
  $("btnCrmCreateArInvoice").hidden = !canCreateArInvoice;
  $("btnCrmCreateReturnAuthorization").hidden = !canCreateReturnAuthorization;
  $("crmDeliveryOrderWriteControls").hidden = !(
    canReleaseDeliveryOrder ||
    canCreateArInvoice ||
    canCreateReturnAuthorization
  );
  $("btnCrmIssueArInvoice").hidden = !canIssueArInvoice;
  $("btnCrmVoidArInvoice").hidden = !canVoidArInvoice;
  $("crmArInvoiceWriteControls").hidden = !(canIssueArInvoice || canVoidArInvoice);
}

async function loadCrmPermissions() {
  state.crmPermissionGrants = [];
  state.crmPermissionsLoaded = false;
  syncCrmWriteControls();
  const indicator = $("crmPermissionState");
  indicator.dataset.state = "loading";
  indicator.textContent = "Checking write permissions…";
  const principalId = $("subjectId")?.value.trim();
  if (!principalId) {
    indicator.dataset.state = "denied";
    indicator.textContent = "Write controls locked";
    return false;
  }
  try {
    const payload = await api(
      "GET",
      TERMINAL_PATHS.effectivePermissions(principalId),
      undefined,
      { auth: true, platform: false },
    );
    state.crmPermissionGrants = Array.isArray(payload) ? payload : [];
    state.crmPermissionsLoaded = true;
    const crmGrants = state.crmPermissionGrants.filter((grant) =>
      String(grant?.resource_type || "").startsWith("pkg.crm."),
    );
    indicator.dataset.state = crmGrants.length ? "ready" : "denied";
    indicator.textContent = crmGrants.length
      ? `Managed actions governed · ${crmGrants.length} grant(s)`
      : "No CRM write grants";
    syncCrmWriteControls();
    return true;
  } catch (err) {
    indicator.dataset.state = "denied";
    indicator.textContent = "Write controls locked";
    syncCrmWriteControls();
    log("CRM effective permissions unavailable — writes hidden", {
      message: String(err.message || err),
    });
    return false;
  }
}

function setCrmState(id, kind, message) {
  const node = $(id);
  if (!node) {
    return;
  }
  node.dataset.state = kind;
  node.textContent = message;
}

function formatCrmDate(value) {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
}

function setCrmDetail(id, fields, value) {
  const detail = $(id);
  if (!detail) {
    return;
  }
  for (const field of fields) {
    const node = detail.querySelector(`[data-field="${field}"]`);
    if (node) {
      node.textContent = value?.[field] ?? "—";
    }
  }
}

function crmErrorState(err) {
  if (err?.status === 403 || err?.code === "PERMISSION_DENIED") {
    return ["denied", "Permission denied. Server authorization remains authoritative."];
  }
  if (err?.status === 404 || err?.code === "COMMON_NOT_FOUND") {
    return ["empty", "No governed record was found in this tenant."];
  }
  if (err?.status === 401) {
    return ["denied", "Authentication is required before CRM data can be loaded."];
  }
  return ["error", `CRM query failed: ${String(err?.message || err)}`];
}

function createCrmChoiceRow({ id, title, meta, selected, onSelect }) {
  const row = document.createElement("button");
  row.type = "button";
  row.className = "choice-row";
  row.dataset.recordId = id;
  row.setAttribute("role", "option");
  row.setAttribute("aria-selected", selected ? "true" : "false");
  row.classList.toggle("is-selected", selected);
  const titleNode = document.createElement("span");
  titleNode.className = "choice-title";
  titleNode.textContent = title;
  const metaNode = document.createElement("span");
  metaNode.className = "choice-meta";
  metaNode.textContent = meta;
  row.append(titleNode, metaNode);
  row.addEventListener("click", onSelect);
  return row;
}

function createCrmTraceRow({ id, title, meta }) {
  const row = document.createElement("div");
  row.className = "choice-row crm-trace-row";
  row.dataset.recordId = id;
  row.setAttribute("role", "listitem");
  const titleNode = document.createElement("span");
  titleNode.className = "choice-title";
  titleNode.textContent = title;
  const metaNode = document.createElement("span");
  metaNode.className = "choice-meta";
  metaNode.textContent = meta;
  row.append(titleNode, metaNode);
  return row;
}

function clearCrmCustomer360() {
  state.selectedCrmCustomer360 = null;
  setCrmDetail(
    "crmCustomer360Detail",
    [
      "customer_code",
      "display_name",
      "commercial_hold",
      "opportunities_count",
      "open_sales_orders_count",
      "open_delivery_orders_count",
    ],
    null,
  );
  for (const [listId, countId] of [
    ["crmCustomer360InvoiceList", "crmCustomer360InvoiceCount"],
    ["crmCustomer360ReceiptList", "crmCustomer360ReceiptCount"],
    ["crmCustomer360CreditList", "crmCustomer360CreditCount"],
  ]) {
    $(listId)?.replaceChildren();
    if ($(countId)) $(countId).textContent = "—";
  }
  setCrmState(
    "crmCustomer360State",
    "idle",
    "Select a customer to load Customer 360.",
  );
  setEnabled("btnCrmRefreshCustomer360", false);
}

function renderCrmCustomer360Traces() {
  const projection = state.selectedCrmCustomer360;
  const invoices = Array.isArray(projection?.invoice_traces)
    ? projection.invoice_traces
    : [];
  const receipts = Array.isArray(projection?.applied_receipt_traces)
    ? projection.applied_receipt_traces
    : [];
  const credits = Array.isArray(projection?.credit_note_traces)
    ? projection.credit_note_traces
    : [];
  const invoiceHost = $("crmCustomer360InvoiceList");
  const receiptHost = $("crmCustomer360ReceiptList");
  const creditHost = $("crmCustomer360CreditList");
  invoiceHost?.replaceChildren(
    ...invoices.map((item) =>
      createCrmTraceRow({
        id: item.id,
        title: item.code,
        meta: `${item.status} · ${item.currency} ${item.total_amount}`,
      }),
    ),
  );
  receiptHost?.replaceChildren(
    ...receipts.map((item) =>
      createCrmTraceRow({
        id: item.id,
        title: item.code,
        meta: `${item.status} · ${item.currency} ${item.amount}`,
      }),
    ),
  );
  creditHost?.replaceChildren(
    ...credits.map((item) =>
      createCrmTraceRow({
        id: item.id,
        title: item.code,
        meta: `${item.status} · ${item.currency} ${item.amount}`,
      }),
    ),
  );
  if ($("crmCustomer360InvoiceCount")) {
    $("crmCustomer360InvoiceCount").textContent = String(invoices.length);
  }
  if ($("crmCustomer360ReceiptCount")) {
    $("crmCustomer360ReceiptCount").textContent = String(receipts.length);
  }
  if ($("crmCustomer360CreditCount")) {
    $("crmCustomer360CreditCount").textContent = String(credits.length);
  }
}

async function loadCrmCustomer360() {
  const customerId = state.selectedCrmCustomerId;
  if (!customerId) {
    clearCrmCustomer360();
    return;
  }
  setEnabled("btnCrmRefreshCustomer360", false);
  setCrmState(
    "crmCustomer360State",
    "loading",
    "Loading governed Customer 360…",
  );
  try {
    const payload = await api(
      "GET",
      TERMINAL_PATHS.crmCustomer360(customerId),
    );
    const projection = payload?.data || null;
    state.selectedCrmCustomer360 = projection;
    setCrmDetail(
      "crmCustomer360Detail",
      [
        "customer_code",
        "display_name",
        "opportunities_count",
        "open_sales_orders_count",
        "open_delivery_orders_count",
      ],
      projection,
    );
    const holdNode = $("crmCustomer360Detail")?.querySelector(
      '[data-field="commercial_hold"]',
    );
    if (holdNode) {
      holdNode.textContent =
        projection?.commercial_hold == null
          ? "—"
          : projection.commercial_hold
            ? "Yes"
            : "No";
    }
    renderCrmCustomer360Traces();
    setCrmState(
      "crmCustomer360State",
      "ready",
      "Customer 360 projection loaded. Traces are read-only.",
    );
    setEnabled("btnCrmRefreshCustomer360", true);
    log("CRM Customer 360 loaded", {
      customer_id: customerId,
      opportunities_count: projection?.opportunities_count ?? null,
      invoice_traces: projection?.invoice_traces?.length ?? 0,
    });
  } catch (err) {
    state.selectedCrmCustomer360 = null;
    renderCrmCustomer360Traces();
    setCrmDetail(
      "crmCustomer360Detail",
      [
        "customer_code",
        "display_name",
        "commercial_hold",
        "opportunities_count",
        "open_sales_orders_count",
        "open_delivery_orders_count",
      ],
      null,
    );
    const [kind, message] = crmErrorState(err);
    setCrmState("crmCustomer360State", kind, message);
    setEnabled("btnCrmRefreshCustomer360", true);
  }
}

function renderCrmCustomers() {
  const host = $("crmCustomerList");
  if (!host) {
    return;
  }
  host.replaceChildren();
  for (const customer of state.crmCustomers) {
    host.appendChild(
      createCrmChoiceRow({
        id: customer.id,
        title: customer.display_name,
        meta: `${customer.code} · ${customer.status}`,
        selected: customer.id === state.selectedCrmCustomerId,
        onSelect: () => {
          selectCrmCustomer(customer.id).catch((err) => {
            log("CRM customer selection failed", { message: String(err.message || err) });
          });
        },
      }),
    );
  }
  $("crmCustomerCount").textContent = String(state.crmCustomers.length);
}

function renderCrmContacts() {
  const host = $("crmContactList");
  if (!host) {
    return;
  }
  host.replaceChildren();
  for (const contact of state.crmContacts) {
    host.appendChild(
      createCrmChoiceRow({
        id: contact.id,
        title: contact.display_name,
        meta: `${contact.title || "No title"} · ${contact.status}`,
        selected: contact.id === state.selectedCrmContactId,
        onSelect: () => {
          selectCrmContact(contact.id).catch((err) => {
            log("CRM contact selection failed", { message: String(err.message || err) });
          });
        },
      }),
    );
  }
  $("crmContactCount").textContent = String(state.crmContacts.length);
}

async function loadCrmCustomers({ append = false } = {}) {
  if (!append) {
    state.crmCustomers = [];
    state.crmCustomerCursor = null;
    state.selectedCrmCustomerId = null;
    state.selectedCrmContactId = null;
    state.selectedCrmCustomer = null;
    state.selectedCrmContact = null;
    state.crmContacts = [];
    renderCrmContacts();
    clearCrmCustomer360();
    setCrmDetail(
      "crmCustomerDetail",
      ["code", "display_name", "status", "commercial_hold", "owner_subject_id", "updated_at"],
      null,
    );
    setCrmDetail(
      "crmContactDetail",
      ["display_name", "title", "email", "phone", "status", "updated_at"],
      null,
    );
    $("crmCustomerDetailHeading").textContent = "Select a customer";
    $("crmContactDetailHeading").textContent = "Select a contact";
    setCrmState("crmContactState", "idle", "Select a customer to load contacts.");
    syncCrmWriteControls();
  }
  setCrmState("crmCustomerState", "loading", "Loading governed customers…");
  setEnabled("btnCrmRefreshCustomers", false);
  setEnabled("btnCrmMoreCustomers", false);
  try {
    const query = new URLSearchParams({ limit: "50" });
    if (append && state.crmCustomerCursor) {
      query.set("cursor", state.crmCustomerCursor);
    }
    const payload = await api("GET", `${TERMINAL_PATHS.crmCustomers}?${query}`);
    const items = Array.isArray(payload?.data?.items) ? payload.data.items : [];
    const known = new Set(state.crmCustomers.map((item) => item.id));
    state.crmCustomers.push(...items.filter((item) => !known.has(item.id)));
    state.crmCustomerCursor = payload?.data?.next_cursor || null;
    state.crmLoaded = true;
    renderCrmCustomers();
    syncCrmWriteControls();
    setCrmState(
      "crmCustomerState",
      state.crmCustomers.length ? "ready" : "empty",
      state.crmCustomers.length
        ? `${state.crmCustomers.length} active customer record(s) loaded.`
        : "No active customers are visible in this tenant.",
    );
    setEnabled("btnCrmMoreCustomers", Boolean(state.crmCustomerCursor));
    log("CRM customers loaded", {
      count: items.length,
      next_cursor: Boolean(state.crmCustomerCursor),
    });
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmCustomerState", kind, message);
    state.crmLoaded = false;
  } finally {
    setEnabled("btnCrmRefreshCustomers", true);
  }
}

async function selectCrmCustomer(customerId) {
  state.selectedCrmCustomerId = customerId;
  state.selectedCrmContactId = null;
  state.selectedCrmCustomer = null;
  state.selectedCrmContact = null;
  clearCrmCustomer360();
  syncCrmWriteControls();
  renderCrmCustomers();
  renderCrmContacts();
  setCrmState("crmCustomerState", "loading", "Loading customer detail…");
  try {
    const payload = await api("GET", TERMINAL_PATHS.crmCustomer(customerId));
    const customer = payload?.data;
    state.selectedCrmCustomer = customer || null;
    setCrmDetail(
      "crmCustomerDetail",
      ["code", "display_name", "status", "commercial_hold", "owner_subject_id"],
      customer,
    );
    const updatedNode = $("crmCustomerDetail")?.querySelector('[data-field="updated_at"]');
    if (updatedNode) {
      updatedNode.textContent = formatCrmDate(customer?.updated_at);
    }
    $("crmCustomerDetailHeading").textContent = customer?.display_name || "Customer";
    syncCrmWriteControls();
    setCrmState("crmCustomerState", "ready", "Customer detail loaded.");
    await Promise.all([loadCrmContacts(), loadCrmCustomer360()]);
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmCustomerState", kind, message);
  }
}

async function loadCrmContacts({ append = false } = {}) {
  const customerId = state.selectedCrmCustomerId;
  if (!customerId) {
    setCrmState("crmContactState", "idle", "Select a customer to load contacts.");
    return;
  }
  if (!append) {
    state.crmContacts = [];
    state.crmContactCursor = null;
    state.selectedCrmContactId = null;
    state.selectedCrmContact = null;
    syncCrmWriteControls();
    renderCrmContacts();
    setCrmDetail(
      "crmContactDetail",
      ["display_name", "title", "email", "phone", "status", "updated_at"],
      null,
    );
    $("crmContactDetailHeading").textContent = "Select a contact";
  }
  setCrmState("crmContactState", "loading", "Loading governed contacts…");
  setEnabled("btnCrmMoreContacts", false);
  try {
    const query = new URLSearchParams({ limit: "50" });
    if (append && state.crmContactCursor) {
      query.set("cursor", state.crmContactCursor);
    }
    const payload = await api(
      "GET",
      `${TERMINAL_PATHS.crmContacts(customerId)}?${query}`,
    );
    const items = Array.isArray(payload?.data?.items) ? payload.data.items : [];
    const known = new Set(state.crmContacts.map((item) => item.id));
    state.crmContacts.push(...items.filter((item) => !known.has(item.id)));
    state.crmContactCursor = payload?.data?.next_cursor || null;
    renderCrmContacts();
    setCrmState(
      "crmContactState",
      state.crmContacts.length ? "ready" : "empty",
      state.crmContacts.length
        ? `${state.crmContacts.length} active contact record(s) loaded.`
        : "No active contacts are visible for this customer.",
    );
    setEnabled("btnCrmMoreContacts", Boolean(state.crmContactCursor));
    log("CRM contacts loaded", {
      customer_id: customerId,
      count: items.length,
      next_cursor: Boolean(state.crmContactCursor),
    });
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmContactState", kind, message);
  }
}

async function selectCrmContact(contactId) {
  const customerId = state.selectedCrmCustomerId;
  if (!customerId) {
    return;
  }
  state.selectedCrmContactId = contactId;
  state.selectedCrmContact = null;
  syncCrmWriteControls();
  renderCrmContacts();
  setCrmState("crmContactState", "loading", "Loading contact detail…");
  try {
    const payload = await api("GET", TERMINAL_PATHS.crmContact(customerId, contactId));
    const contact = payload?.data;
    state.selectedCrmContact = contact || null;
    setCrmDetail(
      "crmContactDetail",
      ["display_name", "title", "email", "phone", "status"],
      contact,
    );
    const updatedNode = $("crmContactDetail")?.querySelector('[data-field="updated_at"]');
    if (updatedNode) {
      updatedNode.textContent = formatCrmDate(contact?.updated_at);
    }
    $("crmContactDetailHeading").textContent = contact?.display_name || "Contact";
    syncCrmWriteControls();
    setCrmState("crmContactState", "ready", "Contact detail loaded.");
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmContactState", kind, message);
  }
}

function renderCrmOpportunities() {
  const host = $("crmOpportunityList");
  if (!host) {
    return;
  }
  host.replaceChildren();
  for (const opportunity of state.crmOpportunities) {
    const customer = state.crmCustomers.find(
      (item) => item.id === opportunity.customer_id,
    );
    host.appendChild(
      createCrmChoiceRow({
        id: opportunity.id,
        title: opportunity.title,
        meta: `${opportunity.code} · ${customer?.display_name || opportunity.customer_id} · ${opportunity.status}`,
        selected: opportunity.id === state.selectedCrmOpportunityId,
        onSelect: () => {
          selectCrmOpportunity(opportunity.id).catch((err) => {
            log("CRM opportunity selection failed", {
              message: String(err.message || err),
            });
          });
        },
      }),
    );
  }
  $("crmOpportunityCount").textContent = String(state.crmOpportunities.length);
}

async function loadCrmOpportunities({ append = false } = {}) {
  if (!append) {
    state.crmOpportunities = [];
    state.crmOpportunityCursor = null;
    state.selectedCrmOpportunityId = null;
    state.selectedCrmOpportunity = null;
    renderCrmOpportunities();
    setCrmDetail(
      "crmOpportunityDetail",
      ["code", "title", "customer_id", "status", "owner_subject_id", "updated_at"],
      null,
    );
    $("crmOpportunityDetailHeading").textContent = "Select an opportunity";
    syncCrmWriteControls();
  }
  setCrmState("crmOpportunityState", "loading", "Loading governed opportunities…");
  setEnabled("btnCrmRefreshOpportunities", false);
  setEnabled("btnCrmMoreOpportunities", false);
  try {
    const query = new URLSearchParams({ limit: "50" });
    if (append && state.crmOpportunityCursor) {
      query.set("cursor", state.crmOpportunityCursor);
    }
    const payload = await api(
      "GET",
      `${TERMINAL_PATHS.crmOpportunities}?${query}`,
    );
    const items = Array.isArray(payload?.data?.items) ? payload.data.items : [];
    const known = new Set(state.crmOpportunities.map((item) => item.id));
    state.crmOpportunities.push(...items.filter((item) => !known.has(item.id)));
    state.crmOpportunityCursor = payload?.data?.next_cursor || null;
    renderCrmOpportunities();
    syncCrmWriteControls();
    setCrmState(
      "crmOpportunityState",
      state.crmOpportunities.length ? "ready" : "empty",
      state.crmOpportunities.length
        ? `${state.crmOpportunities.length} active opportunity record(s) loaded.`
        : "No active opportunities are visible in this tenant.",
    );
    setEnabled(
      "btnCrmMoreOpportunities",
      Boolean(state.crmOpportunityCursor),
    );
    log("CRM opportunities loaded", {
      count: items.length,
      next_cursor: Boolean(state.crmOpportunityCursor),
    });
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmOpportunityState", kind, message);
  } finally {
    setEnabled("btnCrmRefreshOpportunities", true);
  }
}

async function selectCrmOpportunity(opportunityId) {
  state.selectedCrmOpportunityId = opportunityId;
  state.selectedCrmOpportunity = null;
  renderCrmOpportunities();
  syncCrmWriteControls();
  setCrmState("crmOpportunityState", "loading", "Loading opportunity detail…");
  try {
    const payload = await api(
      "GET",
      TERMINAL_PATHS.crmOpportunity(opportunityId),
    );
    const opportunity = payload?.data;
    state.selectedCrmOpportunity = opportunity || null;
    setCrmDetail(
      "crmOpportunityDetail",
      ["code", "title", "customer_id", "status", "owner_subject_id"],
      opportunity,
    );
    const updatedNode = $("crmOpportunityDetail")?.querySelector(
      '[data-field="updated_at"]',
    );
    if (updatedNode) {
      updatedNode.textContent = formatCrmDate(opportunity?.updated_at);
    }
    $("crmOpportunityDetailHeading").textContent =
      opportunity?.title || "Opportunity";
    setCrmState("crmOpportunityState", "ready", "Opportunity detail loaded.");
    syncCrmWriteControls();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmOpportunityState", kind, message);
  }
}

function renderCrmRequirements() {
  const host = $("crmRequirementList");
  if (!host) {
    return;
  }
  host.replaceChildren();
  for (const requirement of state.crmRequirements) {
    const opportunity = state.crmOpportunities.find(
      (item) => item.id === requirement.opportunity_id,
    );
    host.appendChild(
      createCrmChoiceRow({
        id: requirement.id,
        title: requirement.title,
        meta: `${requirement.code} · ${opportunity?.title || requirement.opportunity_id} · ${requirement.status}`,
        selected: requirement.id === state.selectedCrmRequirementId,
        onSelect: () => {
          selectCrmRequirement(requirement.id).catch((err) => {
            log("CRM requirement selection failed", {
              message: String(err.message || err),
            });
          });
        },
      }),
    );
  }
  $("crmRequirementCount").textContent = String(state.crmRequirements.length);
}

async function loadCrmRequirements({ append = false } = {}) {
  if (!append) {
    state.crmRequirements = [];
    state.crmRequirementCursor = null;
    state.selectedCrmRequirementId = null;
    state.selectedCrmRequirement = null;
    renderCrmRequirements();
    setCrmDetail(
      "crmRequirementDetail",
      ["code", "title", "opportunity_id", "description", "status", "updated_at"],
      null,
    );
    $("crmRequirementDetailHeading").textContent = "Select a requirement";
    syncCrmWriteControls();
  }
  setCrmState("crmRequirementState", "loading", "Loading governed requirements…");
  setEnabled("btnCrmRefreshRequirements", false);
  setEnabled("btnCrmMoreRequirements", false);
  try {
    const query = new URLSearchParams({ limit: "50" });
    if (append && state.crmRequirementCursor) {
      query.set("cursor", state.crmRequirementCursor);
    }
    const payload = await api(
      "GET",
      `${TERMINAL_PATHS.crmRequirements}?${query}`,
    );
    const items = Array.isArray(payload?.data?.items) ? payload.data.items : [];
    const known = new Set(state.crmRequirements.map((item) => item.id));
    state.crmRequirements.push(...items.filter((item) => !known.has(item.id)));
    state.crmRequirementCursor = payload?.data?.next_cursor || null;
    renderCrmRequirements();
    syncCrmWriteControls();
    setCrmState(
      "crmRequirementState",
      state.crmRequirements.length ? "ready" : "empty",
      state.crmRequirements.length
        ? `${state.crmRequirements.length} active requirement record(s) loaded.`
        : "No active requirements are visible in this tenant.",
    );
    setEnabled("btnCrmMoreRequirements", Boolean(state.crmRequirementCursor));
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmRequirementState", kind, message);
  } finally {
    setEnabled("btnCrmRefreshRequirements", true);
  }
}

async function selectCrmRequirement(requirementId) {
  state.selectedCrmRequirementId = requirementId;
  state.selectedCrmRequirement = null;
  renderCrmRequirements();
  syncCrmWriteControls();
  setCrmState("crmRequirementState", "loading", "Loading requirement detail…");
  try {
    const payload = await api(
      "GET",
      TERMINAL_PATHS.crmRequirement(requirementId),
    );
    const requirement = payload?.data;
    state.selectedCrmRequirement = requirement || null;
    setCrmDetail(
      "crmRequirementDetail",
      ["code", "title", "opportunity_id", "description", "status"],
      requirement,
    );
    const updatedNode = $("crmRequirementDetail")?.querySelector(
      '[data-field="updated_at"]',
    );
    if (updatedNode) {
      updatedNode.textContent = formatCrmDate(requirement?.updated_at);
    }
    $("crmRequirementDetailHeading").textContent =
      requirement?.title || "Requirement";
    setCrmState("crmRequirementState", "ready", "Requirement detail loaded.");
    syncCrmWriteControls();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmRequirementState", kind, message);
  }
}

function renderCrmQuotes() {
  const host = $("crmQuoteList");
  if (!host) return;
  host.replaceChildren();
  for (const quote of state.crmQuotes) {
    const requirement = state.crmRequirements.find(
      (item) => item.id === quote.requirement_id,
    );
    host.appendChild(
      createCrmChoiceRow({
        id: quote.id,
        title: quote.code,
        meta: `${quote.currency} · ${requirement?.title || quote.requirement_id} · ${quote.status}`,
        selected: quote.id === state.selectedCrmQuoteId,
        onSelect: () =>
          selectCrmQuote(quote.id).catch((err) =>
            log("CRM quote selection failed", { message: String(err.message || err) }),
          ),
      }),
    );
  }
  $("crmQuoteCount").textContent = String(state.crmQuotes.length);
}

async function loadCrmQuotes({ append = false } = {}) {
  if (!append) {
    state.crmQuotes = [];
    state.crmQuoteCursor = null;
    state.selectedCrmQuoteId = null;
    state.selectedCrmQuote = null;
    state.crmQuoteLines = [];
    state.selectedCrmQuoteLineId = null;
    state.selectedCrmQuoteLine = null;
    clearCrmConvertWorkspace();
    renderCrmQuotes();
    setCrmDetail(
      "crmQuoteDetail",
      ["code", "requirement_id", "currency", "notes", "status", "updated_at"],
      null,
    );
    $("crmQuoteDetailHeading").textContent = "Select a quote";
    renderCrmQuoteLines();
    setCrmDetail(
      "crmQuoteLineDetail",
      [
        "line_number",
        "description",
        "quantity",
        "unit_price",
        "amount",
        "status",
        "updated_at",
      ],
      null,
    );
    $("crmQuoteLineDetailHeading").textContent = "Select a line";
    setCrmState(
      "crmQuoteLineState",
      "idle",
      "Select a Quote Header to load its active lines.",
    );
    setEnabled("btnCrmRefreshQuoteLines", false);
    syncCrmWriteControls();
  }
  setCrmState("crmQuoteState", "loading", "Loading governed Quote headers…");
  setEnabled("btnCrmRefreshQuotes", false);
  setEnabled("btnCrmMoreQuotes", false);
  try {
    const query = new URLSearchParams({ limit: "50" });
    if (append && state.crmQuoteCursor) query.set("cursor", state.crmQuoteCursor);
    const payload = await api("GET", `${TERMINAL_PATHS.crmQuotes}?${query}`);
    const items = Array.isArray(payload?.data?.items) ? payload.data.items : [];
    const known = new Set(state.crmQuotes.map((item) => item.id));
    state.crmQuotes.push(...items.filter((item) => !known.has(item.id)));
    state.crmQuoteCursor = payload?.data?.next_cursor || null;
    renderCrmQuotes();
    setCrmState(
      "crmQuoteState",
      state.crmQuotes.length ? "ready" : "empty",
      state.crmQuotes.length
        ? `${state.crmQuotes.length} Quote header(s) loaded.`
        : "No non-archived Quotes are visible in this tenant.",
    );
    setEnabled("btnCrmMoreQuotes", Boolean(state.crmQuoteCursor));
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmQuoteState", kind, message);
  } finally {
    setEnabled("btnCrmRefreshQuotes", true);
  }
}

async function selectCrmQuote(quoteId) {
  state.selectedCrmQuoteId = quoteId;
  state.selectedCrmQuote = null;
  clearCrmConvertWorkspace();
  renderCrmQuotes();
  syncCrmWriteControls();
  setCrmState("crmQuoteState", "loading", "Loading Quote header detail…");
  try {
    const payload = await api("GET", TERMINAL_PATHS.crmQuote(quoteId));
    const quote = payload?.data;
    state.selectedCrmQuote = quote || null;
    setCrmDetail(
      "crmQuoteDetail",
      ["code", "requirement_id", "currency", "notes", "status"],
      quote,
    );
    const updated = $("crmQuoteDetail")?.querySelector('[data-field="updated_at"]');
    if (updated) updated.textContent = formatCrmDate(quote?.updated_at);
    $("crmQuoteDetailHeading").textContent = quote?.code || "Quote";
    setCrmState("crmQuoteState", "ready", "Quote header detail loaded.");
    if (quote?.status === "issued") {
      setCrmState(
        "crmConversionState",
        "idle",
        "Issued Quote ready. Convert to create a Conversion instruction.",
      );
    } else {
      setCrmState(
        "crmConversionState",
        "idle",
        "Only issued Quotes can be converted. Issue remains outside this surface.",
      );
    }
    syncCrmWriteControls();
    await loadCrmQuoteLines();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmQuoteState", kind, message);
  }
}

function clearCrmConvertWorkspace() {
  state.selectedCrmConversion = null;
  state.selectedCrmConvertSalesOrder = null;
  setCrmDetail(
    "crmConversionDetail",
    [
      "id",
      "quote_id",
      "quote_version",
      "currency",
      "functional_currency",
      "fx_rate",
      "functional_total",
      "status",
    ],
    null,
  );
  setCrmDetail(
    "crmConvertSoDetail",
    ["code", "id", "status", "total_amount", "currency"],
    null,
  );
  $("crmConvertSoHeading").textContent = "No sales order yet";
  setEnabled("btnCrmRefreshConversion", false);
  setCrmState(
    "crmConversionState",
    "idle",
    "Select an issued Quote and convert it to create a Conversion instruction.",
  );
  setCrmState(
    "crmConvertSoState",
    "idle",
    "Create a Sales Order shell from a ready Conversion. Confirmation remains G520.",
  );
}

function renderCrmConversion() {
  const conversion = state.selectedCrmConversion;
  setCrmDetail(
    "crmConversionDetail",
    [
      "id",
      "quote_id",
      "quote_version",
      "currency",
      "functional_currency",
      "fx_rate",
      "functional_total",
      "status",
    ],
    conversion,
  );
  setEnabled("btnCrmRefreshConversion", Boolean(conversion?.id));
  if (!conversion) {
    return;
  }
  setCrmState(
    "crmConversionState",
    "ready",
    conversion.status === "ready"
      ? "Conversion is ready for Sales Order shell creation."
      : `Conversion status: ${conversion.status}.`,
  );
}

function renderCrmConvertSalesOrder() {
  const salesOrder = state.selectedCrmConvertSalesOrder;
  setCrmDetail(
    "crmConvertSoDetail",
    ["code", "id", "status", "total_amount", "currency"],
    salesOrder,
  );
  $("crmConvertSoHeading").textContent = salesOrder?.code || "No sales order yet";
  if (!salesOrder) {
    setCrmState(
      "crmConvertSoState",
      "idle",
      "Create a Sales Order shell from a ready Conversion. Confirmation remains G520.",
    );
    return;
  }
  setCrmState(
    "crmConvertSoState",
    "ready",
    "Sales Order shell loaded. Confirmation remains outside this milestone.",
  );
}

async function loadCrmConversion() {
  const conversionId = state.selectedCrmConversion?.id;
  if (!conversionId) {
    setCrmState(
      "crmConversionState",
      "idle",
      "Select an issued Quote and convert it to create a Conversion instruction.",
    );
    return;
  }
  setCrmState("crmConversionState", "loading", "Loading Conversion…");
  try {
    const payload = await api("GET", TERMINAL_PATHS.crmConversion(conversionId));
    state.selectedCrmConversion = payload?.data || null;
    renderCrmConversion();
    syncCrmWriteControls();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmConversionState", kind, message);
  }
}

function renderCrmSalesOrders() {
  const host = $("crmSalesOrderList");
  if (!host) return;
  host.replaceChildren();
  for (const order of state.crmSalesOrders) {
    host.appendChild(
      createCrmChoiceRow({
        id: order.id,
        title: order.code,
        meta: `${order.currency} · ${order.total_amount} · ${order.status}`,
        selected: order.id === state.selectedCrmSalesOrderId,
        onSelect: () =>
          selectCrmSalesOrder(order.id).catch((err) =>
            log("CRM sales order selection failed", {
              message: String(err.message || err),
            }),
          ),
      }),
    );
  }
  $("crmSalesOrderCount").textContent = String(state.crmSalesOrders.length);
}

function clearCrmSalesOrderLines() {
  state.crmSalesOrderLines = [];
  state.selectedCrmSalesOrderLineId = null;
  state.selectedCrmSalesOrderLine = null;
  const host = $("crmSalesOrderLineList");
  if (host) host.replaceChildren();
  $("crmSalesOrderLineCount").textContent = "0";
  setCrmDetail(
    "crmSalesOrderLineDetail",
    ["line_number", "description", "quantity", "unit_price", "amount"],
    null,
  );
  $("crmSalesOrderLineDetailHeading").textContent = "Select a line";
  setCrmState(
    "crmSalesOrderLineState",
    "idle",
    "Select a Sales Order to load its lines.",
  );
}

async function loadCrmSalesOrders({ append = false } = {}) {
  if (!append) {
    state.crmSalesOrders = [];
    state.crmSalesOrderCursor = null;
    state.selectedCrmSalesOrderId = null;
    state.selectedCrmSalesOrder = null;
    renderCrmSalesOrders();
    setCrmDetail(
      "crmSalesOrderDetail",
      [
        "code",
        "quote_id",
        "conversion_id",
        "currency",
        "total_amount",
        "status",
        "created_at",
      ],
      null,
    );
    $("crmSalesOrderDetailHeading").textContent = "Select a sales order";
    clearCrmSalesOrderLines();
  }
  setCrmState("crmSalesOrderState", "loading", "Loading governed Sales Orders…");
  setEnabled("btnCrmRefreshSalesOrders", false);
  setEnabled("btnCrmMoreSalesOrders", false);
  try {
    const query = new URLSearchParams({ limit: "50" });
    if (append && state.crmSalesOrderCursor) {
      query.set("cursor", state.crmSalesOrderCursor);
    }
    const payload = await api(
      "GET",
      `${TERMINAL_PATHS.crmSalesOrders}?${query}`,
    );
    const items = Array.isArray(payload?.data?.items) ? payload.data.items : [];
    const known = new Set(state.crmSalesOrders.map((item) => item.id));
    state.crmSalesOrders.push(...items.filter((item) => !known.has(item.id)));
    state.crmSalesOrderCursor = payload?.data?.next_cursor || null;
    renderCrmSalesOrders();
    setCrmState(
      "crmSalesOrderState",
      state.crmSalesOrders.length ? "ready" : "empty",
      state.crmSalesOrders.length
        ? `${state.crmSalesOrders.length} Sales Order(s) loaded.`
        : "No Sales Orders are visible in this tenant.",
    );
    setEnabled("btnCrmMoreSalesOrders", Boolean(state.crmSalesOrderCursor));
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmSalesOrderState", kind, message);
  } finally {
    setEnabled("btnCrmRefreshSalesOrders", true);
  }
}

function clearCrmDeliveryOrder() {
  state.selectedCrmDeliveryOrder = null;
  setCrmDetail(
    "crmDeliveryOrderDetail",
    [
      "code",
      "sales_order_id",
      "currency",
      "total_amount",
      "status",
      "released_at",
    ],
    null,
  );
  if ($("crmDeliveryOrderDetailHeading")) {
    $("crmDeliveryOrderDetailHeading").textContent = "No delivery order yet";
  }
  setCrmState(
    "crmDeliveryOrderState",
    "idle",
    "Create a Delivery Order from a confirmed Sales Order. No tenant DO list is available.",
  );
  setEnabled("btnCrmRefreshDeliveryOrder", false);
  clearCrmArInvoice();
  clearCrmReturnAuthorization();
  syncCrmWriteControls();
}

function renderCrmDeliveryOrder() {
  const order = state.selectedCrmDeliveryOrder;
  setCrmDetail(
    "crmDeliveryOrderDetail",
    ["code", "sales_order_id", "currency", "total_amount", "status"],
    order,
  );
  const released = $("crmDeliveryOrderDetail")?.querySelector(
    '[data-field="released_at"]',
  );
  if (released) released.textContent = formatCrmDate(order?.released_at);
  if ($("crmDeliveryOrderDetailHeading")) {
    $("crmDeliveryOrderDetailHeading").textContent =
      order?.code || "Delivery Order";
  }
  setCrmState(
    "crmDeliveryOrderState",
    order ? "ready" : "idle",
    order
      ? "Delivery Order detail loaded. Invoice create available when permitted; RA create when shipped and permitted. Restock/Credit Note remain unavailable."
      : "Create a Delivery Order from a confirmed Sales Order. No tenant DO list is available.",
  );
  setEnabled("btnCrmRefreshDeliveryOrder", Boolean(order?.id));
  syncCrmWriteControls();
}

async function refreshCrmDeliveryOrder() {
  const orderId = state.selectedCrmDeliveryOrder?.id;
  if (!orderId) {
    clearCrmDeliveryOrder();
    return;
  }
  setCrmState(
    "crmDeliveryOrderState",
    "loading",
    "Refreshing governed Delivery Order…",
  );
  try {
    const payload = await api("GET", TERMINAL_PATHS.crmDeliveryOrder(orderId));
    state.selectedCrmDeliveryOrder = payload?.data || null;
    renderCrmDeliveryOrder();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmDeliveryOrderState", kind, message);
    syncCrmWriteControls();
  }
}

function clearCrmArInvoice() {
  state.selectedCrmArInvoice = null;
  setCrmDetail(
    "crmArInvoiceDetail",
    [
      "code",
      "delivery_order_id",
      "sales_order_id",
      "currency",
      "total_amount",
      "status",
      "issued_at",
      "voided_at",
      "void_reason",
    ],
    null,
  );
  const voided = $("crmArInvoiceDetail")?.querySelector(
    '[data-field="voided_at"]',
  );
  if (voided) voided.textContent = "—";
  const voidReason = $("crmArInvoiceDetail")?.querySelector(
    '[data-field="void_reason"]',
  );
  if (voidReason) voidReason.textContent = "—";
  if ($("crmArInvoiceDetailHeading")) {
    $("crmArInvoiceDetailHeading").textContent = "No AR invoice yet";
  }
  setCrmState(
    "crmArInvoiceState",
    "idle",
    "Create an AR Invoice from a released Delivery Order. No tenant Invoice list is available.",
  );
  setEnabled("btnCrmRefreshArInvoice", false);
  syncCrmWriteControls();
}

function renderCrmArInvoice() {
  const invoice = state.selectedCrmArInvoice;
  setCrmDetail(
    "crmArInvoiceDetail",
    [
      "code",
      "delivery_order_id",
      "sales_order_id",
      "currency",
      "total_amount",
      "status",
    ],
    invoice,
  );
  const issued = $("crmArInvoiceDetail")?.querySelector(
    '[data-field="issued_at"]',
  );
  if (issued) issued.textContent = formatCrmDate(invoice?.issued_at);
  const voided = $("crmArInvoiceDetail")?.querySelector(
    '[data-field="voided_at"]',
  );
  if (voided) voided.textContent = formatCrmDate(invoice?.voided_at);
  const voidReason = $("crmArInvoiceDetail")?.querySelector(
    '[data-field="void_reason"]',
  );
  if (voidReason) {
    voidReason.textContent = invoice?.void_reason || "—";
  }
  if ($("crmArInvoiceDetailHeading")) {
    $("crmArInvoiceDetailHeading").textContent = invoice?.code || "AR Invoice";
  }
  setCrmState(
    "crmArInvoiceState",
    invoice ? "ready" : "idle",
    invoice
      ? "AR Invoice detail loaded. Void available when issued and permitted. RA create when DO is shipped and permitted. Restock/Credit Note/Receipt remain unavailable."
      : "Create an AR Invoice from a released Delivery Order. No tenant Invoice list is available.",
  );
  setEnabled("btnCrmRefreshArInvoice", Boolean(invoice?.id));
  syncCrmWriteControls();
}

async function refreshCrmArInvoice() {
  const invoiceId = state.selectedCrmArInvoice?.id;
  if (!invoiceId) {
    clearCrmArInvoice();
    return;
  }
  setCrmState(
    "crmArInvoiceState",
    "loading",
    "Refreshing governed AR Invoice…",
  );
  try {
    const payload = await api("GET", TERMINAL_PATHS.crmArInvoice(invoiceId));
    state.selectedCrmArInvoice = payload?.data || null;
    renderCrmArInvoice();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmArInvoiceState", kind, message);
    syncCrmWriteControls();
  }
}

function clearCrmReturnAuthorization() {
  state.selectedCrmReturnAuthorization = null;
  setCrmDetail(
    "crmReturnAuthorizationDetail",
    [
      "code",
      "delivery_order_id",
      "invoice_id",
      "credit_note_id",
      "reason",
      "status",
    ],
    null,
  );
  const created = $("crmReturnAuthorizationDetail")?.querySelector(
    '[data-field="created_at"]',
  );
  if (created) created.textContent = "—";
  const restocked = $("crmReturnAuthorizationDetail")?.querySelector(
    '[data-field="restocked_at"]',
  );
  if (restocked) restocked.textContent = "—";
  if ($("crmReturnAuthorizationDetailHeading")) {
    $("crmReturnAuthorizationDetailHeading").textContent =
      "No return authorization yet";
  }
  setCrmState(
    "crmReturnAuthorizationState",
    "idle",
    "Create a Return Authorization from a shipped Delivery Order. No tenant RA list is available.",
  );
  setEnabled("btnCrmRefreshReturnAuthorization", false);
  syncCrmWriteControls();
}

function renderCrmReturnAuthorization() {
  const authorization = state.selectedCrmReturnAuthorization;
  setCrmDetail(
    "crmReturnAuthorizationDetail",
    [
      "code",
      "delivery_order_id",
      "invoice_id",
      "credit_note_id",
      "reason",
      "status",
    ],
    authorization,
  );
  const created = $("crmReturnAuthorizationDetail")?.querySelector(
    '[data-field="created_at"]',
  );
  if (created) {
    created.textContent = formatCrmDate(authorization?.created_at);
  }
  const restocked = $("crmReturnAuthorizationDetail")?.querySelector(
    '[data-field="restocked_at"]',
  );
  if (restocked) {
    restocked.textContent = formatCrmDate(authorization?.restocked_at);
  }
  if ($("crmReturnAuthorizationDetailHeading")) {
    $("crmReturnAuthorizationDetailHeading").textContent =
      authorization?.code || "Return Authorization";
  }
  setCrmState(
    "crmReturnAuthorizationState",
    authorization ? "ready" : "idle",
    authorization
      ? "Return Authorization detail loaded. Restock/Credit Note remain unavailable."
      : "Create a Return Authorization from a shipped Delivery Order. No tenant RA list is available.",
  );
  setEnabled("btnCrmRefreshReturnAuthorization", Boolean(authorization?.id));
  syncCrmWriteControls();
}

async function refreshCrmReturnAuthorization() {
  const authorizationId = state.selectedCrmReturnAuthorization?.id;
  if (!authorizationId) {
    clearCrmReturnAuthorization();
    return;
  }
  setCrmState(
    "crmReturnAuthorizationState",
    "loading",
    "Refreshing governed Return Authorization…",
  );
  try {
    const payload = await api(
      "GET",
      TERMINAL_PATHS.crmReturnAuthorization(authorizationId),
    );
    state.selectedCrmReturnAuthorization = payload?.data || null;
    renderCrmReturnAuthorization();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmReturnAuthorizationState", kind, message);
    syncCrmWriteControls();
  }
}

async function selectCrmSalesOrder(salesOrderId) {
  state.selectedCrmSalesOrderId = salesOrderId;
  state.selectedCrmSalesOrder = null;
  renderCrmSalesOrders();
  clearCrmSalesOrderLines();
  clearCrmDeliveryOrder();
  setCrmState("crmSalesOrderState", "loading", "Loading Sales Order detail…");
  try {
    const payload = await api("GET", TERMINAL_PATHS.crmSalesOrder(salesOrderId));
    const order = payload?.data;
    state.selectedCrmSalesOrder = order || null;
    setCrmDetail(
      "crmSalesOrderDetail",
      [
        "code",
        "quote_id",
        "conversion_id",
        "currency",
        "total_amount",
        "status",
      ],
      order,
    );
    const created = $("crmSalesOrderDetail")?.querySelector(
      '[data-field="created_at"]',
    );
    if (created) created.textContent = formatCrmDate(order?.created_at);
    $("crmSalesOrderDetailHeading").textContent = order?.code || "Sales Order";
    setCrmState("crmSalesOrderState", "ready", "Sales Order detail loaded.");
    syncCrmWriteControls();
    await loadCrmSalesOrderLines();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmSalesOrderState", kind, message);
    syncCrmWriteControls();
  }
}

function renderCrmSalesOrderLines() {
  const host = $("crmSalesOrderLineList");
  if (!host) return;
  host.replaceChildren();
  for (const line of state.crmSalesOrderLines) {
    host.appendChild(
      createCrmChoiceRow({
        id: line.id,
        title: `${line.line_number}. ${line.description}`,
        meta: `${line.quantity} × ${line.unit_price} = ${line.amount}`,
        selected: line.id === state.selectedCrmSalesOrderLineId,
        onSelect: () => selectCrmSalesOrderLine(line.id),
      }),
    );
  }
  $("crmSalesOrderLineCount").textContent = String(
    state.crmSalesOrderLines.length,
  );
}

async function loadCrmSalesOrderLines() {
  const salesOrderId = state.selectedCrmSalesOrderId;
  clearCrmSalesOrderLines();
  if (!salesOrderId) return;
  setCrmState(
    "crmSalesOrderLineState",
    "loading",
    "Loading governed Sales Order lines…",
  );
  try {
    const payload = await api(
      "GET",
      TERMINAL_PATHS.crmSalesOrderLines(salesOrderId),
    );
    state.crmSalesOrderLines = Array.isArray(payload?.data) ? payload.data : [];
    renderCrmSalesOrderLines();
    setCrmState(
      "crmSalesOrderLineState",
      state.crmSalesOrderLines.length ? "ready" : "empty",
      state.crmSalesOrderLines.length
        ? `${state.crmSalesOrderLines.length} line(s) loaded.`
        : "No Sales Order lines exist for the selected order.",
    );
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmSalesOrderLineState", kind, message);
  }
}

function selectCrmSalesOrderLine(lineId) {
  const line = state.crmSalesOrderLines.find((item) => item.id === lineId);
  if (!line) return;
  state.selectedCrmSalesOrderLineId = lineId;
  state.selectedCrmSalesOrderLine = line;
  renderCrmSalesOrderLines();
  setCrmDetail(
    "crmSalesOrderLineDetail",
    ["line_number", "description", "quantity", "unit_price", "amount"],
    line,
  );
  $("crmSalesOrderLineDetailHeading").textContent = `Line ${line.line_number}`;
  setCrmState(
    "crmSalesOrderLineState",
    "ready",
    "Sales Order line detail loaded.",
  );
}

function renderCrmQuoteLines() {
  const host = $("crmQuoteLineList");
  if (!host) return;
  host.replaceChildren();
  for (const line of state.crmQuoteLines) {
    host.appendChild(
      createCrmChoiceRow({
        id: line.id,
        title: `${line.line_number}. ${line.description}`,
        meta: `${line.quantity} × ${line.unit_price} = ${line.amount}`,
        selected: line.id === state.selectedCrmQuoteLineId,
        onSelect: () => selectCrmQuoteLine(line.id),
      }),
    );
  }
  $("crmQuoteLineCount").textContent = String(state.crmQuoteLines.length);
}

async function loadCrmQuoteLines() {
  state.crmQuoteLines = [];
  state.selectedCrmQuoteLineId = null;
  state.selectedCrmQuoteLine = null;
  renderCrmQuoteLines();
  setCrmDetail(
    "crmQuoteLineDetail",
    [
      "line_number",
      "description",
      "quantity",
      "unit_price",
      "amount",
      "status",
      "updated_at",
    ],
    null,
  );
  $("crmQuoteLineDetailHeading").textContent = "Select a line";
  syncCrmWriteControls();
  const quoteId = state.selectedCrmQuoteId;
  setEnabled("btnCrmRefreshQuoteLines", Boolean(quoteId));
  if (!quoteId) {
    setCrmState(
      "crmQuoteLineState",
      "idle",
      "Select a Quote Header to load its active lines.",
    );
    return;
  }
  setCrmState("crmQuoteLineState", "loading", "Loading governed Quote Lines…");
  try {
    const payload = await api("GET", TERMINAL_PATHS.crmQuoteLines(quoteId));
    state.crmQuoteLines = Array.isArray(payload?.data)
      ? payload.data.filter((line) => line.status === "active")
      : [];
    renderCrmQuoteLines();
    setCrmState(
      "crmQuoteLineState",
      state.crmQuoteLines.length ? "ready" : "empty",
      state.crmQuoteLines.length
        ? `${state.crmQuoteLines.length} active line(s) loaded.`
        : "No active Quote Lines exist for the selected Quote.",
    );
    syncCrmWriteControls();
  } catch (err) {
    const [kind, message] = crmErrorState(err);
    setCrmState("crmQuoteLineState", kind, message);
  }
}

function selectCrmQuoteLine(lineId) {
  const line = state.crmQuoteLines.find((item) => item.id === lineId);
  if (!line) return;
  state.selectedCrmQuoteLineId = lineId;
  state.selectedCrmQuoteLine = line;
  renderCrmQuoteLines();
  setCrmDetail(
    "crmQuoteLineDetail",
    [
      "line_number",
      "description",
      "quantity",
      "unit_price",
      "amount",
      "status",
    ],
    line,
  );
  const updated = $("crmQuoteLineDetail")?.querySelector('[data-field="updated_at"]');
  if (updated) updated.textContent = formatCrmDate(line.updated_at);
  $("crmQuoteLineDetailHeading").textContent = `Line ${line.line_number}`;
  setCrmState("crmQuoteLineState", "ready", "Quote Line detail loaded.");
  syncCrmWriteControls();
}

function closeCrmEditors() {
  $("crmCustomerEditor").hidden = true;
  $("crmContactEditor").hidden = true;
  $("crmOpportunityEditor").hidden = true;
  $("crmRequirementEditor").hidden = true;
  $("crmQuoteEditor").hidden = true;
  $("crmQuoteLineEditor").hidden = true;
  $("crmIssueQuoteEditor").hidden = true;
  $("crmConvertEditor").hidden = true;
  $("crmCreateSoEditor").hidden = true;
  $("crmConfirmSoEditor").hidden = true;
  $("crmCreateDoEditor").hidden = true;
  $("crmReleaseDoEditor").hidden = true;
  $("crmCreateArInvoiceEditor").hidden = true;
  $("crmIssueArInvoiceEditor").hidden = true;
  $("crmVoidArInvoiceEditor").hidden = true;
  $("crmCreateReturnAuthorizationEditor").hidden = true;
  $("crmArchiveEditor").hidden = true;
  state.crmArchiveTarget = null;
}

function setCrmFormState(id, kind, message) {
  const node = $(id);
  node.dataset.state = kind;
  node.textContent = message;
}

function crmWriteErrorMessage(err) {
  if (err?.status === 403) {
    return "Permission denied. No change was made.";
  }
  if (err?.status === 404) {
    return "Record not found in this tenant. The view will be refreshed.";
  }
  if (err?.status === 409) {
    return "Version conflict. The latest record will be refreshed; no overwrite was attempted.";
  }
  if (err?.status === 422) {
    return "The server rejected one or more fields. Review the form and try again.";
  }
  return "The write failed. No automatic retry was attempted.";
}

function optionalCrmText(id) {
  const value = $(id).value.trim();
  return value || null;
}

function openCrmCustomerEditor(mode) {
  const customer = state.selectedCrmCustomer;
  if (
    (mode === "create" && !crmCan("pkg.crm.customer", "create")) ||
    (mode === "edit" &&
      (!customer || !crmCan("pkg.crm.customer", "update", customer.id)))
  ) {
    return;
  }
  closeCrmEditors();
  $("crmCustomerMode").value = mode;
  $("crmCustomerEditorHeading").textContent =
    mode === "create" ? "Create customer" : "Edit customer";
  $("crmCustomerCode").disabled = mode === "edit";
  $("crmCustomerCode").value = mode === "edit" ? customer.code || "" : "";
  $("crmCustomerName").value = mode === "edit" ? customer.display_name || "" : "";
  $("crmCustomerOwner").value =
    mode === "edit" ? customer.owner_subject_id || "" : "";
  setCrmFormState(
    "crmCustomerFormState",
    "idle",
    "Tenant and actor context are supplied by the trusted session.",
  );
  $("crmCustomerEditor").hidden = false;
  $("crmCustomerName").focus();
}

function openCrmContactEditor(mode) {
  const customerId = state.selectedCrmCustomerId;
  const contact = state.selectedCrmContact;
  if (
    !customerId ||
    (mode === "create" && !crmCan("pkg.crm.contact", "create")) ||
    (mode === "edit" &&
      (!contact || !crmCan("pkg.crm.contact", "update", contact.id)))
  ) {
    return;
  }
  closeCrmEditors();
  $("crmContactMode").value = mode;
  $("crmContactEditorHeading").textContent =
    mode === "create" ? "Create contact" : "Edit contact";
  $("crmContactName").value = mode === "edit" ? contact.display_name || "" : "";
  $("crmContactTitle").value = mode === "edit" ? contact.title || "" : "";
  $("crmContactEmail").value = mode === "edit" ? contact.email || "" : "";
  $("crmContactPhone").value = mode === "edit" ? contact.phone || "" : "";
  setCrmFormState(
    "crmContactFormState",
    "idle",
    "Email and phone are optional and are never inferred.",
  );
  $("crmContactEditor").hidden = false;
  $("crmContactName").focus();
}

function openCrmOpportunityEditor(mode) {
  const opportunity = state.selectedCrmOpportunity;
  if (
    (mode === "create" &&
      (!state.crmCustomers.length ||
        !crmCan("pkg.crm.opportunity", "create"))) ||
    (mode === "edit" &&
      (!opportunity ||
        !crmCan("pkg.crm.opportunity", "update", opportunity.id)))
  ) {
    return;
  }
  closeCrmEditors();
  $("crmOpportunityMode").value = mode;
  $("crmOpportunityEditorHeading").textContent =
    mode === "create" ? "Create opportunity" : "Edit opportunity";
  const customerSelect = $("crmOpportunityCustomer");
  customerSelect.replaceChildren();
  for (const customer of state.crmCustomers) {
    const option = document.createElement("option");
    option.value = customer.id;
    option.textContent = `${customer.code} · ${customer.display_name}`;
    customerSelect.appendChild(option);
  }
  if (
    mode === "edit" &&
    !state.crmCustomers.some((item) => item.id === opportunity.customer_id)
  ) {
    const option = document.createElement("option");
    option.value = opportunity.customer_id;
    option.textContent = opportunity.customer_id;
    customerSelect.appendChild(option);
  }
  customerSelect.value =
    mode === "edit" ? opportunity.customer_id : state.crmCustomers[0].id;
  customerSelect.disabled = mode === "edit";
  $("crmOpportunityTitle").value =
    mode === "edit" ? opportunity.title || "" : "";
  $("crmOpportunityOwner").value =
    mode === "edit" ? opportunity.owner_subject_id || "" : "";
  setCrmFormState(
    "crmOpportunityFormState",
    "idle",
    "Customer choices come only from the governed Customer collection.",
  );
  $("crmOpportunityEditor").hidden = false;
  $("crmOpportunityTitle").focus();
}

function openCrmRequirementEditor(mode) {
  const requirement = state.selectedCrmRequirement;
  if (
    (mode === "create" &&
      (!state.crmOpportunities.length ||
        !crmCan("pkg.crm.requirement", "create"))) ||
    (mode === "edit" &&
      (!requirement ||
        !crmCan("pkg.crm.requirement", "update", requirement.id)))
  ) {
    return;
  }
  closeCrmEditors();
  $("crmRequirementMode").value = mode;
  $("crmRequirementEditorHeading").textContent =
    mode === "create" ? "Create requirement" : "Edit requirement";
  const opportunitySelect = $("crmRequirementOpportunity");
  opportunitySelect.replaceChildren();
  for (const opportunity of state.crmOpportunities) {
    const option = document.createElement("option");
    option.value = opportunity.id;
    option.textContent = `${opportunity.code} · ${opportunity.title}`;
    opportunitySelect.appendChild(option);
  }
  if (
    mode === "edit" &&
    !state.crmOpportunities.some(
      (item) => item.id === requirement.opportunity_id,
    )
  ) {
    const option = document.createElement("option");
    option.value = requirement.opportunity_id;
    option.textContent = requirement.opportunity_id;
    opportunitySelect.appendChild(option);
  }
  opportunitySelect.value =
    mode === "edit"
      ? requirement.opportunity_id
      : state.crmOpportunities[0].id;
  opportunitySelect.disabled = mode === "edit";
  $("crmRequirementTitle").value =
    mode === "edit" ? requirement.title || "" : "";
  $("crmRequirementDescription").value =
    mode === "edit" ? requirement.description || "" : "";
  setCrmFormState(
    "crmRequirementFormState",
    "idle",
    "Opportunity choices come only from the governed collection.",
  );
  $("crmRequirementEditor").hidden = false;
  $("crmRequirementTitle").focus();
}

function openCrmQuoteEditor(mode) {
  const quote = state.selectedCrmQuote;
  if (
    (mode === "create" &&
      (!state.crmRequirements.length || !crmCan("pkg.crm.quote", "create"))) ||
    (mode === "edit" &&
      (!quote || !crmCan("pkg.crm.quote", "update", quote.id)))
  ) {
    return;
  }
  closeCrmEditors();
  $("crmQuoteMode").value = mode;
  $("crmQuoteEditorHeading").textContent =
    mode === "create" ? "Create Quote header" : "Edit Quote header";
  const requirementSelect = $("crmQuoteRequirement");
  requirementSelect.replaceChildren();
  for (const requirement of state.crmRequirements) {
    const option = document.createElement("option");
    option.value = requirement.id;
    option.textContent = `${requirement.code} · ${requirement.title}`;
    requirementSelect.appendChild(option);
  }
  if (
    mode === "edit" &&
    !state.crmRequirements.some((item) => item.id === quote.requirement_id)
  ) {
    const option = document.createElement("option");
    option.value = quote.requirement_id;
    option.textContent = quote.requirement_id;
    requirementSelect.appendChild(option);
  }
  requirementSelect.value =
    mode === "edit" ? quote.requirement_id : state.crmRequirements[0].id;
  requirementSelect.disabled = mode === "edit";
  $("crmQuoteCurrency").value = mode === "edit" ? quote.currency : "USD";
  $("crmQuoteNotes").value = mode === "edit" ? quote.notes || "" : "";
  setCrmFormState(
    "crmQuoteFormState",
    "idle",
    "Quote Lines, Issue, and Convert remain outside this form.",
  );
  $("crmQuoteEditor").hidden = false;
  $("crmQuoteCurrency").focus();
}

function openCrmQuoteLineEditor(mode) {
  const quoteId = state.selectedCrmQuoteId;
  const line = state.selectedCrmQuoteLine;
  if (
    (mode === "create" &&
      (!quoteId || !crmCan("pkg.crm.quote_line", "create", quoteId))) ||
    (mode === "edit" &&
      (!line || !crmCan("pkg.crm.quote_line", "update", line.id)))
  ) {
    return;
  }
  closeCrmEditors();
  $("crmQuoteLineMode").value = mode;
  $("crmQuoteLineEditorHeading").textContent =
    mode === "create" ? "Create Quote Line" : `Edit line ${line.line_number}`;
  $("crmQuoteLineDescription").value = mode === "edit" ? line.description : "";
  $("crmQuoteLineQuantity").value = mode === "edit" ? line.quantity : "1.000";
  $("crmQuoteLineUnitPrice").value =
    mode === "edit" ? line.unit_price : "0.00";
  setCrmFormState(
    "crmQuoteLineFormState",
    "idle",
    "Amount is calculated by the server; Issue and Convert remain unavailable.",
  );
  $("crmQuoteLineEditor").hidden = false;
  $("crmQuoteLineDescription").focus();
}

function openCrmIssueQuoteEditor() {
  const quote = state.selectedCrmQuote;
  if (
    !quote ||
    quote.status !== "draft" ||
    !crmCan("pkg.crm.quote", "issue", quote.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmIssueQuoteApprovalRef").value = "";
  $("crmIssueQuoteConfirmed").checked = false;
  $("crmIssueQuoteEditorHeading").textContent =
    `Issue Quote ${quote.code || quote.id}`;
  setCrmFormState(
    "crmIssueQuoteFormState",
    "idle",
    "Idempotency is generated per submission. Convert remains a separate action.",
  );
  $("crmIssueQuoteEditor").hidden = false;
  $("crmIssueQuoteConfirmed").focus();
}

function openCrmConvertEditor() {
  const quote = state.selectedCrmQuote;
  if (
    !quote ||
    quote.status !== "issued" ||
    !crmCan("pkg.crm.quote_conversion", "convert", quote.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmConvertEditorHeading").textContent = `Convert ${quote.code}`;
  $("crmConvertFunctionalCurrency").value = "";
  $("crmConvertFxRate").value = "";
  $("crmConvertApprovalRef").value = "";
  $("crmConvertConfirmed").checked = false;
  setCrmFormState(
    "crmConvertFormState",
    "idle",
    "Idempotency is generated per submission. Delivery and Invoice remain unavailable here.",
  );
  $("crmConvertEditor").hidden = false;
  $("crmConvertConfirmed").focus();
}

function openCrmCreateSoEditor() {
  const conversion = state.selectedCrmConversion;
  if (
    !conversion ||
    conversion.status !== "ready" ||
    state.selectedCrmConvertSalesOrder ||
    !crmCan("pkg.crm.sales_order", "create", conversion.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmCreateSoConfirmed").checked = false;
  setCrmFormState(
    "crmCreateSoFormState",
    "idle",
    "Creates a Sales Order shell only. Confirm remains a separate action.",
  );
  $("crmCreateSoEditor").hidden = false;
  $("crmCreateSoConfirmed").focus();
}

function openCrmConfirmSalesOrderEditor() {
  const order = state.selectedCrmSalesOrder;
  if (
    !order ||
    order.status !== "created" ||
    !crmCan("pkg.crm.sales_order", "confirm", order.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmConfirmSoApprovalRef").value = "";
  $("crmConfirmSoConfirmed").checked = false;
  $("crmConfirmSoEditorHeading").textContent =
    `Confirm Sales Order ${order.code || order.id}`;
  setCrmFormState(
    "crmConfirmSoFormState",
    "idle",
    "Idempotency is generated per submission. Delivery Order remains a separate action.",
  );
  $("crmConfirmSoEditor").hidden = false;
  $("crmConfirmSoConfirmed").focus();
}

function openCrmCreateDeliveryOrderEditor() {
  const order = state.selectedCrmSalesOrder;
  if (
    !order ||
    (order.status !== "confirmed" && order.status !== "partially_shipped") ||
    !crmCan("pkg.crm.delivery_order", "create", order.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmCreateDoConfirmed").checked = false;
  setCrmFormState(
    "crmCreateDoFormState",
    "idle",
    "Creates a Delivery Order shell from remaining SO quantity. Release remains separate.",
  );
  $("crmCreateDoEditor").hidden = false;
  $("crmCreateDoConfirmed").focus();
}

function openCrmReleaseDeliveryOrderEditor() {
  const deliveryOrder = state.selectedCrmDeliveryOrder;
  if (
    !deliveryOrder ||
    deliveryOrder.status !== "draft" ||
    !crmCan("pkg.crm.delivery_order", "release", deliveryOrder.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmReleaseDoApprovalRef").value = "";
  $("crmReleaseDoConfirmed").checked = false;
  $("crmReleaseDoEditorHeading").textContent =
    `Release Delivery Order ${deliveryOrder.code || deliveryOrder.id}`;
  setCrmFormState(
    "crmReleaseDoFormState",
    "idle",
    "Idempotency is generated per submission. Invoice create available when permitted; RA create when shipped and permitted. Restock/Credit Note remain unavailable.",
  );
  $("crmReleaseDoEditor").hidden = false;
  $("crmReleaseDoConfirmed").focus();
}

function openCrmCreateArInvoiceEditor() {
  const deliveryOrder = state.selectedCrmDeliveryOrder;
  if (
    !deliveryOrder ||
    deliveryOrder.status !== "released" ||
    !crmCan("pkg.crm.ar_invoice", "create", deliveryOrder.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmCreateArInvoiceConfirmed").checked = false;
  setCrmFormState(
    "crmCreateArInvoiceFormState",
    "idle",
    "Creates an AR Invoice shell from the released Delivery Order. Issue remains separate.",
  );
  $("crmCreateArInvoiceEditor").hidden = false;
  $("crmCreateArInvoiceConfirmed").focus();
}

function openCrmIssueArInvoiceEditor() {
  const invoice = state.selectedCrmArInvoice;
  if (
    !invoice ||
    invoice.status !== "draft" ||
    !crmCan("pkg.crm.ar_invoice", "issue", invoice.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmIssueArInvoiceConfirmed").checked = false;
  $("crmIssueArInvoiceEditorHeading").textContent =
    `Issue AR Invoice ${invoice.code || invoice.id}`;
  setCrmFormState(
    "crmIssueArInvoiceFormState",
    "idle",
    "Idempotency is generated per submission. Void available when issued and permitted. RA create when DO is shipped and permitted. Restock/Credit Note/Receipt remain unavailable.",
  );
  $("crmIssueArInvoiceEditor").hidden = false;
  $("crmIssueArInvoiceConfirmed").focus();
}

function openCrmVoidArInvoiceEditor() {
  const invoice = state.selectedCrmArInvoice;
  if (
    !invoice ||
    invoice.status !== "issued" ||
    !crmCan("pkg.crm.ar_invoice", "void", invoice.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmVoidArInvoiceReason").value = "";
  $("crmVoidArInvoiceConfirmed").checked = false;
  $("crmVoidArInvoiceEditorHeading").textContent =
    `Void AR Invoice ${invoice.code || invoice.id}`;
  setCrmFormState(
    "crmVoidArInvoiceFormState",
    "idle",
    "Reason is required (1–500 characters). Idempotency is generated per submission. Restock/Credit Note/Receipt remain unavailable.",
  );
  $("crmVoidArInvoiceEditor").hidden = false;
  $("crmVoidArInvoiceReason").focus();
}

function openCrmCreateReturnAuthorizationEditor() {
  const deliveryOrder = state.selectedCrmDeliveryOrder;
  if (
    !deliveryOrder ||
    deliveryOrder.status !== "shipped" ||
    !crmCan("pkg.crm.return_authorization", "create", deliveryOrder.id)
  ) {
    return;
  }
  closeCrmEditors();
  $("crmCreateReturnAuthorizationReason").value = "";
  $("crmCreateReturnAuthorizationConfirmed").checked = false;
  const invoice = state.selectedCrmArInvoice;
  const invoiceNote =
    invoice &&
    (invoice.status === "issued" || invoice.status === "voided")
      ? "An issued or voided AR Invoice is selected; invoice_id will be attached automatically."
      : "No issued or voided AR Invoice selected; invoice_id will be omitted.";
  setCrmFormState(
    "crmCreateReturnAuthorizationFormState",
    "idle",
    invoiceNote,
  );
  $("crmCreateReturnAuthorizationEditor").hidden = false;
  $("crmCreateReturnAuthorizationReason").focus();
}

function openCrmArchiveEditor(kind) {
  const records = {
    customer: state.selectedCrmCustomer,
    contact: state.selectedCrmContact,
    opportunity: state.selectedCrmOpportunity,
    requirement: state.selectedCrmRequirement,
    quote: state.selectedCrmQuote,
    quoteLine: state.selectedCrmQuoteLine,
  };
  const resourceTypes = {
    customer: "pkg.crm.customer",
    contact: "pkg.crm.contact",
    opportunity: "pkg.crm.opportunity",
    requirement: "pkg.crm.requirement",
    quote: "pkg.crm.quote",
    quoteLine: "pkg.crm.quote_line",
  };
  const record = records[kind];
  const resourceType = resourceTypes[kind];
  if (!record || !crmCan(resourceType, "archive", record.id)) {
    return;
  }
  closeCrmEditors();
  state.crmArchiveTarget = {
    kind,
    id: record.id,
    version: record.version,
    customerId: state.selectedCrmCustomerId,
    quoteId: state.selectedCrmQuoteId,
  };
  $("crmArchiveHeading").textContent =
    `Archive ${kind}: ${record.display_name || record.code || record.description || record.id}`;
  $("crmArchiveReason").value = "";
  $("crmArchiveConfirmed").checked = false;
  setCrmFormState(
    "crmArchiveFormState",
    "idle",
    "Submission remains subject to server Permission and version checks.",
  );
  $("crmArchiveEditor").hidden = false;
  $("crmArchiveReason").focus();
}

async function submitCrmCustomer(event) {
  event.preventDefault();
  const mode = $("crmCustomerMode").value;
  const selected = state.selectedCrmCustomer;
  if (
    (mode === "create" && !crmCan("pkg.crm.customer", "create")) ||
    (mode === "edit" &&
      (!selected || !crmCan("pkg.crm.customer", "update", selected.id)))
  ) {
    setCrmFormState("crmCustomerFormState", "denied", "Write permission is unavailable.");
    return;
  }
  const body = {
    display_name: $("crmCustomerName").value.trim(),
    owner_subject_id: optionalCrmText("crmCustomerOwner"),
  };
  let path = TERMINAL_PATHS.crmCustomers;
  let method = "POST";
  if (mode === "create") {
    body.code = $("crmCustomerCode").value.trim();
  } else {
    path = TERMINAL_PATHS.crmCustomer(selected.id);
    method = "PATCH";
    body.expected_version = selected.version;
  }
  setEnabled("btnCrmSubmitCustomer", false);
  setCrmFormState("crmCustomerFormState", "loading", "Saving governed customer…");
  try {
    const payload = await api(method, path, body);
    const savedId = payload?.data?.id;
    closeCrmEditors();
    await loadCrmCustomers();
    if (savedId) {
      await selectCrmCustomer(savedId);
    }
    log(`CRM customer ${mode === "create" ? "created" : "updated"}`, {
      customer_id: savedId,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState("crmCustomerFormState", "error", crmWriteErrorMessage(err));
    if (err?.status === 404 || err?.status === 409) {
      const selectedId = selected?.id;
      closeCrmEditors();
      await loadCrmCustomers();
      if (selectedId && err.status === 409) {
        await selectCrmCustomer(selectedId).catch(() => {});
      }
    }
  } finally {
    setEnabled("btnCrmSubmitCustomer", true);
  }
}

async function submitCrmContact(event) {
  event.preventDefault();
  const mode = $("crmContactMode").value;
  const customerId = state.selectedCrmCustomerId;
  const selected = state.selectedCrmContact;
  if (
    !customerId ||
    (mode === "create" && !crmCan("pkg.crm.contact", "create")) ||
    (mode === "edit" &&
      (!selected || !crmCan("pkg.crm.contact", "update", selected.id)))
  ) {
    setCrmFormState("crmContactFormState", "denied", "Write permission is unavailable.");
    return;
  }
  const body = {
    display_name: $("crmContactName").value.trim(),
    title: optionalCrmText("crmContactTitle"),
    email: optionalCrmText("crmContactEmail"),
    phone: optionalCrmText("crmContactPhone"),
  };
  let path = TERMINAL_PATHS.crmContacts(customerId);
  let method = "POST";
  if (mode === "edit") {
    path = TERMINAL_PATHS.crmContact(customerId, selected.id);
    method = "PATCH";
    body.expected_version = selected.version;
  }
  setEnabled("btnCrmSubmitContact", false);
  setCrmFormState("crmContactFormState", "loading", "Saving governed contact…");
  try {
    const payload = await api(method, path, body);
    const savedId = payload?.data?.id;
    closeCrmEditors();
    await loadCrmContacts();
    if (savedId) {
      await selectCrmContact(savedId);
    }
    log(`CRM contact ${mode === "create" ? "created" : "updated"}`, {
      customer_id: customerId,
      contact_id: savedId,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState("crmContactFormState", "error", crmWriteErrorMessage(err));
    if (err?.status === 404 || err?.status === 409) {
      const selectedId = selected?.id;
      closeCrmEditors();
      await loadCrmContacts();
      if (selectedId && err.status === 409) {
        await selectCrmContact(selectedId).catch(() => {});
      }
    }
  } finally {
    setEnabled("btnCrmSubmitContact", true);
  }
}

async function submitCrmOpportunity(event) {
  event.preventDefault();
  const mode = $("crmOpportunityMode").value;
  const selected = state.selectedCrmOpportunity;
  if (
    (mode === "create" && !crmCan("pkg.crm.opportunity", "create")) ||
    (mode === "edit" &&
      (!selected ||
        !crmCan("pkg.crm.opportunity", "update", selected.id)))
  ) {
    setCrmFormState(
      "crmOpportunityFormState",
      "denied",
      "Write permission is unavailable.",
    );
    return;
  }
  const body = {
    title: $("crmOpportunityTitle").value.trim(),
    owner_subject_id: optionalCrmText("crmOpportunityOwner"),
  };
  let path = TERMINAL_PATHS.crmOpportunities;
  let method = "POST";
  if (mode === "create") {
    body.customer_id = $("crmOpportunityCustomer").value;
  } else {
    path = TERMINAL_PATHS.crmOpportunity(selected.id);
    method = "PATCH";
    body.expected_version = selected.version;
  }
  setEnabled("btnCrmSubmitOpportunity", false);
  setCrmFormState(
    "crmOpportunityFormState",
    "loading",
    "Saving governed opportunity…",
  );
  try {
    const payload = await api(method, path, body);
    const savedId = payload?.data?.id;
    closeCrmEditors();
    await loadCrmOpportunities();
    if (savedId) {
      await selectCrmOpportunity(savedId);
    }
    log(`CRM opportunity ${mode === "create" ? "created" : "updated"}`, {
      opportunity_id: savedId,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmOpportunityFormState",
      "error",
      crmWriteErrorMessage(err),
    );
    if (err?.status === 404 || err?.status === 409) {
      const selectedId = selected?.id;
      closeCrmEditors();
      await loadCrmOpportunities();
      if (selectedId && err.status === 409) {
        await selectCrmOpportunity(selectedId).catch(() => {});
      }
    }
  } finally {
    setEnabled("btnCrmSubmitOpportunity", true);
  }
}

async function submitCrmRequirement(event) {
  event.preventDefault();
  const mode = $("crmRequirementMode").value;
  const selected = state.selectedCrmRequirement;
  if (
    (mode === "create" && !crmCan("pkg.crm.requirement", "create")) ||
    (mode === "edit" &&
      (!selected || !crmCan("pkg.crm.requirement", "update", selected.id)))
  ) {
    setCrmFormState(
      "crmRequirementFormState",
      "denied",
      "Write permission is unavailable.",
    );
    return;
  }
  const body = {
    title: $("crmRequirementTitle").value.trim(),
    description: optionalCrmText("crmRequirementDescription"),
  };
  let path = TERMINAL_PATHS.crmRequirements;
  let method = "POST";
  if (mode === "create") {
    body.opportunity_id = $("crmRequirementOpportunity").value;
  } else {
    path = TERMINAL_PATHS.crmRequirement(selected.id);
    method = "PATCH";
    body.expected_version = selected.version;
  }
  setEnabled("btnCrmSubmitRequirement", false);
  setCrmFormState(
    "crmRequirementFormState",
    "loading",
    "Saving governed requirement…",
  );
  try {
    const payload = await api(method, path, body);
    const savedId = payload?.data?.id;
    closeCrmEditors();
    await loadCrmRequirements();
    if (savedId) {
      await selectCrmRequirement(savedId);
    }
    log(`CRM requirement ${mode === "create" ? "created" : "updated"}`, {
      requirement_id: savedId,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmRequirementFormState",
      "error",
      crmWriteErrorMessage(err),
    );
    if (err?.status === 404 || err?.status === 409) {
      const selectedId = selected?.id;
      closeCrmEditors();
      await loadCrmRequirements();
      if (selectedId && err.status === 409) {
        await selectCrmRequirement(selectedId).catch(() => {});
      }
    }
  } finally {
    setEnabled("btnCrmSubmitRequirement", true);
  }
}

async function submitCrmQuote(event) {
  event.preventDefault();
  const mode = $("crmQuoteMode").value;
  const selected = state.selectedCrmQuote;
  if (
    (mode === "create" && !crmCan("pkg.crm.quote", "create")) ||
    (mode === "edit" &&
      (!selected || !crmCan("pkg.crm.quote", "update", selected.id)))
  ) {
    setCrmFormState("crmQuoteFormState", "denied", "Write permission is unavailable.");
    return;
  }
  const body = {
    currency: $("crmQuoteCurrency").value.trim().toUpperCase(),
    notes: optionalCrmText("crmQuoteNotes"),
  };
  let path = TERMINAL_PATHS.crmQuotes;
  let method = "POST";
  if (mode === "create") {
    body.requirement_id = $("crmQuoteRequirement").value;
  } else {
    path = TERMINAL_PATHS.crmQuote(selected.id);
    method = "PATCH";
    body.expected_version = selected.version;
  }
  setEnabled("btnCrmSubmitQuote", false);
  setCrmFormState("crmQuoteFormState", "loading", "Saving governed Quote header…");
  try {
    const payload = await api(method, path, body);
    const savedId = payload?.data?.id;
    closeCrmEditors();
    await loadCrmQuotes();
    if (savedId) await selectCrmQuote(savedId);
    log(`CRM Quote header ${mode === "create" ? "created" : "updated"}`, {
      quote_id: savedId,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState("crmQuoteFormState", "error", crmWriteErrorMessage(err));
    if (err?.status === 404 || err?.status === 409) {
      const selectedId = selected?.id;
      closeCrmEditors();
      await loadCrmQuotes();
      if (selectedId && err.status === 409) {
        await selectCrmQuote(selectedId).catch(() => {});
      }
    }
  } finally {
    setEnabled("btnCrmSubmitQuote", true);
  }
}

async function submitCrmQuoteLine(event) {
  event.preventDefault();
  const mode = $("crmQuoteLineMode").value;
  const quoteId = state.selectedCrmQuoteId;
  const selected = state.selectedCrmQuoteLine;
  if (
    (mode === "create" &&
      (!quoteId || !crmCan("pkg.crm.quote_line", "create", quoteId))) ||
    (mode === "edit" &&
      (!selected || !crmCan("pkg.crm.quote_line", "update", selected.id)))
  ) {
    setCrmFormState(
      "crmQuoteLineFormState",
      "denied",
      "Write permission is unavailable.",
    );
    return;
  }
  const body = {
    description: $("crmQuoteLineDescription").value.trim(),
    quantity: $("crmQuoteLineQuantity").value,
    unit_price: $("crmQuoteLineUnitPrice").value,
  };
  let path = TERMINAL_PATHS.crmQuoteLines(quoteId);
  let method = "POST";
  if (mode === "edit") {
    path = TERMINAL_PATHS.crmQuoteLine(quoteId, selected.id);
    method = "PATCH";
    body.expected_version = selected.version;
  }
  setEnabled("btnCrmSubmitQuoteLine", false);
  setCrmFormState(
    "crmQuoteLineFormState",
    "loading",
    "Saving governed Quote Line…",
  );
  try {
    const payload = await api(method, path, body);
    const savedId = payload?.data?.id;
    closeCrmEditors();
    await loadCrmQuoteLines();
    if (savedId) selectCrmQuoteLine(savedId);
    log(`CRM Quote Line ${mode === "create" ? "created" : "updated"}`, {
      quote_id: quoteId,
      quote_line_id: savedId,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmQuoteLineFormState",
      "error",
      crmWriteErrorMessage(err),
    );
    if (err?.status === 404 || err?.status === 409) {
      const selectedId = selected?.id;
      closeCrmEditors();
      await loadCrmQuoteLines();
      if (selectedId && err.status === 409) selectCrmQuoteLine(selectedId);
    }
  } finally {
    setEnabled("btnCrmSubmitQuoteLine", true);
  }
}

async function submitCrmIssueQuote(event) {
  event.preventDefault();
  const quote = state.selectedCrmQuote;
  if (
    !quote ||
    quote.status !== "draft" ||
    !crmCan("pkg.crm.quote", "issue", quote.id)
  ) {
    setCrmFormState(
      "crmIssueQuoteFormState",
      "denied",
      "Quote issue permission is unavailable.",
    );
    return;
  }
  if (!$("crmIssueQuoteConfirmed").checked) {
    setCrmFormState(
      "crmIssueQuoteFormState",
      "error",
      "Explicit confirmation is required before Quote Issue.",
    );
    return;
  }
  const body = {
    idempotency_key: uuid(),
    human_confirm: true,
  };
  const approvalRef = optionalCrmText("crmIssueQuoteApprovalRef");
  if (approvalRef) {
    body.approval_ref = approvalRef;
  }
  setEnabled("btnCrmSubmitIssueQuote", false);
  setCrmFormState(
    "crmIssueQuoteFormState",
    "loading",
    "Submitting governed Quote Issue…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmQuoteIssue(quote.id),
      body,
    );
    closeCrmEditors();
    await loadCrmQuotes();
    await selectCrmQuote(quote.id);
    syncCrmWriteControls();
    log("CRM Quote issued", {
      quote_id: quote.id,
      status: payload?.data?.status || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmIssueQuoteFormState",
      "error",
      crmWriteErrorMessage(err),
    );
    if (err?.status === 409) {
      closeCrmEditors();
      await selectCrmQuote(quote.id).catch(() => {});
    }
  } finally {
    setEnabled("btnCrmSubmitIssueQuote", true);
  }
}

async function submitCrmConvert(event) {
  event.preventDefault();
  const quote = state.selectedCrmQuote;
  if (
    !quote ||
    quote.status !== "issued" ||
    !crmCan("pkg.crm.quote_conversion", "convert", quote.id)
  ) {
    setCrmFormState(
      "crmConvertFormState",
      "denied",
      "Convert permission is unavailable for this Quote.",
    );
    return;
  }
  if (!$("crmConvertConfirmed").checked) {
    setCrmFormState(
      "crmConvertFormState",
      "error",
      "Explicit confirmation is required before Convert.",
    );
    return;
  }
  const body = {
    idempotency_key: uuid(),
  };
  const functionalCurrency = optionalCrmText("crmConvertFunctionalCurrency");
  if (functionalCurrency) {
    body.functional_currency = functionalCurrency.toUpperCase();
  }
  const fxRate = $("crmConvertFxRate").value.trim();
  if (fxRate) {
    body.fx_rate = fxRate;
  }
  const approvalRef = optionalCrmText("crmConvertApprovalRef");
  if (approvalRef) {
    body.approval_ref = approvalRef;
  }
  setEnabled("btnCrmSubmitConvert", false);
  setCrmFormState(
    "crmConvertFormState",
    "loading",
    "Submitting governed Quote Convert…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmQuoteConvert(quote.id),
      body,
    );
    state.selectedCrmConversion = payload?.data || null;
    state.selectedCrmConvertSalesOrder = null;
    closeCrmEditors();
    renderCrmConversion();
    renderCrmConvertSalesOrder();
    syncCrmWriteControls();
    log("CRM Quote converted", {
      quote_id: quote.id,
      conversion_id: state.selectedCrmConversion?.id || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState("crmConvertFormState", "error", crmWriteErrorMessage(err));
  } finally {
    setEnabled("btnCrmSubmitConvert", true);
  }
}

async function submitCrmCreateSo(event) {
  event.preventDefault();
  const conversion = state.selectedCrmConversion;
  if (
    !conversion ||
    conversion.status !== "ready" ||
    !crmCan("pkg.crm.sales_order", "create", conversion.id)
  ) {
    setCrmFormState(
      "crmCreateSoFormState",
      "denied",
      "Sales Order create permission is unavailable.",
    );
    return;
  }
  if (!$("crmCreateSoConfirmed").checked) {
    setCrmFormState(
      "crmCreateSoFormState",
      "error",
      "Explicit confirmation is required before Sales Order shell creation.",
    );
    return;
  }
  setEnabled("btnCrmSubmitCreateSo", false);
  setCrmFormState(
    "crmCreateSoFormState",
    "loading",
    "Creating governed Sales Order shell…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmConversionSalesOrder(conversion.id),
      { idempotency_key: uuid() },
    );
    state.selectedCrmConvertSalesOrder = payload?.data || null;
    closeCrmEditors();
    await loadCrmConversion();
    renderCrmConvertSalesOrder();
    await loadCrmSalesOrders();
    if (state.selectedCrmConvertSalesOrder?.id) {
      await selectCrmSalesOrder(state.selectedCrmConvertSalesOrder.id).catch(
        () => {},
      );
    }
    syncCrmWriteControls();
    log("CRM Sales Order shell created from Conversion", {
      conversion_id: conversion.id,
      sales_order_id: state.selectedCrmConvertSalesOrder?.id || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState("crmCreateSoFormState", "error", crmWriteErrorMessage(err));
    if (err?.status === 409) {
      closeCrmEditors();
      await loadCrmConversion();
    }
  } finally {
    setEnabled("btnCrmSubmitCreateSo", true);
  }
}

async function submitCrmConfirmSalesOrder(event) {
  event.preventDefault();
  const order = state.selectedCrmSalesOrder;
  if (
    !order ||
    order.status !== "created" ||
    !crmCan("pkg.crm.sales_order", "confirm", order.id)
  ) {
    setCrmFormState(
      "crmConfirmSoFormState",
      "denied",
      "Sales Order confirm permission is unavailable.",
    );
    return;
  }
  if (!$("crmConfirmSoConfirmed").checked) {
    setCrmFormState(
      "crmConfirmSoFormState",
      "error",
      "Explicit confirmation is required before Sales Order Confirm.",
    );
    return;
  }
  const body = {
    idempotency_key: uuid(),
    human_confirm: true,
  };
  const approvalRef = optionalCrmText("crmConfirmSoApprovalRef");
  if (approvalRef) {
    body.approval_ref = approvalRef;
  }
  setEnabled("btnCrmSubmitConfirmSo", false);
  setCrmFormState(
    "crmConfirmSoFormState",
    "loading",
    "Submitting governed Sales Order Confirm…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmSalesOrderConfirm(order.id),
      body,
    );
    closeCrmEditors();
    await loadCrmSalesOrders();
    await selectCrmSalesOrder(order.id);
    syncCrmWriteControls();
    log("CRM Sales Order confirmed", {
      sales_order_id: order.id,
      status: payload?.data?.status || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmConfirmSoFormState",
      "error",
      crmWriteErrorMessage(err),
    );
    if (err?.status === 409) {
      closeCrmEditors();
      await selectCrmSalesOrder(order.id).catch(() => {});
    }
  } finally {
    setEnabled("btnCrmSubmitConfirmSo", true);
  }
}

async function submitCrmCreateDeliveryOrder(event) {
  event.preventDefault();
  const order = state.selectedCrmSalesOrder;
  if (
    !order ||
    (order.status !== "confirmed" && order.status !== "partially_shipped") ||
    !crmCan("pkg.crm.delivery_order", "create", order.id)
  ) {
    setCrmFormState(
      "crmCreateDoFormState",
      "denied",
      "Delivery Order create permission is unavailable.",
    );
    return;
  }
  if (!$("crmCreateDoConfirmed").checked) {
    setCrmFormState(
      "crmCreateDoFormState",
      "error",
      "Explicit confirmation is required before Delivery Order creation.",
    );
    return;
  }
  setEnabled("btnCrmSubmitCreateDo", false);
  setCrmFormState(
    "crmCreateDoFormState",
    "loading",
    "Creating governed Delivery Order shell…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmSalesOrderDeliveryOrder(order.id),
      { idempotency_key: uuid() },
    );
    state.selectedCrmDeliveryOrder = payload?.data || null;
    closeCrmEditors();
    renderCrmDeliveryOrder();
    syncCrmWriteControls();
    log("CRM Delivery Order shell created", {
      sales_order_id: order.id,
      delivery_order_id: state.selectedCrmDeliveryOrder?.id || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState("crmCreateDoFormState", "error", crmWriteErrorMessage(err));
  } finally {
    setEnabled("btnCrmSubmitCreateDo", true);
  }
}

async function submitCrmReleaseDeliveryOrder(event) {
  event.preventDefault();
  const deliveryOrder = state.selectedCrmDeliveryOrder;
  if (
    !deliveryOrder ||
    deliveryOrder.status !== "draft" ||
    !crmCan("pkg.crm.delivery_order", "release", deliveryOrder.id)
  ) {
    setCrmFormState(
      "crmReleaseDoFormState",
      "denied",
      "Delivery Order release permission is unavailable.",
    );
    return;
  }
  if (!$("crmReleaseDoConfirmed").checked) {
    setCrmFormState(
      "crmReleaseDoFormState",
      "error",
      "Explicit confirmation is required before Delivery Order Release.",
    );
    return;
  }
  const body = {
    idempotency_key: uuid(),
    human_confirm: true,
  };
  const approvalRef = optionalCrmText("crmReleaseDoApprovalRef");
  if (approvalRef) {
    body.approval_ref = approvalRef;
  }
  setEnabled("btnCrmSubmitReleaseDo", false);
  setCrmFormState(
    "crmReleaseDoFormState",
    "loading",
    "Submitting governed Delivery Order Release…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmDeliveryOrderRelease(deliveryOrder.id),
      body,
    );
    state.selectedCrmDeliveryOrder = payload?.data || null;
    clearCrmArInvoice();
    closeCrmEditors();
    renderCrmDeliveryOrder();
    syncCrmWriteControls();
    log("CRM Delivery Order released", {
      delivery_order_id: deliveryOrder.id,
      status: payload?.data?.status || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmReleaseDoFormState",
      "error",
      crmWriteErrorMessage(err),
    );
    if (err?.status === 409) {
      closeCrmEditors();
      await refreshCrmDeliveryOrder().catch(() => {});
    }
  } finally {
    setEnabled("btnCrmSubmitReleaseDo", true);
  }
}

async function submitCrmCreateArInvoice(event) {
  event.preventDefault();
  const deliveryOrder = state.selectedCrmDeliveryOrder;
  if (
    !deliveryOrder ||
    deliveryOrder.status !== "released" ||
    !crmCan("pkg.crm.ar_invoice", "create", deliveryOrder.id)
  ) {
    setCrmFormState(
      "crmCreateArInvoiceFormState",
      "denied",
      "AR Invoice create permission is unavailable.",
    );
    return;
  }
  if (!$("crmCreateArInvoiceConfirmed").checked) {
    setCrmFormState(
      "crmCreateArInvoiceFormState",
      "error",
      "Explicit confirmation is required before AR Invoice creation.",
    );
    return;
  }
  setEnabled("btnCrmSubmitCreateArInvoice", false);
  setCrmFormState(
    "crmCreateArInvoiceFormState",
    "loading",
    "Creating governed AR Invoice shell…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmDeliveryOrderArInvoice(deliveryOrder.id),
      { idempotency_key: uuid() },
    );
    state.selectedCrmArInvoice = payload?.data || null;
    closeCrmEditors();
    renderCrmArInvoice();
    syncCrmWriteControls();
    log("CRM AR Invoice shell created", {
      delivery_order_id: deliveryOrder.id,
      ar_invoice_id: state.selectedCrmArInvoice?.id || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmCreateArInvoiceFormState",
      "error",
      crmWriteErrorMessage(err),
    );
  } finally {
    setEnabled("btnCrmSubmitCreateArInvoice", true);
  }
}

async function submitCrmIssueArInvoice(event) {
  event.preventDefault();
  const invoice = state.selectedCrmArInvoice;
  if (
    !invoice ||
    invoice.status !== "draft" ||
    !crmCan("pkg.crm.ar_invoice", "issue", invoice.id)
  ) {
    setCrmFormState(
      "crmIssueArInvoiceFormState",
      "denied",
      "AR Invoice issue permission is unavailable.",
    );
    return;
  }
  if (!$("crmIssueArInvoiceConfirmed").checked) {
    setCrmFormState(
      "crmIssueArInvoiceFormState",
      "error",
      "Explicit confirmation is required before AR Invoice Issue.",
    );
    return;
  }
  setEnabled("btnCrmSubmitIssueArInvoice", false);
  setCrmFormState(
    "crmIssueArInvoiceFormState",
    "loading",
    "Submitting governed AR Invoice Issue…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmArInvoiceIssue(invoice.id),
      { idempotency_key: uuid(), human_confirm: true },
    );
    state.selectedCrmArInvoice = payload?.data || null;
    closeCrmEditors();
    renderCrmArInvoice();
    syncCrmWriteControls();
    log("CRM AR Invoice issued", {
      ar_invoice_id: invoice.id,
      status: payload?.data?.status || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmIssueArInvoiceFormState",
      "error",
      crmWriteErrorMessage(err),
    );
    if (err?.status === 409) {
      closeCrmEditors();
      await refreshCrmArInvoice().catch(() => {});
    }
  } finally {
    setEnabled("btnCrmSubmitIssueArInvoice", true);
  }
}

async function submitCrmVoidArInvoice(event) {
  event.preventDefault();
  const invoice = state.selectedCrmArInvoice;
  if (
    !invoice ||
    invoice.status !== "issued" ||
    !crmCan("pkg.crm.ar_invoice", "void", invoice.id)
  ) {
    setCrmFormState(
      "crmVoidArInvoiceFormState",
      "denied",
      "AR Invoice void permission is unavailable.",
    );
    return;
  }
  const reason = $("crmVoidArInvoiceReason").value.trim();
  if (!reason) {
    setCrmFormState(
      "crmVoidArInvoiceFormState",
      "error",
      "Void reason is required (1–500 characters).",
    );
    return;
  }
  if (!$("crmVoidArInvoiceConfirmed").checked) {
    setCrmFormState(
      "crmVoidArInvoiceFormState",
      "error",
      "Explicit confirmation is required before AR Invoice Void.",
    );
    return;
  }
  setEnabled("btnCrmSubmitVoidArInvoice", false);
  setCrmFormState(
    "crmVoidArInvoiceFormState",
    "loading",
    "Submitting governed AR Invoice Void…",
  );
  try {
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmArInvoiceVoid(invoice.id),
      { idempotency_key: uuid(), human_confirm: true, reason },
    );
    state.selectedCrmArInvoice = payload?.data || null;
    closeCrmEditors();
    renderCrmArInvoice();
    syncCrmWriteControls();
    log("CRM AR Invoice voided", {
      ar_invoice_id: invoice.id,
      status: payload?.data?.status || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmVoidArInvoiceFormState",
      "error",
      crmWriteErrorMessage(err),
    );
    if (err?.status === 409) {
      closeCrmEditors();
      await refreshCrmArInvoice().catch(() => {});
    }
  } finally {
    setEnabled("btnCrmSubmitVoidArInvoice", true);
  }
}

async function submitCrmCreateReturnAuthorization(event) {
  event.preventDefault();
  const deliveryOrder = state.selectedCrmDeliveryOrder;
  if (
    !deliveryOrder ||
    deliveryOrder.status !== "shipped" ||
    !crmCan("pkg.crm.return_authorization", "create", deliveryOrder.id)
  ) {
    setCrmFormState(
      "crmCreateReturnAuthorizationFormState",
      "denied",
      "Return Authorization create permission is unavailable.",
    );
    return;
  }
  const reason = $("crmCreateReturnAuthorizationReason").value.trim();
  if (!reason) {
    setCrmFormState(
      "crmCreateReturnAuthorizationFormState",
      "error",
      "A reason is required before Return Authorization creation.",
    );
    return;
  }
  if (!$("crmCreateReturnAuthorizationConfirmed").checked) {
    setCrmFormState(
      "crmCreateReturnAuthorizationFormState",
      "error",
      "Explicit confirmation is required before Return Authorization creation.",
    );
    return;
  }
  setEnabled("btnCrmSubmitCreateReturnAuthorization", false);
  setCrmFormState(
    "crmCreateReturnAuthorizationFormState",
    "loading",
    "Creating governed Return Authorization…",
  );
  try {
    const body = {
      reason,
      idempotency_key: uuid(),
      human_confirm: true,
    };
    const invoice = state.selectedCrmArInvoice;
    if (
      invoice &&
      (invoice.status === "issued" || invoice.status === "voided")
    ) {
      body.invoice_id = invoice.id;
    }
    const payload = await api(
      "POST",
      TERMINAL_PATHS.crmDeliveryOrderReturnAuthorization(deliveryOrder.id),
      body,
    );
    state.selectedCrmReturnAuthorization = payload?.data || null;
    closeCrmEditors();
    renderCrmReturnAuthorization();
    syncCrmWriteControls();
    log("CRM Return Authorization created", {
      delivery_order_id: deliveryOrder.id,
      return_authorization_id: state.selectedCrmReturnAuthorization?.id || null,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState(
      "crmCreateReturnAuthorizationFormState",
      "error",
      crmWriteErrorMessage(err),
    );
  } finally {
    setEnabled("btnCrmSubmitCreateReturnAuthorization", true);
  }
}

async function submitCrmArchive(event) {
  event.preventDefault();
  const target = state.crmArchiveTarget;
  const reason = $("crmArchiveReason").value.trim();
  if (!target || !reason || !$("crmArchiveConfirmed").checked) {
    setCrmFormState(
      "crmArchiveFormState",
      "error",
      "A reason and explicit confirmation are required.",
    );
    return;
  }
  const resourceTypes = {
    customer: "pkg.crm.customer",
    contact: "pkg.crm.contact",
    opportunity: "pkg.crm.opportunity",
    requirement: "pkg.crm.requirement",
    quote: "pkg.crm.quote",
    quoteLine: "pkg.crm.quote_line",
  };
  const resourceType = resourceTypes[target.kind];
  if (!crmCan(resourceType, "archive", target.id)) {
    setCrmFormState("crmArchiveFormState", "denied", "Write permission is unavailable.");
    return;
  }
  const paths = {
    customer: TERMINAL_PATHS.crmCustomerArchive(target.id),
    contact: TERMINAL_PATHS.crmContactArchive(target.customerId, target.id),
    opportunity: TERMINAL_PATHS.crmOpportunityArchive(target.id),
    requirement: TERMINAL_PATHS.crmRequirementArchive(target.id),
    quote: TERMINAL_PATHS.crmQuoteArchive(target.id),
    quoteLine: TERMINAL_PATHS.crmQuoteLineArchive(target.quoteId, target.id),
  };
  const path = paths[target.kind];
  setEnabled("btnCrmConfirmArchive", false);
  setCrmFormState("crmArchiveFormState", "loading", "Archiving governed record…");
  try {
    const payload = await api("POST", path, {
      reason,
      expected_version: target.version,
    });
    closeCrmEditors();
    if (target.kind === "customer") {
      await loadCrmCustomers();
    } else if (target.kind === "opportunity") {
      await loadCrmOpportunities();
    } else if (target.kind === "requirement") {
      await loadCrmRequirements();
    } else if (target.kind === "quote") {
      await loadCrmQuotes();
    } else if (target.kind === "quoteLine") {
      await loadCrmQuoteLines();
    } else {
      await loadCrmContacts();
    }
    log(`CRM ${target.kind} archived`, {
      record_id: target.id,
      audit_id: payload?.audit_id || null,
    });
  } catch (err) {
    setCrmFormState("crmArchiveFormState", "error", crmWriteErrorMessage(err));
    if (err?.status === 404 || err?.status === 409) {
      closeCrmEditors();
      if (target.kind === "customer") {
        await loadCrmCustomers();
      } else if (target.kind === "opportunity") {
        await loadCrmOpportunities();
      } else if (target.kind === "requirement") {
        await loadCrmRequirements();
      } else if (target.kind === "quote") {
        await loadCrmQuotes();
      } else if (target.kind === "quoteLine") {
        await loadCrmQuoteLines();
      } else {
        await loadCrmContacts();
      }
    }
  } finally {
    setEnabled("btnCrmConfirmArchive", true);
  }
}

async function loadDemoBootstrap() {
  try {
    const response = await fetch(TERMINAL_PATHS.demoBootstrap, {
      method: "GET",
      headers: { Accept: "application/json" },
    });
    if (response.status === 404) {
      return false;
    }
    const payload = await response.json();
    const data = payload?.data || {};
    if (!response.ok || !data.available) {
      return false;
    }
    if (data.subject_id && $("subjectId")) {
      $("subjectId").value = data.subject_id;
    }
    if (data.tenant_id && $("tenantId")) {
      $("tenantId").value = data.tenant_id;
    }
    if (!$("correlationId")?.value) {
      $("correlationId").value = uuid();
    }
    if (data.extension_id) {
      state.extensionId = data.extension_id;
    }
    if (data.extension_key) {
      state.extensionKeyHint = data.extension_key;
      if ($("extKey")) {
        $("extKey").value = data.extension_key;
      }
    }
    if (data.extension_version && $("extVersion")) {
      $("extVersion").value = data.extension_version;
    }
    if (data.listing_id) {
      state.demoListingId = data.listing_id;
      if ($("listingId")) {
        $("listingId").value = data.listing_id;
      }
    }
    if (data.listing_package_key && $("listingPackageKey")) {
      $("listingPackageKey").value = data.listing_package_key;
    }
    if (typeof syncExtensionButtons === "function") {
      syncExtensionButtons();
    }
    if (data.sample_knowledge_pack_url && $("sampleKnowledgePackLink")) {
      $("sampleKnowledgePackLink").href = data.sample_knowledge_pack_url;
    }
    log("Demo bootstrap applied (PHX-G182)", {
      subject_id: data.subject_id,
      tenant_id: data.tenant_id,
      extension_id: data.extension_id || null,
      listing_id: data.listing_id || null,
      declared_surface_keys: data.declared_surface_keys || [],
      sample_knowledge_pack_path: data.sample_knowledge_pack_path || null,
      sample_knowledge_pack_milestone: data.sample_knowledge_pack_milestone || null,
    });
    try {
      await hydrateSignedExtensionHost({ quiet: true });
    } catch (err) {
      log("Extension hydrate deferred", { message: String(err.message || err) });
    }
    try {
      await loadHostAcquireStatus({ quiet: true });
    } catch (err) {
      log("Host-acquire status deferred", { message: String(err.message || err) });
    }
    try {
      await loadPaymentClearingStatus({ quiet: true });
    } catch (err) {
      log("Payment-clearing status deferred", {
        message: String(err.message || err),
      });
    }
    try {
      await loadDomainFoundationStatus({ quiet: true });
    } catch (err) {
      log("Domain foundation status deferred", {
        message: String(err.message || err),
      });
    }
    try {
      await loadFinancePlatformStatus({ quiet: true });
    } catch (err) {
      log("Finance/platform status deferred", {
        message: String(err.message || err),
      });
    }
    try {
      await loadEventOutboxStatus({ quiet: true });
    } catch (err) {
      log("Event/outbox status deferred", {
        message: String(err.message || err),
      });
    }
    try {
      await loadPackageResolveAlignStatus({ quiet: true });
    } catch (err) {
      log("Package resolve align status deferred", {
        message: String(err.message || err),
      });
    }
    try {
      await loadRoleCatalogStatus({ quiet: true });
    } catch (err) {
      log("Role catalog status deferred", {
        message: String(err.message || err),
      });
    }
    try {
      await loadExtHostPathReadiness({ quiet: true });
    } catch (err) {
      log("Host-path readiness deferred", { message: String(err.message || err) });
    }
    try {
      await loadSampleKnowledgePackProductPosture({ quiet: true });
    } catch (err) {
      log("Sample knowledge pack posture deferred", {
        message: String(err.message || err),
      });
    }
    return true;
  } catch {
    return false;
  }
}

async function loadPackageSurfaces() {
  try {
    const data = await api("GET", TERMINAL_PATHS.packageSurfaces, undefined, {
      auth: true,
      platform: false,
    });
    const rows = Array.isArray(data?.data) ? data.data : Array.isArray(data) ? data : [];
    state.packageSurfaces = rows;
    state.packageSurfacesSource = rows.length ? "declared" : "fixture";
    log("Package surfaces loaded", {
      count: rows.length,
      source: state.packageSurfacesSource,
    });
  } catch (err) {
    state.packageSurfaces = [];
    state.packageSurfacesSource = "fixture";
    log("Package surfaces unavailable; using offline fixtures", {
      message: String(err.message || err),
    });
  }
  renderProductCatalog();
  renderOpsQueue();
  renderSampleFlowQueue();
  renderOrderFlowQueue();
}

function renderProductCatalog() {
  const host = $("productCatalog");
  if (!host) {
    return;
  }
  host.replaceChildren();
  const declared = surfacesForPrefix("product.");
  if (declared.length) {
    for (const surface of declared) {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "choice-row";
      row.dataset.surfaceKey = surface.surface_key;
      row.setAttribute("role", "option");
      row.innerHTML = `<span class="choice-title">${surface.title || surface.surface_key}</span><span class="choice-meta">declared · ${surface.surface_key}</span>`;
      row.addEventListener("click", () => selectProductSurface(surface.surface_key));
      host.appendChild(row);
    }
    return;
  }
  for (const product of DEMO_PRODUCTS) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "choice-row";
    row.dataset.productId = product.id;
    row.setAttribute("role", "option");
    row.innerHTML = `<span class="choice-title">${product.name}</span><span class="choice-meta">fixture · ${product.sku}</span>`;
    row.addEventListener("click", () => selectProduct(product.id));
    host.appendChild(row);
  }
}

function selectProductSurface(surfaceKey) {
  state.selectedProductSurfaceKey = surfaceKey;
  state.selectedProductId = null;
  const surface = state.packageSurfaces.find((item) => item.surface_key === surfaceKey);
  const detail = $("productDetail");
  if (!surface || !detail) {
    return;
  }
  detail.querySelector('[data-field="name"]').textContent = surface.title || surface.surface_key;
  detail.querySelector('[data-field="sku"]').textContent = surface.surface_key;
  detail.querySelector('[data-field="status"]').textContent = "declared";
  detail.querySelector('[data-field="summary"]').textContent =
    surface.description || "Declared Package Surface (BOOK23 §10.1).";
  document.querySelectorAll("#productCatalog .choice-row").forEach((row) => {
    row.classList.toggle("is-selected", row.dataset.surfaceKey === surfaceKey);
  });
  setEnabled("btnProductHandoff", true);
  if (surfaceKey === "product.sample" && DEMO_SAMPLE_FLOW.length) {
    selectSampleFlowStep(DEMO_SAMPLE_FLOW[0].id);
  }
}

function selectProduct(productId) {
  state.selectedProductId = productId;
  state.selectedProductSurfaceKey = null;
  const product = DEMO_PRODUCTS.find((item) => item.id === productId);
  const detail = $("productDetail");
  if (!product || !detail) {
    return;
  }
  detail.querySelector('[data-field="name"]').textContent = product.name;
  detail.querySelector('[data-field="sku"]').textContent = product.sku;
  detail.querySelector('[data-field="status"]').textContent = `${product.status} (fixture)`;
  detail.querySelector('[data-field="summary"]').textContent = product.summary;
  document.querySelectorAll("#productCatalog .choice-row").forEach((row) => {
    row.classList.toggle("is-selected", row.dataset.productId === productId);
  });
  setEnabled("btnProductHandoff", true);
}

async function handoffSelectedProduct() {
  if (state.selectedProductSurfaceKey) {
    const surfaceKey = state.selectedProductSurfaceKey;
    const actionKey =
      SURFACE_DEFAULT_ACTIONS[surfaceKey] || "product.offer.review";
    let resolved;
    try {
      resolved = await api(
        "POST",
        TERMINAL_PATHS.packageActionResolve,
        { action_key: actionKey },
        { auth: true, platform: false },
      );
    } catch (err) {
      log("Declared product surface resolve denied — handoff blocked (fail-closed)", {
        message: String(err.message || err),
        action: actionKey,
        surface: surfaceKey,
      });
      throw err;
    }
    handoffToOperator({
      intentText: `Declared product action ${resolved.action_key} on ${surfaceKey}`,
      action: resolved.action_key || actionKey,
      resourceRef: `package:${resolved.package_key || "noventi.sample.product"}:${surfaceKey}`,
      impactSummary: `Resolve ${actionKey} via Package Platform (source=${resolved.source || "package_manifest"})`,
      highImpact: Boolean(resolved.high_impact),
    });
    return;
  }
  const product = DEMO_PRODUCTS.find((item) => item.id === state.selectedProductId);
  if (!product) {
    throw new Error("Select a product or declared surface first");
  }
  let action = product.action;
  let highImpact = false;
  let source = "fixture";
  try {
    const resolved = await api(
      "POST",
      TERMINAL_PATHS.packageActionResolve,
      { action_key: product.action },
      { auth: true, platform: false },
    );
    action = resolved.action_key || product.action;
    highImpact = Boolean(resolved.high_impact);
    source = resolved.source || "package_manifest";
  } catch (err) {
    log("Product fixture resolve denied — handoff blocked (fail-closed)", {
      message: String(err.message || err),
      action: product.action,
    });
    throw err;
  }
  handoffToOperator({
    intentText: `Review product offer: ${product.name} (${product.sku})`,
    action,
    resourceRef: product.resourceRef,
    impactSummary: `${product.impactSummary} (source=${source})`,
    highImpact,
  });
}

function renderOpsQueue() {
  const host = $("opsQueue");
  if (!host) {
    return;
  }
  host.replaceChildren();
  const declared = surfacesForPrefix("ops.");
  if (declared.length) {
    for (const surface of declared) {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "choice-row";
      row.dataset.surfaceKey = surface.surface_key;
      row.setAttribute("role", "option");
      row.innerHTML = `<span class="choice-title">${surface.title || surface.surface_key}</span><span class="choice-meta">declared · ${surface.surface_key}</span>`;
      row.addEventListener("click", () => selectOpsSurface(surface.surface_key));
      host.appendChild(row);
    }
    return;
  }
  for (const item of DEMO_OPS_ITEMS) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "choice-row";
    row.dataset.opsId = item.id;
    row.setAttribute("role", "option");
    const impact = item.highImpact ? "high-impact" : "standard";
    row.innerHTML = `<span class="choice-title">${item.title}</span><span class="choice-meta">fixture · ${impact}</span>`;
    row.addEventListener("click", () => selectOpsItem(item.id));
    host.appendChild(row);
  }
}

function selectOpsSurface(surfaceKey) {
  state.selectedOpsSurfaceKey = surfaceKey;
  state.selectedOpsId = null;
  const surface = state.packageSurfaces.find((item) => item.surface_key === surfaceKey);
  if (!surface) {
    return;
  }
  if ($("opsBriefTitle")) {
    $("opsBriefTitle").value = surface.title || surface.surface_key;
  }
  if ($("opsBriefFocus")) {
    $("opsBriefFocus").value = surfaceKey === "ops.order" ? "order" : "declared";
  }
  if ($("opsBriefBody")) {
    $("opsBriefBody").value =
      surface.description || "Compose ops brief from declared Package Surface.";
  }
  document.querySelectorAll("#opsQueue .choice-row").forEach((row) => {
    row.classList.toggle("is-selected", row.dataset.surfaceKey === surfaceKey);
  });
  setEnabled("btnOpsHandoffSelected", true);
  if ($("opsBriefView")) {
    $("opsBriefView").textContent = JSON.stringify(
      {
        source: "declared_package_surface",
        surface_key: surface.surface_key,
        title: surface.title,
        description: surface.description,
        default_action: SURFACE_DEFAULT_ACTIONS[surfaceKey] || "ops.brief.compose",
      },
      null,
      2,
    );
  }
  if (surfaceKey === "ops.order" && DEMO_ORDER_FLOW.length) {
    selectOrderFlowStep(DEMO_ORDER_FLOW[0].id);
  }
}

function selectOpsItem(opsId) {
  state.selectedOpsId = opsId;
  state.selectedOpsSurfaceKey = null;
  const item = DEMO_OPS_ITEMS.find((entry) => entry.id === opsId);
  if (!item) {
    return;
  }
  if ($("opsBriefTitle")) {
    $("opsBriefTitle").value = item.title;
  }
  if ($("opsBriefFocus")) {
    $("opsBriefFocus").value = item.focus;
  }
  if ($("opsBriefBody")) {
    $("opsBriefBody").value = item.body;
  }
  document.querySelectorAll("#opsQueue .choice-row").forEach((row) => {
    row.classList.toggle("is-selected", row.dataset.opsId === opsId);
  });
  setEnabled("btnOpsHandoffSelected", true);
  if ($("opsBriefView")) {
    $("opsBriefView").textContent = JSON.stringify(
      {
        id: item.id,
        title: item.title,
        focus: item.focus,
        action: item.action,
        resource_ref: item.resourceRef,
        high_impact: item.highImpact,
        body: item.body,
      },
      null,
      2,
    );
  }
}

async function handoffSelectedOpsItem() {
  if (state.selectedOpsSurfaceKey) {
    const surfaceKey = state.selectedOpsSurfaceKey;
    const actionKey = SURFACE_DEFAULT_ACTIONS[surfaceKey] || "ops.brief.compose";
    let resolved;
    try {
      resolved = await api(
        "POST",
        TERMINAL_PATHS.packageActionResolve,
        { action_key: actionKey },
        { auth: true, platform: false },
      );
    } catch (err) {
      log("Declared ops surface resolve denied — handoff blocked (fail-closed)", {
        message: String(err.message || err),
        action: actionKey,
        surface: surfaceKey,
      });
      throw err;
    }
    const title = ($("opsBriefTitle")?.value || "").trim() || surfaceKey;
    const body =
      ($("opsBriefBody")?.value || "").trim() ||
      "Compose ops brief from declared Package Surface.";
    handoffToOperator({
      intentText: `${title}: ${body}`,
      action: resolved.action_key || actionKey,
      resourceRef: `package:${resolved.package_key || "noventi.sample.ops"}:${surfaceKey}`,
      impactSummary: `Resolve ${actionKey} via Package Platform (source=${resolved.source || "package_manifest"})`,
      highImpact: Boolean(resolved.high_impact),
    });
    return;
  }
  const item = DEMO_OPS_ITEMS.find((entry) => entry.id === state.selectedOpsId);
  if (!item) {
    throw new Error("Select an ops surface or queue item first");
  }
  let action = item.action;
  let highImpact = Boolean(item.highImpact);
  let source = "fixture";
  try {
    const resolved = await api(
      "POST",
      TERMINAL_PATHS.packageActionResolve,
      { action_key: item.action },
      { auth: true, platform: false },
    );
    action = resolved.action_key || item.action;
    highImpact = Boolean(resolved.high_impact);
    source = resolved.source || "package_manifest";
  } catch (err) {
    log("Ops fixture resolve denied — handoff blocked (fail-closed)", {
      message: String(err.message || err),
      action: item.action,
    });
    throw err;
  }
  handoffToOperator({
    intentText: `${item.title}: ${item.body}`,
    action,
    resourceRef: item.resourceRef,
    impactSummary: `Ops brief — ${item.focus} (source=${source})`,
    highImpact,
  });
}

async function composeOpsBriefAndHandoff() {
  const title = ($("opsBriefTitle")?.value || "").trim() || "运营简报";
  const focus = ($("opsBriefFocus")?.value || "").trim() || "general";
  const body = ($("opsBriefBody")?.value || "").trim();
  if (!body) {
    throw new Error("Ops brief body is required");
  }
  const actionKey = "ops.brief.compose";
  // Fail-closed: resolve must succeed before Operator handoff (DAL-U167 pattern).
  let resolved;
  try {
    resolved = await api(
      "POST",
      TERMINAL_PATHS.packageActionResolve,
      { action_key: actionKey },
      { auth: true, platform: false },
    );
  } catch (err) {
    log("Ops brief resolve denied — handoff blocked (fail-closed)", {
      message: String(err.message || err),
      action: actionKey,
    });
    throw err;
  }
  const brief = {
    title,
    focus,
    body,
    action: resolved.action_key || actionKey,
    resource_ref: `pkg.ops.brief:${focus}`,
    high_impact: Boolean(resolved.high_impact),
    package_key: resolved.package_key || null,
    source: resolved.source || "package_manifest",
  };
  if ($("opsBriefView")) {
    $("opsBriefView").textContent = JSON.stringify(brief, null, 2);
  }
  handoffToOperator({
    intentText: `${title} [${focus}]: ${body}`,
    action: brief.action,
    resourceRef: brief.resource_ref,
    impactSummary: `Compose ops brief for ${focus} (source=${brief.source})`,
    highImpact: brief.high_impact,
  });
}

function renderSampleFlowQueue() {
  const host = $("sampleFlowQueue");
  if (!host) {
    return;
  }
  host.replaceChildren();
  for (const step of DEMO_SAMPLE_FLOW) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "choice-row";
    row.dataset.sampleFlowId = step.id;
    row.setAttribute("role", "option");
    row.innerHTML = `<span class="choice-title">${step.title}</span><span class="choice-meta">demo · ${step.action}</span>`;
    row.addEventListener("click", () => selectSampleFlowStep(step.id));
    host.appendChild(row);
  }
}

function selectSampleFlowStep(stepId) {
  state.selectedSampleFlowId = stepId;
  const step = DEMO_SAMPLE_FLOW.find((item) => item.id === stepId);
  if (!step) {
    return;
  }
  document.querySelectorAll("#sampleFlowQueue .choice-row").forEach((row) => {
    row.classList.toggle("is-selected", row.dataset.sampleFlowId === stepId);
  });
  setEnabled("btnSampleFlowHandoff", true);
  if ($("sampleFlowView")) {
    $("sampleFlowView").textContent = JSON.stringify(
      {
        id: step.id,
        title: step.title,
        body: step.body,
        action: step.action,
        resource_ref: step.resourceRef,
        high_impact: step.highImpact,
        knowledge_refs: step.knowledgeRefs,
        surface: "product.sample",
        mode: "terminal_demo_handoff",
      },
      null,
      2,
    );
  }
}

async function handoffSelectedSampleFlow() {
  const step = DEMO_SAMPLE_FLOW.find((item) => item.id === state.selectedSampleFlowId);
  if (!step) {
    throw new Error("Select a sample flow step first");
  }
  let action = step.action;
  let resourceRef = step.resourceRef;
  let highImpact = step.highImpact;
  let source = "demo_fixture";
  try {
    const resolved = await api(
      "POST",
      TERMINAL_PATHS.packageActionResolve,
      { action_key: step.action },
      { auth: true, platform: false },
    );
    action = resolved.action_key || step.action;
    resourceRef = `package:${resolved.package_key || "noventi.sample.product"}:product.sample:${step.id}`;
    highImpact = Boolean(resolved.high_impact);
    source = resolved.source || "package_manifest";
  } catch (err) {
    log("Sample flow resolve denied — handoff blocked (fail-closed)", {
      message: String(err.message || err),
      action: step.action,
    });
    throw err;
  }
  handoffToOperator({
    intentText: `[样品演示] ${step.title}: ${step.body}`,
    action,
    resourceRef,
    impactSummary: `Sample demo · ${step.id} · source=${source} · refs=${(step.knowledgeRefs || []).join(",")}`,
    highImpact,
  });
  log("Sample flow handoff", { step: step.id, action, source, highImpact });
}

function renderOrderFlowQueue() {
  const host = $("orderFlowQueue");
  if (!host) {
    return;
  }
  host.replaceChildren();
  for (const step of DEMO_ORDER_FLOW) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "choice-row";
    row.dataset.orderFlowId = step.id;
    row.setAttribute("role", "option");
    const impact = step.highImpact ? "high-impact" : "standard";
    row.innerHTML = `<span class="choice-title">${step.title}</span><span class="choice-meta">demo · ${impact}</span>`;
    row.addEventListener("click", () => selectOrderFlowStep(step.id));
    host.appendChild(row);
  }
}

function selectOrderFlowStep(stepId) {
  state.selectedOrderFlowId = stepId;
  const step = DEMO_ORDER_FLOW.find((item) => item.id === stepId);
  if (!step) {
    return;
  }
  document.querySelectorAll("#orderFlowQueue .choice-row").forEach((row) => {
    row.classList.toggle("is-selected", row.dataset.orderFlowId === stepId);
  });
  setEnabled("btnOrderFlowHandoff", true);
  if ($("orderFlowView")) {
    $("orderFlowView").textContent = JSON.stringify(
      {
        id: step.id,
        title: step.title,
        body: step.body,
        action: step.action,
        resource_ref: step.resourceRef,
        high_impact: step.highImpact,
        knowledge_refs: step.knowledgeRefs,
        surface: "ops.order",
        mode: "terminal_demo_handoff",
      },
      null,
      2,
    );
  }
}

async function handoffSelectedOrderFlow() {
  const step = DEMO_ORDER_FLOW.find((item) => item.id === state.selectedOrderFlowId);
  if (!step) {
    throw new Error("Select an order flow step first");
  }
  let action = step.action;
  let resourceRef = step.resourceRef;
  let highImpact = step.highImpact;
  let source = "demo_fixture";
  try {
    const resolved = await api(
      "POST",
      TERMINAL_PATHS.packageActionResolve,
      { action_key: step.action },
      { auth: true, platform: false },
    );
    action = resolved.action_key || step.action;
    resourceRef = `package:${resolved.package_key || "noventi.sample.ops"}:ops.order:${step.id}`;
    highImpact = Boolean(resolved.high_impact);
    source = resolved.source || "package_manifest";
  } catch (err) {
    log("Order flow resolve denied — handoff blocked (fail-closed)", {
      message: String(err.message || err),
      action: step.action,
    });
    throw err;
  }
  handoffToOperator({
    intentText: `[订单演示] ${step.title}: ${step.body}`,
    action,
    resourceRef,
    impactSummary: `Order demo · ${step.id} · source=${source} · refs=${(step.knowledgeRefs || []).join(",")}`,
    highImpact,
  });
  log("Order flow handoff", { step: step.id, action, source, highImpact });
}

function surfaceFromHash() {
  const raw = (location.hash || "").replace(/^#/, "").trim().toLowerCase();
  if (SURFACES.includes(raw)) {
    return raw;
  }
  return "operator";
}

function trustedHeaders({
  platform = false,
  subjectType = "human",
  subjectId: subjectIdOverride = null,
} = {}) {
  const correlationId = $("correlationId").value.trim() || crypto.randomUUID();
  if (!$("correlationId").value.trim()) {
    $("correlationId").value = correlationId;
  }
  if (state.accessToken) {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${state.accessToken}`,
      "X-Correlation-Id": correlationId,
    };
  }
  const subjectId = (subjectIdOverride || $("subjectId").value).trim();
  if (!subjectId || !correlationId) {
    throw new Error("Subject and Correlation are required as trusted headers");
  }
  const resolvedType = subjectType.trim() || "human";
  if (platform) {
    // Platform control-plane: no tenant_id (BOOK23 / no elevation via body or tenant header).
    return {
      "Content-Type": "application/json",
      "X-EAOS-Subject-Id": subjectId,
      "X-EAOS-Subject-Type": resolvedType,
      "X-Correlation-Id": correlationId,
    };
  }
  const tenantId = $("tenantId").value.trim();
  if (!tenantId) {
    throw new Error("Subject, Tenant and Correlation are required as trusted headers");
  }
  return {
    "Content-Type": "application/json",
    "X-EAOS-Subject-Id": subjectId,
    "X-EAOS-Subject-Type": resolvedType,
    "X-EAOS-Tenant-Id": tenantId,
    "X-Correlation-Id": correlationId,
  };
}

function applyOidcFragment() {
  const raw = window.location.hash.replace(/^#/, "");
  if (!raw) {
    const stored = sessionStorage.getItem("eaos_access_token");
    if (stored) {
      state.accessToken = stored;
    }
    updateAuthHint();
    return;
  }
  const params = new URLSearchParams(raw);
  const token = params.get("access_token");
  if (token) {
    state.accessToken = token;
    sessionStorage.setItem("eaos_access_token", token);
    const subject = params.get("subject_id");
    const tenant = params.get("tenant_id");
    if (subject) {
      $("subjectId").value = subject;
    }
    if (tenant) {
      $("tenantId").value = tenant;
    }
    history.replaceState(null, "", window.location.pathname + window.location.search);
    log("OIDC Bearer applied from callback");
  }
  updateAuthHint();
}

async function oidcRefreshBearer() {
  if (!state.accessToken) {
    throw new Error("OIDC Bearer required for refresh");
  }
  const response = await fetch(TERMINAL_PATHS.oidcRefresh, {
    method: "POST",
    headers: { Authorization: `Bearer ${state.accessToken}` },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      (payload.detail && payload.detail.message) || `Refresh failed (${response.status})`
    );
  }
  const token = payload.data && payload.data.access_token;
  if (!token) {
    throw new Error("Refresh response missing access_token");
  }
  state.accessToken = token;
  try {
    sessionStorage.setItem("eaos_access_token", token);
  } catch (_err) {
    /* ignore */
  }
  updateAuthHint();
  log("OIDC Bearer refreshed");
}

async function oidcLogoutBearer() {
  if (!state.accessToken) {
    throw new Error("OIDC Bearer required for logout");
  }
  const response = await fetch(TERMINAL_PATHS.oidcLogout, {
    method: "POST",
    headers: { Authorization: `Bearer ${state.accessToken}` },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      (payload.detail && payload.detail.message) || `Logout failed (${response.status})`
    );
  }
  const endSession = payload.data && payload.data.end_session_url;
  clearBearer();
  log("OIDC logout complete", payload.data || {});
  if (endSession) {
    window.location.href = endSession;
  }
}

function clearBearer() {
  state.accessToken = null;
  sessionStorage.removeItem("eaos_access_token");
  updateAuthHint();
  log("Bearer cleared; using development headers if provided");
}

function updateAuthHint() {
  const hint = $("authHint");
  if (!hint) {
    return;
  }
  hint.textContent = state.accessToken
    ? "Using OIDC Bearer for Gateway calls."
    : "Prefer OIDC Bearer; otherwise fill development trusted headers. Body elevation fields forbidden.";
}

async function loadOidcProviderLinks() {
  const host = $("oidcProviderLinks");
  if (!host) {
    return;
  }
  try {
    const response = await fetch(TERMINAL_PATHS.oidcProviders);
    if (!response.ok) {
      return;
    }
    const payload = await response.json();
    const providers = (payload.data && payload.data.providers) || [];
    host.replaceChildren();
    if (!providers.length) {
      host.hidden = true;
      return;
    }
    for (const item of providers) {
      if (!item || !item.key) {
        continue;
      }
      const link = document.createElement("a");
      link.className = "text-link";
      link.href = `/v1/auth/oidc/login?provider=${encodeURIComponent(item.key)}`;
      link.textContent = `OIDC (${item.key})`;
      host.appendChild(link);
    }
    host.hidden = host.childElementCount === 0;
  } catch (_err) {
    host.hidden = true;
  }
}

async function loadOidcMfaEnrollmentLink() {
  const row = $("oidcMfaEnrollmentRow");
  if (!row) {
    return;
  }
  try {
    const response = await fetch(TERMINAL_PATHS.oidcStatus);
    if (!response.ok) {
      row.hidden = true;
      return;
    }
    const payload = await response.json();
    const enabled = Boolean(payload.data && payload.data.mfa_enrollment_enabled);
    row.hidden = !enabled;
  } catch (_err) {
    row.hidden = true;
  }
}

async function loadOidcLoginProductPosture() {
  const row = $("oidcLoginProductRow");
  const label = $("oidcLoginProductPosture");
  if (!row || !label) {
    return;
  }
  try {
    const response = await fetch(TERMINAL_PATHS.oidcStatus);
    if (!response.ok) {
      label.textContent =
        "OIDC Login Product: authorization_code_enabled=false (status unavailable; fail-closed when unconfigured)";
      return;
    }
    const payload = await response.json();
    const data = payload.data || {};
    const product = data.oidc_login_product || {};
    const enabled = Boolean(
      product.authorization_code_enabled ?? data.enabled,
    );
    const failClosed = Boolean(
      product.fail_closed ?? !enabled,
    );
    label.textContent = `OIDC Login Product: authorization_code_enabled=${enabled} (fail_closed=${failClosed}; Auth Code G40/G61/G132; fail-closed when unconfigured)`;
  } catch (_err) {
    label.textContent =
      "OIDC Login Product: authorization_code_enabled=false (status unavailable; fail-closed when unconfigured)";
  }
}

async function loadWebauthnProductPosture() {
  const row = $("webauthnProductRow");
  const label = $("webauthnProductPosture");
  const enrollLink = $("btnWebauthnMfaEnrollment");
  if (!row || !label) {
    return;
  }
  try {
    const response = await fetch(TERMINAL_PATHS.oidcStatus);
    if (!response.ok) {
      label.textContent =
        "MFA / WebAuthn product: webauthn_registration_enabled=false (status unavailable)";
      if (enrollLink) {
        enrollLink.hidden = true;
      }
      return;
    }
    const payload = await response.json();
    const data = payload.data || {};
    const product = data.webauthn_product || {};
    const regEnabled = Boolean(product.webauthn_registration_enabled);
    const mintReady = Boolean(product.webauthn_live_mint_ready);
    const attestationCrypto = Boolean(product.attestation_crypto_verified);
    const mfaEnabled = Boolean(
      product.mfa_enrollment_enabled ?? data.mfa_enrollment_enabled,
    );
    const stubRoutes = Array.isArray(product.registration_routes)
      ? product.registration_routes.length
      : 0;
    const mintNote = mintReady
      ? "challenge-bound live mint ready G160; attestation_crypto still deferred"
      : regEnabled
        ? "env on but RP_ID/ORIGIN required for live mint G160"
        : "default 503; env EAOS_WEBAUTHN_REGISTRATION_ENABLED + RP for live mint G160";
    label.textContent = `MFA / WebAuthn product: webauthn_registration_enabled=${regEnabled} (${mintNote}; attestation_crypto_verified=${attestationCrypto}; registration_routes=${stubRoutes}; IdP enrollment remains available)`;
    if (enrollLink) {
      enrollLink.hidden = !mfaEnabled;
      enrollLink.href = TERMINAL_PATHS.oidcMfaEnrollment;
    }
  } catch (_err) {
    label.textContent =
      "MFA / WebAuthn product: webauthn_registration_enabled=false (status unavailable)";
    if (enrollLink) {
      enrollLink.hidden = true;
    }
  }
}

async function loadRoleGrantProductPosture() {
  const row = $("roleGrantProductRow");
  const label = $("roleGrantProductPosture");
  if (!row || !label) {
    return;
  }
  try {
    const payload = await api("GET", TERMINAL_PATHS.rolesStatus, undefined, {
      auth: true,
      platform: false,
    });
    const data = payload?.data || {};
    const product = data.role_grant_product || {};
    const autoEnabled = Boolean(product.auto_grant_from_role_enabled);
    const mintReady = Boolean(product.role_grant_live_mint_ready);
    const stubRoutes = Array.isArray(product.auto_write_routes)
      ? product.auto_write_routes.join(",")
      : "";
    label.textContent = `Role→grant product: auto_grant_from_role_enabled=${autoEnabled}; live_mint_ready=${mintReady} (routes=${stubRoutes}; env EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED; Cap≠grant; manual G128/G129; evaluate-only G83)`;
  } catch (_err) {
    label.textContent =
      "Role→grant product: auto_grant_from_role_enabled=false (status unavailable; default 503; env EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED for live mint G161; Cap≠grant; manual G128/G129; evaluate-only G83)";
  }
}

function setRoleCatalogAdminStatus(text) {
  const node = $("roleCatalogAdminStatus");
  if (node) {
    node.textContent = text;
  }
}

/** Role catalog status strip — source_counts + Cap≠grant fences (PHX-G201). */
async function loadRoleCatalogStatus({ quiet = false } = {}) {
  const label = $("roleCatalogStatusPosture");
  try {
    const payload = await api("GET", TERMINAL_PATHS.rolesStatus, undefined, {
      auth: true,
      platform: false,
    });
    const data = payload?.data || {};
    const counts = data.source_counts || {};
    const product = data.role_grant_product || {};
    const summary =
      `Role catalog: store=${data.catalog_store}; enabled=${data.catalog_enabled}; ` +
      `roles=${data.role_count}; grant_map=${data.grant_map_enabled}; ` +
      `sources={catalog:${counts.catalog ?? 0},oidc_map:${counts.oidc_map ?? 0},grant_map:${counts.grant_map ?? 0}}; ` +
      `auto_grant=${Boolean(product.auto_grant_from_role_enabled)}; ` +
      `mint_ready=${Boolean(product.role_grant_live_mint_ready)} ` +
      `(Cap≠grant; title≠permission; PHX-G201)`;
    if (label) {
      label.textContent = summary;
    }
    setRoleCatalogAdminStatus(summary);
    if (!quiet) {
      showJson("adminView", data);
      log("Role catalog status (PHX-G201)", data);
    }
    return true;
  } catch (_err) {
    const msg =
      "Role catalog: unavailable (Cap≠grant; source_counts deferred; G195/G201)";
    if (label) {
      label.textContent = msg;
    }
    setRoleCatalogAdminStatus(msg);
    return false;
  }
}

/** Sample knowledge pack discoverability (PHX-G293; docs-only; ≠ CRUD). */
async function loadSampleKnowledgePackProductPosture({ quiet = false } = {}) {
  const row = $("sampleKnowledgePackProductRow");
  const label = $("sampleKnowledgePackProductPosture");
  const admin = $("sampleKnowledgePackAdminStatus");
  const link = $("sampleKnowledgePackLink");
  if (!row || !label) {
    return false;
  }
  try {
    const response = await fetch(TERMINAL_PATHS.adapters, {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      const msg = "Sample pack: unavailable (G293 discoverability via /v1/adapters)";
      label.textContent = msg;
      if (admin) {
        admin.textContent = msg;
      }
      return false;
    }
    const payload = await response.json();
    const product = payload?.meta?.sample_knowledge_pack_product || {};
    const milestone = product.milestone || "—";
    const packPath = product.pack_path || "—";
    const assembles = Array.isArray(product.assembles)
      ? product.assembles.join("+")
      : "—";
    const crud = product.crud === false ? "false" : String(product.crud ?? "—");
    const msg = `Sample pack: ${milestone} · path=${packPath} · assembles=${assembles} · crud=${crud} · Brain/Twin fail-closed`;
    label.textContent = msg;
    if (admin) {
      admin.textContent = msg;
    }
    if (link && Array.isArray(product.discovery_routes)) {
      const demoRoute = product.discovery_routes.find((r) =>
        String(r).includes("/demo/sample-pack"),
      );
      if (demoRoute) {
        link.href = `${demoRoute.replace(/\/?$/, "/")}INDEX.md`;
      }
    }
    if (!quiet) {
      showJson("adminView", { sample_knowledge_pack_product: product });
      log("Sample knowledge pack posture", product);
    }
    return true;
  } catch (err) {
    const msg = `Sample pack: error (${String(err.message || err)})`;
    label.textContent = msg;
    if (admin) {
      admin.textContent = msg;
    }
    return false;
  }
}

/** OpenAPI inventory posture strip (PHX-G184 → … → PHX-G289). */
async function loadOpenapiInventoryProductPosture({ quiet = false } = {}) {
  const row = $("openapiInventoryProductRow");
  const label = $("openapiInventoryProductPosture");
  const admin = $("openapiInventoryAdminStatus");
  if (!row || !label) {
    return false;
  }
  try {
    const response = await fetch(TERMINAL_PATHS.adapters, {
      headers: {
        Accept: "application/json",
      },
    });
    if (!response.ok) {
      const msg =
        "OpenAPI Inventory: unavailable (mount parity complete; semantic parity still deferred; G289)";
      label.textContent = msg;
      if (admin) {
        admin.textContent = msg;
      }
      return false;
    }
    const payload = await response.json();
    const meta = payload.meta || {};
    const product = meta.openapi_inventory_product || {};
    const count = product.openapi_contract_count ?? meta.count ?? "—";
    const aligned = Boolean(product.adapter_registry_aligned);
    const complete = Boolean(product.full_openapi_http_complete);
    const mountOk = Boolean(product.route_mount_parity_complete);
    const milestone = product.milestone || "—";
    const t0188 = product.t0188_status || "—";
    const detailsClosed = String(t0188).includes("errorbody_details");
    const fieldsShape = String(t0188).includes("error_details_fields");
    const enumConst = String(t0188).includes("single_enum_const");
    const elevationCode = String(t0188).includes("elevation_details_code");
    const oidcCode = String(t0188).includes("oidc_details_code");
    const hostAcquire = String(t0188).includes("host_acquire_details");
    const mfaEnrollment = String(t0188).includes("oidc_mfa_enrollment");
    const descKey = String(t0188).includes("error_details_description_key");
    const namedRefs = String(t0188).includes("named_details_ref_composition");
    const crossElev = String(t0188).includes("cross_domain_elevation_details_ref");
    const stubConst = String(t0188).includes("stub_detail_const");
    const namedEnvelopes = String(t0188).includes("named_success_envelopes");
    const hostPayload = String(t0188).includes("host_acquire_payload_named");
    const nestedPayload = String(t0188).includes("nested_data_payload_named");
    const fedMatrix = String(t0188).includes("federation_matrix_payload_named");
    const nestedGe2 = String(t0188).includes("nested_anon_ge2_payload_named");
    const countMeta = String(t0188).includes("count_meta_and_oidc_providers_payload_named");
    const opaqueAuth = String(t0188).includes("opaque_auth_array_items_named");
    const discoveryWrite = String(t0188).includes("discovery_registry_write_posture_named");
    const webauthnPk = String(t0188).includes("webauthn_public_key_creation_options_named");
    const webauthnVerify = String(t0188).includes("webauthn_register_verify_response_closed");
    const amrAcrClosed = String(t0188).includes("oidc_amr_acr_details_closed");
    const jwksDoc = String(t0188).includes("idp_jwks_document_named");
    const webauthnDeny = String(t0188).includes("webauthn_verify_denial");
    const roleNoMatch = String(t0188).includes("role_grant_no_match_denial");
    const payStubErr = String(t0188).includes("payment_clearing_stub_error_envelope");
    const paySuccess = String(t0188).includes("payment_clearing_success_schemas_closed");
    const uuidClosed = String(t0188).includes("uuid_boolean_ok_result_schemas_closed");
    const mktWrite = String(t0188).includes("marketplace_write_listing_schemas_closed");
    const orgEnt = String(t0188).includes("organization_entity_schemas_closed");
    const pkgSch = String(t0188).includes("package_manifest_schemas_closed");
    const termSch = String(t0188).includes("terminal_session_schemas_closed");
    const aiEnt = String(t0188).includes("ai_agent_memory_schemas_closed");
    const evtEnt = String(t0188).includes("event_envelope_dead_letter_schemas_closed");
    const knowEnt = String(t0188).includes("knowledge_entity_provenance_schemas_closed");
    const brainTwin = String(t0188).includes("brain_twin_schemas_closed");
    const opsParity = String(t0188).includes("ops_milestone_const_parity");
    const soft2 = String(t0188).includes("contract_softener_wave2");
    const soft3 = String(t0188).includes("contract_softener_wave3_tip_parity_guard");
    const soft4 = String(t0188).includes("contract_softener_wave4");
    const soft5 = String(t0188).includes("contract_softener_wave5");
    const soft6 = String(t0188).includes("contract_softener_wave6");
    const errOuter = String(t0188).includes("errorbody_outer_closed");
    const outerGuard = String(t0188).includes("outer_close_regression_guard");
    const summary =
      `OpenAPI Inventory ${milestone}: contracts=${count} · registry_aligned=${aligned} · ` +
      `mount_parity=${mountOk} · full_http_complete=${complete} · t0188=${t0188}` +
      (detailsClosed ? " · ErrorBody.details inventory closed (G202/G203)" : "") +
      (fieldsShape
        ? " · details.fields[] known-shape honest (G204/G205)"
        : "") +
      (enumConst ? " · single-enum const honest (G206/G207)" : "") +
      (elevationCode
        ? " · elevation details per-code honest (G208/G209)"
        : "") +
      (oidcCode ? " · OIDC details per-code honest (G210/G211)" : "") +
      (hostAcquire
        ? " · host-acquire details per-code honest (G212/G213)"
        : "") +
      (mfaEnrollment
        ? " · OIDC MFA enrollment details honest (G214/G215)"
        : "") +
      (descKey
        ? " · ErrorResponse.details description-key honest (G216/G217)"
        : "") +
      (namedRefs
        ? " · named Details $ref composition honest (G218/G219)"
        : "") +
      (crossElev
        ? " · cross-domain elevation details $ref honest (G220/G221)"
        : "") +
      (stubConst ? " · stub detail const honest (G222/G223)" : "") +
      (namedEnvelopes
        ? " · named success envelopes honest (G224/G225)"
        : "") +
      (hostPayload
        ? " · HostAcquirePayload named honest (G226/G227)"
        : "") +
      (nestedPayload
        ? " · nested data payload named honest (G228/G229)"
        : "") +
      (fedMatrix
        ? " · federation matrix payload named honest (G230/G231)"
        : "") +
      (nestedGe2
        ? " · nested-anon≥2 payload named honest (G232/G233)"
        : "") +
      (countMeta
        ? " · CountMeta/OidcProvidersPayload named honest (G234/G235)"
        : "") +
      (opaqueAuth
        ? " · opaque auth array-item named honest (G236/G237)"
        : "") +
      (discoveryWrite
        ? " · DiscoveryRegistryWritePosture named honest (G238/G239)"
        : "") +
      (webauthnPk
        ? " · PublicKeyCredentialCreationOptions named honest (G240/G241)"
        : "") +
      (webauthnVerify
        ? " · WebAuthn RegisterVerifyResponse closed (G242/G243)"
        : "") +
      (amrAcrClosed
        ? " · OIDC Amr/Acr details closed (G244/G245)"
        : "") +
      (jwksDoc
        ? " · IdP JWKS document named honest (G246/G247)"
        : "") +
      (webauthnDeny
        ? " · WebAuthn verify denial honest (G248/G249)"
        : "") +
      (roleNoMatch
        ? " · RoleGrant no-match denial honest (G250/G251)"
        : "") +
      (payStubErr
        ? " · PaymentClearingStubError envelope honest (G252/G253)"
        : "") +
      (paySuccess
        ? " · PaymentClearing success schemas closed (G254/G255)"
        : "") +
      (uuidClosed
        ? " · UuidResult/BooleanResult/OkResponse closed (G256/G257)"
        : "") +
      (mktWrite
        ? " · Marketplace write/listing schemas closed (G258/G259)"
        : "") +
      (orgEnt
        ? " · Organization entity schemas closed (G260/G261)"
        : "") +
      (pkgSch
        ? " · Package manifest schemas closed (G262/G263)"
        : "") +
      (termSch
        ? " · Terminal session schemas closed (G264/G265)"
        : "") +
      (aiEnt
        ? " · AI AgentRun/MemoryEntry schemas closed (G266/G267)"
        : "") +
      (evtEnt
        ? " · Event envelope/dead-letter schemas closed (G268/G269)"
        : "") +
      (knowEnt
        ? " · Knowledge entity/provenance schemas closed (G270/G271)"
        : "") +
      (brainTwin
        ? " · Brain/Twin outer schemas closed (G272/G273)"
        : "") +
      (opsParity
        ? " · Ops milestone const parity + contract softener (G274/G275)"
        : "") +
      (soft2
        ? " · Contract softener wave2 (G276/G277)"
        : "") +
      (soft3
        ? " · Contract softener wave3 + tip-parity guard (G278/G279)"
        : "") +
      (soft4
        ? " · Contract softener wave4 (G280/G281)"
        : "") +
      (soft5
        ? " · Contract softener wave5 (G282/G283)"
        : "") +
      (soft6
        ? " · Contract softener wave6 (G284/G285)"
        : "") +
      (errOuter
        ? " · ErrorBody outer closed (G286/G287)"
        : "") +
      (outerGuard
        ? " · Outer-close regression guard (G288/G289)"
        : "") +
      " (semantic remainder deferred)";
    label.textContent = summary;
    if (admin) {
      admin.textContent = summary;
    }
    if (!quiet) {
      showJson("adminView", product);
      log("OpenAPI inventory posture (PHX-G289)", {
        milestone,
        t0188_status: t0188,
        openapi_contract_count: count,
        full_openapi_http_complete: complete,
        errorbody_details_closed: detailsClosed,
        error_details_fields_shape_honest: fieldsShape,
        single_enum_const_honest: enumConst,
        elevation_details_code_shape_honest: elevationCode,
        oidc_details_code_shapes_honest: oidcCode,
        host_acquire_details_code_shape_honest: hostAcquire,
        oidc_mfa_enrollment_details_honest: mfaEnrollment,
        error_details_description_key_honest: descKey,
        named_details_ref_composition_honest: namedRefs,
        cross_domain_elevation_details_ref_honest: crossElev,
        stub_detail_const_honest: stubConst,
        named_success_envelopes_honest: namedEnvelopes,
        host_acquire_payload_named_honest: hostPayload,
        nested_data_payload_named_honest: nestedPayload,
        federation_matrix_payload_named_honest: fedMatrix,
        nested_anon_ge2_payload_named_honest: nestedGe2,
        count_meta_and_oidc_providers_payload_named_honest: countMeta,
        opaque_auth_array_items_named_honest: opaqueAuth,
        webauthn_public_key_creation_options_named_honest: webauthnPk,
        webauthn_register_verify_response_closed_honest: webauthnVerify,
        oidc_amr_acr_details_closed_honest: amrAcrClosed,
        idp_jwks_document_named_honest: jwksDoc,
        webauthn_verify_denial_honest: webauthnDeny,
        role_grant_no_match_denial_honest: roleNoMatch,
        payment_clearing_stub_error_envelope_honest: payStubErr,
        payment_clearing_success_schemas_closed_honest: paySuccess,
        uuid_boolean_ok_result_schemas_closed_honest: uuidClosed,
        marketplace_write_listing_schemas_closed_honest: mktWrite,
        organization_entity_schemas_closed_honest: orgEnt,
        package_manifest_schemas_closed_honest: pkgSch,
        terminal_session_schemas_closed_honest: termSch,
        ai_agent_memory_schemas_closed_honest: aiEnt,
        event_envelope_dead_letter_schemas_closed_honest: evtEnt,
        knowledge_entity_provenance_schemas_closed_honest: knowEnt,
        brain_twin_schemas_closed_honest: brainTwin,
        ops_milestone_const_parity_honest: opsParity,
        contract_softener_wave2_honest: soft2,
        contract_softener_wave3_tip_parity_guard_honest: soft3,
        contract_softener_wave4_honest: soft4,
        contract_softener_wave5_honest: soft5,
        contract_softener_wave6_honest: soft6,
        errorbody_outer_closed_honest: errOuter,
        outer_close_regression_guard_honest: outerGuard,
        discovery_registry_write_posture_named_honest: discoveryWrite,
      });
    }
    return true;
  } catch (_err) {
    const msg =
      "OpenAPI Inventory: unavailable (mount parity complete; semantic parity still deferred; G289)";
    label.textContent = msg;
    if (admin) {
      admin.textContent = msg;
    }
    return false;
  }
}

export function sanitizeBody(body) {
  const clean = { ...body };
  for (const key of FORBIDDEN_BODY_KEYS) {
    delete clean[key];
  }
  return clean;
}

async function api(
  method,
  path,
  body,
  { auth = true, platform = false, subjectType = "human", subjectId = null } = {},
) {
  const init = {
    method,
    headers: auth
      ? trustedHeaders({ platform, subjectType, subjectId })
      : body !== undefined
        ? { "Content-Type": "application/json" }
        : {},
  };
  if (body !== undefined) {
    init.body = JSON.stringify(sanitizeBody(body));
  }
  const response = await fetch(path, init);
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  if (!response.ok) {
    const code = data?.detail?.code || data?.error?.code || `HTTP_${response.status}`;
    const message = data?.detail?.message || data?.error?.message || response.statusText;
    const error = new Error(`${code}: ${message}`);
    error.code = code;
    error.status = response.status;
    error.details = data?.detail?.details || data?.error?.details || null;
    throw error;
  }
  return data;
}

function uuid() {
  if (crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/** PHX-G171: accept dual-key UuidResult (`id` and/or `data`). */
function uuidFromResult(payload) {
  if (!payload || typeof payload !== "object") {
    return null;
  }
  const value = payload.id || payload.data;
  if (typeof value !== "string" || !value.trim()) {
    return null;
  }
  return value.trim();
}

function seedDefaults() {
  if (!$("subjectId").value) {
    $("subjectId").value = uuid();
  }
  if (!$("tenantId").value) {
    $("tenantId").value = uuid();
  }
  if (!$("correlationId").value) {
    $("correlationId").value = uuid();
  }
  if (!$("approvalSubjectId").value) {
    $("approvalSubjectId").value = $("subjectId").value;
  }
}

function showJson(id, value) {
  $(id).textContent = JSON.stringify(value, null, 2);
}

async function openSession() {
  seedDefaults();
  const data = await api("POST", TERMINAL_PATHS.sessions, { device_trust: "trusted" });
  state.sessionId = uuidFromResult(data);
  state.intentId = null;
  state.previewId = null;
  state.receipt = null;
  state.approval = null;
  $("receiptView").textContent = "No receipt yet.";
  $("approvalView").textContent = "No approval presentation yet.";
  setStep("intent");
  syncButtons();
  log("Session opened", data);
}

async function refreshSession() {
  if (!state.sessionId) {
    throw new Error("Open a session first");
  }
  const data = await api("GET", TERMINAL_PATHS.session(state.sessionId));
  log("Session refreshed", data);
  showJson("receiptView", data);
}

async function closeSession() {
  if (!state.sessionId) {
    throw new Error("Open a session first");
  }
  const data = await api("POST", TERMINAL_PATHS.session(state.sessionId));
  state.sessionId = null;
  state.intentId = null;
  state.previewId = null;
  setStep("session");
  syncButtons();
  log("Session closed", data);
}

async function composeIntent() {
  const text = $("intentText").value.trim();
  if (!state.sessionId || !text) {
    throw new Error("Open a session and enter intent text first");
  }
  const data = await api("POST", TERMINAL_PATHS.intents, {
    terminal_session_id: state.sessionId,
    text,
  });
  state.intentId = uuidFromResult(data);
  state.previewId = null;
  state.receipt = null;
  setStep("preview");
  syncButtons();
  log("Intent composed", data);
}

async function refreshIntent() {
  if (!state.intentId) {
    throw new Error("Compose an intent first");
  }
  const data = await api("GET", TERMINAL_PATHS.intent(state.intentId));
  log("Intent refreshed", data);
  showJson("aiView", data);
}

async function buildPreview() {
  if (!state.intentId) {
    throw new Error("Compose an intent first");
  }
  const data = await api("POST", TERMINAL_PATHS.previews, {
    intent_id: state.intentId,
    action: $("action").value.trim(),
    resource_ref: $("resourceRef").value.trim(),
    plan_version: $("planVersion").value.trim(),
    scope: $("scope").value.trim(),
    impact_summary: $("impactSummary").value.trim(),
    high_impact: $("highImpact").checked,
  });
  state.previewId = uuidFromResult(data);
  state.receipt = null;
  state.approval = null;
  // Server-authoritative high_impact (Package resolve / DAL-U167); never trust checkbox alone.
  const preview = await api("GET", TERMINAL_PATHS.preview(state.previewId));
  const highImpact = Boolean(preview.high_impact);
  if ($("highImpact")) {
    $("highImpact").checked = highImpact;
  }
  setStep(highImpact ? "approval" : "commit");
  syncButtons();
  log("Preview built", { id: state.previewId, high_impact: highImpact, preview });
}

async function refreshPreview() {
  if (!state.previewId) {
    throw new Error("Build a preview first");
  }
  const data = await api("GET", TERMINAL_PATHS.preview(state.previewId));
  log("Preview refreshed", data);
  showJson("receiptView", data);
}

async function requestApproval() {
  if (!state.previewId) {
    throw new Error("Build a preview first");
  }
  const definitionId = $("definitionId").value.trim();
  const approvalSubjectId = $("approvalSubjectId").value.trim();
  if (!definitionId || !approvalSubjectId) {
    throw new Error("Definition ID and Approver subject are required");
  }
  const data = await api("POST", TERMINAL_PATHS.approvals(state.previewId), {
    definition_id: definitionId,
    approval_subject_id: approvalSubjectId,
  });
  setStep("approval");
  log("Approval requested", data);
  switchSurface("approval");
}

async function presentApproval() {
  if (!state.previewId) {
    throw new Error("Build a preview first");
  }
  const data = await api("GET", TERMINAL_PATHS.approvals(state.previewId));
  state.approval = data;
  showJson("approvalView", data);
  setStep("approval");
  log("Approval presented", data);
}

async function commitPreview() {
  if (!state.previewId) {
    throw new Error("Build a preview first");
  }
  const data = await api("POST", TERMINAL_PATHS.commit(state.previewId));
  state.receipt = data;
  showJson("receiptView", data);
  setStep("receipt");
  log("Commit receipt", data);
}

async function adminProbe(path, label) {
  const needsAuth = path === TERMINAL_PATHS.context;
  const data = await api("GET", path, undefined, { auth: needsAuth });
  showJson("adminView", data);
  log(label, data);
}

async function adminContextEchoElevationReject() {
  const response = await fetch(TERMINAL_PATHS.contextEcho, {
    method: "POST",
    headers: trustedHeaders({ platform: false }),
    body: JSON.stringify({
      tenant_id: "should-reject",
      subject_id: "should-reject",
      platform_scope: true,
      note: "g140-ops-echo",
    }),
  });
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  const view = {
    ok: response.ok,
    status: response.status,
    expected_elevation_reject: true,
    data,
  };
  showJson("adminView", view);
  log("Context echo probed (elevation reject)", view);
  if (response.status !== 400) {
    throw new Error(
      `Expected elevation-reject 400, got HTTP_${response.status}`,
    );
  }
}

function parseOptionalJwksJson(raw) {
  const text = (raw || "").trim();
  if (!text) {
    return undefined;
  }
  try {
    return JSON.parse(text);
  } catch (_err) {
    throw new Error("JWKS JSON must be valid JSON object/array");
  }
}

async function adminListIdpIssuers() {
  const data = await api("GET", TERMINAL_PATHS.idpIssuers, undefined, {
    auth: true,
    platform: true,
  });
  const first = Array.isArray(data.data) && data.data[0] ? data.data[0] : null;
  if (first && first.id && $("idpIssuerId")) {
    $("idpIssuerId").value = first.id;
  }
  showJson("adminView", data);
  log("IdP issuers listed", data);
}

async function adminRegisterIdpIssuer() {
  const issuer = $("idpIssuer").value.trim();
  const jwksUrl = $("idpJwksUrl").value.trim();
  const jwksJson = parseOptionalJwksJson($("idpJwksJson").value);
  if (!issuer) {
    throw new Error("Issuer URL is required");
  }
  if (!jwksUrl && jwksJson === undefined) {
    throw new Error("JWKS URL or JWKS JSON is required");
  }
  const body = { issuer };
  if (jwksUrl) {
    body.jwks_url = jwksUrl;
  }
  if (jwksJson !== undefined) {
    body.jwks_json = jwksJson;
  }
  const data = await api("POST", TERMINAL_PATHS.idpIssuers, body, {
    auth: true,
    platform: true,
  });
  if (data.data && data.data.id && $("idpIssuerId")) {
    $("idpIssuerId").value = data.data.id;
  }
  showJson("adminView", data);
  log("IdP issuer registered", data);
}

async function adminDisableIdpIssuer() {
  const issuerId = $("idpIssuerId").value.trim();
  if (!issuerId) {
    throw new Error("Issuer id is required (list issuers first)");
  }
  const data = await api("POST", TERMINAL_PATHS.idpIssuerDisable(issuerId), {}, {
    auth: true,
    platform: true,
  });
  showJson("adminView", data);
  log("IdP issuer disabled", data);
}

async function adminDiscoverySync() {
  const data = await api("POST", TERMINAL_PATHS.idpDiscoverySync, {}, {
    auth: true,
    platform: true,
  });
  showJson("adminView", data);
  log("Discovery sync", data);
}

async function adminListTenantRolesCatalog() {
  const data = await api("GET", TERMINAL_PATHS.tenantRoles, undefined, {
    auth: true,
    platform: false,
  });
  showJson("adminView", data);
  log("Tenant roles catalog listed", data);
}

async function adminRolesStatus() {
  const data = await api("GET", TERMINAL_PATHS.rolesStatus, undefined, {
    auth: true,
    platform: false,
  });
  showJson("adminView", data);
  log("Roles status", data);
}

async function adminEvaluatePermission() {
  const resourceType = $("evalResourceType").value.trim();
  const action = $("evalAction").value.trim();
  if (!resourceType || !action) {
    throw new Error("Evaluate resource type and action are required");
  }
  const body = {
    resource_type: resourceType,
    action,
  };
  const resourceId = $("evalResourceId").value.trim();
  if (resourceId) {
    body.resource_id = resourceId;
  }
  const data = await api("POST", TERMINAL_PATHS.evaluations, body, {
    auth: true,
    platform: false,
  });
  if (data.decision_id && $("evalDecisionId")) {
    $("evalDecisionId").value = data.decision_id;
  }
  showJson("adminView", data);
  log("Permission evaluated", data);
}

async function adminExplainLastDecision() {
  const decisionId = $("evalDecisionId").value.trim();
  if (!decisionId) {
    throw new Error("Decision id is required (evaluate first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.decisionExplanation(decisionId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Decision explained", data);
}

async function adminListEffectivePermissions() {
  let principalId = $("effectivePrincipalId").value.trim();
  if (!principalId) {
    principalId = $("subjectId").value.trim();
  }
  if (!principalId) {
    throw new Error("Effective principal subject id is required (or set Subject)");
  }
  if ($("effectivePrincipalId") && !$("effectivePrincipalId").value.trim()) {
    $("effectivePrincipalId").value = principalId;
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.effectivePermissions(principalId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Effective permissions listed", data);
}

async function adminCreatePermissionPolicy() {
  const name = $("permPolicyName").value.trim();
  const effect = $("permPolicyEffect").value.trim();
  const resourceType = $("evalResourceType").value.trim();
  const actionsRaw = $("evalAction").value.trim();
  const scopeLevel = $("permScopeLevel").value.trim() || "tenant";
  if (!name || !effect || !resourceType || !actionsRaw) {
    throw new Error(
      "Permission policy name, effect, resource type and action(s) are required",
    );
  }
  const actions = actionsRaw.split(",").map((item) => item.trim()).filter(Boolean);
  if (!actions.length) {
    throw new Error("Permission policy actions are required");
  }
  const body = {
    name,
    policy_version: $("permPolicyVersion").value.trim() || "1",
    rules: [
      {
        effect,
        resource_type: resourceType,
        actions,
        scope_level: scopeLevel,
      },
    ],
  };
  const data = await api("POST", TERMINAL_PATHS.permissionPolicies, body, {
    auth: true,
    platform: false,
  });
  if (data.id && $("permPolicyId")) {
    $("permPolicyId").value = data.id;
  }
  showJson("adminView", data);
  log("Permission policy created", data);
}

async function adminActivatePermissionPolicy() {
  const policyId = $("permPolicyId").value.trim();
  if (!policyId) {
    throw new Error("Permission policy id is required (create first)");
  }
  const body = {};
  const versionRaw = $("permExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Permission expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.permissionPolicyActivation(policyId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Permission policy activated", data);
}

async function adminCreatePermissionGrant() {
  let principalId = $("effectivePrincipalId").value.trim();
  if (!principalId) {
    principalId = $("subjectId").value.trim();
  }
  const resourceType = $("evalResourceType").value.trim();
  const actionsRaw = $("evalAction").value.trim();
  const scopeLevel = $("permScopeLevel").value.trim() || "tenant";
  if (!principalId || !resourceType || !actionsRaw) {
    throw new Error(
      "Grant principal, resource type and action(s) are required",
    );
  }
  const actions = actionsRaw.split(",").map((item) => item.trim()).filter(Boolean);
  if (!actions.length) {
    throw new Error("Grant actions are required");
  }
  if ($("effectivePrincipalId") && !$("effectivePrincipalId").value.trim()) {
    $("effectivePrincipalId").value = principalId;
  }
  const body = {
    principal_id: principalId,
    resource_type: resourceType,
    actions,
    scope_level: scopeLevel,
  };
  const resourceId = $("evalResourceId").value.trim();
  if (resourceId) {
    body.resource_id = resourceId;
  }
  const delegableRaw = $("permGrantDelegable").value.trim().toLowerCase();
  if (delegableRaw === "true" || delegableRaw === "1" || delegableRaw === "yes") {
    body.delegable = true;
  }
  const depthRaw = $("permGrantDelegationDepth").value.trim();
  if (depthRaw) {
    const depth = Number(depthRaw);
    if (Number.isNaN(depth)) {
      throw new Error("Permission grant delegation_depth must be a number");
    }
    body.delegation_depth = depth;
  }
  const data = await api("POST", TERMINAL_PATHS.permissionGrants, body, {
    auth: true,
    platform: false,
  });
  if (data.id && $("permGrantId")) {
    $("permGrantId").value = data.id;
  }
  showJson("adminView", data);
  log("Permission grant created", data);
}

async function adminRevokePermissionGrant() {
  const grantId = $("permGrantId").value.trim();
  const reason = $("permRevokeReason").value.trim();
  if (!grantId || !reason) {
    throw new Error("Permission grant id and revoke reason are required");
  }
  const body = { reason };
  const versionRaw = $("permExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Permission expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.permissionGrantRevocation(grantId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Permission grant revoked", data);
}

async function adminDeprecatePermissionPolicy() {
  const policyId = $("permPolicyId").value.trim();
  const reason = $("permRevokeReason").value.trim();
  if (!policyId || !reason) {
    throw new Error("Permission policy id and reason are required");
  }
  const body = { reason };
  const versionRaw = $("permExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Permission expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.permissionPolicyDeprecation(policyId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Permission policy deprecated", data);
}

async function adminDelegatePermissionGrant() {
  const grantId = $("permGrantId").value.trim();
  const delegateeId = $("permDelegateePrincipalId").value.trim();
  const actionsRaw = $("evalAction").value.trim();
  const scopeLevel = $("permScopeLevel").value.trim() || "tenant";
  const versionRaw = $("permExpectedVersion").value.trim();
  if (!grantId || !delegateeId || !actionsRaw || !versionRaw) {
    throw new Error(
      "Parent grant id, delegatee, action(s) and expected_version are required",
    );
  }
  const actions = actionsRaw.split(",").map((item) => item.trim()).filter(Boolean);
  if (!actions.length) {
    throw new Error("Delegated actions are required");
  }
  const expectedVersion = Number(versionRaw);
  if (Number.isNaN(expectedVersion)) {
    throw new Error("Permission expected_version must be a number");
  }
  const body = {
    delegatee_principal_id: delegateeId,
    actions,
    scope_level: scopeLevel,
    expected_version: expectedVersion,
  };
  const resourceId = $("evalResourceId").value.trim();
  if (resourceId) {
    body.resource_id = resourceId;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.permissionGrantDelegations(grantId),
    body,
    { auth: true, platform: false },
  );
  if (data.id && $("permGrantId")) {
    $("permGrantId").value = data.id;
  }
  showJson("adminView", data);
  log("Permission grant delegated", data);
}

async function adminEventDeliveryStats() {
  const data = await api("GET", TERMINAL_PATHS.eventStats, undefined, {
    auth: true,
    platform: false,
  });
  showJson("adminView", data);
  log("Event delivery stats", data);
}

async function adminEventCatalog() {
  const data = await api("GET", TERMINAL_PATHS.eventCatalog, undefined, {
    auth: false,
  });
  showJson("adminView", {
    event_catalog: data,
    milestone: "PHX-G386",
  });
  log("Commercial event catalog (PHX-G386)", data);
}

async function adminListDeadLetters() {
  const data = await api("GET", TERMINAL_PATHS.eventDeadLetters, undefined, {
    auth: true,
    platform: false,
  });
  const first =
    data.data && Array.isArray(data.data) && data.data[0] ? data.data[0] : null;
  if (first && first.id && $("deadLetterId")) {
    $("deadLetterId").value = first.id;
  }
  showJson("adminView", data);
  log("Dead letters listed", data);
}

async function adminReplayDeadLetter() {
  const deadLetterId = $("deadLetterId").value.trim();
  if (!deadLetterId) {
    throw new Error("Dead letter id is required (list dead letters first)");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.eventDeadLetterReplay(deadLetterId),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Dead letter replayed", data);
}

async function adminDispatchDueEvents() {
  const workerId = $("eventWorkerId").value.trim();
  if (!workerId) {
    throw new Error("Event worker id is required");
  }
  const body = { worker_id: workerId };
  const limitRaw = $("eventDispatchLimit").value.trim();
  if (limitRaw) {
    const limit = Number(limitRaw);
    if (!Number.isInteger(limit) || limit < 1) {
      throw new Error("Event dispatch limit must be a positive integer");
    }
    body.limit = limit;
  }
  const data = await api("POST", TERMINAL_PATHS.eventDispatch, body, {
    auth: true,
    platform: false,
  });
  showJson("adminView", data);
  log("Due events dispatched", data);
}

async function adminGetEvent() {
  const eventId = $("eventId").value.trim();
  if (!eventId) {
    throw new Error("Event id is required");
  }
  const data = await api("GET", TERMINAL_PATHS.eventById(eventId), undefined, {
    auth: true,
    platform: false,
  });
  showJson("adminView", data);
  log("Event fetched", data);
}

function buildEventProbeBody() {
  const eventName = $("eventName").value.trim();
  const schemaVersion = $("eventSchemaVersion").value.trim();
  const producer = $("eventProducer").value.trim();
  if (!eventName || !schemaVersion || !producer) {
    throw new Error("Event name, schema version and producer are required");
  }
  const raw = $("eventPayloadJson").value.trim();
  let payload = {};
  if (raw) {
    try {
      payload = JSON.parse(raw);
    } catch (_err) {
      throw new Error("Event payload JSON must be a valid JSON object");
    }
    if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("Event payload JSON must be a JSON object");
    }
  }
  return {
    event_name: eventName,
    schema_version: schemaVersion,
    producer,
    payload,
  };
}

async function adminEnqueueOutbox() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.eventOutbox,
    buildEventProbeBody(),
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Event enqueued to outbox", data);
}

async function adminPublishEvent() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.eventPublish,
    buildEventProbeBody(),
    { auth: true, platform: false },
  );
  const eventId =
    data.data && data.data.event_id ? data.data.event_id : undefined;
  if (eventId && $("eventId")) {
    $("eventId").value = eventId;
  }
  showJson("adminView", data);
  log("Event published", data);
}

async function adminSubscribeEvent() {
  const subscriberId = $("eventSubscriberId").value.trim();
  const eventName = $("eventName").value.trim();
  if (!subscriberId || !eventName) {
    throw new Error("Event subscriber id and event name are required");
  }
  const body = {
    subscriber_id: subscriberId,
    event_name: eventName,
  };
  const deliveryUrl = $("eventDeliveryUrl").value.trim();
  if (deliveryUrl) {
    body.delivery_url = deliveryUrl;
  }
  const data = await api("POST", TERMINAL_PATHS.eventSubscriptions, body, {
    auth: true,
    platform: false,
  });
  showJson("adminView", data);
  log("Event subscription created", data);
}

async function adminReplayEvent() {
  const eventId = $("eventId").value.trim();
  if (!eventId) {
    throw new Error("Event id is required (publish or paste id first)");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.eventReplay(eventId),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Event replayed", data);
}

function _csvList(raw) {
  return (raw || "")
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

async function adminCreateListing() {
  const packageKey = $("listingPackageKey").value.trim();
  const packageVersion = $("listingPackageVersion").value.trim();
  const dataScope = $("listingDataScope").value.trim();
  if (!packageKey || !packageVersion || !dataScope) {
    throw new Error("Listing package key, version and data scope are required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListings,
    {
      package_key: packageKey,
      package_version: packageVersion,
      data_scope: dataScope,
      required_permissions: _csvList($("listingRequiredPermissions").value),
      declared_events: _csvList($("listingDeclaredEvents").value),
    },
    { auth: true, platform: false },
  );
  if (data.data && $("listingId")) {
    $("listingId").value = uuidFromResult(data);
  }
  showJson("adminView", data);
  log("Marketplace listing created", data);
}

async function adminGetListing() {
  const listingId = $("listingId").value.trim();
  if (!listingId) {
    throw new Error("Marketplace listing id is required (create first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.marketplaceListing(listingId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Marketplace listing fetched", data);
}

function requireListingId() {
  const listingId = $("listingId").value.trim();
  if (!listingId) {
    throw new Error("Marketplace listing id is required (create first)");
  }
  return listingId;
}

async function adminAttachListingSignature() {
  const listingId = requireListingId();
  const signatureRef = $("listingSignatureRef").value.trim();
  if (!signatureRef) {
    throw new Error("Listing signature ref is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingSignature(listingId),
    { signature_ref: signatureRef },
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing signature attached", data);
}

async function adminSubmitListing() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingSubmit(requireListingId()),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing submitted", data);
}

async function adminReviewApproveListing() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingReview(requireListingId()),
    { approve: true, notes: "terminal-approve" },
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing review approved", data);
}

async function adminPublishListing() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingPublish(requireListingId()),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing published", data);
}

function setHostAcquireStatus(text) {
  const node = $("hostAcquireStatus");
  if (node) {
    node.textContent = text;
  }
}

async function loadHostAcquireStatus({ quiet = false } = {}) {
  const data = await api("GET", TERMINAL_PATHS.marketplaceStatus, undefined, {
    auth: false,
  });
  const product = data?.data?.host_acquire_product || null;
  if (!product) {
    setHostAcquireStatus("Host-acquire posture missing from marketplace status.");
    if (!quiet) {
      showJson("adminView", data);
      log("Host-acquire status missing", data);
    }
    return false;
  }
  const allowlist = Array.isArray(product.allowlist)
    ? product.allowlist.join(", ")
    : "";
  setHostAcquireStatus(
    `Host-acquire ${product.milestone} · mode=${product.mode} · allowlist=[${allowlist}] · scripts=${product.arbitrary_scripts} · install=${product.package_install} · psp=${product.external_psp}`,
  );
  if (!quiet) {
    showJson("adminView", { host_acquire_product: product, status: data.data });
    log("Host-acquire status (PHX-G175)", product);
  }
  return true;
}

function setPaymentClearingStatus(text) {
  const node = $("paymentClearingStatus");
  if (node) {
    node.textContent = text;
  }
}

async function loadPaymentClearingStatus({ quiet = false } = {}) {
  const data = await api("GET", TERMINAL_PATHS.marketplaceStatus, undefined, {
    auth: false,
  });
  const product = data?.data?.payment_clearing_product || null;
  const economy = data?.data || {};
  if (!product) {
    setPaymentClearingStatus(
      "Payment-clearing posture missing from marketplace status.",
    );
    if (!quiet) {
      showJson("adminView", data);
      log("Payment-clearing status missing", data);
    }
    return false;
  }
  setPaymentClearingStatus(
    `Payment-clearing ${product.milestone} · enabled=${product.payment_clearing_enabled} · rail=${product.settlement_rail} · psp=${product.external_psp} · arbitration=${product.external_arbitration} · metering=${product.metering} · economy_reviewed=${economy.economy_residual_reviewed} · host_acquire_not_install=${economy.host_acquire_not_package_install}`,
  );
  if (!quiet) {
    showJson("adminView", {
      payment_clearing_product: product,
      status: data.data,
    });
    log("Payment-clearing status (PHX-G183)", product);
  }
  return true;
}

function setFinancePlatformStatus(text) {
  const node = $("financePlatformStatus");
  if (node) node.textContent = text;
}

async function loadFinancePlatformStatus({ quiet = false } = {}) {
  const probes = [
    ["finance", TERMINAL_PATHS.financeStatus],
    ["digital_employee", TERMINAL_PATHS.platformDigitalEmployeeStatus],
    ["industry_package", TERMINAL_PATHS.platformIndustryPackageStatus],
    ["ai_workforce", TERMINAL_PATHS.platformAiWorkforceStatus],
  ];
  const rows = {};
  const summary = [];
  for (const [name, path] of probes) {
    try {
      const data = await api("GET", path, undefined, { auth: false });
      const body = data?.data || {};
      rows[name] = body;
      if (name === "finance") {
        summary.push(
          `finance.truth=${body.holds_business_truth}`,
          `finance.terminal_truth=${body.terminal_holds_business_truth}`,
          `finance.auto_write=${body.commercial_auto_write}`,
          `commercial.chain_consistent=${body.crm_quote_so_do_state_consistency}`,
          `commercial.commission=${body.commission_settlement_mode}`,
          `supply.po=${body.purchase_order_observability}`,
          `supply.inventory=${body.inventory_movement_observability}`,
        );
      } else {
        summary.push(
          `${name}.exec=${body.execution_authority}`,
          `${name}.auto_write=${body.commercial_auto_write ?? body.labor_write}`,
        );
      }
    } catch (err) {
      rows[name] = { error: String(err.message || err) };
      summary.push(`${name}=error`);
    }
  }
  setFinancePlatformStatus(`Finance/platform strip (PHX-G394) · ${summary.join(" · ")}`);
  if (!quiet) {
    showJson("adminView", { finance_platform_status: rows, milestone: "PHX-G394" });
    log("Finance/platform status strip (PHX-G394)", rows);
  }
  return true;
}

function setEventOutboxStatus(text) {
  const node = $("eventOutboxStatus");
  if (node) node.textContent = text;
}

async function loadEventOutboxStatus({ quiet = false } = {}) {
  const rows = {};
  const summary = [];
  try {
    const status = await api("GET", TERMINAL_PATHS.eventStatus, undefined, {
      auth: false,
    });
    const body = status?.data || {};
    rows.status = body;
    summary.push(
      `daemon=${body.background_worker_daemon}`,
      `dispatch=${body.dispatch_trigger}`,
      `lease_s=${body.default_lease_seconds}`,
      `dlq=${body.dead_letter_list_access}`,
      `fail_closed=${body.fail_closed_without_grant}`,
      `delivery=${body.outbox_delivery_mode}`,
      `audit_read=${body.audit_read_surface}`,
      `multi_region=${body.multi_region_failover}`,
    );
  } catch (err) {
    rows.status = { error: String(err.message || err) };
    summary.push("status=error");
  }
  try {
    const catalog = await api("GET", TERMINAL_PATHS.eventCatalog, undefined, {
      auth: false,
    });
    const body = catalog?.data || {};
    rows.catalog = body;
    summary.push(
      `catalog=${body.catalog_id}`,
      `events=${(body.events || []).length}`,
    );
  } catch (err) {
    rows.catalog = { error: String(err.message || err) };
    summary.push("catalog=error");
  }
  setEventOutboxStatus(`Event/outbox strip (PHX-G395) · ${summary.join(" · ")}`);
  if (!quiet) {
    showJson("adminView", { event_outbox_status: rows, milestone: "PHX-G395" });
    log("Event/outbox status strip (PHX-G395)", rows);
  }
  return true;
}

function setPackageResolveAlignStatus(text) {
  const node = $("packageResolveAlignStatus");
  if (node) node.textContent = text;
}

async function loadPackageResolveAlignStatus({ quiet = false } = {}) {
  const rows = {};
  const summary = [];
  try {
    const status = await api("GET", TERMINAL_PATHS.packageStatus, undefined, {
      auth: false,
    });
    const body = status?.data || {};
    rows.package_status = body;
    summary.push(
      `resolve=${body.action_resolve_surface}`,
      `surfaces=${body.surface_list_surface}`,
      `aligned=${body.terminal_resolve_aligned}`,
      `terminal_truth=${body.terminal_holds_business_truth}`,
    );
  } catch (err) {
    rows.package_status = { error: String(err.message || err) };
    summary.push("package_status=error");
  }
  try {
    const terminal = await api("GET", TERMINAL_PATHS.terminalStatus, undefined, {
      auth: false,
    });
    const body = terminal?.data || {};
    rows.terminal_status = body;
    summary.push(
      `sig=${body.extension_signature_required_on_activate}`,
      `invoke=${body.extension_invoke_mode}`,
      `executed=${body.extension_invoke_executed}`,
      `sig_bypass=${body.extension_signature_bypass}`,
      `sandbox_escape=${body.sandbox_escape}`,
      `host_path=${body.extension_host_path}`,
    );
  } catch (err) {
    rows.terminal_status = { error: String(err.message || err) };
    summary.push("terminal_status=error");
  }
  const pathAligned =
    TERMINAL_PATHS.packageActionResolve === "/v1/packages/actions/resolve" &&
    TERMINAL_PATHS.packageSurfaces === "/v1/packages/surfaces";
  rows.terminal_paths = {
    packageActionResolve: TERMINAL_PATHS.packageActionResolve,
    packageSurfaces: TERMINAL_PATHS.packageSurfaces,
    aligned: pathAligned,
  };
  summary.push(`paths_aligned=${pathAligned}`);
  setPackageResolveAlignStatus(
    `Package↔Terminal resolve (PHX-G398) · ${summary.join(" · ")}`,
  );
  if (!quiet) {
    showJson("adminView", {
      package_resolve_align_status: rows,
      milestone: "PHX-G398",
    });
    log("Package↔Terminal resolve alignment (PHX-G398)", rows);
  }
  return true;
}

function setDomainFoundationStatus(text) {
  const node = $("domainFoundationStatus");
  if (node) {
    node.textContent = text;
  }
}

/** Read-only multi-domain Foundation status strip (PHX-G194). */
async function loadDomainFoundationStatus({ quiet = false } = {}) {
  const probes = [
    ["twin", TERMINAL_PATHS.twinStatus],
    ["brain", TERMINAL_PATHS.brainStatus],
    ["ai", TERMINAL_PATHS.aiStatus],
    ["workflow", TERMINAL_PATHS.workflowStatus],
    ["package", TERMINAL_PATHS.packageStatus],
    ["terminal", TERMINAL_PATHS.terminalStatus],
    ["event", TERMINAL_PATHS.eventStatus],
    ["knowledge", TERMINAL_PATHS.knowledgeStatus],
    ["identity", TERMINAL_PATHS.identityStatus],
    ["organization", TERMINAL_PATHS.organizationStatus],
    ["marketplace", TERMINAL_PATHS.marketplaceStatus],
    ["permission", "/v1/permission/status"],
    ["jwt", TERMINAL_PATHS.jwtStatus],
    ["oidc", TERMINAL_PATHS.oidcStatus],
    ["idp", TERMINAL_PATHS.idpStatus],
  ];
  const rows = {};
  const summary = [];
  for (const [name, path] of probes) {
    try {
      const data = await api("GET", path, undefined, { auth: false });
      const body = data?.data || {};
      rows[name] = body;
      if (name === "twin") {
        summary.push(
          `twin.authorize=${body.authorize_execution}`,
          `twin.sync=${body.sync_mode}`,
          `twin.daemon=${body.continuous_sync_daemon}`,
        );
      } else if (name === "knowledge") {
        const pack = body.sample_knowledge_pack_product || {};
        summary.push(
          `knowledge.pack=${pack.milestone || "—"}`,
          `knowledge.crud=${pack.crud === false ? "false" : pack.crud ?? "—"}`,
        );
      } else if (name === "brain") {
        summary.push(
          `brain.execute=${body.execute_execution}`,
          `advisory=${body.advisory_required}`,
          `brain.confidence_exec=${body.confidence_drives_execution}`,
          `brain.bias=${body.bias_notes_surface}`,
        );
      } else if (name === "ai") {
        summary.push(
          `ai.subject=${body.ai_subject_required}`,
          `commit_approval=${body.commit_requires_approval}`,
        );
      } else if (name === "workflow") {
        summary.push(`approval_sot=${body.approval_source_of_truth}`);
      } else if (name === "event") {
        summary.push(
          `event.daemon=${body.background_worker_daemon}`,
          `event.dispatch=${body.dispatch_trigger}`,
          `event.lease_s=${body.default_lease_seconds}`,
          `event.dlq=${body.dead_letter_list_access}`,
          `event.fail_closed=${body.fail_closed_without_grant}`,
        );
      } else if (name === "terminal") {
        summary.push(
          `terminal.truth=${body.holds_business_truth}`,
          `terminal.sig=${body.extension_signature_required_on_activate}`,
          `terminal.invoke=${body.extension_invoke_mode}`,
          `terminal.executed=${body.extension_invoke_executed}`,
        );
      } else if (name === "package") {
        summary.push(
          `package.resolve=${body.action_resolve_surface}`,
          `package.aligned=${body.terminal_resolve_aligned}`,
        );
      } else if (name === "marketplace") {
        summary.push(
          `marketplace.clearing=${body.payment_clearing}`,
          `arbitration=${body.external_arbitration}`,
          `metering=${body.metering}`,
        );
      } else if (name === "permission") {
        const surfaces = body.supported_surfaces || [];
        summary.push(
          `permission.writable=${body.writable}`,
          `role_grant_auto_write=${surfaces.includes("role_grant_auto_write")}`,
        );
      } else if (name === "jwt") {
        summary.push(
          `jwt.require=${body.require_jwt}`,
          `dev_headers=${body.allow_dev_headers}`,
        );
      } else if (name === "oidc") {
        const product = body.oidc_login_product || {};
        const webauthn = body.webauthn_product || {};
        summary.push(
          `oidc.enabled=${body.enabled}`,
          `oidc.login_product=${product.authorization_code_enabled}`,
          `webauthn.reg=${webauthn.registration_enabled}`,
        );
      } else if (name === "idp") {
        summary.push(
          `idp.writable=${body.writable}`,
          `idp.federation=${body.federation?.enabled}`,
        );
      } else {
        summary.push(
          `${name}.writable=${body.writable}`,
          `${name}.surfaces=${(body.supported_surfaces || []).length}`,
        );
      }
    } catch (err) {
      rows[name] = { error: String(err.message || err) };
      if (name === "jwt" || name === "oidc" || name === "idp") {
        summary.push(`${name}=fail_closed`);
      } else {
        summary.push(`${name}=error`);
      }
    }
  }
  setDomainFoundationStatus(`Domain status (PHX-G194) · ${summary.join(" · ")}`);
  if (!quiet) {
    showJson("adminView", { domain_foundation_status: rows, milestone: "PHX-G194" });
    log("Domain foundation status (PHX-G194)", rows);
  }
  return true;
}

async function adminAcquireListing() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingAcquire(requireListingId()),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing acquired (technical)", data);
}

async function adminAcquireListingToHost() {
  const listingId = requireListingId();
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingHostAcquire(listingId),
    {},
    { auth: true, platform: false },
  );
  const host = data?.data || {};
  applyHostAcquireResult(host);
  syncExtensionButtons();
  showJson("adminView", data);
  log("Listing host-acquire (PHX-G172)", data);
  try {
    await hydrateSignedExtensionHost({ quiet: false });
  } catch (err) {
    log("Post host-acquire hydrate deferred", {
      message: String(err.message || err),
    });
  }
  try {
    await loadHostAcquireStatus({ quiet: true });
  } catch {
    /* status line is best-effort */
  }
  try {
    await loadExtHostPathReadiness({ quiet: true });
  } catch {
    /* readiness is best-effort */
  }
}

function applyHostAcquireResult(host) {
  if (!host || typeof host !== "object") {
    return;
  }
  if (host.extension_id) {
    state.extensionId = host.extension_id;
  }
  if (host.package_key) {
    state.extensionKeyHint = host.package_key;
    if ($("extKey")) {
      $("extKey").value = host.package_key;
    }
  }
  if (Array.isArray(host.host_actions)) {
    state.hostActions = host.host_actions.map((item) => String(item));
    setExtHostActions(state.hostActions);
  }
}

function setExtHostPathReadiness(text) {
  const node = $("extHostPathReadiness");
  if (node) {
    node.textContent = text;
  }
}

function setExtHostActions(actions) {
  const node = $("extHostActions");
  if (!node) {
    return;
  }
  const list = Array.isArray(actions) ? actions : state.hostActions || [];
  node.textContent = list.length
    ? `host_actions: ${list.join(", ")}`
    : "host_actions: —";
}

async function loadExtHostPathReadiness({ quiet = false } = {}) {
  const listingId =
    ($("listingId")?.value || "").trim() || state.demoListingId || "";
  const keyHint =
    ($("extKey")?.value || "").trim() || state.extensionKeyHint || "noventi.demo.panel";
  let product = null;
  try {
    const status = await api("GET", TERMINAL_PATHS.marketplaceStatus, undefined, {
      auth: false,
    });
    product = status?.data?.host_acquire_product || null;
  } catch (err) {
    if (!quiet) {
      log("Host-path readiness status failed", {
        message: String(err.message || err),
      });
    }
  }
  const allowlist = Array.isArray(product?.allowlist) ? product.allowlist : [];
  const allowlisted = allowlist.includes(keyHint);
  const hydrated = Boolean(state.extensionHydrated && state.extensionId);
  const actions =
    state.hostActions.length > 0 ? state.hostActions : allowlisted ? ["panel.render"] : [];
  if (actions.length && !state.hostActions.length) {
    state.hostActions = actions;
  }
  setExtHostActions(actions);
  setExtHostPathReadiness(
    `Host-path ${product?.milestone || "n/a"} · listing=${listingId || "—"} · key=${keyHint} · allowlisted=${allowlisted} · hydrated=${hydrated} · scripts=${product?.arbitrary_scripts ?? "?"} · install=${product?.package_install ?? "?"} · psp=${product?.external_psp ?? "?"}`,
  );
  if (!quiet) {
    showJson("extView", {
      host_path_readiness: {
        listing_id: listingId || null,
        extension_key: keyHint,
        allowlisted,
        hydrated,
        extension_id: state.extensionId,
        host_actions: actions,
        host_acquire_product: product,
      },
    });
    log("Extensions host-path readiness (PHX-G182)", {
      listing_id: listingId || null,
      allowlisted,
      hydrated,
      host_actions: actions,
    });
  }
  return true;
}

async function extAcquireListingToHost() {
  const listingId =
    ($("listingId")?.value || "").trim() || state.demoListingId || "";
  if (!listingId) {
    throw new Error("Marketplace listing id is required (demo bootstrap or Admin)");
  }
  if ($("listingId") && !$("listingId").value.trim()) {
    $("listingId").value = listingId;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingHostAcquire(listingId),
    {},
    { auth: true, platform: false },
  );
  const host = data?.data || {};
  applyHostAcquireResult(host);
  syncExtensionButtons();
  showJson("extView", data);
  log("Extensions host-acquire (PHX-G182)", data);
  try {
    await hydrateSignedExtensionHost({ quiet: false });
  } catch (err) {
    log("Post host-acquire hydrate deferred", {
      message: String(err.message || err),
    });
  }
  try {
    await loadExtHostPathReadiness({ quiet: true });
  } catch {
    /* readiness is best-effort */
  }
}

async function adminRevokeListing() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingRevoke(requireListingId()),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing revoked", data);
}

async function adminSetListingPricing() {
  const price = $("listingPrice").value.trim();
  if (!price) {
    throw new Error("Listing price is required");
  }
  const body = { price };
  const currency = $("listingCurrency").value.trim();
  if (currency) {
    body.currency = currency;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingPricing(requireListingId()),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing pricing set (Foundation fixed; ≠ payment clearing)", data);
}

async function adminCreateListingInvoice() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingInvoices(requireListingId()),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing invoice issued (not a payment settlement)", data);
}

async function adminCreateListingPaymentClearing() {
  const invoiceId = $("listingInvoiceId").value.trim();
  if (!invoiceId) {
    throw new Error("Listing invoice id is required for payment clearing");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingPaymentClearing(requireListingId()),
    { invoice_id: invoiceId, note: "terminal g162" },
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log(
    "Listing payment clearing (G162 internal record; ≠ external PSP / arbitration)",
    data,
  );
}

async function adminOpenListingDispute() {
  const reason = $("listingDisputeReason").value.trim();
  if (!reason) {
    throw new Error("Listing dispute reason is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingDisputes(requireListingId()),
    { reason },
    { auth: true, platform: false },
  );
  if (data.data && $("listingDisputeId")) {
    $("listingDisputeId").value = uuidFromResult(data);
  }
  showJson("adminView", data);
  log("Listing dispute opened (publisher-tenant; ≠ external arbitration)", data);
}

async function adminResolveListingDispute() {
  const disputeId = $("listingDisputeId").value.trim();
  const resolution = $("listingDisputeResolution").value.trim();
  if (!disputeId || !resolution) {
    throw new Error("Dispute id and resolution are required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceDisputeResolve(disputeId),
    { resolution },
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing dispute resolved (≠ external arbitration)", data);
}

async function adminSetListingRevenueShare() {
  const bpsRaw = $("listingRevenueShareBps").value.trim();
  if (!bpsRaw) {
    throw new Error("platform_share_bps is required");
  }
  const platformShareBps = Number(bpsRaw);
  if (Number.isNaN(platformShareBps)) {
    throw new Error("platform_share_bps must be a number");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.marketplaceListingRevenueShare(requireListingId()),
    { platform_share_bps: platformShareBps },
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Listing revenue share set (≠ payment clearing)", data);
}

async function adminCreateWorkflowDefinition() {
  const name = $("workflowDefinitionName").value.trim();
  const definitionDocumentRef = $("workflowDefinitionDocRef").value.trim();
  const version = $("workflowDefinitionVersion").value.trim();
  if (!name || !definitionDocumentRef || !version) {
    throw new Error("Workflow definition name, document ref and version are required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.workflowDefinitions,
    {
      name,
      definition_document_ref: definitionDocumentRef,
      version,
    },
    { auth: true, platform: false },
  );
  if (data.id && $("workflowDefinitionId")) {
    $("workflowDefinitionId").value = data.id;
  }
  showJson("adminView", data);
  log("Workflow definition created", data);
}

async function adminDeprecateWorkflowDefinition() {
  const definitionId = $("workflowDefinitionId").value.trim();
  if (!definitionId) {
    throw new Error("Workflow definition id is required (create first)");
  }
  const reason =
    ($("workflowDeprecateReason") && $("workflowDeprecateReason").value.trim()) ||
    "terminal deprecate";
  const versionRaw =
    ($("workflowDeprecateExpectedVersion") &&
      $("workflowDeprecateExpectedVersion").value.trim()) ||
    "1";
  const expectedVersion = Number(versionRaw);
  if (!reason || Number.isNaN(expectedVersion)) {
    throw new Error("Workflow deprecate reason and expected_version are required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.workflowDefinitionDeprecation(definitionId),
    { reason, expected_version: expectedVersion },
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Workflow definition deprecated", data);
}

async function adminStartWorkflowInstance() {
  const definitionId = $("workflowDefinitionId").value.trim();
  if (!definitionId) {
    throw new Error("Workflow definition id is required (create first)");
  }
  let payload = {};
  const rawPayload = $("workflowInstancePayload").value.trim();
  if (rawPayload) {
    payload = JSON.parse(rawPayload);
    if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("Workflow instance payload must be a JSON object");
    }
  }
  const body = {
    definition_id: definitionId,
    payload,
  };
  const businessKey = $("workflowBusinessKey").value.trim();
  if (businessKey) {
    body.business_key = businessKey;
  }
  const approvalSubjectId = $("workflowApprovalSubjectId").value.trim();
  if (approvalSubjectId) {
    body.approval_subject_id = approvalSubjectId;
  }
  const approvalPrincipalId = $("workflowApprovalPrincipalId").value.trim();
  if (approvalPrincipalId) {
    body.approval_principal_id = approvalPrincipalId;
  }
  const approvalAction = $("workflowApprovalAction").value.trim();
  if (approvalAction) {
    body.approval_action = approvalAction;
  }
  const approvalResourceRef = $("workflowApprovalResourceRef").value.trim();
  if (approvalResourceRef) {
    body.approval_resource_ref = approvalResourceRef;
  }
  const data = await api("POST", TERMINAL_PATHS.workflowInstances, body, {
    auth: true,
    platform: false,
  });
  if (data.instance_id && $("workflowInstanceId")) {
    $("workflowInstanceId").value = data.instance_id;
  }
  if (data.task_id && $("workflowTaskId")) {
    $("workflowTaskId").value = data.task_id;
  }
  showJson("adminView", data);
  log("Workflow instance started", data);
}

async function adminGetWorkflowInstance() {
  const instanceId = $("workflowInstanceId").value.trim();
  if (!instanceId) {
    throw new Error("Workflow instance id is required (start first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.workflowInstance(instanceId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Workflow instance fetched", data);
}

async function adminListWorkflowTasks() {
  const params = new URLSearchParams();
  const assignee = $("workflowTaskAssigneeId").value.trim();
  if (assignee) {
    params.set("assignee_subject_id", assignee);
  }
  const statusFilter = $("workflowTaskStatus").value.trim();
  if (statusFilter) {
    params.set("status", statusFilter);
  }
  const path = params.toString()
    ? `${TERMINAL_PATHS.workflowTasks}?${params}`
    : TERMINAL_PATHS.workflowTasks;
  const data = await api("GET", path, undefined, {
    auth: true,
    platform: false,
  });
  const first = Array.isArray(data) && data[0] ? data[0] : null;
  if (first && first.id && $("workflowTaskId")) {
    $("workflowTaskId").value = first.id;
  }
  if (first && first.instance_id && $("workflowInstanceId")) {
    $("workflowInstanceId").value = first.instance_id;
  }
  showJson("adminView", data);
  log("Workflow tasks listed", data);
}

function requireWorkflowInstanceAndTask() {
  const instanceId = $("workflowInstanceId").value.trim();
  const taskId = $("workflowTaskId").value.trim();
  if (!instanceId || !taskId) {
    throw new Error("Workflow instance id and task id are required");
  }
  return { instanceId, taskId };
}

async function adminApproveWorkflowTask() {
  const { instanceId, taskId } = requireWorkflowInstanceAndTask();
  const body = {};
  const comment = $("workflowTaskComment").value.trim();
  if (comment) {
    body.comment = comment;
  }
  const expectedTaskVersion = $("workflowTaskExpectedVersion").value.trim();
  if (expectedTaskVersion) {
    body.expected_task_version = Number(expectedTaskVersion);
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.workflowTaskApproval(instanceId, taskId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Workflow task approved", data);
}

async function adminRejectWorkflowTask() {
  const { instanceId, taskId } = requireWorkflowInstanceAndTask();
  const reason = $("workflowTaskRejectReason").value.trim();
  if (!reason) {
    throw new Error("Workflow reject reason is required");
  }
  const body = { reason };
  const expectedTaskVersion = $("workflowTaskExpectedVersion").value.trim();
  if (expectedTaskVersion) {
    body.expected_task_version = Number(expectedTaskVersion);
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.workflowTaskRejection(instanceId, taskId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Workflow task rejected", data);
}

function requireWorkflowInstanceId() {
  const instanceId = $("workflowInstanceId").value.trim();
  if (!instanceId) {
    throw new Error("Workflow instance id is required (start first)");
  }
  return instanceId;
}

async function adminSignalWorkflowInstance() {
  const instanceId = requireWorkflowInstanceId();
  const signalName = $("workflowSignalName").value.trim();
  const idempotencyKey = $("workflowSignalIdempotencyKey").value.trim();
  if (!signalName || !idempotencyKey) {
    throw new Error("Workflow signal name and idempotency key are required");
  }
  const body = {
    signal_name: signalName,
    idempotency_key: idempotencyKey,
  };
  const rawPayload = $("workflowSignalPayload").value.trim();
  if (rawPayload) {
    const payload = JSON.parse(rawPayload);
    if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("Workflow signal payload must be a JSON object");
    }
    body.payload = payload;
  }
  const expectedVersion = $("workflowInstanceExpectedVersion").value.trim();
  if (expectedVersion) {
    body.expected_version = Number(expectedVersion);
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.workflowInstanceSignal(instanceId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Workflow instance signaled", data);
}

async function adminCancelWorkflowInstance() {
  const instanceId = requireWorkflowInstanceId();
  const reason = $("workflowCancelReason").value.trim();
  if (!reason) {
    throw new Error("Workflow cancel reason is required");
  }
  const body = { reason };
  const expectedVersion = $("workflowInstanceExpectedVersion").value.trim();
  if (expectedVersion) {
    body.expected_version = Number(expectedVersion);
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.workflowInstanceCancel(instanceId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Workflow instance cancelled", data);
}

async function adminCompensateWorkflowInstance() {
  const instanceId = requireWorkflowInstanceId();
  const reason = $("workflowCompensateReason").value.trim();
  if (!reason) {
    throw new Error("Workflow compensate reason is required");
  }
  const body = { reason };
  const expectedVersion = $("workflowInstanceExpectedVersion").value.trim();
  if (expectedVersion) {
    body.expected_version = Number(expectedVersion);
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.workflowInstanceCompensate(instanceId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Workflow instance compensating", data);
}

async function adminEscalateWorkflowTask() {
  const { instanceId, taskId } = requireWorkflowInstanceAndTask();
  const toSubjectId = $("workflowEscalateToSubjectId").value.trim();
  const reason = $("workflowEscalateReason").value.trim();
  if (!toSubjectId || !reason) {
    throw new Error("Workflow escalate to_subject_id and reason are required");
  }
  const body = {
    to_subject_id: toSubjectId,
    reason,
  };
  const expectedTaskVersion = $("workflowTaskExpectedVersion").value.trim();
  if (expectedTaskVersion) {
    body.expected_task_version = Number(expectedTaskVersion);
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.workflowTaskEscalation(instanceId, taskId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Workflow task escalated", data);
}

async function adminRegisterPackageManifest() {
  const raw = $("packageManifestJson").value.trim();
  if (!raw) {
    throw new Error("Package manifest JSON is required");
  }
  const body = JSON.parse(raw);
  if (body === null || typeof body !== "object" || Array.isArray(body)) {
    throw new Error("Package manifest JSON must be an object");
  }
  const data = await api("POST", TERMINAL_PATHS.packageManifests, body, {
    auth: true,
    platform: false,
  });
  if (data.data && $("packageManifestId")) {
    $("packageManifestId").value = uuidFromResult(data);
  }
  showJson("adminView", data);
  log("Package manifest registered", data);
}

async function adminGetPackageManifest() {
  const manifestId = $("packageManifestId").value.trim();
  if (!manifestId) {
    throw new Error("Package manifest id is required (register first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.packageManifest(manifestId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Package manifest fetched", data);
}

async function adminListPackageSurfaces() {
  const data = await api("GET", TERMINAL_PATHS.packageSurfaces, undefined, {
    auth: true,
    platform: false,
  });
  showJson("adminView", data);
  log("Package surfaces listed", data);
}

function requirePackageManifestId() {
  const manifestId = $("packageManifestId").value.trim();
  if (!manifestId) {
    throw new Error("Package manifest id is required (register first)");
  }
  return manifestId;
}

async function adminPublishPackageManifest() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.packageManifestPublish(requirePackageManifestId()),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Package manifest published", data);
}

async function adminInstallPackage() {
  const data = await api(
    "POST",
    TERMINAL_PATHS.packageInstallations,
    { manifest_id: requirePackageManifestId() },
    { auth: true, platform: false },
  );
  if (data.data && $("packageInstallationId")) {
    $("packageInstallationId").value = uuidFromResult(data);
  }
  showJson("adminView", data);
  log("Package installed", data);
}

async function adminDisablePackageInstallation() {
  const installationId = $("packageInstallationId").value.trim();
  if (!installationId) {
    throw new Error("Package installation id is required (install first)");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.packageInstallationDisable(installationId),
    {},
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Package installation disabled", data);
}

async function adminResolvePackageAction() {
  const actionKey = $("packageActionKey").value.trim();
  if (!actionKey) {
    throw new Error("Package action key is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.packageActionResolve,
    { action_key: actionKey },
    { auth: true, platform: false },
  );
  if (data.installation_id && $("packageInstallationId")) {
    $("packageInstallationId").value = data.installation_id;
  }
  showJson("adminView", data);
  log("Package action resolved", data);
}

async function adminUpsertKnowledgeEntity() {
  const entityType = $("knowledgeEntityType").value.trim();
  const name = $("knowledgeEntityName").value.trim();
  const layer = $("knowledgeEntityLayer").value.trim();
  const sourceRef = $("knowledgeEntitySourceRef").value.trim();
  const reason = $("knowledgeEntityReason").value.trim();
  if (!entityType || !name || !layer || !sourceRef || !reason) {
    throw new Error(
      "Knowledge entity type, name, layer, source_ref and reason are required",
    );
  }
  const body = {
    entity_type: entityType,
    name,
    layer,
    source_ref: sourceRef,
    reason,
  };
  const labelsRaw = $("knowledgeEntityLabels").value.trim();
  if (labelsRaw) {
    body.labels = labelsRaw
      .split(",")
      .map((part) => part.trim())
      .filter(Boolean);
  }
  const attrsRaw = $("knowledgeEntityAttributes").value.trim();
  if (attrsRaw) {
    const attributes = JSON.parse(attrsRaw);
    if (
      attributes === null ||
      typeof attributes !== "object" ||
      Array.isArray(attributes)
    ) {
      throw new Error("Knowledge attributes must be a JSON object");
    }
    body.attributes = attributes;
  }
  const entityId = $("knowledgeEntityId").value.trim();
  if (entityId) {
    body.entity_id = entityId;
  }
  const data = await api("POST", TERMINAL_PATHS.knowledgeEntities, body, {
    auth: true,
    platform: false,
  });
  if (data.id && $("knowledgeEntityId")) {
    $("knowledgeEntityId").value = data.id;
  }
  showJson("adminView", data);
  log("Knowledge entity upserted", data);
}

async function adminGetKnowledgeEntity() {
  const entityId = $("knowledgeEntityId").value.trim();
  if (!entityId) {
    throw new Error("Knowledge entity id is required (upsert first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.knowledgeEntity(entityId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Knowledge entity fetched", data);
}

async function adminListKnowledgeEntities() {
  const params = new URLSearchParams();
  const entityType = $("knowledgeEntityType").value.trim();
  if (entityType) {
    params.set("entityType", entityType);
  }
  const layer = $("knowledgeEntityLayer").value.trim();
  if (layer) {
    params.set("layer", layer);
  }
  const path = params.toString()
    ? `${TERMINAL_PATHS.knowledgeEntities}?${params}`
    : TERMINAL_PATHS.knowledgeEntities;
  const data = await api("GET", path, undefined, {
    auth: true,
    platform: false,
  });
  const first =
    data.data && Array.isArray(data.data) && data.data[0] ? data.data[0] : null;
  if (first && first.id && $("knowledgeEntityId")) {
    $("knowledgeEntityId").value = first.id;
  }
  showJson("adminView", data);
  log("Knowledge entities listed", data);
}

function requireKnowledgeEntityId() {
  const entityId = $("knowledgeEntityId").value.trim();
  if (!entityId) {
    throw new Error("Knowledge entity id is required (upsert/list first)");
  }
  return entityId;
}

async function adminArchiveKnowledgeEntity() {
  const reason = $("knowledgeArchiveReason").value.trim() || $("knowledgeEntityReason").value.trim();
  const sourceRef =
    $("knowledgeArchiveSourceRef").value.trim() ||
    $("knowledgeEntitySourceRef").value.trim();
  if (!reason || !sourceRef) {
    throw new Error("Knowledge archive reason and source_ref are required");
  }
  const body = { reason, source_ref: sourceRef };
  const expectedVersion = $("knowledgeEntityExpectedVersion").value.trim();
  if (expectedVersion) {
    body.expected_version = Number(expectedVersion);
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.knowledgeEntityArchive(requireKnowledgeEntityId()),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Knowledge entity archived", data);
}

async function adminShareKnowledgeEntity() {
  const shareWith = $("knowledgeShareWithSubjectId").value.trim();
  const reason = $("knowledgeShareReason").value.trim() || $("knowledgeEntityReason").value.trim();
  const sourceRef =
    $("knowledgeShareSourceRef").value.trim() ||
    $("knowledgeEntitySourceRef").value.trim();
  if (!shareWith || !reason || !sourceRef) {
    throw new Error(
      "Knowledge share_with_subject_id, reason and source_ref are required",
    );
  }
  const body = {
    share_with_subject_id: shareWith,
    reason,
    source_ref: sourceRef,
  };
  const expectedVersion = $("knowledgeEntityExpectedVersion").value.trim();
  if (expectedVersion) {
    body.expected_version = Number(expectedVersion);
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.knowledgeEntityShare(requireKnowledgeEntityId()),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Knowledge entity shared", data);
}

async function adminSearchKnowledge() {
  const text = $("knowledgeSearchText").value.trim();
  if (!text) {
    throw new Error("Knowledge search text is required");
  }
  const path = `${TERMINAL_PATHS.knowledgeSearch}?${new URLSearchParams({ text })}`;
  const data = await api("GET", path, undefined, {
    auth: true,
    platform: false,
  });
  const first =
    data.data && Array.isArray(data.data) && data.data[0] ? data.data[0] : null;
  if (first && first.id && $("knowledgeEntityId")) {
    $("knowledgeEntityId").value = first.id;
  }
  showJson("adminView", data);
  log("Knowledge search completed", data);
}

async function adminCreateKnowledgeLink() {
  const fromEntityId = $("knowledgeLinkFromId").value.trim() || $("knowledgeEntityId").value.trim();
  const toEntityId = $("knowledgeLinkToId").value.trim();
  const relationType = $("knowledgeLinkRelationType").value.trim();
  const sourceRef =
    $("knowledgeLinkSourceRef").value.trim() ||
    $("knowledgeEntitySourceRef").value.trim();
  const reason =
    $("knowledgeLinkReason").value.trim() ||
    $("knowledgeEntityReason").value.trim();
  if (!fromEntityId || !toEntityId || !relationType || !sourceRef || !reason) {
    throw new Error(
      "Knowledge link from/to ids, relation_type, source_ref and reason are required",
    );
  }
  const body = {
    from_entity_id: fromEntityId,
    to_entity_id: toEntityId,
    relation_type: relationType,
    source_ref: sourceRef,
    reason,
  };
  const data = await api("POST", TERMINAL_PATHS.knowledgeLinks, body, {
    auth: true,
    platform: false,
  });
  if (data.id && $("knowledgeLinkId")) {
    $("knowledgeLinkId").value = data.id;
  }
  showJson("adminView", data);
  log("Knowledge link created", data);
}

async function adminGetKnowledgeProvenance() {
  const subjectKind = $("knowledgeProvenanceKind").value.trim() || "entity";
  const subjectId =
    $("knowledgeProvenanceSubjectId").value.trim() ||
    $("knowledgeEntityId").value.trim();
  if (!subjectId) {
    throw new Error("Knowledge provenance subject id is required");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.knowledgeProvenance(subjectKind, subjectId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Knowledge provenance fetched", data);
}

async function adminUpsertTwinSnapshot() {
  const entityRef = $("twinEntityRef").value.trim();
  const sourceRef = $("twinSourceRef").value.trim();
  const reason = $("twinReason").value.trim();
  const confidenceRaw = $("twinConfidence").value.trim();
  if (!entityRef || !sourceRef || !reason || !confidenceRaw) {
    throw new Error("Twin entity_ref, source_ref, reason and confidence are required");
  }
  const confidence = Number(confidenceRaw);
  if (Number.isNaN(confidence)) {
    throw new Error("Twin confidence must be a number");
  }
  let state = {};
  const rawState = $("twinStateJson").value.trim();
  if (rawState) {
    state = JSON.parse(rawState);
    if (state === null || typeof state !== "object" || Array.isArray(state)) {
      throw new Error("Twin state must be a JSON object");
    }
  }
  const body = {
    entity_ref: entityRef,
    state,
    source_ref: sourceRef,
    reason,
    confidence,
  };
  const data = await api("POST", TERMINAL_PATHS.twinSnapshots, body, {
    auth: true,
    platform: false,
  });
  if (data.data && $("twinSnapshotId")) {
    $("twinSnapshotId").value = uuidFromResult(data);
  }
  showJson("adminView", data);
  log("Twin snapshot upserted", data);
}

async function adminGetTwinSnapshot() {
  const snapshotId = $("twinSnapshotId").value.trim();
  if (!snapshotId) {
    throw new Error("Twin snapshot id is required (upsert first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.twinSnapshot(snapshotId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Twin snapshot fetched", data);
}

async function adminAuthorizeFromTwin() {
  const snapshotId = $("twinSnapshotId").value.trim();
  if (!snapshotId) {
    throw new Error("Twin snapshot id is required (upsert first)");
  }
  const response = await fetch(TERMINAL_PATHS.twinAuthorize(snapshotId), {
    method: "POST",
    headers: trustedHeaders({ platform: false }),
  });
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  const view = {
    ok: response.ok,
    status: response.status,
    expected_fail_closed: true,
    data,
  };
  showJson("adminView", view);
  log("Twin authorize probed (fail-closed)", view);
  if (response.status !== 403) {
    throw new Error(`Expected fail-closed 403, got HTTP_${response.status}`);
  }
}

async function adminPublishBrainInsight() {
  const kind = $("brainKind").value.trim();
  const summary = $("brainSummary").value.trim();
  const sourceRef = $("brainSourceRef").value.trim();
  const reason = $("brainReason").value.trim();
  const confidenceRaw = $("brainConfidence").value.trim();
  if (!kind || !summary || !sourceRef || !reason || !confidenceRaw) {
    throw new Error("Brain kind, summary, source_ref, reason and confidence are required");
  }
  const confidence = Number(confidenceRaw);
  if (Number.isNaN(confidence)) {
    throw new Error("Brain confidence must be a number");
  }
  const body = {
    kind,
    summary,
    source_ref: sourceRef,
    reason,
    confidence,
    advisory: true,
  };
  const twinRef = $("brainTwinRef").value.trim() || $("twinSnapshotId").value.trim();
  if (twinRef) {
    body.twin_ref = twinRef;
  }
  const data = await api("POST", TERMINAL_PATHS.brainInsights, body, {
    auth: true,
    platform: false,
  });
  if (data.data && $("brainInsightId")) {
    $("brainInsightId").value = uuidFromResult(data);
  }
  showJson("adminView", data);
  log("Brain insight published", data);
}

async function adminGetBrainInsight() {
  const insightId = $("brainInsightId").value.trim();
  if (!insightId) {
    throw new Error("Brain insight id is required (publish first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.brainInsight(insightId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Brain insight fetched", data);
}

async function adminExecuteBrainInsight() {
  const insightId = $("brainInsightId").value.trim();
  if (!insightId) {
    throw new Error("Brain insight id is required (publish first)");
  }
  const response = await fetch(TERMINAL_PATHS.brainExecute(insightId), {
    method: "POST",
    headers: trustedHeaders({ platform: false }),
  });
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  const view = {
    ok: response.ok,
    status: response.status,
    expected_fail_closed: true,
    data,
  };
  showJson("adminView", view);
  log("Brain execute probed (fail-closed)", view);
  if (response.status !== 403) {
    throw new Error(`Expected fail-closed 403, got HTTP_${response.status}`);
  }
}

async function adminCreateAiRun() {
  const goal = $("aiRunGoal").value.trim();
  if (!goal) {
    throw new Error("AI run goal is required");
  }
  const planSummary = $("aiRunPlanSummary").value.trim();
  const body = { goal };
  if (planSummary) {
    body.plan_summary = planSummary;
  }
  const data = await api("POST", TERMINAL_PATHS.aiRuns, body, {
    auth: true,
    platform: false,
    subjectType: "ai_employee",
  });
  if (data.data && $("aiRunId")) {
    $("aiRunId").value = uuidFromResult(data);
  }
  showJson("adminView", data);
  log("AI run created", data);
}

async function adminGetAiRun() {
  const runId = $("aiRunId").value.trim();
  if (!runId) {
    throw new Error("AI run id is required (create first)");
  }
  const data = await api("GET", TERMINAL_PATHS.aiRun(runId), undefined, {
    auth: true,
    platform: false,
    subjectType: "ai_employee",
  });
  showJson("adminView", data);
  log("AI run fetched", data);
}

async function adminRegisterAiTool() {
  const name = $("aiToolName").value.trim();
  const description = $("aiToolDescription").value.trim();
  if (!name || !description) {
    throw new Error("AI tool name and description are required");
  }
  const highImpact = $("aiToolHighImpact").checked;
  const data = await api(
    "POST",
    TERMINAL_PATHS.aiTools,
    { name, description, high_impact: highImpact },
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("AI tool registered", data);
}

async function adminInvokeAiTool() {
  const runId = $("aiRunId").value.trim();
  const toolName = $("aiToolName").value.trim();
  if (!runId || !toolName) {
    throw new Error("AI run id and tool name are required");
  }
  let argumentsPayload = {};
  const rawArgs = $("aiToolArgumentsJson").value.trim();
  if (rawArgs) {
    argumentsPayload = JSON.parse(rawArgs);
    if (
      argumentsPayload === null ||
      typeof argumentsPayload !== "object" ||
      Array.isArray(argumentsPayload)
    ) {
      throw new Error("AI tool arguments must be a JSON object");
    }
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.aiToolInvocations(runId),
    { tool_name: toolName, arguments: argumentsPayload },
    { auth: true, platform: false, subjectType: "ai_employee" },
  );
  showJson("adminView", data);
  log("AI tool invoked", data);
}

async function adminWriteAiMemory() {
  const runId = $("aiRunId").value.trim();
  const key = $("aiMemoryKey").value.trim();
  const rawValue = $("aiMemoryValueJson").value.trim();
  if (!runId || !key || !rawValue) {
    throw new Error("AI run id, memory key and value JSON are required");
  }
  const value = JSON.parse(rawValue);
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("AI memory value must be a JSON object");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.aiMemory(runId),
    { key, value },
    { auth: true, platform: false, subjectType: "ai_employee" },
  );
  showJson("adminView", data);
  log("AI memory written", data);
}

async function adminReadAiMemory() {
  const runId = $("aiRunId").value.trim();
  const key = $("aiMemoryKey").value.trim();
  if (!runId || !key) {
    throw new Error("AI run id and memory key are required");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.aiMemoryKey(runId, encodeURIComponent(key)),
    undefined,
    { auth: true, platform: false, subjectType: "ai_employee" },
  );
  showJson("adminView", data);
  log("AI memory read", data);
}

async function adminRequestAiApproval() {
  const runId = $("aiRunId").value.trim();
  const definitionId =
    $("aiApprovalDefinitionId").value.trim() ||
    $("workflowDefinitionId").value.trim();
  const approvalSubjectId =
    $("aiApprovalSubjectId").value.trim() ||
    $("approvalSubjectId").value.trim() ||
    $("subjectId").value.trim();
  const action = $("aiCommitAction").value.trim();
  const resourceRef = $("aiCommitResourceRef").value.trim();
  if (!runId || !definitionId || !approvalSubjectId || !action || !resourceRef) {
    throw new Error(
      "AI run id, definition id, approval subject, action and resource_ref are required",
    );
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.aiApprovals(runId),
    {
      definition_id: definitionId,
      approval_subject_id: approvalSubjectId,
      action,
      resource_ref: resourceRef,
    },
    { auth: true, platform: false, subjectType: "ai_employee" },
  );
  showJson("adminView", data);
  log("AI approval requested", data);
}

async function adminCommitAiAction() {
  const runId = $("aiRunId").value.trim();
  const action = $("aiCommitAction").value.trim();
  const resourceRef = $("aiCommitResourceRef").value.trim();
  if (!runId || !action || !resourceRef) {
    throw new Error("AI run id, action and resource_ref are required");
  }
  const response = await fetch(TERMINAL_PATHS.aiCommits(runId), {
    method: "POST",
    headers: trustedHeaders({ platform: false, subjectType: "ai_employee" }),
    body: JSON.stringify(
      sanitizeBody({
        action,
        resource_ref: resourceRef,
      }),
    ),
  });
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  const view = {
    ok: response.ok,
    status: response.status,
    expected_fail_closed_without_approval: true,
    data,
  };
  showJson("adminView", view);
  log("AI commit probed (approval-gated)", view);
  if (response.status !== 403 && response.status !== 200) {
    throw new Error(`Unexpected AI commit status HTTP_${response.status}`);
  }
}

async function adminRegisterIdentitySubject() {
  const subjectType = $("identitySubjectType").value.trim() || "human";
  const displayName = $("identityDisplayName").value.trim();
  if (!displayName) {
    throw new Error("Identity display_name is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identitySubjects,
    { subject_type: subjectType, display_name: displayName },
    { auth: true, platform: false },
  );
  if (data.id && $("identitySubjectId")) {
    $("identitySubjectId").value = data.id;
  }
  showJson("adminView", data);
  log("Identity subject registered", data);
}

async function adminResolveIdentitySubject() {
  const subjectId = $("identitySubjectId").value.trim();
  if (!subjectId) {
    throw new Error("Identity subject id is required (register first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.identitySubject(subjectId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Identity subject resolved", data);
}

async function adminBindIdentityCredential() {
  const subjectId = $("identitySubjectId").value.trim();
  const credentialKind = $("identityCredentialKind").value.trim();
  const secretHandle = $("identitySecretHandle").value.trim();
  if (!subjectId || !credentialKind || !secretHandle) {
    throw new Error(
      "Identity subject id, credential_kind and secret_handle are required",
    );
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identityCredentials,
    {
      subject_id: subjectId,
      credential_kind: credentialKind,
      secret_handle: secretHandle,
    },
    { auth: true, platform: false },
  );
  if (data.id && $("identityCredentialId")) {
    $("identityCredentialId").value = data.id;
  }
  showJson("adminView", data);
  log("Identity credential bound", data);
}

async function adminCreateIdentitySession() {
  const subjectId = $("identitySubjectId").value.trim();
  const credentialId = $("identityCredentialId").value.trim();
  if (!subjectId || !credentialId) {
    throw new Error("Identity subject id and credential id are required");
  }
  const ttlRaw = $("identitySessionTtlMinutes").value.trim();
  const body = { credential_id: credentialId };
  if (ttlRaw) {
    const ttl = Number(ttlRaw);
    if (Number.isNaN(ttl)) {
      throw new Error("Identity session ttl_minutes must be a number");
    }
    body.ttl_minutes = ttl;
  }
  const data = await api("POST", TERMINAL_PATHS.identitySessions, body, {
    auth: true,
    platform: false,
    subjectId,
  });
  if (data.session_id && $("identitySessionId")) {
    $("identitySessionId").value = data.session_id;
  }
  showJson("adminView", data);
  log("Identity session created", data);
}

async function adminValidateIdentitySession() {
  const subjectId = $("identitySubjectId").value.trim();
  const sessionId = $("identitySessionId").value.trim();
  if (!subjectId || !sessionId) {
    throw new Error("Identity subject id and session id are required");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.identitySessionValidation(sessionId),
    undefined,
    { auth: true, platform: false, subjectId },
  );
  showJson("adminView", data);
  log("Identity session validated", data);
}

async function adminValidateIdentityCredential() {
  const subjectId = $("identitySubjectId").value.trim();
  const credentialId = $("identityCredentialId").value.trim();
  if (!subjectId || !credentialId) {
    throw new Error("Identity subject id and credential id are required");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.identityCredentialValidation(credentialId),
    undefined,
    { auth: true, platform: false, subjectId },
  );
  showJson("adminView", data);
  log("Identity credential validated", data);
}

async function adminRevokeIdentityCredential() {
  const subjectId = $("identitySubjectId").value.trim();
  const credentialId = $("identityCredentialId").value.trim();
  const reason = $("identityRevokeReason").value.trim();
  if (!subjectId || !credentialId || !reason) {
    throw new Error(
      "Identity subject id, credential id and revoke reason are required",
    );
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identityCredentialRevocation(credentialId),
    { reason },
    { auth: true, platform: false, subjectId },
  );
  showJson("adminView", data ?? { revoked: true, credential_id: credentialId });
  log("Identity credential revoked", data ?? { credential_id: credentialId });
}

async function adminRevokeIdentitySession() {
  const subjectId = $("identitySubjectId").value.trim();
  const sessionId = $("identitySessionId").value.trim();
  const reason = $("identityRevokeReason").value.trim();
  if (!subjectId || !sessionId || !reason) {
    throw new Error(
      "Identity subject id, session id and revoke reason are required",
    );
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identitySessionRevocation(sessionId),
    { reason },
    { auth: true, platform: false, subjectId },
  );
  showJson("adminView", data ?? { revoked: true, session_id: sessionId });
  log("Identity session revoked", data ?? { session_id: sessionId });
}

async function adminGrantIdentityGovernor() {
  const governorSubjectId = $("identityGovernorSubjectId").value.trim();
  if (!governorSubjectId) {
    throw new Error("Identity governor subject id is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identityPlatformGovernors,
    { subject_id: governorSubjectId },
    { auth: true, platform: true },
  );
  showJson("adminView", data);
  log("Platform identity governor granted", data);
}

async function adminRevokeIdentityGovernor() {
  const governorSubjectId = $("identityGovernorSubjectId").value.trim();
  const reason = $("identityRevokeReason").value.trim();
  if (!governorSubjectId || !reason) {
    throw new Error(
      "Identity governor subject id and revoke reason are required",
    );
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identityPlatformGovernorRevocation(governorSubjectId),
    { reason },
    { auth: true, platform: true },
  );
  showJson("adminView", data ?? { revoked: true, subject_id: governorSubjectId });
  log("Platform identity governor revoked", data ?? { subject_id: governorSubjectId });
}

async function adminRegisterIdentityAi() {
  const displayName = $("identityAiDisplayName").value.trim();
  const capabilities = $("identityAiCapabilitiesProfile").value.trim();
  const ownerPolicy = $("identityAiOwnerPolicy").value.trim();
  if (!displayName || !capabilities || !ownerPolicy) {
    throw new Error(
      "AI display name, capabilities profile and owner policy are required",
    );
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identityAiEmployees,
    {
      display_name: displayName,
      capabilities_profile: capabilities,
      owner_policy: ownerPolicy,
    },
    { auth: true, platform: true },
  );
  if (data.id && $("identityAiSubjectId")) {
    $("identityAiSubjectId").value = data.id;
  }
  showJson("adminView", data);
  log("AI employee registered", data);
}

async function adminGetIdentityAiProfile() {
  const aiSubjectId = $("identityAiSubjectId").value.trim();
  if (!aiSubjectId) {
    throw new Error("AI employee subject id is required");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.identityAiProfile(aiSubjectId),
    undefined,
    { auth: true, platform: true },
  );
  if (data.version != null && $("identityAiProfileVersion")) {
    $("identityAiProfileVersion").value = String(data.version);
  }
  showJson("adminView", data);
  log("AI employee profile fetched", data);
}

async function adminUpdateIdentityAiProfile() {
  const aiSubjectId = $("identityAiSubjectId").value.trim();
  const capabilities = $("identityAiCapabilitiesProfile").value.trim();
  const ownerPolicy = $("identityAiOwnerPolicy").value.trim();
  const versionRaw = $("identityAiProfileVersion").value.trim();
  const expectedVersion = Number(versionRaw);
  if (
    !aiSubjectId ||
    !capabilities ||
    !ownerPolicy ||
    !versionRaw ||
    Number.isNaN(expectedVersion)
  ) {
    throw new Error(
      "AI subject id, capabilities, owner policy and expected version are required",
    );
  }
  const data = await api(
    "PATCH",
    TERMINAL_PATHS.identityAiProfile(aiSubjectId),
    {
      expected_version: expectedVersion,
      capabilities_profile: capabilities,
      owner_policy: ownerPolicy,
    },
    { auth: true, platform: true },
  );
  if (data.version != null && $("identityAiProfileVersion")) {
    $("identityAiProfileVersion").value = String(data.version);
  }
  showJson("adminView", data);
  log("AI employee profile updated", data);
}

async function adminAssignIdentityAi() {
  const aiSubjectId = $("identityAiSubjectId").value.trim();
  if (!aiSubjectId) {
    throw new Error("AI employee subject id is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identityAiAssignments(aiSubjectId),
    { management_policy: "tenant_managed" },
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("AI employee assigned to tenant", data);
}

async function adminReassignIdentityAi() {
  const aiSubjectId = $("identityAiSubjectId").value.trim();
  const mode = $("identityAiReassignMode").value.trim();
  if (!aiSubjectId || !mode) {
    throw new Error("AI employee subject id and reassignment mode are required");
  }
  const body = { mode, management_policy: "tenant_managed" };
  if (mode !== "archive") {
    const toTenantId = $("identityAiToTenantId").value.trim();
    if (!toTenantId) {
      throw new Error("to_tenant_id is required unless mode is archive");
    }
    body.to_tenant_id = toTenantId;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.identityAiReassignments(aiSubjectId),
    body,
    { auth: true, platform: true },
  );
  showJson("adminView", data);
  log("AI employee reassignment submitted", data);
}

async function adminGetOrganizationTenant() {
  const tenantId = $("tenantId").value.trim();
  if (!tenantId) {
    throw new Error("Tenant id is required as path id (trusted Tenant header)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.organizationTenant(tenantId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization tenant fetched", data);
}

async function adminCreateOrganizationEnterprise() {
  const legalName = $("orgEnterpriseLegalName").value.trim();
  if (!legalName) {
    throw new Error("Enterprise legal_name is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.organizationEnterprises,
    { legal_name: legalName },
    { auth: true, platform: false },
  );
  if (data.id && $("orgEnterpriseId")) {
    $("orgEnterpriseId").value = data.id;
  }
  showJson("adminView", data);
  log("Organization enterprise created", data);
}

async function adminListOrganizationEnterprises() {
  const data = await api(
    "GET",
    TERMINAL_PATHS.organizationEnterprises,
    undefined,
    { auth: true, platform: false },
  );
  const first = Array.isArray(data) && data[0] ? data[0] : null;
  if (first && first.id && $("orgEnterpriseId")) {
    $("orgEnterpriseId").value = first.id;
  }
  showJson("adminView", data);
  log("Organization enterprises listed", data);
}

async function adminGetOrganizationEnterprise() {
  const enterpriseId = $("orgEnterpriseId").value.trim();
  if (!enterpriseId) {
    throw new Error("Organization enterprise id is required (create/list first)");
  }
  const data = await api(
    "GET",
    TERMINAL_PATHS.organizationEnterprise(enterpriseId),
    undefined,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization enterprise fetched", data);
}

async function adminUpsertOrganizationUnit() {
  const unitType = $("orgUnitType").value.trim();
  const name = $("orgUnitName").value.trim();
  if (!unitType || !name) {
    throw new Error("Organization unit_type and name are required");
  }
  const body = { unit_type: unitType, name };
  const unitId = $("orgUnitId").value.trim();
  if (unitId) {
    body.unit_id = unitId;
  }
  const enterpriseId = $("orgEnterpriseId").value.trim();
  if (enterpriseId) {
    body.enterprise_id = enterpriseId;
  }
  const parentUnitId = $("orgParentUnitId").value.trim();
  if (parentUnitId) {
    body.parent_unit_id = parentUnitId;
  }
  const data = await api("PUT", TERMINAL_PATHS.organizationUnits, body, {
    auth: true,
    platform: false,
  });
  if (data.id && $("orgUnitId")) {
    $("orgUnitId").value = data.id;
  }
  showJson("adminView", data);
  log("Organization unit upserted", data);
}

async function adminGetOrganizationUnitTree() {
  const rootUnitId = $("orgUnitId").value.trim();
  let path = TERMINAL_PATHS.organizationUnitTree;
  if (rootUnitId) {
    path = `${path}?root_unit_id=${encodeURIComponent(rootUnitId)}`;
  }
  const data = await api("GET", path, undefined, {
    auth: true,
    platform: false,
  });
  showJson("adminView", data);
  log("Organization unit tree fetched", data);
}

async function adminAddOrganizationMembership() {
  const subjectId =
    $("orgMembershipSubjectId").value.trim() || $("subjectId").value.trim();
  if (!subjectId) {
    throw new Error("Membership subject_id is required");
  }
  const body = { subject_id: subjectId };
  const roleLabel = $("orgMembershipRoleLabel").value.trim();
  if (roleLabel) {
    body.membership_role_label = roleLabel;
  }
  const enterpriseId = $("orgEnterpriseId").value.trim();
  if (enterpriseId) {
    body.enterprise_id = enterpriseId;
  }
  const orgUnitId = $("orgUnitId").value.trim();
  if (orgUnitId) {
    body.org_unit_id = orgUnitId;
  }
  const data = await api("POST", TERMINAL_PATHS.organizationMemberships, body, {
    auth: true,
    platform: false,
  });
  if (data.id && $("orgMembershipId")) {
    $("orgMembershipId").value = data.id;
  }
  showJson("adminView", data);
  log("Organization membership added", data);
}

async function adminListOrganizationMemberships() {
  const subjectId =
    $("orgMembershipSubjectId").value.trim() || $("subjectId").value.trim();
  let path = TERMINAL_PATHS.organizationMemberships;
  if (subjectId) {
    path = `${path}?subject_id=${encodeURIComponent(subjectId)}`;
  }
  const data = await api("GET", path, undefined, {
    auth: true,
    platform: false,
  });
  const first = Array.isArray(data) && data[0] ? data[0] : null;
  if (first && first.id && $("orgMembershipId")) {
    $("orgMembershipId").value = first.id;
  }
  showJson("adminView", data);
  log("Organization memberships listed", data);
}

async function adminSetOrganizationUnitStatus() {
  const unitId = $("orgUnitId").value.trim();
  const statusValue = $("orgUnitStatus").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!unitId || !statusValue || !reason) {
    throw new Error("Organization unit id, status and reason are required");
  }
  const body = { status: statusValue, reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "PUT",
    TERMINAL_PATHS.organizationUnitStatus(unitId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization unit status set", data);
}

async function adminSuspendOrganizationMembership() {
  const membershipId = $("orgMembershipId").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!membershipId || !reason) {
    throw new Error("Organization membership id and reason are required");
  }
  const body = { reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.organizationMembershipSuspension(membershipId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization membership suspended", data);
}

async function adminReactivateOrganizationMembership() {
  const membershipId = $("orgMembershipId").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!membershipId || !reason) {
    throw new Error("Organization membership id and reason are required");
  }
  const body = { reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "DELETE",
    TERMINAL_PATHS.organizationMembershipSuspension(membershipId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization membership reactivated", data);
}

async function adminTransferOrganizationMembership() {
  const membershipId = $("orgMembershipId").value.trim();
  const toUnitId = $("orgUnitId").value.trim();
  if (!membershipId || !toUnitId) {
    throw new Error("Organization membership id and target unit id are required");
  }
  const body = { to_org_unit_id: toUnitId };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "PUT",
    TERMINAL_PATHS.organizationMembershipUnit(membershipId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization membership transferred", data);
}

async function adminEndOrganizationMembership() {
  const membershipId = $("orgMembershipId").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!membershipId || !reason) {
    throw new Error("Organization membership id and reason are required");
  }
  const body = { reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "DELETE",
    TERMINAL_PATHS.organizationMembershipEnd(membershipId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization membership ended", data);
}

async function adminSuspendOrganizationEnterprise() {
  const enterpriseId = $("orgEnterpriseId").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!enterpriseId || !reason) {
    throw new Error("Organization enterprise id and reason are required");
  }
  const body = { reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.organizationEnterpriseSuspension(enterpriseId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization enterprise suspended", data);
}

async function adminReactivateOrganizationEnterprise() {
  const enterpriseId = $("orgEnterpriseId").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!enterpriseId || !reason) {
    throw new Error("Organization enterprise id and reason are required");
  }
  const body = { reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "DELETE",
    TERMINAL_PATHS.organizationEnterpriseSuspension(enterpriseId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization enterprise reactivated", data);
}

async function adminCloseOrganizationEnterprise() {
  const enterpriseId = $("orgEnterpriseId").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!enterpriseId || !reason) {
    throw new Error("Organization enterprise id and reason are required");
  }
  const body = { reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "DELETE",
    TERMINAL_PATHS.organizationEnterpriseEnd(enterpriseId),
    body,
    { auth: true, platform: false },
  );
  showJson("adminView", data);
  log("Organization enterprise closed", data);
}

async function adminCreatePlatformTenant() {
  const legalName = $("platformTenantLegalName").value.trim();
  if (!legalName) {
    throw new Error("Platform tenant legal_name is required");
  }
  const body = { legal_name: legalName };
  const regionPolicyRef = $("platformTenantRegionPolicyRef").value.trim();
  if (regionPolicyRef) {
    body.region_policy_ref = regionPolicyRef;
  }
  const data = await api("POST", TERMINAL_PATHS.platformTenants, body, {
    auth: true,
    platform: true,
  });
  if (data.id && $("tenantId")) {
    $("tenantId").value = data.id;
  }
  showJson("adminView", data);
  log("Platform tenant created", data);
}

async function adminSuspendPlatformTenant() {
  const tenantId = $("tenantId").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!tenantId || !reason) {
    throw new Error("Tenant id (path) and reason are required");
  }
  const body = { reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.platformTenantSuspension(tenantId),
    body,
    { auth: true, platform: true },
  );
  showJson("adminView", data);
  log("Platform tenant suspended", data);
}

async function adminReactivatePlatformTenant() {
  const tenantId = $("tenantId").value.trim();
  const reason = $("orgLifecycleReason").value.trim();
  if (!tenantId || !reason) {
    throw new Error("Tenant id (path) and reason are required");
  }
  const body = { reason };
  const versionRaw = $("orgExpectedVersion").value.trim();
  if (versionRaw) {
    const expectedVersion = Number(versionRaw);
    if (Number.isNaN(expectedVersion)) {
      throw new Error("Organization expected_version must be a number");
    }
    body.expected_version = expectedVersion;
  }
  const data = await api(
    "DELETE",
    TERMINAL_PATHS.platformTenantSuspension(tenantId),
    body,
    { auth: true, platform: true },
  );
  showJson("adminView", data);
  log("Platform tenant reactivated", data);
}

async function adminListDeclaredRoles() {
  const data = await api("GET", TERMINAL_PATHS.platformRoles, undefined, {
    auth: true,
    platform: true,
  });
  const first = Array.isArray(data.data) && data.data[0] ? data.data[0] : null;
  if (first && first.id && $("roleCatalogId")) {
    $("roleCatalogId").value = first.id;
  }
  if (first && first.name && $("roleCatalogName")) {
    $("roleCatalogName").value = first.name;
  }
  showJson("adminView", data);
  log("Declared roles listed", data);
}

async function adminUpsertDeclaredRole() {
  const name = $("roleCatalogName").value.trim();
  if (!name) {
    throw new Error("Declared role name is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.platformRoles,
    { name },
    { auth: true, platform: true },
  );
  if (data.data && data.data.id && $("roleCatalogId")) {
    $("roleCatalogId").value = data.data.id;
  }
  showJson("adminView", data);
  log("Declared role upserted", data);
}

async function adminDisableDeclaredRole() {
  const roleId = $("roleCatalogId").value.trim();
  if (!roleId) {
    throw new Error("Declared role id is required (list roles first)");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.platformRoleDisable(roleId),
    {},
    { auth: true, platform: true },
  );
  showJson("adminView", data);
  log("Declared role disabled", data);
}

function requireFedTenantId() {
  const tenantId = $("fedTenantId").value.trim();
  if (!tenantId) {
    throw new Error("Federation tenant id is required (path field)");
  }
  return tenantId;
}

async function adminFederationMatrix() {
  const data = await api("GET", TERMINAL_PATHS.fedMatrix, undefined, {
    auth: true,
    platform: true,
  });
  const cells = data.data && Array.isArray(data.data.cells) ? data.data.cells : [];
  const firstBound = cells.find((cell) => cell && cell.binding_id);
  if (firstBound) {
    if (firstBound.bound_tenant_id && $("fedTenantId")) {
      $("fedTenantId").value = firstBound.bound_tenant_id;
    }
    if (firstBound.issuer && $("fedIssuer")) {
      $("fedIssuer").value = firstBound.issuer;
    }
    if (firstBound.binding_id && $("fedBindingId")) {
      $("fedBindingId").value = firstBound.binding_id;
    }
  }
  showJson("adminView", data);
  log("Federation matrix loaded", data);
}

async function adminListFederationBindings() {
  const tenantId = requireFedTenantId();
  const data = await api("GET", TERMINAL_PATHS.fedBindings(tenantId), undefined, {
    auth: true,
    platform: true,
  });
  const first = Array.isArray(data.data) && data.data[0] ? data.data[0] : null;
  if (first && first.id && $("fedBindingId")) {
    $("fedBindingId").value = first.id;
  }
  showJson("adminView", data);
  log("Federation bindings listed", data);
}

async function adminBindFederationIssuer() {
  const tenantId = requireFedTenantId();
  const issuer = $("fedIssuer").value.trim();
  if (!issuer) {
    throw new Error("Federation issuer URL is required");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.fedBindings(tenantId),
    { issuer },
    { auth: true, platform: true },
  );
  if (data.data && data.data.id && $("fedBindingId")) {
    $("fedBindingId").value = data.data.id;
  }
  showJson("adminView", data);
  log("Federation issuer bound", data);
}

async function adminUnbindFederation() {
  const bindingId = $("fedBindingId").value.trim();
  if (!bindingId) {
    throw new Error("Binding id is required (list bindings first)");
  }
  const data = await api("POST", TERMINAL_PATHS.fedUnbind(bindingId), {}, {
    auth: true,
    platform: true,
  });
  showJson("adminView", data);
  log("Federation binding unbound", data);
}

async function adminSetFederationPriority() {
  const bindingId = $("fedBindingId").value.trim();
  if (!bindingId) {
    throw new Error("Binding id is required (list or matrix first)");
  }
  const raw = $("fedPriority").value.trim();
  if (!raw) {
    throw new Error("Federation priority is required");
  }
  const priority = Number(raw);
  if (!Number.isInteger(priority) || priority < 0) {
    throw new Error("Federation priority must be an integer >= 0");
  }
  const data = await api(
    "POST",
    TERMINAL_PATHS.fedPriority(bindingId),
    { priority },
    { auth: true, platform: true },
  );
  showJson("adminView", data);
  log("Federation priority set", data);
}

function applyAiNote() {
  const note = $("aiNote").value.trim();
  if (!note) {
    throw new Error("Enter a collaboration note first");
  }
  $("intentText").value = note;
  $("aiView").textContent = "Note applied to Operator intent composer.";
  log("AI note applied to intent composer");
  switchSurface("operator");
}

async function composeFromAiNote() {
  applyAiNote();
  await composeIntent();
  showJson("aiView", { intent_id: state.intentId, note: $("aiNote").value.trim() });
}

function syncExtensionButtons() {
  setEnabled("btnExtActivate", Boolean(state.extensionId));
  setEnabled("btnExtMount", Boolean(state.extensionId));
  setEnabled("btnExtWorker", Boolean(state.extensionId));
  setEnabled("btnExtInvoke", Boolean(state.extensionId));
  setEnabled("btnExtRevoke", Boolean(state.extensionId));
}

function setExtensionHostStatus(text) {
  const node = $("extHostStatus");
  if (node) {
    node.textContent = text;
  }
}

async function hydrateSignedExtensionHost({ quiet = false } = {}) {
  const subject = $("subjectId")?.value?.trim();
  const tenant = $("tenantId")?.value?.trim();
  if (!subject || !tenant) {
    setExtensionHostStatus("Set Subject/Tenant (or demo bootstrap) before hydrate.");
    return false;
  }
  const data = await api("GET", TERMINAL_PATHS.extensions);
  const items = Array.isArray(data?.data) ? data.data : [];
  const keyHint =
    ($("extKey")?.value || "").trim() || state.extensionKeyHint || "noventi.demo.panel";
  let match = null;
  if (state.extensionId) {
    match = items.find((item) => item.id === state.extensionId) || null;
  }
  if (!match) {
    match =
      items.find(
        (item) => item.extension_key === keyHint && item.status === "active",
      ) ||
      items.find((item) => item.extension_key === keyHint) ||
      items.find((item) => item.status === "active") ||
      null;
  }
  if (!match) {
    state.extensionHydrated = false;
    setExtensionHostStatus("No signed extension found for this tenant.");
    showJson("extView", data);
    if (!quiet) {
      log("Extension hydrate empty", data);
    }
    syncExtensionButtons();
    return false;
  }
  state.extensionId = match.id;
  state.extensionKeyHint = match.extension_key || keyHint;
  state.extensionHydrated = match.status === "active";
  if ($("extKey")) {
    $("extKey").value = match.extension_key || keyHint;
  }
  if ($("extVersion") && match.version) {
    $("extVersion").value = match.version;
  }
  setExtensionHostStatus(
    `Hydrated ${match.extension_key}@${match.version} (${match.status}) · id ${match.id}`,
  );
  syncExtensionButtons();
  showJson("extView", { hydrated: match, list: items });
  if (!quiet) {
    log("Signed extension hydrated (PHX-G169)", match);
  }
  return true;
}

function parseBridgeMessage(data) {
  if (!data || typeof data !== "object") {
    throw new Error("extension bridge payload must be an object");
  }
  for (const key of FORBIDDEN_BODY_KEYS) {
    if (Object.prototype.hasOwnProperty.call(data, key)) {
      throw new Error("extension bridge cannot elevate trusted context");
    }
  }
  if (!ALLOWED_BRIDGE_MESSAGE_TYPES.includes(data.type)) {
    throw new Error("extension bridge message type is not allowlisted");
  }
  if (Object.prototype.hasOwnProperty.call(data, "channel")) {
    const channel = String(data.channel || "").trim();
    if (!ALLOWED_BRIDGE_CHANNELS.includes(channel)) {
      throw new Error("extension bridge channel is not allowlisted");
    }
  }
  const action = String(data.action || "").trim();
  const surface = String(data.surface || "").trim();
  if (!action || !surface) {
    throw new Error("extension bridge requires action and surface");
  }
  return { action, surface };
}

async function dispatchBridgeInvoke(payload, reply) {
  const { action, surface } = parseBridgeMessage(payload);
  if (!state.extensionId) {
    throw new Error("Register an extension first");
  }
  const data = await api("POST", TERMINAL_PATHS.extensionActions(state.extensionId), {
    action,
    surface,
  });
  showJson("extView", data);
  log("Extension bridge invoke", data);
  if (typeof reply === "function") {
    reply({
      type: "eaos.extension.invoke.result",
      ok: true,
      data,
    });
  }
  return data;
}

function unmountExtensionFrame() {
  const host = $("extFrameHost");
  const frame = $("extFrame");
  if (frame) {
    frame.removeAttribute("src");
  }
  if (host) {
    host.hidden = true;
  }
  state.extensionFrameMounted = false;
}

function mountExtensionFrame() {
  if (!state.extensionId) {
    throw new Error("Register an extension first");
  }
  const host = $("extFrameHost");
  const frame = $("extFrame");
  if (!host || !frame) {
    throw new Error("Extension iframe host missing");
  }
  const src = `${EXTENSION_DEMO_PANEL_SRC}?extension_id=${encodeURIComponent(
    state.extensionId
  )}`;
  frame.src = src;
  host.hidden = false;
  state.extensionFrameMounted = true;
  log("Extension iframe mounted", { src, sandbox: "allow-scripts" });
}

async function handleExtensionBridgeMessage(event) {
  const frame = $("extFrame");
  if (!frame || !state.extensionFrameMounted) {
    return;
  }
  if (event.source !== frame.contentWindow) {
    return;
  }
  if (event.origin !== "null" && event.origin !== window.location.origin) {
    return;
  }
  try {
    await dispatchBridgeInvoke(event.data, (result) => {
      if (frame.contentWindow) {
        frame.contentWindow.postMessage(result, "*");
      }
    });
  } catch (err) {
    const message = String(err.message || err);
    log("Extension bridge denied", { message });
    if (frame.contentWindow) {
      frame.contentWindow.postMessage(
        {
          type: "eaos.extension.invoke.result",
          ok: false,
          error: message,
        },
        "*"
      );
    }
  }
}

function stopExtensionWorker() {
  if (state.extensionWorker) {
    state.extensionWorker.terminate();
    state.extensionWorker = null;
    log("Extension worker stopped");
  }
}

async function startExtensionWorker() {
  if (!state.extensionId) {
    throw new Error("Register an extension first");
  }
  if (typeof Worker === "undefined") {
    throw new Error("Worker runtime unavailable in this environment");
  }
  stopExtensionWorker();
  const worker = new Worker(EXTENSION_DEMO_WORKER_SRC);
  worker.onmessage = (event) => {
    handleExtensionWorkerMessage(event).catch((err) => {
      log("Extension worker bridge error", { message: String(err.message || err) });
    });
  };
  state.extensionWorker = worker;
  worker.postMessage({ type: "eaos.extension.worker.ping" });
  log("Extension worker started", { src: EXTENSION_DEMO_WORKER_SRC });
}

async function handleExtensionWorkerMessage(event) {
  if (!state.extensionWorker || event.target !== state.extensionWorker) {
    return;
  }
  try {
    await dispatchBridgeInvoke(event.data, (result) => {
      if (state.extensionWorker) {
        state.extensionWorker.postMessage(result);
      }
    });
  } catch (err) {
    const message = String(err.message || err);
    log("Extension worker bridge denied", { message });
    if (state.extensionWorker) {
      state.extensionWorker.postMessage({
        type: "eaos.extension.invoke.result",
        ok: false,
        error: message,
      });
    }
  }
}

async function registerExtension() {
  const data = await api("POST", TERMINAL_PATHS.extensions, {
    extension_key: $("extKey").value.trim(),
    version: $("extVersion").value.trim(),
    signature_ref: $("extSignature").value.trim(),
    declared_actions: ["panel.render"],
    allowed_surfaces: ["extensions"],
    data_scope: $("extScope").value.trim(),
  });
  state.extensionId = uuidFromResult(data);
  syncExtensionButtons();
  showJson("extView", data);
  log("Extension registered", data);
  await listExtensions();
}

async function listExtensions() {
  const data = await api("GET", TERMINAL_PATHS.extensions);
  showJson("extView", data);
  log("Extensions listed", data);
}

async function activateExtension() {
  if (!state.extensionId) {
    throw new Error("Register an extension first");
  }
  const data = await api("POST", TERMINAL_PATHS.extensionActivate(state.extensionId));
  showJson("extView", data);
  log("Extension activated", data);
  mountExtensionFrame();
}

async function invokeExtension() {
  if (!state.extensionId) {
    throw new Error("Register an extension first");
  }
  const data = await api("POST", TERMINAL_PATHS.extensionActions(state.extensionId), {
    action: "panel.render",
    surface: "extensions",
  });
  showJson("extView", data);
  log("Extension invoke (sandboxed)", data);
}

async function revokeExtension() {
  if (!state.extensionId) {
    throw new Error("Register an extension first");
  }
  const data = await api("POST", TERMINAL_PATHS.extensionRevoke(state.extensionId));
  unmountExtensionFrame();
  stopExtensionWorker();
  showJson("extView", data);
  log("Extension revoked", data);
}

function bind(id, handler) {
  const node = $(id);
  if (!node) {
    return;
  }
  node.addEventListener("click", async () => {
    try {
      await handler();
    } catch (err) {
      log("Error", { message: String(err.message || err) });
    }
  });
}

function boot() {
  seedDefaults();
  applyOidcFragment();
  setStep("session");
  syncButtons();
  renderProductCatalog();
  renderOpsQueue();
  switchSurface(surfaceFromHash());
  loadDemoBootstrap()
    .then(() => loadPackageSurfaces())
    .catch((err) => {
      log("Demo/package bootstrap error", { message: String(err.message || err) });
    });

  document.querySelectorAll(".surface-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      switchSurface(tab.dataset.surface);
      if (tab.dataset.surface === "product" || tab.dataset.surface === "ops") {
        loadPackageSurfaces().catch(() => {});
      }
    });
  });
  window.addEventListener("hashchange", () => switchSurface(surfaceFromHash()));

  bind("btnProductHandoff", handoffSelectedProduct);
  bind("btnCrmRefreshCustomers", async () => {
    await loadCrmPermissions();
    await loadCrmCustomers();
  });
  bind("btnCrmRefreshCustomer360", () => loadCrmCustomer360());
  bind("btnCrmMoreCustomers", () => loadCrmCustomers({ append: true }));
  bind("btnCrmMoreContacts", () => loadCrmContacts({ append: true }));
  bind("btnCrmRefreshOpportunities", () => loadCrmOpportunities());
  bind("btnCrmMoreOpportunities", () =>
    loadCrmOpportunities({ append: true }),
  );
  bind("btnCrmRefreshRequirements", () => loadCrmRequirements());
  bind("btnCrmMoreRequirements", () =>
    loadCrmRequirements({ append: true }),
  );
  bind("btnCrmRefreshQuotes", () => loadCrmQuotes());
  bind("btnCrmMoreQuotes", () => loadCrmQuotes({ append: true }));
  bind("btnCrmRefreshQuoteLines", () => loadCrmQuoteLines());
  bind("btnCrmNewCustomer", () => openCrmCustomerEditor("create"));
  bind("btnCrmEditCustomer", () => openCrmCustomerEditor("edit"));
  bind("btnCrmArchiveCustomer", () => openCrmArchiveEditor("customer"));
  bind("btnCrmNewContact", () => openCrmContactEditor("create"));
  bind("btnCrmEditContact", () => openCrmContactEditor("edit"));
  bind("btnCrmArchiveContact", () => openCrmArchiveEditor("contact"));
  bind("btnCrmNewOpportunity", () => openCrmOpportunityEditor("create"));
  bind("btnCrmEditOpportunity", () => openCrmOpportunityEditor("edit"));
  bind("btnCrmArchiveOpportunity", () =>
    openCrmArchiveEditor("opportunity"),
  );
  bind("btnCrmNewRequirement", () => openCrmRequirementEditor("create"));
  bind("btnCrmEditRequirement", () => openCrmRequirementEditor("edit"));
  bind("btnCrmArchiveRequirement", () =>
    openCrmArchiveEditor("requirement"),
  );
  bind("btnCrmNewQuote", () => openCrmQuoteEditor("create"));
  bind("btnCrmEditQuote", () => openCrmQuoteEditor("edit"));
  bind("btnCrmArchiveQuote", () => openCrmArchiveEditor("quote"));
  bind("btnCrmNewQuoteLine", () => openCrmQuoteLineEditor("create"));
  bind("btnCrmEditQuoteLine", () => openCrmQuoteLineEditor("edit"));
  bind("btnCrmArchiveQuoteLine", () =>
    openCrmArchiveEditor("quoteLine"),
  );
  bind("btnCrmIssueQuote", () => openCrmIssueQuoteEditor());
  bind("btnCrmConvertQuote", () => openCrmConvertEditor());
  bind("btnCrmRefreshConversion", () => loadCrmConversion());
  bind("btnCrmCreateSalesOrder", () => openCrmCreateSoEditor());
  bind("btnCrmConfirmSalesOrder", () => openCrmConfirmSalesOrderEditor());
  bind("btnCrmCreateDeliveryOrder", () => openCrmCreateDeliveryOrderEditor());
  bind("btnCrmReleaseDeliveryOrder", () =>
    openCrmReleaseDeliveryOrderEditor(),
  );
  bind("btnCrmCreateArInvoice", () => openCrmCreateArInvoiceEditor());
  bind("btnCrmCreateReturnAuthorization", () =>
    openCrmCreateReturnAuthorizationEditor(),
  );
  bind("btnCrmRefreshDeliveryOrder", () => refreshCrmDeliveryOrder());
  bind("btnCrmIssueArInvoice", () => openCrmIssueArInvoiceEditor());
  bind("btnCrmVoidArInvoice", () => openCrmVoidArInvoiceEditor());
  bind("btnCrmRefreshArInvoice", () => refreshCrmArInvoice());
  bind("btnCrmRefreshReturnAuthorization", () =>
    refreshCrmReturnAuthorization(),
  );
  bind("btnCrmRefreshSalesOrders", () => loadCrmSalesOrders());
  bind("btnCrmMoreSalesOrders", () =>
    loadCrmSalesOrders({ append: true }),
  );
  bind("btnCrmCancelCustomer", closeCrmEditors);
  bind("btnCrmCancelContact", closeCrmEditors);
  bind("btnCrmCancelArchive", closeCrmEditors);
  bind("btnCrmCancelOpportunity", closeCrmEditors);
  bind("btnCrmCancelRequirement", closeCrmEditors);
  bind("btnCrmCancelQuote", closeCrmEditors);
  bind("btnCrmCancelQuoteLine", closeCrmEditors);
  bind("btnCrmCancelIssueQuote", closeCrmEditors);
  bind("btnCrmCancelConvert", closeCrmEditors);
  bind("btnCrmCancelCreateSo", closeCrmEditors);
  bind("btnCrmCancelConfirmSo", closeCrmEditors);
  bind("btnCrmCancelCreateDo", closeCrmEditors);
  bind("btnCrmCancelReleaseDo", closeCrmEditors);
  bind("btnCrmCancelCreateArInvoice", closeCrmEditors);
  bind("btnCrmCancelIssueArInvoice", closeCrmEditors);
  bind("btnCrmCancelVoidArInvoice", closeCrmEditors);
  bind("btnCrmCancelCreateReturnAuthorization", closeCrmEditors);
  $("crmCustomerForm").addEventListener("submit", submitCrmCustomer);
  $("crmContactForm").addEventListener("submit", submitCrmContact);
  $("crmArchiveForm").addEventListener("submit", submitCrmArchive);
  $("crmOpportunityForm").addEventListener("submit", submitCrmOpportunity);
  $("crmRequirementForm").addEventListener("submit", submitCrmRequirement);
  $("crmQuoteForm").addEventListener("submit", submitCrmQuote);
  $("crmQuoteLineForm").addEventListener("submit", submitCrmQuoteLine);
  $("crmIssueQuoteForm").addEventListener("submit", submitCrmIssueQuote);
  $("crmConvertForm").addEventListener("submit", submitCrmConvert);
  $("crmCreateSoForm").addEventListener("submit", submitCrmCreateSo);
  $("crmConfirmSoForm").addEventListener("submit", submitCrmConfirmSalesOrder);
  $("crmCreateDoForm").addEventListener("submit", submitCrmCreateDeliveryOrder);
  $("crmReleaseDoForm").addEventListener(
    "submit",
    submitCrmReleaseDeliveryOrder,
  );
  $("crmCreateArInvoiceForm").addEventListener(
    "submit",
    submitCrmCreateArInvoice,
  );
  $("crmIssueArInvoiceForm").addEventListener(
    "submit",
    submitCrmIssueArInvoice,
  );
  $("crmVoidArInvoiceForm").addEventListener("submit", submitCrmVoidArInvoice);
  $("crmCreateReturnAuthorizationForm").addEventListener(
    "submit",
    submitCrmCreateReturnAuthorization,
  );
  bind("btnOpsComposeBrief", composeOpsBriefAndHandoff);
  bind("btnOpsHandoffSelected", handoffSelectedOpsItem);
  bind("btnSampleFlowHandoff", handoffSelectedSampleFlow);
  bind("btnOrderFlowHandoff", handoffSelectedOrderFlow);
  renderSampleFlowQueue();
  renderOrderFlowQueue();
  bind("btnOpenSession", openSession);
  bind("btnRefreshSession", refreshSession);
  bind("btnCloseSession", closeSession);
  bind("btnComposeIntent", composeIntent);
  bind("btnRefreshIntent", refreshIntent);
  bind("btnBuildPreview", buildPreview);
  bind("btnRefreshPreview", refreshPreview);
  bind("btnCommit", commitPreview);
  bind("btnRequestApproval", requestApproval);
  bind("btnPresentApproval", presentApproval);
  bind("btnAdminHealth", () => adminProbe(TERMINAL_PATHS.health, "Health"));
  bind("btnAdminRelease", () => adminProbe(TERMINAL_PATHS.release, "Release"));
  bind("btnAdminAdapters", () => adminProbe(TERMINAL_PATHS.adapters, "Adapters"));
  bind("btnAdminContext", () => adminProbe(TERMINAL_PATHS.context, "Context"));
  bind("btnAdminContextEcho", adminContextEchoElevationReject);
  bind("btnAdminIdp", () => adminProbe(TERMINAL_PATHS.idpStatus, "IdP / JWT status"));
  bind("btnAdminJwtStatus", () => adminProbe(TERMINAL_PATHS.jwtStatus, "JWT status"));
  bind("btnAdminMarketplaceStatus", () =>
    adminProbe(TERMINAL_PATHS.marketplaceStatus, "Marketplace status"),
  );
  bind("btnAdminHostAcquireStatus", () => loadHostAcquireStatus());
  bind("btnAdminPaymentClearingStatus", () => loadPaymentClearingStatus());
  bind("btnAdminDomainFoundationStatus", () => loadDomainFoundationStatus());
  bind("btnAdminFinancePlatformStatus", () => loadFinancePlatformStatus());
  bind("btnAdminEventOutboxStatus", () => loadEventOutboxStatus());
  bind("btnAdminPackageResolveAlignStatus", () => loadPackageResolveAlignStatus());
  bind("btnAdminRoleCatalogStatus", () => loadRoleCatalogStatus());
  bind("btnRoleCatalogStatusRefresh", () => loadRoleCatalogStatus());
  bind("btnAdminListingCreate", adminCreateListing);
  bind("btnAdminListingGet", adminGetListing);
  bind("btnAdminListingSignature", adminAttachListingSignature);
  bind("btnAdminListingSubmit", adminSubmitListing);
  bind("btnAdminListingReview", adminReviewApproveListing);
  bind("btnAdminListingPublish", adminPublishListing);
  bind("btnAdminListingAcquire", adminAcquireListing);
  bind("btnAdminListingAcquireHost", adminAcquireListingToHost);
  bind("btnAdminListingRevoke", adminRevokeListing);
  bind("btnAdminListingSetPricing", adminSetListingPricing);
  bind("btnAdminListingCreateInvoice", adminCreateListingInvoice);
  bind("btnAdminListingPaymentClearing", adminCreateListingPaymentClearing);
  bind("btnAdminListingOpenDispute", adminOpenListingDispute);
  bind("btnAdminListingResolveDispute", adminResolveListingDispute);
  bind("btnAdminListingSetRevenueShare", adminSetListingRevenueShare);
  bind("btnAdminWorkflowStatus", () =>
    adminProbe(TERMINAL_PATHS.workflowStatus, "Workflow status"),
  );
  bind("btnAdminWorkflowCreateDefinition", adminCreateWorkflowDefinition);
  bind("btnAdminWorkflowDeprecateDefinition", adminDeprecateWorkflowDefinition);
  bind("btnAdminWorkflowStartInstance", adminStartWorkflowInstance);
  bind("btnAdminWorkflowGetInstance", adminGetWorkflowInstance);
  bind("btnAdminWorkflowListTasks", adminListWorkflowTasks);
  bind("btnAdminWorkflowApproveTask", adminApproveWorkflowTask);
  bind("btnAdminWorkflowRejectTask", adminRejectWorkflowTask);
  bind("btnAdminWorkflowSignalInstance", adminSignalWorkflowInstance);
  bind("btnAdminWorkflowCancelInstance", adminCancelWorkflowInstance);
  bind("btnAdminWorkflowCompensateInstance", adminCompensateWorkflowInstance);
  bind("btnAdminWorkflowEscalateTask", adminEscalateWorkflowTask);
  bind("btnAdminPackageStatus", () =>
    adminProbe(TERMINAL_PATHS.packageStatus, "Package status"),
  );
  bind("btnAdminPackageRegisterManifest", adminRegisterPackageManifest);
  bind("btnAdminPackageGetManifest", adminGetPackageManifest);
  bind("btnAdminPackageListSurfaces", adminListPackageSurfaces);
  bind("btnAdminPackagePublishManifest", adminPublishPackageManifest);
  bind("btnAdminPackageInstall", adminInstallPackage);
  bind("btnAdminPackageDisableInstallation", adminDisablePackageInstallation);
  bind("btnAdminPackageResolveAction", adminResolvePackageAction);
  bind("btnAdminKnowledgeStatus", () =>
    adminProbe(TERMINAL_PATHS.knowledgeStatus, "Knowledge status"),
  );
  bind("btnAdminKnowledgeUpsertEntity", adminUpsertKnowledgeEntity);
  bind("btnAdminKnowledgeGetEntity", adminGetKnowledgeEntity);
  bind("btnAdminKnowledgeListEntities", adminListKnowledgeEntities);
  bind("btnAdminKnowledgeArchiveEntity", adminArchiveKnowledgeEntity);
  bind("btnAdminKnowledgeShareEntity", adminShareKnowledgeEntity);
  bind("btnAdminKnowledgeSearch", adminSearchKnowledge);
  bind("btnAdminKnowledgeCreateLink", adminCreateKnowledgeLink);
  bind("btnAdminKnowledgeGetProvenance", adminGetKnowledgeProvenance);
  bind("btnAdminTwinStatus", () =>
    adminProbe(TERMINAL_PATHS.twinStatus, "Twin status"),
  );
  bind("btnAdminTwinUpsertSnapshot", adminUpsertTwinSnapshot);
  bind("btnAdminTwinGetSnapshot", adminGetTwinSnapshot);
  bind("btnAdminTwinAuthorize", adminAuthorizeFromTwin);
  bind("btnAdminBrainStatus", () =>
    adminProbe(TERMINAL_PATHS.brainStatus, "Brain status"),
  );
  bind("btnAdminBrainPublishInsight", adminPublishBrainInsight);
  bind("btnAdminBrainGetInsight", adminGetBrainInsight);
  bind("btnAdminBrainExecute", adminExecuteBrainInsight);
  bind("btnAdminAiStatus", () =>
    adminProbe(TERMINAL_PATHS.aiStatus, "AI Runtime status"),
  );
  bind("btnAdminAiCreateRun", adminCreateAiRun);
  bind("btnAdminAiGetRun", adminGetAiRun);
  bind("btnAdminAiRegisterTool", adminRegisterAiTool);
  bind("btnAdminAiInvokeTool", adminInvokeAiTool);
  bind("btnAdminAiWriteMemory", adminWriteAiMemory);
  bind("btnAdminAiReadMemory", adminReadAiMemory);
  bind("btnAdminAiRequestApproval", adminRequestAiApproval);
  bind("btnAdminAiCommit", adminCommitAiAction);
  bind("btnAdminIdentityStatus", () =>
    adminProbe(TERMINAL_PATHS.identityStatus, "Identity status"),
  );
  bind("btnAdminIdentityRegisterSubject", adminRegisterIdentitySubject);
  bind("btnAdminIdentityResolveSubject", adminResolveIdentitySubject);
  bind("btnAdminIdentityBindCredential", adminBindIdentityCredential);
  bind("btnAdminIdentityCreateSession", adminCreateIdentitySession);
  bind("btnAdminIdentityValidateSession", adminValidateIdentitySession);
  bind("btnAdminIdentityValidateCredential", adminValidateIdentityCredential);
  bind("btnAdminIdentityRevokeCredential", adminRevokeIdentityCredential);
  bind("btnAdminIdentityRevokeSession", adminRevokeIdentitySession);
  bind("btnAdminIdentityGrantGovernor", adminGrantIdentityGovernor);
  bind("btnAdminIdentityRevokeGovernor", adminRevokeIdentityGovernor);
  bind("btnAdminIdentityRegisterAi", adminRegisterIdentityAi);
  bind("btnAdminIdentityGetAiProfile", adminGetIdentityAiProfile);
  bind("btnAdminIdentityUpdateAiProfile", adminUpdateIdentityAiProfile);
  bind("btnAdminIdentityAssignAi", adminAssignIdentityAi);
  bind("btnAdminIdentityReassignAi", adminReassignIdentityAi);
  bind("btnAdminOrganizationStatus", () =>
    adminProbe(TERMINAL_PATHS.organizationStatus, "Organization status"),
  );
  bind("btnAdminOrganizationGetTenant", adminGetOrganizationTenant);
  bind("btnAdminOrganizationCreateEnterprise", adminCreateOrganizationEnterprise);
  bind("btnAdminOrganizationListEnterprises", adminListOrganizationEnterprises);
  bind("btnAdminOrganizationGetEnterprise", adminGetOrganizationEnterprise);
  bind("btnAdminOrganizationUpsertUnit", adminUpsertOrganizationUnit);
  bind("btnAdminOrganizationUnitTree", adminGetOrganizationUnitTree);
  bind("btnAdminOrganizationAddMembership", adminAddOrganizationMembership);
  bind("btnAdminOrganizationListMemberships", adminListOrganizationMemberships);
  bind("btnAdminOrganizationSetUnitStatus", adminSetOrganizationUnitStatus);
  bind("btnAdminOrganizationSuspendMembership", adminSuspendOrganizationMembership);
  bind(
    "btnAdminOrganizationReactivateMembership",
    adminReactivateOrganizationMembership,
  );
  bind(
    "btnAdminOrganizationTransferMembership",
    adminTransferOrganizationMembership,
  );
  bind("btnAdminOrganizationEndMembership", adminEndOrganizationMembership);
  bind(
    "btnAdminOrganizationSuspendEnterprise",
    adminSuspendOrganizationEnterprise,
  );
  bind(
    "btnAdminOrganizationReactivateEnterprise",
    adminReactivateOrganizationEnterprise,
  );
  bind("btnAdminOrganizationCloseEnterprise", adminCloseOrganizationEnterprise);
  bind("btnAdminPlatformCreateTenant", adminCreatePlatformTenant);
  bind("btnAdminPlatformSuspendTenant", adminSuspendPlatformTenant);
  bind("btnAdminPlatformReactivateTenant", adminReactivatePlatformTenant);
  bind("btnAdminIdpList", adminListIdpIssuers);
  bind("btnAdminIdpRegister", adminRegisterIdpIssuer);
  bind("btnAdminIdpDisable", adminDisableIdpIssuer);
  bind("btnAdminIdpDiscoverySync", adminDiscoverySync);
  bind("btnAdminTenantRoles", adminListTenantRolesCatalog);
  bind("btnAdminRolesStatus", adminRolesStatus);
  bind("btnAdminEvaluate", adminEvaluatePermission);
  bind("btnAdminExplainDecision", adminExplainLastDecision);
  bind("btnAdminEffectivePerms", adminListEffectivePermissions);
  bind("btnAdminPermissionCreatePolicy", adminCreatePermissionPolicy);
  bind("btnAdminPermissionActivatePolicy", adminActivatePermissionPolicy);
  bind("btnAdminPermissionCreateGrant", adminCreatePermissionGrant);
  bind("btnAdminPermissionRevokeGrant", adminRevokePermissionGrant);
  bind("btnAdminPermissionDeprecatePolicy", adminDeprecatePermissionPolicy);
  bind("btnAdminPermissionDelegateGrant", adminDelegatePermissionGrant);
  bind("btnAdminEventStats", adminEventDeliveryStats);
  bind("btnAdminEventCatalog", adminEventCatalog);
  bind("btnAdminDeadLetters", adminListDeadLetters);
  bind("btnAdminReplayDeadLetter", adminReplayDeadLetter);
  bind("btnAdminEventDispatch", adminDispatchDueEvents);
  bind("btnAdminEventGet", adminGetEvent);
  bind("btnAdminEventEnqueue", adminEnqueueOutbox);
  bind("btnAdminEventPublish", adminPublishEvent);
  bind("btnAdminEventSubscribe", adminSubscribeEvent);
  bind("btnAdminEventReplay", adminReplayEvent);
  bind("btnAdminRoleList", adminListDeclaredRoles);
  bind("btnAdminRoleUpsert", adminUpsertDeclaredRole);
  bind("btnAdminRoleDisable", adminDisableDeclaredRole);
  bind("btnAdminFedMatrix", adminFederationMatrix);
  bind("btnAdminFedList", adminListFederationBindings);
  bind("btnAdminFedBind", adminBindFederationIssuer);
  bind("btnAdminFedUnbind", adminUnbindFederation);
  bind("btnAdminFedPriority", adminSetFederationPriority);
  bind("btnAiApplyNote", applyAiNote);
  bind("btnAiCompose", composeFromAiNote);
  bind("btnExtHydrate", () => hydrateSignedExtensionHost());
  bind("btnExtHostAcquire", () => extAcquireListingToHost());
  bind("btnExtHostPathReadiness", () => loadExtHostPathReadiness());
  bind("btnExtRegister", registerExtension);
  bind("btnExtList", listExtensions);
  bind("btnExtActivate", activateExtension);
  bind("btnExtMount", mountExtensionFrame);
  bind("btnExtWorker", startExtensionWorker);
  bind("btnExtInvoke", invokeExtension);
  bind("btnExtRevoke", revokeExtension);
  bind("btnOidcRefresh", oidcRefreshBearer);
  bind("btnOidcLogout", oidcLogoutBearer);
  bind("btnClearBearer", clearBearer);
  loadOidcProviderLinks().catch(() => {});
  loadOidcMfaEnrollmentLink().catch(() => {});
  loadOidcLoginProductPosture().catch(() => {});
  loadWebauthnProductPosture().catch(() => {});
  loadRoleGrantProductPosture().catch(() => {});
  loadRoleCatalogStatus({ quiet: true }).catch(() => {});
  loadOpenapiInventoryProductPosture({ quiet: true }).catch(() => {});
  loadSampleKnowledgePackProductPosture({ quiet: true }).catch(() => {});
  bind("btnOpenapiInventoryRefresh", () => loadOpenapiInventoryProductPosture());
  bind("btnAdminOpenapiInventoryStatus", () => loadOpenapiInventoryProductPosture());
  bind("btnSampleKnowledgePackRefresh", () =>
    loadSampleKnowledgePackProductPosture(),
  );
  bind("btnAdminSampleKnowledgePackStatus", () =>
    loadSampleKnowledgePackProductPosture(),
  );
  syncExtensionButtons();
  window.addEventListener("message", (event) => {
    handleExtensionBridgeMessage(event).catch((err) => {
      log("Extension bridge error", { message: String(err.message || err) });
    });
  });

  log("Complete Terminal UI ready", {
    surfaces: SURFACES,
    note: "Presentation-only; OIDC Bearer optional; Extension iframe/Worker + CSP Foundation",
  });
}

if (typeof document !== "undefined") {
  boot();
}
