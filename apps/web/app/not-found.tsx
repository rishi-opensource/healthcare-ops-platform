import Link from "next/link";

export default function NotFound() {
  return (
    <main className="main">
      <h1 className="title">Page not found</h1>
      <p className="muted">This route is not implemented in the Phase 2 shell.</p>
      <Link className="button" href="/dashboard">
        Back to dashboard
      </Link>
    </main>
  );
}

