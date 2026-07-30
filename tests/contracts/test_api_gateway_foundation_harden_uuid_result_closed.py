"""Foundation harden — shared UuidResult / OkResponse closed response DTOs."""

from __future__ import annotations

from uuid import uuid4

from api.gateway.schemas.common import BooleanResult, OkResponse, UuidResult
from api.gateway.serializers.common import uuid_result
from api.gateway.serializers.permission import ok_response
from api.gateway.serializers.terminal import boolean_result


def test_uuid_result_helper_matches_closed_dto() -> None:
    resource_id = uuid4()
    audit_id = uuid4()
    payload = uuid_result(resource_id, audit_id=audit_id)
    closed = UuidResult.model_validate(payload)
    assert closed.id == resource_id
    assert closed.data == resource_id
    assert str(closed.audit_id) == str(audit_id)


def test_boolean_result_helper_matches_closed_dto() -> None:
    payload = boolean_result(True, audit_id=uuid4())
    closed = BooleanResult.model_validate(payload)
    assert closed.data is True
    assert closed.audit_id is not None


def test_ok_response_helper_matches_closed_dto() -> None:
    audit_id = uuid4()
    payload = ok_response(audit_id=audit_id)
    closed = OkResponse.model_validate(payload)
    assert closed.ok is True
    assert str(closed.audit_id) == str(audit_id)


def test_ok_response_rejects_extra_fields() -> None:
    try:
        OkResponse.model_validate({"ok": True, "extra": 1})
        raise AssertionError("expected ValidationError")
    except Exception as exc:  # noqa: BLE001 — pydantic ValidationError
        assert "extra" in str(exc).lower() or "forbid" in str(exc).lower()
