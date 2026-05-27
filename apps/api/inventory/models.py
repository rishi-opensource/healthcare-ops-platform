from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class StockItem(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        LOW_STOCK = "low_stock", "Low Stock"
        ARCHIVED = "archived", "Archived"

    entity = models.OneToOneField(
        "entities.Entity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_item",
    )
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="stock_items")
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=120)
    barcode = models.CharField(max_length=120, blank=True)
    unit = models.CharField(max_length=40, default="each")
    quantity_on_hand = models.IntegerField(default=0)
    reorder_threshold = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    preferred_supplier = models.ForeignKey(
        "entities.Entity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplied_stock_items",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "sku"], name="unique_stock_item_sku_per_branch"),
        ]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["barcode"]),
        ]

    def __str__(self) -> str:
        return self.name


class InventoryBatch(TimeStampedModel):
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="batches")
    batch_number = models.CharField(max_length=120)
    expiry_date = models.DateField(null=True, blank=True)
    quantity = models.IntegerField(default=0)
    location_label = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["expiry_date", "batch_number"]
        constraints = [
            models.UniqueConstraint(fields=["stock_item", "batch_number"], name="unique_batch_per_stock_item"),
        ]
        indexes = [
            models.Index(fields=["expiry_date"]),
        ]


class StockMovement(TimeStampedModel):
    class MovementType(models.TextChoices):
        RECEIPT = "receipt", "Receipt"
        ISSUE = "issue", "Issue"
        ADJUSTMENT = "adjustment", "Adjustment"
        DAMAGE = "damage", "Damage"
        TRANSFER = "transfer", "Transfer"

    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="movements")
    batch = models.ForeignKey(
        InventoryBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements",
    )
    movement_type = models.CharField(max_length=32, choices=MovementType.choices)
    quantity_delta = models.IntegerField()
    note = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    related_ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["stock_item", "movement_type"]),
        ]


class PurchaseOrder(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ORDERED = "ordered", "Ordered"
        PART_RECEIVED = "part_received", "Part Received"
        RECEIVED = "received", "Received"
        CANCELLED = "cancelled", "Cancelled"

    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="purchase_orders")
    supplier = models.ForeignKey(
        "entities.Entity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_orders",
    )
    po_number = models.CharField(max_length=32, unique=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_purchase_orders",
    )
    ordered_at = models.DateTimeField(null=True, blank=True)
    expected_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["branch", "status"]),
        ]


class PurchaseOrderLine(TimeStampedModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="purchase_order_lines")
    quantity_ordered = models.PositiveIntegerField(default=1)
    quantity_received = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["purchase_order", "stock_item"], name="unique_po_line_stock_item"),
        ]


class DeliveryReceipt(TimeStampedModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
    )
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="deliveries")
    batch = models.ForeignKey(
        InventoryBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
    )
    quantity_received = models.PositiveIntegerField(default=0)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_receipts",
    )
    supplier_issue = models.TextField(blank=True)
    damage_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at", "-id"]


class BarcodeAlias(TimeStampedModel):
    class TargetType(models.TextChoices):
        STOCK_ITEM = "stock_item", "Stock Item"
        BATCH = "batch", "Batch"
        PURCHASE_ORDER = "purchase_order", "Purchase Order"
        DELIVERY = "delivery", "Delivery"

    barcode = models.CharField(max_length=255, unique=True)
    target_type = models.CharField(max_length=32, choices=TargetType.choices)
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, null=True, blank=True, related_name="barcodes")
    batch = models.ForeignKey(InventoryBatch, on_delete=models.CASCADE, null=True, blank=True, related_name="barcodes")
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="barcodes",
    )
    delivery = models.ForeignKey(
        DeliveryReceipt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="barcodes",
    )
    label = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["barcode"]
