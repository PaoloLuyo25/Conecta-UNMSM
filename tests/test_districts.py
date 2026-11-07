import pytest
from backend.app.districts import DistrictDirectory, DistrictSourceError
from backend.app.normalization import normalize_query


def write(tmp_path, text):
    path = tmp_path / 'distritos_verificados.md'
    path.write_text(text, encoding='utf-8')
    return path


def test_missing_source_is_safe(tmp_path):
    directory = DistrictDirectory.from_markdown(tmp_path / 'no-existe.md')
    assert not directory.available
    assert directory.lookup('Distrito de Prueba') is None


def test_canonical_district_with_documented_zone(tmp_path):
    path = write(tmp_path, '| Distrito | Zona | Alias |\n|---|---|---|\n| Distrito Alfa | Norte | D. Alfa |\n')
    directory = DistrictDirectory.from_markdown(path)
    assert directory.lookup('Voy a distrito ÁLFA').region == 'norte'
    assert directory.lookup('Voy a D. Alfa').name == 'Distrito Alfa'
    q = normalize_query('Transporte a distrito alfa', directory=directory)
    assert q.region_code == 'norte'


def test_recognized_district_without_zone_does_not_infer(tmp_path):
    path = write(tmp_path, '| Distrito | Zona |\n|---|---|\n| Distrito Beta | |\n')
    directory = DistrictDirectory.from_markdown(path)
    q = normalize_query('Transporte a distrito beta', directory=directory)
    assert q.district_unmapped and q.region_code is None


@pytest.mark.parametrize('table', [
    '| Distrito | Zona | Alias |\n|---|---|---|\n| Alfa | Norte | X |\n| Beta | Sur | X |\n',
    '| Distrito | Zona |\n|---|---|\n| Alfa | Oeste |\n',
    '| Distrito | Zona |\n|---|---|\n| Alfa | Sur |\n| Alfa | Norte |\n',
    '| Distrito | Zona |\n|---|---|\n| | Sur |\n',
])
def test_ambiguous_or_invalid_rows_fail_closed(tmp_path, table):
    with pytest.raises(DistrictSourceError):
        DistrictDirectory.from_markdown(write(tmp_path, table))


def test_unlisted_name_not_recognized(tmp_path):
    directory = DistrictDirectory.from_markdown(write(
        tmp_path, '| Distrito | Zona |\n|---|---|\n| Alfa | Sur |\n'))
    assert directory.lookup('Otro lugar') is None
