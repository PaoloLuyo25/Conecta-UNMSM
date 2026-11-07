"""Orquestación de rutas: resultado honesto incluso si fallan datos o IA."""
from datetime import date
from backend.app.ai_adapter import AIUnavailable
from backend.app.local_repo import LocalCatalogRepository
from backend.app.repository import CatalogUnavailable, list_eligible, public_service
from backend.app.validator import validate_selection
from backend.app.normalization import normalize_query
from backend.app.targeting import detected_profile, detected_intents, shortlist


class RouteService:
    def __init__(self, repository, ai_adapter, settings, *, today=None, districts=None):
        self.repository = repository
        self.ai_adapter = ai_adapter
        self.settings = settings
        self.today = today or date.today
        self.districts = districts

    def _catalog(self, faculty_code: str = 'FISI'):
        warnings = []
        try:
            snapshot = self.repository.read()
        except CatalogUnavailable:
            if self.settings.catalog_backend != 'supabase':
                return [], 'unavailable', None, ['Catálogo no disponible; no se muestran rutas sin evidencia.']
            try:
                snapshot = LocalCatalogRepository(self.settings.fallback_file).read()
                warnings.append('Fuente principal inaccesible; se usa una copia local que puede estar desactualizada.')
            except CatalogUnavailable:
                return [], 'unavailable', None, ['La fuente principal y su respaldo no están disponibles.']
        try:
            eligible = list_eligible(snapshot, faculty_code=faculty_code, as_of=self.today(),
                                     allow_demo_records=self.settings.allow_demo_records)
        except CatalogUnavailable:
            return [], 'unavailable', None, ['El catálogo contiene IDs duplicados y no puede usarse.']
        if snapshot.source == 'local_snapshot':
            warnings.append('Catálogo local: comprueba la vigencia antes de utilizar un servicio.')
        if any(s.evidence_type.value == 'prueba_ficticia' for s in eligible):
            warnings.append('MODO DEMOSTRACIÓN: HAY REGISTROS FICTICIOS; CADA FICHA SE IDENTIFICA INDIVIDUALMENTE.')
        if not eligible:
            warnings.append('No hay servicios documentados elegibles para la facultad indicada.')
        return eligible, snapshot.source, snapshot.verified_at, warnings

    def catalog(self, faculty_code: str = 'FISI'):
        eligible, source, checked, warnings = self._catalog(faculty_code)
        return {
            'services': [public_service(s, as_of=self.today()) for s in eligible],
            'catalog_source': source,
            'catalog_verified_at': checked,
            'warnings': warnings,
        }

    def route(self, request):
        eligible, source, checked, warnings = self._catalog(request.faculty_code)
        if request.faculty_code != 'FISI' and not any(s.faculty_code == request.faculty_code for s in eligible):
            warnings.append('Fuera del piloto FISI original: no hay fichas específicas de esa facultad; solo se ofrecen servicios centrales universales.')
        base = dict(mode='degraded', needs=[], constraints=[], question=None, services=[],
                    warnings=warnings, ai_used=False,
                    catalog_source=source, catalog_verified_at=checked)
        if not eligible:
            return base
        normalized = normalize_query(request.message, request.clarification_answer,
                                     clarification_used=request.clarification_used,
                                     directory=self.districts)
        if normalized.district_unmapped:
            warnings.append('Distrito reconocido, pero su zona no figura en la fuente verificada.')
        if normalized.ambiguous:
            base.update(mode='question', question='¿Qué zona de transporte necesitas: norte, sur, centro o este?')
            base['warnings'].append('Hay zonas incompatibles; no se asignó ninguna automáticamente.')
            return base
        profile = detected_profile(request.message, request.clarification_answer, request.applicant_type)
        intents = detected_intents(request.message, request.clarification_answer)
        if (not profile and intents.intersection({'becas', 'movilidad_academica', 'oportunidades_academicas'})
                and any(s.category_code.value in {'becas', 'movilidad_academica', 'oportunidades_academicas'}
                        for s in eligible)):
            # No recomendar una beca de docentes a quien no especificó su perfil.
            if not request.clarification_used:
                base.update(mode='question', question='¿La consulta es para pregrado, posgrado o docentes?')
                return base
            base['warnings'].append('No se identificó el grupo de la convocatoria; indícalo en el selector.')
            return base
        candidates = shortlist(eligible, profile=profile, intents=intents,
                               faculty_code=request.faculty_code)
        if not candidates:
            base['warnings'].append('No hay registros documentados compatibles con el perfil y la necesidad indicados.')
            return base
        try:
            result = self.ai_adapter.choose(
                request.message + ('\n' + normalized.context_line if normalized.context_line else ''),
                (normalized.region_code if request.clarification_used and normalized.region_code
                 else request.clarification_answer),
                request.clarification_used, candidates)
        except Exception:
            # No disfrazar un catálogo de respaldo como recomendaciones personalizadas.
            base['services'] = [public_service(item, as_of=self.today()) for item in candidates[:3]]
            base['warnings'] = warnings + [
                'Gemini no está disponible; se muestra información de referencia, no una recomendación personalizada.'
            ]
            return base

        base['needs'] = result.needs
        base['constraints'] = result.constraints
        base['ai_used'] = self.ai_adapter.is_real
        if not self.ai_adapter.is_real:
            base['warnings'] = warnings + ['SIMULACIÓN: selección programada, Gemini no fue utilizado.']
        if result.ask_clarification and not request.clarification_used:
            # Banco controlado: ninguna pregunta de texto libre del LLM es visible.
            question_bank = {
                'modality': '¿Prefieres una modalidad presencial o virtual?',
                'region': '¿Qué zona de transporte te interesa: norte, sur, centro o este?',
            }
            modalities = {m for s in candidates for m in s.modality}
            regions = {s.route_region.value for s in candidates if s.route_region}
            allowed_questions = set()
            if {'presencial', 'virtual'}.issubset(modalities):
                allowed_questions.add('modality')
            if len(regions) > 1:
                allowed_questions.add('region')
            code = result.question_code
            if code in allowed_questions:
                base.update(mode='question', question=question_bank[code])
                return base
            base['warnings'].append('No se pudo formular una aclaración segura y respaldada por el catálogo.')
            base['ai_used'] = False
            return base

        cards, selection_warnings = validate_selection(
            result.selected_ids, result.reason_codes, candidates, as_of=self.today())
        base['warnings'].extend(selection_warnings)
        if cards:
            base.update(mode='route', services=cards)
        else:
            base['warnings'].append('No se identificó una ruta verificable para esta necesidad.')
            # No atribuir selección válida a una llamada que no produjo resultados.
            base['ai_used'] = False
        return base
