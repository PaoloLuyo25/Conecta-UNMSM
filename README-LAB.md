> **VERSIÓN ACTUAL: v4.4 LAB.** Para instalar en CMD y usar la bienvenida con inicio de sesión opcional, lee [INICIO_CMD_v4_4.txt](INICIO_CMD_v4_4.txt) y [docs/implementacion-v4_4-LAB.md](docs/implementacion-v4_4-LAB.md). La información que sigue documenta etapas anteriores.

> **Guía actual del historial privado:** [docs/implementacion-v4_3-LAB.md](docs/implementacion-v4_3-LAB.md). Este documento describe una versión antigua del laboratorio (puede contener referencias a OTP).

> **AVISO:** Esta guía describe la versión previa. Para la implementación v3 con otras facultades, Gemini y SQL Supabase, consulta [README-V3.md](README-V3.md).

# Conecta UNMSM — laboratorio SDD (versión integral)

**Actualización:** 6 de noviembre de 2026. **No es repositorio ni entrega oficial de ENEISOFT.**
Este laboratorio existe por autorización de la cláusula 11 de `docs/constitution.md`. Las bases del evento mantienen prioridad sobre cualquier reutilización de código previo.

## 1. Arrancar en Windows — demostración funcional, SIN API key

1. Descomprimir el ZIP, por ejemplo en `C:\conecta-unmsm-lab`. Mantener todas las carpetas.
2. Abrir PowerShell **dentro** de esa carpeta, la que contiene `requirements.txt`.
3. Ejecutar:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q -W error
.\start-demo.bat
```

4. Abrir **http://127.0.0.1:8000/** (interfaz). La ventana `.bat` debe permanecer abierta.
5. Para salir, `Ctrl+C` en esa ventana.

**Importante:** el modo `start-demo.bat` utiliza `data/catalog.demo.json` (seis servicios elegibles FICTICIOS y uno fuera de facultad que debe excluirse) con un algoritmo simulado que NO llama a Gemini. Está etiquetado permanentemente como SIMULACIÓN. Es útil para probar el flujo sin gastos, datos reales ni claves.

### Ejemplos de prueba

- `Necesito orientación para adaptarme a la universidad` → una pregunta; responder `Prefiero modalidad virtual` → tarjeta ficticia virtual.
- `Busco información de bienestar y alimentación` → tarjeta ficticia de bienestar.
- `Quiero información sobre transporte hacia el norte` → solo registro ficticio norte; sin inventar paradas, precios ni horarios.
- `Necesito orientación y prefiero modalidad virtual` → tarjeta virtual; abajo escribir `ahora prefiero modalidad presencial` → reevaluar y pasar a otra tarjeta de demostración.
- La opción «Necesito ayuda urgente» funciona sin consultar IA.

## 2. Arranque conservador sin datos ficticios

En PowerShell: ` .\start-real.bat `. Usa por defecto `data/catalog.snapshot.json`, que está **vacío deliberadamente**. No promete servicios ni instituciones verificadas. El modo degradado indica falta de catálogo.

## 3. Activar Gemini real SOLO si tienes una key funcional

1. Copia `.env.example` a `.env` y edita `.env` localmente. **Nunca compartas ese archivo ni subas la key a Git.**
2. Configura por lo menos:

```dotenv
AI_MODE=gemini
GEMINI_API_KEY=TU_CLAVE_PRIVADA
GEMINI_MODEL=gemini-2.5-flash
CATALOG_BACKEND=local
CATALOG_FILE=data/catalog.demo.json
ALLOW_DEMO_RECORDS=true
```

3. Usa `start-real.bat`. La interfaz mostrará los registros como **FICTICIOS**, aunque Gemini sea real. Cambiar a una clave o modelo no valida la cuota, disponibilidad o corrección de la selección: debe probarse en el equipo.
4. Para funcionamiento con registros verificables, carga únicamente información autorizada en `data/catalog.snapshot.json`, modifica `CATALOG_FILE=data/catalog.snapshot.json` y pon `ALLOW_DEMO_RECORDS=false`.

**Privacidad:** no pruebes Gemini con situaciones clínicas o datos personales reales. El mensaje se envía al proveedor cuando se usa el adaptador real; este laboratorio no almacena el texto de la consulta en una base de datos.

## 4. Supabase opcional (NO probado en nube)

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-optional-supabase.txt
```

En `.env`, usar `CATALOG_BACKEND=supabase`, `SUPABASE_URL`, `SUPABASE_ANON_KEY` y `FALLBACK_FILE`. La tabla pública `services` requiere columnas compatibles con `docs/catalog-contract.md`. **Comprobar manualmente RLS SELECT y que INSERT/UPDATE/DELETE sin autorización no funcionan; no se ha comprobado en una instancia real.** Si falla la lectura, el backend retorna el snapshot de respaldo y lo identifica como tal.

## 5. Archivos y responsabilidades

| Archivo o carpeta | Función |
|---|---|
| `backend/app/main.py` | Arranque FastAPI, frontend y API en mismo origen |
| `backend/app/api.py` | `GET /api/health`, `GET /api/services`, `POST /api/route`; límites de entrada |
| `backend/app/schemas.py` | Entidad de servicios, categorías, estados y fechas |
| `backend/app/route_service.py` | Orquestación; aclaración, ruta o degradación |
| `backend/app/ai_adapter.py` | Gemini real y simulador local claramente identificado |
| `backend/app/validator.py` | Verificación de IDs y reason codes; máximo 3 resultados |
| `backend/app/repository.py` | Elegibilidad de ámbito y vigencia; salida pública |
| `backend/app/local_repo.py` | Lectura segura del JSON local |
| `backend/app/supabase_repo.py` | Lectura Supabase opcional, sin escritura |
| `backend/app/config.py` | Configuración por variables de entorno |
| `frontend/index.html` | Interfaz y opción de ayuda humana |
| `frontend/styles.css` | Vista responsive |
| `frontend/app.js` | Consume API y renderiza con `textContent` |
| `data/catalog.demo.json` | SOLO datos sintéticos etiquetados ficticios |
| `data/catalog.snapshot.json` | Catálogo vacío hasta aportar evidencias autorizadas |
| `tests/` | Tests automáticos sin red, claves ni datos reales |
| `docs/lab-test-report.md` | Informe de qué se ejecutó realmente y qué falta probar |

## 6. Límites reales

- **Se ejecutó** `python -m pytest -q -W error` en este laboratorio y se registró el resultado en el reporte.
- **Se comprobó** vía HTTP que `/api/health` retorna 200 y que `/api/services` retorna seis entradas de demo FISI/CENTRAL (ninguna de otra facultad).
- **Se comprobó** la interfaz en Chromium con respuestas API simuladas (pregunta → tarjeta, botón urgente, sin errores JS). No se pudo abrir el servidor real desde Chromium debido a la política de navegación del entorno de pruebas; realizar la comprobación end-to-end en tu navegador.
- **No se ha probado** Gemini con una clave real, el modelo real, la cuota, Supabase o RLS con un servidor real.
- No se han incorporado datos institucionales verificados; por eso la DEMO no es material válido para presentar servicios reales ante jurado.
- Es un prototipo de exploración, no un sistema oficial ni un servicio de triaje, agenda o atención clínica.

## 7. Pruebas y documentación

```powershell
.\.venv\Scripts\python.exe -m pytest -q -W error
```

Documentación SDD original en `docs/`, `specs/001-rutas-bienestar-mvp/` y `.claude/skills/spec-generator/`. Los estados y pendientes se detallan en `docs/lab-test-report.md`. Si se modifica el contrato acordado, debe revisarse primero el plan/spec con el equipo.
