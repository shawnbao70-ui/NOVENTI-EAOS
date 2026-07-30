# ADR-0422 — Remediation Contract Shards Boundary

**状态：** Accepted（PHX-G408）  
**日期：** 2026-07-27  
**里程碑：** PHX-G408  
**授权源：** [Coding Authorization](../project/REMEDIATION_P0_CONTRACT_SHARDS_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 契约测试按域分片；`pr_required` 为每个 PR 必跑集合，墙钟预算 ≤ 600 秒。  
2. 全量 `tests/contracts` 走 nightly / parallel，并**公布** `DURATION_SECONDS`，不得用 PR 绿隐藏全量耗时。  
3. 分片清单以 `tests/contracts/shards.yaml` 为真源；说明见 `docs/release/CONTRACT_SHARDS.md`。  
4. 禁止为凑预算发明 flaky skip；扩 `pr_required` 必须重测预算。  
5. 本切片不安装宿主机 CI；GitHub Actions 另属 G410。
