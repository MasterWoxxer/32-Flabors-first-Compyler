/**
 * POST /api/pipeline/compyle
 * Stage 3: labor output → compyler verdict (labor or voice check).
 */

import { NextRequest } from "next/server";
import { proxyToPipeline } from "@/lib/pipeline-proxy";

export const maxDuration = 120;

export async function POST(req: NextRequest) {
  return proxyToPipeline(req, "/compyle");
}
