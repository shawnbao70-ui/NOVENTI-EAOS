#!/usr/bin/env python3
"""Run a named contract shard and print wall-clock duration (PHX-G408)."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SHARDS = ROOT / "tests" / "contracts" / "shards.yaml"


def _load() -> dict:
    data = yaml.safe_load(SHARDS.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "shards" not in data:
        raise SystemExit(f"invalid shards file: {SHARDS}")
    return data


def _expand(shard: dict) -> list[str]:
    paths: list[str] = []
    for item in shard.get("paths") or []:
        paths.append(str(ROOT / item))
    collect = shard.get("collect")
    if collect:
        # shell-like split on whitespace; pytest accepts globs / dirs
        for token in str(collect).split():
            paths.append(str(ROOT / token) if not Path(token).is_absolute() else token)
    if not paths:
        raise SystemExit("shard has no paths/collect")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shard", help="shard name from tests/contracts/shards.yaml")
    parser.add_argument("--pytest-arg", action="append", default=[], help="extra pytest args")
    args = parser.parse_args()

    doc = _load()
    shards = doc["shards"]
    if args.shard not in shards:
        names = ", ".join(sorted(shards))
        raise SystemExit(f"unknown shard {args.shard!r}; choose one of: {names}")

    shard = shards[args.shard]
    targets = _expand(shard)
    budget = shard.get("budget_seconds") or doc.get("budget_seconds_pr_required")

    cmd = [sys.executable, "-m", "pytest", *targets, *args.pytest_arg]
    print(f"SHARD={args.shard}", flush=True)
    print(f"OWNERSHIP={shard.get('ownership')}", flush=True)
    print(f"SCHEDULE={shard.get('schedule')}", flush=True)
    if budget:
        print(f"BUDGET_SECONDS={budget}", flush=True)
    print("CMD=", " ".join(cmd), flush=True)
    started = time.perf_counter()
    completed = subprocess.run(cmd, cwd=str(ROOT), check=False)
    elapsed = time.perf_counter() - started
    print(f"DURATION_SECONDS={elapsed:.1f}", flush=True)
    print(f"EXIT_CODE={completed.returncode}", flush=True)
    if budget is not None and args.shard == "pr_required" and elapsed > float(budget):
        print(
            f"BUDGET_EXCEEDED: pr_required {elapsed:.1f}s > {budget}s",
            file=sys.stderr,
        )
        return 2 if completed.returncode == 0 else completed.returncode
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
