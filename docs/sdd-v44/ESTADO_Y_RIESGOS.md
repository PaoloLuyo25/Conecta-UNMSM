# Estado comprobado de la maqueta (laboratorio)

- Fuente: RAR v4.4 proporcionado por el equipo, sin recurrir al antiguo kit.
- Extracción: se omitieron `.env`, `.venv`, caches, bytecode y directorios de herramientas privados.
- Corrección no funcional en la distribución: `requirements.txt` cambió `httpx2>=2,<3` por `httpx>=0.28,<1`, que es la librería que importa realmente el código.
- Prueba en entorno de empaquetado del **código original recuperado**: `python -m pytest -q -W error` → **127 passed**. Ejecutar de nuevo tras cambios es obligatorio.
- Esta suite usa dobles/mock para Auth, Gemini y Supabase; su éxito no acredita conexión real.

## Pendientes antes de un despliegue verdadero
- Gemini: prueba real con modelo, cuota, respuesta estructurada y clave protegida.
- Supabase: conexión real, migraciones aplicadas en el proyecto correcto, permisos y políticas RLS con usuarios A y B reales de prueba, y fallo de escritura para anónimo.
- Autenticación: correo `@unmsm.edu.pe` es validación sintáctica solamente. `Confirm Email OFF` **no acredita posesión de correo**; deshabilitar producción hasta resolverlo.
- SMTP: no se acredita configuración ni entrega. Si se habilita confirmación por email sin OTP, validar enlace de confirmación y proveedor SMTP.
- Base: `catalog.demo.json` son registros ficticios; el `catalog.snapshot.json` es vacío. La evidencia recibida **no** se ha transformado automáticamente en filas de Supabase.
- Distritos: no se ha recibido en estos materiales el Markdown canónico `data/distritos_verificados.md`, por lo que no asignar distritos por intuición.
- Historial: se documentó SQL `003_route_history.sql`, pero no se verificó remotamente desde este empaquetado; expiración lógica no es purga física.
- Seguridad de red/despliegue: `COOKIE_SECURE=true` + HTTPS + `PUBLIC_ORIGIN` + limitación de abuso distribuida + política de privacidad antes de usuarios reales.
- Concurso: comprobar las bases y el permiso de reutilizar un laboratorio/código previo y fuentes de investigación.

**Estado de entrega:** maqueta de laboratorio íntegra, ejecución local probada mediante test automatizado, integraciones externas por verificar. No es certificación de producto desplegado.
