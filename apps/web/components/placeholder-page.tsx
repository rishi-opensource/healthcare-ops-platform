import { AppShell } from "@/components/app-shell";

type PlaceholderPageProps = {
  eyebrow: string;
  title: string;
  description: string;
};

export function PlaceholderPage({ eyebrow, title, description }: PlaceholderPageProps) {
  return (
    <AppShell>
      <div className="page-header">
        <div>
          <div className="eyebrow">{eyebrow}</div>
          <h1 className="title">{title}</h1>
          <p className="muted">{description}</p>
        </div>
      </div>
      <div className="card">Phase 2 route shell. The vertical slice for this module will replace this panel.</div>
    </AppShell>
  );
}

