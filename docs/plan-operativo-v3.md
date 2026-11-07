# CONECTA UNMSM — Plan de operación técnica v3

**Versión:** 3.0 · **Actualización:** 4 de noviembre de 2026  
**Competencia:** Hackathon ENEISOFT XVI 2026 · sábado 7 de noviembre  
**Estado:** planificación, **sin código del MVP**  
**Equipo elegible previsto:** José, Paolo y Daniela. Coach externo: asesoría solo si las bases lo permiten.  
**Tiempo efectivo:** 6,5 horas de desarrollo (08:30–13:00 y 14:00–16:00) · **Code Freeze:** 16:00 según las últimas bases proporcionadas · **cierre interno recomendado:** 15:30.

> **Propósito:** entregar un único marco de ejecución para tres desarrolladores con niveles intermedio/básico/básico. Este documento reemplaza las decisiones de arquitectura de los planes v1 y v2 **en los puntos expresamente modificados**. No incorpora entrevistas, resultados de campo, datos de servicios FISI ni afirmaciones sobre su vigencia; esa información llegará como un insumo independiente y será validada antes de ingresar al catálogo.

## 0. Decisiones que quedan cerradas

| Asunto | Decisión v3 | Motivo |
|---|---|---|
| Producto | **Conecta UNMSM — Ruta de Bienestar Adaptativa** | Misma idea aprobada; no cambiar el eje. |
| Eje y alcance | **Bienestar Universitario; piloto FISI**; modelo extensible a toda la UNMSM | Promesa demostrable en 6,5 h. |
| Equipo de desarrollo | **José / Paolo / Daniela** | El coach no es cuarto programador confirmado. |
| Arquitectura | **Monolito modular cliente-servidor en tres capas** | Suficiente complejidad para modularidad, pocas piezas móviles. |
| Frontend | **HTML, CSS y JavaScript vanilla** | Daniela trabaja sin incorporar una segunda curva de aprendizaje. |
| API | **Python + FastAPI + Pydantic** | Python compartido; contrato explícito. |
| Datos | **Supabase PostgreSQL como catálogo principal, condicionado a configuración comprobada antes de la competencia** | Facilita edición controlada y demostración web; no añadir si se convierte en bloqueo. |
| Respaldo de datos | **Instantánea local JSON de registros verificables, de solo lectura**, integrada por un adaptador `Repository` | Mantiene modo informativo si Supabase falla; no crea una segunda infraestructura. |
| IA del producto | **Gemini API; probar `gemini-3.5-flash-lite` con la cuenta efectiva** | Una llamada por interacción; JSON estructurado; acceso y cuota por confirmar. |
| Dónde ejecutar | **Local estable obligatorio; Vercel como despliegue web condicionado a que no retrase el MVP** | Internet y serverless no deben ser únicos puntos de éxito. |
| Git | **GitHub + ramas por persona + integraciones en horarios fijos** | Reducir colisiones. |
| QA | **pytest/TestClient, pruebas manuales y video de evidencia** | La IA revisora no sustituye ejecución real. |

**Decisión de compuerta para Supabase:** se utilizará como fuente principal **solo si** José comprueba acceso al proyecto, permisos de lectura, RLS y una consulta real antes de la jornada. Si no se cumple, se ejecuta el `Repository` local con los mismos campos; **no se intentará configurar una nueva infraestructura en el último tramo**. Supabase no es un requisito para aprobar el MVP y SQLite tampoco es una obligación: la alternativa mínima es un catálogo JSON de solo lectura cargado por el backend.

## 1. Qué construimos y qué no

### Función principal («killer feature»)

**De una necesidad cotidiana descrita en lenguaje natural a una ruta de bienestar explicable, verificable y adaptativa.**

1. La persona indica **FISI** y escribe su situación en términos generales.
2. La IA identifica varias necesidades y restricciones; **puede formular una sola aclaración** cuando cambie la selección de ruta.
3. El sistema elige **IDs de servicios ya presentes en un catálogo permitido**.
4. El backend obtiene de la base los **pasos, contactos, ubicaciones, horarios y fuentes**, sin pedirle al modelo que invente ninguno.
5. El resultado muestra de 1 a 3 tarjetas con fuentes, advertencias y estado de comprobación.
6. Si cambia una restricción importante, **recalcula** la selección de manera coherente. No se exige que la ruta cambie si la nueva información no modifica nada.

