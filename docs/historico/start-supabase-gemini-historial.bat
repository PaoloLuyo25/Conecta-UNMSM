@echo off
setlocal
cd /d "%~dp0"
REM SOLO LABORATORIO: requiere supabase/003_route_history.sql, correo/contraseña (sin confirmación, solo laboratorio) y pruebas RLS.
set "ENABLE_HISTORY=true"
set "COOKIE_SECURE=false"
call "%~dp0start-supabase-gemini.bat"
endlocal
