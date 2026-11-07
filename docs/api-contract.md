# Contrato API — Conecta UNMSM

**Contrato vigente del servidor.** La consulta es pública; Auth e historial son opcionales. El frontend y la API comparten el mismo origen.

## Endpoints principales

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/api/health` | `{"status":"ok"}` (solo salud local del servidor) |
| GET | `/api/services?faculty_code=FISI` | Catálogo filtrado de la facultad + centrales universales; incluye fuentes y advertencias |
| POST | `/api/route` | `mode = question / route / degraded`, servicios hasta 3, advertencias |
| GET | `/api/features` | Estado de funciones opcionales (historial) |

### POST /api/route

```json
{
  "faculty_code": "FISI",
  "applicant_type": "sin_especificar",
  "message": "Soy un estudiante y quiero conocer oportunidades de movilidad académica",
  "clarification_answer": null,
  "clarification_used": false,
  "previous_service_ids": [],
  "save_to_history": false
}
```

`faculty_code`: cualquiera de los 20 códigos de `data/facultades_unmsm.json`, en mayúscula; puede conservarse el código general de prueba `OTRA` para compatibilidad. `applicant_type`: `pregrado`, `posgrado`, `docentes` o `sin_especificar`. El mensaje acepta 1–800 caracteres visibles. El backend jamás da por válidos IDs proporcionados por el navegador.

**Modo `question`:** una sola aclaración; no mostrar fichas de servicios en esa respuesta. **Modo `route`:** 1–3 servicios con `id`, `category_code`, `faculty_code`, `audience`, `source_url`, `availability_status`, `warnings`, `why_text` calculado por el servidor y hechos provenientes del catálogo. **Modo `degraded`:** IA o fuente no disponible, `ai_used=false`, advertencia visible, posiblemente resultados informativos **no personalizados**.

## Acceso e historial privados (solo cuando ENABLE_HISTORY=true)
`POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`, `POST /api/history/save`, `GET /api/history`, `DELETE /api/history/{id}`, `DELETE /api/history`.

Son contratos conservados: correo y contraseña gestionados por Supabase Auth; sesión con cookies HttpOnly; `Origin` validado en operaciones de escritura; RLS por propietario y datos mínimos (IDs/fechas/ámbito, no mensaje original). Verificar con instancias reales antes de producción. La cuenta es opcional para todas las consultas públicas.

## Contrato de Gemini
Una llamada por turno, máximo seis candidatos compactos. Devuelve IDs existentes y códigos (`matches_need`, `matches_modality`, `matches_location`, `requires_confirmation`), sin redactar hechos, enlaces, requisitos ni disponibilidades. El servidor valida cantidad, IDs y alcance nuevamente antes de construir la tarjeta.