### Dentro del MVP

- Pantalla de consulta; campo de necesidad; facultad FISI fijada o seleccionada para piloto.
- Modo `pregunta` (máximo una aclaración) y modo `ruta` con tarjetas de servicios.
- Información institucional tomada de un catálogo revisado, con enlace y estado de vigencia.
- Modo `degradado` cuando falla Gemini, Supabase o hay datos insuficientes; nunca fingir una respuesta de IA.
- Probar al menos tres casos y dos fallos controlados.

### Fuera del MVP

Autenticación universitaria, historiales personalizados, diagnóstico o triaje clínico, envío real de solicitudes, cita confirmada, notificaciones, panel de administración propio, scraping de facultades, edición por usuarios, mapas, reconocimiento de imágenes, lectura automática de denuncias, sincronización de comunicados, RAG vectorial, embeddings, agentes múltiples, microservicios y analítica con datos personales. **La idea de cambiar estado por comunicados queda para fase posterior, con revisión humana.**

## 2. Arquitectura defendible ante el jurado

**Nombre técnico:** arquitectura cliente-servidor de tres capas con monolito modular, recuperación controlada de registros institucionales y generación de selección fundamentada. **No** es un agente autónomo ni RAG vectorial.

```text
     Navegador — HTML + CSS + JS (Daniela)
       ├─ Describe necesidad / responde aclaración
       └─ Muestra tarjetas / pasos / fuentes / alertas
                              │ HTTPS (o localhost) / JSON
                              ▼
           FastAPI — aplicación monolítica modular (José)
       ├─ Validación de entrada y contrato (Pydantic)
       ├─ Casos de uso: resolver / adaptar ruta
       ├─ ServiceRepository (interfaz de lectura)
       │      ├─ Supabase PostgreSQL [principal condicionado]
       │      └─ snapshot JSON verificado [contingencia]
       ├─ GeminiAdapter (Paolo) — Gemini API del lado servidor
       ├─ Validador de IDs, alcance, vigencia y reglas
       └─ Presenter: arma tarjetas con hechos desde catálogo
                              │
                              ▼
                   Respuesta al navegador
                 pregunta | ruta | degradado
```

**Separación de responsabilidades:**

- **Presentación:** captura necesidad y representa resultados, sin decidir criterios de elegibilidad.
- **Aplicación:** valida, consulta candidatos, llama al LLM una vez, aplica reglas, decide el modo y compone respuesta.
- **Datos:** repositorio intercambiable que entrega registros publicados sin permitir escrituras por el público.

**Patrón Repository:** interfaz simple de lectura con dos implementaciones conceptuales: `SupabaseRepository` y `SnapshotRepository`. La lógica de rutas no conoce el origen del dato; así un cambio de fuente no obliga a reescribir IA ni frontend.

**Importante:** el navegador **no llama directamente a Gemini** ni necesita acceso directo a Supabase. El backend utiliza una clave publicable de Supabase con RLS y permisos mínimos para consultas de catálogo. No se utilizará una clave `service_role` o secret para lecturas ordinarias.

## 3. Catálogo: esquema conceptual mínimo (no son registros reales)

**`services` (campos propuestos, no información institucional):**

| Campo | Para qué sirve | Restricción |
|---|---|---|
| `id` | Identificador inmutable utilizado por Gemini | Único; no lo inventa el usuario. |
| `scope` | `FISI` o `CENTRAL_UNMSM` | Nunca atribuir un servicio central a FISI. |
| `name`, `category`, `description` | Información de identificación | Copiada de evidencia verificada. |
| `needs_tags` | Búsqueda estructurada y evaluación | Etiquetas controladas, no texto de IA libre. |
| `modalities`, `constraints` | Posibilita una ruta adaptativa | Vacíos cuando no existen datos verificables. |
| `official_steps` | Lista ordenada de pasos comprobados | Solo fuente documentada. |
| `requirements`, `contact`, `location`, `hours` | Datos accionables | `null`/«por confirmar» si no están confirmados. |
| `source_url`, `source_published_at` | Trazabilidad documental | `source_url` obligatorio para ruta accionable. |
| `reviewed_at` | Cuándo se revisó la evidencia | No implica servicio abierto. |
| `valid_from`, `valid_until` | Plazos de una convocatoria/comunicado | No inventar vigencia. |
| `evidence_status` | Verificado / histórico / por confirmar | El backend decide qué puede recomendar. |
| `availability_status` | Abierto documentado / cerrado / por confirmar | No inferir por un horario histórico. |

