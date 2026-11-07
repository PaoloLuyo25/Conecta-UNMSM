# Ruta canónica SDD — Conecta UNMSM v4.4 (laboratorio)

**Versión de partida:** el código exacto recuperado de `conecta-unmsm-lab-v4_4-LAB.rar`. Las versiones `v3`, `v4`, `v4.2`, `v4.3` documentan la historia; **v4.4 manda** cuando describen comportamientos contradictorios.

**Jerarquía de trabajo:**
1. `docs/constitution.md`, incluida su adenda v4.4 de laboratorio.
2. `specs/001-rutas-bienestar-mvp/spec.md` (requisitos históricos) y `specs/002-laboratorio-v44/spec.md` (cambios funcionales posteriores).
3. `specs/002-laboratorio-v44/plan.md` y los contratos `docs/sdd-v44/CONTRATO_API_ACTUAL.md` + `docs/catalog-contract.md`.
4. `specs/002-laboratorio-v44/tasks.md`, instrucciones de `agents/` y pruebas bajo `tests/`.
5. Código existente en `backend/` + `frontend/`; cualquier cambio nuevo exige revisar el RF y escribir/actualizar prueba **antes** de editar lógica.

Este material reordena la implementación experimental **ya existente** y los cambios en v4.4; no convierte el proyecto en una aplicación de producción ni certifica API externa, correos, RLS o elegibilidad institucional.

## Reglas de partición
José, Paolo y Daniela reciben cada uno una **copia funcional completa** para ejecutar tests aislados. Solo deben modificar el conjunto de archivos que se les asigna, no todo lo que ven. José integra en un **repositorio único** por commits/PR de archivos propios. No sobrescribir el integrado extrayendo los tres ZIP uno detrás de otro: así podrían reemplazarse cambios ya integrados.

## Secuencia por cambio SDD
Solicitud → actualizar EARS de `spec.md` → aprobación equipo/alcance → modificar plan/contratos → tarea de 15–30 min con dueño y RF → test primero → cambio acotado → correr suite → registrar evidencia → commit/merge → validación manual con proveedor real cuando aplica.
