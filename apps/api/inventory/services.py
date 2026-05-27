from __future__ import annotations

from django.db import models, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from audit.services import record_audit_event
from tickets.models import Ticket
from tickets.services import create_ticket

from .models import (
    BarcodeAlias,
    DeliveryReceipt,
    InventoryBatch,
    PurchaseOrder,
    PurchaseOrderLine,
    StockItem,
    StockMovement,
)


def next_po_number(po_id: int) -> str:
    return f"PO-{po_id:06d}"


def refresh_stock_status(stock_item: StockItem) -> StockItem:
    stock_item.status = (
        StockItem.Status.LOW_STOCK
        if stock_item.quantity_on_hand <= int(stock_item.reorder_threshold)
        else StockItem.Status.ACTIVE
    )
    stock_item.save(update_fields=["status", "updated_at"])
    return stock_item


@transaction.atomic
def record_stock_movement(
    *,
    stock_item: StockItem,
    movement_type: str,
    quantity_delta: int,
    actor_user,
    batch: InventoryBatch | None = None,
    note: str = "",
    related_ticket=None,
    request=None,
) -> StockMovement:
    if stock_item.quantity_on_hand + quantity_delta < 0:
        raise ValidationError({"quantity_delta": "Stock quantity cannot go below zero."})
    stock_item.quantity_on_hand += quantity_delta
    stock_item.save(update_fields=["quantity_on_hand", "updated_at"])
    if batch:
        if batch.quantity + quantity_delta < 0:
            raise ValidationError({"quantity_delta": "Batch quantity cannot go below zero."})
        batch.quantity += quantity_delta
        batch.save(update_fields=["quantity", "updated_at"])
    movement = StockMovement.objects.create(
        stock_item=stock_item,
        batch=batch,
        movement_type=movement_type,
        quantity_delta=quantity_delta,
        note=note,
        performed_by=actor_user,
        related_ticket=related_ticket,
    )
    refresh_stock_status(stock_item)
    record_audit_event(
        actor_user=actor_user,
        action="inventory.stock.move",
        target=stock_item,
        request=request,
        metadata={"movement_id": movement.id, "movement_type": movement_type, "quantity_delta": quantity_delta},
    )
    return movement


@transaction.atomic
def order_purchase_order(*, purchase_order: PurchaseOrder, actor_user, request=None) -> PurchaseOrder:
    if not purchase_order.po_number:
        purchase_order.po_number = next_po_number(purchase_order.id)
    purchase_order.status = PurchaseOrder.Status.ORDERED
    purchase_order.ordered_at = timezone.now()
    purchase_order.save(update_fields=["po_number", "status", "ordered_at", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="inventory.purchase_order.order",
        target=purchase_order,
        request=request,
        metadata={"po_number": purchase_order.po_number},
    )
    return purchase_order


@transaction.atomic
def receive_delivery(
    *,
    stock_item: StockItem,
    actor_user,
    quantity_received: int,
    purchase_order: PurchaseOrder | None = None,
    batch_number: str = "",
    expiry_date=None,
    supplier_issue: str = "",
    damage_quantity: int = 0,
    request=None,
) -> DeliveryReceipt:
    if damage_quantity > quantity_received:
        raise ValidationError({"damage_quantity": "Damaged quantity cannot exceed received quantity."})
    batch = None
    if batch_number:
        batch, _ = InventoryBatch.objects.get_or_create(
            stock_item=stock_item,
            batch_number=batch_number,
            defaults={"expiry_date": expiry_date},
        )
    usable_quantity = quantity_received - damage_quantity
    delivery = DeliveryReceipt.objects.create(
        purchase_order=purchase_order,
        stock_item=stock_item,
        batch=batch,
        quantity_received=quantity_received,
        received_by=actor_user,
        supplier_issue=supplier_issue,
        damage_quantity=damage_quantity,
    )
    if usable_quantity:
        record_stock_movement(
            stock_item=stock_item,
            batch=batch,
            movement_type=StockMovement.MovementType.RECEIPT,
            quantity_delta=usable_quantity,
            actor_user=actor_user,
            note=f"Delivery {delivery.id} received.",
            request=request,
        )
    if damage_quantity:
        record_stock_movement(
            stock_item=stock_item,
            batch=batch,
            movement_type=StockMovement.MovementType.DAMAGE,
            quantity_delta=0,
            actor_user=actor_user,
            note=f"{damage_quantity} damaged on delivery. {supplier_issue}".strip(),
            request=request,
        )
    if purchase_order:
        line = PurchaseOrderLine.objects.filter(purchase_order=purchase_order, stock_item=stock_item).first()
        if line:
            line.quantity_received += quantity_received
            line.save(update_fields=["quantity_received", "updated_at"])
        remaining = purchase_order.lines.filter(quantity_received__lt=models.F("quantity_ordered")).exists()
        purchase_order.status = PurchaseOrder.Status.PART_RECEIVED if remaining else PurchaseOrder.Status.RECEIVED
        purchase_order.save(update_fields=["status", "updated_at"])
    record_audit_event(
        actor_user=actor_user,
        action="inventory.delivery.receive",
        target=delivery,
        request=request,
        metadata={"stock_item_id": stock_item.id, "quantity_received": quantity_received},
    )
    return delivery


@transaction.atomic
def create_reorder_ticket(*, stock_item: StockItem, actor_user, request=None) -> Ticket:
    ticket = create_ticket(
        actor_user=actor_user,
        title=f"Reorder {stock_item.name}",
        description=(
            f"{stock_item.name} is at {stock_item.quantity_on_hand} {stock_item.unit}; "
            f"threshold is {stock_item.reorder_threshold}."
        ),
        category=Ticket.Category.INVENTORY,
        priority=Ticket.Priority.HIGH,
        branch=stock_item.branch,
        related_entity=stock_item.entity,
        source=Ticket.Source.SYSTEM,
        request=request,
    )
    record_audit_event(
        actor_user=actor_user,
        action="inventory.reorder_ticket.create",
        target=stock_item,
        request=request,
        metadata={"ticket_id": ticket.id},
    )
    return ticket


def resolve_barcode(barcode: str) -> dict[str, object]:
    alias = BarcodeAlias.objects.select_related("stock_item", "batch", "purchase_order", "delivery").filter(
        barcode=barcode
    ).first()
    if alias:
        target = alias.stock_item or alias.batch or alias.purchase_order or alias.delivery
        return {
            "barcode": barcode,
            "target_type": alias.target_type,
            "target_id": target.id if target else None,
            "label": alias.label or str(target),
        }
    stock_item = StockItem.objects.filter(barcode=barcode).first()
    if stock_item:
        return {
            "barcode": barcode,
            "target_type": BarcodeAlias.TargetType.STOCK_ITEM,
            "target_id": stock_item.id,
            "label": stock_item.name,
        }
    raise ValidationError({"barcode": "No inventory record found for this barcode."})
