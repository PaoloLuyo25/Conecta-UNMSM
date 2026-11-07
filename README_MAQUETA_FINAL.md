# CONECTA UNMSM — MAQUETA FINAL v4.4 (laboratorio SDD)

**Esta es la versión integrada y ejecutable del laboratorio v4.4 extraída del RAR recibido**, no la antigua maqueta del plan v3. Trae código real, frontend, pruebas, documentación histórica, especificación delta SDD y agentes por propietario.

## Qué funciona en la base
Bienvenida; visitante; correo y contraseña opcionales para cuentas de prueba con dominio `@unmsm.edu.pe`; descripción de necesidad; rutas 1–3 servicios o pregunta de aclaración; modo degradado; nuevas consultas; guardado explícito de ruta con comprobante firmado; historial individual condicionado al proveedor.

La selección real de Gemini, acceso real a Supabase y guardado real de historiales solo operan después de configurar tu propio entorno y validar cuenta/permisos. `data/catalog.demo.json` es **ficticio** y el respaldo por defecto está vacío. No presenta ninguna integración institucional oficial.

## Estructura
```text
backend/app/                 FastAPI, Auth/Historial, repositorios, rutas, Gemini
frontend/                    HTML + CSS + JS de la interfaz web
data/                        fixture demo (ficticia) y snapshot vacío
supabase/                    SQL para catálogo/historial en laboratorio
tests/                       suite Python y smoke Chromium con red simulada
docs/                        documentación previa conservada y fuentes recibidas
docs/sdd-v44/                jerarquía actual, contratos, reparto, límites
specs/001-rutas-bienestar-mvp/ spec histórica
specs/002-laboratorio-v44/   spec EARS, plan y tareas de la actualización
agents/                      instrucciones por José, Paolo y Daniela
.claude/skills/spec-generator/ ayuda para redactar/revisar specs
```

## Arranque rápido (Windows CMD)
```bat
cd /d C:\conecta-unmsm-v4_4
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-supabase.txt
.venv\Scripts\python.exe -m pytest -q -W error
start-supabase-gemini-historial.bat
```
Antes de iniciar, copiar `.env.example` a `.env` **privado**, completar variables **solo en el equipo de trabajo** y configurar Supabase de laboratorio. Si no quieres historial, usa `start-supabase-gemini.bat`. Si solo se quieren pruebas locales y modo demo, revisar `start-demo.bat` y mantener **evidente** que los datos son ficticios. Navegador: `http://127.0.0.1:8001/` con el script de historial.

**Aviso crítico:** Confirm Email OFF no comprueba que una cuenta controle el buzón institucional; únicamente usar cuentas sintéticas de laboratorio. Para un entorno real se necesitan confirmación por correo/SMTP o autenticación institucional, HTTPS y verificación de RLS. No compartir contraseñas, claves, documentos sensibles ni datos reales. Evitar transferir código preexistente al concurso si sus bases no lo permiten.

## Organización del equipo
- José: `agents/JOSE.md` — backend, Auth/Supabase, datos e integración.
- Paolo: `agents/PAOLO.md` — Gemini, normalizador, distritos, pruebas adversas.
- Daniela: `agents/DANIELA.md` — UI, visitantes/login, estados, historial visible, smoke.
- Contrato de integración: `docs/sdd-v44/CONTRATO_API_ACTUAL.md`; reparto: `docs/sdd-v44/REPARTO_Y_MERGE.md`.

**Las tres maquetas separadas son copias funcionales completas de esta misma base con un `AGENTS.md` ajustado al rol.** Cada persona modifica únicamente los archivos indicados para evitar conflictos; la fusión de cambios se hace por Git/PR, no sobrescribiendo carpetas enteras.

## Validación
En el entorno de preparación se ejecutó `python -m pytest -q -W error` y pasaron **127 pruebas** sobre el código v4.4 original; las integraciones remotas no se ejecutaron. Revisar `docs/sdd-v44/ESTADO_Y_RIESGOS.md` para el alcance exacto.
