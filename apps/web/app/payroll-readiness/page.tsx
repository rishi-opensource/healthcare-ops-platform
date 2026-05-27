"use client";

import type { TimesheetSummary, WorkforceSummary } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

function label(value: string) {
  return value.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join(" ");
}

export default function PayrollReadinessPage() {
  const [summary, setSummary] = useState<WorkforceSummary | null>(null);
  const [timesheets, setTimesheets] = useState<TimesheetSummary[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    const api = webApiClient();
    const [nextSummary, timesheetPage] = await Promise.all([api.workforceSummary(), api.listTimesheetSummaries()]);
    setSummary(nextSummary);
    setTimesheets(timesheetPage.results);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error instanceof Error ? error.message : "Unable to load payroll readiness."));
  }, []);

  async function review(id: number, status: "approved" | "needs_correction") {
    await webApiClient().reviewTimesheet(id, status, status === "approved" ? "Approved for payroll." : "Needs correction before payroll.");
    await load();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Payroll</div>
          <h1 className="title">Payroll readiness</h1>
          <p className="muted">Timesheets, worked minutes, task minutes, exceptions, and manager approval.</p>
        </div>
        <div className="card">Payroll ready: {summary?.payroll_ready ?? 0}</div>
      </div>
      {message ? <div className="alert">{message}</div> : null}
      <section className="card">
        <div className="section-title">Timesheets needing review: {summary?.timesheets_needing_review ?? 0}</div>
        <div className="table">
          <div className="table-row table-head">
            <span>Staff</span>
            <span>Worked</span>
            <span>Tasks</span>
            <span>Exceptions</span>
            <span>Status</span>
            <span>Action</span>
          </div>
          {timesheets.map((timesheet) => (
            <div className="table-row" key={timesheet.id}>
              <span>{timesheet.staff_email}</span>
              <span>{timesheet.worked_minutes}m</span>
              <span>{timesheet.task_minutes}m</span>
              <span>{timesheet.exception_count}</span>
              <span>{label(timesheet.status)}</span>
              <span className="button-row">
                <button className="button" type="button" onClick={() => void review(timesheet.id, "approved")}>Approve</button>
                <button className="button secondary-button" type="button" onClick={() => void review(timesheet.id, "needs_correction")}>Correct</button>
              </span>
            </div>
          ))}
          {!timesheets.length ? <div className="muted">No timesheet summaries found.</div> : null}
        </div>
      </section>
    </AppShell>
  );
}
