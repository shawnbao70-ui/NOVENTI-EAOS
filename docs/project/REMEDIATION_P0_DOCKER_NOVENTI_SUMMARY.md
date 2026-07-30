# PHX-G407 — Remediation P0-3 Docker noventi Summary

**Status:** TRACK-REMEDIATION-DOCKER-NOVENTI COMPLETE / TRACK-G407 COMPLETE  
**Milestone:** PHX-G407  
**Authorization:** `REMEDIATION_P0_DOCKER_NOVENTI_CODING_AUTHORIZATION_SUMMARY.md`

- `deploy/docker/Dockerfile` now `COPY noventi ./noventi` and ships `/smoke_imports.py`.
- Layout smoke（image-equivalent `PYTHONPATH`）imports `api.gateway.app`,
  `noventi.crm`, `noventi.finance`, `noventi.purchase`, `noventi.inventory`.
- `docs/release/COMPOSE.md` documents packaging boundary：≠ host OS install；
  ≠ Marketplace/Industry host-install runtime invent.
- Contract：`tests/contracts/test_ops_g407_docker_noventi_packaging.py`.
- **Host Docker CLI unavailable** in this environment；optional in-image smoke
  auto-skips. No Docker Desktop / host daemon install was performed（宪章：主机软件另批）.

**G1 BUILD PARTIAL** — recipe + layout import green；full container evidence when PO-authorized Docker is present.

Tip verified: `0092_finance_realized_fx_gl_bridge_g372`  
Package verified: `0.2.3`  
Next: PHX-G408（await separate Coding Auth）— P0-2 PR contract shard.
