"""Flujos v4.4 en Chromium real con red simulada, SIN verificar Supabase remoto.

Ejecutar opcionalmente: python tests/browser_smoke.py
Requiere Playwright/Chromium (opcional, NO dependencia del proyecto).
"""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1] / 'frontend'


def load(page, fetch_script):
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    html = re.sub(r'<script src="/static/app\.js[^" ]*" defer></script>', '', html)
    page.set_content(html)
    page.add_style_tag(content=(ROOT / 'styles.css').read_text(encoding='utf-8'))
    page.evaluate("""() => {if (!crypto.randomUUID) {
      Object.defineProperty(crypto, 'randomUUID', {value:()=> '11111111-1111-4111-8111-111111111111'});
    }}""")
    page.evaluate(fetch_script)
    page.add_script_tag(content=(ROOT / 'app.js').read_text(encoding='utf-8'))


MOCK = """() => {
  window.calls = [];
  window.saved = false;
  window.logged = false;
  window.service = {id:'TEST',name:'Ruta FICTICIA',faculty_code:'FISI',
    category_code:'bienestar',description:'Ejemplo sintético',warnings:[]};
  window.fetch = async (url, options) => {
    window.calls.push({url, body: options?.body || null});
    if (url === '/api/features') return {ok:true,json:async()=>({history_enabled:true})};
    if (url === '/api/auth/me') return {ok:true,json:async()=>({authenticated:window.logged})};
    if (url === '/api/auth/signup' || url === '/api/auth/login') {
      window.logged = true;
      return {ok:true,json:async()=>({authenticated:true})};
    }
    if (url === '/api/auth/logout') {
      window.logged = false;
      return {ok:true,json:async()=>({authenticated:false})};
    }
    if (url === '/api/route') return {ok:true,json:async()=>({
      mode:'route',warnings:[],catalog_source:'primary',catalog_verified_at:null,
      ai_used:true,route_ticket:'test.signed',services:[window.service]
    })};
    if (url === '/api/history/save') {
      window.saved = true;
      return {ok:true,json:async()=>({saved:true,id:'mock-id'})};
    }
    if (url.startsWith('/api/history?')) return {ok:true,json:async()=>({items:
      window.saved ? [{id:'mock-id',created_at:'2026-11-06T20:00:00Z',
        faculty_code:'FISI',catalog_source:'primary',services:[window.service],
        needs_revalidation:false}] : []})};
    return {ok:false,json:async()=>({detail:'Fallo simulado'})};
  };
}"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium',
                                    headless=True, args=['--no-sandbox'])
        errors = []
        # Flujo 1: visitante, nueva consulta, login posterior y guardado sin reconsultar Gemini.
        page = browser.new_page(viewport={'width': 1365, 'height': 910})
        page.on('pageerror', lambda error: errors.append(str(error)))
        load(page, MOCK)
        assert page.locator('#welcome-screen').is_visible()
        assert page.locator('#app-main').is_hidden()
        assert page.locator('#header-auth-button').is_visible()
        page.locator('#welcome-guest').click()
        assert page.locator('#welcome-screen').is_hidden()
        assert page.locator('#message').is_visible()
        page.locator('#message').fill('Quiero información de bienestar')
        page.locator('#submit').click()
        page.locator('.service-card').first.wait_for(timeout=3000)
        assert page.locator('#save-route-button').is_visible()
        assert not page.evaluate('window.saved')
        page.locator('#save-route-button').click()
        assert page.locator('#auth-overlay').is_visible()
        assert page.locator('#login-form').is_visible()
        assert not page.evaluate('window.saved')
        page.locator('#login-email').fill('usuario@gmail.com')
        page.locator('#login-password').fill('ClaveEspecial2026!')
        page.locator('#register-button').click()
        page.get_by_text('Utiliza un correo que termine en @unmsm.edu.pe.').wait_for()
        assert page.evaluate("window.calls.filter(x=>x.url==='/api/auth/signup').length") == 0
        page.locator('#login-email').fill('usuario@unmsm.edu.pe')
        page.locator('#register-button').click()
        page.get_by_text('Ruta guardada correctamente.').wait_for(timeout=4000)
        assert page.evaluate('window.saved')
        assert page.evaluate("window.calls.filter(x=>x.url==='/api/route').length") == 1
        assert page.evaluate("window.calls.filter(x=>x.url==='/api/history/save').length") == 1
        assert page.locator('#auth-overlay').is_hidden()
        assert page.locator('#result .service-card').count() == 1
        page.locator('#header-auth-button').click()
        page.locator('#history-items .history-entry').first.wait_for()
        page.locator('#close-auth-button').click()
        page.locator('#new-query-button').click()
        assert page.locator('#message').input_value() == ''
        assert page.locator('#history-choice').is_hidden()
        page.locator('#header-auth-button').click()
        assert page.locator('#history-items .history-entry').count() == 1
        page.locator('#logout').click()
        page.locator('#auth-overlay').wait_for(state='hidden')
        assert page.locator('#header-auth-button').inner_text() == 'Iniciar sesión'
        assert not errors, errors
        page.close()

        # Flujo 2: iniciar sesión ANTES de generar una ruta, guardar con un solo clic.
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        load(page, MOCK)
        page.locator('#welcome-login').click()
        page.locator('#login-email').fill('estudiante@unmsm.edu.pe')
        page.locator('#login-password').fill('ClaveEspecial2026!')
        page.locator('#login-form button[type=submit]').click()
        page.locator('#app-main').wait_for(state='visible')
        assert page.locator('#auth-overlay').is_hidden()
        page.locator('#message').fill('Bienestar universitario')
        page.locator('#submit').click()
        page.locator('#save-route-button').wait_for(state='visible')
        page.locator('#save-route-button').click()
        page.get_by_text('Ruta guardada correctamente.').wait_for()
        assert page.evaluate('window.saved')
        assert page.evaluate("window.calls.filter(x=>x.url==='/api/auth/login').length") == 1
        assert not errors, errors
        page.close()

        # Flujo 3: una cookie existente omite la bienvenida (consultando /api/auth/me).
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        load(page, MOCK.replace('window.logged = false;', 'window.logged = true;', 1))
        page.locator('#app-main').wait_for(state='visible')
        assert page.locator('#welcome-screen').is_hidden()
        assert not errors, errors
        page.close()
        browser.close()
        print('BROWSER SMOKE OK: visita anónima, login inicial, dominio UNMSM, guardado diferido y sesión previa; red simulada.')


if __name__ == '__main__':
    main()