Se usará **una sola tabla legible y pequeña**; JSONB para listas de pasos/etiquetas si facilita el trabajo, evitando normalizaciones innecesarias durante el concurso. En el futuro podría separarse `faculties`, `sources`, `service_updates` y `procedures`, pero **no construirlo ahora**.

**Fuente de datos:** material verificado y autorizado según reglas. Si no hay permiso para llevar catálogos preparados, ingresar únicamente lo permitido al comenzar oficialmente el desarrollo. No confundir `reviewed_at` con fecha de vigencia o confirmación de disponibilidad.

## 4. Flujo de IA (contrato funcional, sin código)

### Entrada del frontend → `POST /api/route`

- `faculty_code`: `FISI`.
- `message`: descripción breve, máximo sugerido de **800 caracteres**.
- `clarification_answer`: opcional, si respondió a pregunta anterior.
- `context_summary`: opcional, breve y enviado solo para una iteración adicional.
- `asked_once`: booleano para no provocar un bucle de preguntas; **el backend no confía ciegamente** en él y debe limitar la ronda.

No permitir que el usuario defina URLs «oficiales» o IDs elegidos para forzar resultados. No almacenar una sesión permanente.

### Algoritmo lógico

1. FastAPI valida campos, tamaño y alcance; normaliza datos sin almacenar PII.
2. `Repository` recupera registros **FISI o centrales elegibles para el alumno** que tengan evidencia suficiente. Para 5–15 registros, es preferible entregar a Gemini todos los candidatos válidos que filtrar con etiquetas demasiado restrictivas que podrían ocultar un servicio pertinente.
3. Gemini recibe **solo un resumen mínimo de candidatos** (`id`, categoría, propósito, restricciones verificadas); se pide identificar necesidades, restricciones, y seleccionar de 1 a 3 IDs, o una pregunta que realmente cambie la elección.
4. Gemini responde un JSON con **enumeraciones**, `candidate_ids[]`, `need_codes[]`, `constraint_codes[]`, `reason_codes[]` y opcional `question_code`; se evita texto libre de recomendaciones institucionales.
5. Pydantic y reglas deterministas comprueban esquema, IDs dentro de la lista autorizada, restricciones explícitas, fechas y datos disponibles. Si la salida es incompatible, no se muestra como una respuesta válida.
6. El backend convierte `reason_codes` en explicaciones cortas predefinidas; añade **solo del catálogo** nombres, horarios, correos, pasos, enlaces, aviso de vigencia y situación de convocatoria.
7. Si se requiere aclaración, solo se formula **una pregunta útil**. Si responde, se reinvoca el mismo procedimiento con la respuesta; si no aporta diferencia, la ruta puede permanecer igual.
8. Si la IA está caída o devuelve JSON inválido, `modo=degradado`: listar **alternativas pertinentes conocidas por categoría/alcance** sin afirmar personalización inteligente. Si también falla Supabase, leer snapshot autorizado; si no existe snapshot, informar indisponibilidad sin inventar servicios.

### Salida del backend → frontend

- `mode`: `question` / `route` / `degraded`.
- `needs[]`, `constraints[]`: códigos o etiquetas estables.
- `question`: solo para el modo de aclaración; texto desde banco controlado de preguntas si se puede.
- `route[]`: elementos `{service_id, name, reason_label, official_steps, contact, location, hours, source_url, reviewed_at, availability_status, warning}`. **Los hechos proceden del catálogo, no del LLM.**
- `diagnostics_public`: `{ai_available, data_source, verified_only}` sin credenciales ni trazas.

**Endpoints mínimos:** `GET /api/health`, `GET /api/services`, `POST /api/route`. No exponer endpoints de escritura anónima. Para un MVP pequeño, el mismo FastAPI puede servir la carpeta estática del frontend en local; si se usa Vercel, colocar los estáticos como indique la documentación de despliegue para evitar rutas rotas.

