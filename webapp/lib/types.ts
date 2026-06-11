/**
 * Canonical contract types shared between Next.js API routes and UI components.
 * These match the Python service's run_pipeline() return shape 1-to-1.
 */

export type VerdictType =
  | "PASS"
  | "FAIL"
  | "MCQ"
  | "CURRENCY_FAIL"
  | "SCOPE_FAIL"
  | "VOICE_FAIL"
  | "CANDIDATE_FAIL"
  | "UNKNOWN";

export interface CompilerVerdict {
  verdict: VerdictType;
  /** Explanation text (empty on PASS). */
  body: string;
  /** Full raw text returned by the compyler. */
  raw: string;
}

/** Full structured output from one pipeline run. */
export interface PipelineResult {
  orchestrator_instruction: string;
  labor_output: string;
  direct_response: string | null;
  compiler: {
    labor_verdict: CompilerVerdict;
    voice_verdict: CompilerVerdict | null;
  };
}

// ── Toggle settings ─────────────────────────────────────────────────────────

export type ModelProvider = "claude" | "openai" | "gemini" | "xai";

export interface ToggleSettings {
  model: ModelProvider;
  orchestrator: {
    strictMode: boolean;
  };
  compiler: {
    flagHallucinations: boolean;
    sensitivity: "low" | "medium" | "high";
  };
  display: {
    showOnlyCompilerFlags: boolean;
  };
}

export const DEFAULT_SETTINGS: ToggleSettings = {
  model: "claude",
  orchestrator: { strictMode: false },
  compiler: { flagHallucinations: true, sensitivity: "medium" },
  display: { showOnlyCompilerFlags: false },
};

// ── Chat history ─────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  /** Only present on assistant messages. */
  pipeline?: PipelineResult;
  timestamp: number;
}
