"""Foundation OpenAPI inventory product posture (PHX-G148 → PHX-G193).

Read-only helper. Surfaces contract count, adapter registry alignment,
route-mount parity vs semantic completeness, and which gateway domains have
thin HTTP probes vs deferred catalog domains.

PHX-G164: mount parity complete; high-value semantic deepen started.
PHX-G166: semantic remainder deepen (identity/org/permission/package/terminal/
workflow → GatewayDetailError).
PHX-G170: UuidResult dual-key unification (``id`` + ``data``); fence closed.
PHX-G174: auth/platform/marketplace KernelError → GatewayDetailError.
PHX-G176: platform IdP/roles named status-code honesty (400/404/409/503).
PHX-G177: auth OIDC login/callback/refresh/logout named status-code honesty.
PHX-G178: identity/organization named status-code honesty.
PHX-G179: permission/workflow named status-code honesty.
PHX-G180: package/terminal/knowledge named status-code honesty.
PHX-G181: ai/event/brain/marketplace named status-code honesty.
PHX-G185: auth/permission product-posture schema field parity.
PHX-G186: marketplace status body field parity (PaymentClearingProduct /
FoundationStatusData).
PHX-G187: OIDC login product-posture schema field parity.
PHX-G188: JWT status body field parity (JwtStatusData / JwtDenylistPosture).
PHX-G189: IdP status body field parity (IdpStatusData top-level + aggregates).
PHX-G190: OIDC status body field parity (OidcStatusData; nested under IdP).
PHX-G191: Brain/Twin/AI/Workflow status body field parity (fail-closed fences).
PHX-G192: Identity/Org/Knowledge status body field parity.
PHX-G193: Package status parity + Terminal/Event status mounts.
``full_openapi_http_complete`` stays false (remaining semantic gaps).
"""

from __future__ import annotations

from typing import Any

from api.adapters import list_adapters
from eaos_sdk.catalog import list_openapi_contracts

# Domains with mounted thin Gateway HTTP probes (routers / ops meta).
_THIN_PROBE_DOMAINS = (
    "identity",
    "organization",
    "permission",
    "workflow",
    "knowledge",
    "event",
    "ai",
    "terminal",
    "package",
    "brain",
    "marketplace",
    "auth",
    "platform",
    "ops",
)

_KNOWN_DEFER_FENCES = (
    "full_openapi_semantic_parity_t0188",
    "webauthn_attestation_crypto_verify",
    "role_grant_cap_neq_grant_invariant",
    "marketplace_payment_external_psp_and_arbitration",
    "brain_execute",
    "twin_authorize",
)

