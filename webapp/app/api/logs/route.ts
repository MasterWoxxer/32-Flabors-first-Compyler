/**
 * GET /api/logs
 * Returns conversation history.
 * TODO: Wire to Supabase — query conversations + messages tables by user_id.
 * For MVP, conversation history is managed client-side.
 */

import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    logs: [],
    note: "Supabase integration pending — history is managed client-side for now.",
  });
}
