/**
 * GET /api/logs?sessionId=X&n=10
 * Returns the last N conversation turns for a session (user+assistant pairs).
 * Used to inject prior context into the orchestrator at session start.
 */

import { NextRequest, NextResponse } from "next/server";
import { supabaseServer } from "@/lib/supabase-server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const sessionId = searchParams.get("sessionId");
  const n = Math.min(parseInt(searchParams.get("n") ?? "10", 10), 50);

  if (!sessionId) {
    return NextResponse.json({ turns: [] });
  }

  if (!supabaseServer) {
    return NextResponse.json({ turns: [] });
  }

  try {
    // Find conversations for this session, most recent first.
    const { data: convos, error: convErr } = await supabaseServer
      .from("conversations")
      .select("id")
      .eq("session_id", sessionId)
      .order("created_at", { ascending: false })
      .limit(1);

    if (convErr || !convos?.length) {
      return NextResponse.json({ turns: [] });
    }

    const conversationId = convos[0].id;

    // Fetch the last 2*n messages (n user + n assistant) from this conversation.
    const { data: msgs, error: msgErr } = await supabaseServer
      .from("messages")
      .select("role, content")
      .eq("conversation_id", conversationId)
      .order("created_at", { ascending: false })
      .limit(n * 2);

    if (msgErr || !msgs) {
      return NextResponse.json({ turns: [] });
    }

    // Reverse so oldest-first, then return.
    const turns = msgs.reverse().map((m: { role: string; content: string }) => ({
      role: m.role,
      content: m.content,
    }));

    return NextResponse.json({ turns });
  } catch {
    return NextResponse.json({ turns: [] });
  }
}
