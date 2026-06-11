-- 32 Flavors / Show Me Work — research logging schema.
-- Derived from docs/specs/show-me-work/03-backend-specifications.md, adjusted:
--   * gen_random_uuid() defaults
--   * session_id (anonymous browser session) instead of user_id — swaps to a
--     real user_id when Supabase Auth lands (see auth roadmap)
--   * stage outputs + toggle snapshot stored on assistant message rows
-- Apply in the Supabase SQL editor.

create extension if not exists pgcrypto;

create table if not exists conversations (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  created_at timestamptz not null default now()
);
create index if not exists conversations_session_idx on conversations (session_id);

create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations (id),
  role text not null, -- 'user' | 'assistant'
  content text not null,
  orchestrator_instruction text, -- assistant rows: stage-1 output
  orchestrator_thinking text,    -- assistant rows: orchestrator reasoning trace
  labor_output text,             -- assistant rows: stage-2 output
  labor_thinking text,           -- assistant rows: labor model's thinking trace
  direct_response text,          -- assistant rows: [DIRECT RESPONSE TO HUMAN]
  settings_json jsonb,           -- toggle snapshot incl. session instructions
  created_at timestamptz not null default now()
);
create index if not exists messages_conversation_idx on messages (conversation_id);

create table if not exists compiler_flags (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references messages (id),
  flag_type text not null,                  -- verdict: PASS | FAIL | MCQ | ...
  check_kind text not null default 'labor', -- 'labor' | 'voice'
  detail text,
  created_at timestamptz not null default now()
);
create index if not exists compiler_flags_message_idx on compiler_flags (message_id);

create table if not exists toggle_settings (
  id uuid primary key default gen_random_uuid(),
  session_id text not null unique,
  settings_json jsonb not null,
  updated_at timestamptz not null default now()
);

-- Writes go through the service-role key (server-side only). Enabling RLS
-- with no policies locks the public anon key out entirely.
alter table conversations enable row level security;
alter table messages enable row level security;
alter table compiler_flags enable row level security;
alter table toggle_settings enable row level security;