### Seguridad semántica / alucinaciones

- **Allowlist de IDs y códigos de motivo**, no redacción libre de «hechos».
- **Validaciones en código:** alcance FISI/central, plazos, estado y campos presentes.
- **Frases controladas en UI:** «Información verificada el...», «Disponibilidad por confirmar», «Convocatoria cerrada» solo cuando el dato lo sostenga.
- **Ataques de prompt injection:** el mensaje estudiantil se trata como dato; no puede ordenar al sistema cambiar sus fuentes o revelar secretos.
- Si el modelo no elige servicio adecuado, respuesta honesta: «No tenemos una ruta suficientemente documentada».

## 5. Supabase frente a SQLite: decisión razonada

### Por qué **sí** considerar Supabase como principal

- El catálogo se puede revisar/editar desde un panel conocido sin construir administración.
- PostgreSQL es una base persistente accesible desde el backend local y desde un posible despliegue web.
- Facilita una demostración desde otra computadora y crecimiento del catálogo en una fase posterior.
- Su nivel gratuito indica una capacidad de BD de **500 MB** y dos proyectos gratuitos por cuenta/organización según documentación actual; suficiente para este MVP, pero sujeto a límites y pausa por inactividad.

### Por qué **no** hacerlo una dependencia irrenunciable

- Agrega credenciales, control de acceso, RLS, red y un servicio remoto que puede fallar.
- Para un catálogo de 5–15 registros, no aporta mejoras a la calidad de la IA por sí solo.
- No se justifica si al iniciar el concurso todavía no se comprobó una lectura segura.

### Política de selección (antes y durante la hackathon)

- **PREPARACIÓN:** cuentas y proyecto accesibles, lectura validada, RLS activado, solo SELECT publicable; **sin código del concurso**.
- **09:45:** primer endpoint de servicios funcionando desde `Repository`. Si Supabase retrasa el flujo, conmutar a lectura de instantánea verificada.
- **10:30:** si el flujo sin IA no es demostrable, recortar interfaz/deploy y priorizar consulta + tarjetas.
- **No cambiar de tecnología después de las 12:15** salvo bloqueo crítico que obligue a fallback.

### Protección de Supabase

- Habilitar **RLS** para cualquier tabla expuesta en `public` y comprobar tanto **GRANTS como políticas**: permitir SELECT de filas publicables y denegar INSERT/UPDATE/DELETE desde roles anónimos.
- Usar **publishable key** en backend, aunque no sea un secreto privilegiado; ninguna `service_role`/secret key en frontend ni en la app ordinaria.
- Cargar el catálogo desde dashboard con permisos de administrador, no mediante un endpoint web público.
- No incluir historial del usuario, mensajes o datos personales en PostgreSQL.
- Comprobar con consulta real que `anon` puede leer solo lo previsto e **intentar una escritura de prueba controlada** que debe ser denegada.

**Documentación:** https://supabase.com/docs/guides/database/secure-data ; https://supabase.com/docs/guides/database/postgres/row-level-security ; https://supabase.com/pricing

## 6. Herramientas del equipo y librerías

| Componente | Paquete / herramienta | Responsable | Condición |
|---|---|---|---|
| Servidor | `fastapi`, `uvicorn`, `pydantic` | José | Obligatorios. |
| IA | `google-genai` | Paolo | API key y modelo probados. |
| Supabase | `supabase` (SDK Python) | José | Si Supabase pasa la compuerta; alternativa instantánea JSON. |
| Configuración | `python-dotenv` | José | Solo local; `.env` excluido de Git. |
| Pruebas | `pytest`, `httpx` / TestClient | Paolo + José | Obligatorios para los casos críticos. |
| Calidad | `ruff` | Quien lo tenga disponible | Opcional; no bloquear entrega. |
| Frontend | HTML/CSS/JS sin framework | Daniela | Evitar Node/npm si no son imprescindibles. |
| Git | Git + GitHub Desktop | Todos | Repositorio único y ramas pequeñas. |
| IA de apoyo | ChatGPT Plus, Claude Free, Gemini web, Cursor Hobby | Todos | Ayudan a producir/revisar, **no son piezas del producto**. |
| Evidencia | OBS o grabador del sistema | Paolo + Daniela | Video real de ejecución, no prueba automática. |

