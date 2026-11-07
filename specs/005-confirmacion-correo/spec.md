# Conecta UNMSM · Confirmación de correo e historial

## Alcance
Conservar el acceso de invitados, el correo+contraseña institucional, sesiones HttpOnly, historial privado y reglas de no guardar texto libre.

## Requisitos EARS
- RF-AUTH-01: CUANDO el proveedor responda a un registro con credenciales de sesión válidas, EL SISTEMA verificará la identidad antes de establecer cookies HttpOnly.
- RF-AUTH-02: CUANDO el proveedor acepte el registro sin devolver sesión por requerir confirmación de correo, EL SISTEMA responderá `authenticated=false` y `confirmation_required=true`, sin establecer cookies.
- RF-AUTH-03: CUANDO la interfaz reciba `confirmation_required=true`, EL SISTEMA mantendrá abierto el diálogo y mostrará que se debe confirmar el correo y luego iniciar sesión con contraseña.
- RF-AUTH-04: SI el proveedor devuelve una respuesta sin una identidad identificable ni tokens, EL SISTEMA deberá tratarla como un fallo controlado y no iniciar sesión.
- RF-AUTH-05: MIENTRAS un usuario no esté autenticado, EL SISTEMA no guardará rutas bajo una identidad supuesta.
- RF-AUTH-06: EN TODO MOMENTO EL SISTEMA validará el dominio `@unmsm.edu.pe`; la coincidencia del dominio por sí sola no acredita matrícula ni identidad.

## Fuera de alcance
No se implementa login por enlace mágico, OTP, restablecimiento de contraseña ni recepción automática de tokens tras abrir un enlace de verificación. El usuario debe iniciar sesión después de confirmar.
