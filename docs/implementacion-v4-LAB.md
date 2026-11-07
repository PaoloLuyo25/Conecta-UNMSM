# Conecta UNMSM — Implementación v4 del laboratorio SDD

**Fecha:** 6 de noviembre de 2026. **Alcance:** exclusivamente laboratorio; no transferir código al repositorio de competencia sin revisar sus bases. Los registros de demostración no son servicios institucionales reales.

## Decisiones implementadas y motivos

| Función | Cómo se implementó | Por qué / alternativa descartada |
|---|---|---|
| Zona `nte` → norte | `normalization.py`, aliases acotados, contexto de transporte y concordancia con el catálogo. | Determinista, auditable, barato; no permitir que Gemini decida arbitrariamente si un distrito pertenece a un área. |
| Distritos | `districts.py` carga una tabla Markdown de `data/distritos_verificados.md`, rechaza colisiones, sin registros predeterminados. | Solo la fuente autorizada aporta geografía. El documento recibido NO incluye la tabla real; no se inventa ninguna zona. |
| Nueva consulta | `frontend/app.js` invalida `sequence`, aborta `fetch`, reinicia formulario y tarjetas, conserva sesión e historial. | Evita contaminación por respuestas que llegan después de pulsar reinicio. |
| Loading | Spinner CSS dentro del botón, `aria-busy`, lector de pantalla, reduce motion. | Sin dependencias, sin otra solicitud a Gemini. |
| Retiro de bloque urgencia | HTML, JS y CSS limpios. | Mantiene el flujo aprobado sin borrar restricciones clínicas del backend. |
| Auth opcional | Supabase Auth OTP, FastAPI intermedio, cookies HttpOnly/SameSite Strict; sesión validada consultando `/auth/v1/user`. | Identifica propietario sin crear contraseñas ni poner tokens en localStorage. El correo no confirma matrícula UNMSM. |
| Historial privado | Consentimiento explícito, `service_ids` 1–3, usuario, fecha, facultad, origen e idempotencia por UUID; RLS por `auth.uid()`. | Recuperable entre dispositivos, minimiza datos sensibles. No se persiste el mensaje, el distrito, contacto ni condición del alumno. |
| Puerta de activación | `ENABLE_HISTORY=false` de forma predeterminada. | Evita registrar historiales hasta aprobar privacidad, correr SQL, verificar OTP/RLS reales y asegurar HTTPS en despliegue. |

## Archivos nuevos

- `backend/app/normalization.py`
- `backend/app/districts.py`
- `backend/app/auth_history.py`
- `backend/app/auth_api.py`
- `supabase/003_route_history.sql`
- `tests/test_normalization.py`
- `tests/test_districts.py`
- `tests/test_auth_history_v4.py`
- `tests/test_frontend_v4.py`
- `tests/browser_smoke.py` (opcional: requiere Playwright + Chromium)
- `docs/implementacion-v4-LAB.md` (este documento)

## Archivos modificados

- `backend/app/config.py`: settings y bandera segura de activación.
- `backend/app/main.py`: inyección de identidad, historial y catálogo de distritos.
- `backend/app/api.py`: campos aditivos `save_to_history`, `client_request_id`, `history_saved`, `history_id`.
- `backend/app/route_service.py`: normalización canónica antes de IA, sin relajar la elegibilidad.
- `backend/app/ai_adapter.py`: conserva el esquema Gemini corregido de lista tipada.
- `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`: reinicio, loading, cuenta/historial opcional, retiro de sección.
- `tests/test_ai_contract.py`, `tests/test_security.py`: adecuación a esquema y UI vigentes.

**Archivos existentes sin cambios necesarios en la versión del usuario:** `start-supabase-gemini.bat` (puerto 8001), `diagnostico_conecta.py`, el catálogo y sus SQL anteriores. El archivo de distritos no fue generado al no disponer de datos verificados.

## Cómo arrancar

Copiar los archivos anteriores dentro de `C:\conecta-unmsm-lab-v3`, preservando la carpeta del proyecto y su `.venv`. Ejecutar:

```powershell
cd C:\conecta-unmsm-lab-v3
.\.venv\Scripts\python.exe -m pytest -q -W error
.\start-supabase-gemini.bat
```

Abrir `http://127.0.0.1:8001/` y refrescar con `Ctrl + Shift + R`. La interfaz nueva y la normalización funcionan con historial apagado.

### Habilitar el historial **solo en el laboratorio y después de comprobar los requisitos**

1. Aprobar la modificación del alcance de privacidad y la retención de 30 días.
2. Aplicar `supabase/003_route_history.sql` en la base Supabase **de laboratorio**. No elimina la tabla `services` ni el catálogo.
3. Configurar Supabase Auth para OTP real: la plantilla debe enviar `{{ .Token }}` y debe verificarse que el correo llega a cuentas de prueba. El proyecto necesita disponer del método de email activo.
4. Probar en Supabase real con dos cuentas sintéticas que A no vea ni borre rutas de B, que anónimo reciba denegación y que el acceso para el titular funcione. La suite de mocks Python NO comprueba las políticas remotas.
5. Solo entonces iniciar el laboratorio en PowerShell mediante:

```powershell
cd C:\conecta-unmsm-lab-v3
$env:ENABLE_HISTORY = 'true'
$env:COOKIE_SECURE = 'false'  # exclusivamente localhost sobre HTTP
.\start-supabase-gemini.bat
```

Para despliegue con dominio HTTPS se exige `COOKIE_SECURE=true` y `PUBLIC_ORIGIN=https://dominio-autorizado`, además de rate limit distribuido y política real de eliminación de historiales caducados. **No activar en producción desde esta configuración de laboratorio.** El logout revoca la sesión de Supabase cuando responde; los JWT ya emitidos pueden persistir hasta su vencimiento.

## Formato de distritos pendiente

La fuente recibida no tiene los distritos; no se generó `data/distritos_verificados.md`. Al proporcionarla, **primero se debe validar que su estructura coincide con el lector o adaptar el lector a la estructura original, nunca inventar filas**. El lector actual requiere la tabla `Distrito | Zona | Alias` (alias opcional) y admite `norte`, `sur`, `centro`, `este` o zona vacía. Los tests usan **Distrito Alfa / Beta ficticios** y no prueban ninguna relación real.

## Pruebas realmente ejecutadas en este entorno

- `python -m pytest -q -W error` → **103 passed** (fakes para Gemini/Auth/Supabase; ninguna petición externa).
- `node --check frontend/app.js` → correcto.
- `python -m compileall -q backend tests` → correcto.
- `python tests/browser_smoke.py` → **BROWSER SMOKE OK** con DOM en Chromium y red simulada: consulta, spinner, reinicio y respuesta tardía; ninguna conexión remota. El navegador del contenedor bloquea la navegación localhost por política del entorno; por eso la prueba de UI carga HTML/JS directamente con un `fetch` simulado.

**Pendientes no simulables aquí:** envío de OTP real, compatibilidad real del endpoint REST de escritura Supabase, RLS con dos JWT de usuario distintos, pruebas sobre el Markdown geográfico real y prueba integral de Gemini desde la máquina del usuario. No confundir resultados simulados con confirmación de producción.
