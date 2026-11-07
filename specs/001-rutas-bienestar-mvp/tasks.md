# Tareas — Spec 001 (SDD, programación solo cuando esté autorizada)

**Estado inicial:** TODAS PENDIENTES. Cada tarea 15–30 minutos de trabajo enfocado en su dueño; estimaciones orientativas, no promesa de duración. Una tarea se marca `[x]` únicamente tras comprobar su «Hecho cuando». Las tareas pueden realizarse en paralelo según dependencias.

## Fase 0 — Contrato e inicio
- [ ] **T01 — José + todos (20 min).** Crear repo limpio y acordar `api-contract.md`, variables y `spec.md`. **RF:** todos. **Dep.:** ninguna. **Hecho cuando:** tres integrantes confirman contrato y `.gitignore` protege secretos.
- [ ] **T02 — José (20 min).** Esqueleto FastAPI, health y conexión básica; sin IA. **RF:** RF-01, 22. **Dep.:** T01. **Hecho cuando:** `GET /api/health` responde desde navegador/TestClient.
- [ ] **T03 — Daniela (20 min).** HTML inicial: campo, selector FISI fijo, submit, contador y aviso. **RF:** RF-01, 02, 22. **Dep.:** T01. **Hecho cuando:** formulario permite entrada ficticia sin pedir datos personales.
- [ ] **T04 — Paolo (20 min).** Definir salida del adaptador IA y respuestas simuladas válidas/inválidas para tests. **RF:** RF-03, 05, 08, 13. **Dep.:** T01. **Hecho cuando:** Jose conoce formato de IDs/códigos y existen fixtures de pruebas sintéticas.

## Fase 1 — Catálogo sin IA (prioridad absoluta)
- [ ] **T05 — José (25 min).** Modelar/validar entidad `service` y estados de vigencia. **RF:** RF-10–15, 19. **Dep.:** T02. **Hecho cuando:** prueba rechaza un servicio sin ID/categoría válida y no inventa campos faltantes.
- [ ] **T06 — José (25 min).** Repositorio local JSON de solo lectura con datos de prueba sintéticos **etiquetados**. **RF:** RF-08, 10, 13, 15. **Dep.:** T05. **Hecho cuando:** un test recupera servicios de FISI/CENTRAL y excluye ámbito incorrecto.
- [ ] **T07 — José (20 min).** Endpoint `GET /api/services` contra Repository. **RF:** RF-10–15, 19. **Dep.:** T06. **Hecho cuando:** JSON válido incluye fuente/estado o informa falta de datos.
- [ ] **T08 — Daniela (25 min).** Crear vista de tarjetas reutilizable para `route` y `degraded` con JSON simulado. **RF:** RF-10–12, 16–18. **Dep.:** T03 + contrato. **Hecho cuando:** las tarjetas muestran fuente/advertencia y faltantes de forma legible.
- [ ] **T09 — Daniela + José (25 min).** Conectar formulario a backend para mostrar catálogo sin IA. **RF:** RF-01, 02, 10, 11, 15. **Dep.:** T07, T08. **Hecho cuando:** consulta → servicio → fuente es visible en navegador real.

## Fase 2 — IA restringida e integración
- [ ] **T10 — Paolo (20 min).** Integración mínima al modelo Gemini vía backend, secreto externo al código. **RF:** RF-03, 08, 18. **Dep.:** T04. **Hecho cuando:** prueba real con **texto ficticio** y cuota confirmada devuelve JSON estructurado, sin revelar clave.
- [ ] **T11 — Paolo (25 min).** Prompt de extracción de necesidades y restricciones con candidatos autorizados. **RF:** RF-03, 08, 19, 20. **Dep.:** T10, T06. **Hecho cuando:** los tests golden devuelven IDs existentes para casos cubiertos y reconocen límites cuando no hay datos.
- [ ] **T12 — José (25 min).** Validador de IDs, deduplicación, scope y códigos de razón. **RF:** RF-08, 10–15, 20. **Dep.:** T05, T04. **Hecho cuando:** test rechaza IDs ficticios y afirma pasos proceden del Repository.
- [ ] **T13 — José + Paolo (25 min).** Implementar `/api/route` con consulta → selección → ruta en una llamada. **RF:** RF-01, 03, 08, 10–15, 18. **Dep.:** T11, T12. **Hecho cuando:** caso extremo a extremo devuelve 1–3 tarjetas verificables.
- [ ] **T14 — Daniela (20 min).** Integrar UI con respuesta real `mode=route`; loaders y errores de entrada. **RF:** RF-01, 02, 08, 11, 18. **Dep.:** T13, T08. **Hecho cuando:** el flujo principal se ejecuta desde navegador sin copiar JSON manualmente.

