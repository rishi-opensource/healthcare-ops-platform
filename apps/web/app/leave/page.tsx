"use client";

import type { LeaveRequest, WorkforceSummary } from "@healthcare/api-client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

function label(value: string) {
  return value.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join(" ");
}

export default function LeavePage() {
  const [summary, setSummary] = useState<WorkforceSummary | null>(null);
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    const api = webApiClient();
    const [nextSummary, requestPage] = await Promise.all([api.workforceSummary(), api.listLeaveRequests()]);
    setSummary(nextSummary);
    setRequests(requestPage.results);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error instanceof Error ? error.message : "Unable to load leave."));
  }, []);

  async function review(id: number, status: "approved" | "rejected") {
    await webApiClient().reviewLeaveRequest(id, status, status === "approved" ? "Approved from leave workspace." : "Rejected from leave workspace.");
    await load();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Leave</div>
          <h1 className="title">Leave requests</h1>
          <p className="muted">Leave approvals, roster impact, and pending workforce coverage decisions.</p>
        </div>
        <div className="card">Open requests: {summary?.open_leave_requests ?? 0}</div>
      </div>
      {message ? <div className="alert">{message}</div> : null}
      <section className="card">
        <div className="section-title">Requests</div>
        <div className="stack">
          {requests.map((request) => (
            <div className="subcard" key={request.id}>
              <div className="detail-heading">
                <div>
                  <strong>{request.staff_email}</strong>
                  <div className="muted">{label(request.leave_type)} · {new Date(request.starts_at).toLocaleDateString()} - {new Date(request.ends_at).toLocaleDateString()}</div>
                </div>
                <span className="pill pill-warning">{label(request.status)}</span>
              </div>
              <div>{request.reason || "No reason provided."}</div>
              {request.status === "requested" ? (
                <div className="button-row">
                  <button className="button" type="button" onClick={() => void review(request.id, "approved")}>Approve</button>
                  <button className="button danger-button" type="button" onClick={() => void review(request.id, "rejected")}>Reject</button>
                </div>
              ) : null}
            </div>
          ))}
          {!requests.length ? <div className="muted">No leave requests found.</div> : null}
        </div>
      </section>
    </AppShell>
  );
}
