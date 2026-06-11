/**
 * POST /api/pipeline/execute
 * Stage 2: orchestrator instruction → labor model output.
 */

import { NextRequest } from "next/server";
import { proxyToPipeline } from "@/lib/pipeline-proxy";

export const maxDuration = 120;

export async function POST(req: NextRequest) {
  return proxyToPipeline(req, "/execute");
}
