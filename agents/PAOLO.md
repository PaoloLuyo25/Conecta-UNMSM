# Agente Paolo — IA, semántica y QA adverso

**Rol:** propietario de `backend/app/ai_adapter.py`, `normalization.py` y `districts.py` y pruebas de IA/normalización. No editar Auth/BD/frontend por tu cuenta.

## Leer primero
Constitución → Spec 002 → Plan 002 → contrato API v4.4 → matriz de propiedad → tasks `T2-Pxx`.

## Reglas
- Mantener el esquema **GeminiWireResponse tipado** de v4.4. La IA selecciona solo IDs/códigos permitidos, no textos institucionales ni enlaces/horarios.
- `choose(message, clarification_answer, clarification_used, eligible)` debe continuar compatible con José; coordinar cambio de firma o campos antes de editar.
- Una sola aclaración por consulta; zonas abreviadas solo cuando el contexto lo permite; si hay ambigüedad no deducir una región.
- No fabricar `data/distritos_verificados.md`, paradas, coberturas ni horarios. Al faltar fuente marcar limitado.
- Distinguir pruebas con dobles de una llamada REAL a Gemini y cuota real; claves sólo en `.env` servidor.
- Probar input hostil, JSON inválido, ID inautorizado, timeout/429 y mensajes con errores semánticos.

## Tarea y prueba
Solo `T2-Pxx` aprobada; primero fixture/test, después código; `python -m pytest -q -W error`. No emitir hechos del modelo fuera de allowlist; entregar reporte RF/test y límite conocido.
