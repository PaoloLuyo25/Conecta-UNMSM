"""Snapshot JSON local. Sin escrituras ni datos institucionales inventados."""
import json
from datetime import date
from pathlib import Path
from pydantic import ValidationError

from backend.app.repository import CatalogSnapshot, CatalogUnavailable
from backend.app.schemas import Service


class LocalCatalogRepository:
    def __init__(self, path: Path):
        self.path = Path(path)

    def read(self) -> CatalogSnapshot:
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(raw, dict) or not isinstance(raw.get('services'), list):
                raise ValueError('Estructura del catálogo incorrecta.')
            timestamp = raw.get('snapshot_at')
            snapshot_date = date.fromisoformat(timestamp) if timestamp else None
            records = tuple(Service.model_validate(item) for item in raw['services'])
            ids = [item.id for item in records]
            if len(ids) != len(set(ids)):
                raise ValueError('IDs duplicados.')
            return CatalogSnapshot(records, 'local_snapshot', snapshot_date)
        except (OSError, ValueError, TypeError, ValidationError, json.JSONDecodeError) as exc:
            raise CatalogUnavailable('El catálogo local no está disponible o es inválido.') from exc
