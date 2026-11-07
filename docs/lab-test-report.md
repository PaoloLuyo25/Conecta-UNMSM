# Informe de pruebas reales — Conecta UNMSM, laboratorio

**Fecha:** 6 nov 2026. **Ámbito:** laboratorio autorizado por cláusula 11; NO repositorio del concurso.

## Resultado automatizado

- Comando REAL: `python -m pytest -q -W error`
- Resultado REAL: **61 passed in 0.20s**, sin warnings en el entorno de ejecución actual.
- Los tests están en `tests/` y se ejecutaron con servicios **ficticios**. No se hicieron solicitudes a Gemini ni a Supabase.

## Smoke tests HTTP reales

- Se arrancó `uvicorn backend.app.main:app` en localhost con `AI_MODE=demo`, `ALLOW_DEMO_RECORDS=true`, `CATALOG_FILE=data/catalog.demo.json`.
- `GET /api/health`: HTTP **200** y `{"status":"ok"}`.
- `GET /api/services`: HTTP **200**, `catalog_source=local_snapshot`, **6 registros elegibles** de demostración (todos ficticios y excluyendo uno de otra facultad).
- Segunda ejecución con servidor real: `GET /` **200**; primera petición `POST /api/route` **200**, `mode=question`, cero tarjetas; segunda petición con `clarification_used=true` **200**, `mode=route`, una tarjeta ficticia virtual. **PASÓ el ciclo HTTP completo** (no se abrió un navegador conectado a la API).

## Interfaz

- Chromium headless con HTML/CSS/JS reales y **respuestas de API simuladas**: **PASÓ** `question → route`, mostró la tarjeta sintética virtual, funcionó la opción urgente y no se observaron errores de JavaScript.
- Chromium navegando directamente contra `localhost`: **NO EJECUTADO con éxito** por bloqueo `ERR_BLOCKED_BY_ADMINISTRATOR` en el entorno. No se presenta la prueba con mocks como prueba de conexión real de interfaz ↔ API.
- Pantallas de laptop (capturadas con mock) incluidas aparte de la carpeta entregable como vista previa.

## Matriz de QA según documento del equipo

| QA | Estado | Comprobación |
|---|---|---|
| 01–02 | PASA automatizado | `test_routes.py`, validación y 422 |
| 03–04 | PASA automatizado | `test_question_only_one_round`, `test_second_clarification_from_ai_is_ignored` |
| 05–06 | PASA automatizado | `test_bad_ai_id_is_rejected`, `test_missing_source_contact_hours_are_not_invented` |
| 07 | PASA simulado | `test_ai_failure_returns_nonpersonalized_catalog`, `test_invalid_ai_json_is_controlled`; **sin proveedor real** |
| 08–09 | PASA automatizado | `test_changed_restriction_recalculates_mock`, `test_irrelevant_restriction_does_not_force_fake_change` |
| 10 | PASA automatizado | `test_demo_excludes_other_faculty`, `test_other_faculty_is_out_of_scope` |
| 11 | PASA automatizado | `test_expired_and_closed_are_not_offered`, avisos de fecha/fuente |
| 12 | PASA automatizado | `test_no_records_when_no_demo_flag`, `test_default_snapshot_empty_not_fictional` |
| 13 | PASA simulado | `test_remote_failure_uses_labeled_local_fallback`; **sin Supabase real** |
| 14 | PASA parcial | tests de inyección + UI no `innerHTML`; pruebas de navegador con backend real pendientes |
| 15 | PASA con mock UI | `test_urgent_help_works_without_ai` y navegación Chromium simulada |

## Estado de tareas

**Implementado y verificado automáticamente en laboratorio:** T02, T04 (contrato simulado), T05–T07, T12–T13 (con adapter simulado), T15 y T17–T18. **Implementado, con verificación manual real aún pendiente:** T03, T08–T09, T14, T16, T20. **Implementado, sin prueba de proveedor real:** T10–T11 (Gemini), T19 (Supabase condicional). **Pendientes / no declaradas terminadas:** T01 (aprobación de los tres), T21–T24 (QA completo, integración limpia verificada en Windows, video y entrega).

Ningún RF ni tarea se declara **validado ante el evento** únicamente por estas pruebas de laboratorio. No hay datos verificados de la UNMSM. Consultar la spec para los 22 RF y las advertencias de alcance.
