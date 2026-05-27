# Phase 8 - Inventory, Procurement, and Barcode

Phase 8 adds stock control, purchase order tracking, delivery receipt handling, and barcode resolution for mobile and web workflows.

## Delivered

- Inventory API app with stock items, batches, stock movements, purchase orders, purchase order lines, delivery receipts, and barcode aliases.
- Stock issue/adjustment, reorder ticket creation, purchase order ordering, delivery receipt, damaged goods, and barcode resolution actions.
- Audit events for stock movement, purchase order, delivery, and reorder ticket actions.
- Shared TypeScript client coverage for inventory, procurement, delivery, barcode, and summary endpoints.
- Web `/inventory` workspace for stock levels, expiring batches, low-stock alerts, issue actions, and reorder tickets.
- Web `/procurement` workspace for purchase orders, delivery receipts, damaged goods, and receiving workflows.
- Mobile Scan tab now resolves barcodes against the backend inventory registry.
- Demo seed data now includes stock, batch, barcode, purchase order, delivery, and supplier records.
- Focused tests cover the Phase 8 inventory workflow.

## Verification

```bash
.venv/bin/ruff check apps/api
.venv/bin/python apps/api/manage.py makemigrations --check --dry-run
.venv/bin/python apps/api/manage.py migrate
.venv/bin/python apps/api/manage.py seed_demo
.venv/bin/python apps/api/manage.py test tests
.venv/bin/python apps/api/manage.py spectacular --file packages/api-client/src/generated/schema.yaml
npm run lint
npm run typecheck
npm --workspace @healthcare/web run build
```

OpenAPI generation completed with non-blocking action path parameter warnings and no errors.
