# Colaboración Git + asistentes de IA

## Roles y propiedad de módulos
| Persona | Área futura | Integración acordada |
|---|---|---|
| José | `backend/app/main.py`, `routes.py`, `repository.py`, validación y configuración | Contrato API y fuente de datos; merge a `main` |
| Paolo | `backend/app/ai_adapter.py`, casos adversos / test de IA | Consume candidatos tipados; devuelve IDs/códigos |
| Daniela | `frontend/` y QA manual UI | Usa únicamente `/api/route`, no la API del modelo |

Nadie cambia contrato de datos o nombres de propiedades unilateralmente. Si una tarea afecta a dos módulos, se acuerda primero el cambio en Markdown y se implementa en ramas separadas.

## Ramas
- `main`: siempre demostrable, aprobada por José tras tests.
- `feature/api-jose`, `feature/ia-paolo`, `feature/ui-daniela` (o ramas nuevas y cortas por tarea).
- Commit pequeño y descriptivo por tarea, referenciando `Txx` y RF.
- Integraciones planificadas: primera ~10:00, segunda ~12:15, última ~14:40. Evitar force push a main.

## Flujo estándar
1. Hacer pull de `main` y crear rama propia.
2. Revisar la tarea y sus RF; pedir a la IA solo una tarea.
3. Escribir o pedir los tests primero (sin afirmar que pasaron hasta ejecutarlos).
4. Implementar, ejecutar tests y revisar `git diff`.
5. Hacer commit; integrar en `main` solo con pruebas básicas verdes.
6. Si falla integración, revertir el último cambio estable; **no** permitir tres agentes editando simultáneamente los mismos archivos.

## Qué puede y no puede hacer cada IA
- **ChatGPT:** clarificar requisitos, revisar API, errores, test adversos, defensa del jurado.
- **Claude:** segunda opinión y revisión de contradicciones. Claude web no ejecuta automáticamente instrucciones del archivo `SKILL.md`.
- **Cursor:** generar y editar código **solo después de autorización**, usando `AGENTS.md`, spec activa, plan y tarea indicada. AGENTS.md es entendido por Cursor; no se necesita Cursor Pro como requisito.
- **Gemini API:** IA que utiliza el producto para interpretar; no confundir con Gemini web usado para resolver dudas de Git.

## Seguridad del repositorio
- Crear `.gitignore` antes del primer commit de código; incluir `.env`, `.venv`, secretos, credenciales y archivos temporales.
- Nunca pegar keys en prompts, commits, capturas de OBS ni logs entregados al jurado.
- No almacenar mensajes reales de estudiantes ni documentos personales.
- Verificar permiso de material preparatorio bajo bases oficiales antes de incorporarlo a repo.
