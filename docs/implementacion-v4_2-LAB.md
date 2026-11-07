# Conecta UNMSM — Laboratorio v4.2 (corrección de reinicio e historial)

**Ámbito:** laboratorio SDD autorizado, no repositorio oficial de la competencia. No incluye claves ni datos personales reales. No modificar el catálogo de servicios existente ni inventar información universitaria.

## Hallazgos y decisiones

| Hallazgo | Corrección | Razonamiento |
|---|---|---|
| Nueva consulta aparecía pero no reaccionaba en la captura | Recursos `/static/app.js?v=4.2.1` y `/static/styles.css?v=4.2.1`, más `Cache-Control: no-store` en el laboratorio. Se conserva y prueba `newQuery()`. | La captura mostraba textos del JS anterior; esto es compatible con caché/mezcla de versiones. No atribuir un error a la lógica de reinicio cuando la versión cargada puede ser incorrecta. |
| Botón poco visible | Ajustes de CSS para botón secundario y distribución adaptable. | La intención debe ser obvia; no simular un enlace pequeño. |
| Historial invisible | Sección «Tus rutas guardadas» siempre visible con aviso explícito cuando aún no está habilitado. | El usuario puede entender qué existe y qué requisito falta sin alterar privacidad. |
| Casilla de guardado aparecía después del resultado | Botón «Guardar esta ruta» **después** del resultado, con `POST /api/history/save`. | Guardar es una decisión posterior al resultado. No se repite la llamada a Gemini ni se exige anticipar consentimiento. |
| Almacenamiento de rutas sin prueba de selección | Comprobante temporal HMAC-SHA256 firmado en el backend, con facultad, IDs, origen y hora, válido 30 min; el backend verifica vigencia y elegibilidad de los IDs antes de guardar. | No confiar en IDs arbitrarios enviados por el navegador. El comprobante no contiene la consulta. Reiniciar servidor invalida comprobantes previos, no el historial persistido. |
| Clave `sb_publishable_...` utilizada como Bearer en REST Auth | `apikey` siempre contiene la clave publicable; `Authorization: Bearer` solo si existe JWT de usuario. | Una clave publicable no es un JWT; Supabase necesita JWT de usuario para hacer cumplir RLS. |
| Histórico compartido | Supabase Auth por OTP, cookies HttpOnly SameSite Strict, políticas RLS `auth.uid() = user_id`, retención lógica de 30 días, borrado individual/total. | Propiedad verificable, aislamiento entre usuarios, minimización: no se guarda mensaje, email ni información clínica. |

## Reemplazar archivos en Windows

La carpeta original de trabajo sigue siendo `C:\conecta-unmsm-lab-v3`. Copiar el contenido del paquete **solo cambios** dentro de ella conservando las subcarpetas y sobrescribiendo únicamente los archivos listados. El ZIP completo contiene el laboratorio entero. Ambos excluyen `.env`, tokens y `.venv`.

No ejecutar `start-demo.bat` para usar Gemini y Supabase.

### Comprobar v4.2 sin historial privado

```powershell
cd C:\conecta-unmsm-lab-v3
.\.venv\Scripts\python.exe -m pytest -q -W error
.\start-supabase-gemini.bat
```

Abrir `http://127.0.0.1:8001/`. Usar `Ctrl + Shift + R` tras reemplazar archivos. Probar una consulta, pulsar «Nueva consulta» y comprobar que desaparecen la entrada, la tarjeta y las aclaraciones. La sección «Tus rutas guardadas» debe ser visible, mostrando **no activado** mientras `ENABLE_HISTORY=false`.

### Activar historial real (SOLO después de configurar y verificar)

1. En el **Supabase de laboratorio**, ejecutar `supabase/003_route_history.sql` una vez en SQL Editor. No borrar tablas de servicios existentes.
2. Configurar Supabase Auth > Email: OTP de código numérico y plantilla que contenga `{{ .Token }}`. Verificar recepción del correo en cuentas de prueba. El envío de correos depende del proveedor y límites de Supabase.
3. Comprobar RLS realmente con cuentas sintéticas A y B: A ve sus rutas, B no puede leerlas ni borrarlas, un anónimo recibe denegación; comprobar también que fallos no aparenten guardado. **Estos tests remotos no se han hecho desde este contenedor.**
4. Detener el servidor y arrancar solo la versión habilitada con el nuevo script:

```powershell
cd C:\conecta-unmsm-lab-v3
.\start-supabase-gemini-historial.bat
```

5. En la web: generar ruta → bajar a «Tus rutas guardadas» → solicitar y verificar código por correo → pulsar «Guardar esta ruta» → «Ver mi historial». Para nuevas consultas repetir el flujo de la ruta, conservando el inicio de sesión.

**No activar `ENABLE_HISTORY` para estudiantes reales ni producción con HTTP**: el script fija `COOKIE_SECURE=false` únicamente para `127.0.0.1`. En un dominio real se requiere HTTPS, `COOKIE_SECURE=true`, origen restringido, protección de abuso distribuida, revisión legal de privacidad y purga efectiva del historial vencido. Las consultas y los mensajes personales NO se guardan en la base.

## Pruebas realizadas aquí

- `python -m pytest -q -W error` → **109 pruebas aprobadas** (mocks de Auth/Supabase/Gemini; no pruebas remotas).
- `node --check frontend/app.js` → sintaxis válida.
- `python tests/browser_smoke.py` → recorrido de DOM real en Chromium: reinicio normal, cancelación de resultado tardío, estado del historial desactivado y, con respuestas HTTP simuladas, OTP, guardado posterior, visualización de historial y permanencia de historial al reiniciar consulta.
- `python -m compileall -q backend tests` → correcto.

**Pendiente de comprobar en el Supabase real:** migración aplicada, correo OTP enviado y recibido, permisos RLS con dos cuentas reales de prueba, escritura REST del historial y comportamiento multiusuario. No etiquetar como probado remotamente.
