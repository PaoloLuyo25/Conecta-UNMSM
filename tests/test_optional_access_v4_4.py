"""Flujo de bienvenida, validación de correo institucional y privacidad."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.auth_api import CredentialsRequest
from backend.app.config import BASE_DIR, Settings
from backend.app.main import create_app


@pytest.mark.parametrize('email', (
    'usuario@gmail.com',
    'usuario@unmsm.edu.pe.invalido',
    'usuario@sub.unmsm.edu.pe',
    'usuario@unmsmXeduXpe',
    'x@evilunmsm.edu.pe',
    '@unmsm.edu.pe',
    'usuario @unmsm.edu.pe',
    'usuario@@unmsm.edu.pe',
))
def test_university_suffix_rejects_other_domains(email):
    with pytest.raises(ValidationError):
        CredentialsRequest(email=email, password='ClaveDePrueba-123')


@pytest.mark.parametrize('email', (
    'persona@unmsm.edu.pe',
    ' PERSONA@UNMSM.EDU.PE ',
))
def test_university_suffix_accepts_only_exact_domain(email):
    account = CredentialsRequest(email=email, password='ClaveDePrueba-123')
    assert account.email == 'persona@unmsm.edu.pe'


def test_rejection_before_supabase_signup_or_login_and_no_password_leak():
    client = TestClient(create_app(settings=Settings(enable_history=True)))
    for path in ('/api/auth/signup', '/api/auth/login'):
        res = client.post(path, headers={'Origin': 'http://testserver'}, json={
            'email': 'persona@gmail.com', 'password': 'ClaveConfidencial-123'})
        assert res.status_code == 422
        assert 'ClaveConfidencial-123' not in res.text


def test_public_page_has_optional_welcome_and_not_extra_main_panel():
    html = (BASE_DIR / 'frontend/index.html').read_text(encoding='utf-8')
    js = (BASE_DIR / 'frontend/app.js').read_text(encoding='utf-8')
    assert 'id="welcome-screen"' in html
    assert 'id="welcome-login"' in html
    assert 'id="welcome-guest"' in html
    assert 'id="header-auth-button"' in html
    assert 'id="app-main" class="hidden"' in html
    assert 'id="auth-overlay"' in html
    assert 'id="account-panel" role="dialog"' in html or 'class="panel account-panel auth-dialog" id="account-panel" role="dialog"' in html
    assert '¿Deseas guardar esta ruta?' in html
    assert 'usuario@unmsm.edu.pe' in html
    assert 'enterWorkspace()' in js
    assert 'pendingSaveAfterAuth' in js
    assert 'await saveExistingRoute()' in js
    assert '<title>Conecta UNMSM</title>' in html


def test_supabase_session_checks_domain_even_if_token_preexists(monkeypatch):
    import httpx
    from backend.app import auth_history
    from backend.app.auth_history import SupabaseIdentity, UpstreamFailure

    user_id = '11111111-1111-4111-8111-111111111111'
    real = httpx.Client
    def mock(email):
        transport = httpx.MockTransport(lambda request: httpx.Response(200,
            json={'id': user_id, 'email': email}))
        monkeypatch.setattr(auth_history.httpx, 'Client', lambda **kw: real(transport=transport, **kw))
        return SupabaseIdentity('https://fake.supabase.co', 'public-test-key')
    assert mock('Test@UNMSM.EDU.PE').user('demo-token') == user_id
    with pytest.raises(UpstreamFailure):
        mock('antigua@gmail.com').user('demo-token')
    with pytest.raises(UpstreamFailure):
        mock('').user('demo-token')
