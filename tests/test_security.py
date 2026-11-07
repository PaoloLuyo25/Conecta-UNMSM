from pathlib import Path


def test_frontend_avoids_innerhtml_and_secrets():
    code = (Path(__file__).resolve().parents[1]/'frontend/app.js').read_text(encoding='utf-8')
    assert '.innerHTML' not in code
    assert 'GEMINI_API_KEY' not in code and 'SUPABASE_ANON_KEY' not in code
    assert 'textContent' in code


def test_urgent_section_was_removed(demo_client):
    html = demo_client.get('/')
    assert html.status_code == 200
    assert 'ACCESO A AYUDA HUMANA' not in html.text
    assert 'urgent-button' not in html.text
    code = (Path(__file__).resolve().parents[1]/'frontend/app.js').read_text(encoding='utf-8')
    assert 'urgent-button' not in code
    assert 'new-query-button' in code
    assert demo_client.get('/static/app.js').status_code == 200
    assert demo_client.get('/static/styles.css').status_code == 200


def test_html_in_prompt_is_never_inserted_in_service(demo_client):
    data = demo_client.post('/api/route', json={'message':'bienestar <img src=x onerror=alert(1)>'}).json()
    assert all('onerror' not in s['name'] for s in data['services'])
    assert all('onerror' not in (s.get('why_text') or '') for s in data['services'])
