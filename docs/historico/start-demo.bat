@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Falta el entorno virtual. Sigue los pasos de README-LAB.md.
  pause
  exit /b 1
)
set "CATALOG_BACKEND=local"
set "CATALOG_FILE=data/catalog.demo.json"
set "ALLOW_DEMO_RECORDS=true"
set "AI_MODE=demo"
echo ===============================================
echo CONECTA UNMSM - LABORATORIO CON DATOS FICTICIOS
 echo Gemini NO se utiliza en esta demostracion.
echo ===============================================
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
pause
