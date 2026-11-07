# Plan 002 — Maqueta funcional dividida por responsables (LAB v4.4)

**Derivado de:** `spec.md` (RF2-01 a RF2-22). Arquitectura actual: mismo-origen HTML/CSS/JS → FastAPI/Pydantic → `RouteService` + normalizador + `GeminiAdapter` → `CatalogRepository` Supabase/JSON. Auth Supabase gestionado por backend; historial separado y condicionado.

## Componentes y dueños
- **José — capa servidor/datos:** `backend/app/api.py`, `auth_api.py`, `auth_history.py`, `main.py`, `config.py`, `schemas.py`, `repository.py`, `local_repo.py`, `supabase_repo.py`, `route_service.py`, `route_ticket.py`, `validator.py` y migraciones SQL. Propietario del contrato de integración, no de las decisiones UX o del prompt IA.
- **Paolo — semántica y selección:** `backend/app/ai_adapter.py`, `normalization.py`, `districts.py`; responder con IDs de catálogo autorizados, códigos de motivo y pregunta controlada; sin textos libres con hechos nuevos.
- **Daniela — presentación:** `frontend/index.html`, `app.js`, `styles.css`; tres modos `question/route/degraded`, bienvenida, login opcional, historial y reinicio; no comunicar navegador directamente con Supabase o Gemini.

## Persistencia y datos
- `services`: catálogo público de lectura con RLS de solo consulta, universalidad verificada para facultades distintas de FISI.
- `route_history`: solo para titulares autenticados; tabla con políticas RLS, metadatos mínimos e idempotencia; no conservar textos de necesidades ni contraseñas. SQL histórico `supabase/003_route_history.sql` se mantiene sin nueva migración en esta partición.
- `catalog.snapshot.json`: respaldo vacío salvo datos documentados y permitidos. `catalog.demo.json`: solo fixtures ficticias con bandera explícita. Documento de distritos ausente: no inventar.

## Flujos (contrato)
A. Visitante abre la web → continúa sin cuenta → `POST /api/route` → `route/question/degraded` → «Nueva consulta» limpia lo anterior.
B. Usuario elige inicio de sesión → `POST /api/auth/login` (correo y contraseña) → `GET /api/auth/me` → consulta → botón «Guardar esta ruta» → `POST /api/history/save` con comprobante firmado → historial propio.
C. Visitante recibe una ruta → pulsa guardar → login → guardar comprobante de la misma ruta sin reconsultar Gemini.
D. Falla IA/Supabase/historial → degradación transparente; nunca una cita ni contacto inventado.

## Decisiones y alternativas descartadas
- Copias ejecutables idénticas por ZIP, **modificaciones separadas por propiedad**, en lugar de fragmentos de proyecto sin imports ni tests.
- Backend como única puerta a Gemini/Auth y lectura de Supabase, en lugar de claves en JS.
- Historial opt-in por comprobante firmado temporal en lugar de volver a ejecutar IA o confiar en IDs del cliente.
- Contraseña en Supabase Auth (v4.4), no OTP (etapa v4 anterior); Confirm Email desactivado solo es aceptable para laboratorio ficticio.
- Normalizador conservador de zonas y fuente Markdown para distrito, en lugar de inferir geografía con IA.

## Trazabilidad resumida
- RF2-01,02,05–07,10–12,17 → Daniela UI y pruebas de navegador; José endpoints de sesión/guardado.
- RF2-03,04,18,19,21 → Paolo IA/normalización + José validación/repositorio.
- RF2-08,09,13–16,20,22 → José Auth, tickets, RLS y filtros, con pruebas compartidas.

## Pruebas
`python -m pytest -q -W error`; `node --check frontend/app.js`; `python tests/browser_smoke.py` si Playwright/Chromium está instalado (simula HTTP). Aparte, pruebas **remotas reales** de Auth, RLS, correo y Gemini antes de desplegar.

## Riesgos que no se cierran con esta división
Contrato legado v3 conserva texto anterior que excluía login; prevalece la spec 002 para el **LAB**. La fuente geográfica y las credenciales son externas. El calendario de hackathon original es histórico, no reloj de ejecución de esta entrega. No desplegar en producción con `Confirm Email OFF`.
