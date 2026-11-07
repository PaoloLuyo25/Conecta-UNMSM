# Conecta UNMSM — ampliación funcional y decisiones de arquitectura (v4)

**Fecha:** 6 de noviembre de 2026  
**Estado:** propuesta técnica SDD para el **laboratorio**, pendiente de aprobación e implementación. **No** es un reporte de funciones ya programadas.  
**Destino dentro del proyecto:** `docs/actualizaciones-sdd-v4.md`  
**Base:** `prompt_conecta_unmsm.md`, constitución y contratos del laboratorio v3, esquema FastAPI/JavaScript/Supabase/Gemini existente.

> **Alcance y honestidad:** Este documento especifica qué cambiar, cómo integrarlo, por qué se elige esa solución y cómo verificarla. La copia v3 examinada procede del paquete del laboratorio; no se debe sobrescribir la versión local más reciente que ya superó la prueba real de Gemini con un esquema estructurado corregido. No se han aplicado estos cambios al código operativo ni ejecutado pruebas de v4.

## 0. Resultado de la evaluación

| Requerimiento | Decisión | Cómo se agrega | Justificación técnica |
|---|---|---|---|
| Comprensión de `nte` → `norte` y otras variantes | **Sí, con límites** | Normalizador determinista antes de Gemini; abreviaturas controladas y coincidencia difusa de alta confianza | Reduce latencia, costo y alucinaciones. No delega información geográfica al modelo. |
| Distritos | **Sí, condicionado a la fuente** | Lector y validador de un único archivo Markdown canónico; ningún distrito escrito a mano en el código | Permite rastrear cambios y prohíbe inferir cobertura geográfica. **No se recibió el listado de distritos:** el MD adjunto solo lo menciona. |
| Botón «Nueva consulta» | **Sí** | Reinicio integral del estado frontend, formulario, resultados y petición en vuelo | El usuario empieza de cero sin resultados obsoletos; no cierra sesión ni elimina el historial guardado. |
| Loading atractivo | **Sí** | Spinner CSS en el botón, bloqueo de doble envío, accesibilidad y manejo de errores | Da respuesta visual inmediata sin exponer etiquetas técnicas como «Sin IA». |
| Retirar «ACCESO A AYUDA HUMANA» | **Sí, en la UI solicitada** | Eliminar HTML, eventos JS, CSS y prueba asociada | Evita una sección que el equipo excluyó del flujo. No cambia la prohibición de diagnóstico/triaje clínico del backend. |
| Historial de rutas | **Sí, opcional y mínimo** | Registro de IDs de servicios seleccionados, usuario, fecha y origen del catálogo; nunca consulta textual completa | Habilita seguimiento sin conservar necesidades económicas, médicas o personales en texto libre. |
| Identificación de usuario | **Sí para historial individual; no para consulta pública** | Supabase Auth por correo y código temporal (OTP); sesión bajo control del backend | Permite asociar, consultar y borrar historiales de manera aislada sin crear otro sistema de contraseñas. |
| Seguridad y pruebas | **Obligatorias** | RLS por propietario, endpoints protegidos, tests de normalización, UI, autenticación y dos usuarios | Un historial sin aislamiento puede exponer información privada. |

### Decisiones transversales

1. **Mantener el monolito modular**: HTML/CSS/JS → FastAPI → repositorios/normalización/Auth → Supabase y Gemini. No introducir microservicios ni un frontend nuevo.
2. **No cambiar el papel de Gemini**: interpreta intención y propone únicamente IDs/códigos válidos. Los distritos y los datos institucionales siguen siendo responsabilidad del backend y de las fuentes autorizadas.
3. **Separar consulta e historial**: navegar y obtener rutas sigue siendo posible sin iniciar sesión; guardar y recuperar un historial exige cuenta verificada y consentimiento explícito.
4. **No guardar textos privados por defecto**: una ruta guardada es una referencia a servicios, no un expediente ni una evaluación de la condición personal.
5. **No confundir identificación y matrícula**: verificar un correo establece control de ese correo, **no demuestra** que el usuario sea alumno de la UNMSM. Si en el futuro se requiere verificación institucional, será una decisión y un procedimiento nuevos.
6. **No introducir datos ni código preexistentes en la competencia** sin revisar sus bases. Las modificaciones propuestas corresponden al laboratorio SDD.

## 1. Compatibilidad con la constitución y registro de decisiones

**Conflicto detectado:** la constitución vigente prohíbe conservar información sensible real y el ADR-10 excluye autenticación, escritura pública e historial; el ADR-11 difiere el historial. La solicitud v4 cambia esos supuestos. No se debe tratar el nuevo alcance como si ya estuviera aprobado por la constitución.

### Propuestas de ADR (estado: PENDIENTE DE APROBACIÓN)

