"use client";

import type { DashboardMetric, DashboardReport } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { StatusCard } from "@/components/status-card";
import { webApiClient } from "@/lib/api";

function metricsFromReport(report: DashboardReport | null): DashboardMetric[] {
  return [
    { label: "Open tickets", value: String(report?.tickets.open ?? 0), href: "/tickets", tone: "info" },
    {
      label: "Pending approvals",
      value: String(report?.tickets.pending_approvals ?? 0),
      href: "/tickets?status=waiting_approval",
      tone: "warning"
    },
    {
      label: "Overdue tickets",
      value: String(report?.tickets.overdue ?? 0),
      href: "/tickets",
      tone: "danger"
    },
    { label: "Users working", value: String(report?.workforce.users_working ?? 0), href: "/users", tone: "neutral" },
    {
      label: "Training overdue",
      value: String(report?.compliance.overdue_training ?? 0),
      href: "/training",
      tone: "warning"
    },
    {
      label: "Inventory alerts",
      value: String(report?.operations.inventory_alerts ?? 0),
      href: "/inventory",
      tone: "danger"
    }
  ];
}

export default function DashboardPage() {
  const [apiStatus, setApiStatus] = useState("Checking API...");
  const [report, setReport] = useState<DashboardReport | null>(null);

  useEffect(() => {
    const api = webApiClient();
    api
      .health()
      .then((result) => setApiStatus(`${result.service} ${result.version} is ${result.status}`))
      .catch(() => setApiStatus("API unavailable"));
    api.dashboardReport().then(setReport).catch(() => setReport(null));
  }, []);

  const daily = report?.daily_workspace;

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Phase 6 reporting</div>
          <h1 className="title">Command dashboard</h1>
          <p className="muted">Live operational workload, approvals, compliance, staff activity, and daily alerts.</p>
        </div>
        <div className="card">{apiStatus}</div>
      </div>

      <section className="grid metric-grid">
        {metricsFromReport(report).map((metric) => (
          <StatusCard key={metric.label} metric={metric} />
        ))}
      </section>

      <section className="dashboard-grid" style={{ marginTop: 18 }}>
        <div className="card">
          <div className="section-title">Daily workspace</div>
          <div className="detail-grid">
            <div>
              <div className="muted">Due today</div>
              <strong>{daily?.due_today ?? 0}</strong>
            </div>
            <div>
              <div className="muted">Handover</div>
              <strong>{daily?.handover ?? 0}</strong>
            </div>
            <div>
              <div className="muted">Stock warnings</div>
              <strong>{daily?.stock_warnings ?? 0}</strong>
            </div>
            <div>
              <div className="muted">Communication follow-ups</div>
              <strong>{daily?.communication_followups ?? 0}</strong>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="section-title">Compliance</div>
          <div className="detail-grid">
            <div>
              <div className="muted">Pending documents</div>
              <strong>{report?.compliance.pending_documents ?? 0}</strong>
            </div>
            <div>
              <div className="muted">Expiring documents</div>
              <strong>{report?.compliance.expiring_documents ?? 0}</strong>
            </div>
            <div>
              <div className="muted">Active consents</div>
              <strong>{report?.compliance.active_consents ?? 0}</strong>
            </div>
            <div>
              <div className="muted">Expiring training</div>
              <strong>{report?.compliance.expiring_training ?? 0}</strong>
            </div>
          </div>
        </div>
      </section>
    </AppShell>
  );
}
