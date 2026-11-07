"""Contratos de la entrega final sin depender de servicios externos ni credenciales."""
from datetime import date
from pathlib import Path
import tomllib

from fastapi.testclient import TestClient

from backend.app.config import BASE_DIR, Settings
from backend.app.main import create_app
from tools import explorar_fuentes


def test_editable_package_has_every_runtime_dependency():
    doc = tomllib.loads((BASE_DIR / 'pyproject.toml').read_text('utf-8'))
    assert doc['project']['name'] == 'conecta-unmsm'
    assert 'dev' in doc['project']['optional-dependencies']
    dependencies = ' '.join(doc['project']['dependencies']).lower()
    for name in ('fastapi', 'supabase', 'google-genai', 'python-dotenv', 'uvicorn'):
        assert name in dependencies
    assert (BASE_DIR / 'INSTALAR_Y_PROBAR.bat').exists()
    assert (BASE_DIR / 'INICIAR_CONECTA_FINAL.bat').exists()


def test_final_sql_is_incremental_and_discards_obsolete_records():
    sql = (BASE_DIR / 'supabase/010_VERSION_FINAL.sql').read_text('utf-8')
    assert 'CENTRAL-VRAP-PREGRADO' in sql
    assert "'CENTRAL-VRAP-GUIA-INVESTIGACION'" in sql
    assert 'CENTRAL-OGCRI-ESPANA-2027I-JAEN' in sql
    assert 'ON CONFLICT (id) DO UPDATE' in sql
    assert 'DROP TABLE' not in sql.upper()
    assert 'CREATE TABLE' not in sql.upper()
    assert 'PRUEBA_FICTICIA' not in sql.upper()
    assert 'ALTER POLICY' not in sql.upper()


def test_frontend_is_received_design_not_development_splash():
    html = (BASE_DIR / 'frontend/index.html').read_text('utf-8')
    js = (BASE_DIR / 'frontend/app.js').read_text('utf-8')
    assert 'ilustracion-bienvenida.png' in html
    assert 'logo-horizontal.png' in html
    assert all(term not in html.lower() for term in ('piloto', 'prototipo', 'laboratorio'))
    assert html.count('value="FISI"') == 2
    assert html.count('value="OTRA"') == 2
    assert 'Guardando ruta…' in js and 'Búsqueda cancelada.' in js
    for path in ('/static/app.js', '/static/styles.css', '/static/assets/img/logo-horizontal.png',
                 '/static/assets/img/ilustracion-bienvenida.png'):
        client = TestClient(create_app(settings=Settings(catalog_backend='local', ai_mode='demo')))
        assert client.get(path).status_code == 200


def test_transport_real_catalog_is_deterministic_without_gemini():
    c = TestClient(create_app(settings=Settings(
        catalog_file=BASE_DIR/'data/catalog.academico.json', ai_mode='gemini', gemini_api_key='',
    ), today=lambda: date(2026, 11, 7)))
    first = c.post('/api/route', json={'faculty_code': 'FISI', 'message': 'Necesito transporte externo'}).json()
    assert first['mode'] == 'question'
    second = c.post('/api/route', json={'faculty_code': 'FISI', 'message': 'Necesito transporte externo',
                                       'clarification_answer': 'sur', 'clarification_used': True}).json()
    assert second['mode'] == 'route'
    assert second['ai_used'] is False
    assert second['services']
    assert {item['route_region'] for item in second['services']} == {'sur'}
    third = c.post('/api/route', json={'faculty_code': 'FISI', 'message': 'transporte sur'}).json()
    assert third['services'] and {item['route_region'] for item in third['services']} == {'sur'}
    ambiguous = c.post('/api/route', json={'faculty_code': 'FISI', 'message': 'transporte',
                                          'clarification_answer': 'sur y norte', 'clarification_used': True}).json()
    assert ambiguous['services'] == [] and ambiguous['mode'] != 'question'
    other = c.post('/api/route', json={'faculty_code': 'OTRA', 'message': 'transporte sur'}).json()
    assert other['services'] == []  # La cobertura universal de esta fuente no está documentada.


def test_spain_uses_expired_historical_record_not_current_call():
    c = TestClient(create_app(settings=Settings(
        catalog_file=BASE_DIR/'data/catalog.academico.json', ai_mode='gemini', gemini_api_key='',
    ), today=lambda: date(2026, 11, 7)))
    payload = c.post('/api/route', json={'faculty_code': 'OTRA', 'message':
                                        'Soy de pregrado y quiero ir de intercambio a España'}).json()
    assert payload['country_context'] and 'España' in payload['country_context']
    assert any('Jaén' in x['name'] for x in payload['historical_services'])
    assert all(x['availability_status'] == 'cerrado_documentado' for x in payload['historical_services'])
    assert all(x['valid_until'] < '2026-11-07' for x in payload['historical_services'])


def test_ogcri_archive_fallback_respects_host_and_keeps_dates_unknown(monkeypatch):
    content = b'''<!doctype html><html><body><h3>
      <a href="https://cooperacion-unmsm.blogspot.com/2026/09/intercambio-francia-2027-i.html">INTERCAMBIO: FRANCIA 2027-I</a>
      <a href="https://phishing.invalid/2026/09/beca.html">BECA FALSA</a></h3></body></html>'''
    rows = explorar_fuentes.parse_archive_html(content, 'OGCRI')
    assert len(rows) == 1
    assert rows[0]['open_status'] == 'sin_verificar'
    assert rows[0]['published_at'] is None
    def mock_fetch(url):
        if url.endswith('/2026/'):
            return content
        raise ValueError('Feed bloqueado en esta prueba')
    monkeypatch.setattr(explorar_fuentes, 'fetch', mock_fetch)
    result = explorar_fuentes.scan({'Feed': 'https://cooperacion-unmsm.blogspot.com/feeds/posts/default'}, pause=0)
    assert len(result['items']) == 1
    assert result['errors'] and 'Feed bloqueado' in result['errors'][0]
