-- LABORATORIO SDD. Ejecutar solo en Supabase de prueba tras aprobar Auth/retención.
-- No incorpora consultas, correos, distritos ni información clínica.
create table if not exists public.route_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  service_ids text[] not null,
  faculty_code text not null check (faculty_code ~ '^[A-Z][A-Z0-9_]*$'),
  catalog_source text not null check (catalog_source in ('primary', 'local_snapshot')),
  client_request_id uuid not null,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default (now() + interval '30 days'),
  constraint route_history_service_count check (cardinality(service_ids) between 1 and 3),
  constraint route_history_unique_request unique (user_id, client_request_id)
);
create index if not exists route_history_owner_created_idx
  on public.route_history (user_id, created_at desc);
create index if not exists route_history_expiry_idx on public.route_history (expires_at);
alter table public.route_history enable row level security;
revoke all on public.route_history from public, anon, authenticated;
grant select, insert, delete on public.route_history to authenticated;
drop policy if exists route_history_select_own on public.route_history;
create policy route_history_select_own on public.route_history
  for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists route_history_insert_own on public.route_history;
create policy route_history_insert_own on public.route_history
  for insert to authenticated with check ((select auth.uid()) = user_id);
drop policy if exists route_history_delete_own on public.route_history;
create policy route_history_delete_own on public.route_history
  for delete to authenticated using ((select auth.uid()) = user_id);
-- RLS impide acceso a datos ajenos; probar con dos JWT reales antes de activarlo.
-- El filtro expires_at > now() no borra físicamente las filas; planificar purga.
