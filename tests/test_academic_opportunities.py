"""Pruebas del catálogo real documentado y filtros académicos, sin llamadas de red."""
import json
from datetime import date
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app.config import BASE_DIR, Settings
from backend.app.local_repo import LocalCatalogRepository
from backend.app.repository import list_eligible
from backend.app.targeting import detected_intents, detected_profile, shortlist, audience_codes
from backend.app.main import create_app
from backend.app.ai_adapter import DemoAdapter
from tools.explorar_fuentes import parse_atom, parse_rss, safe_link
from tools.generar_sql_catalogo import generate

CATALOG=BASE_DIR/'data/catalog.academico.json'

def eligible(faculty='FISI'):
    snap=LocalCatalogRepository(CATALOG).read()
    return list_eligible(snap,faculty_code=faculty,as_of=date(2026,11,7),allow_demo_records=False)

def test_real_catalog_has_sources_and_no_fictitious_records():
    catalog=LocalCatalogRepository(CATALOG).read()
    assert len(catalog.services)>=12
    assert all(s.evidence_type.value!='prueba_ficticia' for s in catalog.services)
    assert all(s.source_url for s in catalog.services if s.evidence_type.value=='web_oficial')
    assert all(s.availability_status.value!='confirmado_documentalmente' for s in catalog.services)

def test_medical_specific_records_never_leak_to_other_faculties():
    assert 'MEDICINA-ROCHESTER' in {s.id for s in eligible('MEDICINA')}
    assert 'MEDICINA-ROCHESTER' not in {s.id for s in eligible('FISI')}
    assert 'FISI-BIENESTAR' not in {s.id for s in eligible('MEDICINA')}
    assert 'CENTRAL-OGCRI-MOVILIDAD-SALIENTE' in {s.id for s in eligible('DERECHO')}

def test_postgrad_trip_receives_real_mobility_candidates_not_transport():
    text='Soy un estudiante de posgrado y quiero viajar por intercambio'
    profile=detected_profile(text,None,'sin_especificar')
    intents=detected_intents(text,None)
    chosen=shortlist(eligible('DERECHO'),profile=profile,intents=intents,faculty_code='DERECHO')
    assert profile=='posgrado'
    assert 'movilidad_academica' in intents
    assert chosen and len(chosen)<=6
    assert all(s.category_code.value!='transporte_externo' for s in chosen)
    assert any(s.id=='CENTRAL-OGCRI-MOVILIDAD-SALIENTE' for s in chosen)
    assert any(s.id=='CENTRAL-VRIP-AUIP-MAGALLANES' for s in chosen)

def test_auip_multi_audience_and_not_pregrado():
    auip=next(s for s in eligible('FISI') if s.id=='CENTRAL-VRIP-AUIP-MAGALLANES')
    assert audience_codes(auip)=={'posgrado','docentes'}
    for role in ('posgrado','docentes'):
        chosen=shortlist(eligible('FISI'),profile=role,intents={'becas'},faculty_code='FISI')
        assert auip in chosen
    assert auip not in shortlist(eligible('FISI'),profile='pregrado',intents={'becas'},faculty_code='FISI')

def test_unqualified_academic_student_gets_profile_question():
    client=TestClient(create_app(settings=Settings(catalog_file=CATALOG,ai_mode='demo'),ai_adapter=DemoAdapter(),today=lambda:date(2026,11,7)))
    r=client.post('/api/route',json={'faculty_code':'DERECHO','message':'Soy un estudiante y quiero una beca'})
    assert r.status_code==200
    assert r.json()['mode']=='question'
    assert 'pregrado' in r.json()['question']

def test_source_outage_is_degraded_but_still_offers_real_reference():
    client=TestClient(create_app(settings=Settings(catalog_file=CATALOG,ai_mode='gemini',gemini_api_key=''),today=lambda:date(2026,11,7)))
    j=client.post('/api/route',json={'faculty_code':'DERECHO','message':'Soy estudiante de posgrado y quiero viajar'}).json()
    assert j['mode']=='degraded' and j['ai_used'] is False
    assert all(s['evidence_type']!='prueba_ficticia' for s in j['services'])
    assert all(s['source_url'] for s in j['services'])

def test_ogcri_can_be_found_without_calling_ai():
    assert 'oportunidades_academicas' in detected_intents('Soy un estudiante y busco los convenios de OGCRI',None)
    assert 'becas' in detected_intents('Me interesan las becas para investigadores',None)

def test_feed_atom_and_rss_extract_only_allowed_urls():
    atom=b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Convocatoria movilidad</title><published>2026-11-05T00:00:00Z</published><link rel="alternate" href="https://cooperacion-unmsm.blogspot.com/2026/11/anuncio.html"/><summary>Postulaciones</summary></entry><entry><title>Premio</title><link rel="alternate" href="https://attacker.example/phishing"/></entry></feed>'''
    rows=parse_atom(atom,'OGCRI');assert len(rows)==1 and rows[0]['review_status']=='pendiente_revision'
    rss=b'''<rss><channel><item><title>Becas</title><link>https://vrip.unmsm.edu.pe/anuncio/</link><description>investigacion</description></item></channel></rss>'''
    assert parse_rss(rss,'VRIP')[0]['url']=='https://vrip.unmsm.edu.pe/anuncio/'
    assert not safe_link('http://vrip.unmsm.edu.pe/item')
    assert not safe_link('https://vrip.unmsm.edu.pe.evil.test/item')

def test_sql_never_imports_mock_services():
    doc=json.loads(CATALOG.read_text(encoding='utf8'))
    sql=generate(doc)
    assert "'CENTRAL-OGCRI-MOVILIDAD-SALIENTE'" in sql
    assert 'ON CONFLICT' in sql
    doc['services'].append(json.loads((BASE_DIR/'data/catalog.demo.json').read_text(encoding='utf8'))['services'][0])
    with pytest.raises(ValueError):generate(doc)

def test_frontend_placeholder_and_name():
    html=(BASE_DIR/'frontend/index.html').read_text(encoding='utf8')
    assert '<title>Conecta UNMSM</title>' in html
    assert 'Soy un estudiante y quiero conocer convocatorias' in html
    assert 'v=4.' not in html
    assert 'id="welcome-guest"' in html and 'id="auth-overlay"' in html
