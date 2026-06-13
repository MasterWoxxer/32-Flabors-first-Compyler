/**
 * POST /api/log
 * Persists one completed pipeline run to Supabase (research logging).
 * Called by the UI after the compyle stage finishes — the voice verdict comes
 * from a second compyle call, so only the client sees the complete run.
 * No-ops with { ok: false } when Supabase env vars are not configured.
 */

import { NextRequest, NextResponse } from "next/server";
import { rejectUnlessAuthorized } from "@/lib/pipeline-proxy";
import { supabaseServer } from "@/lib/supabase-server";
import type { PipelineResult, ToggleSettings } from "@/lib/types";

interface LogPayload {
  sessionId: string;
  conversationId?: string | null;
  message: string;
  result: PipelineResult;
  settings: ToggleSettings;
}

export async function POST(req: NextRequest) {
  const denied = rejectUnlessAuthorized(req);
  if (denied) return denied;

  const payload = (await req.json().catch(() => null)) as LogPayload | null;
  if (!payload?.sessionId || !payload.message || !payload.result) {
    return NextResponse.json({ detail: "invalid log payload" }, { status: 422 });
  }

  if (!supabaseServer) {
    return NextResponse.json({ ok: false, note: "Supabase not configured" });
  }

  try {
    // Conversation: reuse the id from earlier runs in this thread, else create.
    let conversationId = payload.conversationId ?? null;
    if (!conversationId) {
      const { data, error } = await supabaseServer
        .from("conversations")
        .insert({ session_id: payload.sessionId })
        .select("id")
        .single();
      if (error) throw error;
      conversationId = data.id;
    }

    const { result, settings } = payload;

    const { error: userErr } = await supabaseServer.from("messages").insert({
      conversation_id: conversationId,
      role: "user",
      content: payload.message,
      settings_json: settings,
    });
    if (userErr) throw userErr;

    const { data: assistantRow, error: asstErr } = await supabaseServer
      .from("messages")
      .insert({
        conversation_id: conversationId,
        role: "assistant",
        content: result.direct_response ?? result.labor_output,
        orchestrator_instruction: result.orchestrator_instruction,
        orchestrator_thinking: result.orchestrator_thinking,
        labor_output: result.labor_output,
        labor_thinking: result.labor_thinking,
        direct_response: result.direct_response,
        settings_json: settings,
      })
      .select("id")
      .single();
    if (asstErr) throw asstErr;

    // Log one row per compyler section (labor + voice).
    const flags = [
      ...result.compiler.labor_verdict.sections.map((s) => ({
        message_id: assistantRow.id,
        flag_type: s.decision,
        check_kind: "labor",
        detail: s.note ? `${s.note} | ${s.text.slice(0, 200)}` : s.text.slice(0, 200),
      })),
      ...(result.compiler.voice_verdict
        ? result.compiler.voice_verdict.sections.map((s) => ({
            message_id: assistantRow.id,
            flag_type: s.decision,
            check_kind: "voice",
            detail: s.note ? `${s.note} | ${s.text.slice(0, 200)}` : s.text.slice(0, 200),
          }))
        : []),
    ];
    if (flags.length > 0) {
      const { error: flagErr } = await supabaseServer
        .from("compiler_flags")
        .insert(flags);
      if (flagErr) throw flagErr;
    }

    const { error: toggleErr } = await supabaseServer
      .from("toggle_settings")
      .upsert(
        { session_id: payload.sessionId, settings_json: settings, updated_at: new Date().toISOString() },
        { onConflict: "session_id" },
      );
    if (toggleErr) throw toggleErr;

    return NextResponse.json({ ok: true, conversationId });
  } catch (err) {
    // Logging must never break the user-facing flow.
    return NextResponse.json(
      { ok: false, detail: String(err) },
      { status: 200 },
    );
  }
}
