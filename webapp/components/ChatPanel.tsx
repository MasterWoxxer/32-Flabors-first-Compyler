"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage, CompylerResult } from "@/lib/types";
import { CompylerMessage } from "./CompilerFlag";

function messageResult(msg: ChatMessage): CompylerResult | null {
  if (!msg.pipeline) return null;
  return msg.pipeline.direct_response
    ? (msg.pipeline.compiler.voice_verdict ?? msg.pipeline.compiler.labor_verdict)
    : msg.pipeline.compiler.labor_verdict;
}

export function ChatPanel({
  messages,
  onSend,
  loading,
  error,
  showOnlyFlags,
  approvedSections,
  pendingCheckIds,
}: {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  loading: boolean;
  error: string | null;
  showOnlyFlags: boolean;
  approvedSections: Record<string, string[]>;
  pendingCheckIds: Set<string>;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = () => {
    const val = inputRef.current?.value.trim();
    if (!val || loading) return;
    onSend(val);
    inputRef.current!.value = "";
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => {
          if (showOnlyFlags && msg.role === "assistant" && !msg.pipeline) return null;

          const compylerResult = msg.role === "assistant" ? messageResult(msg) : null;
          const approved = approvedSections[msg.id] ?? [];
          const hasPending = pendingCheckIds.has(msg.id);

          return (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[70%] rounded-lg px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-indigo-700 text-white text-sm"
                    : "bg-gray-800 text-gray-100"
                }`}
              >
                {msg.role === "user" || !compylerResult ? (
                  <p className="whitespace-pre-wrap leading-relaxed text-sm">{msg.content}</p>
                ) : (
                  <CompylerMessage
                    result={compylerResult}
                    approvedTexts={approved}
                    hasPendingChecks={hasPending}
                  />
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-lg px-4 py-3 text-sm text-gray-400 animate-pulse">
              Running pipeline…
            </div>
          </div>
        )}

        {error && (
          <p className="text-xs text-red-400 text-center py-2">Error: {error}</p>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="border-t border-gray-800 p-4">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            rows={2}
            onKeyDown={handleKeyDown}
            placeholder="Type your input… (Enter to send, Shift+Enter for newline)"
            disabled={loading}
            className="flex-1 resize-none rounded-lg bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
          />
          <button
            onClick={submit}
            disabled={loading}
            className="shrink-0 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 px-4 py-2 text-sm font-medium text-white transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
