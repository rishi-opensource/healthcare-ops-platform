"use client";

import type { Shift, WorkforceSummary } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

function label(value: string) {
  return value.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join(" ");
}

export default function RosterPage() {
  const [summary, setSummary] = useState<WorkforceSummary | null>(null);
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    const api = webApiClient();
    const [nextSummary, shiftPage] = await Promise.all([api.workforceSummary(), api.listShifts()]);
    setSummary(nextSummary);
    setShifts(shiftPage.results);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error instanceof Error ? error.message : "Unable to load roster."));
  }, []);

  async function publish(id: number) {
    await webApiClient().publishShift(id);
    await load();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Roster</div>
          <h1 className="title">Roster management</h1>
          <p className="muted">Shift allocation, coverage status, overtime visibility, and publication control.</p>
        </div>
        <div className="card">Published upcoming shifts: {summary?.published_shifts ?? 0}</div>
      </div>
      {message ? <div className="alert">{message}</div> : null}
      <section className="grid metric-grid">
        <div className="card"><div className="muted">Open leave</div><div className="metric-value">{summary?.open_leave_requests ?? 0}</div></div>
        <div className="card"><div className="muted">Clocked in</div><div className="metric-value">{summary?.clocked_in ?? 0}</div></div>
        <div className="card"><div className="muted">Exceptions</div><div className="metric-value">{summary?.attendance_exceptions ?? 0}</div></div>
      </section>
      <section className="card" style={{ marginTop: 18 }}>
        <div className="section-title">Shifts</div>
        <div className="stack">
          {shifts.map((shift) => (
            <div className="subcard" key={shift.id}>
              <div className="detail-heading">
                <div>
                  <strong>{shift.staff_email}</strong>
                  <div className="muted">{new Date(shift.starts_at).toLocaleString()} - {new Date(shift.ends_at).toLocaleTimeString()}</div>
                </div>
                <span className="pill pill-info">{label(shift.status)}</span>
              </div>
              <div className="muted">{shift.branch_name} · {shift.role_label || "Rostered staff"} · overtime {shift.overtime_minutes}m</div>
              {shift.status === "draft" ? (
                <button className="button" type="button" onClick={() => void publish(shift.id)}>Publish</button>
              ) : null}
            </div>
          ))}
          {!shifts.length ? <div className="muted">No shifts found.</div> : null}
        </div>
      </section>
    </AppShell>
  );
}
