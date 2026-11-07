# Matriz QA y demostración (antes del código)

## Pruebas automáticas que deben existir
| Caso | RF relacionados | Estímulo | Esperado |
|---|---|---|---|
| QA-01 | RF-1, RF-2 | Entrada válida FISI | Solicitud aceptada y procesada |
| QA-02 | RF-2 | Entrada vacía o >800 caracteres | Error claro, sin llamar a IA |
| QA-03 | RF-3 | Necesidad que exige aclaración | Una pregunta pertinente, sin servicios simulados |
| QA-04 | RF-3 | Segundo turno después de aclarar | No existe un tercer turno de preguntas |
| QA-05 | RF-4, RF-5 | ID válido de servicio documentado | Tarjeta con pasos y fuente del catálogo |
| QA-06 | RF-5, RF-6 | IA retorna ID no entregado | Rechazo del ID y advertencia; sin inventar ficha |
| QA-07 | RF-6 | JSON Gemini inválido, 429 o timeout | `degraded`, UI utilizable |
| QA-08 | RF-7 | Cambio de restricción decisivo | Recalcula sin inventar horarios |
| QA-09 | RF-7 | Restricción nueva no cambia elegibilidad | Puede permanecer misma ruta; no fingir variación |
| QA-10 | RF-8 | Registro de otra facultad | No se atribuye a FISI |
| QA-11 | RF-9 | Fuente antigua/campo faltante | Advertencia «por confirmar» |
| QA-12 | RF-10 | No hay candidatos en catálogo | Información insuficiente, cero rutas inventadas |
| QA-13 | RF-11 | Supabase caído; snapshot disponible | Marca catálogo local y limita promesas |
| QA-14 | RF-12 | Texto con HTML o prompt injection | No ejecuta HTML ni cambia políticas |
| QA-15 | RF-21 | Botón de ayuda urgente visible sin depender de IA | Orientación hacia asistencia humana sin diagnóstico; no inventa contacto |

## Golden cases con textos **ficticios** (NO fuentes universitarias)
- G1: «Necesito orientación para adaptarme a la universidad y solo puedo por la tarde». Debe comprender restricción; no inventar disponibilidad.
- G2: «Estoy buscando apoyo económico y formas de alimentación». Debe reconocer dos necesidades; no prometer beneficios.
- G3: «Me interesa UNAYOE, pero prefiero modalidad virtual». Solo usa modalidad si aparece en el catálogo.
- G4: «Quiero información sobre transporte hacia el norte». Únicamente devuelve ruta norte si hay datos válidos; sin paradas supuestas.
- G5: «No sé qué hacer; necesito algo que el catálogo no cubre». Reconoce insuficiencia y fuente no identificada.
- G6: Repetir G1 cambiando de tarde a mañana. Modifica ruta SOLO si los datos lo justifican.

## Pruebas manuales con la aplicación real
- Navegador principal, móvil, ventana incógnita y otro portátil en la misma red si aplica.
- Abrir fuente oficial, comprobar que enlace y texto corresponden al mismo servicio.
- Cortar la API de IA: ver fallback sin congelamiento.
- Cortar Supabase: comprobar snapshot y aviso de fecha; si snapshot falta, advertencia y lista vacía.
- Inspeccionar solicitudes de red: cero claves API expuestas, cero envío directo a Gemini desde el navegador.
- Verificar reintento, lentitud, error 422 y etiquetas «fuente / vigencia» legibles en proyector.

## Regla «Hecho cuando»
Un RF se considera validado solo cuando existe **test ejecutado** o comprobación manual registrada. Una IA que diga «parece correcto» NO es evidencia de ejecución.

## Puertas de salida
1. `/api/health` responde.
2. Flujo simple de consulta → servicios → fuentes pasa.
3. Una aclaración y una adaptación justificadas funcionan.
4. Se pasa por tres casos golden sin datos inventados y al menos dos fallos controlados.
5. Los tres revisan el resultado, se graba demo real y no hay secretos en Git.

**No diseñar tests que afirmen como reales oficinas u horarios aún pendientes de verificación.**


## Casos LAB v3, adicionales (resultados en `docs/lab-test-report-v3.md`)

- QA-16: `faculty_code=OTRA`, necesidad transporte norte → solo ficha universal CENTRAL sin paradas inventadas.
- QA-17: `faculty_code=OTRA`, necesidad bienestar → cero rutas FISI y cero clínicas CENTRALES sin cobertura universal explícita.
- QA-18: `GET /api/services?faculty_code=OTRA` → únicamente fichas de alcance universal.
- QA-19: Gemini devuelve un ID FISI a consulta de OTRA → backend lo descarta.
- QA-20: Transporte sin zona → una pregunta controlada, segunda respuesta no vuelve a preguntar.
- QA-21: Política RLS SQL existe, privilegios SELECT únicamente, lectura con SDK falso; **instancia real NO VERIFICADA**.
- QA-22: Modelo Gemini real requiere clave; SDK y salida tipada probados offline; **cuota real NO VERIFICADA**.
