"""Lectura Supabase/PostgreSQL sin credenciales privilegiadas ni escrituras.

La tabla usa RLS (ver supabase/001_services.sql); probar RLS con una
instancia externa es una comprobación manual, NO cubierta por tests mock.
"""
from datetime import date
from backend.app.repository import CatalogSnapshot, CatalogUnavailable
from backend.app.schemas import Service


class SupabaseCatalogRepository:
    def __init__(self, url: str, anon_key: str):
        self.url = url
        self.anon_key = anon_key

    def read(self) -> CatalogSnapshot:
        if not self.url or not self.anon_key:
            raise CatalogUnavailable('Falta la conexión a Supabase.')
        try:
            # La biblioteca es opcional: se instala con requirements-supabase.txt.
            from supabase import create_client
            client = create_client(self.url, self.anon_key)
            # Selección explícita: excluir `is_public` y otras columnas internas.
            public_columns = ','.join(Service.model_fields)
            response = client.table('services').select(public_columns).execute()
            if not isinstance(response.data, list):
                raise ValueError('Respuesta de base de datos inválida.')
            rows = tuple(Service.model_validate(row) for row in response.data)
            if len({row.id for row in rows}) != len(rows):
                raise ValueError('IDs duplicados en fuente primaria.')
            dates = [row.verified_at for row in rows if row.verified_at]
            checked = max(dates) if dates else None
            return CatalogSnapshot(rows, 'primary', checked)
        except Exception as exc:
            # No pasar tokens, URL, cuerpos de error, ni trazas al navegador.
            raise CatalogUnavailable('No se puede consultar el catálogo principal.') from exc
