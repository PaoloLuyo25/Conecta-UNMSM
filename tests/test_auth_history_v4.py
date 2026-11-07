"""Integración HTTP con proveedores simulados, sin afirmar prueba remota de RLS."""
from datetime import date
from uuid import uuid4
from fastapi.testclient import TestClient
from backend.app.config import Settings, BASE_DIR
from backend.app.main import create_app
from backend.app.ai_adapter import DemoAdapter
from backend.app.auth_history import UpstreamFailure

ORIGIN = {'Origin': 'http://testserver'}


class FakeIdentity:
    def __init__(self):
        self.active = {'access-A': str(uuid4()), 'access-B': str(uuid4())}
        self.starts = []

    def sign_up(self, email, password):
        self.starts.append(('signup', email))
        if password != 'Prueba-2026!':
            raise UpstreamFailure('Datos inválidos')
        return {'access_token': 'access-A', 'refresh_token': 'refresh-A', 'expires_in': 300}

    def sign_in(self, email, password):
        self.starts.append(('login', email))
        if email != 'fake@unmsm.edu.pe' or password != 'Prueba-2026!':
            raise UpstreamFailure('Datos inválidos')
        self.active.setdefault('access-A', str(uuid4()))
        return {'access_token': 'access-A', 'refresh_token': 'refresh-A', 'expires_in': 300}

    def user(self, token):
        if token not in self.active:
            raise UpstreamFailure('No validado')
        return self.active[token]

    def refresh(self, token):
        if token != 'refresh-A':
            raise UpstreamFailure('Expirado')
        return self.sign_in('fake@unmsm.edu.pe', 'Prueba-2026!')

    def logout(self, token):
        self.active.pop(token, None)


class FakeHistory:
    def __init__(self):
        self.rows = {}

    def insert(self, user, *, ids, faculty_code, source, request_id):
        key = (user.user_id, str(request_id))
        if key not in self.rows:
            self.rows[key] = {'id': str(uuid4()), 'service_ids': list(ids),
                              'faculty_code': faculty_code, 'catalog_source': source,
                              'created_at': '2026-11-06T20:00:00+00:00',
                              'expires_at': '2026-12-06T20:00:00+00:00'}
        return self.rows[key]['id']

    def list(self, user, *, limit, offset):
        return [row for (uid, _), row in self.rows.items() if uid == user.user_id][offset:offset + limit]

    def delete(self, user, route_id=None):
        self.rows = {key: row for key, row in self.rows.items()
                     if not (key[0] == user.user_id and (route_id is None or row['id'] == str(route_id)))}


def build(enabled=True):
    settings = Settings(catalog_file=BASE_DIR / 'data/catalog.demo.json',
                        allow_demo_records=True, ai_mode='demo', enable_history=enabled)
    identity, history = FakeIdentity(), FakeHistory()
    client = TestClient(create_app(settings=settings, ai_adapter=DemoAdapter(),
                                   today=lambda: date(2026, 11, 6), identity=identity, history=history))
    return client, identity, history


def route_payload(save=False, request_id=None):
    data = {'message': 'Quiero información de bienestar universitario', 'save_to_history': save}
    if save:
        data['client_request_id'] = str(request_id or uuid4())
    return data


def test_public_route_without_auth_is_accessible_and_not_saved():
    client, _, history = build()
    answer = client.post('/api/route', json=route_payload()).json()
    assert answer['mode'] == 'route' and not answer['history_saved']
    assert not history.rows
    assert client.get('/api/history').status_code == 401


def test_signup_login_logout_and_unverified_cookie():
    client, _, _ = build()
    credentials = {'email': 'fake@unmsm.edu.pe', 'password': 'Prueba-2026!'}
    assert client.post('/api/auth/signup', json=credentials).status_code == 403
    assert client.post('/api/auth/signup', json=credentials, headers=ORIGIN).status_code == 200
    assert client.get('/api/auth/me').json()['authenticated'] is True
    assert client.post('/api/auth/logout', headers=ORIGIN).status_code == 200
    assert client.get('/api/auth/me').json()['authenticated'] is False
    invalid = client.post('/api/auth/login', json={**credentials, 'password': 'Bad-Password!'}, headers=ORIGIN)
    assert invalid.status_code == 401
    assert client.get('/api/auth/me').json() == {'authenticated': False}
    logged_in = client.post('/api/auth/login', json=credentials, headers=ORIGIN)
    assert logged_in.status_code == 200
    assert 'httponly' in logged_in.headers['set-cookie'].lower()
    assert 'Prueba-2026!' not in logged_in.text
    assert client.get('/api/auth/me').json()['authenticated'] is True


def test_history_optin_idempotency_and_privacy():
    client, identity, history = build()
    client.cookies.set('conecta_access', 'access-A')
    rid = uuid4()
    payload = route_payload(True, rid)
    assert client.post('/api/route', json=payload).status_code == 403  # CSRF
    first = client.post('/api/route', json=payload, headers=ORIGIN).json()
    second = client.post('/api/route', json=payload, headers=ORIGIN).json()
    assert first['history_saved'] and first['history_id'] == second['history_id']
    assert len(history.rows) == 1
    assert 'message' not in repr(history.rows)
    assert 'email' not in repr(history.rows)
    own = client.get('/api/history').json()['items']
    assert len(own) == 1
    client.cookies.set('conecta_access', 'access-B')
    assert client.get('/api/history').json()['items'] == []
    assert client.delete('/api/history/' + own[0]['id'], headers=ORIGIN).status_code == 200
    client.cookies.set('conecta_access', 'access-A')
    assert len(client.get('/api/history').json()['items']) == 1
    assert client.delete('/api/history', headers=ORIGIN).status_code == 200
    assert client.get('/api/history').json()['items'] == []


