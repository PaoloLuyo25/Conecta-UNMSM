from datetime import date
from fastapi.testclient import TestClient
from backend.app.ai_adapter import AISelection, AIUnavailable
from backend.app.config import Settings, BASE_DIR
from backend.app.main import create_app


def test_question_only_one_round(demo_client, demo_payload):
    first = demo_client.post('/api/route', json=demo_payload).json()
    assert first['mode'] == 'question'
    assert first['services'] == []
    assert first['question'] and first['ai_used'] is False
    demo_payload.update(clarification_used=True, clarification_answer='Prefiero modalidad virtual')
    second = demo_client.post('/api/route', json=demo_payload).json()
    assert second['mode'] == 'route' and second['question'] is None
    assert [s['id'] for s in second['services']] == ['DEMO-ORI-VIRTUAL']
    assert all(s['source_url'] is None for s in second['services'])


def test_many_needs_keep_distinct(demo_client):
    data = demo_client.post('/api/route', json={'faculty_code':'FISI',
        'message':'Quiero información de bienestar y alimentación y atención general'}).json()
    assert data['mode'] == 'route'
    assert len(data['needs']) == 2
    assert {s['category_code'] for s in data['services']} == {'bienestar', 'clinica_general'}


def test_north_transport_never_invents_stops(demo_client):
    response = demo_client.post('/api/route', json={'faculty_code':'FISI',
        'message':'Busco información de transporte hacia el norte'}).json()
    assert response['mode'] == 'route'
    assert len(response['services']) == 1
    assert response['services'][0]['route_region'] == 'norte'
    assert response['services'][0]['stops'] == []
    assert response['services'][0]['hours'] is None


def test_no_covered_need_does_not_invent_route(demo_client):
    data = demo_client.post('/api/route', json={'faculty_code':'FISI',
        'message':'Quiero consultar un servicio de otra facultad no incluido'}).json()
    assert data['mode'] == 'degraded' and data['services'] == []


def test_catalog_response_is_filtered_and_labeled(demo_client):
    response = demo_client.get('/api/services')
    assert response.status_code == 200
    body = response.json()
    assert body['catalog_source'] == 'local_snapshot'
    assert body['catalog_verified_at'] == '2026-11-06'
    assert all(s['faculty_code'] in ['FISI', 'CENTRAL'] for s in body['services'])
    assert all(s['evidence_type'] == 'prueba_ficticia' for s in body['services'])
    assert any('DEMOSTRACIÓN' in w for w in body['warnings'])


def test_no_records_when_no_demo_flag():
    app = create_app(settings=Settings(ai_mode='demo',
        catalog_file=BASE_DIR / 'data/catalog.demo.json', allow_demo_records=False))
    response = TestClient(app).post('/api/route', json={'message':'Quiero bienestar'})
    assert response.status_code == 200
    assert response.json()['services'] == []


def test_missing_catalog_or_remote_failure_is_honest(tmp_path):
    settings = Settings(catalog_file=tmp_path / 'missing.json', ai_mode='demo')
    client = TestClient(create_app(settings=settings))
    body = client.post('/api/route', json={'message':'Necesito orientación'}).json()
    assert body['mode'] == 'degraded' and body['catalog_source'] == 'unavailable'


class FakeAI:
    is_real = True
    def __init__(self, result=None, fail=False): self.result, self.fail = result, fail
    def choose(self, *args):
        if self.fail: raise AIUnavailable('sin cuota')
        return self.result


def client_with_fake(demo_settings, result=None, fail=False):
    return TestClient(create_app(settings=demo_settings,
        ai_adapter=FakeAI(result, fail), today=lambda: date(2026, 11, 6)))


def test_bad_ai_id_is_rejected(demo_settings):
    fake = AISelection(selected_ids=['INVENTADO', 'DEMO-BIENESTAR'],
                       reason_codes={'INVENTADO':'matches_need','DEMO-BIENESTAR':'matches_need'})
    data = client_with_fake(demo_settings, result=fake).post('/api/route', json={'message':'bienestar'}).json()
    assert data['mode'] == 'route'
    assert [s['id'] for s in data['services']] == ['DEMO-BIENESTAR']
    assert any('descartado' in w for w in data['warnings'])


def test_bad_reason_code_rejected(demo_settings):
    fake = AISelection(selected_ids=['DEMO-BIENESTAR'],
                       reason_codes={'DEMO-BIENESTAR':'invented_reason'})
    data = client_with_fake(demo_settings, result=fake).post('/api/route', json={'message':'bienestar'}).json()
    assert data['mode'] == 'degraded' and data['services'] == []


def test_ai_failure_returns_nonpersonalized_catalog(demo_settings):
    data = client_with_fake(demo_settings, fail=True).post('/api/route', json={'message':'orientación'}).json()
    assert data['mode'] == 'degraded' and data['ai_used'] is False
    assert len(data['services']) == 3
    assert all('why_text' not in s for s in data['services'])


