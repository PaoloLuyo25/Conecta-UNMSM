"""Configuración mediante entorno. No se almacenan claves en el repositorio."""
from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / '.env')


@dataclass(frozen=True)
class Settings:
    catalog_backend: str = 'local'
    catalog_file: Path = BASE_DIR / 'data/catalog.academico.json'
    fallback_file: Path = BASE_DIR / 'data/catalog.academico.json'
    allow_demo_records: bool = False
    ai_mode: str = 'gemini'
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.5-flash-lite'
    gemini_timeout_seconds: int = 10
    supabase_url: str = ''
    supabase_anon_key: str = ''
    districts_file: Path = BASE_DIR / 'data/distritos_verificados.md'
    enable_history: bool = False  # Opt-in técnico: requiere migración, Auth y pruebas RLS.
    cookie_secure: bool = False  # Solo localhost; poner true detrás de HTTPS.
    public_origin: str = ''

    @classmethod
    def from_env(cls):
        def as_path(value: str) -> Path:
            p = Path(value)
            return p if p.is_absolute() else BASE_DIR / p

        return cls(
            catalog_backend=os.getenv('CATALOG_BACKEND', 'local').lower(),
            catalog_file=as_path(os.getenv('CATALOG_FILE', 'data/catalog.academico.json')),
            fallback_file=as_path(os.getenv('FALLBACK_FILE', 'data/catalog.academico.json')),
            allow_demo_records=os.getenv('ALLOW_DEMO_RECORDS', 'false').lower() == 'true',
            ai_mode=os.getenv('AI_MODE', 'gemini').lower(),
            gemini_api_key=os.getenv('GEMINI_API_KEY', ''),
            gemini_model=os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite'),
            gemini_timeout_seconds=int(os.getenv('GEMINI_TIMEOUT_SECONDS', '10')),
            districts_file=as_path(os.getenv('DISTRICTS_FILE', 'data/distritos_verificados.md')),
            enable_history=os.getenv('ENABLE_HISTORY', 'false').lower() == 'true',
            cookie_secure=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
            public_origin=os.getenv('PUBLIC_ORIGIN', ''),
            supabase_url=os.getenv('SUPABASE_URL', ''),
            supabase_anon_key=os.getenv('SUPABASE_PUBLISHABLE_KEY', '') or os.getenv('SUPABASE_ANON_KEY', ''),
        )
