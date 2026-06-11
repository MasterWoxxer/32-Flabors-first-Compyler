"use client";

import { useEffect } from "react";
import { DEFAULT_SETTINGS } from "@/lib/types";
import type { ModelProvider, ToggleSettings } from "@/lib/types";
import { saveToggles } from "@/lib/api";

const STORAGE_KEY = "32flavors-settings";

const MODELS: { value: ModelProvider; label: string }[] = [
  { value: "claude", label: "Claude (Anthropic)" },
  { value: "openai", label: "GPT-4o (OpenAI)" },
  { value: "gemini", label: "Gemini (Google)" },
  { value: "xai", label: "Grok (xAI)" },
];

export function TogglesPanel({
  settings,
  onChange,
}: {
  settings: ToggleSettings;
  onChange: (s: ToggleSettings) => void;
}) {
  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) onChange(JSON.parse(stored) as ToggleSettings);
    } catch {
      /* ignore */
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Persist to localStorage + API on every change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch {
      /* ignore */
    }
    saveToggles(settings).catch(() => {});
  }, [settings]);

  // Type-safe deep-set helper
  const set = (path: string[], value: unknown) => {
    const next = structuredClone(settings) as unknown as Record<string, unknown>;
    let cursor = next;
    for (let i = 0; i < path.length - 1; i++) {
      cursor = cursor[path[i]] as Record<string, unknown>;
    }
    cursor[path[path.length - 1]] = value;
    onChange(next as unknown as ToggleSettings);
  };

  return (
    <div className="p-4 space-y-6">
      <h2 className="text-xs uppercase tracking-widest text-gray-500 font-semibold">
        Settings
      </h2>

      {/* ── Model selection ─────────────────────────────────────────── */}
      <section>
        <h3 className="text-xs text-gray-500 mb-2">Labor Model</h3>
        <div className="space-y-1.5">
          {MODELS.map(({ value, label }) => (
            <label key={value} className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="model"
                value={value}
                checked={settings.model === value}
                onChange={() => set(["model"], value)}
                className="accent-indigo-500"
              />
              <span className="text-xs text-gray-300">{label}</span>
            </label>
          ))}
        </div>
      </section>

      {/* ── Orchestrator rules ──────────────────────────────────────── */}
      <section>
        <h3 className="text-xs text-gray-500 mb-2">Orchestrator Rules</h3>
        <Toggle
          label="Strict Mode"
          description="Prevents the orchestrator from scoping out any topic the human explicitly raised"
          checked={settings.orchestrator.strictMode}
          onChange={(v) => set(["orchestrator", "strictMode"], v)}
        />
      </section>

      {/* ── Compiler ────────────────────────────────────────────────── */}
      <section className="space-y-2">
        <h3 className="text-xs text-gray-500">Compiler</h3>
        <Toggle
          label="Flag Hallucinations"
          description="Detect and flag confabulated grounding (CONFABULATION failure mode)"
          checked={settings.compiler.flagHallucinations}
          onChange={(v) => set(["compiler", "flagHallucinations"], v)}
        />
        <div>
          <label className="text-xs text-gray-400 block mb-1">Sensitivity</label>
          <select
            value={settings.compiler.sensitivity}
            onChange={(e) => set(["compiler", "sensitivity"], e.target.value)}
            className="w-full text-xs bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-gray-300 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
      </section>

      {/* ── Display filters ─────────────────────────────────────────── */}
      <section>
        <h3 className="text-xs text-gray-500 mb-2">Display</h3>
        <Toggle
          label="Show only compiler flags"
          description="Hide message content; show verdict badges only"
          checked={settings.display.showOnlyCompilerFlags}
          onChange={(v) => set(["display", "showOnlyCompilerFlags"], v)}
        />
      </section>

      {/* ── Reset ───────────────────────────────────────────────────── */}
      <button
        onClick={() => onChange(DEFAULT_SETTINGS)}
        className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
      >
        Reset to defaults
      </button>
    </div>
  );
}

// ── Shared toggle switch ─────────────────────────────────────────────────────

function Toggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-start gap-2 cursor-pointer py-0.5">
      {/* Custom switch */}
      <div className="relative mt-0.5 shrink-0">
        <input
          type="checkbox"
          className="sr-only"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <div
          className={`w-8 h-4 rounded-full transition-colors ${
            checked ? "bg-indigo-600" : "bg-gray-700"
          }`}
        />
        <div
          className={`absolute top-0.5 left-0.5 w-3 h-3 rounded-full bg-white transition-transform ${
            checked ? "translate-x-4" : "translate-x-0"
          }`}
        />
      </div>

      <div>
        <span className="text-xs text-gray-300 leading-tight">{label}</span>
        {description && (
          <p className="text-xs text-gray-600 leading-snug mt-0.5">{description}</p>
        )}
      </div>
    </label>
  );
}
