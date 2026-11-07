-- SOLO PARA UN PROYECTO SUPABASE DE PRUEBAS, NUNCA PARA UN CATÁLOGO OFICIAL.
-- Todos los servicios de este archivo son FICTICIOS; solo habilitar ALLOW_DEMO_RECORDS=true en laboratorio.
-- Ejecutar DESPUÉS de 001_services.sql. No usar en la instancia de competición.
WITH synthetic AS (
    SELECT jsonb_array_elements($conecta_lab$[
  {
    "id": "DEMO-ORI-PRESENCIAL",
    "name": "Orientación presencial (SERVICIO FICTICIO)",
    "faculty_code": "FISI",
    "category_code": "unayoe",
    "description": "Ficha sintética para mostrar la selección de orientación presencial.",
    "needs_tags": [
      "orientacion"
    ],
    "modality": [
      "presencial"
    ],
    "requirements": [],
    "official_steps": [
      "Paso de demostración: consultar un canal que deberá verificarse con una fuente oficial."
    ],
    "evidence_type": "prueba_ficticia",
    "availability_status": "vigencia_por_confirmar",
    "warnings": [
      "Ejemplo de laboratorio; no atribuir a ninguna oficina real."
    ],
    "accessible_to_all_faculties": false,
    "is_public": true
  },
  {
    "id": "DEMO-ORI-VIRTUAL",
    "name": "Orientación virtual (SERVICIO FICTICIO)",
    "faculty_code": "FISI",
    "category_code": "unayoe",
    "description": "Ficha sintética para demostrar cómo una preferencia cambia la elección.",
    "needs_tags": [
      "orientacion"
    ],
    "modality": [
      "virtual"
    ],
    "requirements": [],
    "official_steps": [
      "Paso de demostración: solicitar orientación usando un medio documentado, si existe."
    ],
    "evidence_type": "prueba_ficticia",
    "availability_status": "vigencia_por_confirmar",
    "accessible_to_all_faculties": false,
    "is_public": true
  },
  {
    "id": "DEMO-BIENESTAR",
    "name": "Información de bienestar (SERVICIO FICTICIO)",
    "faculty_code": "FISI",
    "category_code": "bienestar",
    "description": "Registro sintético para ensayar consultas sobre apoyos económicos y alimentación.",
    "needs_tags": [
      "bienestar"
    ],
    "evidence_type": "prueba_ficticia",
    "availability_status": "vigencia_por_confirmar",
    "accessible_to_all_faculties": false,
    "is_public": true
  },
  {
    "id": "DEMO-CLINICA",
    "name": "Información de atención general (SERVICIO FICTICIO)",
    "faculty_code": "CENTRAL",
    "category_code": "clinica_general",
    "description": "Registro sintético central de orientación administrativa sobre atención general.",
    "needs_tags": [
      "atencion_general"
    ],
    "evidence_type": "prueba_ficticia",
    "availability_status": "vigencia_por_confirmar",
    "accessible_to_all_faculties": false,
    "is_public": true
  },
  {
    "id": "DEMO-EMOCIONAL",
    "name": "Información sobre apoyo emocional (SERVICIO FICTICIO)",
    "faculty_code": "CENTRAL",
    "category_code": "salud_mental",
    "description": "Ficha ficticia de orientación informativa; no diagnostica ni ofrece atención real.",
    "needs_tags": [
      "orientacion_salud_mental"
    ],
    "evidence_type": "prueba_ficticia",
    "availability_status": "datos_insuficientes",
    "accessible_to_all_faculties": false,
    "is_public": true
  },
  {
    "id": "DEMO-TRANSPORTE-NORTE",
    "name": "Información de transporte norte (SERVICIO FICTICIO)",
    "faculty_code": "CENTRAL",
    "category_code": "transporte_externo",
    "description": "Ficha sintética sobre una zona de transporte, sin paradas, tarifas ni horarios.",
    "needs_tags": [
      "transporte"
    ],
    "route_region": "norte",
    "evidence_type": "prueba_ficticia",
    "availability_status": "datos_insuficientes",
    "accessible_to_all_faculties": true,
    "is_public": true
  },
  {
    "id": "DEMO-OTRA-FACULTAD",
    "name": "Registro excluido (SERVICIO FICTICIO)",
    "faculty_code": "OTRA_FACULTAD",
    "category_code": "bienestar",
    "description": "Debe quedar fuera de todos los resultados del piloto FISI.",
    "needs_tags": [
      "bienestar"
    ],
    "evidence_type": "prueba_ficticia",
    "availability_status": "vigencia_por_confirmar",
    "accessible_to_all_faculties": false,
    "is_public": true
  },
  {
    "id": "DEMO-TRANSPORTE-SUR",
    "name": "Información transporte sur (SERVICIO FICTICIO)",
    "faculty_code": "CENTRAL",
    "accessible_to_all_faculties": true,
    "category_code": "transporte_externo",
    "description": "Registro de ensayo para clasificación por zona sur; no afirma rutas, horarios ni paradas reales.",
    "needs_tags": [
      "transporte"
    ],
    "route_region": "sur",
    "evidence_type": "prueba_ficticia",
    "availability_status": "datos_insuficientes",
    "is_public": true
  },
  {
    "id": "DEMO-TRANSPORTE-CENTRO",
    "name": "Información transporte centro (SERVICIO FICTICIO)",
    "faculty_code": "CENTRAL",
    "accessible_to_all_faculties": true,
    "category_code": "transporte_externo",
    "description": "Registro de ensayo para clasificación por zona centro; no afirma rutas, horarios ni paradas reales.",
    "needs_tags": [
      "transporte"
    ],
    "route_region": "centro",
    "evidence_type": "prueba_ficticia",
    "availability_status": "datos_insuficientes",
    "is_public": true
  },
  {
    "id": "DEMO-TRANSPORTE-ESTE",
    "name": "Información transporte este (SERVICIO FICTICIO)",
    "faculty_code": "CENTRAL",
    "accessible_to_all_faculties": true,
    "category_code": "transporte_externo",
    "description": "Registro de ensayo para clasificación por zona este; no afirma rutas, horarios ni paradas reales.",
    "needs_tags": [
      "transporte"
    ],
    "route_region": "este",
    "evidence_type": "prueba_ficticia",
    "availability_status": "datos_insuficientes",
    "is_public": true
  }
]$conecta_lab$::jsonb) AS entry
)
INSERT INTO public.services (
  id, name, faculty_code, accessible_to_all_faculties, category_code,
  description, needs_tags, audience, modality, requirements, official_steps,
  contact, location, hours, route_region, stops, source_url, evidence_type,
  source_published_at, verified_at, valid_from, valid_until,
  availability_status, warnings, is_public
)
SELECT
  entry->>'id', entry->>'name', entry->>'faculty_code',
  COALESCE((entry->>'accessible_to_all_faculties')::boolean,false),
  entry->>'category_code', entry->>'description', COALESCE(entry->'needs_tags','[]'::jsonb),
  entry->>'audience', COALESCE(entry->'modality','[]'::jsonb),
  COALESCE(entry->'requirements','[]'::jsonb), COALESCE(entry->'official_steps','[]'::jsonb),
  entry->'contact', entry->>'location', entry->>'hours', entry->>'route_region',
  COALESCE(entry->'stops','[]'::jsonb), entry->>'source_url', entry->>'evidence_type',
  NULLIF(entry->>'source_published_at','')::date,
  NULLIF(entry->>'verified_at','')::date,
  NULLIF(entry->>'valid_from','')::date, NULLIF(entry->>'valid_until','')::date,
  entry->>'availability_status', COALESCE(entry->'warnings','[]'::jsonb), true
FROM synthetic
ON CONFLICT (id) DO NOTHING;
