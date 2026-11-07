# Conecta UNMSM — José · versión de laboratorio 4.5 (multifacultad)

**Descarga de José sobre v4.4:** no reinstalar la base SQL 001 ni 003; aplicar solo 004 y 005, en ese orden. Esta versión incluye 20 nombres reales de facultades de la web oficial UNMSM y **140 escenarios inventados**, identificados de forma inequívoca como pruebas. No prueba disponibilidad, elegibilidad ni convocatorias reales.

**Primero:** lee `INICIO_CMD_MULTIFACULTAD.txt`; después `specs/003-multifacultad-demo/` y `agents/JOSE.md`.

**Cambios:** `backend/app/targeting.py`, filtros en `repository.py`, `route_service.py`, contrato aditivo en `api.py`, modelo Gemini más compacto, frontend selector + tipo de público, SQL 004/005, snapshot demo ampliado y tests.

**Ejemplos:** Facultad Medicina + posgrado + `Soy de posgrado y quiero viajar` muestra exclusivamente movilidad académica ficticia para posgrado; Derecho + pregrado + `Busco becas` devuelve beca ficticia de pregrado; Educación + docentes + `Becas para docentes` muestra beca ficticia dirigida a docentes. Sin perfil declarado se pregunta una vez.

**Privacidad:** `ENABLE_HISTORY=false` por defecto en BAT nuevo. El BAT con historial solo corresponde a localhost y a un Supabase LAB con RLS ya validado. No enviar secretos ni subir el paquete como aplicativo universitario oficial.

**Fuente de nombres de facultades:** https://www.unmsm.edu.pe/formacion-academica/facultades
**Modelo Gemini:** https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
