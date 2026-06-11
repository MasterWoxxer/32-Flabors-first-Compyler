/**
 * Supabase browser client.
 * Requires NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to be set.
 * Until those are configured, this module exports null and callers should degrade gracefully.
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Export null when env vars are absent so callers can skip persistence gracefully.
export const supabase: SupabaseClient | null =
  url && anonKey ? createClient(url, anonKey) : null;
