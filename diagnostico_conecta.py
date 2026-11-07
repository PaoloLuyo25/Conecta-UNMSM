"""Diagnóstico local de Conecta UNMSM v3.

Ejecutar: .venv\\Scripts\\python.exe diagnostico_conecta.py

No imprime claves, tokens, URLs ni mensajes completos de proveedores.
Usa una consulta FICTICIA para comprobar la integración real con Gemini.
Puede consumir una petición de la cuota de Gemini.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import re

from backend.app.ai_adapter import GeminiAdapter
from backend.app.config import BASE_DIR, Settings
from backend.app.local_repo import LocalCatalogRepository
from backend.app.repository import list_eligible
from backend.app.supabase_repo import SupabaseCatalogRepository
from backend.app.validator import validate_selection

CODES = {400, 401, 402, 403, 404, 408, 422, 429, 500, 502, 503, 504}


def cause_of(error: BaseException) -> BaseException:
    seen: set[int] = set()
    while error.__cause__ is not None and id(error.__cause__) not in seen:
        seen.add(id(error))
        error = error.__cause__
    return error


def classify(error: BaseException) -> tuple[str, str]:
    root = cause_of(error)
    code = getattr(root, 'code', None) or getattr(root, 'status_code', None)
    try:
        code = int(code)
    except (TypeError, ValueError):
        match = re.search(r'\b(400|401|402|403|404|408|422|429|500|502|503|504)\b', str(root))
        code = int(match.group(1)) if match else None

    raw_class = type(root).__name__
    # Se inspecciona el mensaje únicamente para clasificarlo; jamás se imprime.
    raw_text = str(root).lower()
    if 'timeout' in raw_class.lower() or 'timed out' in raw_text or 'timeout' in raw_text:
        return 'TIEMPO DE ESPERA', f'{raw_class}: aumenta GEMINI_TIMEOUT_SECONDS y revisa la conexión.'
    if 'modulenotfound' in raw_class.lower() or 'importerror' in raw_class.lower():
        return 'DEPENDENCIA AUSENTE', f'{raw_class}: instala requirements-supabase.txt.'
    hints = {
        400: 'Solicitud rechazada: podría ser formato/schema JSON o configuración del proyecto.',
        401: 'Credencial inválida, caducada o no reconocida.',
        402: 'Revisa la facturación o los créditos de la cuenta.',
        403: 'Permisos insuficientes, API no habilitada o restricciones de la clave.',
        404: 'Modelo o recurso no disponible para esta API/cuenta.',
        408: 'Tiempo de respuesta agotado.',
        422: 'Formato de solicitud inválido.',
        429: 'Cuota o límite de peticiones alcanzado.',
        500: 'Error del proveedor.',
        502: 'Error temporal de un servidor intermedio.',
        503: 'Servicio del proveedor temporalmente indisponible.',
        504: 'Timeout del proveedor.',
    }
    if code in CODES:
        return f'HTTP {code}', f'{raw_class}: {hints[code]}'
    if 'schema' in raw_text or 'additionalproperties' in raw_text or 'validation' in raw_class.lower():
        return 'ESQUEMA', f'{raw_class}: la salida estructurada no cumple el esquema.'
    return 'OTRO', f'{raw_class}: consulta la configuración y dependencias (sin divulgar secretos).'


def main() -> None:
    settings = Settings.from_env()
    print('=== CONECTA UNMSM: DIAGNÓSTICO SEGURO ===')
    print('No se mostrarán las claves ni se utilizarán datos reales de estudiantes.')
    print('Modo indicado en .env:')
    print('  Catálogo:', settings.catalog_backend)
    print('  IA:', settings.ai_mode)
    print('  Modelo:', settings.gemini_model)
    print('  Supabase URL presente:', 'SÍ' if settings.supabase_url else 'NO')
    print('  Clave publicable Supabase presente:', 'SÍ' if settings.supabase_anon_key else 'NO')
    print('  Clave Gemini presente:', 'SÍ' if settings.gemini_api_key else 'NO')

    print('\n[1] Consulta REAL de lectura a Supabase:')
    eligible = []
    try:
        snapshot = SupabaseCatalogRepository(settings.supabase_url, settings.supabase_anon_key).read()
        eligible = list_eligible(snapshot, faculty_code='FISI', as_of=date.today(),
                                 allow_demo_records=True)
        count_other = len(list_eligible(snapshot, faculty_code='OTRA', as_of=date.today(),
                                        allow_demo_records=True))
        print('  CONEXIÓN OK. Registros visibles:', len(snapshot.services))
        print('  Elegibles FISI (solo laboratorio):', len(eligible))
        print('  Elegibles otras facultades (solo laboratorio):', count_other)
        if not snapshot.services:
            print('  AVISO: ninguna fila visible. Revisa seed, is_public y RLS en Supabase.')
        elif not eligible:
            print('  AVISO: las filas visibles no son elegibles; revisa campos/estados/fechas.')
    except Exception as exc:
        label, hint = classify(exc)
        print('  FALLO:', label, '-', hint)
        print('  El backend podría estar mostrando el catálogo de respaldo, no Supabase.')

    print('\n[2] Prueba REAL de Gemini con texto sintético (puede consumir cuota):')
    if not settings.gemini_api_key:
        print('  NO EJECUTADO: falta GEMINI_API_KEY en .env.')
        return
    if not eligible:
        try:
            snapshot = LocalCatalogRepository(BASE_DIR / 'data/catalog.demo.json').read()
            eligible = list_eligible(snapshot, faculty_code='FISI', as_of=date.today(),
                                     allow_demo_records=True)
            print('  Se usarán candidatos FICTICIOS locales para aislar el fallo de Gemini.')
        except Exception as exc:
            print('  AVISO: tampoco se pudo preparar el catálogo local:', classify(exc)[0])
    try:
        adapter = GeminiAdapter(settings.gemini_api_key, settings.gemini_model,
                                timeout_seconds=settings.gemini_timeout_seconds)
        result = adapter.choose('Quiero solamente información de bienestar universitario.',
                                None, False, eligible)
        cards, rejected = validate_selection(result.selected_ids, result.reason_codes,
                                             eligible, as_of=date.today())
        print('  CONEXIÓN GEMINI OK: salida estructurada recibida.')
        print('  Servicios seleccionados por Gemini:', len(result.selected_ids))
        print('  Servicios aceptados por el validador:', len(cards))
        print('  IDs descartados o razones inválidas:', len(rejected))
        print('  Solicitó aclaración:', 'SÍ' if result.ask_clarification else 'NO')
        if not cards and not result.ask_clarification:
            print('  AVISO: la API funciona, pero esta selección no produjo tarjetas válidas.')
    except Exception as exc:
        label, hint = classify(exc)
        print('  FALLO:', label, '-', hint)
        print('  La aplicación volverá a mostrar "Sin IA" mientras continúe este problema.')
    print('\nPuedes compartir este resultado: NO contiene claves ni respuestas crudas del proveedor.')


if __name__ == '__main__':
    main()