**Gemini:** `gemini-3.5-flash-lite` figura documentado como modelo estable y con salida estructurada, pero ello **no acredita la disponibilidad ni cuota de la API de su cuenta**; comprobarlo en Google AI Studio. Los límites pueden aplicar por proyecto. Usar solo textos ficticios y no salud mental sensible. https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite

**Cursor Pro:** no es requisito. El editor puede seguir utilizándose con límites del modo gratuito; si se acaban llamadas de IA, continuar en VS Code/Cursor como editor y consultar ChatGPT/Claude por módulos pequeños.

## 7. Reparto final de trabajo y contrato de integración

| Persona | Dueño de | Entregable que acepta integración | Fuera de su responsabilidad primaria |
|---|---|---|---|
| **José** | FastAPI, Pydantic, `Repository`, seguridad de datos, Git merge, elección de deploy | `/api/services` y `/api/route` con datos y respuestas válidas | No escribir todas las pantallas, no construir el prompt principal. |
| **Paolo** | `GeminiAdapter`, prompt/JSON estructurado, casos adversos y guía de demo | Función conceptual `analyze(context, candidates) -> AIResult` que José pueda invocar; manejo de timeout/error | No editar lógica de BD ni rutas del frontend por su cuenta. |
| **Daniela** | UI y estados, tarjeta de fuente, manejo de loading/error, móvil | Formulario → pregunta → ruta / degradado, usando contrato conocido | No llamar Gemini ni Supabase desde navegador. |
| **Coach externo** | Revisión crítica/ensayo, si está autorizado | Observaciones, no componente obligatorio | No asumir rol de desarrollador oficial. |

**El contrato se acuerda en los primeros 30 minutos:** nombres exactos de campos, modos de respuesta, estructura de tarjeta y códigos de motivo. Daniela empieza con respuestas simuladas **creadas el mismo día**; después reemplaza el mock por `fetch` a la API. Paolo trabaja con candidatos simulados **del evento**, y José integra ambos módulos. Evitar que dos personas editen el mismo archivo simultáneamente.

## 8. Git y despliegue: cómo trabajar y publicar

1. Abrir **un nuevo repositorio** al iniciar el tiempo permitido; tres colaboradores; `main` siempre demostrable.
2. Una rama por dueño: `feature/jose-api`, `feature/paolo-ai`, `feature/daniela-ui`.
3. Repositorio con áreas conceptuales `/backend`, `/frontend`, `/data`, `/tests`, `/docs`; la estructura concreta se crea en el concurso.
4. `.gitignore` antes del primer commit: `.env`, entornos virtuales, claves, respaldos privados, caches. **Nunca** enviar secrets ni token a la IA para debugging.
5. Commits pequeños, pull antes de cambiar, revisión mínima del diff y merge por José en puntos fijos **10:00**, **12:15** y **14:40** (adaptables según progreso).
6. Si hay conflicto, una persona lo resuelve y los demás paran de tocar esos archivos. No `force-push` a `main`.

### Local vs web

- **Obligatorio:** demo local en la laptop de exposición, con FastAPI sirviendo interfaz y API, fuente de datos disponible y flujo de IA si hay conexión.
- **Condicionado:** Vercel puede hospedar FastAPI en una función Python y servir estáticos, pero exige comprobar importación, dependencias, variables, rutas y errores reales. Hacer una prueba pequeña temprano si está autorizado; **abortar despliegue si consume más de 30 minutos o amenaza el MVP**.
- **No** guardar escritura persistente en el filesystem de funciones Vercel.
- **Defensa:** una URL pública es un plus, **no reemplaza una demo local estable**. Enviar únicamente los entregables exigidos por las bases.

**Fuentes oficiales:** https://vercel.com/docs/frameworks/backend/fastapi ; https://vercel.com/docs/functions/limitations ; https://github.com/pricing

## 9. Pruebas y aceptación (QA real)

**Automatizadas, con Gemini reemplazado por respuesta falsa durante las pruebas:**

