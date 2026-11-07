# Plan 003 — Multifactultad LAB

1. No tocar la autenticación ni el historial de v4.4.
2. Usar lista oficial de nombres de facultades en `data/facultades_unmsm.json`; UI presenta sus códigos en `frontend/index.html`.
3. `supabase/004_multifacultad_categories.sql`: agregar `becas` y `movilidad_academica`, sin crear tablas nuevas.
4. `supabase/005_seed_multifacultad_FICTICIO.sql`: 7 ejemplos por facultad (140), solo pruebas, sin fuentes/fechas/requisitos inventados.
5. `repository.list_eligible`: alcance por facultad; central solo universal para otras facultades; preservar FISI legado.
6. `targeting.py`: perfil declarativo y vocabulario controlado, distinguir viaje académico vs transporte, máximo 6 candidatos.
7. `route_service.py`: decide única aclaración de público, genera shortlist y valida IDs antes de mostrar ruta.
8. `ai_adapter.py`: adaptador existente y esquema estructurado, mensaje corto por cada candidato.
9. `frontend/index.html` y `app.js`: 20 facultades y público; consulta de invitado y cuentas quedan intactas.
10. QA: archivos de prueba sintéticos, regresión, ejecución real en Windows y prueba RLS con dos cuentas antes de activar historial.

Alternativas descartadas: mandar 140 servicios a Gemini, crear becas oficiales a partir de suposiciones, interpretar cada viaje como transporte, migrar el historial con campos sensibles.
