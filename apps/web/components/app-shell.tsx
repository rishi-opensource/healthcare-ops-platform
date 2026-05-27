"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { clearStoredToken, getStoredToken, webApiClient } from "@/lib/api";

const navItems = [
  ["Dashboard", "/dashboard"],
  ["Tickets", "/tickets"],
  ["Users", "/users"],
  ["Entities", "/entities"],
  ["Onboarding", "/onboarding"],
  ["Contracts", "/contracts"],
  ["Training", "/training"],
  ["Roster", "/roster"],
  ["Payroll", "/payroll-readiness"],
  ["Inventory", "/inventory"],
  ["Incidents", "/incidents"],
  ["AI Review", "/ai-review"],
  ["Reports", "/reports"],
  ["Audit", "/audit"]
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [userLabel, setUserLabel] = useState("Not signed in");

  useEffect(() => {
    const token = getStoredToken();
    setIsSignedIn(Boolean(token));
    if (!token) {
      setUserLabel("Not signed in");
      return;
    }
    webApiClient()
      .me()
      .then((user) => setUserLabel(user.full_name || user.email))
      .catch(() => {
        clearStoredToken();
        setIsSignedIn(false);
        setUserLabel("Not signed in");
      });
  }, []);

  function signOut() {
    clearStoredToken();
    setIsSignedIn(false);
    setUserLabel("Not signed in");
    window.location.href = "/login";
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="sidebar-title">Healthcare Doctors</div>
        <nav className="sidebar-nav" aria-label="Primary navigation">
          {navItems.map(([label, href]) => (
            <Link key={href} href={href} className="sidebar-link">
              {label}
            </Link>
          ))}
        </nav>
        <div className="sidebar-auth">
          <div className="sidebar-user">{userLabel}</div>
          {isSignedIn ? (
            <button className="sidebar-auth-button" onClick={signOut} type="button">
              Sign out
            </button>
          ) : (
            <Link href="/login" className="sidebar-auth-button">
              Sign in
            </Link>
          )}
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
