/**
 * Server-side helper shared by the staged pipeline proxy routes.
 * Validates the tester access code, then forwards the request to the
 * Python pipeline service (local uvicorn in dev, /api/py/* on Vercel).
 */

import { NextRequest, NextResponse } from "next/server";

const PYTHON_BASE =
  process.env.PYTHON_SERVICE_URL ??
  (process.env.VERCEL_URL
    ? `https://${process.env.VERCEL_URL}/api/py`
    : "http://localhost:8000");

/** Returns a 401 response if the access code is missing/wrong, else null. */
export function rejectUnlessAuthorized(req: NextRequest): NextResponse | null {
  const required = process.env.ACCESS_CODE;
  if (!required) return null; // no code configured (local dev) — open
  if (req.headers.get("x-access-code") === required) return null;
  return NextResponse.json({ detail: "invalid access code" }, { status: 401 });
}

/** Proxy the JSON body of `req` to the given Python service path. */
export async function proxyToPipeline(
  req: NextRequest,
  path: string,
): Promise<NextResponse> {
  const denied = rejectUnlessAuthorized(req);
  if (denied) return denied;

  const body = await req.json().catch(() => null);
  if (!body?.message?.trim()) {
    return NextResponse.json(
      { detail: "message is required and must not be empty" },
      { status: 422 },
    );
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  // Lets the Python function (publicly reachable on Vercel) reject requests
  // that didn't come through these proxy routes.
  const secret = process.env.PIPELINE_INTERNAL_SECRET;
  if (secret) headers["x-internal-secret"] = secret;

  let upstream: Response;
  try {
    upstream = await fetch(`${PYTHON_BASE}${path}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  } catch (err) {
    return NextResponse.json(
      { detail: `Could not reach pipeline service: ${String(err)}` },
      { status: 502 },
    );
  }

  const data = await upstream
    .json()
    .catch(() => ({ detail: "invalid upstream response" }));
  return NextResponse.json(data, { status: upstream.status });
}
