"use client";

import type { DeliveryReceipt, InventorySummary, PurchaseOrder, StockItem } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

function label(value: string) {
  return value.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join(" ");
}

export default function ProcurementPage() {
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [deliveries, setDeliveries] = useState<DeliveryReceipt[]>([]);
  const [items, setItems] = useState<StockItem[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    const api = webApiClient();
    const [nextSummary, orderPage, deliveryPage, itemPage] = await Promise.all([
      api.inventorySummary(),
      api.listPurchaseOrders(),
      api.listDeliveryReceipts(),
      api.listStockItems()
    ]);
    setSummary(nextSummary);
    setOrders(orderPage.results);
    setDeliveries(deliveryPage.results);
    setItems(itemPage.results);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error instanceof Error ? error.message : "Unable to load procurement."));
  }, []);

  async function order(id: number) {
    await webApiClient().orderPurchaseOrder(id);
    await load();
  }

  async function receiveFirstItem() {
    const item = items[0];
    if (!item) return;
    await webApiClient().receiveDelivery({
      stock_item: item.id,
      purchase_order: orders[0]?.id ?? null,
      quantity_received: 5,
      batch_number: `BATCH-${Date.now()}`,
      damage_quantity: 0
    });
    await load();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Procurement</div>
          <h1 className="title">Procurement workflows</h1>
          <p className="muted">Purchase orders, deliveries, supplier issues, damaged goods, and reorder follow-up.</p>
        </div>
        <div className="card">Open POs: {summary?.open_purchase_orders ?? 0}</div>
      </div>
      {message ? <div className="alert">{message}</div> : null}
      <section className="dashboard-grid">
        <div className="card">
          <div className="detail-heading">
            <div className="section-title">Purchase orders</div>
            <button className="button" type="button" onClick={() => void receiveFirstItem()}>Receive demo delivery</button>
          </div>
          <div className="stack">
            {orders.map((po) => (
              <div className="subcard" key={po.id}>
                <div className="detail-heading">
                  <div>
                    <strong>{po.po_number || `PO ${po.id}`}</strong>
                    <div className="muted">{po.supplier_name || "No supplier"} · {po.branch_name}</div>
                  </div>
                  <span className="pill pill-info">{label(po.status)}</span>
                </div>
                <div className="muted">{po.lines.length} lines · expected {po.expected_at ? new Date(po.expected_at).toLocaleDateString() : "not set"}</div>
                {po.status === "draft" ? <button className="button" type="button" onClick={() => void order(po.id)}>Order</button> : null}
              </div>
            ))}
            {!orders.length ? <div className="muted">No purchase orders found.</div> : null}
          </div>
        </div>
        <div className="card">
          <div className="section-title">Deliveries</div>
          <div className="stack">
            {deliveries.map((delivery) => (
              <div className="subcard" key={delivery.id}>
                <strong>{delivery.stock_item_name}</strong>
                <div className="muted">Received {delivery.quantity_received} · damaged {delivery.damage_quantity}</div>
                <div className="muted">{delivery.purchase_order_number || "No PO"} · {delivery.batch_number || "No batch"}</div>
                {delivery.supplier_issue ? <div>{delivery.supplier_issue}</div> : null}
              </div>
            ))}
            {!deliveries.length ? <div className="muted">No deliveries found.</div> : null}
          </div>
        </div>
      </section>
    </AppShell>
  );
}