def test_invalid_cookie_cannot_save_and_no_consent_no_storage():
    client, _, history = build()
    client.cookies.set('conecta_access', 'fabricated')
    answer = client.post('/api/route', json=route_payload(True), headers=ORIGIN).json()
    assert not answer['history_saved'] and not history.rows
    assert client.get('/api/history').status_code == 401


def test_disabled_private_features_preserve_public_route():
    client, _, history = build(False)
    assert client.get('/api/features').json()['history_enabled'] is False
    assert client.get('/api/history').status_code == 503
    answer = client.post('/api/route', json=route_payload()).json()
    assert answer['mode'] == 'route' and not history.rows


def test_cannot_save_question_or_invalid_route():
    client, _, history = build()
    client.cookies.set('conecta_access', 'access-A')
    payload = route_payload(True)
    payload['message'] = 'Necesito orientación para adaptarme a la universidad'
    answer = client.post('/api/route', json=payload, headers=ORIGIN).json()
    assert answer['mode'] == 'question' and not answer['history_saved']
    assert not history.rows


def test_auth_rate_limit_blocks_repeated_password_attempts():
    client, _, _ = build()
    credentials = {'email': 'fake@unmsm.edu.pe', 'password': 'Incorrecta123'}
    for _ in range(5):
        assert client.post('/api/auth/login', json=credentials,
                           headers=ORIGIN).status_code == 401
    assert client.post('/api/auth/login', json=credentials,
                       headers=ORIGIN).status_code == 429


def test_storage_failure_keeps_route_visible():
    client, _, history = build()
    client.cookies.set('conecta_access', 'access-A')
    def broken_insert(*args, **kwargs):
        raise UpstreamFailure('Simulado')
    history.insert = broken_insert
    answer = client.post('/api/route', json=route_payload(True), headers=ORIGIN).json()
    assert answer['mode'] == 'route' and len(answer['services']) == 1
    assert not answer['history_saved'] and answer['history_id'] is None
    assert any('No fue posible guardar' in note for note in answer['warnings'])


def test_no_optin_does_not_write_even_when_logged_in():
    client, _, history = build()
    client.cookies.set('conecta_access', 'access-A')
    assert client.post('/api/route', json=route_payload(), headers=ORIGIN).status_code == 200
    assert not history.rows


def test_missing_request_uuid_for_saving_is_validation_error():
    client, _, _ = build()
    assert client.post('/api/route', json={'message': 'bienestar', 'save_to_history': True},
                       headers=ORIGIN).status_code == 422


def test_save_existing_route_after_generation_without_requery():
    client, _, history = build()
    client.cookies.set('conecta_access', 'access-A')
    generated = client.post('/api/route', json=route_payload()).json()
    assert generated['route_ticket'] and not generated['history_saved']
    assert not history.rows  # Mostrar una ruta no implica consentimiento para guardarla.
    rid = str(uuid4())
    save = {'route_ticket': generated['route_ticket'], 'client_request_id': rid}
    assert client.post('/api/history/save', json=save).status_code == 403
    first = client.post('/api/history/save', json=save, headers=ORIGIN)
    assert first.status_code == 200, first.text
    assert first.json()['saved'] is True
    assert client.post('/api/history/save', json=save, headers=ORIGIN).json()['id'] == first.json()['id']
    assert len(history.rows) == 1
    assert 'message' not in repr(history.rows)
    assert client.get('/api/history').json()['items'][0]['service_ids'] == ['DEMO-BIENESTAR']
    client.cookies.set('conecta_access', 'access-B')
    assert client.get('/api/history').json()['items'] == []


def test_rejects_forged_tampered_and_expired_tickets():
    client, _, history = build()
    client.cookies.set('conecta_access', 'access-A')
    generated = client.post('/api/route', json=route_payload()).json()
    good = generated['route_ticket']
    request_id = str(uuid4())
    for candidate in ('fake.jwt', good[:-1] + ('A' if good[-1] != 'A' else 'B')):
        result = client.post('/api/history/save', json={
            'route_ticket': candidate, 'client_request_id': request_id}, headers=ORIGIN)
        assert result.status_code == 422, result.text
    # Contrato del comprobante: no se puede usar fuera de su TTL.
    signer = client.app.state.route_ticket_signer
    real_clock = signer.clock
    signer.clock = lambda: real_clock() + 1860
    try:
        expired = client.post('/api/history/save', json={
            'route_ticket': good, 'client_request_id': request_id}, headers=ORIGIN)
        assert expired.status_code == 422
    finally:
        signer.clock = real_clock
    assert not history.rows


def test_history_visible_disabled_and_static_not_cached():
    client, _, _ = build(False)
    html = client.get('/')
    assert html.status_code == 200
    assert 'no-store' in html.headers.get('cache-control', '')
    assert 'id="account-panel"' in html.text
    assert 'id="history-unavailable"' in html.text
    assert '/static/app.js' in html.text
    assert '/static/styles.css' in html.text
    script = client.get('/static/app.js')
    assert script.status_code == 200 and 'no-store' in script.headers.get('cache-control', '')
    assert client.post('/api/history/save', json={
        'route_ticket': 'x' * 30, 'client_request_id': str(uuid4())}, headers=ORIGIN).status_code == 503
