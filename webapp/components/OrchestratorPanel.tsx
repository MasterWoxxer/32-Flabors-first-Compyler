import type { CompylerSection, PipelineProgress, PipelineStage } from "@/lib/types";
import { CheckReviewCard, FailFlag, PassSummary } from "./CompilerFlag";

const STAGE_ORDER = ["orchestrating", "executing", "compyling"] as const;
type RunStage = (typeof STAGE_ORDER)[number];

const STAGE_LABELS: Record<RunStage, string> = {
  orchestrating: "Orchestrator",
  executing: "Labor",
  compyling: "Compyler",
};

type StageStatus = "pending" | "running" | "done";

function stageStatus(stage: RunStage, current: PipelineStage): StageStatus {
  if (current === "done") return "done";
  if (current === "idle" || current === "error") return "pending";
  const order = STAGE_ORDER.indexOf(stage);
  const cur = STAGE_ORDER.indexOf(current as RunStage);
  if (order < cur) return "done";
  if (order === cur) return "running";
  return "pending";
}

function StatusDot({ status }: { status: StageStatus }) {
  if (status === "running") {
    return <span className="inline-block w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />;
  }
  return (
    <span
      className={`inline-block w-2 h-2 rounded-full ${
        status === "done" ? "bg-green-500" : "bg-gray-700"
      }`}
    />
  );
}

interface PendingCheck {
  messageId: string;
  section: CompylerSection;
}

export function OrchestratorPanel({
  progress,
  pendingChecks,
  onPass,
  onDismiss,
}: {
  progress: PipelineProgress;
  pendingChecks: PendingCheck[];
  onPass: (messageId: string, text: string) => void;
  onDismiss: (messageId: string, text: string) => void;
}) {
  const running = progress.stage !== "idle";

  return (
    <div className="p-4 space-y-5">
      <h2 className="text-xs uppercase tracking-widest text-gray-500 font-semibold">
        AI Showing Its Work
      </h2>

      {!running && !pendingChecks.length && (
        <p className="text-xs text-gray-600 italic leading-relaxed">
          Send a message to watch the pipeline unfold here: the orchestrator&apos;s
          task framing, the labor model&apos;s output, and the Compyler&apos;s verdict.
        </p>
      )}

      {/* Pending CHECK review queue — visible whenever checks exist */}
      {pendingChecks.length > 0 && (
        <section className="space-y-2">
          <h3 className="text-xs text-amber-400 font-medium uppercase tracking-wide">
            Flagged for Review
          </h3>
          {pendingChecks.map((c, i) => (
            <CheckReviewCard
              key={i}
              section={c.section}
              messageId={c.messageId}
              onPass={onPass}
              onDismiss={onDismiss}
            />
          ))}
        </section>
      )}

      {running && (
        <>
          {/* Stage tracker */}
          <section className="space-y-1.5">
            {STAGE_ORDER.map((s) => {
              const status = stageStatus(s, progress.stage);
              return (
                <div key={s} className="flex items-center gap-2">
                  <StatusDot status={status} />
                  <span
                    className={`text-xs ${
                      status === "pending" ? "text-gray-600" : "text-gray-300"
                    }`}
                  >
                    {STAGE_LABELS[s]}
                    {status === "running" && "…"}
                  </span>
                </div>
              );
            })}
          </section>

          {/* Orchestrator thinking */}
          {progress.orchestrator_thinking && (
            <section className="space-y-1">
              <h3 className="text-xs text-gray-500">Orchestrator Thinking</h3>
              <p className="text-xs text-gray-500 italic whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                {progress.orchestrator_thinking}
              </p>
            </section>
          )}

          {/* Task instruction */}
          {progress.instruction && (
            <section className="space-y-1">
              <h3 className="text-xs text-gray-500">Task Instruction</h3>
              <p className="text-xs text-gray-300 whitespace-pre-wrap leading-relaxed">
                {progress.instruction}
              </p>
            </section>
          )}

          {/* Labor thinking */}
          {progress.labor_thinking && (
            <section className="space-y-1">
              <h3 className="text-xs text-gray-500">Labor Thinking</h3>
              <p className="text-xs text-gray-500 italic whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                {progress.labor_thinking}
              </p>
            </section>
          )}

          {/* Labor output */}
          {progress.labor_output && (
            <section className="space-y-1">
              <h3 className="text-xs text-gray-500">Labor Output</h3>
              <p className="text-xs text-gray-400 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                {progress.labor_output}
              </p>
            </section>
          )}

          {/* Compyler results — pass summary + fail blocks only (CHECKs go to review queue above) */}
          {(progress.labor_verdict || progress.voice_verdict) && (
            <section className="space-y-2">
              <h3 className="text-xs text-gray-500">Compyler</h3>
              {progress.labor_verdict && (
                <>
                  <PassSummary result={progress.labor_verdict} />
                  {progress.labor_verdict.sections
                    .filter((s) => s.decision === "FAIL")
                    .map((s, i) => <FailFlag key={i} section={s} />)}
                </>
              )}
              {progress.voice_verdict && (
                <>
                  <PassSummary result={progress.voice_verdict} />
                  {progress.voice_verdict.sections
                    .filter((s) => s.decision === "FAIL")
                    .map((s, i) => <FailFlag key={i} section={s} />)}
                </>
              )}
            </section>
          )}

          {progress.stage === "error" && (
            <p className="text-xs text-red-400 leading-relaxed">
              Pipeline error: {progress.error}
            </p>
          )}
        </>
      )}
    </div>
  );
}
