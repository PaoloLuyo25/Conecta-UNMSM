from datetime import date
import json
import pytest
from backend.app.local_repo import LocalCatalogRepository
from backend.app.repository import CatalogUnavailable, list_eligible, public_service
from backend.app.config import BASE_DIR


def test_demo_excludes_other_faculty():
    snapshot = LocalCatalogRepository(BASE_DIR / 'data/catalog.demo.json').read()
    services = list_eligible(snapshot, faculty_code='FISI', as_of=date(2026, 11, 6), allow_demo_records=True)
    assert len(services) == 9
    assert all(s.faculty_code in {'FISI', 'CENTRAL'} for s in services)
    assert 'DEMO-OTRA-FACULTAD' not in [s.id for s in services]


def test_mock_records_do_not_leak_without_explicit_optin():
    snap = LocalCatalogRepository(BASE_DIR / 'data/catalog.demo.json').read()
    assert list_eligible(snap, faculty_code='FISI', as_of=date(2026, 11, 6), allow_demo_records=False) == []


def test_default_snapshot_empty_not_fictional():
    snap = LocalCatalogRepository(BASE_DIR / 'data/catalog.snapshot.json').read()
    assert snap.services == ()
    assert snap.verified_at is None


def test_unknown_file_fails_cleanly(tmp_path):
    with pytest.raises(CatalogUnavailable):
        LocalCatalogRepository(tmp_path / 'absent.json').read()


def test_invalid_and_duplicate_ids_fail_cleanly(tmp_path):
    raw = json.loads((BASE_DIR / 'data/catalog.demo.json').read_text(encoding='utf-8'))
    raw['services'].append(raw['services'][0].copy())
    p = tmp_path / 'duplicate.json'; p.write_text(json.dumps(raw), encoding='utf-8')
    with pytest.raises(CatalogUnavailable): LocalCatalogRepository(p).read()
    raw['services'][0]['category_code'] = 'extraña'
    p.write_text(json.dumps(raw), encoding='utf-8')
    with pytest.raises(CatalogUnavailable): LocalCatalogRepository(p).read()


def test_expired_and_closed_are_not_offered(tmp_path):
    raw = json.loads((BASE_DIR / 'data/catalog.demo.json').read_text(encoding='utf-8'))
    raw['services'][0]['valid_until'] = '2026-10-01'
    raw['services'][1]['availability_status'] = 'cerrado_documentado'
    p = tmp_path / 'expired.json'; p.write_text(json.dumps(raw), encoding='utf-8')
    services = list_eligible(LocalCatalogRepository(p).read(), faculty_code='FISI',
                             as_of=date(2026, 11, 6), allow_demo_records=True)
    assert 'DEMO-ORI-PRESENCIAL' not in {s.id for s in services}
    assert 'DEMO-ORI-VIRTUAL' not in {s.id for s in services}


def test_missing_source_contact_hours_are_not_invented():
    snap = LocalCatalogRepository(BASE_DIR / 'data/catalog.demo.json').read()
    card = public_service(snap.services[0], as_of=date(2026, 11, 6))
    assert card['contact'] is None and card['hours'] is None and card['source_url'] is None
    assert any('ficticio' in warning for warning in card['warnings'])
