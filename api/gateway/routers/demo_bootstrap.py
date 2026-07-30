"""Dev-only demo bootstrap surface (PHX-G167 / PHX-G168 / PHX-G172 / G182).

Mounted exclusively by ``api.gateway.demo`` — never by production ``app``.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Request

from api.gateway.sample_knowledge_pack import SAMPLE_PACK_PATH
from api.gateway.schemas.demo_bootstrap import DemoBootstrapData, DemoBootstrapEnvelope

router = APIRouter(prefix="/v1/demo", tags=["Demo Bootstrap"])


@router.get(
    "/bootstrap",
    response_model=DemoBootstrapEnvelope,
    response_model_exclude_none=True,
)
def demo_bootstrap(request: Request) -> DemoBootstrapEnvelope:
    """Return seeded demo Subject/Tenant and declared surface keys (no secrets)."""

    state = request.app.state
    subject = getattr(state, "demo_seeded_subject_id", None)
    tenant = getattr(state, "demo_seeded_tenant_id", None)
    if not isinstance(subject, UUID) or not isinstance(tenant, UUID):
        return DemoBootstrapEnvelope(
            data=DemoBootstrapData(available=False, reason="demo_seed_missing")
        )
    surfaces = list(getattr(state, "demo_declared_surface_keys", ()) or ())
    extension_id = getattr(state, "demo_seeded_extension_id", None)
    listing_id = getattr(state, "demo_seeded_listing_id", None)
    data = DemoBootstrapData(
        available=True,
        milestone="PHX-G182",
        subject_id=str(subject),
        tenant_id=str(tenant),
        subject_type="human",
        declared_surface_keys=surfaces,
        product_url="/terminal/#product",
        ops_url="/terminal/#ops",
        notes=[
            "dev-only bootstrap; not mounted on production gateway",
            "Open session -> Compose -> Preview -> Commit on Operator",
            "Signed demo extension is pre-activated for Extensions surface",
            "Published host listing supports Acquire -> Host on Extensions (PHX-G182)",
            "Sample knowledge pack (PHX-G293) is docs-only assembly — ≠ CRM CRUD",
        ],
        sample_knowledge_pack_path=SAMPLE_PACK_PATH,
        sample_knowledge_pack_url="/v1/demo/sample-pack/INDEX.md",
        sample_knowledge_pack_milestone="PHX-G293",
    )
    if isinstance(extension_id, UUID):
        data = data.model_copy(
            update={
                "extension_id": str(extension_id),
                "extension_key": "noventi.demo.panel",
                "extension_version": "1.0.0",
                "extensions_url": "/terminal/#extensions",
            }
        )
    if isinstance(listing_id, UUID):
        data = data.model_copy(
            update={
                "listing_id": str(listing_id),
                "listing_package_key": "noventi.demo.panel",
                "host_acquire_url": (
                    f"/v1/marketplace/listings/{listing_id}/host-acquire"
                ),
                "host_actions": ["panel.render"],
            }
        )
    return DemoBootstrapEnvelope(data=data)