| ID propuesto | Decisión | Sustituye/complementa | Riesgo nuevo | Mitigación |
|---|---|---|---|---|
| ADR-17 | Normalización controlada y catálogo Markdown de distritos como autoridad exclusiva | Complementa ADR-07 y esquema de transporte | Interpretación errónea de abreviaturas | Aliases explícitos, umbral, ambigüedad → aclaración; tests negativos. |
| ADR-18 | Rediseño de formulario: reinicio, carga y supresión del bloque de urgencia | UI actual | Peticiones que finalizan después del reinicio; pérdida de mensajes accesibles | `AbortController`, identificador de solicitud, `aria-live`, mensajes de error comprensibles. |
| ADR-19 | Supabase Auth OTP para historial opcional y titularidad | **Modifica ADR-10 y ADR-11** | Exposición de sesiones, acceso entre usuarios, dependencia del correo | Cookies seguras, comprobación de identidad, RLS, rate limit y pruebas con dos usuarios. |
| ADR-20 | Historial mínimo y borrable, sin texto libre | **Complementa/modifica cláusula 6 de constitución** | Inferencias de situaciones personales a partir de categorías | Opt-in, mínimo de columnas, retención limitada, RLS y borrado. |

**Flujo de aprobación SDD:** actualizar constitución (solo el alcance permitido), `spec.md` → `plan.md` → ADR → contratos de API/catálogo → tareas → código → pruebas. Aprobación conjunta del equipo antes de migraciones de persistencia; en el laboratorio los cambios siguen siendo experimentales.

## 2. RF-17 — Normalización semántica segura

### Comportamiento exigido

- Entrada `nte` → zona normalizada `norte` **cuando el contexto es transporte o una respuesta a la pregunta de zona**.
- Acentos y mayúsculas no cambian el significado: `NÓRTE` → `norte`.
- Errores tipográficos **inequívocos** de un vocabulario cerrado podrán corregirse: `nrotE` → `norte` si supera el umbral fijado.
- Si existen dos interpretaciones plausibles, **no seleccionar silenciosamente una**: devolver `ambiguous` y solicitar la aclaración permitida.
- Un distrito no listado en la fuente Markdown no se inventa ni se asigna a una zona por cercanía aparente.
- La normalización no modifica las reglas de elegibilidad por facultad, vigencia o disponibilidad.

### Diseño de procesamiento

```text
RouteRequest validado (máx. 800 caracteres)
      │
      ▼
normalize_input.py  → Unicode NFKC, acentos, espacios, tokens
      │
      ├─ alias exacto permitido (ej.: nte → norte)
      ├─ vocabulario cerrado + similitud conservadora
      └─ ambiguo/desconocido → no corregir a ciegas
      │
      ▼
districts.py → busca solo en la fuente .md validada
      │
      ▼
RouteService → filtra facultad/servicios como siempre
      │
      ▼
GeminiAdapter → texto contextual controlado + IDs elegibles
      │
      ▼
validator.py → valida IDs/códigos (sin confiar en Gemini)
```

**Cómo:** módulo puro `backend/app/normalization.py` con una función que devuelve `NormalizedQuery(original_text, intent_tokens, region_code, district_id, confidence, ambiguous)`; las coincidencias de distrito se resuelven en el módulo de distritos, no dentro de Gemini. En caso de respuesta `clarification_answer="nte"`, aplicar normalización también a esa respuesta. Pasar al LLM un contexto canónico separado del texto original; nunca sustituir sin trazabilidad la consulta del usuario.

**Por qué así:** un diccionario de aliases + coincidencia limitada a 4 zonas conocidas es más predecible que pedirle al modelo que adivine topónimos. Una corrección difusa global podría cambiar nombres de personas, distritos o necesidades. Mantener un umbral de confianza alto y tests de falso positivo es preferible a «corregir todo».

**Alternativa descartada:** corrección exclusivamente con Gemini: aumenta dependencia del proveedor y no ofrece garantías de reproducibilidad. También se descarta añadir bibliotecas de fuzzy matching de entrada; `difflib` de Python basta para el vocabulario breve. Si más adelante aparecen muchos topónimos, evaluar rendimiento sin cambiar esta política.

**Caso especial:** `nte` en un mensaje completamente aislado puede interpretarse como `norte` solamente si el flujo pendiente es una aclaración de región; en una consulta nueva aislada, primero se requiere identificar que habla de transporte o pedir contexto. Esto evita inventar la necesidad del estudiante.

## 3. RF-18 — Distritos: un solo Markdown como fuente de verdad

### Estado de la fuente

El archivo adjunto `prompt_conecta_unmsm.md` **no incluye distritos, relaciones distrito-zona ni aliases**. No se encontró un catálogo de distritos en los documentos revisados del laboratorio v3. Por ello **no es posible incorporar ni probar una asignación real de distritos** todavía. Se define la integración sin completar el catálogo con memoria, Internet ni suposiciones.

### Contrato de incorporación

