"use client";

import type { ComplianceSummary, TrainingAssignment, TrainingModule } from "@healthcare/api-client";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

function label(value: string) {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function statusTone(status: string) {
  if (status === "completed" || status === "waived") return "pill-success";
  if (status === "overdue" || status === "expired") return "pill-danger";
  if (status === "in_progress") return "pill-info";
  return "pill-warning";
}

function dateLabel(value: string | null) {
  return value ? new Date(value).toLocaleDateString() : "No date";
}

export default function TrainingPage() {
  const api = useMemo(() => webApiClient(), []);
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [assignments, setAssignments] = useState<TrainingAssignment[]>([]);
  const [modules, setModules] = useState<TrainingModule[]>([]);
  const [selected, setSelected] = useState<TrainingAssignment | null>(null);
  const [message, setMessage] = useState("");

  async function load() {
    setMessage("");
    try {
      const [nextSummary, assignmentPage, modulePage] = await Promise.all([
        api.complianceSummary(),
        api.listTrainingAssignments(),
        api.listTrainingModules()
      ]);
      setSummary(nextSummary);
      setAssignments(assignmentPage.results);
      setModules(modulePage.results);
      setSelected((current) => current ?? assignmentPage.results[0] ?? null);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load training.");
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function completeSelected() {
    if (!selected) return;
    const updated = await api.completeTraining(selected.id, {
      completion_note: "Completed from training workspace.",
      quiz_score: selected.quiz_score ?? 92,
      evidence_label: "Digital certificate"
    });
    setSelected(updated);
    await load();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Phase 5</div>
          <h1 className="title">Training and certification</h1>
          <p className="muted">Assigned modules, completion, quiz placeholder, certificates, expiry, overdue state, and manager review.</p>
        </div>
      </div>

      {message ? <div className="alert">{message}</div> : null}

      <section className="grid metric-grid ticket-metrics">
        {[
          ["Assigned", summary?.assigned_training ?? 0],
          ["Completed", summary?.completed_training ?? 0],
          ["Overdue", summary?.overdue_training ?? 0],
          ["Expiring", summary?.expiring_training ?? 0]
        ].map(([name, value]) => (
          <div className="card metric-compact" key={name}>
            <div className="muted">{name}</div>
            <div className="metric-value">{value}</div>
          </div>
        ))}
      </section>

      <div className="ticket-workspace">
        <section className="card ticket-list-panel">
          <div className="section-title">Assignments</div>
          <div className="ticket-list">
            {assignments.map((assignment) => (
              <button
                className={`ticket-row ${selected?.id === assignment.id ? "ticket-row-active" : ""}`}
                key={assignment.id}
                onClick={() => setSelected(assignment)}
                type="button"
              >
                <span>
                  <strong>{assignment.module_title}</strong>
                  <span>{assignment.assigned_to_email || assignment.assigned_to_entity_name || "Unassigned"}</span>
                </span>
                <span className={`pill ${statusTone(assignment.status)}`}>{label(assignment.status)}</span>
                <span className="muted">Due {dateLabel(assignment.due_at)}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="card ticket-detail-panel">
          {selected ? (
            <>
              <div className="detail-heading">
                <div>
                  <div className="eyebrow">{label(selected.module_type)}</div>
                  <h2>{selected.module_title}</h2>
                  <p className="muted">{selected.assigned_to_email || selected.assigned_to_entity_name || "No assignee"}</p>
                </div>
                <span className={`pill ${statusTone(selected.status)}`}>{label(selected.status)}</span>
              </div>
              <div className="detail-grid">
                <div>
                  <span className="label">Due</span>
                  <div>{dateLabel(selected.due_at)}</div>
                </div>
                <div>
                  <span className="label">Completed</span>
                  <div>{dateLabel(selected.completed_at)}</div>
                </div>
                <div>
                  <span className="label">Expires</span>
                  <div>{dateLabel(selected.expires_at)}</div>
                </div>
                <div>
                  <span className="label">Quiz score</span>
                  <div>{selected.quiz_score ?? "Not recorded"}</div>
                </div>
                <div>
                  <span className="label">Certificate</span>
                  <div>{selected.certificate_label || "Pending"}</div>
                </div>
              </div>
              <button className="button" onClick={() => void completeSelected()} type="button">Mark completed</button>
              <div className="section-title" style={{ marginTop: 18 }}>Completion note</div>
              <p className="muted">{selected.completion_note || "No completion note recorded."}</p>
            </>
          ) : <p className="muted">No training assignment selected.</p>}
        </section>

        <section className="card ticket-create-panel">
          <div className="section-title">Training library</div>
          <div className="stack">
            {modules.map((module) => (
              <div className="subcard" key={module.id}>
                <strong>{module.title}</strong>
                <span className="muted">{label(module.module_type)} · v{module.version}</span>
                <span className="muted">{module.assignment_count} assignments · valid {module.validity_days} days</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
