/**
 * POST /api/pipeline
 * Proxies the chat request to the Python FastAPI service and returns the result.
 */

import { NextRequest, NextResponse } from "next/server";

const PYTHON_SERVICE_URL =
  process.env.PYTHON_SERVICE_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);

  if (!body?.message?.trim()) {
    return NextResponse.json(
      { detail: "message is required and must not be empty" },
      { status: 422 },
    );
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${PYTHON_SERVICE_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: body.message,
        settings: body.settings ?? {},
      }),
    });
  } catch (err) {
    return NextResponse.json(
      { detail: `Could not reach pipeline service: ${String(err)}` },
      { status: 502 },
    );
  }

  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}
