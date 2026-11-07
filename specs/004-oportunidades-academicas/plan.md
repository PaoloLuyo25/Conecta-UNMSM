# Plan — oportunidades académicas verificables

## Decisiones de arquitectura
Se mantiene el monolito modular **frontend vanilla → FastAPI → Repository (Supabase / respaldo documental) + Gemini**. Sin nuevas tablas ni escrituras públicas, excepto la tabla de servicios existente actualizada por un administrador. Se conserva Supabase Auth opcional y se deja historial privado apagado de forma predeterminada.

## Módulos y flujo
1. **Consulta (Daniela):** un campo libre con placeholder «Soy un estudiante y...», selector de facultad (20) y público opcional; mantiene login opcional, reset, spinner, tarjetas, fuentes y advertencias.
2. **Elegibilidad (José):** `repository.py` filtra la facultad propia + servicios centrales realmente universales, exclusión de periodos vencidos y registros ficticios para modo normal.
3. **Intención y público (Paolo/José):** `targeting.py` separa becas, movilidad, convocatorias académicas, bienestar, clínica y transporte; admite audiencias conjuntas documentadas en CSV (`pregrado,posgrado` / `posgrado,docentes`) sin inventar requisitos.
4. **LLM (Paolo):** Gemini recibe como máximo seis registros compactos; selecciona IDs/códigos. `validator.py` rechaza identificadores no admitidos. `RouteService` compone los datos desde el catálogo, con modo degradado cuando falla.
5. **Fuentes (José):** `tools/explorar_fuentes.py` recorre feeds públicos limitados de OGCRI Blog, OGCRI, VRAP y VRIP con robots/allowlist. La salida `data/discovered.pending.json` NO equivale a fuente validada. Revisión humana posterior rellena el contrato de `Service` y `tools/generar_sql_catalogo.py` genera SQL de importación. La ejecución es manual en SQL Editor para mantener RLS (anon no escribe).
6. **Catálogo (José):** `data/catalog.academico.json` documenta fuente, destinatarios, límites y vigencia de publicaciones revisadas. `supabase/006_categorias_academicas.sql` añade categoría informativa general y `007_catalogo_revisado.sql` importa registros de forma idempotente. Otros SQL son históricos: no recrear la tabla.

## Reglas de procedencia
La revisión de publicación web se registra como fecha de revisión, NO como disponibilidad o apertura. Los anuncios sin estado verificable usan `vigencia_por_confirmar`. No mezclar programas de una facultad con otra. Los datos aportados por entrevistas y carteles se identifican como `informacion_directa`, no como verificación web independiente.

## Alternativas descartadas
- Alimentar directamente la base desde scraping: riesgo de anuncios vencidos, duplicados y atribución incorrecta.
- Enviar textos web íntegros a Gemini: añade prompt injection y probabilidad de alucinación.
- Importar 140 fichas ficticias: ya no responde al nuevo objetivo.
- Prometer que convenio financia viaje: contradice documentación OGCRI.

## Pruebas
Pruebas offline del contrato, elegibilidad, parser, topes de candidatos, cadenas de interfaz y ausencia de `prueba_ficticia` en catálogo real. RLS, correo y Gemini reales requieren verificación externa. Pruebas desde navegador con `tests/browser_smoke.py` usan respuestas simuladas; no prueban el acceso a Supabase/Google.
