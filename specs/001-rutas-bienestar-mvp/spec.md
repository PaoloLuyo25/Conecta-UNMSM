# Spec 001 — Conecta UNMSM: Rutas de Bienestar Adaptativas (MVP)

**Estado:** PROPUESTA LISTA PARA REVISIÓN del equipo, no aprobada automáticamente. **Fecha:** 5 nov 2026.
**Método:** SDD. Este archivo expresa el **QUÉ y POR QUÉ**, sin decidir librerías, rutas de código, tablas ni algoritmos.

## Contexto y objetivo
La UNMSM dispone de diversas unidades de ayuda, bienestar y apoyo cuyo acceso varía entre dependencias. Un estudiante puede expresar varias necesidades a la vez, tener restricciones de horario o modalidad y desconocer los procedimientos. Conecta propone orientar desde una necesidad escrita en lenguaje natural hasta un **conjunto ordenado de próximos pasos y servicios documentados**. La primera demostración está limitada a estudiantes de la FISI y servicios centrales aplicables. No se garantiza que todos los canales estén disponibles en el momento de la consulta.

## Usuarios / actores
- **Estudiante FISI:** consulta de forma anónima y no registra información personal identificable.
- **Equipo de demostración:** usa casos ficticios, comprueba fuentes y prueba fallos.
- **Administrador futuro:** no existe en MVP; el catálogo lo mantiene el equipo por procedimientos externos.

## Historias de usuario
- **H1:** Como estudiante quiero describir mi necesidad en lenguaje cotidiano para no tener que conocer previamente el nombre de una oficina.
- **H2:** Como estudiante quiero responder una aclaración breve si es importante para obtener una ruta más útil.
- **H3:** Como estudiante quiero ver pasos, canales y fuentes para decidir mi siguiente acción sin creer información inventada.
- **H4:** Como estudiante quiero ajustar una restricción para reconsiderar las recomendaciones.
- **H5:** Como estudiante quiero consultar categorías de bienestar, orientación, clínica y transporte cuando haya evidencia verificable.
- **H6:** Como evaluador quiero comprobar que los errores de IA/datos se reconocen y no destruyen el flujo de la aplicación.

## Requisitos funcionales (criterios de aceptación EARS)

### Consulta y alcance
- **RF-01:** CUANDO el estudiante ingrese una descripción válida de su necesidad, EL SISTEMA iniciará una consulta orientada al piloto FISI.
- **RF-02:** SI la descripción está vacía o excede 800 caracteres visibles, ENTONCES EL SISTEMA la rechazará con un mensaje en español sin iniciar el análisis inteligente.
- **RF-03:** CUANDO una consulta contenga varias necesidades relacionadas, EL SISTEMA las identificará como elementos diferenciados para decidir una ruta.
- **RF-04:** SI el usuario pide procedimientos de otra facultad fuera del piloto, ENTONCES EL SISTEMA advertirá el límite y no atribuirá a FISI procedimientos de esa facultad.

### Inteligencia adaptativa
- **RF-05:** SI falta un dato cuya respuesta pueda cambiar la selección de servicios y no se ha realizado aclaración, ENTONCES EL SISTEMA formulará como máximo una pregunta relevante.
- **RF-06:** CUANDO el estudiante responda la aclaración, EL SISTEMA evaluará esa respuesta junto con la necesidad original para presentar una ruta o una insuficiencia informativa.
- **RF-07:** MIENTRAS una consulta ya haya utilizado su aclaración, EL SISTEMA no formulará otra pregunta adicional para esa misma consulta.
- **RF-08:** CUANDO exista información suficiente y servicios elegibles, EL SISTEMA propondrá hasta tres servicios pertinentes ordenados por utilidad contextual.
- **RF-09:** CUANDO el estudiante modifique una restricción relevante, EL SISTEMA reevaluará los servicios con el contexto actualizado, sin prometer un cambio si el resultado sigue siendo válido.

