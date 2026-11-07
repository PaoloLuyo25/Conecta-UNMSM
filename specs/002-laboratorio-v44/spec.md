# Spec 002 — Conecta UNMSM: actualización funcional LAB v4.4

**Estado:** especificación consolidada para la maqueta del laboratorio solicitada por el usuario; revisión cruzada del equipo pendiente. Complementa la spec 001 histórica sin reescribir sus RF ni revivir funciones descartadas. **No es autorización para incorporar código previo en el concurso.**

## Contexto y objetivo
Un estudiante describe una situación cotidiana y recibe una ruta adaptativa basada en servicios documentados. Desde v4.4, puede entrar como visitante o autenticarse de forma opcional para guardar rutas con consentimiento explícito. La UI no diagnostica ni inventa prestaciones.

## Usuarios / actores
Visitante, titular con cuenta de prueba, backend validador, sistema de identidad y catálogo; usuarios de facultades distintas de FISI con cobertura limitada a servicios centrales explícitamente universales.

## Historias de usuario
- H2-1: Como visitante quiero consultar sin cuenta para conocer opciones antes de registrarme.
- H2-2: Como titular quiero entrar con correo institucional y contraseña para recuperar rutas que guardé voluntariamente.
- H2-3: Como visitante quiero guardar una ruta después de registrarme sin repetir la consulta.
- H2-4: Como usuario quiero reiniciar una consulta para describir otra necesidad sin perder mi sesión.
- H2-5: Como persona que escribe abreviaturas quiero obtener ayuda cuando el significado esté documentado y, si no, una aclaración.

## Requisitos funcionales EARS
- **RF2-01:** CUANDO un visitante abra la aplicación sin sesión, EL SISTEMA mostrará las opciones de ingresar y continuar como visitante.
- **RF2-02:** CUANDO el visitante elija continuar sin cuenta, EL SISTEMA permitirá la consulta y mostrará resultados sin exigir inicio de sesión.
- **RF2-03:** CUANDO una persona envíe una consulta válida, EL SISTEMA mostrará una pregunta decisiva como máximo una vez o una ruta de hasta tres servicios documentados.
- **RF2-04:** SI falla la IA o el catálogo principal, ENTONCES EL SISTEMA informará la limitación sin presentar una personalización ficticia.
- **RF2-05:** CUANDO el usuario pulse «Nueva consulta», EL SISTEMA limpiará la consulta anterior e ignorará cualquier respuesta pendiente.
- **RF2-06:** CUANDO el usuario pulse «Nueva consulta» con sesión abierta, EL SISTEMA conservará la sesión y las rutas previamente guardadas.
- **RF2-07:** MIENTRAS una consulta esté en curso, EL SISTEMA mostrará su estado y evitará solicitudes duplicadas.
- **RF2-08:** SI el correo de registro o inicio de sesión no termina exactamente en `@unmsm.edu.pe`, ENTONCES EL SISTEMA rechazará esa autenticación.
- **RF2-09:** CUANDO un usuario envíe credenciales válidas al proveedor configurado, EL SISTEMA ofrecerá una sesión únicamente tras recibir confirmación válida del proveedor.
- **RF2-10:** CUANDO una persona consulte como visitante, EL SISTEMA no guardará automáticamente la ruta en un historial privado.
- **RF2-11:** CUANDO una persona pida guardar una ruta válida sin sesión, EL SISTEMA le ofrecerá autenticarse antes de intentar el guardado.
- **RF2-12:** CUANDO una persona se autentique después de solicitar el guardado, EL SISTEMA intentará guardar la ruta previamente seleccionada sin repetir el análisis de IA.
- **RF2-13:** SI no existe comprobante válido o la ruta ha caducado, ENTONCES EL SISTEMA rechazará el guardado sin inventar un resultado exitoso.
- **RF2-14:** CUANDO un titular guarde una ruta con consentimiento explícito, EL SISTEMA conservará solamente referencias a servicios y metadatos mínimos, sin el texto de la necesidad.
- **RF2-15:** SI un usuario intenta recuperar o borrar rutas de otra identidad, ENTONCES EL SISTEMA denegará el acceso.
- **RF2-16:** CUANDO el titular pida eliminar una ruta o su historial, EL SISTEMA realizará la operación únicamente sobre sus registros.
- **RF2-17:** SI el historial está desactivado o inaccesible, ENTONCES EL SISTEMA permitirá continuar la consulta sin afirmar que guardó la ruta.
- **RF2-18:** CUANDO una consulta de transporte contenga una zona abreviada inequívoca en contexto, EL SISTEMA utilizará la zona documentada.
- **RF2-19:** SI el distrito no aparece en la fuente canónica o su zona es ambigua, ENTONCES EL SISTEMA no inferirá una zona ni inventará paradas.
- **RF2-20:** CUANDO se consulte desde una facultad distinta de FISI, EL SISTEMA seleccionará únicamente servicios centrales documentados como disponibles para todas las facultades.
- **RF2-21:** CUANDO una ruta se muestre al usuario, EL SISTEMA obtendrá nombres, pasos, horarios, contactos y fuentes solamente de los datos institucionales aprobados.
- **RF2-22:** SI una cuenta o servicio carece de comprobación de disponibilidad o pertenencia institucional, ENTONCES EL SISTEMA no afirmará haber verificado esa condición.

## Requisitos no funcionales
- UI y mensajes en español, identificadores de código en inglés.
- Solicitud máxima: 800 caracteres visibles; aclaración de hasta 400.
- Contraseña tratada como secreto y nunca incluida en respuesta pública, logs, documentación ni frontend persistente.
- Cookies de sesión HttpOnly; Secure para HTTPS, protecciones Origin/CSRF y RLS antes de exponer historial real.
- Accesibilidad mínima por teclado, estados de carga para lectores de pantalla, reducción de movimiento cuando se solicite.

## Casos límite
Sesión preexistente; visitante que inicia sesión después; cierre de diálogo sin guardado; repetición de UUID; guardado doble; comprobante alterado/vencido; correo ajeno al dominio; token falsificado; IA devuelve ID inexistente; ambigüedad entre zonas; ausencia de datos del distrito; catálogo ficticio y evidencias caducadas.

## Fuera de alcance
OTP por correo, comprobación automática de matrícula, provisión de correo SMTP, recuperación de contraseña no configurada, diagnóstico/triage, citas reales, acciones en nombre de estudiantes, mapas/GPS/ETA, panel de administración, comunicaciones a oficinas y recomendaciones de servicios no documentados. **Producción con `Confirm Email OFF` está excluida.**

## Criterios de finalización
Todos los RF2 tienen prueba automatizada específica o verificación manual documentada; el flujo invitado→ruta→login→guardar funciona sin segunda consulta a Gemini; la suite regresiva original pasa; acceso remoto a Auth/RLS/Gemini se reporta verificado o pendiente de forma independiente; sin credenciales ni datos sensibles en entregables.

## Dudas abiertas
- [NECESITA ACLARACIÓN] ¿Cuándo habilitará el equipo confirmación de correo con SMTP o identidad institucional comprobada para salir de laboratorio?
- [NECESITA ACLARACIÓN] ¿Qué permisos de las bases del concurso autorizan reutilizar esta versión LAB?
- [NECESITA ACLARACIÓN] ¿Qué fuentes institucionales verificadas se publicarán en el catálogo real?
- [NECESITA ACLARACIÓN] ¿Se aportará el Markdown canónico de distritos?
