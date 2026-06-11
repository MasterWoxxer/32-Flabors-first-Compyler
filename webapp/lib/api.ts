/**
 * Client-side API helpers.
 * All network calls go through Next.js BFF routes — never directly to the Python service.
 */

import type { PipelineResult, ToggleSettings } from "./types";

export async function runPipeline(
  message: string,
  settings: ToggleSettings,
): Promise<PipelineResult> {
  const res = await fetch("/api/pipeline", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, settings }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail ?? "Pipeline request failed");
  }
  return res.json() as Promise<PipelineResult>;
}

export async function saveToggles(settings: ToggleSettings): Promise<void> {
  await fetch("/api/toggles", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
}