### Fiabilidad y fuentes
- **RF-10:** EL SISTEMA mostrará los pasos, requisitos, datos de contacto, ubicación y horarios **solo cuando estén documentados** en el catálogo.
- **RF-11:** EL SISTEMA mostrará la fuente y el estado de verificación de cada servicio recomendado.
- **RF-12:** SI falta un dato institucional necesario, ENTONCES EL SISTEMA indicará «Por confirmar» en lugar de completarlo por inferencia.
- **RF-13:** SI un servicio no existe dentro del catálogo permitido o no corresponde al ámbito de aplicación, ENTONCES EL SISTEMA no lo mostrará como recomendación válida.
- **RF-14:** MIENTRAS un servicio pertenezca a una convocatoria cerrada o a información de vigencia incierta, EL SISTEMA mostrará una advertencia y no afirmará que está abierta o disponible ahora.
- **RF-15:** SI no hay servicios documentados elegibles para una necesidad, ENTONCES EL SISTEMA informará que no dispone de una ruta confirmada sin inventar alternativas.

### Resiliencia, seguridad y transparencia
- **RF-16:** SI falla la IA o no devuelve una respuesta aceptable, ENTONCES EL SISTEMA mantendrá accesible la información documentada disponible y avisará que no pudo personalizar la ruta.
- **RF-17:** SI falla el catálogo principal pero existe una copia local válida, ENTONCES EL SISTEMA podrá mostrar la información de esa copia, identificándola como respaldo y advirtiendo su posible desactualización.
- **RF-18:** CUANDO el sistema utilice IA para seleccionar servicios, EL SISTEMA lo identificará sin presentar opiniones generadas como hechos institucionales.
- **RF-19:** CUANDO el estudiante consulte información sobre transporte externo, EL SISTEMA utilizará solamente rutas y zonas que consten en los datos disponibles y no inventará paradas, tiempos ni trayectos.
- **RF-20:** SI la entrada contiene órdenes para ignorar reglas, revelar secretos o inventar servicios, ENTONCES EL SISTEMA mantendrá sus restricciones de selección, contenido y privacidad.
- **RF-21:** EL SISTEMA mantendrá visible una opción de «Necesito ayuda urgente» que oriente a buscar asistencia humana, sin diagnóstico, clasificación clínica ni contactos no verificados.
- **RF-22:** EL SISTEMA funcionará sin exigir registro de cuenta, código universitario, DNI ni historial personal persistente.

## Requisitos no funcionales
- **RNF-01:** Interfaz y mensajes de error en español; legibles en laptop y móvil.
- **RNF-02:** Ningún dato secreto aparece en la interfaz ni en las respuestas al usuario.
- **RNF-03:** La aplicación no guarda el texto de consultas del usuario en una base persistente en esta versión.
- **RNF-04:** Ante fallo de conexión inteligente, mostrar una respuesta controlada en lugar de esperar indefinidamente; presupuesto de espera objetivo de hasta ~10 segundos por intento.
- **RNF-05:** Las fuentes y advertencias son distinguibles visualmente en la vista de resultados.
- **RNF-06:** El sistema no requiere servicios clínicos, acceso privado a plataformas universitarias ni datos personales para funcionar.

## Casos límite
- Descripción vacía, repetida, demasiado extensa, con HTML o instrucciones adversarias.
- Necesidad múltiple; restricción de mañana/tarde, presencial/virtual que no cambia los servicios.
- Servicio de FISI con dato de 2021 pero sin revalidación actual; no atribuir disponibilidad.
- Servicio central aplicable a FISI que no debe presentarse como servicio de la facultad.
- Clínica/atención mental con categorías similares; no mezclarlas sin evidencia.
- Transporte «norte/sur/centro/este» sin mapa o paradas verificadas.
- Usuario pide servicio inexistente, convocatorias vencidas o una cita inmediata.
- IA devuelve selección inexistente, formato incorrecto, demora o falla de cuota.
- Catálogo principal no disponible, respaldo ausente o desactualizado.

