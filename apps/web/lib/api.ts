import { createApiClient } from "@healthcare/api-client";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export function getStoredToken() {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem("healthcare.authToken");
}

export function setStoredToken(token: string) {
  window.localStorage.setItem("healthcare.authToken", token);
}

export function clearStoredToken() {
  window.localStorage.removeItem("healthcare.authToken");
}

export function webApiClient() {
  return createApiClient(API_BASE_URL, getStoredToken);
}

