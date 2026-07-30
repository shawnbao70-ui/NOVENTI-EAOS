"""PHX-G76 deploy region identity API contracts."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

fastapi = pytest.importorskip("fastapi")

from api.gateway import create_app
from api.gateway.deploy_region import configure_deploy_region, deploy_region


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_DEPLOY_REGION", raising=False)
    configure_deploy_region()
    yield
    configure_deploy_region()
    monkeypatch.delenv("EAOS_DEPLOY_REGION", raising=False)


def test_release_deploy_region_null_by_default() -> None:
    assert deploy_region() is None
    client = TestClient(create_app())
    body = client.get("/v1/release").json()["data"]
    assert body["deploy_region"] is None
    assert body["version"] == "0.2.1"


def test_release_exposes_deploy_region(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_DEPLOY_REGION", "ap-east-1")
    configure_deploy_region()
    client = TestClient(create_app())
    body = client.get("/v1/release").json()["data"]
    assert body["deploy_region"] == "ap-east-1"


def test_invalid_deploy_region_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_DEPLOY_REGION", "NOT VALID")
    configure_deploy_region()
    with pytest.raises(RuntimeError, match="EAOS_DEPLOY_REGION"):
        deploy_region()
