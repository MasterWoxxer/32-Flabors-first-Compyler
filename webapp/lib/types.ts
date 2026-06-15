/**
 * Canonical contract types shared between Next.js API routes and UI components.
 * These match the Python service's run_pipeline() return shape 1-to-1.
 */

// ── Compyler section result ──────────────────────────────────────────────────

export type SectionDecision = "PASS" | "CHECK" | "FAIL";

export interface CompylerSection {
  text: string;
  decision: SectionDecision;
  note: string;
}

export interface CompylerResult {
  sections: CompylerSection[];
  /** The raw output text that was segmented. */
  raw: string;
}

/** One labor sub-task emitted by the orchestrator. */
export interface Segment {
  title: string;
  instruction: string;
}

/** Full structured output from one pipeline run. */
export interface PipelineResult {
  orchestrator_instruction: string;
  orchestrator_thinking: string | null;
  labor_output: string;
  labor_thinking: string | null;
  direct_response: string | null;
  compiler: {
    labor_verdict: CompylerResult;
    voice_verdict: CompylerResult | null;
  };
}

// ── Toggle settings ─────────────────────────────────────────────────────────

export type ModelProvider = "claude" | "openai" | "gemini" | "xai";

export type ResponseLength = "full" | "one_page" | "400_words";

export interface ToggleSettings {
  model: ModelProvider;
  orchestrator: {
    strictMode: boolean;
    sessionInstructions: string;
  };
  compiler: {
    flagHallucinations: boolean;
    sensitivity: "low" | "medium" | "high";
  };
  display: {
    showOnlyCompilerFlags: boolean;
  };
  responseLength: ResponseLength;
  languageSmoothness: boolean;
  historyTurns: number;
  /** Placeholder — not yet wired; the orchestrator auto-decides segmentation. */
  segmentComplexQueries: boolean;
}

export const DEFAULT_SETTINGS: ToggleSettings = {
  model: "claude",
  orchestrator: { strictMode: false, sessionInstructions: "" },
  compiler: { flagHallucinations: true, sensitivity: "medium" },
  display: { showOnlyCompilerFlags: false },
  responseLength: "full",
  languageSmoothness: false,
  historyTurns: 0,
  segmentComplexQueries: false,
};

// ── Staged pipeline progress ─────────────────────────────────────────────────

export type PipelineStage =
  | "idle"
  | "orchestrating"
  | "executing"
  | "compyling"
  | "done"
  | "error";

export interface PipelineProgress {
  stage: PipelineStage;
  instruction?: string;
  orchestrator_thinking?: string | null;
  labor_output?: string;
  labor_thinking?: string | null;
  direct_response?: string | null;
  labor_verdict?: CompylerResult;
  voice_verdict?: CompylerResult | null;
  error?: string;
  /** 1-based index of the segment currently running, when segmented. */
  segmentIndex?: number;
  segmentCount?: number;
  segmentTitle?: string;
}

export const IDLE_PROGRESS: PipelineProgress = { stage: "idle" };

// ── Chat history ─────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  pipeline?: PipelineResult;
  /** Segment title, shown as a header on the bubble in multi-segment turns. */
  title?: string;
  timestamp: number;
}

export interface HistoryTurn {
  role: "user" | "assistant";
  content: string;
}
