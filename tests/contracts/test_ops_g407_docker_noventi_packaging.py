"""PHX-G407 Docker noventi packaging + import smoke contracts."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = ROOT / "deploy" / "docker" / "Dockerfile"
SMOKE = ROOT / "deploy" / "docker" / "smoke_imports.py"
COMPOSE_DOC = ROOT / "docs" / "release" / "COMPOSE.md"
DOCKERIGNORE = ROOT / ".dockerignore"


def test_g407_dockerfile_copies_noventi_and_smoke() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert "COPY noventi ./noventi" in text
    assert "COPY deploy/docker/smoke_imports.py /smoke_imports.py" in text
    # PYTHONPATH must include /app so editable layout resolves noventi
    assert "PYTHONPATH=/app:/app/sdk" in text or "PYTHONPATH=/app" in text


def test_g407_dockerignore_does_not_exclude_noventi() -> None:
    text = DOCKERIGNORE.read_text(encoding="utf-8")
    lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert "noventi" not in lines
    assert "noventi/" not in lines
    assert not any(ln == "noventi" or ln.startswith("noventi/") for ln in lines)


def test_g407_layout_import_smoke_matches_image_pythonpath() -> None:
    """Host layout smoke with image-equivalent PYTHONPATH (packaging proof)."""

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(ROOT / "sdk")])
    completed = subprocess.run(
        [sys.executable, str(SMOKE)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "SMOKE_IMPORTS_OK" in completed.stdout
    assert "noventi.crm" in completed.stdout
    assert "noventi.finance" in completed.stdout


def test_g407_docs_state_packaging_not_host_install() -> None:
    text = COMPOSE_DOC.read_text(encoding="utf-8")
    assert "noventi" in text.casefold()
    assert "PHX-G407" in text or "G407" in text
    folded = text.casefold()
    assert "host" in folded or "packaging" in folded
    assert "industry" in folded or "marketplace" in folded or "≠" in text


def test_g407_optional_docker_image_smoke() -> None:
    """If Docker daemon is available, build and run /smoke_imports.py in the image."""

    try:
        probe = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return
    if probe.returncode != 0:
        return

    tag = "eaos-g407-noventi-smoke:local"
    build = subprocess.run(
        [
            "docker",
            "build",
            "-f",
            str(DOCKERFILE),
            "-t",
            tag,
            str(ROOT),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=1200,
    )
    assert build.returncode == 0, build.stderr[-4000:] if build.stderr else build.stdout[-4000:]
    run = subprocess.run(
        ["docker", "run", "--rm", "--entrypoint", "python", tag, "/smoke_imports.py"],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert run.returncode == 0, run.stderr or run.stdout
    assert "SMOKE_IMPORTS_OK" in run.stdout
