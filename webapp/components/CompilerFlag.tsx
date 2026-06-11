import type { CompilerVerdict } from "@/lib/types";

const VARIANT: Record<string, string> = {
  PASS: "bg-green-900/60 text-green-300 border-green-700",
  FAIL: "bg-red-900/60 text-red-300 border-red-700",
  MCQ: "bg-yellow-900/60 text-yellow-300 border-yellow-700",
  CURRENCY_FAIL: "bg-orange-900/60 text-orange-300 border-orange-700",
  SCOPE_FAIL: "bg-purple-900/60 text-purple-300 border-purple-700",
  VOICE_FAIL: "bg-pink-900/60 text-pink-300 border-pink-700",
  CANDIDATE_FAIL: "bg-blue-900/60 text-blue-300 border-blue-700",
  UNKNOWN: "bg-gray-800 text-gray-400 border-gray-600",
};

export function CompilerFlag({
  verdict,
  label,
}: {
  verdict: CompilerVerdict;
  label?: string;
}) {
  const cls = VARIANT[verdict.verdict] ?? VARIANT.UNKNOWN;
  return (
    <div className={`rounded border px-3 py-2 text-xs font-mono ${cls}`}>
      <div className="font-bold">
        {label && <span className="opacity-50 mr-1">{label}:</span>}
        {verdict.verdict}
      </div>
      {verdict.verdict !== "PASS" && verdict.body && (
        <p className="mt-0.5 opacity-80 break-words leading-snug">{verdict.body}</p>
      )}
    </div>
  );
}
