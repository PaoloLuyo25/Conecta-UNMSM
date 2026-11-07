# Conecta UNMSM — laboratorio SDD v3

**Desarrollo experimental autorizado, NO repositorio ni entrega del concurso.**
El código reutilizado del laboratorio no se incorporará al repositorio competitivo sin
confirmación escrita de las bases. La aplicación **no está avalada por UNMSM**.

## Qué hay

- Formulario con ámbito **FISI** u **otra facultad**.
- FISI recibe fichas FISI y centrales elegibles; otras facultades solo registros **centrales** con `accessible_to_all_faculties=true`. Que un servicio sea `CENTRAL` **no** implica acceso universal.
- Banco de preguntas controladas; solo una aclaración. Evaluación IA: IDs permitidos, códigos de razón. Explicaciones, fuentes y pasos desde el catálogo, nunca texto institucional generado.
- Cuatro zonas de transporte FICTICIAS (`norte`, `sur`, `centro`, `este`), sin rutas/paradas/horarios/tarifas inventadas.
- Supabase/PostgreSQL con SQL `001_services.sql` + `002_seed_lab_FICTICIO.sql`, RLS y lecturas únicamente; respaldo local JSON de solo lectura.
- Conexión real de servidor a Gemini API, requiere **tu clave API**. Sin clave, respuesta `degraded`, no se finge IA.
- En modo local de demostración, el motor de selección es **simulado** y así se indica.

## 1. Instalar (Windows, PowerShell)

Extrae el ZIP. Abre PowerShell en la carpeta **que contiene** `requirements.txt`.

```powershell
cd C:\conecta-unmsm-lab-v3
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q -W error
```

## 2. Prueba inmediata SIN claves: demo local

```powershell
.\start-demo.bat
```

Abre http://127.0.0.1:8000/ . Selecciona **Otra facultad** y escribe:
`Necesito transporte hacia el norte`. Solo aparece una tarjeta sintética de
transporte; no aparecen orientaciones y beneficios exclusivos de FISI.

Otra prueba: `Necesito transporte` → una pregunta sobre zona → responde `sur` → tarjeta ficticia sur.
`Busco becas y bienestar` con **Otra facultad** → ninguna ruta, porque
no hay datos verificables de ese alcance.

## 3. Gemini REAL con catálogo ficticio local

1. Crea tu clave en [Google AI Studio](https://aistudio.google.com/apikey).
2. Copia `.env.example` a `.env` (`Copy-Item .env.example .env`) y en `.env` configura:

```dotenv
GEMINI_API_KEY=TU_CLAVE_PRIVADA
GEMINI_MODEL=gemini-3.5-flash-lite
```

3. Ejecuta `start-gemini-lab.bat`. El programa llama a Gemini desde el **backend**, nunca el navegador. Necesitas acceso, cuota y conexión reales. Las pruebas automatizadas no sustituyen esta prueba con tu cuenta. **Utiliza únicamente descripciones ficticias, no datos clínicos/personales.**

## 4. Supabase PostgreSQL REAL y registros de prueba

Esta configuración requiere crear un proyecto en tu propia cuenta Supabase. No se ha creado ni conectado una instancia remota desde este laboratorio.

1. Ve a [Supabase](https://supabase.com/dashboard), crea un proyecto **separado de pruebas**.
2. En SQL Editor, ejecuta **primero** `supabase/001_services.sql` para crear la tabla, restricciones, permisos y RLS.
3. Ejecuta **después** `supabase/002_seed_lab_FICTICIO.sql` para añadir los 10 servicios **sintéticos** y publicarlos solo en el proyecto de prueba. **No ejecutar este seed en producción.**
4. Obtén *Project URL* y *publishable key* en la configuración API de tu proyecto. No uses `service_role` ni una secret key.
5. Instala el SDK Supabase:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-supabase.txt
```

6. Completa en `.env` las claves sin comillas ni espacios alrededor del `=`:

```dotenv
SUPABASE_URL=https://TU-PROYECTO.supabase.co
SUPABASE_PUBLISHABLE_KEY=TU_CLAVE_PUBLICABLE
GEMINI_API_KEY=TU_CLAVE_GEMINI
GEMINI_MODEL=gemini-3.5-flash-lite
```

7. Ejecuta **`start-supabase-gemini.bat`**; abre http://127.0.0.1:8000/ .
8. **Validación real obligatoria**: en SQL Editor, verificar `select count(*) from public.services;` y comprobar desde un cliente con **rol `anon`** que solo hay lectura (SELECT) de `is_public=true`; un intento controlado de INSERT/UPDATE/DELETE debe ser denegado. No hacer esas operaciones con credenciales `service_role` porque su bypass de RLS invalida la prueba. Revisa el panel Network: no aparecen claves Gemini ni un token privilegiado de Supabase.

**Nota:** si Supabase falla, se muestra copia JSON de prueba `data/catalog.demo.json` etiquetada como respaldo. Para la modalidad conservadora reemplaza el respaldo con un snapshot real verificado y desactiva `ALLOW_DEMO_RECORDS`.

## 5. Arranque conservador (cero datos ficticios)

`start-real.bat` utiliza por defecto la copia vacía `data/catalog.snapshot.json` y `AI_MODE=gemini`, si no personalizaste el `.env`. Con este modo el sistema no inventará ninguna ficha oficial.

## 6. Árbol y configuración

| Ruta | Papel |
|---|---|
| `backend/app/api.py` | API HTTP, validación de facultad y límites |
| `backend/app/route_service.py` | Determina candidatos por facultad, pregunta única, respaldo |
| `backend/app/schemas.py` | Tipos y campo `accessible_to_all_faculties` |
| `backend/app/repository.py` | Regla FISI/otra y filtrado de catálogos |
| `backend/app/ai_adapter.py` | Gemini real o simulación honesta, JSON tipado |
| `backend/app/supabase_repo.py` | SDK Supabase, lectura de columnas explícitas |
| `frontend/index.html`, `frontend/app.js` | Selector de facultad y resultados seguros |
| `supabase/001_services.sql` | Creación de tabla, GRANTS, política RLS SELECT |
| `supabase/002_seed_lab_FICTICIO.sql` | Carga sintética a Supabase de laboratorio |
| `data/catalog.demo.json` | Registros ficticios para demo y respaldo |
| `tests/test_scope_v3.py` | Aislamiento de facultades + preguntas + inyección |
| `tests/test_supabase_v3.py` | Adaptador simulado y auditoría estática SQL |
| `docs/plan-operativo-v3.md` | Plan proporcionado por José, base técnica de esta versión |
| `docs/lab-test-report-v3.md` | Pruebas ejecutadas y límites pendientes |

## Verdad de los datos

El catálogo FICTICIO contiene información experimental para probar el flujo. No prueba que haya servicios de transporte universales reales ni trámites de FISI disponibles. Una ficha real solo puede sustituirlo cuando exista fuente, alcance, vigencia y autorización. No registrar datos privados. **La IA real no vuelve reales los datos ficticios.**
