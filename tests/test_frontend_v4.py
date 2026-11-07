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
