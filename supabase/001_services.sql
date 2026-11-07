-- CONECTA UNMSM · LABORATORIO SDD (no es una base institucional oficial).
-- Ejecutar UNA VEZ en Supabase > SQL Editor de un proyecto de laboratorio.
-- Tabla pública de lectura únicamente. NO guardar datos personales.
create table if not exists public.services (
    id text primary key,
    name text not null check (length(btrim(name)) > 0),
    faculty_code text not null check (faculty_code ~ '^[A-Z][A-Z0-9_]*$'),
    accessible_to_all_faculties boolean not null default false,
    category_code text not null check (category_code in (
        'bienestar','unayoe','clinica_general','salud_mental','transporte_externo')),
    description text not null check (length(btrim(description)) > 0),
    needs_tags jsonb not null default '[]'::jsonb check (jsonb_typeof(needs_tags) = 'array'),
    audience text,
    modality jsonb not null default '[]'::jsonb check (jsonb_typeof(modality) = 'array'),
    requirements jsonb not null default '[]'::jsonb check (jsonb_typeof(requirements) = 'array'),
    official_steps jsonb not null default '[]'::jsonb check (jsonb_typeof(official_steps) = 'array'),
    contact jsonb,
    location text,
    hours text,
    route_region text check (route_region in ('norte','sur','centro','este')),
    stops jsonb not null default '[]'::jsonb check (jsonb_typeof(stops) = 'array'),
    source_url text,
    evidence_type text not null check (evidence_type in (
        'web_oficial','documento_oficial','informacion_directa','prueba_ficticia')),
    source_published_at date,
    verified_at date,
    valid_from date,
    valid_until date,
    availability_status text not null check (availability_status in (
        'confirmado_documentalmente','vigencia_por_confirmar',
        'cerrado_documentado','datos_insuficientes')),
    warnings jsonb not null default '[]'::jsonb check (jsonb_typeof(warnings) = 'array'),
    is_public boolean not null default false,
    constraint valid_service_period check (valid_from is null or valid_until is null or valid_from <= valid_until),
    constraint universal_scope_is_central check (not accessible_to_all_faculties or faculty_code = 'CENTRAL'),
    constraint transport_only_zone check (category_code = 'transporte_externo' or (route_region is null and stops = '[]'::jsonb))
);

-- Si se creó la tabla anteriormente, revisar manualmente su esquema antes de ejecutar seed.
-- No usar service_role para las consultas habituales del backend.
alter table public.services enable row level security;
alter table public.services force row level security;
revoke all on public.services from public, anon, authenticated;
grant usage on schema public to anon, authenticated;
-- Únicamente las columnas del contrato del servicio; `is_public` no se expone.
grant select (
 id, name, faculty_code, accessible_to_all_faculties, category_code,
 description, needs_tags, audience, modality, requirements, official_steps,
 contact, location, hours, route_region, stops, source_url, evidence_type,
 source_published_at, verified_at, valid_from, valid_until,
 availability_status, warnings
) on public.services to anon, authenticated;

drop policy if exists service_catalog_public_read on public.services;
create policy service_catalog_public_read on public.services
    for select to anon, authenticated using (is_public = true);
-- No crear políticas INSERT, UPDATE ni DELETE para anon/authenticated.
-- El SQL Editor, usando permisos de administrador del proyecto, puede cargar los datos.
