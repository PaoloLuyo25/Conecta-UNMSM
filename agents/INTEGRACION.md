# Agente integrador — José (solo después de aprobar los cambios)

- Para integrar un equipo real, partir de **un solo** repo creado a partir de `CONECTA_UNMSM_v4_4_MAQUETA_FINAL.zip`.
- Una rama por persona; transferir únicamente cambios de archivos propios de la matriz.
- Comparar el contrato actual, ejecutar pruebas de regresión, resolver conflictos por un dueño.
- Tratar las tres copias del proyecto como **bases de trabajo autónomas**. NO descomprimirlas secuencialmente sobre el integrado.
- Si una tarea altera el alcance, aprobar primero la actualización `spec.md` y `plan.md`; no cambiar contratos sobre la marcha.
- Los archivos `AGENTS.md` de los tres ZIP tienen un encabezado diferente por rol: conservar el AGENTS común del integrado, o actualizarlo por acuerdo.
- Los scripts `.bat` son para Windows/CMD; no exponer `.env`. El servidor de laboratorio usa `127.0.0.1:8001` para la ruta de Supabase/Gemini/historial.