- Ubicación propuesta del archivo fuente cuando el equipo lo entregue: `data/distritos_verificados.md`.
- Única autoridad de nombres oficiales, aliases y correspondencias explícitas entre distritos y zonas: ese archivo.
- **No reescribirlo** para acomodarlo al parser. Primero inspeccionar su estructura real; después crear un lector compatible con sus encabezados/tablas originales.
- `backend/app/districts.py` carga y valida al inicio. El resultado es una colección inmutable en memoria para esa ejecución.
- Validaciones técnicas, no geográficas: nombres vacíos, duplicados normalizados, aliases ambiguos, zonas fuera de `norte/sur/centro/este` y filas mal formadas generan error de carga; **nunca se «corrige» la fuente automáticamente**.
- Si el documento contiene solo una lista de distritos sin correspondencia de zonas, la app podrá **reconocer distritos**, pero **no deducir una ruta geográfica**. Si no ofrece aliases, tampoco inventarlos.
- Cambios de fuente requieren revisión de diff, fecha/versión y reejecución de tests. Si falta la fuente, las consultas por distrito dan un aviso de «zona por confirmar» sin crear una ruta.

**Por qué no usar una API geográfica externa:** contradiría la decisión de utilizar un único `.md` verificado y podría mezclar nomenclaturas o límites territoriales de distintas fuentes. Los distritos son un contexto de búsqueda; **no permiten inventar paradas, horarios, costos ni tiempos de llegada**.

### Contrato funcional sugerido (no presupone columnas existentes)

```python
# Interfaz, no implementación aprobada del parser:
class DistrictDirectory:
    def lookup(self, text: str) -> "DistrictMatch | None": ...
    def region_of(self, district_id: str) -> "str | None": ...
    def validate_source(self) -> None: ...
```

**Pruebas obligatorias** con fixtures sintéticos basados en la estructura efectiva del Markdown: coincidencia exacta; variantes de acentos; alias expresamente documentado; duplicados; dos aliases idénticos; región ausente; zona inválida; distrito desconocido; fuente faltante y fallo seguro. **Pruebas con nombres reales solo cuando esté presente el archivo canónico.**

## 4. RF-19 — Botón «Nueva consulta»

### Diseño de UI

Agregar un botón secundario visible `type="button"`, texto **«Nueva consulta»**, contiguo al botón principal o debajo del formulario. Identificador: `id="new-query-button"`. Debe funcionar con teclado y móvil.

### Contrato de reinicio completo

Cuando se pulse:

1. Cancelar la consulta HTTP activa mediante `AbortController`, si existe.
2. Incrementar un contador de petición (`requestSequence`) para ignorar respuestas anteriores que lleguen tarde.
3. Ejecutar `form.reset()`; volver al valor predeterminado de facultad (FISI) de la vista inicial; vaciar la descripción, aclaración y restricción.
4. Limpiar `state.message`, `previousIds`, `clarificationUsed`, indicadores de loading y errores.
5. Restablecer contador `0 / 800`, tarjetas, alertas, panel de aclaración, sección de refinamiento y metadata de la consulta previa.
6. Mostrar el estado inicial amigable y enfocar el textarea.
7. **No** cerrar la sesión de autenticación ni borrar rutas persistidas: una «nueva consulta» no es un «borrar mi historial».

**Decisión:** reiniciar también la facultad al valor inicial evita reutilizar accidentalmente un alcance antiguo; al ser un prototipo FISI, el selector seguirá disponible para cambiarlo. **Riesgo:** borrado accidental del texto todavía no enviado; se considera aceptable porque es una acción explícita y el botón se distingue visualmente de «Consultar».

## 5. RF-20 — Animación de carga y estados comprensibles

**Cómo:** mantener el mismo botón principal, con spinner CSS (`.loading-spinner`) mientras la petición esté activa; conservar su anchura y una animación suave del fondo. Bloquear envío y refinamiento duplicados hasta que termine la respuesta. En caso de timeout, permitir reintento.

**Accesibilidad y conducta:**

- `aria-busy="true"` en el área de resultados durante la petición y `aria-live="polite"` en un texto exclusivo para lectores de pantalla (p. ej. «Buscando opciones»).
- Spinner oculto a lectores (`aria-hidden="true"`), etiqueta del botón «Buscando tu ruta…» durante el envío; restaurar siempre el texto normal mediante `finally`.
- Respetar `@media (prefers-reduced-motion: reduce)` para eliminar la rotación.
- No usar eternamente el spinner si falla Gemini o Supabase; el backend conserva un resultado honesto y la UI presenta mensajes entendibles como «No pudimos personalizar la consulta; puedes volver a intentarlo».
- Retirar las **etiquetas técnicas prominentes** «Procesando», «Error de IA» y «Ruta IA». La transparencia no desaparece: una nota discreta indica, si procede, «Versión de demostración», «Datos por confirmar» o «No fue posible personalizar».
- No se introduce otra llamada de IA por hacer la animación ni se alteran los tiempos de espera sin pruebas.

