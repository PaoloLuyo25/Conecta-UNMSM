"""Contrato HTTP v1: solo health, services y route."""
import re
from datetime import date
from uuid import UUID
from typing import Literal

from fastapi import APIRouter, Request, HTTPException
from backend.app.auth_history import assert_origin, get_identity, UpstreamFailure
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

router = APIRouter(prefix='/api')


class HealthResponse(BaseModel):
    status: Literal['ok'] = 'ok'


class RouteRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    faculty_code: str = Field(default='FISI', min_length=2, max_length=40, pattern=r'^[A-Z][A-Z0-9_]*$')
    message: str
    applicant_type: Literal['sin_especificar', 'pregrado', 'posgrado', 'docentes'] = 'sin_especificar'
    clarification_answer: str | None = None
    clarification_used: bool = False
    previous_service_ids: list[str] = Field(default_factory=list, max_length=20)
    save_to_history: bool = False
    client_request_id: UUID | None = None

    @field_validator('message', 'clarification_answer')
    @classmethod
    def validate_text(cls, value, info):
        if value is None:
            return None
        value = value.strip()
        limit = 800 if info.field_name == 'message' else 400
        visible = re.sub(r'<[^>]*>', '', value)
        visible = re.sub(r'[\x00-\x1f\x7f]', '', visible).strip()
        if (not visible and info.field_name == 'message') or len(visible) > limit:
            raise ValueError(f'El campo debe contener entre 1 y {limit} caracteres visibles.')
        if len(value) > limit * 3:
            raise ValueError('Entrada demasiado extensa.')
        return value or None

    @field_validator('previous_service_ids')
    @classmethod
    def validate_ids(cls, value):
        if any(not isinstance(item, str) or len(item) > 80 for item in value):
            raise ValueError('Los identificadores previos no cumplen el formato permitido.')
        return value

    @model_validator(mode='after')
    def check_message(self):
        if self.message is None:
            raise ValueError('Introduce una necesidad para consultar.')
        if self.save_to_history and self.client_request_id is None:
            raise ValueError('Para guardar, asigna un client_request_id UUID.')
        if self.clarification_used and not self.clarification_answer:
            raise ValueError('Indica la respuesta a la aclaración utilizada.')
        return self


class RouteResponse(BaseModel):
    mode: Literal['question', 'route', 'degraded']
    needs: list[str]
    constraints: list[str]
    question: str | None
    services: list[dict]
    historical_services: list[dict] = Field(default_factory=list)
    country_context: str | None = None
    warnings: list[str]
    ai_used: bool
    catalog_source: Literal['primary', 'local_snapshot', 'unavailable']
    catalog_verified_at: date | None
    history_saved: bool = False
    history_id: str | None = None
    route_ticket: str | None = None


class CatalogResponse(BaseModel):
    services: list[dict]
    catalog_source: Literal['primary', 'local_snapshot', 'unavailable']
    catalog_verified_at: date | None
    warnings: list[str]


@router.get('/health', response_model=HealthResponse, tags=['Sistema'])
def health():
    """No implica que Gemini o las fuentes estén operativos."""
    return HealthResponse()


@router.get('/services', response_model=CatalogResponse, tags=['Servicios'])
def services(request: Request, faculty_code: str = 'FISI'):
    if not re.fullmatch(r'[A-Z][A-Z0-9_]{1,39}', faculty_code):
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail='Código de facultad no válido.')
    return request.app.state.route_service.catalog(faculty_code=faculty_code)


@router.post('/route', response_model=RouteResponse, tags=['Rutas'])
def route(body: RouteRequest, request: Request):
    answer = request.app.state.route_service.route(body)
    answer['history_saved'] = False
    answer['history_id'] = None
    answer['route_ticket'] = None
    if answer['mode'] == 'route' and 1 <= len(answer['services']) <= 3:
        answer['route_ticket'] = request.app.state.route_ticket_signer.issue(
            faculty=body.faculty_code,
            ids=[service['id'] for service in answer['services']],
            source=answer['catalog_source'],
        )
    if not body.save_to_history:
        return answer
    assert_origin(request)
    if not request.app.state.settings.enable_history:
        answer['warnings'].append('Historial desactivado; no se guardó la ruta.')
        return answer
    user = get_identity(request, required=False)
    if not user:
        answer['warnings'].append('Inicia sesión y vuelve a solicitar guardar la ruta.')
        return answer
    if answer['mode'] != 'route' or not 1 <= len(answer['services']) <= 3:
        answer['warnings'].append('Solo pueden guardarse rutas válidas; esta consulta no se guardó.')
        return answer
    if answer['catalog_source'] not in {'primary', 'local_snapshot'}:
        return answer
    try:
        answer['history_id'] = request.app.state.history.insert(
            user, ids=[s['id'] for s in answer['services']],
            faculty_code=body.faculty_code, source=answer['catalog_source'],
            request_id=body.client_request_id)
        answer['history_saved'] = True
    except UpstreamFailure:
        answer['warnings'].append('No fue posible guardar la ruta; puedes seguir consultándola.')
    return answer
