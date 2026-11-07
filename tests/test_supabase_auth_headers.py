"""Seguridad: publishable key solo apikey; JWT de usuario en Authorization."""
import httpx
from backend.app import auth_history


def test_publishable_key_is_not_sent_as_bearer(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)
    real_client = httpx.Client
    monkeypatch.setattr(auth_history.httpx, 'Client',
                        lambda **kw: real_client(transport=transport, **kw))
    identity = auth_history.SupabaseIdentity('https://example.supabase.co', 'sb_publishable_fake')
    identity._call('POST', '/auth/v1/token', params={'grant_type':'password'}, payload={'email':'fake@test.local','password':'Password-2026!'})
    assert seen[-1].headers['apikey'] == 'sb_publishable_fake'
    assert 'Authorization' not in seen[-1].headers
    identity._call('GET', '/auth/v1/user', token='synthetic.valid.jwt')
    assert seen[-1].headers['authorization'] == 'Bearer synthetic.valid.jwt'
    assert seen[-1].headers['apikey'] == 'sb_publishable_fake'
