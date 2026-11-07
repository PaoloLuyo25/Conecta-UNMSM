from fastapi.testclient import TestClient
from backend.app.main import create_app
from backend.app.config import Settings, BASE_DIR


def test_transport_south_clarification_never_leaks_other_regions():
    app = create_app(settings=Settings(ai_mode='demo', catalog_file=BASE_DIR/'data/catalog.demo.json', allow_demo_records=True))
    client = TestClient(app)
    first = client.post('/api/route', json={'message': 'Necesito transporte externo', 'faculty_code': 'FISI'}).json()
    assert first['mode'] == 'question'
    second = client.post('/api/route', json={'message': 'Necesito transporte externo', 'faculty_code': 'FISI', 'clarification_used': True, 'clarification_answer': 'sur'}).json()
    assert second['mode'] == 'route'
    assert second['services']
    assert {x['route_region'] for x in second['services']} == {'sur'}
    assert second['ai_used'] is False


def test_transport_unknown_zone_does_not_guess():
    app = create_app(settings=Settings(ai_mode='demo', catalog_file=BASE_DIR/'data/catalog.demo.json', allow_demo_records=True))
    client = TestClient(app)
    result = client.post('/api/route', json={'message':'Transporte externo', 'clarification_used':True, 'clarification_answer':'desconocida'}).json()
    assert result['services'] == []
