import type { CompylerResult, CompylerSection, SectionDecision } from "@/lib/types";

const DECISION_STYLES: Record<SectionDecision, string> = {
  PASS: "bg-green-900/40 text-green-300 border-green-700",
  CHECK: "bg-amber-900/40 text-amber-300 border-amber-700",
  FAIL: "bg-red-900/40 text-red-300 border-red-700",
};

/** Single section badge — used in the sidebar section list. */
export function SectionBadge({ section }: { section: CompylerSection }) {
  const cls = DECISION_STYLES[section.decision] ?? DECISION_STYLES.CHECK;
  return (
    <div className={`rounded border px-2 py-1 text-xs font-mono ${cls}`}>
      <span className="font-bold">{section.decision}</span>
      {section.note && (
        <span className="opacity-70 ml-1">— {section.note}</span>
      )}
      <p className="mt-0.5 text-xs opacity-60 leading-snug line-clamp-2 font-sans">
        {section.text}
      </p>
    </div>
  );
}

/** Full section list — used in the sidebar to show all compyler decisions. */
export function CompylerResultPanel({
  result,
  label,
}: {
  result: CompylerResult;
  label?: string;
}) {
  return (
    <div className="space-y-1">
      {label && <p className="text-xs text-gray-600 font-medium">{label}</p>}
      {result.sections.map((s, i) => (
        <SectionBadge key={i} section={s} />
      ))}
    </div>
  );
}

/**
 * Reconstructed message body for the chat panel.
 * PASS → verbatim. CHECK → verbatim with amber left border.
 * FAIL → blocked placeholder (text never shown to user).
 */
export function CompylerMessage({ result }: { result: CompylerResult }) {
  return (
    <div className="space-y-2">
      {result.sections.map((s, i) => {
        if (s.decision === "FAIL") {
          return (
            <div
              key={i}
              className="rounded border border-red-700 bg-red-900/30 px-3 py-1.5 text-xs text-red-300 font-mono"
            >
              [Compyler blocked{s.note ? `: ${s.note}` : ""}]
            </div>
          );
        }
        return (
          <div
            key={i}
            className={
              s.decision === "CHECK"
                ? "border-l-2 border-amber-500 pl-3"
                : undefined
            }
          >
            <p className="whitespace-pre-wrap leading-relaxed text-sm">{s.text}</p>
            {s.decision === "CHECK" && s.note && (
              <span className="text-xs text-amber-500 mt-0.5 block">{s.note}</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
