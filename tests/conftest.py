"""Fixtures sintéticas. No hay datos ni cuentas reales de estudiantes."""
import json
from datetime import date
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app.config import Settings, BASE_DIR
from backend.app.main import create_app


@pytest.fixture
def demo_settings():
    return Settings(catalog_file=BASE_DIR / 'data/catalog.demo.json',
                    fallback_file=BASE_DIR / 'data/catalog.snapshot.json',
                    allow_demo_records=True, ai_mode='demo')


@pytest.fixture
def demo_client(demo_settings):
    from backend.app.ai_adapter import DemoAdapter
    return TestClient(create_app(settings=demo_settings, ai_adapter=DemoAdapter(),
                                 today=lambda: date(2026, 11, 6)))


@pytest.fixture
def demo_payload():
    return {'faculty_code': 'FISI', 'message': 'Necesito orientación para adaptarme a la universidad',
            'clarification_answer': None, 'clarification_used': False, 'previous_service_ids': []}