_FAIL_CLOSED_REASONS = (
    "inventory_posture_does_not_claim_semantic_complete",
    "full_openapi_semantic_surface_still_deferred",
    "uuid_result_dual_key_unified_g170",
    "auth_platform_marketplace_gateway_detail_aligned_g174",
    "platform_idp_roles_status_codes_honest_g176",
    "auth_oidc_status_codes_honest_g177",
    "identity_org_status_codes_honest_g178",
    "permission_workflow_status_codes_honest_g179",
    "package_terminal_knowledge_status_codes_honest_g180",
    "ai_event_brain_marketplace_status_codes_honest_g181",
    "auth_permission_product_posture_schemas_honest_g185",
    "marketplace_status_body_field_parity_g186",
    "oidc_login_product_posture_schema_honest_g187",
    "jwt_status_body_field_parity_g188",
    "idp_status_body_field_parity_g189",
    "oidc_status_body_field_parity_g190",
    "brain_twin_ai_workflow_status_body_field_parity_g191",
    "identity_org_knowledge_status_body_field_parity_g192",
    "package_terminal_event_status_mount_parity_g193",
    "role_catalog_status_source_counts_field_parity_g195",
    "role_grant_auto_write_response_detail_parity_g196",
    "ops_gateway_detail_error_parity_g197",
    "terminal_extension_list_response_parity_g198",
    "terminal_extension_invoke_response_parity_g199",
    "success_response_catalog_closed_semantic_partial_g200",
    "errorbody_details_inventory_closed_g202",
    "error_details_fields_shape_honest_g204",
    "single_enum_const_honest_g206",
    "elevation_details_code_shape_honest_g208",
    "oidc_details_code_shapes_honest_g210",
    "host_acquire_details_code_shape_honest_g212",
    "oidc_mfa_enrollment_details_honest_g214",
    "error_details_description_key_honest_g216",
    "named_details_ref_composition_honest_g218",
    "cross_domain_elevation_details_ref_honest_g220",
    "stub_detail_const_honest_g222",
    "named_success_envelopes_honest_g224",
    "host_acquire_payload_named_honest_g226",
    "nested_data_payload_named_honest_g228",
    "federation_matrix_payload_named_honest_g230",
    "nested_anon_ge2_payload_named_honest_g232",
    "count_meta_and_oidc_providers_payload_named_honest_g234",
    "opaque_auth_array_items_named_honest_g236",
    "discovery_registry_write_posture_named_honest_g238",
    "webauthn_public_key_creation_options_named_honest_g240",
    "webauthn_register_verify_response_closed_g242",
    "oidc_amr_acr_details_closed_g244",
    "idp_jwks_document_named_honest_g246",
    "webauthn_verify_denial_honest_g248",
    "role_grant_no_match_denial_honest_g250",
    "payment_clearing_stub_error_envelope_honest_g252",
    "payment_clearing_success_schemas_closed_g254",
    "uuid_boolean_ok_result_schemas_closed_g256",
    "marketplace_write_listing_schemas_closed_g258",
    "package_manifest_schemas_closed_g262",
    "terminal_session_schemas_closed_g264",
    "ai_agent_memory_schemas_closed_g266",
    "event_envelope_dead_letter_schemas_closed_g268",
    "knowledge_entity_provenance_schemas_closed_g270",
    "brain_twin_schemas_closed_g272",
    "ops_milestone_const_parity_and_contract_softener_g274",
    "contract_softener_wave2_g276",
    "contract_softener_wave3_tip_parity_guard_g278",
    "contract_softener_wave4_g280",
    "contract_softener_wave5_g282",
    "contract_softener_wave6_g284",
    "errorbody_outer_closed_g286",
    "outer_close_regression_guard_g288",
    "organization_entity_schemas_closed_g260",
    "external_psp_arbitration_brain_twin_webauthn_attestation_crypto_remain_closed",
    "webauthn_live_mint_env_gated_default_off_g160",
    "payment_clearing_internal_record_env_gated_default_off_g162",
    "role_grant_live_mint_env_gated_default_off",
)

# Measured: every catalog OpenAPI operation has a mounted /v1 FastAPI route
# (param-name camelCase vs snake_case normalized). Semantic shapes still partial.
_ROUTE_MOUNT_PARITY_COMPLETE = True


def _adapter_name_from_contract(relative: str) -> str:
    stem = relative.replace("\\", "/").rsplit("/", 1)[-1]
    return stem.replace(".openapi.yaml", "").replace(".openapi.yml", "")


def openapi_inventory_product_posture() -> dict[str, Any]:
    """Return desensitized Foundation OpenAPI inventory product posture."""

    contracts = [item.replace("\\", "/") for item in list_openapi_contracts()]
    adapters = list_adapters()
    adapter_paths = {item.openapi_path.replace("\\", "/") for item in adapters}
    contract_set = set(contracts)
    aligned = adapter_paths == contract_set and len(adapters) == len(contracts)

    catalog_domains = sorted({_adapter_name_from_contract(path) for path in contracts})
    thin_probe = [name for name in _THIN_PROBE_DOMAINS if name in catalog_domains]
    deferred = [name for name in catalog_domains if name not in set(thin_probe)]

    return {
        "surface": "foundation_openapi_inventory_product",
        "milestone": "PHX-G288",
        "openapi_contract_count": len(contracts),
        "adapter_count": len(adapters),
        "adapter_registry_status": "aligned" if aligned else "drift",
        "adapter_registry_aligned": aligned,
        "thin_probe_domains": thin_probe,
        "deferred_domains": deferred,
        "route_mount_parity_complete": _ROUTE_MOUNT_PARITY_COMPLETE,
        "known_defer_fences": list(_KNOWN_DEFER_FENCES),
        "full_openapi_http_complete": False,
        "semantic_remainder_honest": True,
        "t0188_status": "mount_parity_complete_outer_close_regression_guard_honest",
        "fail_closed_reasons": list(_FAIL_CLOSED_REASONS),
    }
