"use client";

import type { AttendanceRecord, HandoverNote, WorkforceSummary } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

function label(value: string) {
  return value.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join(" ");
}

export default function AttendancePage() {
  const [summary, setSummary] = useState<WorkforceSummary | null>(null);
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [handovers, setHandovers] = useState<HandoverNote[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    const api = webApiClient();
    const [nextSummary, attendancePage, handoverPage] = await Promise.all([
      api.workforceSummary(),
      api.listAttendanceRecords(),
      api.listHandoverNotes()
    ]);
    setSummary(nextSummary);
    setRecords(attendancePage.results);
    setHandovers(handoverPage.results);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error instanceof Error ? error.message : "Unable to load attendance."));
  }, []);

  async function approve(id: number) {
    await webApiClient().approveAttendance(id);
    await load();
  }

  async function acknowledge(id: number) {
    await webApiClient().acknowledgeHandover(id);
    await load();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Attendance</div>
          <h1 className="title">Attendance and handover</h1>
          <p className="muted">Clock records, exceptions, handover notes, and shift readiness.</p>
        </div>
        <div className="card">Clocked in: {summary?.clocked_in ?? 0}</div>
      </div>
      {message ? <div className="alert">{message}</div> : null}
      <section className="dashboard-grid">
        <div className="card">
          <div className="section-title">Attendance records</div>
          <div className="stack">
            {records.map((record) => (
              <div className="subcard" key={record.id}>
                <strong>{record.staff_email}</strong>
                <div className="muted">{new Date(record.clock_in_at).toLocaleString()} · {label(record.status)}</div>
                {record.exception_note ? <div>{record.exception_note}</div> : null}
                {!record.approved_at ? <button className="button" type="button" onClick={() => void approve(record.id)}>Approve</button> : null}
              </div>
            ))}
            {!records.length ? <div className="muted">No attendance records found.</div> : null}
          </div>
        </div>
        <div className="card">
          <div className="section-title">Handovers</div>
          <div className="stack">
            {handovers.map((note) => (
              <div className="subcard" key={note.id}>
                <strong>{note.title}</strong>
                <div className="muted">{note.assigned_to_email || "Unassigned"} · {label(note.status)}</div>
                <div>{note.body}</div>
                {note.status === "open" ? <button className="button" type="button" onClick={() => void acknowledge(note.id)}>Acknowledge</button> : null}
              </div>
            ))}
            {!handovers.length ? <div className="muted">No handover notes found.</div> : null}
          </div>
        </div>
      </section>
    </AppShell>
  );
}
