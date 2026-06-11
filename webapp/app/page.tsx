"use client";

import { useState, useCallback } from "react";
import { ChatPanel } from "@/components/ChatPanel";
import { OrchestratorPanel } from "@/components/OrchestratorPanel";
import { TogglesPanel } from "@/components/TogglesPanel";
import { runPipeline } from "@/lib/api";
import { DEFAULT_SETTINGS } from "@/lib/types";
import type { ChatMessage, PipelineResult, ToggleSettings } from "@/lib/types";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [settings, setSettings] = useState<ToggleSettings>(DEFAULT_SETTINGS);
  const [lastPipeline, setLastPipeline] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = useCallback(
    async (text: string) => {
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);
      setError(null);

      try {
        const result = await runPipeline(text, settings);
        setLastPipeline(result);
        const assistantMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          // Prefer the direct response if present; fall back to labor output.
          content: result.direct_response ?? result.labor_output,
          pipeline: result,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    },
    [settings],
  );

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left panel — orchestrator trace + compiler flags */}
      <aside className="w-72 shrink-0 border-r border-gray-800 overflow-y-auto">
        <OrchestratorPanel pipeline={lastPipeline} />
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
