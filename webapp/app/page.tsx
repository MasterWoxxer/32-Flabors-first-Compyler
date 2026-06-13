"use client";

import { useState, useCallback, useRef, useEffect } from "react";
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
  HistoryTurn,
  PipelineProgress,
  PipelineResult,
  ToggleSettings,
} from "@/lib/types";

const STORAGE_KEY = "32flavors-settings";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [settings, setSettings] = useState<ToggleSettings>(DEFAULT_SETTINGS);
  const [progress, setProgress] = useState<PipelineProgress>(IDLE_PROGRESS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gateOpen, setGateOpen] = useState(false);
  const pendingRef = useRef<string | null>(null);
  const conversationRef = useRef<string | null>(null);
  const historyRef = useRef<HistoryTurn[]>([]);

  // Load prior conversation turns from Supabase once on session start.
  useEffect(() => {
    const sessionId = getSessionId();
    let n = DEFAULT_SETTINGS.historyTurns;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) n = JSON.parse(stored)?.historyTurns ?? n;
    } catch { /* ignore */ }

    fetch(`/api/logs?sessionId=${encodeURIComponent(sessionId)}&n=${n}`)
      .then((r) => r.json())
      .then((data: { turns?: HistoryTurn[] }) => {
        if (data.turns?.length) historyRef.current = data.turns;
      })
      .catch(() => { /* history is best-effort */ });
  }, []);

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
          historyRef.current,
        );

        // Stage 2 — labor model executes.
        setProgress({ stage: "executing", instruction, orchestrator_thinking });
        const { labor_output, labor_thinking, direct_response } = await execute(
          text,
          instruction,
          settings,
        );

        // Stage 3 — compyler gates the output.
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
          content: result.direct_response ?? result.labor_output,
          pipeline: result,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, assistantMsg]);

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
      if (pending) void runStages(pending);
    },
    [runStages],
  );

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {gateOpen && <AccessGate onSubmit={handleAccessCode} />}

      {/* Header bar */}
      <header className="shrink-0 border-b border-gray-800 px-6 py-3">
        <h1 className="text-base font-semibold text-gray-100 leading-tight">
          32 Flavors: Show My Work Alpha
        </h1>
        <p className="text-xs text-gray-500 leading-snug mt-1 max-w-4xl">
          This interface allows you to talk to an LLM that is guided by a process designed
          to limit hallucinations, drift, lying, and treading into the human user&apos;s lane.
          You can transparently see in the left sidebar the thinking of the models as they
          decide how to respond to you. On the right is a control panel where you can change
          the settings for the orchestrator, the model, and the Compyler&nbsp;(TM).
        </p>
      </header>

      {/* Three-panel layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel — live pipeline trace */}
        <aside className="w-[27rem] shrink-0 border-r border-gray-800 overflow-y-auto">
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

        {/* Right panel — control panel */}
        <aside className="w-72 shrink-0 border-l border-gray-800 overflow-y-auto">
          <TogglesPanel settings={settings} onChange={setSettings} />
        </aside>
      </div>
    </div>
  );
}
