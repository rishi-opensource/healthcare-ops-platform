from django.contrib import admin

from .models import (
    BarcodeAlias,
    DeliveryReceipt,
    InventoryBatch,
    PurchaseOrder,
    PurchaseOrderLine,
    StockItem,
    StockMovement,
)


class PurchaseOrderLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 1


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "branch", "quantity_on_hand", "reorder_threshold", "status")
    list_filter = ("status", "branch")
    search_fields = ("name", "sku", "barcode")


@admin.register(InventoryBatch)
class InventoryBatchAdmin(admin.ModelAdmin):
    list_display = ("stock_item", "batch_number", "expiry_date", "quantity", "location_label")
    list_filter = ("expiry_date",)
    search_fields = ("batch_number", "stock_item__name")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("stock_item", "movement_type", "quantity_delta", "performed_by", "created_at")
    list_filter = ("movement_type",)
    search_fields = ("stock_item__name", "note")


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    inlines = [PurchaseOrderLineInline]
    list_display = ("po_number", "supplier", "branch", "status", "ordered_at", "expected_at")
    list_filter = ("status", "branch")
    search_fields = ("po_number", "supplier__display_name", "notes")


@admin.register(DeliveryReceipt)
class DeliveryReceiptAdmin(admin.ModelAdmin):
    list_display = ("stock_item", "purchase_order", "quantity_received", "damage_quantity", "received_by")
    search_fields = ("stock_item__name", "purchase_order__po_number", "supplier_issue")


@admin.register(BarcodeAlias)
class BarcodeAliasAdmin(admin.ModelAdmin):
    list_display = ("barcode", "target_type", "label")
    list_filter = ("target_type",)
    search_fields = ("barcode", "label")
