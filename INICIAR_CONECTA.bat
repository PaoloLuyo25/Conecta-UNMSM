@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Falta el entorno. Consulta README.md para instalar los paquetes.
 pause
 exit /b 1
)
set "CATALOG_BACKEND=supabase"
set "CATALOG_FILE=data/catalog.academico.json"
set "FALLBACK_FILE=data/catalog.academico.json"
set "ALLOW_DEMO_RECORDS=false"
set "AI_MODE=gemini"
set "ENABLE_HISTORY=false"
set "COOKIE_SECURE=false"
echo CONECTA UNMSM - Oportunidades academicas y bienestar.
echo Abre http://127.0.0.1:8001
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
endlocal
