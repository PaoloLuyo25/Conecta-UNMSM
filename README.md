# Conecta UNMSM

**Orientación universitaria contextual, con oportunidades académicas documentadas.** Proyecto independiente: **no** es un sitio ni un servicio oficial de la UNMSM.

Desde un mismo campo de texto, una persona plantea su situación (por ejemplo: *«Soy un estudiante de posgrado y quiero viajar para hacer investigación»*). El servidor elige hasta seis candidatos del catálogo mediante reglas de facultad, público e intención; Gemini selecciona como máximo tres IDs. **Ningún dato institucional es generado por Gemini:** nombres, requisitos, plazos, contacto y fuentes proceden de registros revisados. El sistema no verifica inscripción abierta en tiempo real.

## Qué incluye

- Las 20 facultades en un selector. Servicios académicos centrales publicados por OGCRI, VRAP y VRIP; programas propios de facultades solo para sus destinatarios.
- Rutas de Bienestar FISI, Clínica Universitaria y transporte externo conservadas **con advertencias de alcance y vigencia**.
- Acceso opcional con Supabase Auth (correo `@unmsm.edu.pe` y contraseña); consulta como invitado. Historial separado, opcional y desactivado por defecto.
- `tools/explorar_fuentes.py`: consulta feeds públicos de OGCRI Blog, OGCRI, VRAP y VRIP respetando `robots.txt`. Genera `data/discovered.pending.json`: **no publica anuncios ni atribuye elegibilidad automáticamente**.
- `data/catalog.academico.json`: catálogo inicial de 15 registros revisados manualmente a partir de páginas externas accesibles y documentos aportados por el equipo, con trazabilidad y advertencias. Nueve registros corresponden a publicaciones web académicas; los demás son apoyos con cobertura por verificar.
- `supabase/EJECUTAR_CATALOGO_ACADEMICO.sql`: migración aditiva + registros para aplicar desde SQL Editor **con cuenta administradora**. No cambia políticas RLS ni autenticación.
- Docs SDD `specs/004-oportunidades-academicas/` y `docs/`; pruebas `tests/`.

## Preparación en Windows (CMD)

La carpeta puede ser `C:\Users\josem\Downloads\conecta-unmsm` (o extraer los contenidos sobre tu carpeta existente, tras respaldar tu `.env`).

```bat
cd /d "C:\Users\josem\Downloads\conecta-unmsm"
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements-supabase.txt
if not exist .env copy .env.example .env
notepad .env
.venv\Scripts\python.exe -m pytest -q -W error
INICIAR_CONECTA.bat
```

Configura `.env` con `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `GEMINI_API_KEY` y `GEMINI_MODEL=gemini-3.5-flash-lite`. Mantén `.env` fuera de Git. Abre http://127.0.0.1:8001/ . Si falla Supabase, la app usa `data/catalog.academico.json` con advertencia de copia local; si falta Gemini, responde con modo degradado explícito. No colocar ninguna clave en JS.

### Supabase

Ya tienes `public.services` con RLS y lectura pública. **No repitas el SQL de creación 001 ni el seed ficticio 005.** Ejecuta únicamente `supabase/EJECUTAR_CATALOGO_ACADEMICO.sql` (primero amplía categorías sin borrar datos; después inserta/actualiza IDs `CENTRAL-*`, `MEDICINA-*` y `FISI-*`). En la tabla, los datos de `prueba_ficticia` previos pueden permanecer para tests pero la app normal los excluye con `ALLOW_DEMO_RECORDS=false`.

Verifica en Supabase SQL Editor:

```sql
select evidence_type, category_code, count(*) from public.services
where is_public = true group by evidence_type, category_code order by 1,2;
```

Para leer mediante la clave publicable, prueba SELECT; los roles `anon`/`authenticated` **no** deben poder escribir. Ejecutar el SQL desde el Editor no significa que ya se haya comprobado el acceso real ni la fecha de cada convocatoria.

### Actualizar hallazgos de web scraping

```bat
.venv\Scripts\python.exe -m tools.explorar_fuentes
```

Solo genera `data/discovered.pending.json`. Ante robots bloqueado, error de red o cambios de HTML, informa y no inventa resultados. Revisa individualmente cada candidato: titular, fuente original, destinatarios (pregrado / posgrado / docentes), plazos, requisitos, facultad, vigencia y si es beca **o únicamente convenio**. Tras revisar, modifica `data/catalog.academico.json`, actualiza la fecha de revisión y ejecuta:

```bat
.venv\Scripts\python.exe -m tools.generar_sql_catalogo
```

Ejecuta el SQL generado manualmente desde Supabase SQL Editor. **Nunca** copies directamente `discovered.pending.json` a la base. Si cambias el catálogo con nuevas categorías, haz una migración aprobada.

### Historial y login

El login existente se conserva. `INICIAR_CONECTA.bat` deja `ENABLE_HISTORY=false` para no recopilar datos; habilítalo en laboratorio **solo** después de configurar Auth, correo, HTTPS para cualquier despliegue y probar RLS con dos cuentas autorizadas. `INICIAR_CONECTA_HISTORIAL_LAB.bat` es **exclusivo para localhost y pruebas**. Desactivar confirmación por correo **no verifica titularidad ni matrícula**.

### Publicar en GitHub (repositorio remoto vacío)

Crea o elige tu repositorio y copia su URL HTTPS. En esta carpeta:

```bat
git init
git branch -M main
git add .
git status --short
git commit -m "Base integradora Conecta UNMSM"
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Si ya existe `origin`, usa `git remote -v` y no repitas `git remote add origin`. **No enviar `.env`, claves, `.venv` ni `discovered.pending.json`.** No es posible subir a tu repositorio desde esta entrega sin su URL y acceso autorizado.

## Seguridad y procedencia

- Las publicaciones universitarias son **fuentes**; no equivalen a aceptación, financiación o inscripción vigente. Los sitios pueden cambiar entre escaneos.
- Los convenios normalmente exoneran costos académicos bajo condiciones, pero no necesariamente cubren pasajes o manutención.
- Los datos de Clínica de noviembre 2026 no garantizan citas o atención actual. No se realizan diagnósticos ni trámites.
- Leer `AGENTS.md`, `docs/constitution.md`, la spec activa y los tests antes de modificar código. Respetar las bases de la hackathon sobre código preexistente.
