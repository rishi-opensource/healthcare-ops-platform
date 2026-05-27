"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { setStoredToken, webApiClient } from "@/lib/api";

type LoginFormValues = {
  email: string;
  password: string;
};

export default function LoginPage() {
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, formState } = useForm<LoginFormValues>({
    defaultValues: {
      email: "admin@healthcare.local",
      password: "ChangeMe123!"
    }
  });

  async function onSubmit(values: LoginFormValues) {
    setError(null);
    try {
      const result = await webApiClient().login(values.email, values.password);
      setStoredToken(result.token);
      window.location.href = "/dashboard";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <main className="main">
      <div className="page-header">
        <div>
          <div className="eyebrow">Secure access</div>
          <h1 className="title">Healthcare Doctors OS</h1>
          <p className="muted">Sign in to manage tickets, approvals, rosters, inventory, and compliance.</p>
        </div>
      </div>

      <form className="form card" onSubmit={handleSubmit(onSubmit)}>
        <div className="field">
          <label className="label" htmlFor="email">
            Email
          </label>
          <input className="input" id="email" type="email" {...register("email", { required: true })} />
        </div>
        <div className="field">
          <label className="label" htmlFor="password">
            Password
          </label>
          <input className="input" id="password" type="password" {...register("password", { required: true })} />
        </div>
        {error ? <div className="alert">{error}</div> : null}
        <button className="button" type="submit" disabled={formState.isSubmitting}>
          {formState.isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}

