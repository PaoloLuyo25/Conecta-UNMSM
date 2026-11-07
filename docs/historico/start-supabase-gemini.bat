@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Primero instala el entorno con los pasos del README-V3.md
  pause
  exit /b 1
)
set "CATALOG_BACKEND=supabase"
set "FALLBACK_FILE=data/catalog.demo.json"
set "ALLOW_DEMO_RECORDS=true"
set "AI_MODE=gemini"
echo ============================================================
echo Conecta UNMSM - Supabase REAL + Gemini REAL
 echo ATENCION: catalogo FICTICIO; requiere claves propias en .env
 echo No usar esta configuracion con estudiantes reales.
echo ============================================================
echo Abre http://127.0.0.1:8001/
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
pause
