"""Arranque único. Frontend y API comparten origen (sin CORS abierto)."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.ai_adapter import DemoAdapter, GeminiAdapter
from backend.app.auth_api import router as auth_router
from backend.app.auth_history import AttemptLimiter, SupabaseHistory, SupabaseIdentity
from backend.app.route_ticket import RouteTicketSigner
from backend.app.districts import DistrictDirectory
from backend.app.api import router as api_router
from backend.app.config import Settings, BASE_DIR
from backend.app.local_repo import LocalCatalogRepository
from backend.app.route_service import RouteService
from backend.app.supabase_repo import SupabaseCatalogRepository

FRONTEND = BASE_DIR / 'frontend'


def create_app(settings: Settings | None = None, *, repository=None, ai_adapter=None,
               today=None, identity=None, history=None) -> FastAPI:
    settings = settings or Settings.from_env()
    if repository is None:
        repository = (SupabaseCatalogRepository(settings.supabase_url, settings.supabase_anon_key)
                      if settings.catalog_backend == 'supabase' else
                      LocalCatalogRepository(settings.catalog_file))
    if ai_adapter is None:
        ai_adapter = (DemoAdapter() if settings.ai_mode == 'demo' else
                      GeminiAdapter(settings.gemini_api_key, settings.gemini_model,
                                    settings.gemini_timeout_seconds))
    app = FastAPI(title='Conecta UNMSM')
    app.state.settings = settings
    app.state.identity = identity or SupabaseIdentity(settings.supabase_url, settings.supabase_anon_key)
    app.state.history = history or SupabaseHistory(app.state.identity)
    app.state.attempt_limiter = AttemptLimiter()
    app.state.route_ticket_signer = RouteTicketSigner()
    districts = DistrictDirectory.from_markdown(settings.districts_file)
    app.state.route_service = RouteService(repository, ai_adapter, settings,
                                          today=today, districts=districts)
    @app.exception_handler(RequestValidationError)
    async def safe_auth_validation(request: Request, exc: RequestValidationError):
        # La respuesta estándar de FastAPI puede incluir el input original
        # (por ejemplo la contraseña) en errores 422; NUNCA devolverlo.
        if request.url.path in ('/api/auth/signup', '/api/auth/login'):
            return JSONResponse(status_code=422, content={
                'detail': 'Revisa el correo y utiliza una contraseña de 8 a 128 caracteres.'})
        return await request_validation_exception_handler(request, exc)

    app.include_router(api_router)
    app.include_router(auth_router)

    @app.middleware('http')
    async def no_cache_frontend(request, call_next):
        response = await call_next(request)
        if request.url.path == '/' or request.url.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'no-store, max-age=0'
        return response

    @app.get('/', include_in_schema=False)
    def home():
        return FileResponse(FRONTEND / 'index.html')

    app.mount('/static', StaticFiles(directory=FRONTEND), name='static')
    return app


app = create_app()
