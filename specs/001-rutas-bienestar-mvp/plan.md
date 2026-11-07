# Plan técnico — Spec 001 Conecta UNMSM

**Estado:** PROPUESTO; deriva de `spec.md` y `docs/constitution.md`. No es código. La fuente canónica del esquema HTTP es `docs/api-contract.md`; la del catálogo, `docs/catalog-contract.md`.

## 1. Arquitectura
**Monolito modular en capas (cliente-servidor)**, con despliegue local preferente para la demo.

```text
Navegador: HTML / CSS / JavaScript (Daniela)
                 │  GET /api/services, POST /api/route
                 ▼
FastAPI: transporte HTTP, validación Pydantic (José)
                 │
                 ▼
Servicio de rutas: casos, estados, validaciones (José)
       ├──► CatalogRepository (José)
       │       ├── Supabase/PostgreSQL (principal CONDICIONAL)
       │       └── JSON local validado (contingencia)
       └──► GeminiAdapter (Paolo)
                 │
                 └── 1 llamada por turno / salida estructurada
                 ▼
Validador y presentador: ids + códigos permitidos (José)
                 │
                 ▼
Respuesta tipada: question / route / degraded (Daniela)
```

**No es un sistema de agentes autónomos ni RAG vectorial.** Se recuperan candidatos desde registros controlados y la IA realiza comprensión/selección dentro de ese conjunto. La lógica de negocio impide inventar información.

## 2. Estructura prevista del código (SOLO futura)
```text
conecta-unmsm/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI, sirve static y API
│       ├── api.py              # rutas HTTP, conversión de errores
│       ├── schemas.py          # modelos de request/response
│       ├── route_service.py    # orquestación de flujo y estados
│       ├── repository.py       # contrato CatalogRepository
│       ├── supabase_repo.py    # adaptador remoto opcional
│       ├── local_repo.py       # instantánea local de solo lectura
│       ├── ai_adapter.py       # Gemini: SOLO IDs/códigos
│       ├── validator.py        # allowlist y reglas deterministas
│       └── config.py           # configuración/secretos de entorno
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/
│   └── catalog.snapshot.json  # registro verificado SOLO si autorizado; nunca inventado
├── tests/
│   ├── test_api.py
│   ├── test_routes.py
│   ├── test_ai_contract.py
│   ├── test_catalog.py
│   └── test_security.py
├── requirements.txt
├── .gitignore
└── [documentación SDD ya descrita]
```
No crear carpetas/archivos `.py/.js/.html` de este árbol antes de la autorización de programación. Si una dependencia demora, fusionar módulos manteniendo separadas sus responsabilidades.

## 3. Modelo de datos
Consultar `docs/catalog-contract.md`: cada servicio con ID, alcance FISI/CENTRAL, categoría, necesidades, pasos documentados, contactos, fuente, estado y fecha. Tipos opcionales para transporte: zona norte/sur/centro/este, paradas/hora **solo si existen evidencias**. **Una oficina no equivale automáticamente a un servicio**.

**Ejemplos de esquema son ficticios.** No copiar el inventario histórico de otras facultades y atribuirlo a FISI. La carga de registros será tarea posterior al aporte de datos por el usuario, previa confirmación de reglas de concurso.

## 4. Interfaz y estados
- **Inicio:** selector FISI (único en piloto), descripción (máx. 800 caracteres), aviso «No introduzcas datos personales sensibles».
- **Enviando:** estado de carga con posibilidad de reintentar de forma segura.
- **Pregunta:** una pregunta y campo de aclaración (≤400); tras responder, no volver a preguntar.
- **Ruta:** hasta 3 tarjetas ordenadas; nombre, categoría, explicación por plantilla, pasos, fuente, estado y advertencias.
- **Degradado:** mostrar catálogo elegible no personalizado y motivo del límite; no usar distintivo «IA procesó».
- **Sin datos:** explicación de falta de información oficial; no inventar recomendaciones.
- **Reevaluación:** modificar mensaje/restricción y reconsultar; la ruta anterior no es autoridad sobre la nueva.

