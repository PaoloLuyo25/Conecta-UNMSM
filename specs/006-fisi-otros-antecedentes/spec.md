# Especificación EARS — ámbitos y antecedentes documentados

- **RF6-01** CUANDO se abra el formulario, EL SISTEMA ofrecerá únicamente `FISI` y `OTROS` como ámbitos visibles. `OTROS` no concede acceso a servicios exclusivos de una facultad.
- **RF6-02** CUANDO se consulte movilidad hacia un país identificable, EL SISTEMA comprobará primero si el catálogo contiene una oportunidad de ese destino con fechas y apertura verificadas; SI no existe evidencia suficiente, comunicará que **no ha encontrado una convocatoria abierta confirmada en su catálogo**, nunca que no exista en todo el mundo.
- **RF6-03** CUANDO haya antecedentes documentados y vencidos para el país, EL SISTEMA mostrará hasta tres fichas históricas separadas de los servicios de orientación; indicará plazos anteriores, destinatarios y fuentes sin habilitar postulación.
- **RF6-04** CUANDO la consulta sea sobre investigación formativa VRAP, EL SISTEMA priorizará documentos de investigación formativa. La búsqueda sobre proyectos competitivos VRIP podrá remitirse a VRIP, sin presentarla como convocatoria VRAP.
- **RF6-05** MIENTRAS se procesa una consulta, LA INTERFAZ mostrará estado accesible y botón de cancelar; la respuesta tardía cancelada no reemplazará resultados posteriores.
- **RF6-06** MIENTRAS se guarda una ruta, LA INTERFAZ indicará «Guardando ruta…» y después el resultado de la operación. No se guardará texto libre de la consulta.
- **RF6-07** CUANDO alguien intente crear una cuenta, EL SISTEMA informará cómo iniciar sesión si la dirección ya está registrada, sin afirmar que pueda detectar duplicados si Supabase oculta deliberadamente esa información para evitar enumeración de correos.
- **RF6-08** CUANDO el recolector consulte fuentes, EL SISTEMA guardará sus entradas como `pendiente_revision` e indicará estado `sin_verificar`; ninguna entrada pasa automáticamente a `public.services`.
- **RF6-09** SOLO personal con acceso de administrador ejecutará SQL revisado; las políticas RLS de lectura y el historial existente se conservarán.

## Límites
No se adjudican becas, se reservan vacantes, se confirma apertura en tiempo real ni se ejecutan solicitudes de postulación. Una fecha histórica no constituye vigencia actual. La biblioteca de convenios es orientativa, no un listado de becas aprobadas.
