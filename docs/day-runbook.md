# Runbook del día de hackathon — SDD bajo 6,5 horas

**Horario de planificación basado en bases aportadas:** sábado 7 nov 2026, Sprint 08:30–13:00 y 14:00–16:00, freeze 16:00. El equipo prioriza enviar todo a las **15:30**. Si la organización publica horarios nuevos, estos prevalecen.

## Antes de empezar (sin implementar MVP)
- Confirmar elegibilidad, uso de herramientas IA, recursos preparados, datos y formato de entregables.
- Tener cuentas instaladas: Python, Git/GitHub Desktop, Cursor o VS Code, grabador OBS/Windows y conectividad de respaldo.
- Obtener la información de servicios por separado; el kit no presupone hechos institucionales aún no aportados.
- Revisar juntos `spec.md`, `plan.md`, `api-contract.md` y las tareas. Acordar la demo ficticia.

## Secuencia SDD durante el evento
| Tramo | Entregable | Responsables |
|---|---|---|
| 08:30–09:00 | Repo nuevo, reglas, contrato fijo, esqueleto, tests básicos | José; todos aprueban |
| 09:00–10:00 | UI simulada + API health/catalog + adapter local | Daniela / José |
| 09:00–10:15 | Adapter Gemini con respuesta tipada y pruebas offline | Paolo |
| 10:00 | Merge 1: sin IA, consulta catálogo y fuentes | José |
| 10:00–12:15 | Integración IA con IDs, razón, pregunta única | Paolo + José + Daniela |
| 12:15 | Merge 2: flujo de punta a punta demostrable | Todos |
| 14:00–14:40 | QA, seguridad, contingencia y ajuste de UX | Todos |
| 14:40 | Merge 3: congelar funcionalidades, elegir demo local/web | José |
| 14:40–15:30 | Video real OBS, diapositivas, QA final y entrega preventiva | Paolo y Daniela + José |
| 15:30–16:00 | Margen para errores de entrega; ningún cambio grande | Todos |

## Puertas de corte
- Si a las **11:00** no hay servicios documentados que se muestren sin IA: **eliminar refinamiento visual** y reparar flujo básico.
- Si a las **12:15** la IA no retorna una ruta verificada: mantener ruta inicial simple; aclaración pasa a opcional; **no** introducir agentes ni RAG.
- Si Supabase no está listo, elegir snapshot JSON local; **no** configurar infra desde cero a las 14:00.
- Si Gemini falla: informar modo degradado; no fingir salida IA.
- Después de **14:00**, no nuevas features. Después de **14:40**, solo bloqueadores y entrega.

## Inicio de implementación con IA (cuando lo autoricen)
1. Abrir Cursor en el directorio del repo nuevo, leer `AGENTS.md`.
2. Pegar prompt de `samples/prompts.md` indicando **Txx** y limitar edición a archivos de esa tarea.
3. Pedir tests primero, ejecutar tests, inspeccionar diff. Si falla, reparar solamente esa tarea.
4. Integrar en los horarios definidos; probar el flujo desde el navegador real.
5. Registrar estado honesto: `PASA / FALLA / NO EJECUTADO` por prueba.

## Presentación al jurado
**Demostración recomendada:** estudiante FISI describe dos necesidades → IA decide pregunta si hace falta → usuario responde → aparecen 1–3 tarjetas con fuente oficial → estudiante modifica una restricción → ruta se recalcula justificadamente. Mostrar después error controlado de IA o una captura del test, sin comprometer la demo principal.

**Mensaje técnico:** recuperación controlada del catálogo + IA para comprender contexto y ordenar servicios + validador determinista + datos oficiales proporcionados por backend. No se necesita arquitectura distribuida ni base vectorial para 5–15 registros.
