# Conecta UNMSM — reglas del agente

## Jerarquía SDD
1. `docs/constitution.md` (actualizar por acuerdo del equipo).
2. `specs/006-fisi-otros-antecedentes/spec.md` (requisitos vigentes EARS, no código).
3. `specs/006-fisi-otros-antecedentes/plan.md` (módulos y decisiones).
4. `specs/006-fisi-otros-antecedentes/tasks.md` (tareas pequeñas, tests por RF).
5. Contratos: `docs/api-contract.md`, `docs/catalog-contract.md`.

## Roles
- José: backend FastAPI, repositorios, Supabase/RLS, lectura de catálogo y Git.
- Paolo: Gemini y reglas de selección, pruebas adversas y normalización.
- Daniela: HTML/CSS/JS, placeholder, modo invitado, login y visualización.

## Principios obligatorios
- Producto independiente, nombre visible **Conecta UNMSM** (sin etiquetas de versión).
- Web scraping SOLO descubre noticias en fuentes permitidas; **no convierte automáticamente información web en registros publicables**. La revisión humana decide alcance, público, requisito, fecha, estatus y si algo es beca o convenio.
- La base de datos es la fuente de los hechos. Gemini recibe como máximo seis candidatos, selecciona hasta tres IDs y nunca inventa contactos, pasos, plazos ni elegibilidad.
- El frontend solo permite `FISI` y `OTROS`; este último recibe exclusivamente servicios centrales universales. El historial conserva IDs y no texto de consultas. Los antecedentes vencidos nunca son convocatoria activa.
- `ALLOW_DEMO_RECORDS=false` en operación real; fixtures sintéticas solo en tests.
- Historial no guarda texto libre, requiere opt-in y RLS probado; ninguna clave en cliente/Git.
- No afirmar pruebas remotas sin ejecutar; no confundir `reviewed_at` con convocatoria abierta.

## Comandos
`python -m pytest -q -W error` / `python -m tools.explorar_fuentes` / `python -m tools.generar_sql_catalogo`. 
