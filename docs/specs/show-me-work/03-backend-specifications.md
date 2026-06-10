# Backend Specifications

## 4.1 Supabase Schema

```sql
-- Placeholder schema, refine as requirements stabilize.
create table if not exists conversations (
  id uuid primary key,
  user_id text not null,
  created_at timestamptz not null default now()
);

create table if not exists messages (
  id uuid primary key,
  conversation_id uuid not null references conversations(id),
  role text not null,
  content text not null,
  created_at timestamptz not null default now()
);

create table if not exists compiler_flags (
  id uuid primary key,
  message_id uuid not null references messages(id),
  flag_type text not null,
  detail text,
  created_at timestamptz not null default now()
);

create table if not exists toggle_settings (
  id uuid primary key,
  user_id text not null,
  settings_json jsonb not null,
  updated_at timestamptz not null default now()
);
```

## 4.2 API Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| /api/chat | POST | Send user input and return model response. |
| /api/logs | GET | Fetch user conversation logs. |
| /api/toggles | GET, POST | Get and update toggle settings. |
| /api/admin/activity | GET | Admin view of all user activity. |