**Por qué spinner CSS en lugar de GIF/Lottie:** sin dependencias, carga rápida, bajo costo de mantenimiento y accesibilidad mejor controlable. **No** sustituir el mensaje de error por una animación: una falla requiere explicación y recuperación.

## 6. RF-21 — Retiro de sección no requerida

**Eliminar completamente** del documento `frontend/index.html` los elementos `.urgent-banner` y `#urgent-message`, incluyendo encabezado «ACCESO A AYUDA HUMANA», textos, botón y enlaces si los hubiera. Eliminar del `frontend/app.js` el listener `$('urgent-button')`, y de `frontend/styles.css` las reglas `.urgent-banner`, `.urgent-message` y variantes responsivas.

Actualizar `tests/test_security.py`: quitar o sustituir `test_urgent_help_works_without_ai`; añadir `test_urgent_section_not_rendered` y una prueba estática que asegure que el JS ya no consulta elementos eliminados. **No dejar event listeners para nodos inexistentes**: provocarían un error de JavaScript que puede romper el resto de la página.

**Decisión de alcance:** retirar el bloque no autoriza al asistente a hacer diagnósticos, ofrecer intervención clínica ni representar una ruta de emergencia. Las limitaciones del sistema permanecen en la lógica y en la documentación; no reintroducir el bloque bajo otro nombre.

## 7. RF-22 — Identidad de usuario: decisión arquitectónica

### ¿Es necesario crear autenticación?

**Para consultas efímeras, no.** Un estudiante puede usar el orientador sin cuenta. **Para un historial persistente vinculado a la misma persona en varios dispositivos, sí es necesaria una forma fiable de identidad**. Basarse en `localStorage`, dirección IP, cookie anónima o nombre escrito en un formulario no identifica adecuadamente a un usuario y puede exponer historiales o hacerlos irrecuperables.

### Elección

**Supabase Auth con código de un solo uso por correo (OTP)**, sin contraseña propia. Aprovecha el Supabase ya seleccionado para el catálogo y entrega un `user_id` estable. No integrar un nuevo servidor de identidad ni construir tablas de contraseñas.

**Decisión de privacidad:** el usuario solo inicia sesión si desea guardar o consultar historial. La cuenta es opcional para las rutas normales; iniciar sesión no es consentimiento para guardar automáticamente todas las consultas.

### Flujo técnico, manteniendo FastAPI como puerta de entrada

```text
Navegador (JS vanilla)       FastAPI                       Supabase
       │                       │                              │
       ├─ POST /api/auth/start ─► validar email/rate limit ─► Auth: solicitar OTP
       │                       │◄──────────────────────────────┤
       ├─ POST /api/auth/verify► verificar código ─────────► Auth: sesión
       │                       │◄──────── tokens ──────────────┤
       │◄─ cookies HttpOnly ───┤                              │
       ├─ GET /api/auth/me ────► validar sesión vigente ────► Auth
       │◄─ {authenticated} ────┤                              │
       ├─ POST /api/route ─────► consulta normal             │
       │    + save_to_history  │                              │
       │                       ├─ si hay opt-in y ruta válida ► tabla route_history
       │                       │      con JWT del usuario y RLS
       │◄─ ruta + history_saved┤                              │
       ├─ GET /api/history ────► validar identidad y RLS ────► historial propio
       └─ DELETE /api/history/{id} ──────────────────────────► borrar propio
```

**Sesión segura:** cookies `HttpOnly`, `SameSite=Lax` o `Strict` según navegación, `Secure` **obligatorio en HTTPS**; en `localhost` por HTTP, configuración de desarrollo explícita. Verificar token/usuario con Supabase o comprobación criptográfica adecuada; **nunca** confiar en el `user_id` que venga del navegador ni en un JWT decodificado sin verificar. Proteger mutaciones con comprobación de `Origin`/CSRF y límites de intentos de OTP. Los access/refresh tokens nunca deben almacenarse en `localStorage` ni registrarse en logs. Gestionar expiración, renovación, logout y revocación; no considerar terminada la funcionalidad hasta probarlo.

**Compatibilidad con el stack:** el navegador continúa hablando solo con FastAPI; el backend usa la clave publicable para Auth/RLS y la sesión del usuario al acceder a datos privados. La lectura pública del catálogo continúa igual. No usar `service_role` para operaciones ordinarias de historial; esa credencial omite RLS y aumenta el riesgo.

**Alternativas evaluadas:**

| Alternativa | Veredicto | Motivo |
|---|---|---|
| Email + contraseña casera | Descartada | Manejo de hashes, recuperación, abuso y seguridad innecesarios. |
| IP o `localStorage` como identidad | Descartada | No es identidad verificable, no sirve entre dispositivos y se pierde fácilmente. |
| Login obligatorio para consultar | Descartada | Fricción y recopilación de datos innecesarias. |
| Supabase Auth OTP opcional | **Elegida** | Reutiliza infraestructura; identidad persistente sin contraseña propia. |
| Inicio de sesión con cuenta institucional | Diferido | Depende de autorización y disponibilidad real de integración de la UNMSM. |

