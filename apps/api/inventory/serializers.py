from rest_framework import serializers

from .models import (
    BarcodeAlias,
    DeliveryReceipt,
    InventoryBatch,
    PurchaseOrder,
    PurchaseOrderLine,
    StockItem,
    StockMovement,
)


class InventoryBatchSerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(source="stock_item.name", read_only=True)

    class Meta:
        model = InventoryBatch
        fields = [
            "id",
            "stock_item",
            "stock_item_name",
            "batch_number",
            "expiry_date",
            "quantity",
            "location_label",
            "created_at",
            "updated_at",
        ]


class StockItemSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    entity_name = serializers.CharField(source="entity.display_name", read_only=True)
    preferred_supplier_name = serializers.CharField(source="preferred_supplier.display_name", read_only=True)

    class Meta:
        model = StockItem
        fields = [
            "id",
            "entity",
            "entity_name",
            "branch",
            "branch_name",
            "name",
            "sku",
            "barcode",
            "unit",
            "quantity_on_hand",
            "reorder_threshold",
            "status",
            "preferred_supplier",
            "preferred_supplier_name",
            "created_at",
            "updated_at",
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(source="stock_item.name", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)
    performed_by_email = serializers.CharField(source="performed_by.email", read_only=True)
    related_ticket_number = serializers.CharField(source="related_ticket.ticket_number", read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "stock_item",
            "stock_item_name",
            "batch",
            "batch_number",
            "movement_type",
            "quantity_delta",
            "note",
            "performed_by",
            "performed_by_email",
            "related_ticket",
            "related_ticket_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["performed_by", "related_ticket"]


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(source="stock_item.name", read_only=True)

    class Meta:
        model = PurchaseOrderLine
        fields = ["id", "stock_item", "stock_item_name", "quantity_ordered", "quantity_received"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.display_name", read_only=True)
    requested_by_email = serializers.CharField(source="requested_by.email", read_only=True)
    lines = PurchaseOrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "branch",
            "branch_name",
            "supplier",
            "supplier_name",
            "po_number",
            "status",
            "requested_by",
            "requested_by_email",
            "ordered_at",
            "expected_at",
            "notes",
            "lines",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["po_number", "requested_by", "ordered_at"]


class DeliveryReceiptSerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(source="stock_item.name", read_only=True)
    purchase_order_number = serializers.CharField(source="purchase_order.po_number", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)
    received_by_email = serializers.CharField(source="received_by.email", read_only=True)

    class Meta:
        model = DeliveryReceipt
        fields = [
            "id",
            "purchase_order",
            "purchase_order_number",
            "stock_item",
            "stock_item_name",
            "batch",
            "batch_number",
            "quantity_received",
            "received_by",
            "received_by_email",
            "supplier_issue",
            "damage_quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["received_by", "batch"]


class BarcodeAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeAlias
        fields = [
            "id",
            "barcode",
            "target_type",
            "stock_item",
            "batch",
            "purchase_order",
            "delivery",
            "label",
            "created_at",
            "updated_at",
        ]


class StockMovementActionSerializer(serializers.Serializer):
    movement_type = serializers.ChoiceField(choices=StockMovement.MovementType.choices)
    quantity_delta = serializers.IntegerField()
    batch = serializers.IntegerField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True)


class DeliveryReceiveSerializer(serializers.Serializer):
    stock_item = serializers.IntegerField()
    purchase_order = serializers.IntegerField(required=False, allow_null=True)
    quantity_received = serializers.IntegerField(min_value=1)
    batch_number = serializers.CharField(required=False, allow_blank=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    supplier_issue = serializers.CharField(required=False, allow_blank=True)
    damage_quantity = serializers.IntegerField(default=0, min_value=0)


class BarcodeResolveSerializer(serializers.Serializer):
    barcode = serializers.CharField()


class InventorySummarySerializer(serializers.Serializer):
    stock_items = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    expiring_batches = serializers.IntegerField()
    open_purchase_orders = serializers.IntegerField()
    damaged_deliveries = serializers.IntegerField()
    reorder_tickets = serializers.IntegerField()