1. Mensaje vacío o mayor al límite → error controlado.
2. Modelo devuelve servicio ID inexistente → no se muestra.
3. Modelo intenta inventar horario/contacto en texto → no se representa, porque la UI solo imprime hechos del catálogo.
4. Respuesta JSON inválida → `degraded` sin caída.
5. Timeout/429 de Gemini → `degraded` con aviso veraz.
6. Supabase falla → snapshot local verificado si existe; de lo contrario, indisponibilidad transparente.
7. Convocatoria vencida o atención por confirmar → no aparece como oferta abierta.
8. Registro de otra facultad → nunca se muestra como servicio FISI.
9. Entrada con «ignora instrucciones» → no altera catálogo/IDs permitidos.
10. Intento de INSERT/UPDATE anónimo en Supabase → rechazado.

**Pruebas manuales:** ventana normal e incógnita, pantalla móvil, navegación por teclado básica, links oficiales, recarga, consola sin errores JS, panel Network sin llamadas del navegador a Gemini ni secretos expuestos, demo desde laptop con proyector/HDMI.

**Criterio de aceptación:** un flujo completo real + 3 escenarios válidos + 2 fallos controlados + exposición de fuentes + sin secretos en Git + captación real en OBS. La IA revisora ayuda a localizar errores; **no certifica que pasaron las pruebas**.

### Calidad mínima para el jurado

- **Funcionamiento:** el núcleo no depende de que una tercera persona introduzca datos mientras se presenta.
- **IA demostrable:** pregunta/adaptación justificada, no sólo un «buscador con IA».
- **Trazabilidad:** cada tarjeta muestra fuente y advertencia; ninguna cifra de impacto sin medición.
- **Seguridad:** sin credenciales y sin solicitudes personales almacenadas.
- **Transparencia:** piloto estudiantil, **sin aval o integración oficial de UNMSM**.

## 10. Cronograma del sábado con compuertas

| Hora | Meta observable | Dueño |
|---|---|---|
| **08:30–09:00** | Repo nuevo, .gitignore, contrato API, criterio de elección Supabase/snapshot | Todos; José decide la integración. |
| **09:00–10:00** | Daniela: UI con mock. José: GET catálogo y backend. Paolo: Gemini devuelve JSON básico. | Trabajo paralelo. |
| **10:00** | Merge 1: catálogo → tarjetas con fuentes sin IA. | José |
| **10:00–11:15** | IA por ID + reglas + primera ruta real, sin aclaración si aún falla. | Paolo + José |
| **11:15–12:15** | Aclaración si diferencia decisiones y demo adaptativa; merge 2. | Equipo |
| **12:15–13:00** | Flujo extremo a extremo; tres casos; primer video corto si está listo. | Equipo |
| **14:00–14:40** | Tests adversos, permisos RLS, secrets, responsive. | Paolo + Daniela + José |
| **14:40** | Merge 3; última versión estable, decidir deploy si no amenaza tiempo. | José |
| **14:40–15:25** | QA final, diapositivas y grabación OBS de 1–2 tomas. | Paolo + Daniela |
| **15:25–15:30** | Paquete técnico listo; revisión de repositorio. | José |
| **15:30–16:00** | Reserva de entrega; no introducir nuevas funciones. | Todos |

**Cortes de alcance:** si a las 10:30 no hay catálogo → snapshot, no Supabase. Si a las 12:15 no hay selección IA de punta a punta → quitar aclaración y garantizar una sola ruta válida. Después de 14:00 **solo correcciones**. El equipo no debe gastar el cierre en desplegar a Vercel si todavía hay fallos en el MVP.

## 11. Respuestas cortas ante el jurado

