from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'frontend'


def test_new_query_spinner_and_optional_history_exist():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    js = (ROOT / 'app.js').read_text(encoding='utf-8')
    css = (ROOT / 'styles.css').read_text(encoding='utf-8')
    for name in ('new-query-button', 'loading-spinner', 'history-choice', 'account-panel'):
        assert f'id="{name}"' in html
    for name in ('new-query-button', 'loading-spinner', 'requestSequence', 'urgent-button'):
        if name in ('requestSequence', 'urgent-button'):
            assert name not in js
        else:
            assert name in js
    assert 'state.sequence += 1' in js
    assert 'state.controller.abort()' in js
    assert 'seq !== state.sequence' in js
    assert 'prefers-reduced-motion' in css
    assert '.urgent-banner' not in css
    assert 'aria-busy' in js


def test_faculty_selector_on_welcome_is_synced_and_cancels_pending_request():
    """T2-D01: la facultad se elige en la bienvenida y el cambio cancela consultas en curso."""
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    js = (ROOT / 'app.js').read_text(encoding='utf-8')
    welcome = html.index('id="welcome-screen"')
    workspace = html.index('id="app-main"')
    selector = html.index('id="welcome-faculty"')
    assert welcome < selector < workspace
    for code in ('value="FISI"', 'value="OTRA"'):
        assert code in html[selector:workspace]  # se conserva «otra facultad» (RF2-20)
    assert 'function setFaculty' in js
    assert 'function cancelPendingRequest' in js
    change_handler = js[js.index("$('faculty').addEventListener('change'"):]
    assert 'cancelPendingRequest()' in change_handler.split('\n\n')[0]
    assert "state.facultyCode = 'FISI'" not in js  # «Nueva consulta» no devuelve a FISI

def test_visual_system_t2_d04_tokens_fonts_and_assets_are_local():
    """T2-D04: paleta y tipografía del sistema visual, sin recursos externos ni gradientes."""
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    css = (ROOT / 'styles.css').read_text(encoding='utf-8')
    js = (ROOT / 'app.js').read_text(encoding='utf-8')
    for token in ('#313647', '#435663', '#A3B087', '#F8F0E7'):
        assert token in css
    assert "font-family: 'Outfit'" in css and "font-family: 'DM Sans'" in css
    assert 'fonts.googleapis' not in css + html  # fuentes alojadas en el proyecto
    assert 'gradient' not in css  # sin degradados decorativos
    assert 'prefers-reduced-motion' in css
    assert '100vh' not in css.replace('max-height: calc(100vh - 28px);', '')  # dvh en el modal
    assert 'innerHTML' not in js  # datos externos solo con textContent
    # Todo archivo referenciado en /static/ existe.
    import re
    refs = set(re.findall(r'/static/(assets/[^"\')? ]+\.\w+)', html + css))
    assert refs, 'se esperaban recursos en /static/assets/'
    for ref in refs:
        assert (ROOT / ref).is_file(), ref


def test_brand_logo_resets_query_and_toast_region_exists():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    js = (ROOT / 'app.js').read_text(encoding='utf-8')
    assert 'id="brand-home"' in html and 'id="toast-region"' in html
    assert "$('brand-home').addEventListener('click'" in js
    assert 'function toast' in js
