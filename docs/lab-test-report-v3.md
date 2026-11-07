# Informe de ejecución real — Conecta UNMSM laboratorio v3

**Fecha de ejecución:** 6 noviembre 2026. **Entorno:** contenedor Python 3.13, pruebas sin Gemini ni Supabase externos.

## Ejecutado y APROBADO

| Prueba real | Resultado |
|---|---|
| `python -m pytest -q -W error` desde la raíz | **79 passed in 0.29s**, 0 warnings |
| `node --check frontend/app.js` | **PASS**, sin errores sintácticos |
| Uvicorn en `127.0.0.1:18764` y `GET /api/health` | **HTTP 200**, `{"status":"ok"}` |
| `GET /` | **HTTP 200**, contiene selector de facultad |
| `GET /api/services?faculty_code=OTRA` | **HTTP 200**, cuatro fichas sintéticas CENTRALES universales de transporte, ninguna ficha FISI |
| `POST /api/route` para OTRA y «Necesito información de transporte» | **HTTP 200**, `mode=question` con banco controlado de zona |
| Segunda `POST /api/route` con `clarification_used=true` y «zona sur» | **HTTP 200**, `mode=route`, único `DEMO-TRANSPORTE-SUR` |
| `POST /api/route` para OTRA y «Quiero bienestar y becas» | **HTTP 200**, `mode=degraded`, 0 servicios |
| SDK Gemini con doble de pruebas, JSON inválido y secretos no expuestos | **Automatizado**, no contacto externo |
| Supabase SDK con doble de pruebas, columnas explícitas, esquema y política SQL inspeccionada | **Automatizado**, no contacto externo |

## NO EJECUTADO / por verificar fuera del contenedor

- **Gemini API con clave real, acceso a `gemini-3.5-flash-lite`, respuesta semántica y cuota del usuario**: NO EJECUTADO. El SDK se ensayó mediante dobles de prueba; `GEMINI_API_KEY` debe ser aportada privadamente por José en su ordenador.
- **Supabase PostgreSQL real y RLS sobre una instancia en nube**: NO EJECUTADO. No se proporcionó Project URL ni publishable key; los SQL están listos pero NO aplicados. Es obligatorio verificar SELECT y rechazo de INSERT/UPDATE/DELETE con rol anon.
- **Prueba de navegador gráfico sobre FastAPI real**: NO EJECUTADO. Se intentó Playwright, pero Chromium Headless Shell no está disponible en este entorno. Los flujos HTTP de FastAPI y la sintaxis de JavaScript sí fueron comprobados.
- **Datos institucionales oficiales**: NO INCORPORADOS. Los registros del catálogo de laboratorio se etiquetan `prueba_ficticia`; zonas, modalidad y categoría son sintéticas y no prometen disponibilidad real.
- **Verificación de que una persona de verdad pertenece a FISI**: NO EXISTE, por diseño del MVP anónimo. Se usa la facultad declarada por la persona; no hay autenticación ni autorización universitaria.
- **Despliegue público, compatibilidad desde otra laptop y captura de video**: NO EJECUTADO.

## Requisitos SDD relacionados

- **RF-23/24/25:** pruebas unitarias + HTTP local aprobadas para los escenarios ficticios, no equivalen a verificación institucional de cobertura central.
- **RF-26:** comportamiento fallback probado offline con repositorio simulado; Supabase real no verificado.
- **RF-01–22:** conservar resultados y límites del informe anterior; la adenda no los convierte automáticamente en VALIDADO para el concurso.

**Conclusión:** núcleo local funcional y verificable; despliegue de infraestructura real y datos reales requieren operaciones explícitas y evidencias adicionales. Ningún resultado de ensayo justifica afirmar que la universidad ofrece hoy un servicio.
