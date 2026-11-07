"""Acceso opcional por correo/contraseña e historial privado. Sesión HttpOnly."""
from uuid import UUID

import httpx
from backend.app.route_ticket import InvalidRouteTicket
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, SecretStr, field_validator

from backend.app.auth_history import (UpstreamFailure, assert_origin, clear_session,
                                      get_identity, set_session)
from backend.app.repository import public_service

router = APIRouter(prefix='/api')


class EmailRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)


    @field_validator('email')
    @classmethod
    def check_email(cls, value):
        import re
        email = value.strip().lower()
        # Filtro de sufijo institucional, NO prueba la titularidad del buzón.
        if not re.fullmatch(r'[^\s@]+@unmsm\.edu\.pe', email):
            raise ValueError('El correo debe terminar en @unmsm.edu.pe.')
        return email


class CredentialsRequest(EmailRequest):
    # SecretStr evita exponer el valor en representaciones y errores del modelo.
    password: SecretStr = Field(min_length=8, max_length=128)


def available(request: Request):
    if not request.app.state.settings.enable_history:
        raise HTTPException(503, 'Autenticación e historial no habilitados.')
    if not request.app.state.settings.cookie_secure and request.url.hostname not in ('localhost', '127.0.0.1', 'testserver'):
        raise HTTPException(503, 'Se requiere HTTPS para gestionar sesiones.')


@router.get('/features')
def features(request: Request):
    return {'history_enabled': request.app.state.settings.enable_history}


def _authenticate(session: dict, request: Request, response: Response):
    try:
        uid = request.app.state.identity.user(session['access_token'])
    except (UpstreamFailure, KeyError, TypeError):
        raise HTTPException(503, 'No se pudo verificar la sesión.') from None
    set_session(response, session, secure=request.app.state.settings.cookie_secure)
    return {'authenticated': True, 'user_id': uid}


@router.post('/auth/signup')
def auth_signup(body: CredentialsRequest, request: Request, response: Response):
    available(request)
    assert_origin(request)
    ip = request.client.host if request.client else 'local'
    request.app.state.attempt_limiter.check(f'signup:{ip}', count=3)
    try:
        session = request.app.state.identity.sign_up(
            body.email, body.password.get_secret_value())
    except UpstreamFailure as error:
        # Solo afirmar duplicado si GoTrue lo devuelve explícitamente.
        # Con confirmación activa Supabase puede ocultarlo deliberadamente.
        cause = error.__cause__
        if isinstance(cause, httpx.HTTPStatusError):
            try:
                detail = cause.response.json()
            except ValueError:
                detail = {}
            if isinstance(detail, dict) and (
                detail.get('code') in {'user_already_exists', 'user_already_registered'}
                or str(detail.get('msg') or detail.get('message') or '').lower().strip()
                == 'user already registered'
            ):
                raise HTTPException(409, 'Este correo ya tiene una cuenta. Inicia sesión.') from None
        raise HTTPException(400, 'No se pudo completar el registro. Vuelve a intentarlo o inicia sesión si ya tienes cuenta.') from None
    if session.get('confirmation_required'):
        return {'authenticated': False, 'confirmation_required': True}
    return _authenticate(session, request, response)


@router.post('/auth/login')
def auth_login(body: CredentialsRequest, request: Request, response: Response):
    available(request)
    assert_origin(request)
    ip = request.client.host if request.client else 'local'
    request.app.state.attempt_limiter.check(f'login:{ip}', count=5)
    try:
        session = request.app.state.identity.sign_in(
            body.email, body.password.get_secret_value())
    except UpstreamFailure:
        # No distinguir correo no registrado, contraseña errónea o cuenta pendiente.
        raise HTTPException(401, 'No se pudo iniciar sesión. Verifica tus credenciales.') from None
    return _authenticate(session, request, response)


