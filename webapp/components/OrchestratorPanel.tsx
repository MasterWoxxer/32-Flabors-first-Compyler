import type { PipelineResult } from "@/lib/types";
import { CompilerFlag } from "./CompilerFlag";

export function OrchestratorPanel({ pipeline }: { pipeline: PipelineResult | null }) {
  return (
    <div className="p-4 space-y-5">
      <h2 className="text-xs uppercase tracking-widest text-gray-500 font-semibold">
        Orchestrator
      </h2>

      {!pipeline && (
        <p className="text-xs text-gray-600 italic leading-relaxed">
          Send a message to see the orchestrator trace and compiler verdicts here.
        </p>
      )}

      {pipeline && (
        <>
          <section className="space-y-1">
            <h3 className="text-xs text-gray-500">Task Instruction</h3>
            <p className="text-xs text-gray-300 whitespace-pre-wrap leading-relaxed">
              {pipeline.orchestrator_instruction}
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="text-xs text-gray-500">Compiler Flags</h3>
            <CompilerFlag verdict={pipeline.compiler.labor_verdict} label="Labor" />
            {pipeline.compiler.voice_verdict && (
              <CompilerFlag verdict={pipeline.compiler.voice_verdict} label="Voice" />
            )}
          </section>
        </>
      )}
    </div>
  );
}