## Fuera de alcance
Login, registro de estudiantes, seguimiento de solicitudes reales, expedientes, historias clínicas, evaluación emocional automatizada, citas agendadas, pagos, autoseguro automático, trámites, modificación de horarios, denuncia pública, mensajes automáticos a oficinas, chatbot terapéutico, mapas/ETA de autobuses, horarios en vivo, publicación de datos personales, integración oficial con sistemas internos de UNMSM, actualización automática por comunicados y administración de servicios desde la web.

## Criterios de finalización
1. Todos los RF-01 a RF-22 tienen evidencia de test ejecutado o prueba manual registrada; los que no puedan probarse se marcan **NO VALIDADO**, nunca aprobados por intuición.
2. Tres escenarios ficticios muestran información documentada cuando existe; dos escenarios de fallo se controlan sin caída.
3. Se demuestra al menos una pregunta decisiva y una reevaluación coherente cuando existan registros que permitan probarlas; si no, se declara esa limitación.
4. Ningún servicio ficticio aparece presentado como real; las fuentes de datos del MVP están autorizadas y comprobadas.
5. Aplicación disponible localmente, repositorio entregado, video de ejecución auténtica y presentación preparada antes del Code Freeze.

## Dudas abiertas — NO sustituir por suposiciones
- **[NECESITA ACLARACIÓN]** ¿Qué registros de Bienestar, UNAYOE, clínica y transporte serán documentados y autorizados para la demostración?
- **[NECESITA ACLARACIÓN]** ¿Se autoriza importar al concurso documentación y datos preparados previamente? No es lo mismo que código previo, pero las bases deben aclararlo.
- **[NECESITA ACLARACIÓN]** ¿Hay una denominación oficial y dependencia concreta del servicio llamado provisionalmente «clínica de salud mental»?
- **[NECESITA ACLARACIÓN]** ¿El equipo quiere que el transporte externo entre en la demostración principal o quede como categoría disponible solo si hay datos suficientes? **Default provisional:** solo si tiene registros verificados.

**Regla de aprobación:** José, Paolo y Daniela revisan este documento antes de implementar. Cualquier cambio de comportamiento se acuerda aquí primero.


## Extensión de especificación para el laboratorio — aprobada por José (6 noviembre 2026)

**Motivo:** permitir orientación parcial a estudiantes ajenos al piloto FISI sin presentar trámites de una facultad como propios de otra. Aplica solo al laboratorio bajo cláusula 11.

- **H7:** Como estudiante de otra facultad, quiero consultar información central accesible a toda la UNMSM sin recibir recomendaciones de trámites exclusivos de FISI.
- **RF-23:** CUANDO un estudiante seleccione una facultad distinta de FISI, EL SISTEMA consultará únicamente servicios centrales cuya cobertura para todas las facultades esté respaldada por el catálogo.
- **RF-24:** SI un servicio central no acredita cobertura para todas las facultades, ENTONCES EL SISTEMA no lo mostrará al estudiante de otra facultad como opción elegible, aunque el servicio sea CENTRAL.
- **RF-25:** CUANDO un estudiante de otra facultad solicite transporte externo documentado como universal, EL SISTEMA podrá presentar exclusivamente la información disponible, sin inferir paradas, rutas, horarios, tarifas o disponibilidad.
- **RF-26:** SI el sistema está configurado con una base externa inaccesible, ENTONCES EL SISTEMA informará del fallo y utilizará únicamente el respaldo autorizado que exista, identificando su origen y vigencia.

**Criterios verificables:** `tests/test_scope_v3.py` para RF-23–25, `tests/test_supabase_v3.py` para el contrato estructural; la verificación de RLS en una instancia real es obligatoria antes de declarar **VALIDADO** el RF-26 remoto. La demostración utiliza exclusivamente registros ficticios explícitos.

**PENDIENTE:** fuente que demuestre cuáles servicios centrales realmente admiten estudiantes de otras facultades; cuenta Gemini/API key y Supabase reales; comprobación real de acceso, cuota y políticas.
