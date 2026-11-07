-- MIGRACIÓN LABORATORIO 004: ampliar categorías, NO recrear tabla ni alterar Auth/RLS.
-- Requiere public.services creado con 001_services.sql.
BEGIN;
ALTER TABLE public.services DROP CONSTRAINT IF EXISTS services_category_code_check;
ALTER TABLE public.services ADD CONSTRAINT services_category_code_check
 CHECK (category_code IN ('bienestar','unayoe','clinica_general','salud_mental',
  'transporte_externo','becas','movilidad_academica'));
COMMIT;