**Dependencias operativas:** habilitación del método OTP, plantilla de correo, límites de envío y proveedor de email con capacidad apropiada. En producción, el correo verificado no equivale a condición universitaria acreditada.

## 8. RF-23 — Historial mínimo, consentimiento y seguimiento futuro

### Qué persistir y qué no

| Dato | ¿Se guarda? | Por qué |
|---|---|---|
| `user_id` (UUID de Supabase Auth) | Sí | Titularidad controlada por RLS. |
| `route_id` (UUID), `created_at`, `expires_at` | Sí | Identificación, orden, retención. |
| `service_ids` (máximo tres) | Sí | Permite reconstruir tarjetas desde el catálogo actual. |
| `faculty_code` | Sí | Contexto de elegibilidad para revalidar al consultar el historial. |
| `catalog_source` | Sí | Distingue origen y advierte sobre demostraciones. |
| Consulta original / aclaraciones / problemas económicos / salud mental | **No** | Minimización de información potencialmente sensible. |
| Correo del usuario duplicado en historial | **No** | Ya lo gestiona Supabase Auth; evitar duplicados. |
| Distrito exacto / geolocalización / IP | **No** | No se necesita para recuperar los servicios recomendados. |
| Diagnóstico, prioridad clínica o expediente | **No** | Fuera de alcance. |

**Consentimiento:** casilla independiente **«Guardar esta ruta en mi historial»**, desmarcada por defecto; explica que se guardan solo referencias a servicios y fecha. Si se pulsa sin sesión, ofrecer acceso opcional y no guardar nada hasta que el usuario lo autorice de nuevo. Se presenta «Guardada» **únicamente tras confirmación real de Supabase**.

**Regla de persistencia:** guardar únicamente `mode='route'` con 1–3 IDs **ya validados por el backend**, nunca `mode='question'`, catálogo degradado, IDs sugeridos sin validación o rutas resultantes de fallo de IA. No bloquear la visualización de una ruta por un error de guardado; devolver `history_saved=false` y mensaje no técnico.

**Consulta de historial:** devolver IDs, fecha y servicios recuperados con el catálogo actual; revalidar por facultad, estado y vigencia. Una recomendación antigua puede haber caducado; el historial no equivale a disponibilidad actual. El usuario puede borrar una entrada o todo su historial. Una futura función de seguimiento requerirá consentimiento independiente, canal de contacto explícito, revisión de datos/privacidad y alcance definido.

**Retención recomendada para el laboratorio:** `expires_at` a 30 días; excluir caducados de las lecturas y programar purga real en la fase de despliegue (no confundir filtrado con borrado físico). Permitir eliminación inmediata a solicitud del titular y eliminación en cascada al borrar la cuenta. Los backups también deben sujetarse a la política de retención aprobada.

### Migración SQL propuesta (referencial; NO ejecutada)

Ruta: `supabase/003_route_history.sql`. **No reemplaza** `001_services.sql` ni los registros del catálogo. Ejecutar primero en un proyecto de prueba, verificar permisos/roles e integrar solo tras aprobación.

```sql
create table if not exists public.route_history (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    service_ids text[] not null,
    faculty_code text not null,
    catalog_source text not null
        check (catalog_source in ('primary', 'local_snapshot')),
    client_request_id uuid not null,
    created_at timestamptz not null default now(),
    expires_at timestamptz not null default (now() + interval '30 days'),
    constraint route_history_item_count
        check (cardinality(service_ids) between 1 and 3),
    constraint route_history_unique_request
        unique (user_id, client_request_id)
);

create index if not exists route_history_owner_created_idx
    on public.route_history (user_id, created_at desc);

alter table public.route_history enable row level security;

revoke all on public.route_history from anon, authenticated;
grant select, insert, delete on public.route_history to authenticated;

create policy "route_history_select_own"
    on public.route_history for select to authenticated
    using ((select auth.uid()) = user_id);

create policy "route_history_insert_own"
    on public.route_history for insert to authenticated
    with check ((select auth.uid()) = user_id);

create policy "route_history_delete_own"
    on public.route_history for delete to authenticated
    using ((select auth.uid()) = user_id);
```

**Límite del SQL anterior:** RLS impide leer o borrar rutas de otros usuarios, pero **no demuestra que un ID de servicio sea válido** si alguien escribe directamente en la API de Supabase con su propio token. Por tanto, FastAPI valida IDs antes de guardar y al leer; si se exige integridad de catálogo a nivel de base de datos, reemplazar `service_ids[]` por una tabla hija con claves foráneas y RLS, o por una RPC restringida y auditada. No usar un array de IDs como prueba de disponibilidad institucional. Fijar permisos de esquemas y probar el comportamiento real con cuentas distintas.

### API v4: ampliación aditiva del contrato

No renombrar los campos actuales de `/api/route` ni cambiar el esquema de Gemini que ya funciona. Añadir solo:

```json
// Solo esquema ilustrativo; quitar comentarios en HTTP real.
{
  "faculty_code": "FISI",
  "message": "Texto ficticio sobre orientación",
  "clarification_answer": null,
  "clarification_used": false,
  "previous_service_ids": [],
  "save_to_history": false,
  "client_request_id": "UUID-generado-por-el-cliente"
}
```

- Respuesta de `POST /api/route`: campos v3 intactos + `history_saved: boolean` y, si se guardó, `history_id: string | null`. Se confirma el guardado tras recibir respuesta de Supabase; la idempotencia usa `(user_id, client_request_id)`.
- `POST /api/auth/start`: solicita envío de código OTP; respuesta genérica para no enumerar correos.
- `POST /api/auth/verify`: verifica código y establece cookies seguras.
- `GET /api/auth/me`: estado de autenticación **sin exponer tokens**.
- `POST /api/auth/logout`: revoca sesión cuando sea posible y elimina cookies.
- `GET /api/history`: lista paginada del **propio** usuario, sin mensajes crudos; `401` si no tiene sesión.
- `DELETE /api/history/{route_id}`: elimina solo la ruta propia; las ajenas son inaccesibles.
- `DELETE /api/history`: opción de borrar todo el historial propio, con confirmación clara en UI.

**Reglas de seguridad:** limitar resultados y paginar; IDs UUID validados con Pydantic; `user_id` siempre procede de sesión validada; CORS cerrado salvo autorización expresa; CSRF/Origin verificado en mutaciones; respuestas y logs sin códigos OTP, claves o tokens; `429` ante abuso. La lectura de servicios públicos sigue disponible sin cuenta.

## 9. Distribución exacta de responsabilidades por archivo

**Archivo nuevo** = crear en laboratorio. **Modificar** = conservar el código que funciona y añadir una integración pequeña; en particular, mantener la corrección vigente del esquema Gemini (lista tipada de selección) y las pruebas reales del usuario.

| Ruta relativa | Acción | Responsabilidad / decisión |
|---|---|---|
| `docs/constitution.md` | Propuesta de modificación | Permitir solo el historial mínimo voluntario; mantener prohibición de guardar información sensible en texto libre. |
| `docs/architecture-decisions.md` | Añadir ADR-17 a 20 | Guardar decisiones, alternativas y riesgos. |
| `specs/001-rutas-bienestar-mvp/spec.md` | Extender o crear spec v4 | RF-17 a RF-23 y aceptación EARS; distinguir MVP original de extensión. |
| `specs/001-rutas-bienestar-mvp/plan.md` | Extender plan | Secuencia y decisiones implementables. |
| `docs/api-contract.md` | Extender contrato v4 | Campos opcionales de guardado y endpoints Auth/History. |
| `docs/catalog-contract.md` | Extender | Fuente Markdown de distritos, sin inferencias externas. |
| `data/distritos_verificados.md` | **Fuente externa pendiente** | Solo copiar el archivo realmente proporcionado, sin fabricar registros. |
| `backend/app/normalization.py` | Nuevo | Normalización pura y conservadora, aliases regionales. |
| `backend/app/districts.py` | Nuevo | Parser de estructura real del `.md` y validación. |
| `backend/app/route_service.py` | Modificar | Conectar normalización y distritos; guardado posterior a selección validada. |
| `backend/app/ai_adapter.py` | Cambio mínimo, si necesario | Recibir contexto ya normalizado; mantener el esquema funcional de Gemini. |
| `backend/app/api.py` | Modificar | Contrato v4 aditivo, no romper `POST /api/route`. |
| `backend/app/auth_service.py` | Nuevo | Envío/verificación de OTP, validación/refresco/logout y cookies. |
| `backend/app/api_auth.py` | Nuevo | Endpoints /api/auth con control de abuso. |
| `backend/app/history_repo.py` | Nuevo | Lectura, inserción idempotente, borrado por propietario; token delegado y RLS. |
| `backend/app/api_history.py` | Nuevo | Endpoints del historial y paginación. |
| `backend/app/main.py` | Modificar | Registrar routers y servicios por inyección; mantener mismo origen. |
| `backend/app/config.py` | Modificar | Banderas de habilitación, cookies y retención mediante entorno. |
| `frontend/index.html` | Modificar | Nueva consulta, spinner, pantalla Auth opcional, historial; retirar bloque de urgencia. |
| `frontend/app.js` | Modificar | Reset integral, carga, abort, opt-in, UI Auth/History. |
| `frontend/styles.css` | Modificar | Spinner y diseño accesible, quitar reglas del bloque retirado. |
| `supabase/003_route_history.sql` | Nuevo | Tabla, permisos, RLS, índices. No modificar `services` existente. |
| `tests/test_normalization.py` | Nuevo | Alias, similitud, falsos positivos, contexto. |
| `tests/test_districts.py` | Nuevo | Parser, fuente única, colisiones y errores; pruebas reales pendientes de archivo. |
| `tests/test_frontend_v4.py` | Nuevo | Ausencia de sección, presencia del botón/spinner y sin listeners muertos; complementar con prueba navegador. |
| `tests/test_auth.py` | Nuevo | OTP simulado, cookies, expiración, sesión inválida, abuso, logout. |
| `tests/test_history.py` | Nuevo | Guardado opt-in, no guardar consultas, aislamiento, idempotencia, borrado. |
| `supabase/tests/route_history_rls_test.sql` | Nuevo | Verificación PostgreSQL real con usuario A, usuario B y anónimo. |
| `tests/test_ai_contract.py` | Conservar y ampliar solo si necesario | No revertir el contrato corregido y probado con Gemini real. |