## 5. Contrato de API
`docs/api-contract.md` es la **fuente única**: `GET /api/health`, `GET /api/services`, `POST /api/route`. Mode = `question|route|degraded`.

El frontend **no** contacta a Gemini/Supabase con credenciales privilegiadas y **no** decide la elegibilidad de servicios. La lógica de seguridad pertenece al servidor.

## 6. Algoritmo de enrutamiento propuesto (pseudocódigo no ejecutable)
```text
VALIDAR la descripción y el ámbito FISI
CARGAR candidatos elegibles por FISI + servicios CENTRALES aplicables
SI fuente remota falla, usar snapshot autorizado e informar su origen
SI no hay candidatos válidos, devolver 'sin datos'
ENVIAR a Gemini texto + contexto + candidatos compactos
SI hay aclaración decisiva y no se usó antes, devolver pregunta única
SINO recibir IDs seleccionados + códigos de razón
VALIDAR cada ID contra la lista entregada; eliminar duplicados y excedentes
RECUPERAR cada ficha institucional del repositorio
COMPONER explicación con plantillas y datos validados
DEVOLVER tarjetas + advertencias + origen y fecha del catálogo
ANTE fallo IA: devolver modo degradado; nunca fabricar rutas
```
**Cuidado:** como el catálogo es pequeño, evitar filtrar demasiado por palabras antes de mandar candidatos al LLM; se podrían excluir necesidades implícitas. En la primera versión enviar **todos** los elegibles por ámbito y estado, compactados, si cabe en presupuesto. Ajustar solo si los datos lo exigen.

## 7. IA / contrato interno
Gemini interpreta **necesidades múltiples**, identifica restricciones (horario, modalidad, zona de transporte), decide si una pregunta cambia la ruta y propone IDs ordenados con reason codes de una enumeración finita. Respuesta estructurada y validada con Pydantic. El backend **NO** muestra prosa institucional libre generada por LLM.

### Códigos internos de razón
- `matches_need`: responde a la necesidad expresada.
- `matches_modality`: modalidad documentada compatible.
- `matches_location`: ámbito o zona documentada pertinente.
- `requires_confirmation`: hay una incertidumbre que el usuario debe comprobar.

Las explicaciones de UI se generan con **plantillas seguras**, no con frases libres que puedan prometer beneficios. Si no existe justificación validada, no mostrar una explicación inventada.

### Duración del ciclo
Una llamada por **turno**; dos turnos como máximo si hay una única aclaración. Timeout objetivo del proveedor ~10 s para el primer intento; sin bucles de reintentos indefinidos. Las cuotas, modelo y key deberán probarse en Google AI Studio. No prometer latencias garantizadas.

## 8. Repository / selección Supabase o local
- `CatalogRepository.list_eligible(scope)` + `get_by_ids(ids)` como interfaz interna.
- Fuente primaria **Supabase PostgreSQL, solo lectura, RLS probado**, si la cuenta/infra están listas antes del evento. No usar service-role key en navegador ni API pública.
- Alternativa mínima `LocalCatalogRepository` de **JSON validado de solo lectura**, con fecha de copia, si Supabase falla o no está listo.
- Si los datos locales son viejos, aviso visible. No se simula estado `abierto ahora`.
- **No hace falta SQLite** para un catálogo tan pequeño; puede incorporarse más adelante sin cambiar el motor.
- No se construye un panel administrativo. La modificación de contenido se hará fuera de la app, por personas autorizadas y según reglas del evento.

## 9. Librerías previstas, solo cuando se permita programar
- `fastapi`, `uvicorn`, `pydantic` — API y contrato.
- `google-genai` — Gemini.
- `supabase` — solo si se usa la fuente Supabase.
- `python-dotenv` — desarrollo local, sin comprometer `.env`.
- `pytest`, `httpx` — tests de backend con TestClient.
- Frontend: HTML/CSS/JS nativos, sin build, sin React.
- Sin LangChain, LangGraph, FAISS, ORM pesado, Docker ni SDK frontend de IA.

