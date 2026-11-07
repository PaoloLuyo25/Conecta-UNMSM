"""RF-23/24: alcance multiplataforma; NO existen registros institucionales reales."""
from datetime import date
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend.app.schemas import Service
from backend.app.main import create_app
from backend.app.config import Settings, BASE_DIR
from backend.app.ai_adapter import DemoAdapter, AISelection
from backend.app.repository import CatalogUnavailable
from backend.app.local_repo import LocalCatalogRepository
from backend.app.repository import list_eligible


@pytest.mark.parametrize('faculty', ['OTRA','MEDICINA','DERECHO','INGENIERIA_CIVIL'])
def test_non_fisi_receives_only_universal_transport(demo_client, faculty):
    response = demo_client.post('/api/route', json={
        'faculty_code':faculty, 'message':'Necesito transporte hacia el norte'})
    assert response.status_code == 200
    data = response.json()
    assert data['mode'] == 'route'
    assert [x['id'] for x in data['services']] == ['DEMO-TRANSPORTE-NORTE']
    assert all(x['faculty_code'] == 'CENTRAL' for x in data['services'])
    assert all(x['accessible_to_all_faculties'] for x in data['services'])
    assert any('Fuera del piloto' in w for w in data['warnings'])


def test_non_fisi_cannot_see_specific_or_non_universal_central(demo_client):
    response = demo_client.get('/api/services?faculty_code=OTRA').json()
    assert {row['category_code'] for row in response['services']} == {'transporte_externo'}
    assert len(response['services']) == 4
    assert 'DEMO-ORI-VIRTUAL' not in [row['id'] for row in response['services']]
    assert 'DEMO-CLINICA' not in [row['id'] for row in response['services']]


def test_non_fisi_welfare_question_has_no_route(demo_client):
    data = demo_client.post('/api/route', json={
        'faculty_code':'OTRA', 'message':'Necesito becas y bienestar'}).json()
    assert data['mode'] == 'degraded'
    assert data['services'] == []


def test_non_fisi_transport_without_region_prompts_once(demo_client):
    first = demo_client.post('/api/route', json={
        'faculty_code':'OTRA', 'message':'Necesito conocer información de transporte'}).json()
    assert first['mode'] == 'question'
    assert first['question'] and first['services'] == []
    second = demo_client.post('/api/route', json={
        'faculty_code':'OTRA', 'message':'Necesito conocer información de transporte',
        'clarification_used':True, 'clarification_answer':'zona sur'}).json()
    assert second['mode'] == 'route'
    assert [row['id'] for row in second['services']] == ['DEMO-TRANSPORTE-SUR']


def test_fisi_still_has_specialized_services(demo_client):
    body = demo_client.post('/api/route', json={
        'faculty_code':'FISI', 'message':'Quiero apoyo de bienestar'}).json()
    assert [row['id'] for row in body['services']] == ['DEMO-BIENESTAR']


def test_all_faculties_does_not_mean_all_central_services(tmp_path):
    snap = LocalCatalogRepository(BASE_DIR/'data/catalog.demo.json').read()
    eligible = list_eligible(snap, faculty_code='OTRA', as_of=date(2026,11,6),allow_demo_records=True)
    assert all(s.accessible_to_all_faculties and s.faculty_code == 'CENTRAL' for s in eligible)


def test_noncentral_cannot_have_universal_flag():
    raw = {'id':'x','name':'x','faculty_code':'FISI','accessible_to_all_faculties':True,
           'category_code':'bienestar','description':'descripción',
           'evidence_type':'prueba_ficticia','availability_status':'vigencia_por_confirmar'}
    with pytest.raises(ValidationError):
        Service.model_validate(raw)


def test_unsupported_faculty_format_returns_422(demo_client):
    for faculty in ['OTRA FACULTAD','fisi','F'*50, 'SISTEMAS&CIENCIA']:
        assert demo_client.post('/api/route', json={
            'faculty_code':faculty,'message':'información de transporte'}).status_code == 422


def test_no_fictional_records_in_normal_mode():
    settings=Settings(catalog_file=BASE_DIR/'data/catalog.demo.json', allow_demo_records=False, ai_mode='demo')
    app=create_app(settings=settings,ai_adapter=DemoAdapter(),today=lambda:date(2026,11,6))
    body=TestClient(app).post('/api/route',json={
        'faculty_code':'OTRA','message':'Necesito transporte al norte'}).json()
    assert body['services'] == [] and body['mode'] == 'degraded'


class FakeGeminiSelection:
    is_real=True
    def choose(self,*args):
        # Respuesta maliciosa de un modelo: no autorizado como dato en el backend.
        return AISelection(selected_ids=['DEMO-ORI-VIRTUAL','DEMO-TRANSPORTE-NORTE'],
                           reason_codes={'DEMO-ORI-VIRTUAL':'matches_need',
                                         'DEMO-TRANSPORTE-NORTE':'matches_location'})


def test_ai_cannot_override_scope():
    s=Settings(catalog_file=BASE_DIR/'data/catalog.demo.json',allow_demo_records=True,ai_mode='gemini')
    c=TestClient(create_app(settings=s,ai_adapter=FakeGeminiSelection(), today=lambda:date(2026,11,6)))
    data=c.post('/api/route',json={'faculty_code':'OTRA','message':'Transporte norte'}).json()
    assert [row['id'] for row in data['services']] == ['DEMO-TRANSPORTE-NORTE']
    assert any('descartado' in x for x in data['warnings'])


def test_question_must_come_from_bank_not_gemini_free_text():
    class BadQuestion:
        is_real=True
        def choose(self,*a):
            return AISelection(ask_clarification=True, question='Dame tu nombre y DNI', question_code=None)
    s=Settings(catalog_file=BASE_DIR/'data/catalog.demo.json',allow_demo_records=True)
    c=TestClient(create_app(settings=s,ai_adapter=BadQuestion(),today=lambda:date(2026,11,6)))
    data=c.post('/api/route',json={'message':'Quiero orientación'}).json()
    assert data['mode']=='degraded' and data['question'] is None
