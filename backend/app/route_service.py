"""Orquestación de rutas: resultado honesto incluso si fallan datos o IA."""
from datetime import date
from backend.app.ai_adapter import AIUnavailable
from backend.app.local_repo import LocalCatalogRepository
from backend.app.repository import CatalogUnavailable, list_eligible, list_historical, public_service
from backend.app.validator import validate_selection
from backend.app.normalization import normalize_query
from backend.app.targeting import detected_profile, detected_intents, detected_country, shortlist


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
        # «Otros» puede consultar las referencias CENTRALES de transporte de la
        # UNMSM incluso si su cobertura por facultad aún no fue confirmada.
        # Es acceso informativo, NO una afirmación de servicio universal.
        if faculty_code in {'OTRA', 'OTROS'}:
            from backend.app.schemas import CategoryCode, AvailabilityStatus, EvidenceType
            ids = {item.id for item in eligible}
            for service in snapshot.services:
                if (service.id not in ids and service.faculty_code == 'CENTRAL'
                        and service.category_code == CategoryCode.TRANSPORTE_EXTERNO
                        and service.route_region and service.source_url
                        and service.evidence_type != EvidenceType.TEST
                        and service.availability_status != AvailabilityStatus.CLOSED
                        and not (service.valid_until and service.valid_until < self.today())
                        and not (service.valid_from and service.valid_from > self.today())):
                    eligible.append(service)
                    ids.add(service.id)
            if any(s.category_code == CategoryCode.TRANSPORTE_EXTERNO for s in eligible):
                warnings.append(
                    'Transporte UNMSM: la cobertura por facultad, paradas y horarios '
                    'deben confirmarse con la fuente antes de viajar.')
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

    def _cover_multiple_needs(self, candidates, cards, intents):
        """Preserva como máximo tres fichas reales, con una por necesidad relevante."""
        if len(intents) < 2:
            return cards
        by_id = {s.id: s for s in candidates}
        selected = []
        # Bienestar primero en perfiles vulnerables; no perderlo por elegir dos
        # fichas de movilidad académica. El transporte va primero si fue explícito.
        for intent in ('transporte_externo', 'bienestar', 'movilidad_academica',
                       'becas', 'oportunidades_academicas', 'clinica_general', 'salud_mental'):
            if intent not in intents:
                continue
            for service in candidates:
                if (service.category_code.value == intent or intent in service.needs_tags
                        or (intent == 'bienestar' and service.category_code.value == 'unayoe')):
                    if service.id not in {x['id'] for x in selected}:
                        selected.append(public_service(service, as_of=self.today()))
                        break
            if len(selected) >= 3:
                return selected[:3]
        # Conservar recomendaciones válidas de IA, sin rebasar el límite del historial.
        for card in cards:
            if card['id'] in by_id and card['id'] not in {x['id'] for x in selected}:
                selected.append(card)
            if len(selected) >= 3:
                break
        return selected[:3]

    def route(self, request):
        eligible, source, checked, warnings = self._catalog(request.faculty_code)
        base = dict(mode='degraded', needs=[], constraints=[], question=None, services=[],
                    historical_services=[], country_context=None,
                    warnings=warnings, ai_used=False,
                    catalog_source=source, catalog_verified_at=checked)
        if not eligible:
            return base
        normalized = normalize_query(request.message, request.clarification_answer,
                                     clarification_used=request.clarification_used,
                                     directory=self.districts)
        if normalized.district_unmapped:
            warnings.append('Distrito reconocido, pero su zona no figura en la fuente verificada.')
        intents = detected_intents(request.message, request.clarification_answer)
        transport_only = intents == {'transporte_externo'}
        chosen_transport = []
        if normalized.ambiguous and transport_only:
            if not request.clarification_used:
                base.update(mode='question', question='¿Qué zona de transporte necesitas: norte, sur, centro o este?')
            base['warnings'].append('Se mencionaron zonas incompatibles. Indica una sola zona.')
            return base
        if 'transporte_externo' in intents:
            transport = [s for s in eligible if s.category_code.value == 'transporte_externo']
            if not normalized.region_code or normalized.ambiguous:
                if transport_only and not request.clarification_used:
                    base.update(mode='question', question='¿Qué zona de transporte necesitas: norte, sur, centro o este?')
                    return base
                if transport_only:
                    base['warnings'].append('No se identificó una sola zona. Indica norte, sur, centro o este.')
                    return base
                base['warnings'].append(
                    'También puedes consultar transporte externo indicando norte, sur, centro o este. '
                    'La distancia a tu domicilio no permite confirmar una parada ni una ruta.')
            else:
                chosen_transport = [s for s in transport if s.route_region
                                    and s.route_region.value == normalized.region_code]
                if transport_only:
                    if not chosen_transport:
                        base['warnings'].append(
                            'No se encontró una ruta documentada para la zona: ' + normalized.region_code + '.')
                        return base
                    base.update(mode='route', services=[public_service(s, as_of=self.today())
                                                        for s in chosen_transport[:3]])
                    return base
        # Una consulta compuesta no pierde movilidad, bienestar o apoyo por
        # haber mencionado transporte; solo se considera la región confirmada.
        eligible_for_query = [s for s in eligible if s.category_code.value != 'transporte_externo'
                              or (chosen_transport and s in chosen_transport)]
        profile = detected_profile(request.message, request.clarification_answer, request.applicant_type)
        country = detected_country(request.message, request.clarification_answer)
        if country and 'movilidad_academica' in intents:
            code, label = country
            # Las consultas por país no se mezclan con destinos ajenos ni se
            # presentan los convenios como plazas abiertas. La orientación OGCRI
            # general sí puede aparecer, claramente etiquetada como tal.
            exact = [s for s in eligible if 'pais_' + code in s.needs_tags
                     and s.availability_status.value == 'confirmado_documentalmente'
                     and s.valid_from is not None and s.valid_until is not None
                     and s.valid_from <= self.today() <= s.valid_until]
            if exact:
                # Si hubiese un plazo documentado como vigente, presentar SOLO
                # el país solicitado. La fecha no garantiza cupos disponibles.
                support_needed = intents & {'bienestar', 'clinica_general', 'salud_mental'}
                # Reservar espacio para otra necesidad presente en una consulta
                # compuesta, sin exceder el máximo de tres fichas guardables.
                limit_country = 2 if support_needed else 3
                base['services'] = [public_service(s, as_of=self.today())
                                    for s in exact[:limit_country]]
                if support_needed:
                    extras = shortlist(eligible_for_query, profile=profile,
                                       intents=support_needed,
                                       faculty_code=request.faculty_code, message=request.message)
                    for item in extras:
                        if len(base['services']) < 3 and item.id not in {
                                x['id'] for x in base['services']}:
                            base['services'].append(public_service(item, as_of=self.today()))
                    if 'bienestar' in support_needed and not any(
                            x['category_code'] in {'bienestar', 'unayoe'} for x in base['services']):
                        base['warnings'].append(
                            'Consulta Bienestar de tu facultad para orientación socioeconómica; '
                            'no hay una ficha aplicable a este ámbito.')
                base['country_context'] = (
                    f'Encontramos registros de {label} cuya fecha documentada incluye hoy. '
                    'Esto no confirma cupos ni una postulación activa en tiempo real; '
                    'verifica la convocatoria individual en su fuente oficial.'
                )
                base['mode'] = 'route'
                return base
            if not exact:
                try:
                    snapshot = self.repository.read()
                except CatalogUnavailable:
                    try:
                        snapshot = LocalCatalogRepository(self.settings.fallback_file).read()
                    except CatalogUnavailable:
                        snapshot = None
                historical = list_historical(
                    snapshot, faculty_code=request.faculty_code, as_of=self.today(),
                    country_code=code, profile=profile,
                    allow_demo_records=self.settings.allow_demo_records) if snapshot else []
                base['historical_services'] = [public_service(s, as_of=self.today()) for s in historical]
                base['country_context'] = (
                    f'No encontramos una convocatoria para {label} confirmada como abierta ' +
                    'en el catálogo revisado. Los antecedentes de abajo sirven para ' +
                    'preparar documentación, pero sus plazos ya vencieron. ' +
                    'Consulta la OGCRI para conocer novedades.')
                base['warnings'].append(
                    'No se puede afirmar que no exista otra convocatoria fuera del catálogo revisado.')
                general = [s for s in eligible if s.id == 'CENTRAL-OGCRI-MOVILIDAD-SALIENTE']
                if general:
                    base['services'] = [public_service(general[0], as_of=self.today())]
                # No descartar bienestar por mencionar un destino concreto.
                # El servicio de bienestar FISI nunca se ofrece a «Otros».
                welfare_intents = intents & {'bienestar', 'clinica_general', 'salud_mental'}
                if welfare_intents:
                    extras = shortlist(eligible_for_query, profile=profile,
                                       intents=welfare_intents,
                                       faculty_code=request.faculty_code, message=request.message)
                    for service in extras:
                        if (len(base['services']) < 3 and
                                service.id not in {x['id'] for x in base['services']}):
                            base['services'].append(public_service(service, as_of=self.today()))
                    if 'bienestar' in welfare_intents and not any(
                            x['category_code'] in {'bienestar', 'unayoe'} for x in base['services']):
                        base['warnings'].append(
                            'Para apoyo socioeconómico, consulta Bienestar de tu facultad; '
                            'no hay una ficha aplicable a este ámbito en el catálogo revisado.')
                if historical or base['services']:
                    base['mode'] = 'route'
                return base
        if (not profile and intents.intersection({'becas', 'movilidad_academica', 'oportunidades_academicas'})
                and any(s.category_code.value in {'becas', 'movilidad_academica', 'oportunidades_academicas'}
                        for s in eligible)):
            # No recomendar una beca de docentes a quien no especificó su perfil.
            if not request.clarification_used:
                base.update(mode='question', question='¿La consulta es para pregrado, posgrado o docentes?')
                return base
            base['warnings'].append('No se identificó el grupo de la convocatoria; indícalo en el selector.')
            return base
        candidates = shortlist(eligible_for_query, profile=profile, intents=intents,
                               faculty_code=request.faculty_code, message=request.message)
        if 'bienestar' in intents and not any(s.category_code.value in {'bienestar', 'unayoe'}
                                                   for s in candidates):
            base['warnings'].append(
                'No hay ficha de bienestar aplicable a este ámbito. Consulta Bienestar de tu facultad.')
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
            candidates_cards = [public_service(item, as_of=self.today()) for item in candidates[:3]]
            base['services'] = self._cover_multiple_needs(candidates, candidates_cards, intents)
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
        cards = self._cover_multiple_needs(candidates, cards, intents)
        if cards:
            base.update(mode='route', services=cards)
        else:
            base['warnings'].append('No se identificó una ruta verificable para esta necesidad.')
            # No atribuir selección válida a una llamada que no produjo resultados.
            base['ai_used'] = False
        return base
