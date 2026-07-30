# PHX-G354 Summary — Workflow Approval for DO.ship

- Added Alembic revision `0078_inventory_do_ship_approval_g354`, extending the shared CRM tenant policy with `do_ship_approval_required`.
- When enabled, `inventory.delivery_order.ship` verifies an approved Workflow action bound to the delivery-order ID; approval never posts a shipment itself.
- Added CRM policy GET/PUT routes and contract coverage for policy-off, missing approval, and approved-but-not-auto-shipped behavior.
