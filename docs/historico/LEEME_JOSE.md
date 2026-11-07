# Paquete para José — Conecta UNMSM v4.4 LAB

Esta carpeta contiene una **maqueta funcional completa** como punto de partida, no solo fragmentos difíciles de ejecutar. El trabajo autorizado queda **limitado al rol JOSE**, documentado en `agents/JOSE.md`.

1. Leer `AGENTS.md`, `agents/JOSE.md` y `docs/sdd-v44/00-LEER-PRIMERO.md`.
2. Revisar `specs/002-laboratorio-v44/spec.md`, `plan.md` y `tasks.md`.
3. Configurar entorno privado y ejecutar tests; sin proveedores externos, se prueban los contratos con mocks.
4. Implementar solo la tarea propia aprobada, primero pruebas, luego código, commits por rol.
5. José integra **únicamente diffs de archivos propios** a un repo único; no reemplazar la copia integrada con este ZIP completo.

Comandos básicos: `python -m pytest -q -W error` y `node --check frontend/app.js`.

**No incluye `.env`, `.venv`, tokens ni cuentas reales**. El catálogo demo es sintético, las fuentes aportadas no se cargaron como fichas reales y las conexiones remotas requieren verificación independiente.
