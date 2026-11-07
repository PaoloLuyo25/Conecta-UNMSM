"""Flujos v4.4 en Chromium real con red simulada, SIN verificar Supabase remoto.

Ejecutar opcionalmente: python tests/browser_smoke.py
Requiere Playwright/Chromium (opcional, NO dependencia del proyecto).
"""
from pathlib import Path
import os
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
    if (url === '/api/route') {
      await new Promise(resolve => setTimeout(resolve, window.routeDelay || 0));
      return {ok:true,json:async()=>({
        mode:'route',warnings:[],catalog_source:'primary',catalog_verified_at:null,
        ai_used:true,route_ticket:'test.signed',services:[window.service]
      })};
    }
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
        # Por defecto usa el Chromium que instala Playwright (`playwright install chromium`).
        # Si prefieres otro navegador, define CHROMIUM_PATH con la ruta del ejecutable.
        chromium_path = os.environ.get('CHROMIUM_PATH')
        launch_options = {'executable_path': chromium_path} if chromium_path else {}
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **launch_options)
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

        # Flujo 4 (T2-D01): la facultad elegida en la bienvenida viaja al espacio de trabajo,
        # se envía en /api/route y se conserva tras «Nueva consulta».
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        load(page, MOCK)
        assert page.locator('#welcome-faculty').is_visible()
        assert page.locator('#welcome-faculty').input_value() == 'FISI'
        page.locator('#welcome-faculty').select_option('OTRA')
        page.locator('#welcome-guest').click()
        assert page.locator('#faculty').input_value() == 'OTRA'
        page.locator('#message').fill('Quiero información de transporte')
        page.locator('#submit').click()
        page.locator('.service-card').first.wait_for(timeout=3000)
        route_calls = page.evaluate("window.calls.filter(x=>x.url==='/api/route').map(x=>JSON.parse(x.body))")
        assert len(route_calls) == 1 and route_calls[0]['faculty_code'] == 'OTRA', route_calls
        page.locator('#new-query-button').click()
        assert page.locator('#faculty').input_value() == 'OTRA'
        assert page.locator('#welcome-faculty').input_value() == 'OTRA'
        assert not errors, errors
        page.close()

        # Flujo 5 (T2-D01, RF2-05/07): cambiar de facultad con una consulta en curso
        # libera el estado de carga e ignora la respuesta tardía.
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        load(page, MOCK)
        page.evaluate('window.routeDelay = 700')
        page.locator('#welcome-guest').click()
        page.locator('#message').fill('Quiero información de bienestar')
        page.locator('#submit').click()
        page.wait_for_function("document.querySelector('#submit').disabled")
        page.locator('#faculty').select_option('OTRA')
        assert not page.locator('#submit').is_disabled()
        assert page.locator('#state-badge').inner_text() == 'Ámbito actualizado'
        page.wait_for_timeout(1100)  # la respuesta simulada llega después de la demora
        assert page.locator('#result .service-card').count() == 0
        assert page.locator('#history-choice').is_hidden()
        assert page.locator('#state-badge').inner_text() == 'Ámbito actualizado'
        assert not errors, errors
        page.close()

        # Flujo 6 (T2-D04): logo clicable = «Nueva consulta», iconos en tarjetas y aviso emergente al guardar.
        page = browser.new_page(viewport={'width': 1365, 'height': 910})
        page.on('pageerror', lambda error: errors.append(str(error)))
        load(page, MOCK)
        assert page.locator('#brand-home').is_disabled()
        page.locator('#welcome-guest').click()
        assert page.locator('#brand-home').is_enabled()
        page.locator('#message').fill('Quiero información de bienestar')
        page.locator('#submit').click()
        page.locator('.service-card').first.wait_for(timeout=3000)
        assert page.locator('.service-card .service-icon svg').count() == 1
        page.locator('#save-route-button').click()
        page.locator('#login-email').fill('usuario@unmsm.edu.pe')
        page.locator('#login-password').fill('ClaveEspecial2026!')
        page.locator('#login-form button[type=submit]').click()
        page.get_by_text('Ruta guardada en tu historial.').wait_for(timeout=4000)
        assert page.locator('#toast-region .toast').count() == 1
        page.locator('#brand-home').click()
        assert page.locator('#message').input_value() == ''
        assert page.locator('#result .service-card').count() == 0
        assert not errors, errors
        page.close()

        # Flujo 7 (T2-D04): sin scroll horizontal y modal dentro de la pantalla en móvil, tableta y escritorio.
        def no_hscroll(pg):
            return pg.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth')

        for width, side_panel_visible in ((360, False), (768, False), (1280, True)):
            page = browser.new_page(viewport={'width': width, 'height': 800})
            page.on('pageerror', lambda error: errors.append(str(error)))
            load(page, MOCK)
            assert no_hscroll(page), f'bienvenida con scroll horizontal a {width}px'
            page.locator('#welcome-guest').click()
            assert page.locator('.side-panel').is_visible() == side_panel_visible
            page.locator('#message').fill('Quiero información de bienestar')
            page.locator('#submit').click()
            page.locator('.service-card').first.wait_for(timeout=3000)
            assert no_hscroll(page), f'resultados con scroll horizontal a {width}px'
            page.locator('#header-auth-button').click()
            box = page.locator('#account-panel').bounding_box()
            assert box['x'] >= 0 and box['x'] + box['width'] <= width, (width, box)
            assert no_hscroll(page), f'modal con scroll horizontal a {width}px'
            assert not errors, errors
            page.close()
        browser.close()
        print('BROWSER SMOKE OK: visita anónima, login inicial, dominio UNMSM, guardado diferido, sesión previa y facultad (bienvenida + consulta en curso), logo, avisos y diseño responsive; red simulada.')


if __name__ == '__main__':
    main()