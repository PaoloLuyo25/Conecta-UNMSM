"""Pruebas OFFLINE del adaptador y de la estructura RLS (no sustituyen conexión real)."""
import sys
from types import ModuleType, SimpleNamespace
from pathlib import Path
from backend.app.supabase_repo import SupabaseCatalogRepository
from backend.app.config import BASE_DIR
from backend.app.schemas import Service
from backend.app.repository import CatalogUnavailable
import pytest


def test_supabase_adapter_read_with_fake_sdk(monkeypatch):
    captures = {}
    class FakeQuery:
        def select(self, columns):
            captures['columns'] = columns
            return self
        def execute(self):
            return SimpleNamespace(data=[{
                'id':'PUBLIC-TEST', 'name':'Registro ficticio', 'faculty_code':'CENTRAL',
                'accessible_to_all_faculties':True, 'category_code':'transporte_externo',
                'description':'Información sintética de prueba','needs_tags':['transporte'],
                'route_region':'norte','evidence_type':'prueba_ficticia',
                'availability_status':'datos_insuficientes'}])
    class FakeClient:
        def table(self, value):
            assert value == 'services'
            return FakeQuery()
    module=ModuleType('supabase')
    module.create_client=lambda url,key: FakeClient()
    monkeypatch.setitem(sys.modules,'supabase',module)
    snapshot=SupabaseCatalogRepository('https://fake.invalid','dummy').read()
    assert snapshot.source=='primary' and snapshot.services[0].accessible_to_all_faculties
    assert 'is_public' not in captures['columns'].split(',')
    assert set(captures['columns'].split(','))==set(Service.model_fields)


def test_supabase_credentials_required():
    with pytest.raises(CatalogUnavailable):
        SupabaseCatalogRepository('', '').read()


def test_sql_schema_contains_rls_and_no_write_policies():
    sql=(BASE_DIR/'supabase/001_services.sql').read_text(encoding='utf8').lower()
    assert 'enable row level security' in sql
    assert 'force row level security' in sql
    assert 'for select to anon' in sql
    assert 'is_public = true' in sql
    assert 'grant select (' in sql
    assert 'grant insert' not in sql
    assert 'create policy' in sql
    # Solo revisión estática; no establece protección real en instancia Supabase.


def test_demo_sql_distinguishes_fictional_data():
    sql=(BASE_DIR/'supabase/002_seed_lab_FICTICIO.sql').read_text(encoding='utf8')
    assert 'SOLO PARA UN PROYECTO SUPABASE DE PRUEBAS' in sql
    assert 'prueba_ficticia' in sql
    assert 'DEMO-TRANSPORTE-NORTE' in sql
