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
  /** Reasoning trace, when the compyler runs on a reasoning model. */
  thinking?: string | null;
}

/** Full structured output from one pipeline run. */
export interface PipelineResult {
  orchestrator_instruction: string;
  /** Reasoning trace from the orchestrator (Magistral models); null otherwise. */
  orchestrator_thinking: string | null;
  labor_output: string;
  /** Extended-thinking trace from the labor model (Claude); null otherwise. */
  labor_thinking: string | null;
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
    /** Free-text instructions shaping orchestrator behaviour for this session.
     *  Always subordinate to the built-in scope constraints. */
    sessionInstructions: string;
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
  orchestrator: { strictMode: false, sessionInstructions: "" },
  compiler: { flagHallucinations: true, sensitivity: "medium" },
  display: { showOnlyCompilerFlags: false },
};

// ── Staged pipeline progress ─────────────────────────────────────────────────

export type PipelineStage =
  | "idle"
  | "orchestrating"
  | "executing"
  | "compyling"
  | "done"
  | "error";

/** Live state of the run in flight — drives the left panel's unfolding view. */
export interface PipelineProgress {
  stage: PipelineStage;
  instruction?: string;
  orchestrator_thinking?: string | null;
  labor_output?: string;
  labor_thinking?: string | null;
  direct_response?: string | null;
  labor_verdict?: CompilerVerdict;
  voice_verdict?: CompilerVerdict | null;
  error?: string;
}

export const IDLE_PROGRESS: PipelineProgress = { stage: "idle" };

// ── Chat history ─────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  /** Only present on assistant messages. */
  pipeline?: PipelineResult;
  timestamp: number;
}
