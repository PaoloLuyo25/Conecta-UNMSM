# Conecta UNMSM v4.4 — entrada opcional y validación de correo (LABORATORIO SDD)

## Alcance

Se ha añadido una pantalla de bienvenida, navegación como visitante, botón permanente «Iniciar sesión» / «Mis rutas» en cabecera, ventana de autenticación reutilizable, y guardado explícito de una ruta cuando un visitante decide entrar posteriormente. **No** se modificó la selección de Gemini, el catálogo de Supabase, el filtro FISI/otras facultades ni la estructura SQL del historial.

## Decisiones de implementación — cómo y por qué

1. **Bienvenida en frontend, sin redireccionamiento real**. Se añadió `#welcome-screen` y se oculta `#app-main` hasta elegir una modalidad. Así se preservan los dos paneles existentes y no se duplica el backend. Si `/api/auth/me` encuentra una sesión válida, se entra directamente al área de consulta; de lo contrario se ofrece visitante o acceso.
2. **Acceso opcional mediante ventana superpuesta**. `#auth-overlay` reutiliza el formulario correo/contraseña existente en vez de crear un segundo formulario con estados incongruentes. La cabecera ofrece acceso incluso tras elegir visitante. El historial privado se consulta en esa misma ventana después del inicio de sesión.
3. **Guardado diferido sin repetir Gemini**. El botón «Guardar esta ruta» aparece solo tras una ruta válida y cuando la función de historial está habilitada. Si es visitante, se conserva **en memoria del navegador** el comprobante temporal firmado que emitió el backend, se abre el formulario y, tras autenticarse correctamente, se intenta guardar esa misma ruta. Si se cierra el formulario se cancela la intención de guardado. La ruta no se guarda automáticamente al generar un resultado, incluso si ya se ha iniciado sesión.
4. **Comprobación del dominio en cliente, API y sesión**. El frontend valida `@unmsm.edu.pe`; el modelo Pydantic rechaza cualquier otro dominio en `/api/auth/signup` y `/api/auth/login`; `SupabaseIdentity.user` examina también el correo obtenido por el endpoint autenticado `/auth/v1/user`, evitando que una sesión antigua asociada a otro dominio continúe utilizando el historial a través del backend. Se normalizan mayúsculas y espacios exteriores. Las contraseñas siguen siendo administradas por Supabase Auth.
5. **Seguridad y privacidad conservadas**. Cookies HttpOnly, mismo origen, validación `Origin` en mutaciones, RLS según el SQL ya aplicado, comprobante firmado/temporal, idempotencia y almacenamiento únicamente de IDs de servicios, ámbito, procedencia y fecha. Ni el texto original de la consulta ni la contraseña se almacenan en historial.

## Limitación de identidad importante

La comprobación del sufijo **no verifica la propiedad del buzón ni demuestra ser estudiante UNMSM**. Con `Confirm Email` desactivado, una persona puede escribir un correo institucional ajeno y registrar una cuenta si aún está libre. Por eso esta variante es únicamente para laboratorio con datos y usuarios de prueba. Antes de producción se necesita verificar correo y/o autenticación institucional. No publicar ni aceptar datos personales reales bajo estas condiciones.

## Qué cambió respecto de v4.3

| Tipo | Archivo | Cambio |
|---|---|---|
| Modificado | `frontend/index.html` | Pantalla de bienvenida, cabecera y ventana de autenticación, mensaje de guardado |
| Modificado | `frontend/app.js` | Estado de entrada, apertura/cierre de acceso, guardado post-login y verificación del correo |
| Modificado | `frontend/styles.css` | Estilos responsive de bienvenida y modal |
| Modificado | `backend/app/auth_api.py` | Validación exacta del dominio institucional en login/registro |
| Modificado | `backend/app/auth_history.py` | Validación del dominio en cada identidad verificada ante Supabase |
| Modificado | `backend/app/main.py` | Identificación v4.4 |
| Modificado | `tests/test_auth_history_v4.py` | Datos sintéticos admitidos y versión HTML |
| Modificado | `tests/test_password_auth_v4_3.py` | Pruebas actualizadas para correo UNMSM |
| Nuevo | `tests/test_optional_access_v4_4.py` | Pruebas de dominio, endpoints y estructura UI |
| Modificado | `tests/browser_smoke.py` | Pruebas Chromium para ambos flujos y sesión previa, sin red real |
| Nuevo | `INICIO_CMD_v4_4.txt` | Comandos CMD y notas de inicio |

## Pruebas realizadas en este laboratorio

- `python -m pytest -q -W error`: **127 passed**.
- `node --check frontend/app.js`: sintaxis correcta.
- `python tests/browser_smoke.py`: Chromium con respuestas **simuladas**: visitante → ruta → inicio de sesión → guardado de la ruta sin volver a llamar IA; inicio de sesión → consulta → guardado inmediato; correo no UNMSM rechazado en frontend; sesión previa omite bienvenida.
- **No se ejecutaron** peticiones reales de registro, inicio de sesión, guardado ni prueba RLS con cuentas reales en tu Supabase desde este entorno. Realízalas manualmente y con usuarios de prueba autorizados antes de considerarlas verificadas.

## Preparación y ejecución

Ver `INICIO_CMD_v4_4.txt`. El archivo `.env` se agrega localmente y **no forma parte de la distribución ZIP**. El SQL `supabase/003_route_history.sql` ya fue ejecutado anteriormente según lo indicado; no es una migración nueva ni hace falta aplicarlo de nuevo para esta versión. Iniciar mediante `start-supabase-gemini-historial.bat`, no mediante `start-demo.bat`.

Si el servidor tarda en crear la sesión, la ruta puede expirar (comprobante válido durante unos 30 minutos): en ese caso se debe generar otra vez antes de guardarla.
