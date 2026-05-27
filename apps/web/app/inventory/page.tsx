"use client";

import type { InventoryBatch, InventorySummary, StockItem } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

function label(value: string) {
  return value.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join(" ");
}

export default function InventoryPage() {
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [items, setItems] = useState<StockItem[]>([]);
  const [batches, setBatches] = useState<InventoryBatch[]>([]);
  const [message, setMessage] = useState("");
  const [barcode, setBarcode] = useState("093000000001");
  const [barcodeResult, setBarcodeResult] = useState("");

  async function load() {
    const api = webApiClient();
    const [nextSummary, itemPage, batchPage] = await Promise.all([
      api.inventorySummary(),
      api.listStockItems(),
      api.listInventoryBatches()
    ]);
    setSummary(nextSummary);
    setItems(itemPage.results);
    setBatches(batchPage.results);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error instanceof Error ? error.message : "Unable to load inventory."));
  }, []);

  async function issue(item: StockItem) {
    await webApiClient().moveStock(item.id, {
      movement_type: "issue",
      quantity_delta: -1,
      note: "Issued from inventory workspace."
    });
    await load();
  }

  async function reorder(item: StockItem) {
    const result = await webApiClient().createReorderTicket(item.id);
    setMessage(`Created reorder ticket ${result.ticket_number}.`);
    await load();
  }

  async function resolveBarcode() {
    try {
      const resolved = await webApiClient().resolveBarcode(barcode);
      setBarcodeResult(`${resolved.target_type}: ${resolved.label}`);
    } catch (error) {
      setBarcodeResult(error instanceof Error ? error.message : "Unable to resolve barcode.");
    }
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Inventory</div>
          <h1 className="title">Inventory and barcode control</h1>
          <p className="muted">Stock levels, batches, expiry, damaged goods, and reorder alerts.</p>
        </div>
        <div className="card">Low stock: {summary?.low_stock_items ?? 0}</div>
      </div>
      {message ? <div className="alert">{message}</div> : null}
      <section className="grid metric-grid">
        <div className="card"><div className="muted">Stock items</div><div className="metric-value">{summary?.stock_items ?? 0}</div></div>
        <div className="card"><div className="muted">Expiring batches</div><div className="metric-value">{summary?.expiring_batches ?? 0}</div></div>
        <div className="card"><div className="muted">Damaged deliveries</div><div className="metric-value">{summary?.damaged_deliveries ?? 0}</div></div>
        <div className="card"><div className="muted">Reorder tickets</div><div className="metric-value">{summary?.reorder_tickets ?? 0}</div></div>
      </section>
      <section className="card" style={{ marginTop: 18 }}>
        <div className="section-title">Barcode lookup</div>
        <div className="inline-form">
          <input
            className="input"
            value={barcode}
            onChange={(event) => setBarcode(event.target.value)}
            placeholder="Enter barcode"
          />
          <button className="button" type="button" onClick={() => void resolveBarcode()}>Resolve</button>
        </div>
        {barcodeResult ? <div className="subcard">{barcodeResult}</div> : null}
      </section>
      <section className="dashboard-grid" style={{ marginTop: 18 }}>
        <div className="card">
          <div className="section-title">Stock items</div>
          <div className="stack">
            {items.map((item) => (
              <div className="subcard" key={item.id}>
                <div className="detail-heading">
                  <div>
                    <strong>{item.name}</strong>
                    <div className="muted">{item.sku} · {item.quantity_on_hand} {item.unit} · threshold {item.reorder_threshold}</div>
                  </div>
                  <span className={`pill ${item.status === "low_stock" ? "pill-danger" : "pill-success"}`}>{label(item.status)}</span>
                </div>
                <div className="muted">{item.branch_name} · barcode {item.barcode || "not set"}</div>
                <div className="button-row">
                  <button className="button secondary-button" type="button" onClick={() => void issue(item)}>Issue 1</button>
                  <button className="button" type="button" onClick={() => void reorder(item)}>Reorder</button>
                </div>
              </div>
            ))}
            {!items.length ? <div className="muted">No stock items found.</div> : null}
          </div>
        </div>
        <div className="card">
          <div className="section-title">Batches</div>
          <div className="stack">
            {batches.map((batch) => (
              <div className="subcard" key={batch.id}>
                <strong>{batch.stock_item_name}</strong>
                <div className="muted">Batch {batch.batch_number} · qty {batch.quantity}</div>
                <div className="muted">Expiry {batch.expiry_date || "not set"} · {batch.location_label || "no location"}</div>
              </div>
            ))}
            {!batches.length ? <div className="muted">No batches found.</div> : null}
          </div>
        </div>
      </section>
    </AppShell>
  );
}
