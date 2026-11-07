"""SDD: FISI/Otros, antecedentes del país y señales de progreso. Sin red."""
from datetime import date
from pathlib import Path
import json

from fastapi.testclient import TestClient

from backend.app.config import BASE_DIR, Settings
from backend.app.main import create_app
from backend.app.ai_adapter import DemoAdapter
from backend.app.local_repo import LocalCatalogRepository
from backend.app.repository import list_eligible, list_historical
from backend.app.targeting import detected_country, shortlist


def client():
    return TestClient(create_app(settings=Settings(
        catalog_file=BASE_DIR/'data/catalog.academico.json',
        fallback_file=BASE_DIR/'data/catalog.academico.json', ai_mode='demo',
    ), ai_adapter=DemoAdapter(), today=lambda: date(2026, 11, 7)))


def test_ui_has_only_two_faculty_options_and_cancel_button():
    text=(BASE_DIR/'frontend/index.html').read_text(encoding='utf8')
    line=text.split('<select id="faculty"',1)[1].split('</select>',1)[0]
    assert line.count('<option') == 2
    assert 'value="FISI"' in line and 'value="OTRA"' in line
    assert 'value="MEDICINA"' not in line
    assert 'id="cancel-search-button"' in text
    assert 'id="search-progress"' in text


def test_fisi_keeps_welfare_and_others_only_central_universal():
    snapshot=LocalCatalogRepository(BASE_DIR/'data/catalog.academico.json').read()
    fisi=list_eligible(snapshot, faculty_code='FISI', as_of=date(2026,11,7), allow_demo_records=False)
    otros=list_eligible(snapshot, faculty_code='OTROS', as_of=date(2026,11,7), allow_demo_records=False)
    assert any(x.id=='FISI-BIENESTAR' for x in fisi)
    assert all(x.faculty_code=='CENTRAL' and x.accessible_to_all_faculties for x in otros)
    assert not any(x.id=='FISI-BIENESTAR' for x in otros)
    assert not any(x.id.startswith('MEDICINA') for x in otros)


def test_france_historical_only_not_open_and_no_ai_hallucination():
    j=client().post('/api/route',json={
        'faculty_code':'OTROS',
        'message':'Soy un estudiante de pregrado y quiero viajar a Francia para investigar',
    }).json()
    assert j['mode']=='route'
    assert j['ai_used'] is False
    assert j['historical_services']
    assert 'Francia' in j['country_context']
    assert 'no encontramos' in j['country_context'].lower()
    assert all(s['availability_status']=='cerrado_documentado' for s in j['historical_services'])
    assert all(s['valid_until'] < '2026-11-07' for s in j['historical_services'])
    assert all('francia' in s['name'].lower() for s in j['historical_services'])
    assert len(j['historical_services']) <= 3
    assert all(s['id']=='CENTRAL-OGCRI-MOVILIDAD-SALIENTE' for s in j['services'])
    assert 'movilidad' in j['services'][0]['name'].lower()


def test_france_without_profile_still_shows_historic_requirements():
    j=client().post('/api/route',json={
        'faculty_code':'FISI','message':'Soy un estudiante y quiero viajar a Francia'
    }).json()
    assert j['historical_services']
    assert any(s['requirements'] for s in j['historical_services'])
    assert j['country_context']


def test_destination_without_verified_history_not_invented():
    j=client().post('/api/route',json={
        'faculty_code':'OTROS','message':'Soy de pregrado y quiero viajar a Canadá'
    }).json()
    assert j['country_context'] and 'Canadá' in j['country_context']
    assert j['historical_services']==[]
    assert not any('Canadá' in s['name'] for s in j['services'])


def test_historical_records_not_active_in_services_endpoint():
    j=client().get('/api/services?faculty_code=OTROS').json()
    ids={s['id'] for s in j['services']}
    assert 'CENTRAL-OGCRI-FRANCIA' not in ids
    assert 'CENTRAL-OGCRI-FRANCIA-2024' not in ids
    assert 'CENTRAL-VRAP-GUIA-INVESTIGACION' in ids


def test_research_formativa_prioritizes_vrap_within_small_context():
    snapshot=LocalCatalogRepository(BASE_DIR/'data/catalog.academico.json').read()
    pool=list_eligible(snapshot, faculty_code='OTROS', as_of=date(2026,11,7), allow_demo_records=False)
    selected=shortlist(pool, profile='pregrado', intents={'oportunidades_academicas'},
                      faculty_code='OTROS', message='Soy estudiante y quiero investigar con VRAP')
    assert len(selected)<=6
    assert selected[0].id in ('CENTRAL-VRAP-GUIA-INVESTIGACION','CENTRAL-VRAP-PREGRADO')


def test_country_recognition_is_explicit():
    assert detected_country('Quiero viajar a Francia')==('francia','Francia')
    assert detected_country('Quiero viajar a MéXICO')==('mexico','México')
    assert detected_country('Necesito transporte en el norte') is None


def test_frontend_reports_sign_up_privacy_and_saving_progress():
    js=(BASE_DIR/'frontend/app.js').read_text(encoding='utf8')
    assert 'save-route-button' in js
    assert 'Guardando ruta…' in js
    assert 'Ruta guardada correctamente' in js
    assert 'cancel-search-button' in js
    assert 'state.controller.abort()' in js
    assert 'Por privacidad' in js


def test_sql_is_incremental_and_without_fake_demo_records():
    sql=(BASE_DIR/'supabase/008_antecedentes_ogcri_investigacion.sql').read_text(encoding='utf8')
    assert 'ON CONFLICT' in sql
    assert 'CENTRAL-OGCRI-FRANCIA-2025' in sql
    assert 'CENTRAL-VRAP-GUIA-INVESTIGACION' in sql
    assert 'prueba_ficticia' not in sql
    assert 'DROP TABLE' not in sql.upper()
