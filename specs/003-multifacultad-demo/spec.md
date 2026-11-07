# Spec 003 — Demostración multifacultad, público y oportunidades FICTICIAS

**Aprobación de alcance:** José solicitó explícitamente todas las facultades UNMSM y diferencias de pregrado/posgrado/docentes (7/11/2026). La programación es una extensión exclusiva del LAB; la inserción en proyecto oficial depende de las bases del hackathon.

## Contexto y objetivo
La versión 4.4 permitía casos de otras facultades solo para servicios centrales; se amplía a 20 facultades con escenarios sintéticos de orientación, becas y movilidad académica, sin atribuir convocatorias reales a UNMSM.

## Usuarios / actores
Usuarios invitados, usuarios autenticados con acceso opcional, personas de pregrado/posgrado y docentes en una simulación. El login existente no prueba identidad universitaria.

## Historias de usuario
- H1: Como estudiante de posgrado quiero consultar movilidad académica sin recibir rutas de transporte externo.
- H2: Como estudiante de pregrado quiero conocer ejemplos de becas de mi facultad.
- H3: Como docente quiero consultar convocatorias ficticias correspondientes a docentes.
- H4: Como visitante quiero seleccionar cualquiera de las 20 facultades sin crear cuenta.

## Requisitos funcionales (EARS)
- RF3-01: EL SISTEMA ofrecerá un selector con los nombres de las 20 facultades UNMSM verificados en el directorio oficial.
- RF3-02: CUANDO se elija una facultad, EL SISTEMA recuperará únicamente fichas de esa facultad y fichas centrales universales, respetando la excepción histórica FISI del piloto.
- RF3-03: CUANDO se elija un público de pregrado, posgrado o docentes, EL SISTEMA excluirá fichas de público exclusivo incompatible.
- RF3-04: CUANDO el mensaje mencione explícitamente posgrado, pregrado o docentes y no exista selección de público, EL SISTEMA reconocerá ese público antes de consultar la IA.
- RF3-05: CUANDO se soliciten becas o movilidad sin indicar un público, EL SISTEMA pedirá una sola aclaración sin recomendar convocatorias arbitrarias.
- RF3-06: CUANDO el texto indique viajar o intercambio académico, EL SISTEMA buscará la categoría de movilidad académica en lugar de transporte externo.
- RF3-07: CUANDO el texto indique transporte universitario, EL SISTEMA buscará transporte externo sin deducir que se trata de movilidad académica.
- RF3-08: EL SISTEMA enviará un máximo de seis candidatos verificables por turno a Gemini y aceptará un máximo de tres IDs de resultado.
- RF3-09: SI falla Gemini, ENTONCES EL SISTEMA comunicará modo degradado y solo mostrará registros elegibles sin afirmar personalización.
- RF3-10: EL SISTEMA etiquetará cada beca/convocatoria/movilidad artificial como `prueba_ficticia`, sin fuentes, fechas, enlaces ni trámites simulados como hechos.
- RF3-11: CUANDO un usuario guarde una ruta, EL SISTEMA conservará el flujo de opt-in, comprobante firmado y RLS del laboratorio v4.4 sin persistir texto libre.

## Requisitos no funcionales
- Conservación de FastAPI, JS vanilla, Supabase Repository y Gemini Flash-Lite.
- No enviar simultáneamente todo el catálogo al modelo.
- No exponer datos sensibles ni credenciales; sin cambios en el esquema privado del historial.

## Casos límite
- Otra facultad no puede recibir fichas exclusivas FISI ni de terceros.
- Sin datos de audiencia, no inferir convocatoria vigente.
- Una aclaración sin perfil reconocible termina en `degraded`, no más preguntas.
- El filtro de perfiles no elimina fichas antiguas cuando su público no está tipificado.

## Fuera de alcance
Convocatorias universitarias reales, postulación o registro de becas, autorización de viajes, valoración de requisitos, validación de matrícula, cifras de financiamiento, generación de procedimientos oficiales.

## Criterios de finalización
Tests unitarios/HTTP en verde, 20 códigos presentes, rutas sintéticas diferenciadas y paquetes sin secretos. Pruebas contra Supabase/Gemini reales son manuales y quedan pendientes hasta ejecutarlas.

## Dudas abiertas
- [NECESITA ACLARACIÓN] Quién confirmará condiciones oficiales al sustituir las fichas ficticias por programas verdaderos.
