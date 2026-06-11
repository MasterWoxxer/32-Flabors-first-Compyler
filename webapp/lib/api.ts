/**
 * Client-side API helpers.
 * All network calls go through Next.js BFF routes — never directly to the Python service.
 * Every call carries the tester access code (x-access-code) when one is stored.
 */

import type { CompilerVerdict, PipelineResult, ToggleSettings } from "./types";

const ACCESS_CODE_KEY = "32flavors-access-code";
const SESSION_ID_KEY = "32flavors-session-id";

/** Thrown on 401 so the UI can show the access-code gate and retry. */
export class UnauthorizedError extends Error {
  constructor() {
    super("Invalid or missing access code");
    this.name = "UnauthorizedError";
  }
}

export function getAccessCode(): string {
  try {
    return localStorage.getItem(ACCESS_CODE_KEY) ?? "";
  } catch {
    return "";
  }
}

export function setAccessCode(code: string): void {
  try {
    localStorage.setItem(ACCESS_CODE_KEY, code.trim());
  } catch {
    /* ignore */
  }
}

/** Stable anonymous id for this browser — becomes a real user id post-auth. */
export function getSessionId(): string {
  try {
    let id = localStorage.getItem(SESSION_ID_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(SESSION_ID_KEY, id);
    }
    return id;
  } catch {
    return "anonymous";
  }
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const code = getAccessCode();
  if (code) headers["x-access-code"] = code;

  const res = await fetch(path, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (res.status === 401) throw new UnauthorizedError();
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

// ── Staged pipeline calls — one LLM call per request ─────────────────────────

export function orchestrate(
  message: string,
  settings: ToggleSettings,
): Promise<{ instruction: string; orchestrator_thinking: string | null }> {
  return post("/api/pipeline/orchestrate", { message, settings });
}

export function execute(
  message: string,
  instruction: string,
  settings: ToggleSettings,
): Promise<{
  labor_output: string;
  labor_thinking: string | null;
  direct_response: string | null;
}> {
  return post("/api/pipeline/execute", { message, instruction, settings });
}

export function compyle(
  message: string,
  instruction: string,
  output: string,
  checkVoice: boolean,
  settings: ToggleSettings,
): Promise<CompilerVerdict> {
  return post("/api/pipeline/compyle", {
    message,
    instruction,
    output,
    check_voice: checkVoice,
    settings,
  });
}

// ── Research logging ─────────────────────────────────────────────────────────

export async function logRun(payload: {
  sessionId: string;
  conversationId: string | null;
  message: string;
  result: PipelineResult;
  settings: ToggleSettings;
}): Promise<string | null> {
  try {
    const res = await post<{ ok: boolean; conversationId?: string }>(
      "/api/log",
      payload,
    );
    return res.conversationId ?? null;
  } catch {
    return null; // logging must never break the user flow
  }
}

export async function saveToggles(settings: ToggleSettings): Promise<void> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const code = getAccessCode();
  if (code) headers["x-access-code"] = code;
  await fetch("/api/toggles", {
    method: "POST",
    headers,
    body: JSON.stringify(settings),
  });
}
