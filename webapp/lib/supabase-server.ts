/**
 * Server-side Supabase client using the service-role key.
 * Import ONLY from API routes / server components — never client code.
 * Exports null until SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set,
 * so logging degrades gracefully (same pattern as lib/supabase.ts).
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const url = process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL;
const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

export const supabaseServer: SupabaseClient | null =
  url && serviceKey
    ? createClient(url, serviceKey, { auth: { persistSession: false } })
    : null;
