import { createApiClient } from "@healthcare/api-client";
import * as SecureStore from "expo-secure-store";

export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

const tokenKey = "healthcare.authToken";

let inMemoryToken: string | null = null;

export async function setStoredToken(token: string) {
  inMemoryToken = token;
  await SecureStore.setItemAsync(tokenKey, token);
}

export async function hydrateToken() {
  inMemoryToken = await SecureStore.getItemAsync(tokenKey);
  return inMemoryToken;
}

export function mobileApiClient() {
  return createApiClient(API_BASE_URL, () => inMemoryToken);
}

