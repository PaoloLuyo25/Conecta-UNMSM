"""Tests de contrato Gemini sin red ni credenciales."""
import json
from types import ModuleType, SimpleNamespace
import sys
import pytest

from backend.app.ai_adapter import AISelection, AIUnavailable, GeminiAdapter, GeminiWireResponse
from backend.app.config import BASE_DIR
from backend.app.local_repo import LocalCatalogRepository


@pytest.fixture
def fake_google_sdk(monkeypatch):
    services = LocalCatalogRepository(BASE_DIR / 'data/catalog.demo.json').read().services
    captures = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captures['init'] = kwargs
        def __enter__(self): return self
        def __exit__(self, *args): return None
        @property
        def models(self): return self
        def generate_content(self, *, model, contents, config):
            captures.update(model=model, contents=contents, config=config)
            return SimpleNamespace(text=json.dumps({
                'needs':['bienestar'], 'constraints':[], 'ask_clarification':False,
                'question_code':None, 'selected':[{'id':'DEMO-BIENESTAR','reason_code':'matches_need'}]}))

    google = ModuleType('google')
    genai = ModuleType('google.genai')
    types = ModuleType('google.genai.types')
    genai.Client = FakeClient
    genai.types = types
    google.genai = genai
    types.HttpOptions = lambda **kw: kw
    types.GenerateContentConfig = lambda **kw: kw
    monkeypatch.setitem(sys.modules, 'google', google)
    monkeypatch.setitem(sys.modules, 'google.genai', genai)
    monkeypatch.setitem(sys.modules, 'google.genai.types', types)
    return services, captures


def test_gemini_contract_only_supplies_candidate_ids(fake_google_sdk):
    services, captured = fake_google_sdk
    adapter = GeminiAdapter(api_key='DUMMY-NOT-REAL', model='modelo-prueba', timeout_seconds=10)
    result = adapter.choose('Necesito bienestar', None, False, list(services))
    assert result.selected_ids == ['DEMO-BIENESTAR']
    assert captured['config']['response_mime_type'] == 'application/json'
    assert captured['config']['response_schema'] == GeminiWireResponse
    assert captured['init']['http_options']['timeout'] == 10000
    assert 'DUMMY-NOT-REAL' not in captured['contents']
    assert 'source_url' not in captured['contents']
    assert '"contact":' not in captured['contents']


def test_without_api_key_never_calls_external_sdk():
    services = LocalCatalogRepository(BASE_DIR / 'data/catalog.demo.json').read().services
    with pytest.raises(AIUnavailable):
        GeminiAdapter(api_key='', model='desconocido').choose('bienestar', None, False, list(services))


def test_invalid_ai_json_is_controlled(fake_google_sdk, monkeypatch):
    services, _ = fake_google_sdk
    class BadClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): return None
        @property
        def models(self): return self
        def generate_content(self, **kwargs): return SimpleNamespace(text='mal-json')
    sys.modules['google.genai'].Client = BadClient
    with pytest.raises(AIUnavailable):
        GeminiAdapter(api_key='DUMMY', model='modelo').choose('hola', None, False, list(services))
