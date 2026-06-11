/**
 * TEMPORARY diagnostic — reports only the shape of env vars (set, length,
 * first 2 chars), never values. DELETE THIS FILE once env vars are fixed.
 */

import { NextResponse } from "next/server";

const VARS = [
  "MISTRAL_API_KEY",
  "ANTHROPIC_API_KEY",
  "ACCESS_CODE",
  "PIPELINE_INTERNAL_SECRET",
  "SUPABASE_URL",
  "SUPABASE_SERVICE_ROLE_KEY",
];

export async function GET() {
  const report = Object.fromEntries(
    VARS.map((name) => {
      const v = process.env[name];
      return [
        name,
        v
          ? { set: true, length: v.length, startsWith: v.slice(0, 2) }
          : { set: false },
      ];
    }),
  );
  return NextResponse.json(report);
}
