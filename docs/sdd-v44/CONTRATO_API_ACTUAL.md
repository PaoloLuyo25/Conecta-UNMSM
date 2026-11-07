# Contrato API real del código base v4.4

Los endpoints declarados están implementados en `backend/app/api.py` y `backend/app/auth_api.py`. **No renombrar** propiedades sin coordinar José–Paolo–Daniela; preferir cambios aditivos.

| Endpoint | Sesión | Descripción |
|---|---|---|
| `GET /api/health` | Pública | Devuelve `{ "status":"ok" }` solamente; no prueba Gemini/Supabase. |
| `GET /api/features` | Pública | `history_enabled` controla la UI del historial. |
| `GET /api/services?faculty_code=FISI` | Pública | Catálogo filtrado y procedencia; otros códigos solo ven CENTRAL universal comprobado. |
| `POST /api/route` | Pública | Devuelve `question`, `route` o `degraded`; si hay 1–3 tarjetas válidas entrega `route_ticket`. |
| `POST /api/auth/signup` | Pública, Origin validado | Correo exacto `@unmsm.edu.pe` + contraseña por Supabase Auth. |
| `POST /api/auth/login` | Pública, Origin validado | Correo/contraseña, cookies HttpOnly en sesión confirmada. |
| `GET /api/auth/me` | Cookie válida | Indica autenticación sin exponer tokens. |
| `POST /api/auth/logout` | Cookie y Origin | Cierra sesión y limpia cookies. |
| `POST /api/history/save` | Sesión + Origin + historial habilitado | Guarda una ruta existente mediante comprobante firmado temporal; no llama otra vez a Gemini. |
| `GET /api/history?limit=20&offset=0` | Sesión | Recupera historial propio sujeto a RLS/revalidación. |
| `DELETE /api/history/{route_id}` | Sesión + Origin | Borra una ruta propia. |
| `DELETE /api/history` | Sesión + Origin | Borra el historial propio. |

## POST /api/route (forma válida)
```json
{
  "faculty_code":"FISI",
  "message":"Necesito orientación para una situación cotidiana",
  "clarification_answer":null,
  "clarification_used":false,
  "previous_service_ids":[],
  "save_to_history":false,
  "client_request_id":null
}
```
**Respuesta:** `mode`, `needs[]`, `constraints[]`, `question`, `services[]` (máximo 3), `warnings[]`, `ai_used`, `catalog_source`, `catalog_verified_at`, `history_saved`, `history_id`, `route_ticket`. Los hechos de `services[]` vienen exclusivamente del catálogo y el validador.

## Límite de responsabilidades
- **Paolo → José:** `GeminiAdapter.choose(message, clarification_answer, clarification_used, eligible)` y retorno de `AISelection`: IDs y códigos permitidos; excepción controlada para error de IA. No generar horarios/contactos.
- **José → Daniela:** contrato HTTP y errores semánticos en español; sesión exclusiva backend; el navegador no consulta Gemini/Supabase ni maneja tokens privilegiados.
- **Daniela → José:** no inventar modos ni nombres de campo; usar `textContent` para contenido de estudiantes y servicios.

## Auth / privacidad
La versión v4.4 usa **contraseña** y NO OTP. Validar dominio **no prueba** posesión del buzón o matrícula. Con `Confirm Email OFF` es únicamente laboratorio con identidades sintéticas; **no** activar en producción. Para confirmar propiedad del correo, habilitar confirmación por enlace y configurar SMTP, con prueba manual, sin convertir el formulario a OTP salvo cambio de spec aprobado.

Guardado explícito siempre: generar ruta no significa consentir persistencia. El historial guarda IDs, facultad, origen y fecha, nunca el texto de la necesidad. El `route_ticket` vence y puede invalidarse al reiniciar servidor. Habilitarlo solo con Supabase, SQL 003 y RLS probados externamente.
