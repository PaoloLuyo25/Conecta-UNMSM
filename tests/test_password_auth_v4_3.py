"""Contrato de correo/contraseña, sin llamar a Supabase remoto ni filtrar secretos."""
import httpx
import pytest

from backend.app import auth_history
from backend.app.auth_api import CredentialsRequest
from backend.app.auth_history import SupabaseIdentity, UpstreamFailure


def test_password_is_hidden_in_model_repr_and_validation_errors():
    body = CredentialsRequest(email=' TEST@UNMSM.EDU.PE ', password='Password-test-2026!')
    assert body.email == 'test@unmsm.edu.pe'
    assert body.password.get_secret_value() == 'Password-test-2026!'
    assert 'Password-test-2026!' not in repr(body)
    with pytest.raises(Exception):
        CredentialsRequest(email='test@unmsm.edu.pe', password='123')


def test_signup_and_login_call_correct_supabase_endpoints(monkeypatch):
    requests = []
    user_id = '11111111-1111-4111-8111-111111111111'

    def handler(request):
        requests.append(request)
        if request.url.path == '/auth/v1/signup':
            return httpx.Response(200, json={'access_token': 'signup-token',
                                              'refresh_token': 'signup-refresh', 'expires_in': 3600})
        if request.url.path == '/auth/v1/token':
            assert request.url.params.get('grant_type') == 'password'
            return httpx.Response(200, json={'access_token': 'login-token',
                                              'refresh_token': 'login-refresh', 'expires_in': 3600})
        if request.url.path == '/auth/v1/user':
            return httpx.Response(200, json={'id': user_id, 'email': 'test@unmsm.edu.pe'})
        return httpx.Response(404)

    real_client = httpx.Client
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(auth_history.httpx, 'Client',
                        lambda **kw: real_client(transport=transport, **kw))
    identity = SupabaseIdentity('https://example.supabase.co', 'sb_publishable_fake')
    signup = identity.sign_up('test@unmsm.edu.pe', 'Password-test-2026!')
    login = identity.sign_in('test@unmsm.edu.pe', 'Password-test-2026!')
    assert identity.user(login['access_token']) == user_id
    assert signup['access_token'] == 'signup-token'
    assert login['access_token'] == 'login-token'
    assert requests[0].url.path == '/auth/v1/signup'
    assert requests[1].url.path == '/auth/v1/token'
    for request in requests:
        assert request.headers['apikey'] == 'sb_publishable_fake'
        if request.url.path != '/auth/v1/user':
            assert 'Authorization' not in request.headers
    assert requests[-1].headers['authorization'] == 'Bearer login-token'


def test_signup_without_confirm_email_disabled_does_not_create_session(monkeypatch):
    def handler(request):
        # Supabase devuelve un user sin sesión si exige confirmar el correo.
        return httpx.Response(200, json={'user': {'id': '00000000-0000-4000-8000-000000000000'}})

    real_client = httpx.Client
    monkeypatch.setattr(auth_history.httpx, 'Client',
                        lambda **kw: real_client(transport=httpx.MockTransport(handler), **kw))
    identity = SupabaseIdentity('https://example.supabase.co', 'sb_publishable_fake')
    result = identity.sign_up('test@unmsm.edu.pe', 'Password-test-2026!')
    assert result == {'confirmation_required': True}
    assert 'access_token' not in result


def test_public_frontend_has_password_login_and_no_otp():
    from backend.app.config import BASE_DIR
    html = (BASE_DIR / 'frontend' / 'index.html').read_text(encoding='utf-8')
    js = (BASE_DIR / 'frontend' / 'app.js').read_text(encoding='utf-8')
    assert 'type="password"' in html
    assert 'id="register-button"' in html
    assert '/static/app.js' in html
    assert '/api/auth/signup' in js and '/api/auth/login' in js
    assert 'verify-form' not in js
    assert '/api/auth/start' not in js
    assert '/api/auth/verify' not in js


def test_http_validation_never_echoes_submitted_password():
    from fastapi.testclient import TestClient
    from backend.app.config import Settings
    from backend.app.main import create_app
    client = TestClient(create_app(settings=Settings(enable_history=True)))
    passwords = ('abc', 'Password-test-2026!')
    inputs = (
        {'email': 'test@unmsm.edu.pe', 'password': passwords[0]},
        {'email': 'invalid', 'password': passwords[1]},
        {'password': passwords[1]},
    )
    for path in ('/api/auth/signup', '/api/auth/login'):
        for body in inputs:
            response = client.post(path, json=body, headers={'Origin': 'http://testserver'})
            assert response.status_code == 422
            for secret in passwords:
                assert secret not in response.text


def test_pending_email_confirmation_has_no_authenticated_session():
    from fastapi.testclient import TestClient
    from backend.app.config import Settings
    from backend.app.main import create_app

    class PendingIdentity:
        def sign_up(self, email, password):
            assert email == 'test@unmsm.edu.pe'
            return {'confirmation_required': True}

        def user(self, token):
            raise AssertionError('No verificar tokens si Supabase no emitió una sesión')

    client = TestClient(create_app(settings=Settings(enable_history=True), identity=PendingIdentity()))
    result = client.post('/api/auth/signup',
                         json={'email': 'test@unmsm.edu.pe', 'password': 'Password-test-2026!'},
                         headers={'Origin': 'http://testserver'})
    assert result.status_code == 200
    assert result.json() == {'authenticated': False, 'confirmation_required': True}
    assert 'conecta_access' not in result.cookies
    assert 'conecta_refresh' not in result.cookies
    assert client.get('/api/auth/me').json() == {'authenticated': False}


def test_bad_signup_response_is_not_accepted(monkeypatch):
    real_client = httpx.Client
    monkeypatch.setattr(auth_history.httpx, 'Client',
                        lambda **kw: real_client(transport=httpx.MockTransport(
                            lambda request: httpx.Response(200, json={'user': {}})), **kw))
    with pytest.raises(UpstreamFailure):
        SupabaseIdentity('https://example.supabase.co', 'sb_publishable_fake').sign_up(
            'test@unmsm.edu.pe', 'Password-test-2026!')
