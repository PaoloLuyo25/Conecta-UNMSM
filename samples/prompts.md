# Prompts SDD para usar con ChatGPT / Claude / Cursor — Conecta UNMSM

**Siempre** empezar la sesión adjuntando el kit o asegurándose de que el agente lee `AGENTS.md`, `docs/constitution.md`, spec activa y plan. Si se usa Claude web, la carpeta `.claude/skills` no se ejecuta por sí sola; adjuntar su `SKILL.md` para usar esa lógica. Los prompts no conceden permiso para reutilizar código anterior al evento.

## P0 — Lectura y autocontrol (antes de implementar)
> Lee AGENTS.md, docs/constitution.md, docs/context.md, specs/001-rutas-bienestar-mvp/spec.md, plan.md, docs/api-contract.md y docs/catalog-contract.md. Resume en 8 líneas decisiones cerradas, riesgos y 3 límites que NO puedes violar. No escribas código. Indica conflictos entre documentos.

## P1 — Constitución (cuando se crea una nueva línea de producto)
> Revisa docs/constitution.md: verifica que cada principio sea comprobable, compatible con 6,5 h y los RF. Propón solo cambios imprescindibles indicando a qué principio afectan. NO implementes.

## P2 — Especificación / aclaración
> Revisa spec activa como QA estricto. Enumera contradicciones, falta de comportamiento ante fallos, promesas no demostrables y datos institucionales sin evidencia. No propongas código; señala líneas o RF afectados y estados [NECESITA ACLARACIÓN]. No preguntes decisiones ya resueltas en documentos.

## P3 — Plan
> Lee constitución y spec. Verifica que plan.md cubre todos los RF con módulos, contrato, orquestación IA, repositorio, seguridad, fallos y tests. No escribas código. Recomienda simplificaciones para 6,5 h y di qué RF se arriesga a perder cada recorte.

## P4 — Tareas
> Verifica que tasks.md divide el plan en tareas de 15–30 min, con dependencias, dueño, RF y “Hecho cuando”. Encuentra conflictos de archivos entre José, Paolo y Daniela. No cambies el contrato por iniciativa propia.

## P5 — Implementar una sola tarea (SOLO durante el evento y con autorización)
> Implementa **únicamente T[XX]** de specs/001-rutas-bienestar-mvp/tasks.md. Lee AGENTS.md, constitución, spec, plan, contrato API y módulo relacionado. Primero escribe los tests adecuados; luego cambia solo los archivos de esta tarea. Ejecuta los tests disponibles; comunica comandos y resultados exactos. Marca T[XX] solo si pasa «Hecho cuando». DETENTE; no implementes otra tarea.

## P6 — Integración frontend (Daniela)
> Trabajas únicamente en frontend/ para la tarea T[XX]. Usa los tres modos de docs/api-contract.md: question, route, degraded. No inventes datos institucionales, no llames Gemini directo ni uses HTML no seguro para mensajes. Construye con respuesta JSON ficticia **etiquetada como mock**. No toques nombres de claves del contrato.

## P7 — Integración Gemini (Paolo)
> Trabajas únicamente en ai_adapter y tests de salida para T[XX]. Gemini recibe candidatos verificables y devuelve IDs existentes, etiquetas y reason_codes enumerados. No permitas prosa libre que afirme horarios/requisitos. Define timeout y fallo controlado. No incluyas API keys en el resultado.

## P8 — Backend y catálogo (José)
> Implementa solo la tarea T[XX] en API/Repository/validador. Valida ID, scope FISI+CENTRAL, fuente, vigencia y estados. Usa Supabase solo si ya está listo y autorizado; conserva JSON local si no. No agregues CRUD ni logins.

## P9 — Prueba adversa / auditoría final
> Recorre RF-01…RF-22: para cada uno muestra test que lo prueba y resultado REAL ejecutado. Si no pudiste ejecutar, escribe NO EJECUTADO. Revisa prompt injection, HTML, ID inventado, proveedor caído, Supabase caído, fuente antigua y clínica/transportes. Veredicto: PASA / NO PASA / PENDIENTE. No inventes resultados.

## P10 — Cambio posterior a una spec
> NUEVA NECESIDAD: [detallar]. No toques código. Identifica RF, actualiza primero spec.md, después plan.md/api-contract.md/tasks.md, muestra cambios y pide aceptación de los tres integrantes si afecta contratos. Explica qué debemos volver a probar.
