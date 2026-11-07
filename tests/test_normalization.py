from backend.app.normalization import canonical_region, normalize_query


def test_nte_only_in_transport_context():
    assert normalize_query('Quiero transporte al nte').region_code == 'norte'
    assert normalize_query('Me dijeron nte en clase').region_code is None
    assert normalize_query('nte').region_code is None


def test_nte_as_transport_clarification():
    query = normalize_query('Necesito transporte', 'nte', clarification_used=True)
    assert query.region_code == 'norte'
    assert query.context_line == 'ZONA_VERIFICADA=norte'


def test_accents_and_minor_typo():
    assert normalize_query('Busco ruta al NÓRTE').region_code == 'norte'
    assert normalize_query('Busco ruta al nortr').region_code == 'norte'


def test_conflicting_regions_block_inference():
    query = normalize_query('Busco ruta norte y sur')
    assert query.ambiguous and query.region_code is None


def test_unknown_abbreviation_remains_unknown():
    assert canonical_region('nxt', transport_context=True) is None
