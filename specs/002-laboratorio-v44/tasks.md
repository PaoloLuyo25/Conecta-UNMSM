# Tasks 002 — Continuación SDD por persona

**Nota:** son tareas para trabajo **a partir** de la base funcional LAB v4.4; no representan reimplementación de lo que ya existe. El paquete original reportó 127 tests; no se marcan pendientes como completados por tener documentación.

## Compuerta compartida
- [ ] **T2-01 — Equipo**: aprobar `spec.md`, contrato v4.4 y reparto. RF2-01–22. Hecho cuando los tres confirman cambios antes de tocar un contrato.

## José
- [ ] **T2-J01**: comprobar instalación Windows limpia, corregir dependencia y confirmar `.env.example` sin secretos. RF2-08/09/17. Hecho cuando `pip install -r requirements-supabase.txt` y suite corren en instalación limpia (no probado en Windows desde aquí).
- [ ] **T2-J02**: configurar/validar Supabase solo en laboratorio; probar SELECT público, escritura anónima rechazada y RLS con identidades A/B independientes. RF2-14–17/20. Hecho cuando existe bitácora de pruebas remotas, no mocks.
- [ ] **T2-J03**: revisar confirmación del correo y SMTP si se requiere validar identidad antes de producción sin OTP. RF2-08/09/22. Hecho cuando hay prueba autorizada de enlace SMTP y política de seguridad aprobada; de lo contrario mantener entorno LAB.
- [ ] **T2-J04**: integrar branches y correr regresión + revisión de `.env`/secrets. RF2-01–22. Hecho cuando `main` arranca con contrato sin cambios accidentales y se registran PASA/FALLA/NO EJECUTADO.

## Paolo
- [ ] **T2-P01**: comprobar modelo y cuota Gemini reales con texto sintético, respuesta tipada y errores controlados. RF2-03/04/21. Hecho cuando hay evidencia de llamada externa y no se muestra dato generado fuera de catálogo.
- [ ] **T2-P02**: reforzar pruebas de errores tipográficos, `nte`, ambigüedad y prompt injection sin inventar regiones. RF2-18/19. Hecho cuando test adverso es reproducible con fixtures y sin fuente geográfica inventada.
- [ ] **T2-P03**: ampliar matriz QA de fallos 429, timeout, JSON inválido, candidatos ilegítimos, y compatibilidad con José. RF2-03/04/21. Hecho cuando la suite completa pasa y documenta cada caso.

## Daniela
- [ ] **T2-D01**: revisar responsive, teclado, indicador de carga, botón Nueva consulta y no reutilización de respuesta vieja. RF2-01/02/05/06/07. Hecho cuando smoke de navegador y comprobación manual registrados.
- [ ] **T2-D02**: probar visualmente invitado→ruta→guardar→login→historial, login previo y cierre del modal. RF2-08–12/17. Hecho cuando ruta se guarda sin repetir `/api/route` en red simulada y el recorrido remoto queda marcado verificado o pendiente.
- [ ] **T2-D03**: revisar avisos de vigencia, fuente, histórico, alcance y ausencia de datos inventados. RF2-20–22. Hecho cuando tarjetas son legibles en móvil/proyector y los datos ficticios se etiquetan expresamente.

## Integración final
- [ ] **T2-F01 — Todos:** congelar cambios compartidos, reconciliar la matriz de trazabilidad y demo local. RF2-01–22. Hecho cuando existe ejecución registrada sobre versión integrada, con limitaciones honestas y sin clave en ZIP.

**Ritmo SDD:** solo una tarea por agente, test primero, anotar el diff y esperar aceptación antes de la siguiente. Revisar bases del concurso antes de transferir software del laboratorio.
