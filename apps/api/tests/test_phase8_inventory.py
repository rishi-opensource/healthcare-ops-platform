from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Role, RoleAssignment
from audit.models import AuditEvent
from core.models import Branch, Organization
from entities.models import Entity
from inventory.models import BarcodeAlias, InventoryBatch, PurchaseOrder, PurchaseOrderLine, StockItem


class Phase8InventoryTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Healthcare Doctors")
        self.branch = Branch.objects.create(organization=self.organization, name="Main Clinic", code="main")
        inventory_role = Role.objects.create(code=Role.Codes.INVENTORY, name="Inventory")
        User = get_user_model()
        self.inventory_user = User.objects.create_user(
            email="inventory@example.com",
            password="ChangeMe123!",
            full_name="Inventory User",
            primary_branch=self.branch,
        )
        RoleAssignment.objects.create(user=self.inventory_user, role=inventory_role, branch=self.branch)
        self.supplier = Entity.objects.create(
            entity_type=Entity.Types.SUPPLIER,
            display_name="ABC Medical Supplies",
            status=Entity.Status.ACTIVE,
            branch=self.branch,
        )
        self.item_entity = Entity.objects.create(
            entity_type=Entity.Types.INVENTORY_ITEM,
            display_name="Nitrile Gloves Medium",
            status=Entity.Status.ACTIVE,
            branch=self.branch,
        )
        self.stock_item = StockItem.objects.create(
            entity=self.item_entity,
            branch=self.branch,
            name="Nitrile Gloves Medium",
            sku="GLOVE-M",
            barcode="093000000001",
            unit="box",
            quantity_on_hand=10,
            reorder_threshold=12,
            status=StockItem.Status.LOW_STOCK,
            preferred_supplier=self.supplier,
        )
        self.batch = InventoryBatch.objects.create(
            stock_item=self.stock_item,
            batch_number="GLV-2026-01",
            expiry_date=timezone.now().date() + timedelta(days=20),
            quantity=10,
        )
        BarcodeAlias.objects.create(
            barcode="093000000001",
            target_type=BarcodeAlias.TargetType.STOCK_ITEM,
            stock_item=self.stock_item,
            label="Nitrile Gloves Medium",
        )
        self.client = APIClient()

    def test_stock_issue_reorder_and_barcode_resolution(self):
        self.client.force_authenticate(user=self.inventory_user)

        issue = self.client.post(
            f"/api/v1/stock-items/{self.stock_item.id}/move/",
            {"movement_type": "issue", "quantity_delta": -2, "batch": self.batch.id, "note": "Used in room 1."},
            format="json",
        )
        reorder = self.client.post(
            f"/api/v1/stock-items/{self.stock_item.id}/create-reorder-ticket/",
            {},
            format="json",
        )
        resolved = self.client.post("/api/v1/barcode-aliases/resolve/", {"barcode": "093000000001"}, format="json")

        self.assertEqual(issue.status_code, 200)
        self.assertEqual(issue.data["quantity_delta"], -2)
        self.assertEqual(reorder.status_code, 200)
        self.assertTrue(reorder.data["ticket_number"].startswith("HD-"))
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(resolved.data["target_type"], BarcodeAlias.TargetType.STOCK_ITEM)
        self.assertTrue(AuditEvent.objects.filter(action="inventory.stock.move").exists())
        self.assertTrue(AuditEvent.objects.filter(action="inventory.reorder_ticket.create").exists())

    def test_purchase_order_receive_delivery_updates_stock_and_summary(self):
        self.client.force_authenticate(user=self.inventory_user)
        po = PurchaseOrder.objects.create(branch=self.branch, supplier=self.supplier, requested_by=self.inventory_user)
        PurchaseOrderLine.objects.create(purchase_order=po, stock_item=self.stock_item, quantity_ordered=5)

        ordered = self.client.post(f"/api/v1/purchase-orders/{po.id}/order/", {}, format="json")
        delivery = self.client.post(
            "/api/v1/delivery-receipts/receive/",
            {
                "purchase_order": po.id,
                "stock_item": self.stock_item.id,
                "quantity_received": 5,
                "batch_number": "GLV-2026-02",
                "expiry_date": str(timezone.now().date() + timedelta(days=365)),
                "damage_quantity": 1,
                "supplier_issue": "One box crushed.",
            },
            format="json",
        )
        summary = self.client.get("/api/v1/inventory-summary/summary/")

        self.assertEqual(ordered.status_code, 200)
        self.assertEqual(ordered.data["status"], PurchaseOrder.Status.ORDERED)
        self.assertEqual(delivery.status_code, 200)
        self.assertEqual(delivery.data["quantity_received"], 5)
        self.stock_item.refresh_from_db()
        self.assertEqual(self.stock_item.quantity_on_hand, 14)
        self.assertEqual(summary.status_code, 200)
        self.assertEqual(summary.data["damaged_deliveries"], 1)
        self.assertTrue(AuditEvent.objects.filter(action="inventory.delivery.receive").exists())
