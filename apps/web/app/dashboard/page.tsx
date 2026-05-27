"use client";

import type { DashboardMetric, TicketSummary } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { StatusCard } from "@/components/status-card";
import { webApiClient } from "@/lib/api";

function metricsFromSummary(summary: TicketSummary | null): DashboardMetric[] {
  return [
    { label: "Open tickets", value: String(summary?.open ?? 0), href: "/tickets", tone: "info" },
    {
      label: "Waiting approval",
      value: String(summary?.waiting_approval ?? 0),
      href: "/tickets?status=waiting_approval",
      tone: "warning"
    },
    {
      label: "Needs correction",
      value: String(summary?.needs_correction ?? 0),
      href: "/tickets?status=needs_correction",
      tone: "danger"
    },
    { label: "Assigned to me", value: String(summary?.assigned_to_me ?? 0), href: "/tickets", tone: "neutral" },
    { label: "Urgent tickets", value: String(summary?.urgent ?? 0), href: "/tickets", tone: "danger" },
    { label: "Completed", value: String(summary?.completed ?? 0), href: "/tickets?status=completed", tone: "success" }
  ];
}

export default function DashboardPage() {
  const [apiStatus, setApiStatus] = useState("Checking API...");
  const [summary, setSummary] = useState<TicketSummary | null>(null);

  useEffect(() => {
    const api = webApiClient();
    api
      .health()
      .then((result) => setApiStatus(`${result.service} ${result.version} is ${result.status}`))
      .catch(() => setApiStatus("API unavailable"));
    api.ticketSummary().then(setSummary).catch(() => setSummary(null));
  }, []);

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Phase 3 operations</div>
          <h1 className="title">Command dashboard</h1>
          <p className="muted">Ticket workload, approvals, corrections, and urgent follow-up.</p>
        </div>
        <div className="card">{apiStatus}</div>
      </div>

      <section className="grid metric-grid">
        {metricsFromSummary(summary).map((metric) => (
          <StatusCard key={metric.label} metric={metric} />
        ))}
      </section>
    </AppShell>
  );
}
