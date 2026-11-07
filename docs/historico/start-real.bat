@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Falta el entorno virtual. Sigue los pasos de README-LAB.md.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
pause
