"use client";

import type { ReportExport, UserTaskSummary } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

export default function ReportsPage() {
  const [rows, setRows] = useState<UserTaskSummary[]>([]);
  const [reportExport, setReportExport] = useState<ReportExport | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const api = webApiClient();
    Promise.all([api.userTaskSummary(), api.exportReport("ticket_status")])
      .then(([nextRows, nextExport]) => {
        setRows(nextRows);
        setReportExport(nextExport);
      })
      .catch((error) => setMessage(error instanceof Error ? error.message : "Unable to load reports."));
  }, []);

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Reports</div>
          <h1 className="title">Back-office reporting</h1>
          <p className="muted">Completed-task summaries, payroll readiness, corrections, and exportable status data.</p>
        </div>
        <div className="card">{reportExport ? `Export ready: ${reportExport.report_type}` : "Loading export..."}</div>
      </div>
      {message ? <div className="alert">{message}</div> : null}

      <section className="card">
        <div className="section-title">User completed-task summary</div>
        <div className="table">
          <div className="table-row table-head">
            <span>User</span>
            <span>Tasks</span>
            <span>Minutes</span>
            <span>Payroll ready</span>
            <span>Corrections</span>
            <span>Feedback</span>
          </div>
          {rows.map((row) => (
            <div className="table-row" key={row.user_id ?? row.email ?? "unknown"}>
              <span>{row.full_name || row.email || "Unassigned"}</span>
              <span>{row.completed_tasks}</span>
              <span>{row.total_minutes}</span>
              <span>{row.payroll_ready}</span>
              <span>{row.correction_requests}</span>
              <span>{row.appraisal_feedback}</span>
            </div>
          ))}
          {!rows.length ? <div className="muted">No completed task records yet.</div> : null}
        </div>
      </section>

      <section className="card" style={{ marginTop: 18 }}>
        <div className="section-title">Ticket status export preview</div>
        <div className="stack">
          {(reportExport?.rows ?? []).map((row, index) => (
            <div className="subcard" key={`${String(row.status)}-${index}`}>
              <strong>{String(row.status)}</strong>
              <span className="muted">{String(row.count)} tickets</span>
            </div>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