## 10. Plan de implementación en etapas y criterios EARS

| Etapa | Entrega | Requisito verificable | Estimación relativa | Estado |
|---|---|---|---|---|
| P0-A | Normalización regional | **Cuando** reciba `nte` en aclaración de zona, **debe** identificar `norte` sin consultar IA para esa equivalencia; texto ambiguo no se corrige. | Baja-media | Pendiente |
| P0-B | UI de reinicio y loading | **Cuando** pulse «Nueva consulta», **debe** cancelarse/ignorarse la solicitud anterior y limpiarse todo el estado de consulta. | Baja | Pendiente |
| P0-C | Retiro del bloque | **Cuando** se cargue la web, **no debe** aparecer la sección ni existir un listener al botón retirado. | Baja | Pendiente |
| P1 | Distritos | **Cuando** el `.md` esté presente, **debe** usarse como única fuente; **si** falta o es ambiguo, **no debe** inventarse zona. | Media, **bloqueada por archivo** | Bloqueada |
| P2-A | Autenticación | **Cuando** se verifique OTP, **debe** existir sesión validada; sin ella, historial devuelve 401. | Alta | Pendiente/aprobación |
| P2-B | Historial | **Cuando** un usuario autenticado consienta guardar una ruta válida, **debe** guardarse solo la referencia y poder borrarse; **nunca** el texto libre. | Alta | Pendiente/aprobación |
| P2-C | RLS y privacidad | **Si** usuario B solicita ruta de A, **no debe** leerla, actualizarla ni borrarla; anónimo no accede. | Alta | Pendiente/prueba real |

**Prioridad recomendada:** primero P0 (no altera permisos ni datos), después P1 cuando llegue el archivo, y finalmente P2 en una rama o entorno de laboratorio separado hasta pasar auditoría. **No** forzar autenticación e historial en un MVP de concurso de 6,5 horas si comprometen estabilidad o incumplen las bases.

## 11. Matriz mínima de pruebas nuevas

| ID | Prueba | Resultado esperado |
|---|---|---|
| SEM-01 | `nte` como respuesta a región | Canoniza a `norte`. |
| SEM-02 | `NÓRTE` en transporte | `norte`. |
| SEM-03 | Abreviatura no documentada | No se asigna una zona arbitraria. |
| SEM-04 | Error con dos coincidencias similares | Se pide aclaración; no elegir por azar. |
| SEM-05 | Texto con instrucciones hostiles | No modifica filtros ni salta validación de IDs. |
| DIST-01 | Distrito presente en `.md` | Coincide solo con la fuente cargada. |
| DIST-02 | Distrito ausente | Sin distrito ni región inventados. |
| DIST-03 | Alias duplicado/ambiguo | Rechazo controlado al cargar. |
| DIST-04 | Distrito sin zona documentada | Se reconoce, pero no se infiere zona. |
| DIST-05 | Fuente inexistente | Sin rutas geográficas inventadas; se informa limitación. |
| UI-01 | Nueva consulta tras resultado | Sin tarjetas, aclaración, refinamiento, alertas o texto previo. |
| UI-02 | Nueva consulta durante `fetch` | Respuesta tardía no repuebla tarjetas. |
| UI-03 | Petición normal/timeout/error | Spinner aparece y desaparece; botón se re-habilita. |
| UI-04 | `prefers-reduced-motion` | Sin rotación continua; mantiene indicación de actividad. |
| UI-05 | HTML final | No contiene «ACCESO A AYUDA HUMANA» ni listeners a `urgent-button`. |
| AUTH-01 | OTP válido, cuenta simulada | Se establece sesión sin devolver token al JS. |
| AUTH-02 | OTP erróneo/vencido | No se establece sesión; error neutro; rate-limit. |
| AUTH-03 | Cookie falsificada/token no validado | 401. |
| AUTH-04 | Logout/expiración | Se invalida acceso a historial. |
| HIST-01 | Consulta sin login o sin consentimiento | No se inserta historial. |
| HIST-02 | Ruta válida con opt-in + usuario A | Inserta una entrada con solo IDs/fecha/usuario. |
| HIST-03 | Mismo `client_request_id` reintentado | No duplica la entrada. |
| HIST-04 | Usuario B y anónimo | No ven ni borran las entradas de A, comprobado con RLS real. |
| HIST-05 | Servicio vencido tras guardado | Historial informa que la información debe revalidarse. |
| HIST-06 | Eliminación por titular | Entrada deja de ser accesible; sin efecto sobre servicios públicos. |
| HIST-07 | Falla Supabase al guardar | La ruta permanece visible, `history_saved=false`, sin éxito falso. |
| REG-01 | Pruebas anteriores del MVP v3 | Siguen pasando; no se revierte Gemini ni reglas FISI/OTRA. |

