# Contrato de datos y procedencia — Conecta UNMSM

## Catalogación
Modelo `Service` en `backend/app/schemas.py`. Entidad base: `id`, `name`, `faculty_code` (`CENTRAL` o una facultad), `accessible_to_all_faculties`, `category_code`, `description`, `needs_tags[]`, `audience`, `modality[]`, `requirements[]`, `official_steps[]`, `contact`, `location`, `hours`, `route_region`, `stops[]`, `source_url`, `evidence_type`, `source_published_at`, `verified_at`, `valid_from`, `valid_until`, `availability_status`, `warnings[]`.

Categorías admitidas: `bienestar`, `unayoe`, `clinica_general`, `salud_mental`, `transporte_externo`, `becas`, `movilidad_academica`, `oportunidades_academicas`.

- `audience`: texto opcional; para filtrado seguro se admiten códigos exactos `pregrado`, `posgrado`, `docentes`, o una lista de estos separados por coma. Si contiene un texto descriptivo libre, el backend **no** debe inferir una elegibilidad exclusiva.
- `evidence_type`: `web_oficial`, `documento_oficial`, `informacion_directa`, `prueba_ficticia`. En modo normal se excluye el último.
- `availability_status`: `confirmado_documentalmente`, `vigencia_por_confirmar`, `cerrado_documentado`, `datos_insuficientes`. Revisar **cada** convocatoria; no deducir apertura por existencia del anuncio.
- `verified_at`: fecha en que se revisó la publicación. **No** es una garantía de que el programa esté abierto.
- `faculty_code=CENTRAL` + `accessible_to_all_faculties=true`: publicación de alcance general, siempre con requisitos individuales. Para otras facultades, jamás tomar un registro FISI/Medicina como universal por analogía.
- `source_url`: publicación accesible; sin URL pública, evidencia directa identificada con advertencia.

## Flujo de actualización
`tools/explorar_fuentes.py` -> `data/discovered.pending.json` -> revisión humana y fuente original -> `data/catalog.academico.json` -> `tools/generar_sql_catalogo.py` -> SQL Editor administrador (transacción). No hay publicación automática. Es obligatorio comprobar plazos, variantes por universidad y si convenio implica o no financiación.

## SQL y respaldo
El contrato PostgreSQL existente está en `supabase/001_services.sql`. La ampliación nueva se ejecuta desde `supabase/EJECUTAR_CATALOGO_ACADEMICO.sql`, que **no** recrea ni reemplaza el catálogo: añade categoría informativa e inserta/actualiza registros aprobados. El respaldo local `data/catalog.academico.json` es una copia de lectura susceptible de desactualización. Supabase debe conservar RLS y permitir SELECT de columnas públicas; no abrir INSERT/UPDATE/DELETE a `anon`/`authenticated`.
