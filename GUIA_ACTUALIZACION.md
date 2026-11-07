# Conecta UNMSM — FISI/Otros, OCGRI histórico y VRAP investigación

Esta entrega modifica el proyecto ya publicado; **no es otra aplicación** y no reemplaza Supabase Auth ni el historial. Producto independiente, no institucional.

## Qué cambió
- Solo `FISI` y `Otros` en la interfaz. `Otros` se envía a la API como `OTROS` y recibe únicamente servicios centrales probadamente universales.
- Ante «Soy estudiante de pregrado y quiero viajar a Francia» se muestra la guía general de movilidad OGCRI y una sección separada de **antecedentes cerrados**. El plazo Bordeaux de Francia 2027-I venció el 1/10/2026. El anuncio indicaba «próximamente» para otras sedes: eso no demuestra una inscripción abierta. También se incluyeron antecedentes Francia 2025-I y 2024-I, Corea (Keimyung 2027-I), México (UACJ 2027-I) y una convocatoria histórica de investigación VRIP.
- VRAP: prioriza investigación formativa, con la guía publicada por ese Vicerrectorado.
- Durante una petición aparece «Cancelar búsqueda» y se indica actividad; guardar una ruta muestra «Guardando ruta…» y luego el resultado. **El historial guarda IDs de la ruta, no el texto libre ni automáticamente las fichas históricas**.
- Alta de cuenta: se recomienda iniciar sesión a quien tenga cuenta. Con `Confirm Email` habilitado, Supabase puede ocultar si la cuenta existe; no es posible garantizar un aviso inequívoco sin introducir enumeración de correos.

## Aplicar en Windows

1. Respaldar la carpeta y `.env` PRIVADO. Descargar la entrega completa o el parche.
2. Con **el ZIP completo**, descomprimir en `C:\Users\josem\Downloads\conecta-unmsm`, reemplazando archivos de código. No sobrescribir el `.env` local (no viene en el ZIP).
3. Para poner solo los cambios en el repositorio `C:\Users\josem\Downloads\Conecta-UNMSM-repo`, descomprimir el ZIP **SOLO_CAMBIOS** dentro del repositorio, conservando las rutas internas, y ejecutar:

```bat
cd /d "C:\Users\josem\Downloads\Conecta-UNMSM-repo"
git switch main
git pull --ff-only origin main
.venv\Scripts\python.exe -m pytest -q
git status --short
git diff --check
git add backend frontend data/catalog.academico.json supabase/008_antecedentes_ogcri_investigacion.sql tools tests/test_historico_fisi_otros.py specs/006-fisi-otros-antecedentes README.md AGENTS.md GUIA_ACTUALIZACION.md docs/api-contract.md docs/FUENTES_REVISADAS.md
git diff --cached --name-only
git commit -m "FISI y Otros, antecedentes OCGRI y mejoras de acceso"
git push origin main
```

Si `.venv` no está en el clon, instala Python 3.12: `py -3.12 -m venv .venv` y `.venv\Scripts\python.exe -m pip install -r requirements-supabase.txt`. No uses `push --force`.

## SQL en Supabase (solo el nuevo)

**Ya tienes `001_services.sql` y `006_categorias_academicas.sql`.** Ejecuta en SQL Editor solo `supabase/008_antecedentes_ogcri_investigacion.sql`. El SQL es idempotente y actualiza únicamente ocho registros revisados; **no toca `route_history`, Auth ni RLS**, no elimina datos previos y no agrega datos personales.

Verificar:

```sql
SELECT id, name, category_code, availability_status, valid_until, source_url
FROM public.services
WHERE id IN (
  'CENTRAL-OGCRI-FRANCIA', 'CENTRAL-OGCRI-FRANCIA-2025',
  'CENTRAL-OGCRI-FRANCIA-2024','CENTRAL-OGCRI-MEXICO-2027I',
  'CENTRAL-OGCRI-COREA','CENTRAL-VRAP-GUIA-INVESTIGACION')
ORDER BY id;
```

Las filas OGCRI de intercambio vencido deben aparecer con `cerrado_documentado`. La guía VRAP es orientación, no una convocatoria abierta.

## Probar

```bat
cd /d "C:\Users\josem\Downloads\conecta-unmsm"
.venv\Scripts\python.exe -m pytest -q
INICIAR_CONECTA_HISTORIAL_LAB.bat
```

Abre http://127.0.0.1:8001. Consultas útiles:
- `Soy estudiante de pregrado y quiero viajar a Francia.`
- `Soy estudiante de pregrado y quiero ir a México.`
- `Soy estudiante y quiero viajar a Canadá.` (sin historia verificable en el catálogo; no inventar)
- `Soy de pregrado y necesito orientación para hacer investigación formativa en VRAP.`
- `Soy de FISI y necesito bienestar universitario.` / selecciona **Otros** para verificar que no se atribuyan servicios FISI.

## Explorar fuentes y mantener el catálogo

```bat
.venv\Scripts\python.exe -m tools.explorar_fuentes --historical-pages 2
```

El comando consulta feeds y archivo público OGCRI, además de feeds VRAP/VRIP, solo si `robots.txt` lo permite. Guarda hallazgos en `data/discovered.pending.json` (ignorado por Git). **No es un importador SQL automático.** Revisar a mano cada enlace, fechas, destinatarios y fuente, y luego generar SQL con `python -m tools.generar_sql_catalogo`. No se ha ejecutado una extracción remota completa desde esta sesión.

## Limitaciones
- Los plazos históricos fueron contrastados en las páginas originales, pero **no se probó que no existan convocatorias posteriores**. La respuesta se refiere al catálogo revisado.
- RLS, SMTP y Gemini reales requieren prueba desde tu Supabase y tu cuenta; las pruebas incluidas usan simulaciones.
- Nunca copiar `.env` al repositorio. Las claves se configuran en la máquina/servidor, no en Git.
