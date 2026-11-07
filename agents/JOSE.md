# Agente José — backend, Supabase, Auth e integración

**Rol:** propietario técnico de backend/contratos/datos y responsable de merge. Base v4.4 LAB. Nunca reescribir la UI o el prompt Gemini en tu rama.

## Leer primero
`docs/constitution.md` → `specs/002-laboratorio-v44/spec.md` → `specs/002-laboratorio-v44/plan.md` → `docs/sdd-v44/CONTRATO_API_ACTUAL.md` → `specs/002-laboratorio-v44/tasks.md` → `docs/sdd-v44/REPARTO_Y_MERGE.md`.

## Tu área
`backend/app/api.py`, `auth_api.py`, `auth_history.py`, `main.py`, `config.py`, `schemas.py`, `repository.py`, `local_repo.py`, `supabase_repo.py`, `route_service.py`, `route_ticket.py`, `validator.py`; `supabase/*.sql`, `data/catalog*.json`; pruebas de API, Auth/RLS, catálogo y tickets.

## Restricciones
- Mantener los endpoints y campos v4.4 y sesión exclusiva en FastAPI; Auth correo+contraseña, NO OTP.
- No exponer contraseña ni JWT al navegador; los tokens de sesión solo en cookies HttpOnly y solo bajo HTTPS seguro en despliegues reales.
- Rechazar correos fuera del dominio exacto; no afirmar identidad verificada si Supabase Confirm Email está OFF.
- RLS en Supabase debe probarse con A/B y anónimo **real**. SQL estático y TestClient no bastan.
- El backend no inventa información institucional ni permite usar IDs fabricados por IA/cliente.
- El historial es opcional y con consentimiento explícito; jamás almacenar texto de consulta, diagnóstico o datos sensibles.
- No ejecutar `003_route_history.sql` otra vez salvo cambio de esquema revisado.

## Tarea y prueba
Ejecutar solo `T2-Jxx` indicada. Redactar criterios/tests antes del cambio, ejecutar `python -m pytest -q -W error`, registrar comandos/salidas, conservar fallback JSON honesto. Merge solo tras pruebas e inspección de secretos. No marcar proveedores reales como probados sin evidencia.


## Adenda autorizada 003 — José (7 nov 2026)
José aprobó ampliación de demostración para las 20 facultades, becas y movilidad por público. Excepcionalmente aquí se incluye la actualización mínima del frontend de Daniela para probar localmente la integración. Antes de unir ramas, Daniela valida la pantalla y Paolo el contrato Gemini. Revisar `specs/003-multifacultad-demo/` y `INICIO_CMD_MULTIFACULTAD.txt`. Ejecutar SQL 004 antes de 005 y jamás repetir 001/003 sin confirmar su estado.
