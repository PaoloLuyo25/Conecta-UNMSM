# División para trabajo paralelo e integración

Los tres ZIP comparten una base v4.4 idéntica y ejecutable; el **propietario** de un archivo, no su mera presencia, determina quién puede editarlo.

| Propietario | Código editable | Pruebas primarias |
|---|---|---|
| **José** | `backend/app/api.py`, `auth_api.py`, `auth_history.py`, `config.py`, `main.py`, `repository.py`, `local_repo.py`, `supabase_repo.py`, `schemas.py`, `route_service.py`, `route_ticket.py`, `validator.py`; `supabase/*.sql`, `data/catalog*.json` | `test_api.py`, `test_auth_history_v4.py`, `test_password_auth_v4_3.py`, `test_optional_access_v4_4.py` (validación backend compartida), `test_repository.py`, `test_catalog.py`, `test_route_ticket.py`, `test_scope_v3.py`, `test_supabase_auth_headers.py`, `test_supabase_v3.py`, `test_routes.py` (integración) |
| **Paolo** | `backend/app/ai_adapter.py`, `normalization.py`, `districts.py` | `test_ai_contract.py`, `test_normalization.py`, `test_districts.py`; casos adversos y parte de `test_routes.py` bajo acuerdo con José |
| **Daniela** | `frontend/index.html`, `frontend/app.js`, `frontend/styles.css` | `tests/browser_smoke.py`, `test_frontend_v4.py`, revisión de accesibilidad y estado visitante/login |

**Archivos compartidos que no se editan de forma unilateral:** `docs/constitution.md`, `specs/**`, contratos API/catálogo, `requirements*.txt`, `.env.example`, `README.md`, `AGENTS.md`. José custodia el contrato, pero toda alteración que afecte a otra parte requiere conformidad de los tres en la spec.

**Escenario recomendado:** un repo Git único con ramas `feature/jose-api`, `feature/paolo-ia` y `feature/daniela-ui`. Los ZIP contienen la misma copia base para arrancar en paralelo; en Git se suben **solo archivos de propiedad** y los cambios SDD aceptados. José fusiona por pull requests. Nunca copiar tres carpetas completas, una sobre otra, tras haber empezado a editarlas.

## Orden de integración
1. Confirmar contrato de la base y tests iniciales (127 en el origen v4.4).
2. Jose integra contratos/datos y endpoints; si cambia firma de `ai_adapter.choose`, coordinar y actualizar test antes.
3. Paolo integra adaptador/normalizador + tests; José conecta sin duplicar la lógica.
4. Daniela integra HTML/CSS/JS y prueba recorrido visitante → consulta → guardado tras login, sin volver a llamar IA.
5. José ejecuta suite completa y smoke UI; el equipo realiza **aparte** pruebas reales de Supabase Auth, aislamiento RLS, SMTP cuando esté configurado y Gemini.

## Regla de conflicto
No editar simultáneamente `backend/app/route_service.py`, `backend/app/main.py`, `frontend/app.js` ni `docs/sdd-v44/CONTRATO_API_ACTUAL.md` desde ramas distintas. Si cambia un endpoint, aprobar cambio en spec → contrato → fixtures/tests → backend → frontend.
