"use client";

import { useState } from "react";
import type { CompylerResult, CompylerSection } from "@/lib/types";

/**
 * Renders the assistant message in chat.
 * PASS sections: verbatim, clean.
 * FAIL sections: blocked inline, but expandable to reveal the flagged text, with a
 *   "Use anyway" override — the content belongs to the sovereign human user.
 * CHECK sections: not shown here — they live in the sidebar review queue.
 * Approved sections (user passed a CHECK or overrode a FAIL): subtle indigo border.
 */
export function CompylerMessage({
  result,
  approvedTexts = [],
  hasPendingChecks = false,
  messageId,
  onUseAnyway,
}: {
  result: CompylerResult;
  approvedTexts?: string[];
  hasPendingChecks?: boolean;
  messageId?: string;
  onUseAnyway?: (messageId: string, text: string) => void;
}) {
  const passSections = result.sections.filter((s) => s.decision === "PASS");
  // A FAIL the user already overrode renders below as an approved block, not as a flag.
  const failSections = result.sections.filter(
    (s) => s.decision === "FAIL" && !approvedTexts.includes(s.text),
  );
  const checkCount = result.sections.filter((s) => s.decision === "CHECK").length;

  return (
    <div className="space-y-2">
      {checkCount > 0 && hasPendingChecks && (
        <p className="text-xs text-gray-500 italic">
          {checkCount} section{checkCount > 1 ? "s" : ""} held for review — see left sidebar
        </p>
      )}

      {passSections.map((s, i) => (
        <p key={i} className="whitespace-pre-wrap leading-relaxed text-sm">
          {s.text}
        </p>
      ))}

      {failSections.map((s, i) => (
        <FailBlock
          key={i}
          section={s}
          messageId={messageId ?? ""}
          onUseAnyway={onUseAnyway}
        />
      ))}

      {approvedTexts.map((text, i) => (
        <div key={i} className="border-l-2 border-indigo-500 pl-3">
          <p className="whitespace-pre-wrap leading-relaxed text-sm text-gray-100">{text}</p>
          <span className="text-xs text-indigo-400 mt-0.5 block">added by you</span>
        </div>
      ))}
    </div>
  );
}

/**
 * Inline FAIL block in chat: collapsed to a flag, expandable to the full flagged
 * text, with a "Use anyway" override that promotes the content into the answer.
 */
function FailBlock({
  section,
  messageId,
  onUseAnyway,
}: {
  section: CompylerSection;
  messageId: string;
  onUseAnyway?: (messageId: string, text: string) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded border border-red-700 bg-red-900/30 px-3 py-1.5 text-sm text-red-300">
      <button
        onClick={() => setOpen((v) => !v)}
        className="font-mono text-left w-full flex items-center gap-1.5"
      >
        <span className="text-red-400">{open ? "▾" : "▸"}</span>
        <span>[Compyler blocked{section.note ? `: ${section.note}` : ""}]</span>
      </button>
      {open && (
        <div className="mt-2 space-y-2">
          <p className="whitespace-pre-wrap leading-relaxed text-sm text-gray-200">
            {section.text}
          </p>
          {onUseAnyway && (
            <button
              onClick={() => onUseAnyway(messageId, section.text)}
              className="text-sm px-3 py-1 rounded bg-red-800 hover:bg-red-700 text-red-100 transition-colors"
            >
              Use anyway
            </button>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Single CHECK section card for the sidebar review queue.
 * Shows full text — no truncation. Pass or Dismiss.
 */
export function CheckReviewCard({
  section,
  messageId,
  onPass,
  onDismiss,
}: {
  section: CompylerSection;
  messageId: string;
  onPass: (messageId: string, text: string) => void;
  onDismiss: (messageId: string, text: string) => void;
}) {
  return (
    <div className="rounded border border-amber-700 bg-amber-900/20 p-3 space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-sm font-mono font-bold text-amber-300">CHECK</span>
        {section.note && (
          <span className="text-sm text-amber-400 opacity-70">— {section.note}</span>
        )}
      </div>
      <p className="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
        {section.text}
      </p>
      <div className="flex gap-2 pt-1">
        <button
          onClick={() => onPass(messageId, section.text)}
          className="text-sm px-3 py-1 rounded bg-indigo-700 hover:bg-indigo-600 text-white transition-colors"
        >
          Pass
        </button>
        <button
          onClick={() => onDismiss(messageId, section.text)}
          className="text-sm px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}

/** FAIL indicator for the sidebar — label + note, expandable to the flagged text. */
export function FailFlag({ section }: { section: CompylerSection }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded border border-red-800 bg-red-900/20 px-2 py-1 text-sm text-red-400">
      <button
        onClick={() => setOpen((v) => !v)}
        className="font-mono text-left w-full flex items-center gap-1.5"
      >
        <span>{open ? "▾" : "▸"}</span>
        <span>FAIL{section.note ? ` — ${section.note}` : ""}</span>
      </button>
      {open && (
        <p className="mt-1 whitespace-pre-wrap leading-relaxed text-gray-300">
          {section.text}
        </p>
      )}
    </div>
  );
}

/** Summary line for PASS sections in the sidebar. */
export function PassSummary({ result }: { result: CompylerResult }) {
  const count = result.sections.filter((s) => s.decision === "PASS").length;
  if (!count) return null;
  return (
    <p className="text-sm text-green-600">
      ✓ {count} section{count > 1 ? "s" : ""} passed
    </p>
  );
}