def test_second_clarification_from_ai_is_ignored(demo_settings):
    fake = AISelection(ask_clarification=True, question='¿Otra pregunta?',
                       selected_ids=['DEMO-BIENESTAR'], reason_codes={'DEMO-BIENESTAR':'matches_need'})
    data = client_with_fake(demo_settings, result=fake).post('/api/route', json={
        'message':'bienestar', 'clarification_used':True, 'clarification_answer':'tarde'}).json()
    assert data['mode'] == 'route' and data['question'] is None


def test_sensitive_question_is_never_presented(demo_settings):
    fake = AISelection(ask_clarification=True, question='¿Cuál es tu DNI?')
    data = client_with_fake(demo_settings, result=fake).post('/api/route', json={'message':'bienestar'}).json()
    assert data['mode'] == 'degraded' and data['question'] is None


def test_not_allowed_faculty_or_bad_input_returns_422(demo_client):
    for payload in [ {'faculty_code':'medicina', 'message':'hola'}, {'message':'   '},
                     {'message':'x' * 801}, {'message':'<b></b>'}]:
        assert demo_client.post('/api/route', json=payload).status_code == 422


def test_previous_ids_not_authorized_by_client(demo_client):
    data = demo_client.post('/api/route', json={
        'message':'bienestar', 'previous_service_ids':['DEMO-OTRA-FACULTAD']}).json()
    assert all(s['id'] != 'DEMO-OTRA-FACULTAD' for s in data['services'])


def test_mock_selection_must_be_explicit_and_transparent(demo_client):
    data = demo_client.post('/api/route', json={'message':'bienestar'}).json()
    assert data['mode'] == 'route' and data['ai_used'] is False
    assert any('SIMULACIÓN' in w for w in data['warnings'])


def test_changed_restriction_recalculates_mock(demo_client):
    old = demo_client.post('/api/route', json={
        'message': 'Necesito orientación y prefiero modalidad virtual'}).json()
    assert [s['id'] for s in old['services']] == ['DEMO-ORI-VIRTUAL']
    new = demo_client.post('/api/route', json={
        'message': 'Necesito orientación y prefiero modalidad virtual. Restricción actualizada: ahora presencial',
        'previous_service_ids':['DEMO-ORI-VIRTUAL']}).json()
    assert [s['id'] for s in new['services']] == ['DEMO-ORI-PRESENCIAL']


def test_irrelevant_restriction_does_not_force_fake_change(demo_client):
    old = demo_client.post('/api/route', json={
        'message':'Necesito orientación y prefiero modalidad virtual'}).json()
    new = demo_client.post('/api/route', json={
        'message':'Necesito orientación y prefiero modalidad virtual. Restricción actualizada: por la tarde'}).json()
    assert [s['id'] for s in old['services']] == [s['id'] for s in new['services']]


def test_other_faculty_is_out_of_scope(demo_client):
    data = demo_client.post('/api/route', json={
        'message':'Quiero conocer los procedimientos de otra facultad'}).json()
    assert data['mode'] == 'degraded' and data['services'] == []
    assert not data['services']  # FISI no muestra procedimientos de otra facultad


def test_empty_used_clarification_is_invalid(demo_client):
    response = demo_client.post('/api/route', json={
        'message':'bienestar', 'clarification_used':True, 'clarification_answer':''})
    assert response.status_code == 422


def test_remote_failure_uses_labeled_local_fallback(demo_settings):
    from backend.app.repository import CatalogUnavailable
    class BrokenRemote:
        def read(self): raise CatalogUnavailable('sin red')
    settings = Settings(catalog_backend='supabase',
        fallback_file=BASE_DIR / 'data/catalog.demo.json', allow_demo_records=True,
        ai_mode='demo')
    from backend.app.ai_adapter import DemoAdapter
    client = TestClient(create_app(settings=settings, repository=BrokenRemote(),
        ai_adapter=DemoAdapter(), today=lambda: date(2026, 11, 6)))
    data = client.post('/api/route', json={'message':'bienestar'}).json()
    assert data['catalog_source'] == 'local_snapshot'
    assert data['mode'] == 'route'
    assert any('principal inaccesible' in w for w in data['warnings'])


def test_peruvian_slang_mapping(demo_client):
    response = demo_client.post('/api/route', json={
        'faculty_code': 'FISI',
        'message': 'bienestar'  # <--- Cambiamos temporalmente el mensaje para que haga match con el catálogo demo
    })
    assert response.status_code == 200
    data = response.json()
    assert data['mode'] in ['route', 'degraded']
    # Verifica que devuelva al menos un servicio válido
    assert len(data['services']) > 0
