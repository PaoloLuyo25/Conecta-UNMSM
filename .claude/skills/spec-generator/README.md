# Uso del spec-generator

Copia de la metodología del video, adaptada a Conecta UNMSM. `SKILL.md` y `spec-template.md` pertenecen a esta carpeta.

- **Claude Code:** se puede colocar en `.claude/skills/spec-generator/` y solicitar que use `spec-generator`.
- **Claude web/ChatGPT:** adjuntar `SKILL.md` o pegar el prompt de `samples/prompts.md`; **no** asumir que la skill se ejecuta automáticamente.
- **Cursor:** usa `AGENTS.md` como regla de proyecto; para generar specs, copiar el prompt de `samples/prompts.md`. No depende de Cursor Pro.
- **OpenCode:** si realmente se instala, copiar esta carpeta a `.opencode/skill/spec-generator/`. En Windows no asumir que los symlinks del ejemplo sobreviven al ZIP.

**Regla:** editar una sola versión fuente de la skill; cualquier copia se debe sincronizar deliberadamente. No instalar herramientas extra para el MVP si no aportan valor.
