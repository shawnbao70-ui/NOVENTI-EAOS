"""PHX-K07 Organization schema and ownership contracts."""

from __future__ import annotations

from kernel.infrastructure.persistence import metadata
from kernel.organization.models import Enterprise, Membership, OrganizationUnit, Tenant


def test_organization_domain_models_are_orm_independent() -> None:
    for model in (Tenant, Enterprise, OrganizationUnit, Membership):
        assert not hasattr(model, "__table__")


def test_enterprise_is_separate_from_tenant_boundary() -> None:
    enterprise = metadata.tables["kernel.enterprises"]
    assert not enterprise.c.tenant_id.nullable
    assert not enterprise.c.legal_name.nullable
    assert not enterprise.c.is_primary.nullable
    assert {index.name for index in enterprise.indexes} >= {
        "uq_enterprises_tenant_legal_name_ci",
        "uq_enterprises_primary_per_tenant",
    }


def test_units_and_memberships_require_enterprise_scope() -> None:
    for table_name in ("org_units", "memberships"):
        table = metadata.tables[f"kernel.{table_name}"]
        assert not table.c.tenant_id.nullable
        assert not table.c.enterprise_id.nullable
        enterprise_foreign_keys = {
            tuple(element.parent.name for element in constraint.elements)
            for constraint in table.foreign_key_constraints
            if any("enterprises" in element.target_fullname for element in constraint.elements)
        }
        assert ("enterprise_id", "tenant_id") in enterprise_foreign_keys

    unit = metadata.tables["kernel.org_units"]
    membership = metadata.tables["kernel.memberships"]
    assert (
        "parent_unit_id",
        "tenant_id",
        "enterprise_id",
    ) in {
        tuple(element.parent.name for element in constraint.elements)
        for constraint in unit.foreign_key_constraints
    }
    assert (
        "org_unit_id",
        "tenant_id",
        "enterprise_id",
    ) in {
        tuple(element.parent.name for element in constraint.elements)
        for constraint in membership.foreign_key_constraints
    }
    active_indexes = {
        index.name: tuple(column.name for column in index.columns)
        for index in membership.indexes
        if index.name and index.name.startswith("uq_memberships_active")
    }
    assert active_indexes["uq_memberships_active_unit"] == (
        "tenant_id",
        "enterprise_id",
        "subject_id",
        "org_unit_id",
    )
    assert active_indexes["uq_memberships_active_no_unit"] == (
        "tenant_id",
        "enterprise_id",
        "subject_id",
    )
