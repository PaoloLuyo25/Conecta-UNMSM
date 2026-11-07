# Conecta UNMSM · Configuración de correo y publicación

## Supabase: diferencia entre SMTP e historial
Activar SMTP solamente permite a Supabase enviar correos (si el proveedor funciona). No habilita el historial en la app.

En Supabase:
1. **Authentication > Providers > Email**: habilitar Email y **Confirm Email** para comprobar titularidad.
2. **Authentication > SMTP Settings**: comprobar que la configuración fue guardada. Gmail `smtp.gmail.com`, puerto 465 o 587, cuenta de envío autorizada y contraseña de aplicación (no la contraseña normal). Preferir proveedor transaccional en producción.
3. **Authentication > URL Configuration**: **Site URL** `http://127.0.0.1:8001`. Si se usa una lista de redirecciones, agregar ese origen con el puerto exacto.
4. **Authentication > Users / Auth Logs**: verificar si se creó el usuario, si se mandó el correo y si está confirmado. No compartir tokens, contraseñas ni logs con datos sensibles.
5. En Supabase SQL Editor comprobar existencia de `public.route_history` creada por `supabase/003_route_history.sql`; comprobar políticas de RLS.

## En Windows CMD

```bat
cd /d "C:\Users\josem\Downloads\conecta-unmsm"
.venv\Scripts\python.exe -m pytest -q
INICIAR_CONECTA_HISTORIAL_LAB.bat
```

Abrir `http://127.0.0.1:8001/api/features` y esperar `{"history_enabled":true}`. Después abrir `/` para crear usuario con correo `@unmsm.edu.pe`, verificar enlace recibido e iniciar sesión con contraseña. Si hay bloqueo 429, esperar a la ventana permitida, sin intentar crear cuentas masivamente. El `.env` se conserva local, no se sube a Git.

## Subir al repositorio existente con ramas
El repositorio de equipo ya tiene `main` y ramas `feature/jose-api`, `feature/paolo-ai`, `feature/daniela-ui`. Todas comenzaron sobre el mismo README inicial, por lo que NO se debe iniciar otro historial Git independiente ni usar `git push --force`.

```bat
cd /d "C:\Users\josem\Downloads"
git clone https://github.com/PaoloLuyo25/Conecta-UNMSM.git Conecta-UNMSM-repo
robocopy "C:\Users\josem\Downloads\conecta-unmsm" "C:\Users\josem\Downloads\Conecta-UNMSM-repo" /E /XD .git .venv __pycache__ .pytest_cache /XF .env *.pyc *.log
cd /d "C:\Users\josem\Downloads\Conecta-UNMSM-repo"
git status --short
git add -A
git diff --cached --name-only
git commit -m "Base integradora Conecta UNMSM con correo confirmado"
git push origin main
```

Antes de `git commit`, revisar con `git diff --cached --name-only` que NO aparezcan `.env`, respaldos, credenciales ni proyectos ajenos. La carpeta destino del clone debe estar vacía o no existir. Si la carpeta ya existe con un clone, NO repetir `git clone`; en ese caso hacer `git pull --ff-only origin main` y copiar los archivos, en este orden.

Cada integrante puede actualizar su rama **antes de iniciar cambios nuevos**, realizando `git fetch origin`, cambiando a la rama correspondiente y fusionando `origin/main`. No borrar ni forzar ramas ya creadas.

## Gemini
Para comprobar el error de Gemini sin exponer claves, ejecutar desde la carpeta raíz:

```bat
.venv\Scripts\python.exe diagnostico_conecta.py
```

El comando consulta Supabase y consume una petición real de Gemini usando texto ficticio. Compartir solo el diagnóstico final que no incluye secretos. Comprobar `.env`: `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.5-flash-lite` y `GEMINI_TIMEOUT_SECONDS=20` si el diagnóstico identifica tiempo agotado; no subir `.env`.