## Fase 3 — Adaptación y resiliencia
- [ ] **T15 — Paolo + José (25 min).** Pregunta de aclaración decisiva y protección de una sola ronda. **RF:** RF-05–07. **Dep.:** T13. **Hecho cuando:** caso de prueba responde pregunta una vez y una segunda aclaración no se solicita.
- [ ] **T16 — Daniela (20 min).** UI de `mode=question`, segundo envío contextual y `clarification_used`. **RF:** RF-05–07. **Dep.:** T15. **Hecho cuando:** flujo pregunta → respuesta → ruta funciona sin bucle.
- [ ] **T17 — José + Paolo (20 min).** Reevaluar necesidades al modificar restricción; permitir misma ruta si corresponde. **RF:** RF-09. **Dep.:** T15. **Hecho cuando:** QA-08/QA-09 pasan sin cambios artificiales.
- [ ] **T18 — José (25 min).** Resiliencia ante Gemini inválido/429/timeout y fallback honesto. **RF:** RF-15–17, 20. **Dep.:** T13. **Hecho cuando:** tres fallos simulados producen `degraded` sin excepción no controlada.
- [ ] **T19 — José (25 min, CONDICIONAL).** Adaptador Supabase de lectura con RLS probada. **RF:** RF-10–17. **Dep.:** T06. **Hecho cuando:** conexión real lectura segura y caída vuelve a snapshot sin presentar datos obsoletos como actuales. **Eliminar esta tarea si Supabase no está listo.**
- [ ] **T20 — José (15 min).** Opción visible «Necesito ayuda urgente» sin diagnóstico ni enlaces falsos. **RF:** RF-21. **Dep.:** T13. **Hecho cuando:** QA-15 pasa con caso ficticio y no depende de una clasificación clínica.

## Fase 4 — QA / entrega
- [ ] **T21 — Paolo (25 min).** Tests adversos de prompt injection, IDs inventados y datos inexistentes. **RF:** RF-13–16, 20. **Dep.:** T13, T18. **Hecho cuando:** test suite corre y se registran resultados reales.
- [ ] **T22 — Daniela (25 min).** QA visual, móvil, fuentes clicables, caracteres especiales y estados. **RF:** RF-01–22 (cobertura manual). **Dep.:** T14/T16/T18. **Hecho cuando:** tres casos y dos fallos constan como PASA/FALLA; no hay promesas sin datos.
- [ ] **T23 — José (25 min).** Integración final, secretos, ramas, instalación desde entorno limpio. **RF:** transversales. **Dep.:** T21, T22. **Hecho cuando:** `main` arranca, tests verdes y `git diff/status` sin secretos.
- [ ] **T24 — Paolo + Daniela + José (25 min).** Grabar demo auténtica, slides y paquete de entrega. **RF:** DoD general. **Dep.:** T23. **Hecho cuando:** video reproduce una ejecución real y repo/archivos están entregados antes del freeze.

## Reglas de secuencia y recorte
- Bloqueante: **T01 → T02/T05/T06/T07/T09 → T12/T13/T14**. Priorizar este camino sobre adornos.
- En paralelo: **Paolo T04/T10/T11; Daniela T03/T08; José T02/T05/T06**.
- Si faltan registros institucionales, solo pruebas etiquetadas ficticias; **no** presentarlas como fuentes oficiales.
- Si falta tiempo a las 12:15: recortar T15–T17 (aclaración secundaria) antes que estabilidad del core. Explicar cualquier desviación respecto al MVP prometido.
- Si Supabase se retrasa: omitir T19 sin renegociar el resto del sistema.
- No pasar a Txx+1 automáticamente. Test real antes de marcar una tarea `[x]`.