## 10. Seguridad y privacidad
1. API key Gemini solo en servidor, en variables de entorno; sin claves en repositorio ni logs.
2. Nunca almacenar ni transferir intencionalmente DNI, nombre real, correo personal, historial clínico, etc. La pantalla advierte no ingresarlos, pero **no afirma poder evitar que un usuario los escriba**. El proveedor externo puede procesar la consulta; usar demos ficticias.
3. Catálogo público de lectura; RLS deniega escrituras anónimas en Supabase. Si se usa backend con key publicable, limitar privilegios.
4. Backend valida límites, estados, IDs, scope y esquema, aun si el modelo/cliente es malicioso.
5. Frontend escapa contenido; no usa `innerHTML` con entrada o salida de LLM.
6. Mensajes de error no publican stack traces ni secretos.
7. No diagnosticar ni usar la IA para decidir emergencias clínicas.

## 11. Test y trazabilidad
- Tests unitarios por RF de `spec.md`: ID permitido/inexistente, facultad, ausencias, estados, selección de candidatos, falta de datos, texto adversario.
- Tests de integración API con IA simulada (no cuotas reales para cada test).
- Prueba manual real con Gemini, Supabase y fallback; documentar qué se ejecutó.
- UI prueba estados question/route/degraded con respuestas simuladas **claramente marcadas como tales durante desarrollo**.
- QA matriz canónica: `docs/qa-matrix.md`.
- No declarar un RF cubierto por el solo hecho de que la IA escribió el código.

## 12. Riesgos y cortes
| Riesgo | Mitigación | Momento para recorte |
|---|---|---|
| Demora en Supabase/RLS | Repository local | Antes de iniciar o en primera hora |
| Sin datos reales adecuados | Mostrar solo catálogos documentados o límites; NO inventar | Antes de demo |
| Gemini inaccesible o agotado | Modo degradado y video auténtico si existe | En cuanto se detecte |
| Desacuerdo de contrato | Fijar `api-contract.md`; mock común | 08:30–09:00 |
| Diseño tardío | Priorizar flujo funcional antes de estilos | Si sin flujo a las 11:00 |
| IA tardía | Hacer ruta básica primero; aclaración opcional | 12:15 |
| Demasiado trabajo | No añadir features después 14:00 | 14:00 |

## 13. Relación con requisitos
| Módulo | RF principales |
|---|---|
| Frontend | RF-01, 02, 05–09, 11–12, 16–18, 21 |
| API / validación | RF-01, 02, 04, 06–08, 13, 16, 20, 22 |
| Servicio de rutas | RF-03, 05–09, 13–17, 19 |
| Repository | RF-08, 10–15, 17, 19 |
| GeminiAdapter | RF-03, 05, 06, 08, 09, 18 |
| Tests y seguridad | RF-02, 04, 06, 07, 10–22 |

## 14. Pendiente de aprobación
- Spec y contrato API aceptados por los tres integrantes.
- Datos institucionales reales se adjuntarán después (entrevistas suspendidas temporalmente).
- Tras confirmación de bases, definir si documentación preparatoria y dataset podrán incorporarse al repo del día de desarrollo.


## Adenda LABORATORIO v3 — alcance interfacultades y BD (6/11/2026)

- **RF-23 a RF-25:** `frontend/index.html` pregunta ámbito; `frontend/app.js` lo envía en cada turno; `api.py` valida código; `repository.py` limita a FISI+CENTRAL o solo CENTRAL universal si la facultad difiere. El campo nuevo `accessible_to_all_faculties` vive en `schemas.py`, SQL y JSON.
- **RF-26:** `SupabaseCatalogRepository` lee columnas tipadas de `services` utilizando publishable key con RLS; al fallar vuelve a JSON, sin ofrecer resultados falsos. Scripts de SQL en `supabase/`.
- **IA:** `GeminiAdapter` usa un modelo configurable (v3 propone `gemini-3.5-flash-lite`); `question_code` solo elige textos de un banco controlado. Siempre valida IDs contra el catálogo filtrado y jamás compone datos institucionales.
- **Tests:** ejecución offline de esquema/API/selección, más comprobación manual pendiente con Google AI Studio y una instancia Supabase propia. No hay autorización de datos reales en estos tests.
