/**
 * POST /api/pipeline
 * Legacy one-shot run (all stages in a single request). The UI uses the
 * staged routes (orchestrate / execute / compyle); this remains for
 * debugging and scripted use.
 */

import { NextRequest } from "next/server";
import { proxyToPipeline } from "@/lib/pipeline-proxy";

export const maxDuration = 300;

export async function POST(req: NextRequest) {
  return proxyToPipeline(req, "/run");
}
