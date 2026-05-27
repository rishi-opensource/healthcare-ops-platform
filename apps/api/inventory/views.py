from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import has_role
from audit.services import record_audit_event
from tickets.models import Ticket

from .models import BarcodeAlias, DeliveryReceipt, InventoryBatch, PurchaseOrder, StockItem
from .serializers import (
    BarcodeAliasSerializer,
    BarcodeResolveSerializer,
    DeliveryReceiptSerializer,
    DeliveryReceiveSerializer,
    InventoryBatchSerializer,
    InventorySummarySerializer,
    PurchaseOrderSerializer,
    StockItemSerializer,
    StockMovementActionSerializer,
    StockMovementSerializer,
)
from .services import (
    create_reorder_ticket,
    order_purchase_order,
    receive_delivery,
    record_stock_movement,
    resolve_barcode,
)


def can_manage_inventory(user) -> bool:
    return has_role(user, "super_admin", "manager", "inventory", "finance")


def branch_scope(queryset, user):
    if user.primary_branch_id and not has_role(user, "super_admin"):
        return queryset.filter(Q(branch=user.primary_branch) | Q(branch__isnull=True))
    return queryset


class StockItemViewSet(ModelViewSet):
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "branch", "preferred_supplier"]
    search_fields = ["name", "sku", "barcode"]
    ordering_fields = ["name", "quantity_on_hand", "status"]

    def get_queryset(self):
        return branch_scope(
            StockItem.objects.select_related("entity", "branch", "preferred_supplier"),
            self.request.user,
        )

    def perform_create(self, serializer):
        item = serializer.save()
        record_audit_event(
            actor_user=self.request.user,
            action="inventory.stock_item.create",
            target=item,
            request=self.request,
        )

    @extend_schema(request=StockMovementActionSerializer, responses=StockMovementSerializer)
    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        serializer = StockMovementActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        batch = None
        if serializer.validated_data.get("batch"):
            batch = InventoryBatch.objects.get(id=serializer.validated_data["batch"])
        movement = record_stock_movement(
            stock_item=self.get_object(),
            batch=batch,
            actor_user=request.user,
            request=request,
            **{key: value for key, value in serializer.validated_data.items() if key != "batch"},
        )
        return Response(StockMovementSerializer(movement, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="create-reorder-ticket")
    def reorder_ticket(self, request, pk=None):
        ticket = create_reorder_ticket(stock_item=self.get_object(), actor_user=request.user, request=request)
        return Response({"ticket_id": ticket.id, "ticket_number": ticket.ticket_number})


class InventoryBatchViewSet(ModelViewSet):
    serializer_class = InventoryBatchSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["stock_item", "expiry_date"]
    search_fields = ["batch_number", "stock_item__name"]

    def get_queryset(self):
        return InventoryBatch.objects.select_related("stock_item", "stock_item__branch")


class PurchaseOrderViewSet(ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "branch", "supplier"]
    search_fields = ["po_number", "supplier__display_name", "notes"]

    def get_queryset(self):
        return branch_scope(
            PurchaseOrder.objects.select_related("branch", "supplier", "requested_by").prefetch_related("lines"),
            self.request.user,
        )

    def perform_create(self, serializer):
        po = serializer.save(requested_by=self.request.user)
        if not po.po_number:
            po.po_number = f"PO-{po.id:06d}"
            po.save(update_fields=["po_number"])
        record_audit_event(
            actor_user=self.request.user,
            action="inventory.purchase_order.create",
            target=po,
            request=self.request,
        )

    @extend_schema(responses=PurchaseOrderSerializer)
    @action(detail=True, methods=["post"])
    def order(self, request, pk=None):
        po = order_purchase_order(purchase_order=self.get_object(), actor_user=request.user, request=request)
        return Response(PurchaseOrderSerializer(po, context={"request": request}).data)


class DeliveryReceiptViewSet(ModelViewSet):
    serializer_class = DeliveryReceiptSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["purchase_order", "stock_item", "received_by"]

    def get_queryset(self):
        return DeliveryReceipt.objects.select_related("purchase_order", "stock_item", "batch", "received_by")

    @extend_schema(request=DeliveryReceiveSerializer, responses=DeliveryReceiptSerializer)
    @action(detail=False, methods=["post"])
    def receive(self, request):
        serializer = DeliveryReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stock_item = StockItem.objects.get(id=serializer.validated_data["stock_item"])
        purchase_order = None
        if serializer.validated_data.get("purchase_order"):
            purchase_order = PurchaseOrder.objects.get(id=serializer.validated_data["purchase_order"])
        delivery = receive_delivery(
            stock_item=stock_item,
            purchase_order=purchase_order,
            actor_user=request.user,
            request=request,
            **{
                key: value
                for key, value in serializer.validated_data.items()
                if key not in {"stock_item", "purchase_order"}
            },
        )
        return Response(DeliveryReceiptSerializer(delivery, context={"request": request}).data)


class BarcodeAliasViewSet(ModelViewSet):
    serializer_class = BarcodeAliasSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["target_type", "stock_item", "batch", "purchase_order"]
    search_fields = ["barcode", "label"]

    def get_queryset(self):
        return BarcodeAlias.objects.select_related("stock_item", "batch", "purchase_order", "delivery")

    @extend_schema(request=BarcodeResolveSerializer)
    @action(detail=False, methods=["post"])
    def resolve(self, request):
        serializer = BarcodeResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(resolve_barcode(serializer.validated_data["barcode"]))


class InventorySummaryViewSet(ModelViewSet):
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        return branch_scope(StockItem.objects.select_related("branch"), self.request.user)

    @extend_schema(responses=InventorySummarySerializer)
    @action(detail=False, methods=["get"])
    def summary(self, request):
        soon = timezone.now().date() + timedelta(days=30)
        items = self.get_queryset()
        batches = InventoryBatch.objects.filter(stock_item__in=items)
        purchase_orders = branch_scope(PurchaseOrder.objects.all(), request.user)
        return Response(
            {
                "stock_items": items.count(),
                "low_stock_items": items.filter(status=StockItem.Status.LOW_STOCK).count(),
                "expiring_batches": batches.filter(expiry_date__lte=soon, quantity__gt=0).count(),
                "open_purchase_orders": purchase_orders.exclude(
                    status__in=[PurchaseOrder.Status.RECEIVED, PurchaseOrder.Status.CANCELLED]
                ).count(),
                "damaged_deliveries": DeliveryReceipt.objects.filter(
                    stock_item__in=items,
                    damage_quantity__gt=0,
                ).count(),
                "reorder_tickets": Ticket.objects.filter(
                    category=Ticket.Category.INVENTORY,
                    status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS, Ticket.Status.WAITING_APPROVAL],
                ).count(),
            }
        )
