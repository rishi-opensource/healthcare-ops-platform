import type { DashboardMetric } from "@healthcare/api-client";
import Link from "next/link";

export function StatusCard({ metric }: { metric: DashboardMetric }) {
  return (
    <Link href={metric.href} className={`card tone-${metric.tone}`}>
      <div className="muted">{metric.label}</div>
      <div className="metric-value">{metric.value}</div>
    </Link>
  );
}

