"use client";

import type { EntityListItem, EntitySummary } from "@healthcare/api-client";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

function label(value: string) {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

export default function OnboardingPage() {
  const api = useMemo(() => webApiClient(), []);
  const [summary, setSummary] = useState<EntitySummary | null>(null);
  const [entities, setEntities] = useState<EntityListItem[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    setMessage("");
    try {
      const [nextSummary, entityPage] = await Promise.all([
        api.entitySummary(),
        api.listEntities({ status: "onboarding" })
      ]);
      setSummary(nextSummary);
      setEntities(entityPage.results);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load onboarding.");
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Phase 4</div>
          <h1 className="title">Onboarding workflows</h1>
          <p className="muted">Track entity onboarding progress, pending steps, approval readiness, tickets, and activation state.</p>
        </div>
      </div>
      {message ? <div className="alert">{message}</div> : null}
      <section className="grid metric-grid ticket-metrics">
        {[
          ["Draft", summary?.draft ?? 0],
          ["Onboarding", summary?.onboarding ?? 0],
          ["Waiting approval", summary?.waiting_approval ?? 0],
          ["Pending steps", summary?.pending_steps ?? 0],
          ["Active", summary?.active ?? 0]
        ].map(([name, value]) => (
          <div className="card metric-compact" key={name}>
            <div className="muted">{name}</div>
            <div className="metric-value">{value}</div>
          </div>
        ))}
      </section>
      <section className="card">
        <div className="section-title">In progress</div>
        <div className="ticket-list">
          {entities.map((entity) => (
            <a className="ticket-row" href="/entities" key={entity.id}>
              <span>
                <strong>{entity.display_name}</strong>
                <span>{label(entity.entity_type)}</span>
              </span>
              <span className="pill pill-warning">{label(entity.onboarding_status || "onboarding")}</span>
              <span className="muted">{entity.completed_step_count}/{entity.required_step_count} steps · {entity.responsible_email || "Unassigned"}</span>
            </a>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
