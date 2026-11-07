"""SDD v4.5: 20 facultades, perfiles y Gemini limitado. Sin red real."""
from datetime import date
from pathlib import Path
import json

from fastapi.testclient import TestClient
from backend.app.config import BASE_DIR, Settings
from backend.app.main import create_app
from backend.app.ai_adapter import DemoAdapter
from backend.app.local_repo import LocalCatalogRepository
from backend.app.repository import list_eligible
from backend.app.targeting import detected_profile, detected_intents, shortlist


def make_client():
    settings = Settings(catalog_file=BASE_DIR/'data/catalog.multifaculty.demo.json',
                        allow_demo_records=True, ai_mode='demo')
    return TestClient(create_app(settings=settings, ai_adapter=DemoAdapter(),
                                 today=lambda: date(2026, 11, 7)))


def test_all_20_faculties_have_seven_scenarios():
    data = json.loads((BASE_DIR/'data/facultades_unmsm.json').read_text(encoding='utf8'))
    snapshot = LocalCatalogRepository(BASE_DIR/'data/catalog.multifaculty.demo.json').read()
    assert len(data['faculties']) == 20
    assert len(set(f['code'] for f in data['faculties'])) == 20
    for f in data['faculties']:
        own = [s for s in snapshot.services if s.id.startswith('DEMO-MF-') and s.faculty_code == f['code']]
        assert len(own) == 7


def test_faculty_isolation():
    snapshot = LocalCatalogRepository(BASE_DIR/'data/catalog.multifaculty.demo.json').read()
    eligible = list_eligible(snapshot, faculty_code='MEDICINA', as_of=date(2026,11,7), allow_demo_records=True)
    assert all(s.faculty_code in {'MEDICINA','CENTRAL'} for s in eligible)
    assert not any(s.faculty_code=='DERECHO' for s in eligible)
    assert any(s.id=='DEMO-MF-MEDICINA-BECA_POS' for s in eligible)
    assert not any(s.id=='DEMO-MF-DERECHO-BECA_POS' for s in eligible)


def test_profile_and_intents_are_independent():
    assert detected_profile('Soy de posgrado y quiero viajar', None, 'sin_especificar') == 'posgrado'
    assert detected_profile('Busco becas', 'soy docente', 'sin_especificar') == 'docentes'
    assert detected_intents('Soy de posgrado y quiero viajar', None) == {'movilidad_academica'}
    assert detected_intents('Necesito transporte a cono norte', None) == {'transporte_externo'}


def test_shortlist_never_exceeds_six_for_flash_lite():
    snapshot = LocalCatalogRepository(BASE_DIR/'data/catalog.multifaculty.demo.json').read()
    eligible = list_eligible(snapshot, faculty_code='FISI', as_of=date(2026,11,7),allow_demo_records=True)
    result = shortlist(eligible, profile='posgrado', intents={'becas','movilidad_academica'},faculty_code='FISI')
    assert len(result) <= 6
    assert all(s.audience in {None,'todos','posgrado'} for s in result)
    assert all(s.category_code.value in {'becas','movilidad_academica'} for s in result)


def test_posgrado_travel_and_pregrado_scholarship_do_not_mix():
    c = make_client()
    travel = c.post('/api/route',json={'faculty_code':'MEDICINA',
      'message':'Soy de posgrado y quiero viajar en intercambio'}).json()
    assert travel['mode']=='route', travel
    assert all(s['category_code']=='movilidad_academica' and s['audience']=='posgrado' for s in travel['services'])
    assert all(s['faculty_code']=='MEDICINA' for s in travel['services'])
    scholarships = c.post('/api/route',json={'faculty_code':'DERECHO',
      'applicant_type':'pregrado','message':'Busco una beca'}).json()
    assert scholarships['mode']=='route', scholarships
    assert all(s['category_code']=='becas' and s['audience']=='pregrado' for s in scholarships['services'])


def test_becas_without_cohort_ask_once():
    c = make_client()
    first = c.post('/api/route',json={'faculty_code':'MEDICINA','message':'Quiero becas'}).json()
    assert first['mode']=='question' and 'pregrado' in first['question']
    second = c.post('/api/route',json={'faculty_code':'MEDICINA','message':'Quiero becas',
       'clarification_answer':'posgrado', 'clarification_used':True}).json()
    assert second['mode']=='route'
    assert all(s['audience']=='posgrado' for s in second['services'])
    third = c.post('/api/route',json={'faculty_code':'MEDICINA','message':'Quiero becas',
       'clarification_answer':'no sé', 'clarification_used':True}).json()
    assert third['mode']=='degraded' and not third['services']


def test_no_demo_records_without_flag():
    app = create_app(settings=Settings(catalog_file=BASE_DIR/'data/catalog.multifaculty.demo.json',
      allow_demo_records=False,ai_mode='demo'),ai_adapter=DemoAdapter())
    result=TestClient(app).post('/api/route',json={'faculty_code':'MEDICINA',
       'message':'Soy de posgrado y quiero viajar'}).json()
    assert result['mode']=='degraded' and not result['services']


def test_conflicting_profile_selector_does_not_silently_override_text():
    assert detected_profile('Soy de posgrado y busco una beca', None, 'pregrado') is None

def test_movilidad_academica_does_not_activate_geographic_transport_normalizer():
    from backend.app.normalization import normalize_query
    assert normalize_query('Movilidad académica norte y sur').ambiguous is False
