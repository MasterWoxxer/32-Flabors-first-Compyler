/**
 * GET  /api/toggles  — Return persisted toggle settings for the current user.
 * POST /api/toggles  — Upsert toggle settings.
 *
 * TODO: Wire to Supabase toggle_settings table keyed by user_id.
 * For MVP, canonical state lives in localStorage on the client; this route
 * validates and acknowledges the payload.
 */

import { NextRequest, NextResponse } from "next/server";
import type { ToggleSettings } from "@/lib/types";

export async function GET() {
  // TODO: query Supabase toggle_settings by user_id from session.
  return NextResponse.json(null); // client falls back to localStorage
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  const settings = body as ToggleSettings | null;

  if (!settings?.model) {
    return NextResponse.json({ detail: "invalid settings payload" }, { status: 422 });
  }

  // TODO: upsert to Supabase toggle_settings table.
  return NextResponse.json({ ok: true });
}
