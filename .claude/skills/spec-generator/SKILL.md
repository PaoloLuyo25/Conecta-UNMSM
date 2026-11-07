---
name: spec-generator
description: Genera o revisa especificaciones SDD de Conecta UNMSM conforme a la constitución y la plantilla del equipo.
---

# Generador de specs — Conecta UNMSM

Adapta la skill del material de referencia. **No crea código del MVP** y nunca inventa información institucional.

1. Lee `docs/constitution.md`, `docs/context.md`, specs previas en `specs/` y `docs/architecture-decisions.md`.
2. Si el usuario pide una spec nueva, formula **de una en una** hasta seis preguntas que cambien requisitos. No repitas decisiones vigentes ya documentadas.
3. Si existe una ambigüedad no respondida, marca `[NECESITA ACLARACIÓN: ...]` y continúa solo con lo decidido; no llenes silenciosamente.
4. Al crear usa el siguiente prefijo disponible `specs/NNN-nombre/` y plantilla `spec-template.md`.
5. En `spec.md` escribe **solo QUÉ/por qué**, criterios EARS, historias, límites, requisitos no funcionales y DoD; nunca frameworks o nombres de archivos de código.
6. Solicita aprobación explícita antes de generar `plan.md` o `tasks.md`. Si el usuario pide revisión, identifica contradicciones, ambigüedades, casos límite y conflictos sin reescribir salvo que lo solicite.
7. Nunca asumas como verificadas rutas FISI, clínicas, vehículos, precios, horarios, paradas o becas sin documentación adjunta.
8. Al entregar, indica RF afectados y marca las decisiones PENDIENTES/PROPUESTAS/DECIDIDAS.

## EARS
- Ubicuo: `EL SISTEMA <comportamiento>`.
- Evento: `CUANDO <evento>, EL SISTEMA <resultado>`.
- Estado: `MIENTRAS <estado>, EL SISTEMA <resultado>`.
- Condición no deseada: `SI <condición>, ENTONCES EL SISTEMA <resultado>`.

## Límite de alcance
Especificaciones y planes son documentos; la implementación de código requiere permiso y cumplir las bases del evento. **Prohibido afirmar que una spec fue validada sin pruebas ejecutadas.**

La cláusula 11 de la constitución permite prototipos reales en un laboratorio separado; esta skill sigue siendo exclusivamente documental.
