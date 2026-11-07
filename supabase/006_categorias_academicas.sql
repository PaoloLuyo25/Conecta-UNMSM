-- Conecta UNMSM - Migración aditiva; no recrea tabla services ni altera RLS.
-- Ejecutar una vez luego de 001_services.sql. Compatible con ampliación 004 opcional.
BEGIN;
ALTER TABLE public.services DROP CONSTRAINT IF EXISTS services_category_code_check;
ALTER TABLE public.services ADD CONSTRAINT services_category_code_check
  CHECK (category_code IN ('bienestar','unayoe','clinica_general','salud_mental',
    'transporte_externo','becas','movilidad_academica','oportunidades_academicas'));
COMMIT;
