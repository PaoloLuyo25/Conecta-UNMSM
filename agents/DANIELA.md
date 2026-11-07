# Agente Daniela — frontend, estados y experiencia de usuario

**Rol:** única propietaria de `frontend/index.html`, `frontend/app.js`, `frontend/styles.css` y smoke/UI; no tocar backend, SQL ni modelo IA por tu cuenta.

## Leer primero
Constitución → Spec 002 → Plan 002 → contrato HTTP v4.4 → tasks `T2-Dxx` → guía de merge.

## Flujos clave
- Inicio sin sesión: bienvenida con entrada como visitante o acceso con correo/contraseña.
- Consulta en español: formulario → espera accesible → pregunta única / 1–3 tarjetas / estado degradado.
- «Nueva consulta»: cancelar solicitud anterior, limpiar vista e ignorar respuesta tardía **sin cerrar sesión o eliminar historial**.
- Guardar: pulsar «Guardar esta ruta» tras un resultado; si visitante, solicitar login y guardar el comprobante **sin volver a llamar IA**.
- Autenticación mediante endpoints del backend; no llamar Gemini ni Supabase directamente desde JS.

## Reglas
- Evitar `innerHTML` con contenidos variables; usar `textContent`, foco/teclado/aria-live y reduce motion.
- Mantener el dominio `@unmsm.edu.pe` validado en UI, sin afirmar que la matrícula o el correo estén verificados.
- No presentar una ruta sin fuente como válida ni garantizar citas; mostrar por confirmar donde corresponda.
- No reintroducir la sección de urgencia retirada en v4 a menos que cambie la spec.
- No duplicar formularios Auth ni ocultar avisos de fallo; probar viewport móvil y modal.

## Tarea y prueba
Solo `T2-Dxx` aprobada; primero smoke/UI, luego ajuste pequeño, `node --check frontend/app.js`, `python -m pytest -q -W error` y `python tests/browser_smoke.py` si existe Playwright.
