"use client";

import type { Branch, CreateEntityInput, Entity, EntityListItem, EntityStatus, EntityType, UserListItem } from "@healthcare/api-client";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { webApiClient } from "@/lib/api";

const entityTypes: EntityType[] = ["employee", "doctor", "contractor", "supplier", "inventory_item", "equipment", "patient_reference", "ai_agent"];
const statuses: EntityStatus[] = ["draft", "onboarding", "active", "suspended", "archived"];

const emptyForm: CreateEntityInput = {
  entity_type: "employee",
  display_name: "",
  status: "draft",
  branch: null,
  responsible_user: null,
  external_reference: "",
  profile: {}
};

function label(value: string) {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function entityTone(status: EntityStatus) {
  if (status === "active") return "pill-success";
  if (status === "suspended" || status === "archived") return "pill-danger";
  if (status === "onboarding") return "pill-warning";
  return "pill-info";
}

export default function EntitiesPage() {
  const api = useMemo(() => webApiClient(), []);
  const [entities, setEntities] = useState<EntityListItem[]>([]);
  const [selected, setSelected] = useState<Entity | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [form, setForm] = useState<CreateEntityInput>(emptyForm);
  const [message, setMessage] = useState("");

  async function loadEntities(nextStatus = statusFilter) {
    setMessage("");
    try {
      const [entityPage, branchPage, userPage] = await Promise.all([
        api.listEntities(nextStatus ? { status: nextStatus } : {}),
        api.listBranches(),
        api.listUsers()
      ]);
      setEntities(entityPage.results);
      setBranches(branchPage.results);
      setUsers(userPage.results);
      if (!selected && entityPage.results[0]) {
        setSelected(await api.getEntity(entityPage.results[0].id));
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load entities.");
    }
  }

  useEffect(() => {
    void loadEntities();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function createEntity(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const created = await api.createEntity({
      ...form,
      branch: form.branch ? Number(form.branch) : null,
      responsible_user: form.responsible_user ? Number(form.responsible_user) : null,
      profile: profileFromForm(form)
    });
    setForm(emptyForm);
    setSelected(created);
    await loadEntities();
  }

  function profileFromForm(input: CreateEntityInput) {
    if (input.entity_type === "employee" || input.entity_type === "doctor" || input.entity_type === "contractor") {
      return { employment_type: "full_time" };
    }
    if (input.entity_type === "supplier") {
      return { supplier_code: input.external_reference || undefined };
    }
    if (input.entity_type === "inventory_item") {
      return { sku: input.external_reference || undefined, unit: "unit", reorder_threshold: 1 };
    }
    if (input.entity_type === "ai_agent") {
      return { agent_code: input.external_reference || undefined, human_review_required: true };
    }
    return {};
  }

  async function startOnboarding() {
    if (!selected) return;
    await api.startEntityOnboarding(selected.id);
    setSelected(await api.getEntity(selected.id));
    await loadEntities();
  }

  async function activate() {
    if (!selected) return;
    const updated = await api.activateEntity(selected.id);
    setSelected(updated);
    await loadEntities();
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">Phase 4</div>
          <h1 className="title">Entity registry</h1>
          <p className="muted">Human and non-human records with profiles, QR identifiers, onboarding, tickets, and activation state.</p>
        </div>
        <select
          className="input compact-input"
          value={statusFilter}
          onChange={(event) => {
            setStatusFilter(event.target.value);
            void loadEntities(event.target.value);
          }}
          aria-label="Filter entities by status"
        >
          <option value="">All statuses</option>
          {statuses.map((status) => (
            <option key={status} value={status}>{label(status)}</option>
          ))}
        </select>
      </div>

      {message ? <div className="alert">{message}</div> : null}

      <div className="ticket-workspace">
        <section className="card ticket-list-panel">
          <div className="section-title">Registry</div>
          <div className="ticket-list">
            {entities.map((entity) => (
              <button className={`ticket-row ${selected?.id === entity.id ? "ticket-row-active" : ""}`} key={entity.id} onClick={() => void api.getEntity(entity.id).then(setSelected)} type="button">
                <span>
                  <strong>{entity.display_name}</strong>
                  <span>{label(entity.entity_type)}</span>
                </span>
                <span className={`pill ${entityTone(entity.status)}`}>{label(entity.status)}</span>
                <span className="muted">{entity.qr_code_value || "QR pending"}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="card ticket-detail-panel">
          {selected ? (
            <>
              <div className="detail-heading">
                <div>
                  <div className="eyebrow">{label(selected.entity_type)}</div>
                  <h2>{selected.display_name}</h2>
                  <p className="muted">{selected.external_reference || selected.qr_code_value || "No external reference"}</p>
                </div>
                <span className={`pill ${entityTone(selected.status)}`}>{label(selected.status)}</span>
              </div>
              <div className="detail-grid">
                <div>
                  <span className="label">Branch</span>
                  <div>{selected.branch_name || "No branch"}</div>
                </div>
                <div>
                  <span className="label">Responsible</span>
                  <div>{selected.responsible_email || "Unassigned"}</div>
                </div>
                <div>
                  <span className="label">QR / Barcode</span>
                  <div>{selected.qr_code_value || "Not assigned"}</div>
                </div>
              </div>
              <div className="button-row">
                <button className="button secondary-button" onClick={() => void startOnboarding()} type="button">Start onboarding</button>
                <button className="button" onClick={() => void activate()} type="button">Activate</button>
              </div>

              <div className="detail-columns">
                <div>
                  <div className="section-title">Onboarding</div>
                  {selected.onboarding ? (
                    <div className="stack">
                      <div className="subcard">
                        <strong>{selected.onboarding.workflow_template_name}</strong>
                        <span className="muted">{label(selected.onboarding.status)} · {selected.onboarding.completed_step_count}/{selected.onboarding.required_step_count} steps</span>
                      </div>
                      {selected.onboarding.step_completions.map((step) => (
                        <div className="subcard" key={step.id}>
                          <strong>{step.name}</strong>
                          <span className="muted">{label(step.status)} · {label(step.step_type)}</span>
                        </div>
                      ))}
                    </div>
                  ) : <p className="muted">Onboarding has not started.</p>}
                </div>
                <div>
                  <div className="section-title">Lifecycle</div>
                  <div className="timeline">
                    {selected.lifecycle_events.map((event) => (
                      <div className="timeline-item" key={event.id}>
                        <strong>{label(event.to_status)}</strong>
                        <span className="muted">{event.note || "Status updated"}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          ) : <p className="muted">Select an entity.</p>}
        </section>

        <section className="card ticket-create-panel">
          <div className="section-title">Create entity</div>
          <form className="form wide-form" onSubmit={(event) => void createEntity(event)}>
            <label className="field">
              <span className="label">Display name</span>
              <input className="input" required value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} />
            </label>
            <label className="field">
              <span className="label">Type</span>
              <select className="input" value={form.entity_type} onChange={(event) => setForm({ ...form, entity_type: event.target.value as EntityType })}>
                {entityTypes.map((type) => <option key={type} value={type}>{label(type)}</option>)}
              </select>
            </label>
            <label className="field">
              <span className="label">External reference</span>
              <input className="input" value={form.external_reference} onChange={(event) => setForm({ ...form, external_reference: event.target.value })} />
            </label>
            <label className="field">
              <span className="label">Branch</span>
              <select className="input" value={form.branch || ""} onChange={(event) => setForm({ ...form, branch: event.target.value ? Number(event.target.value) : null })}>
                <option value="">No branch</option>
                {branches.map((branch) => <option key={branch.id} value={branch.id}>{branch.name}</option>)}
              </select>
            </label>
            <label className="field">
              <span className="label">Responsible user</span>
              <select className="input" value={form.responsible_user || ""} onChange={(event) => setForm({ ...form, responsible_user: event.target.value ? Number(event.target.value) : null })}>
                <option value="">Unassigned</option>
                {users.map((user) => <option key={user.id} value={user.id}>{user.full_name || user.email}</option>)}
              </select>
            </label>
            <button className="button" type="submit">Create entity</button>
          </form>
        </section>
      </div>
    </AppShell>
  );
}
