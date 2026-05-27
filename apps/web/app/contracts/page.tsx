"use client";

import type { ComplianceSummary, ConsentRecord, DocumentAssignment } from "@healthcare/api-client";
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
  if (status === "signed" || status === "acknowledged" || status === "given") return "pill-success";
  if (status === "expired" || status === "withdrawn" || status === "cancelled") return "pill-danger";
  return "pill-warning";
}

function dateLabel(value: string | null) {
  return value ? new Date(value).toLocaleDateString() : "No date";
}

export default function ContractsPage() {
  const api = useMemo(() => webApiClient(), []);
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [documents, setDocuments] = useState<DocumentAssignment[]>([]);
  const [consents, setConsents] = useState<ConsentRecord[]>([]);
  const [selected, setSelected] = useState<DocumentAssignment | null>(null);
  const [message, setMessage] = useState("");

  async function load() {
    setMessage("");
    try {
      const [nextSummary, documentPage, consentPage] = await Promise.all([
        api.complianceSummary(),
        api.listDocumentAssignments(),
        api.listConsentRecords()
      ]);
      setSummary(nextSummary);
      setDocuments(documentPage.results);
      setConsents(consentPage.results);
      setSelected((current) => current ?? documentPage.results[0] ?? null);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load contracts and consent.");
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function acknowledge() {
    if (!selected) return;
    const updated = await api.acknowledgeDocument(
      selected.id,
      "Acknowledged from compliance workspace.",
      "Digital acknowledgement"
    );
    setSelected(updated);
    await load();
  }

  async function sign() {
    if (!selected) return;
    const updated = await api.signDocument(selected.id, "Signed from compliance workspace.", "Digital signature");
    setSelected(updated);
    await load();
  }

  async function withdrawConsent(id: number) {
    await api.withdrawConsent(id);
    await load();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Phase 5</div>
          <h1 className="title">Contracts and consent</h1>
          <p className="muted">Assignable contracts, policy acknowledgements, consent records, expiry, renewal, evidence, and audit-ready status.</p>
        </div>
      </div>

      {message ? <div className="alert">{message}</div> : null}

      <section className="grid metric-grid ticket-metrics">
        {[
          ["Assigned docs", summary?.assigned_documents ?? 0],
          ["Pending docs", summary?.pending_documents ?? 0],
          ["Signed docs", summary?.signed_documents ?? 0],
          ["Expiring docs", summary?.expiring_documents ?? 0],
          ["Active consents", summary?.active_consents ?? 0]
        ].map(([name, value]) => (
          <div className="card metric-compact" key={name}>
            <div className="muted">{name}</div>
            <div className="metric-value">{value}</div>
          </div>
        ))}
      </section>

      <div className="ticket-workspace">
        <section className="card ticket-list-panel">
          <div className="section-title">Document assignments</div>
          <div className="ticket-list">
            {documents.map((assignment) => (
              <button
                className={`ticket-row ${selected?.id === assignment.id ? "ticket-row-active" : ""}`}
                key={assignment.id}
                onClick={() => setSelected(assignment)}
                type="button"
              >
                <span>
                  <strong>{assignment.template_name}</strong>
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
                  <div className="eyebrow">{label(selected.template_type)}</div>
                  <h2>{selected.template_name}</h2>
                  <p className="muted">{selected.assigned_to_email || selected.assigned_to_entity_name || "No assignee"}</p>
                </div>
                <span className={`pill ${statusTone(selected.status)}`}>{label(selected.status)}</span>
              </div>
              <div className="detail-grid">
                <div>
                  <span className="label">Version</span>
                  <div>{selected.version}</div>
                </div>
                <div>
                  <span className="label">Due</span>
                  <div>{dateLabel(selected.due_at)}</div>
                </div>
                <div>
                  <span className="label">Expires</span>
                  <div>{dateLabel(selected.expires_at)}</div>
                </div>
                <div>
                  <span className="label">Evidence</span>
                  <div>{selected.evidence_label || "No evidence yet"}</div>
                </div>
              </div>
              <div className="button-row">
                <button className="button secondary-button" onClick={() => void acknowledge()} type="button">Acknowledge</button>
                <button className="button" onClick={() => void sign()} type="button">Sign</button>
              </div>
              <div className="section-title" style={{ marginTop: 18 }}>Acknowledgement</div>
              <p className="muted">{selected.acknowledgement_text || "No acknowledgement recorded."}</p>
            </>
          ) : <p className="muted">No document assignment selected.</p>}
        </section>

        <section className="card ticket-create-panel">
          <div className="section-title">Consent records</div>
          <div className="stack">
            {consents.map((consent) => (
              <div className="subcard" key={consent.id}>
                <strong>{consent.purpose}</strong>
                <span className="muted">{label(consent.consent_type)} · {consent.subject_user_email || consent.subject_entity_name || "No subject"}</span>
                <span className={`pill ${statusTone(consent.status)}`}>{label(consent.status)}</span>
                <button className="button danger-button" onClick={() => void withdrawConsent(consent.id)} type="button">Withdraw</button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
