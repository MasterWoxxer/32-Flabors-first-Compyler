import type { CompylerResult, CompylerSection } from "@/lib/types";

/**
 * Renders the assistant message in chat.
 * PASS sections: verbatim, clean.
 * FAIL sections: blocked inline with a flag.
 * CHECK sections: not shown here — they live in the sidebar review queue.
 * Approved sections (user passed from review): shown with a subtle indigo border.
 */
export function CompylerMessage({
  result,
  approvedTexts = [],
  hasPendingChecks = false,
}: {
  result: CompylerResult;
  approvedTexts?: string[];
  hasPendingChecks?: boolean;
}) {
  const passSections = result.sections.filter((s) => s.decision === "PASS");
  const failSections = result.sections.filter((s) => s.decision === "FAIL");
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
        <div
          key={i}
          className="rounded border border-red-700 bg-red-900/30 px-3 py-1.5 text-xs text-red-300 font-mono"
        >
          [Compyler blocked{s.note ? `: ${s.note}` : ""}]
        </div>
      ))}

      {approvedTexts.map((text, i) => (
        <div key={i} className="border-l-2 border-indigo-500 pl-3">
          <p className="whitespace-pre-wrap leading-relaxed text-sm text-gray-100">{text}</p>
          <span className="text-xs text-indigo-400 mt-0.5 block">passed from review</span>
        </div>
      ))}
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
        <span className="text-xs font-mono font-bold text-amber-300">CHECK</span>
        {section.note && (
          <span className="text-xs text-amber-400 opacity-70">— {section.note}</span>
        )}
      </div>
      <p className="text-xs text-gray-300 whitespace-pre-wrap leading-relaxed">
        {section.text}
      </p>
      <div className="flex gap-2 pt-1">
        <button
          onClick={() => onPass(messageId, section.text)}
          className="text-xs px-3 py-1 rounded bg-indigo-700 hover:bg-indigo-600 text-white transition-colors"
        >
          Pass
        </button>
        <button
          onClick={() => onDismiss(messageId, section.text)}
          className="text-xs px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}

/** Brief FAIL indicator for the sidebar — just label + note, no full text. */
export function FailFlag({ section }: { section: CompylerSection }) {
  return (
    <div className="rounded border border-red-800 bg-red-900/20 px-2 py-1 text-xs text-red-400 font-mono">
      FAIL{section.note ? ` — ${section.note}` : ""}
    </div>
  );
}

/** Summary line for PASS sections in the sidebar. */
export function PassSummary({ result }: { result: CompylerResult }) {
  const count = result.sections.filter((s) => s.decision === "PASS").length;
  if (!count) return null;
  return (
    <p className="text-xs text-green-600">
      ✓ {count} section{count > 1 ? "s" : ""} passed
    </p>
  );
}
