# Conecta UNMSM — correcciones de integración

1. En Supabase SQL Editor ejecuta `supabase/009_limpieza_vrap.sql`. Elimina únicamente la ficha genérica `CENTRAL-VRAP-PREGRADO`; mantiene la guía oficial de investigación formativa y el resto de las tablas.
2. Si la guía no está cargada, revisa `supabase/008_antecedentes_ogcri_investigacion.sql` antes de ejecutar: ese script también contiene otras operaciones; no lo vuelvas a ejecutar a ciegas.
3. Inicia `INICIAR_CONECTA_HISTORIAL_LAB.bat`. Conserva `.env` privado.
4. Para explorar OGCRI: `.venv\Scripts\python.exe -m tools.explorar_fuentes --historical-pages 2`. El resultado `data/discovered.pending.json` es una cola de revisión, NO SQL automático.
5. La página final usa la interfaz de `CONECTA_paso2.zip`; conserva rutas, login, historial y resultados históricos.
6. El motor de transporte elige por zona de forma determinista. Una aclaración `sur` solo devuelve servicios `route_region=sur`, sin IA.
7. Las fuentes históricas de OGCRI nunca se anuncian como abiertas solo por estar publicadas; verifica fecha, perfil y requisitos.

## Casos de prueba manual

- FISI, «Soy un estudiante y necesito transporte externo» → pregunta por zona. «sur» → exclusivamente rutas sur.
- FISI, «Soy un estudiante y necesito transporte hacia el norte» → solo norte, sin aclaración.
- Otros, «Soy un estudiante y necesito transporte hacia el este» → solo este si existe registro central universal.
- FISI, «Soy un estudiante de pregrado y quiero viajar a Francia» → si no hay convocatoria abierta confirmada, mostrar antecedentes de Francia con sus fechas vencidas.
- Otros, «Soy estudiante de posgrado y busco becas de movilidad» → únicamente fichas compatibles con el perfil; revisar enlaces y plazos.
- FISI, «Quiero investigar durante mi pregrado» → guía de investigación formativa y otras fuentes documentadas; no noticias genéricas de VRAP.
- Pulsar «Cancelar búsqueda» mientras carga → la respuesta cancelada no debe sustituir el resultado anterior.
- Crear cuenta con correo ya registrado → Supabase puede ocultar su existencia; ofrecer iniciar sesión sin afirmar que la cuenta existe.
- Iniciar sesión, generar ruta y guardar → confirmación visible; consultar y borrar historial propio.
- Desactivar temporalmente Gemini → advertencia de información no personalizada, sin inventar resultados.

**Importante:** pruebas automatizadas locales no sustituyen verificación de Gemini, Supabase RLS y SMTP reales.
