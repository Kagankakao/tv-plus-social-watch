-- Minimal schema inferred from provided screenshots
-- Safe to run multiple times: uses IF NOT EXISTS

create table if not exists public.users (
  user_id varchar primary key,
  name varchar,
  avatar varchar
);

create table if not exists public.rooms (
  room_id varchar primary key,
  title varchar,
  start_at timestamp,
  host_id varchar references public.users(user_id)
);

create table if not exists public.catalog (
  content_id varchar primary key,
  title varchar,
  type varchar,
  duration_min int4,
  tags text
);

create table if not exists public.expenses (
  expense_id varchar primary key,
  room_id varchar references public.rooms(room_id),
  user_id varchar references public.users(user_id),
  amount numeric,
  note varchar,
  weight numeric
);

create table if not exists public.emojis (
  room_id varchar references public.rooms(room_id),
  user_id varchar references public.users(user_id),
  emoji varchar,
  created_at timestamp default now()
);

create table if not exists public.chat (
  room_id varchar references public.rooms(room_id),
  user_id varchar references public.users(user_id),
  message text,
  created_at timestamp default now()
);

create table if not exists public.candidates (
  room_id varchar references public.rooms(room_id),
  content_id varchar references public.catalog(content_id)
);

create table if not exists public.votes (
  room_id varchar references public.rooms(room_id),
  content_id varchar references public.catalog(content_id),
  user_id varchar references public.users(user_id)
);

create table if not exists public.sync_events (
  room_id varchar references public.rooms(room_id),
  user_id varchar references public.users(user_id),
  action varchar,
  ts timestamp default now(),
  position_sec int4
);
