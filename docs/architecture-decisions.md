# Registro de decisiones de arquitectura (ADR liviano)

**Jerarquía:** constitución > spec activa > plan activo > este registro para justificaciones. Cambios con impacto en RF deben reflejarse antes en la spec.

| ID | Estado | Decisión | Razón / alternativa descartada |
|---|---|---|---|
| ADR-01 | DECIDIDO | Metodología SDD: constitución, spec EARS, clarificación, plan, tareas y tests por RF. | Evita prompts sueltos y código no verificable. |
| ADR-02 | DECIDIDO | Monolito modular de tres capas. | Microservicios añaden fallas y complejidad en 6,5 h. |
| ADR-03 | DECIDIDO | Frontend HTML/CSS/JS sin framework. | No forzar React/Next a Daniela. |
| ADR-04 | DECIDIDO | FastAPI/Pydantic; módulos separados para rutas, IA y datos. | Python es el denominador común; contratos tipados. |
| ADR-05 | CONDICIONAL | Supabase PostgreSQL como fuente principal solo si conexión/RLS/lectura funcionan; Repository local JSON como contingencia. | SQLite también sería suficiente, pero no se añade por obligación; no bloquear MVP por cloud. |
| ADR-06 | CONDICIONAL | Gemini API; modelo exacto según acceso real probado. | No asumir que ChatGPT Plus incluye API; ni cuotas sin prueba. |
| ADR-07 | DECIDIDO | IA devuelve IDs permitidos y códigos de razón; el servidor compone todos los datos institucionales. | Evita justificaciones libres con supuestos horarios/requisitos. |
| ADR-08 | DECIDIDO | Una llamada de IA por turno; a lo sumo una ronda de aclaración por consulta. | Limita latencia, consumo y complejidad. |
| ADR-09 | DECIDIDO | Local primero; despliegue público solo si MVP estable y sobra tiempo. | Menos riesgos de demo. |
| ADR-10 | DECIDIDO | Datos públicos de lectura; sin autenticación ni escritura pública y sin persistir conversaciones. | Menor superficie de seguridad. |
| ADR-11 | DIFERIDO | Comunicados, denuncias, ediciones administrativas, mapas, tiempos de transporte, historial. | No son la función principal. |
| ADR-12 | PENDIENTE | Reglas sobre importar documentos/datos preparatorios antes del inicio. | Confirmación escrita de organización. |

## Regla para cambios
Todo cambio debe decir: **qué decisión sustituye, qué RF modifica, coste temporal, riesgo nuevo, impacto en pruebas y quién lo aprueba**. Sin autorización no se asume adoptado.


## ADR adicionales del laboratorio v3 — autorizados por José (6/11/2026)

| ID | Estado | Decisión | Alcance / prueba |
|---|---|---|---|
| ADR-13 | DECIDIDO PARA LABORATORIO | Selector FISI / otra facultad; para otras facultades, únicamente fichas CENTRALES con `accessible_to_all_faculties=true`. | Sin traspasar procedimientos particulares; tests `test_scope_v3.py`. |
| ADR-14 | DECIDIDO PARA LABORATORIO | SQL Supabase de tabla pública RLS + seed ficticio; JSON local como fallback. | Conexión real, GRANTS y RLS externos todavía NO VERIFICADOS. |
| ADR-15 | DECIDIDO PARA LABORATORIO | Gemini `gemini-3.5-flash-lite` desde backend con clave proporcionada por usuario. | SDK y JSON con salida tipada probados con dobles; cuenta/quota real PENDIENTE. |
| ADR-16 | DECIDIDO PARA LABORATORIO | Preguntas de aclaración por `question_code` del banco interno. | No mostrar texto libre de una IA como pregunta institucional o sensible. |

**Relación con el plan v3:** `docs/plan-operativo-v3.md` modifica las decisiones de arquitectura anteriores en los puntos expresos. La extensión de otras facultades fue solicitada y aprobada posteriormente por José y se documenta también en la spec de laboratorio. Los cambios de contrato requerirían coordinación de todos para trasladarlos al repo oficial.


## ADR-21 — DEMO multifacultad autorizada por José (7/11/2026)
Extiende alcance informativo de FISI a las 20 facultades UNMSM **solo mediante escenarios ficticios**. El catálogo marca cada ejemplo `prueba_ficticia`; el filtro por facultad y público se realiza antes de Gemini. Añade categorías `becas` y `movilidad_academica` y máximo seis candidatos de IA. Preserva Auth/History v4.4. Consulta la Spec 003.

## Decisiones vigentes — núcleo académico (aprobadas para esta entrega)

| ID | Estado | Decisión | Motivo |
|---|---|---|---|
| ADR-21 | DECIDIDO | Priorizar oportunidades académicas reales (OGCRI/VRAP/VRIP) y conservar bienestar/clínica/transporte con avisos. | Evita la ficción como núcleo sin perder el orientador contextual. |
| ADR-22 | DECIDIDO | Un solo frontend y un solo backend; ninguna otra fuente de verdad distinta de `Service`. | No romper autenticación, rutas ni historial existentes. |
| ADR-23 | DECIDIDO | Scraping solo para descubrimiento, revisión humana antes de SQL; respetar robots.txt y dominios. | Un anuncio no garantiza apertura, elegibilidad ni beca. |
| ADR-24 | DECIDIDO | Catálogo inicial revisado con fuentes, audiencias controladas y estado por confirmar. | Evita inventar fechas, fondos o acceso universal. |
| ADR-25 | DECIDIDO | Máximo 6 candidatos Gemini y hasta 3 IDs de resultado, validación determinista. | Reduce contexto y errores con Flash-Lite. |

**Alcance sobre decisiones antiguas:** los ADR-10/11 que excluían Auth e historial fueron superados por los cambios explícitos de acceso opcional aprobados previamente. Las modificaciones de `specs/003-multifacultad-demo` quedan históricas: el catálogo ficticio no se activa en uso normal. El proyecto se llama únicamente **Conecta UNMSM**.