- **«¿Por qué este stack?»** Python es la competencia común; el frontend es vanilla para reducir tiempo; FastAPI permite módulos y pruebas.
- **«¿Qué arquitectura usan?»** Cliente-servidor de tres capas, monolito modular con repositorio intercambiable; una sola unidad desplegable, separando UI/lógica/datos.
- **«¿Por qué Supabase?»** Permite un catálogo Postgres accesible y editable sin construir un panel administrativo. El MVP tiene snapshot de solo lectura como contingencia si falla la red.
- **«¿Por qué no SQLite?»** SQLite sería suficiente para el catálogo pequeño; escogimos Supabase por la facilidad de actualización y un posible acceso web multi-dispositivo, **no porque la IA lo requiera**. Si no se pudo configurar a tiempo, la arquitectura usa snapshot local.
- **«¿Cómo participa la IA?»** Entiende necesidades y restricciones, solicita una aclaración decisiva y propone IDs ordenados de candidatos existentes; vuelve a evaluar con nuevo contexto.
- **«¿Qué previene alucinaciones?»** El modelo elige IDs y códigos; nombres, requisitos, pasos y URLs los sirve exclusivamente el backend desde fuentes verificadas. No se promete infalibilidad semántica.
- **«¿Cómo manejan privacidad?»** No hay login ni persistencia de solicitudes; se evitan datos personales reales. El proveedor IA puede procesar la entrada y existen registros técnicos de hosting: no afirmar privacidad absoluta.
- **«¿Por qué FISI?»** Piloto delimitado; no se atribuye a FISI procedimientos de otra facultad. Escalable solo después de comprobar cada fuente.
- **«¿Qué pasa si se cae IA o BD?»** Mensaje honesto y modo informativo con snapshot de catálogo cuando exista; nunca un resultado fingido.
- **«¿Usaron código previo?»** No: únicamente estudio, herramientas y documentación preparatoria, según las reglas; se debe confirmar permiso de importar datos.

## 12. Decisiones pendientes, sin bloquear el diseño

- **Autorización de la organización:** uso de herramientas de IA para programar, coach externo, importar datos estructurados preexistentes y entregables exactos. La penalización histórica de -15 puntos por código previo hace imprescindible aclararlo.
- **Fuente de datos efectiva:** decidir entre Supabase y snapshot según prueba concreta; *no* se supone preparada ninguna ruta de FISI en este documento.
- **Gemini:** API key, modelo disponible y límite por proyecto deben verificarse en Google AI Studio.
- **Vercel:** URL opcional según estabilidad, no prometerla de antemano.
- **Coordinación del equipo:** quién mantiene la laptop de la demo, acceso al repo y respaldos.

## 13. Fuentes técnicas verificables y referencias del equipo

**Documentación de producto:**

- Supabase, *Securing your data*: https://supabase.com/docs/guides/database/secure-data
- Supabase, *Row Level Security*: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase, *Pricing*: https://supabase.com/pricing
- Google, *Gemini 3.5 Flash-Lite*: https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
- Vercel, *FastAPI on Vercel*: https://vercel.com/docs/frameworks/backend/fastapi
- Vercel, *Functions limitations*: https://vercel.com/docs/functions/limitations
- GitHub, *Pricing*: https://github.com/pricing

**Referencias de planificación anteriores:** `CONECTA_UNMSM_CONTEXTO_MAESTRO_2026.md`; `CONECTA_UNMSM_PLAN_TECNICO_OPERATIVO_2026.md` (v1); `CONECTA_UNMSM_DECISIONES_TECNICAS_v2.md`. Esta versión v3 sustituye las decisiones técnicas sobre base de datos, explicaciones IA y compuertas de despliegue. **No sustituye las reglas oficiales ni incorpora resultados de investigación/entrevistas.**

---

### Prompt operativo breve para el asistente de cada integrante

> Eres el CTO revisor de CONECTA UNMSM. Usa `CONECTA_UNMSM_PLAN_OPERATIVO_v3_2026.md` como decisión técnica vigente y el contexto maestro como historial. Eje Bienestar Universitario; piloto FISI; tres desarrolladores (José API/datos, Paolo IA/QA, Daniela frontend/UX), 6,5 horas, Code Freeze 16:00. La killer feature es una ruta de bienestar adaptativa basada en servicios verificables. Arquitectura monolítica FastAPI + frontend vanilla + Gemini + Repository (Supabase principal condicionado / snapshot de contingencia). No generar código previo al evento. No inventar contactos, requisitos, horarios o disponibilidades. Si propones un cambio, indica el beneficio, costo en tiempo y riesgo, y si altera un acuerdo ya cerrado. En QA, diferencia «revisado» de «probado mediante ejecución». TAREA ACTUAL: [escribir solicitud específica].
