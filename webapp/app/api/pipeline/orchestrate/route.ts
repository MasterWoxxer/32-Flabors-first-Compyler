/**
 * POST /api/pipeline/orchestrate
 * Stage 1: human input → orchestrator instruction.
 */

import { NextRequest } from "next/server";
import { proxyToPipeline } from "@/lib/pipeline-proxy";

export const maxDuration = 120;

export async function POST(req: NextRequest) {
  return proxyToPipeline(req, "/orchestrate");
}
