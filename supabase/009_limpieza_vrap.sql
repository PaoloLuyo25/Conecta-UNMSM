-- Conecta UNMSM: retirar la ficha genérica VRAP; conservar únicamente
-- la guía de investigación formativa respaldada por una fuente oficial.
-- Ejecutar en Supabase SQL Editor; no toca Auth ni route_history.
BEGIN;
DELETE FROM public.services
WHERE id = 'CENTRAL-VRAP-PREGRADO';
COMMIT;
SELECT id, name, source_url FROM public.services WHERE id LIKE 'CENTRAL-VRAP-%';
