# Conecta UNMSM v4.3 — acceso con correo y contraseña (SOLO LABORATORIO)

## Qué cambió y por qué

- Reemplaza OTP/Magic Link por registro e inicio de sesión **correo + contraseña** mediante la API oficial de **Supabase Auth**. **No** se crea una base de contraseñas local: Supabase recibe el password a través del backend FastAPI por HTTPS y administra su verificación. No se envía a Gemini, al historial ni al navegador de regreso.
- Se conservan cookies de sesión HttpOnly, SameSite=Strict, RLS por `auth.uid()` y botón «Guardar esta ruta» explícito. **La consulta puede hacerse anónimamente**.
- Se actualiza frontend a `?v=4.3.0` para evitar mezclar JavaScript anterior con HTML nuevo.
- Las pruebas del backend usan dobles (`FakeIdentity`): **no demuestran entrega de correos, disponibilidad de Supabase ni aislamiento RLS remoto**.

## Configuración ya realizada por el usuario

1. `003_route_history.sql` ejecutado previamente. **No volver a ejecutarlo** sin una necesidad de migración.
2. Supabase → Authentication → Providers → Email: **Enable email provider ON** y **Confirm Email OFF**, solo para este laboratorio. Verificar que **Allow new users to sign up** esté activado en configuración general.
3. El usuario debe tener un `.env` privado válido en la misma carpeta (URL/key publicable de Supabase y clave Gemini) como en v4.2. No publicar en Git.

## Ejecución en Windows

```powershell
cd C:\conecta-unmsm-lab-v3
.\.venv\Scripts\python.exe -m pytest -q -W error
.\start-supabase-gemini-historial.bat
```

Abrir `http://127.0.0.1:8001/` y actualizar con Ctrl+Shift+R. El historial exige que `/api/features` devuelva `{"history_enabled":true}`. Si el puerto 8001 está ocupado, cerrar la versión anterior con Ctrl+C.

## Prueba manual con cuentas sintéticas

1. Usar un correo **de prueba** (no datos reales de estudiantes) y una contraseña exclusiva para Conecta, nunca la contraseña real de Gmail/UNMSM.
2. En «Tus rutas guardadas», pulsar **Crear cuenta**; verificar sesión iniciada sin correo/OTP.
3. Generar «Necesito información de bienestar», pulsar «Guardar esta ruta» y después «Ver mi historial».
4. Cerrar sesión y volver a ingresar con **Iniciar sesión**; comprobar que la ruta persiste.
5. Crear segunda cuenta de prueba (otra dirección), comprobar que no ve ni elimina rutas de la primera. Complementar con pruebas REST/RLS **reales con JWT independientes** antes de considerar aprobado el aislamiento.

## Limitaciones y decisiones de seguridad

- **Confirm Email OFF no comprueba que alguien controle la dirección utilizada**. No registrar usuarios reales ni usar direcciones ajenas. No presentar este inicio de sesión como verificación de matrícula UNMSM. En producción requerirá verificación, prevención de abuso y recuperación de cuenta.
- **Sin un proveedor de correo configurado, no está garantizado el flujo de recuperar contraseña**; si se pierde la contraseña de prueba habrá que usar otra cuenta o un restablecimiento administrado. No se debe utilizar este patrón como solución final de identidad.
- El registro de contraseñas reales a través de HTTP no debe usarse fuera de `localhost`. En producción activar `COOKIE_SECURE=true`, `PUBLIC_ORIGIN=https://...` y HTTPS.
- El historial almacena IDs de servicio, facultad y sello de tiempo, pero no el texto de la consulta; `expires_at` solo filtra en lectura y **no elimina físicamente** filas sin tarea de purga.
- Los servicios actuales son ficticios. El archivo de distritos verificados sigue pendiente si no se aportó una lista oficial en Markdown.
- No guardar credenciales, contraseñas ni tokens en capturas o chats.

## Archivos modificados

- `backend/app/auth_history.py`: nuevas funciones `sign_up` y `sign_in` con validación de sesión.
- `backend/app/auth_api.py`: `/api/auth/signup` y `/api/auth/login`, validación, rate limit, sesión HttpOnly.
- `frontend/index.html`: formulario nuevo y recursos v4.3.0.
- `frontend/app.js`: registro/login y guardado vinculado a sesión.
- `frontend/styles.css`: disposición de botones.
- `start-supabase-gemini-historial.bat`: comentario actualizado.
- `tests/test_auth_history_v4.py`, `tests/test_supabase_auth_headers.py`, `tests/browser_smoke.py`: pruebas adaptadas.
- `tests/test_password_auth_v4_3.py`: pruebas nuevas de validación y seguridad.
