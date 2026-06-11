"use client";

import { useState, useCallback, useRef } from "react";
import { AccessGate } from "@/components/AccessGate";
import { ChatPanel } from "@/components/ChatPanel";
import { OrchestratorPanel } from "@/components/OrchestratorPanel";
import { TogglesPanel } from "@/components/TogglesPanel";
import {
  compyle,
  execute,
  getSessionId,
  logRun,
  orchestrate,
  setAccessCode,
  UnauthorizedError,
} from "@/lib/api";
import { DEFAULT_SETTINGS, IDLE_PROGRESS } from "@/lib/types";
import type {
  ChatMessage,
  PipelineProgress,
  PipelineResult,
  ToggleSettings,
} from "@/lib/types";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [settings, setSettings] = useState<ToggleSettings>(DEFAULT_SETTINGS);
  const [progress, setProgress] = useState<PipelineProgress>(IDLE_PROGRESS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gateOpen, setGateOpen] = useState(false);
  // Survives re-renders without triggering them: the message to retry after
  // the access gate, and the Supabase conversation id for this thread.
  const pendingRef = useRef<string | null>(null);
  const conversationRef = useRef<string | null>(null);

  const runStages = useCallback(
    async (text: string) => {
      setLoading(true);
      setError(null);

      try {
        // Stage 1 — orchestrator frames the labor task.
        setProgress({ stage: "orchestrating" });
        const { instruction, orchestrator_thinking } = await orchestrate(
          text,
          settings,
        );

        // Stage 2 — labor model executes.
        setProgress({ stage: "executing", instruction, orchestrator_thinking });
        const { labor_output, labor_thinking, direct_response } = await execute(
          text,
          instruction,
          settings,
        );

        // Stage 3 — compyler gates the output (plus voice check if present).
        setProgress({
          stage: "compyling",
          instruction,
          orchestrator_thinking,
          labor_output,
          labor_thinking,
          direct_response,
        });
        const labor_verdict = await compyle(
          text,
          instruction,
          labor_output,
          false,
          settings,
        );
        const voice_verdict = direct_response
          ? await compyle(text, instruction, direct_response, true, settings)
          : null;

        const result: PipelineResult = {
          orchestrator_instruction: instruction,
          orchestrator_thinking,
          labor_output,
          labor_thinking,
          direct_response,
          compiler: { labor_verdict, voice_verdict },
        };
        setProgress({
          stage: "done",
          instruction,
          orchestrator_thinking,
          labor_output,
          labor_thinking,
          direct_response,
          labor_verdict,
          voice_verdict,
        });

        const assistantMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          // Prefer the direct response if present; fall back to labor output.
          content: result.direct_response ?? result.labor_output,
          pipeline: result,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, assistantMsg]);

        // Fire-and-forget research logging.
        logRun({
          sessionId: getSessionId(),
          conversationId: conversationRef.current,
          message: text,
          result,
          settings,
        }).then((id) => {
          if (id) conversationRef.current = id;
        });
      } catch (err) {
        if (err instanceof UnauthorizedError) {
          pendingRef.current = text;
          setProgress(IDLE_PROGRESS);
          setGateOpen(true);
        } else {
          setProgress({
            stage: "error",
            error: err instanceof Error ? err.message : "Unknown error",
          });
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      } finally {
        setLoading(false);
      }
    },
    [settings],
  );

  const handleSend = useCallback(
    (text: string) => {
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMsg]);
      void runStages(text);
    },
    [runStages],
  );

  const handleAccessCode = useCallback(
    (code: string) => {
      setAccessCode(code);
      setGateOpen(false);
      const pending = pendingRef.current;
      pendingRef.current = null;
      if (pending) void runStages(pending); // retry the interrupted send
    },
    [runStages],
  );

  return (
    <div className="flex h-screen overflow-hidden">
      {gateOpen && <AccessGate onSubmit={handleAccessCode} />}

      {/* Left panel — live pipeline trace + compiler flags */}
      <aside className="w-72 shrink-0 border-r border-gray-800 overflow-y-auto">
        <OrchestratorPanel progress={progress} />
      </aside>

      {/* Center panel — chat */}
      <main className="flex-1 flex flex-col min-w-0">
        <ChatPanel
          messages={messages}
          onSend={handleSend}
          loading={loading}
          error={error}
          showOnlyFlags={settings.display.showOnlyCompilerFlags}
        />
      </main>

      {/* Right panel — toggles */}
      <aside className="w-72 shrink-0 border-l border-gray-800 overflow-y-auto">
        <TogglesPanel settings={settings} onChange={setSettings} />
      </aside>
    </div>
  );
}
