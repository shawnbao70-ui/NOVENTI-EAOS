# Coding Authorization Summary — Controlled Reship (G370)

## Milestone

**PHX-G370** — ADR-0314 controlled reship with new ship identity.

## Alembic

**`0090_inventory_controlled_reship_g370`** revising
`0089_inventory_ship_pod_g367`.

## Authorized

1. After DO is `unshipped`, allow a new ship with a **new** `idempotency_key`
   creating a **new** ship posting row (new ship identity).
2. Reusing the prior posting's idempotency_key must not silently re-ship
   (conflict or idempotent return of unshipped — prefer conflict for reship intent).
3. Relax unique `(tenant, delivery_order_id)` if needed so history of postings
   is retained; at most one `shipped` posting per DO at a time.
4. human_confirm + Permission; contracts: unship→reship with new key OK;
   stock decrements again; old key rejected.

## Out

Treasury (G371), FX-GL (G372), DE invent beyond thin (G374).

## Product Owner response

**Approve — Residual closeout batch.** Auto-continue G371.