@router.get('/auth/me')
def auth_me(request: Request, response: Response):
    if not request.app.state.settings.enable_history:
        return {'authenticated': False}
    user = get_identity(request, required=False)
    if user:
        return {'authenticated': True, 'user_id': user.user_id}
    refresh = request.cookies.get('conecta_refresh')
    if refresh:
        try:
            session = request.app.state.identity.refresh(refresh)
            uid = request.app.state.identity.user(session['access_token'])
            set_session(response, session, secure=request.app.state.settings.cookie_secure)
            return {'authenticated': True, 'user_id': uid}
        except UpstreamFailure:
            clear_session(response)
    return {'authenticated': False}


@router.post('/auth/logout')
def logout(request: Request, response: Response):
    assert_origin(request)
    token = request.cookies.get('conecta_access')
    if token and request.app.state.settings.enable_history:
        try:
            request.app.state.identity.logout(token)
        except UpstreamFailure:
            pass  # Borrar cookie local no implica revocación remota demostrada.
    clear_session(response)
    return {'authenticated': False}




class SaveRouteRequest(BaseModel):
    route_ticket: str = Field(min_length=20, max_length=2048)
    client_request_id: UUID


@router.post('/history/save')
def save_existing_route(body: SaveRouteRequest, request: Request):
    """Persiste la ruta previamente emitida, sin repetir la llamada a IA."""
    available(request)
    assert_origin(request)
    user = get_identity(request)
    request.app.state.attempt_limiter.check(f'save:{user.user_id}', count=20, window=600)
    try:
        receipt = request.app.state.route_ticket_signer.verify(body.route_ticket)
    except InvalidRouteTicket:
        raise HTTPException(422, 'La ruta caducó. Genera una consulta nueva.') from None
    eligible, source, _, _ = request.app.state.route_service._catalog(receipt['f'])
    current = {service.id for service in eligible}
    if source != receipt['s'] or not set(receipt['i']).issubset(current):
        raise HTTPException(409, 'El catálogo cambió. Genera una ruta nueva antes de guardarla.')
    try:
        saved_id = request.app.state.history.insert(
            user, ids=receipt['i'], faculty_code=receipt['f'],
            source=source, request_id=body.client_request_id,
        )
    except UpstreamFailure:
        raise HTTPException(503, 'No se pudo guardar la ruta en este momento.') from None
    return {'saved': True, 'id': saved_id}


@router.get('/history')
def history(request: Request, limit: int = 20, offset: int = 0):
    available(request)
    user = get_identity(request)
    if not 1 <= limit <= 50 or not 0 <= offset <= 10000:
        raise HTTPException(422, 'Paginación no válida.')
    try:
        entries = request.app.state.history.list(user, limit=limit, offset=offset)
    except UpstreamFailure:
        raise HTTPException(503, 'Historial temporalmente no disponible.') from None
    route = request.app.state.route_service
    answer = []
    for entry in entries:
        try:
            faculty = entry['faculty_code']
            ids = entry['service_ids']
            if not isinstance(ids, list) or len(ids) > 3:
                continue
            eligible, _, _, _ = route._catalog(faculty)
            by_id = {s.id: s for s in eligible}
            cards = [public_service(by_id[sid], as_of=route.today()) for sid in ids if sid in by_id]
            answer.append({'id': str(UUID(entry['id'])), 'created_at': entry['created_at'],
                           'faculty_code': faculty, 'catalog_source': entry['catalog_source'],
                           'service_ids': ids, 'services': cards,
                           'needs_revalidation': len(cards) != len(ids)})
        except (KeyError, TypeError, ValueError):
            continue
    return {'items': answer, 'limit': limit, 'offset': offset}


@router.delete('/history/{route_id}')
def delete_one(route_id: UUID, request: Request):
    available(request)
    assert_origin(request)
    user = get_identity(request)
    try:
        request.app.state.history.delete(user, route_id)
    except UpstreamFailure:
        raise HTTPException(503, 'No se pudo borrar la ruta.') from None
    return {'deleted': True}


@router.delete('/history')
def delete_all(request: Request):
    available(request)
    assert_origin(request)
    user = get_identity(request)
    try:
        request.app.state.history.delete(user)
    except UpstreamFailure:
        raise HTTPException(503, 'No se pudo borrar el historial.') from None
    return {'deleted': True}
