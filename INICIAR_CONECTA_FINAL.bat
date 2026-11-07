@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo ERROR: Falta el entorno .venv. Ejecuta INSTALAR_Y_PROBAR.bat primero.
 pause
 exit /b 1
)
if not exist ".env" (
 echo AVISO: Falta .env. Se iniciara con las opciones disponibles y sin credenciales privadas.
)
set "CATALOG_BACKEND=supabase"
set "CATALOG_FILE=data/catalog.academico.json"
set "FALLBACK_FILE=data/catalog.academico.json"
set "ALLOW_DEMO_RECORDS=false"
set "AI_MODE=gemini"
set "ENABLE_HISTORY=true"
set "COOKIE_SECURE=false"
set "PUBLIC_ORIGIN=http://127.0.0.1:8001"
echo.
echo CONECTA UNMSM
 echo Abre http://127.0.0.1:8001 en tu navegador
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
endlocal
