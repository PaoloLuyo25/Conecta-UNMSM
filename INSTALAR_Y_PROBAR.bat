@echo off
setlocal
cd /d "%~dp0"
echo.
echo === CONECTA UNMSM - Instalacion y comprobacion ===
if not exist "pyproject.toml" (
 echo ERROR: No esta pyproject.toml junto a este BAT.
 echo Extrae TODOS los archivos del ZIP directamente en esta carpeta.
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
 echo Creando entorno virtual con Python 3.11...
 py -3.11 -m venv .venv
 if errorlevel 1 (
  echo ERROR: Instala Python 3.11 de 64 bits y reintenta.
  pause
  exit /b 1
 )
)
.venv\Scripts\python.exe -m pip install -e ".[dev]"
if errorlevel 1 (
 echo ERROR: No se pudieron instalar las dependencias. Revisa la salida.
 pause
 exit /b 1
)
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 (
 echo ERROR: Alguna prueba fallo. Revisa la salida.
 pause
 exit /b 1
)
echo.
echo Pruebas aprobadas. Si existe tu .env, ejecuta INICIAR_CONECTA_HISTORIAL_LAB.bat
pause
endlocal
