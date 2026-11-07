"""Filtros deterministas de intención y público para reducir candidatos del LLM.

Ningún match inventa convocatorias, requisitos ni cobertura. Se filtra antes de
invocar Gemini; el backend vuelve a validar los IDs al componer la respuesta.
"""
import re
import unicodedata

VALID_PROFILES = {'pregrado', 'posgrado', 'docentes'}
MAX_GEMINI_CANDIDATES = 6


def normalized(value: str) -> str:
    value = ''.join(c for c in unicodedata.normalize('NFD', value.lower())
                    if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', value).strip()


def detected_profile(message: str, clarification: str | None, selected: str) -> str | None:
    full = normalized(message + ' ' + (clarification or ''))
    found = []
    patterns = {
        'posgrado': r'\b(posgrado|postgrado|maestria|doctorado|doctoranda|doctorando)\b',
        'pregrado': r'\b(pregrado|cachimbo|cachimba)\b',
        'docentes': r'\b(docente|docentes|profesora|profesor|catedratic[oa])\b',
    }
    for code, expression in patterns.items():
        if re.search(expression, full):
            found.append(code)
    if selected in VALID_PROFILES:
        # No ignorar una contradicción explícita entre selector y mensaje.
        return selected if not found or set(found) == {selected} else None
    return found[0] if len(found) == 1 else None


def detected_intents(message: str, clarification: str | None) -> set[str]:
    full = normalized(message + ' ' + (clarification or ''))
    result = set()
    if re.search(r'\b(viajar|viaje|viajes|intercambio|intercambios|estancia|estancias|movilidad academica|internacionalizacion|movilidad saliente)\b', full):
        result.add('movilidad_academica')
    if re.search(r'\b(beca|becas|subvencion|financiamiento)\b', full):
        result.add('becas')
    if re.search(r'\b(convocatoria|convocatorias|convenio|convenios|oportunidad|oportunidades|proyecto|proyectos|investigacion|talleres|actividades academicas|vrap|vrip|ogcri)\b', full):
        result.add('oportunidades_academicas')
    if re.search(r'\b(transporte|bus|buses|autobus|rutas|ruta de transporte|paradero|cono norte|cono sur)\b', full):
        result.add('transporte_externo')
    if re.search(r'\b(orientacion|adaptarme|adaptacion|bienestar|alimentacion|comedor|'
                 r'problemas? economicos?|dificultades? economicas?|situacion economica|'
                 r'condicion economica|escasos recursos|pocos recursos|sin recursos|'
                 r'necesidad economica|economia familiar|vulnerabilidad economica|apoyo economico)\b', full):
        result.add('bienestar')
    # Vivir lejos puede justificar INFORMACIÓN de transporte, pero no demuestra
    # una ruta, parada o cobertura en el distrito descrito.
    if re.search(r'\b(vivo lejos|vivo muy lejos|me queda lejos|vivo distante|traslado largo)\b', full):
        result.add('transporte_externo')
    if re.search(r'\b(clinica|consulta medica|medicina general|atencion general|odontologia)\b', full):
        result.add('clinica_general')
    if re.search(r'\b(psicologia|salud mental|estres|ansiedad|apoyo emocional)\b', full):
        result.add('salud_mental')
    return result


def audience_codes(service) -> set[str]:
    return {part.strip() for part in (service.audience or '').split(',')} & VALID_PROFILES


def shortlist(services, *, profile: str | None, intents: set[str],
              faculty_code: str, limit: int = MAX_GEMINI_CANDIDATES, message: str = ""):
    # audience en el catálogo histórico puede ser texto humano: solo los códigos
    # controlados de esta demo activan una restricción automática.
    pool = [s for s in services if not audience_codes(s)
            or (profile is not None and profile in audience_codes(s))]
    if intents:
        def matches(service):
            category = service.category_code.value
            tags = set(service.needs_tags)
            if 'bienestar' in intents and category == 'unayoe':
                return True
            return any(i == category or i in tags for i in intents)
        pool = [s for s in pool if matches(s)]
    # Fuente específica de la facultad antes de datos centrales; no deducir que
    # un convenio general es una beca para cada estudiante.
    # Datos precisos de la facultad elegida antes de opciones centrales.
    # No mover los originales si el orden importa en la demo anterior.
    focus = normalized(message)
    def research_priority(service):
        tags = set(service.needs_tags)
        if 'vrap' in focus:
            return 0 if 'vrap' in tags else 2
        if 'investigac' in focus or 'investigar' in focus:
            return 0 if 'investigacion_formativa' in tags else (1 if 'investigacion' in tags else 2)
        if 'ogcri' in focus:
            return 0 if 'ogcri' in tags or 'CENTRAL-OGCRI' in service.id else 2
        return 1
    pool.sort(key=lambda s: (research_priority(s), 0 if s.faculty_code == faculty_code else 1,
                             0 if profile in audience_codes(s) else 1,
                             s.id.startswith('DEMO-MF-') is False,
                             s.id))
    # Para consultas con dos necesidades, reservar una plaza por categoría.
    if len(intents) > 1:
        picked = []
        for intent in sorted(intents):
            for s in pool:
                if s.id not in {x.id for x in picked} and (s.category_code.value == intent or intent in s.needs_tags):
                    picked.append(s)
                    break
        pool = picked + [s for s in pool if s.id not in {x.id for x in picked}]
    return pool[:limit]


# Solo destinos reconocidos explícitamente; no se infieren países a partir de
# similitudes léxicas. En Supabase deben etiquetarse `pais_francia`, etc.
COUNTRIES = {
    'francia': 'Francia', 'alemania': 'Alemania', 'espana': 'España',
    'mexico': 'México', 'china': 'China', 'japon': 'Japón',
    'corea del sur': 'Corea del Sur', 'colombia': 'Colombia',
    'brasil': 'Brasil', 'argentina': 'Argentina', 'canada': 'Canadá',
}

def detected_country(message: str, clarification: str | None = None) -> tuple[str, str] | None:
    text = normalized(message + ' ' + (clarification or ''))
    for code, label in sorted(COUNTRIES.items(), key=lambda item: -len(item[0])):
        if re.search(r'(?<![a-z])' + re.escape(code) + r'(?![a-z])', text):
            return code.replace(' ', '_'), label
    return None
