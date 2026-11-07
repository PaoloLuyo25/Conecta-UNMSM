-- MIGRACIÓN LABORATORIO 005 · 20 facultades x 7 escenarios = 140 registros FICTICIOS.
-- NO son convocatorias, becas, oficinas ni trámites reales de la UNMSM.
-- Ejecutar después de 004; idempotente por id. Solo pruebas en proyecto LAB.
WITH faculties(code, faculty_name) AS (VALUES
  ('LETRAS','Letras y Ciencias Humanas'),
  ('DERECHO','Derecho y Ciencia Política'),
  ('MEDICINA','Medicina'),
  ('MATEMATICAS','Ciencias Matemáticas'),
  ('BIOLOGICAS','Ciencias Biológicas'),
  ('ECONOMICAS','Ciencias Económicas'),
  ('FARMACIA','Farmacia y Bioquímica'),
  ('ODONTOLOGIA','Odontología'),
  ('EDUCACION','Educación'),
  ('VETERINARIA','Medicina Veterinaria'),
  ('QUIMICA','Química e Ingeniería Química'),
  ('ADMINISTRATIVAS','Ciencias Administrativas'),
  ('CONTABLES','Ciencias Contables'),
  ('FISICAS','Ciencias Físicas'),
  ('SOCIALES','Ciencias Sociales'),
  ('ING_GEOLOGICA','Ingeniería Geológica, Minera, Metalúrgica y Geográfica'),
  ('INDUSTRIAL','Ingeniería Industrial'),
  ('ELECTRONICA','Ingeniería Electrónica y Eléctrica'),
  ('PSICOLOGIA','Psicología'),
  ('FISI','Ingeniería de Sistemas e Informática')
),
programs(suffix, title, category, audience_level, tags) AS (VALUES
  ('ORIENTACION','Orientación universitaria de ejemplo','bienestar','todos','orientacion,bienestar,adaptacion'),
  ('BECA_PRE','Convocatoria de beca de pregrado de ejemplo','becas','pregrado','becas,pregrado,apoyo_economico'),
  ('BECA_POS','Convocatoria de beca de posgrado de ejemplo','becas','posgrado','becas,posgrado,investigacion'),
  ('BECA_DOC','Convocatoria de apoyo docente de ejemplo','becas','docentes','becas,docentes,investigacion'),
  ('MOV_PRE','Movilidad académica de pregrado de ejemplo','movilidad_academica','pregrado','movilidad_academica,viajar,intercambio,pregrado'),
  ('MOV_POS','Movilidad académica de posgrado de ejemplo','movilidad_academica','posgrado','movilidad_academica,viajar,intercambio,posgrado'),
  ('MOV_DOC','Estancia académica docente de ejemplo','movilidad_academica','docentes','movilidad_academica,viajar,intercambio,docentes')
)
INSERT INTO public.services (
 id, name, faculty_code, accessible_to_all_faculties, category_code,
 description, needs_tags, audience, evidence_type, availability_status,
 official_steps, requirements, modality, warnings, is_public
)
SELECT
 'DEMO-MF-' || f.code || '-' || p.suffix,
 p.title || ' — ' || f.faculty_name || ' [FICTICIO]',
 f.code, false, p.category,
 'Escenario simulado para demostrar orientación por facultad y público; no existe convocatoria ni proceso acreditado.',
 to_jsonb(string_to_array(p.tags, ',')), p.audience_level,
 'prueba_ficticia', 'datos_insuficientes',
 '[]'::jsonb, '[]'::jsonb, '[]'::jsonb,
 jsonb_build_array('DEMO únicamente: no presentar como beca, viaje, convocatoria o servicio vigente.'),
 true
FROM faculties f CROSS JOIN programs p
ON CONFLICT (id) DO UPDATE SET
 name=EXCLUDED.name, faculty_code=EXCLUDED.faculty_code,
 accessible_to_all_faculties=false, category_code=EXCLUDED.category_code,
 description=EXCLUDED.description, needs_tags=EXCLUDED.needs_tags,
 audience=EXCLUDED.audience, evidence_type='prueba_ficticia',
 availability_status='datos_insuficientes', official_steps='[]'::jsonb,
 requirements='[]'::jsonb, modality='[]'::jsonb,
 contact=NULL, location=NULL, hours=NULL, source_url=NULL,
 verified_at=NULL, source_published_at=NULL, valid_from=NULL, valid_until=NULL,
 warnings=EXCLUDED.warnings, is_public=true;

-- Verificar existencia; esto no prueba las políticas RLS del cliente anónimo.
SELECT faculty_code, count(*) AS servicios_ficticios
FROM public.services WHERE id LIKE 'DEMO-MF-%'
GROUP BY faculty_code ORDER BY faculty_code;