### Pruebas que NO sustituyen a otras

- **Mocks**: verifican lógica, no prueban que el correo llegue, que un token real sea seguro o que RLS esté aplicado en el proyecto remoto.
- **Prueba real con dos usuarios**: necesaria antes de guardar historiales en línea, usando cuentas de laboratorio y contenido **sintético**, nunca problemas reales de alumnos.
- **Prueba de navegador**: necesaria para spinner, accesibilidad y respuesta tardía de `fetch`; un test de búsqueda de cadenas en HTML no demuestra el comportamiento visual.
- **No afirmar «81 passed» para v4**: esas pruebas pertenecen a la etapa anterior. El resultado de esta propuesta es documental; v4 aún no tiene tests ejecutados.

Comandos previstos una vez implementado:

```powershell
cd C:\conecta-unmsm-lab-v3
.\.venv\Scripts\python.exe -m pytest -q -W error
.\.venv\Scripts\python.exe diagnostico_conecta.py
.\start-supabase-gemini.bat
```

No hace falta iniciar `start-demo.bat` para utilizar `start-supabase-gemini.bat`. Las pruebas de autenticación y RLS requerirán además un entorno Supabase configurado de laboratorio.

## 12. Definición de terminado y entrega por tarea

Una funcionalidad v4 está terminada **únicamente** cuando:

1. Tiene RF y ADR aceptados por el equipo; si afecta la constitución, se aprobó el cambio.
2. Se implementó en archivos identificados, sin sobreescribir la corrección existente de Gemini.
3. Los tests específicos y toda la suite existente pasaron **realmente**, con comando y salida registrados.
4. El navegador pasó prueba de reinicio, carga y no regresión; autenticación e historial pasaron prueba externa con identidades distintas y RLS.
5. No aparecen distritos, paradas, horarios ni servicios inventados.
6. Ninguna consulta sensible real se guarda en Supabase, logs o herramientas de analítica.
7. El reporte identifica **archivo modificado → qué hace → por qué se eligió así → alternativa descartada → pruebas ejecutadas → limitación**.

**Formato de entrega futuro por cambio:** solo archivos nuevos/modificados con ruta exacta Windows, código completo copiable y pruebas ejecutadas. Evitar enviar un ZIP completo por cada corrección pequeña. Mantener por separado el laboratorio y el repositorio oficial sujeto a bases del hackathon.

## 13. Pendientes concretos antes de programar toda v4

1. **Archivo canónico de distritos** que el prompt menciona pero no contiene. Sin él se puede completar el normalizador regional, no la gestión real de distritos.
2. **Aprobación del equipo** para modificar la constitución/ADR-10 y activar identidad e historial opt-in.
3. **Copia vigente de los archivos corregidos de Gemini y frontend** cuando se programe: el paquete v3 disponible para revisión puede preceder las últimas modificaciones probadas en la máquina del usuario.
4. **Configuración externa de Supabase Auth/OTP** y aceptación de la política de retención/consentimiento antes de probar con personas.
5. **Reglas del hackathon** para decidir si el código de laboratorio puede transferirse al repositorio de competencia.

## 14. Referencias técnicas de implementación

- [Supabase Auth — inicio de sesión sin contraseña mediante OTP](https://supabase.com/docs/guides/auth/auth-email-passwordless): el OTP por correo exige configurar la plantilla para enviar un código numérico; la llamada de sign-in por sí sola puede enviar un *magic link* si se deja la plantilla predeterminada.
- [Supabase — Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security): `GRANT` y RLS son controles distintos; verificar los dos, con `auth.uid()` y políticas por operación.
- [Supabase — validación de sesiones en servidor](https://supabase.com/docs/guides/auth/server-side/creating-a-client): comprobar identidad y firma; no confiar en una sesión decodificada sin validar.
- Documentación SDD local del laboratorio: `docs/constitution.md`, `docs/architecture-decisions.md`, `docs/api-contract.md`, `docs/catalog-contract.md` y `specs/001-rutas-bienestar-mvp/`.

---

**Veredicto:** incorporar ya al plan el normalizador controlado, «Nueva consulta», loading y retirada de bloque. Diseñar y probar Auth + historial opt-in como segunda fase de laboratorio, sin almacenar consultas crudas y sin sacrificar la consulta anónima. La lógica real de distritos permanece expresamente bloqueada hasta recibir el Markdown canónico.
