"""Auth correo/contraseña y rutas privadas: servidor intermedio, JWT y RLS.

No usa service_role; no registra tokens ni el texto de las consultas.
"""
from dataclasses import dataclass
from datetime import datetime
import re
import time
from uuid import UUID

import httpx
from fastapi import HTTPException, Request, Response


ACCESS_COOKIE = 'conecta_access'
REFRESH_COOKIE = 'conecta_refresh'


class UpstreamFailure(Exception):
    """Fallo controlado; no propagar detalles ni secretos de terceros."""


@dataclass(frozen=True)
class Identity:
    user_id: str
    access_token: str


class SupabaseIdentity:
    def __init__(self, url: str, key: str):
        self.base = url.rstrip('/')
        self.key = key

    def _call(self, method: str, endpoint: str, *, token: str | None = None,
              payload: dict | None = None, params: dict | None = None,
              prefer: str | None = None):
        if not self.base.startswith('https://') or not self.key:
            raise UpstreamFailure('Autenticación sin conexión segura.')
        # Las claves publishable nuevas NO son JWT: apikey identifica el proyecto.
        # Únicamente un token emitido por Supabase Auth va en Authorization.
        headers = {'apikey': self.key, 'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        if prefer:
            headers['Prefer'] = prefer
        try:
            with httpx.Client(timeout=10.0, follow_redirects=False) as client:
                r = client.request(method, self.base + endpoint,
                                   json=payload, params=params, headers=headers)
            r.raise_for_status()
            return r.json() if r.content else None
        except (httpx.HTTPError, ValueError) as exc:
            raise UpstreamFailure('Supabase rechazó o no completó la operación.') from exc

    @staticmethod
    def _checked_session(data: dict) -> dict:
        # Si Supabase exige confirmar el correo, signup devuelve usuario SIN sesión.
        # Nunca afirmar acceso si no hay tokens utilizables.
        if not isinstance(data, dict) or not data.get('access_token') or not data.get('refresh_token'):
            raise UpstreamFailure('No se obtuvo una sesión verificable.')
        return data

    def sign_up(self, email: str, password: str) -> dict:
        data = self._call('POST', '/auth/v1/signup',
                          payload={'email': email, 'password': password})
        if not isinstance(data, dict):
            raise UpstreamFailure('Supabase no devolvió una respuesta válida.')
        # Con Confirm Email activo, GoTrue acepta la solicitud pero no emite
        # una sesión hasta que el titular confirme su correo. No se debe
        # confundir esta respuesta con un error, ni crear cookies artificiales.
        if 'access_token' in data or 'refresh_token' in data:
            return self._checked_session(data)
        user = data.get('user', data)
        if isinstance(user, dict) and user.get('id'):
            return {'confirmation_required': True}
        raise UpstreamFailure('No se pudo comprobar el resultado del registro.')

    def sign_in(self, email: str, password: str) -> dict:
        data = self._call('POST', '/auth/v1/token',
                          params={'grant_type': 'password'},
                          payload={'email': email, 'password': password})
        return self._checked_session(data)

    def refresh(self, token: str) -> dict:
        data = self._call('POST', '/auth/v1/token',
                          params={'grant_type': 'refresh_token'},
                          payload={'refresh_token': token})
        if not isinstance(data, dict) or not data.get('access_token') or not data.get('refresh_token'):
            raise UpstreamFailure('Sesión caducada.')
        return data

    def user(self, token: str) -> str:
        data = self._call('GET', '/auth/v1/user', token=token)
        # Valida también las sesiones existentes, no solo el formulario de acceso.
        # Un correo con este sufijo NO acredita la titularidad ni la matrícula.
        try:
            email = data['email'].strip().lower()
            if not re.fullmatch(r'[^\s@]+@unmsm\.edu\.pe', email):
                raise ValueError('Dominio de cuenta no permitido.')
            return str(UUID(data['id']))
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise UpstreamFailure('Identidad institucional no admitida.') from exc

    def logout(self, token: str):
        self._call('POST', '/auth/v1/logout', token=token)


class SupabaseHistory:
    def __init__(self, identity: SupabaseIdentity):
        self.identity = identity

    def insert(self, user: Identity, *, ids: list[str], faculty_code: str,
               source: str, request_id: UUID) -> str:
        # El conflicto repetido se resuelve leyendo la fila que pertenece al mismo usuario.
        row = {'user_id': user.user_id, 'service_ids': ids,
               'faculty_code': faculty_code, 'catalog_source': source,
               'client_request_id': str(request_id)}
        self.identity._call('POST', '/rest/v1/route_history', token=user.access_token,
                            params={'on_conflict': 'user_id,client_request_id'},
                            prefer='resolution=ignore-duplicates,return=minimal', payload=row)
        entries = self.identity._call('GET', '/rest/v1/route_history', token=user.access_token,
                                      params={'select': 'id,service_ids,faculty_code,catalog_source,created_at,expires_at',
                                              'user_id': f'eq.{user.user_id}',
                                              'client_request_id': f'eq.{request_id}', 'limit': 1})
        if not isinstance(entries, list) or not entries:
            raise UpstreamFailure('No fue posible confirmar el historial.')
        return str(UUID(entries[0]['id']))

    def list(self, user: Identity, *, limit: int = 20, offset: int = 0) -> list[dict]:
        data = self.identity._call('GET', '/rest/v1/route_history', token=user.access_token,
                                  params={'select': 'id,service_ids,faculty_code,catalog_source,created_at,expires_at',
                                          'user_id': f'eq.{user.user_id}',
                                          'expires_at': f'gt.{datetime.now().astimezone().isoformat()}',
                                          'order': 'created_at.desc', 'limit': limit, 'offset': offset})
        if not isinstance(data, list):
            raise UpstreamFailure('Historial inválido.')
        return data

    def delete(self, user: Identity, route_id: UUID | None = None):
        params = {'user_id': f'eq.{user.user_id}'}
        if route_id is not None:
            params['id'] = f'eq.{route_id}'
        self.identity._call('DELETE', '/rest/v1/route_history', token=user.access_token, params=params)


def set_session(response: Response, data: dict, *, secure: bool):
    for name, token, duration in (
        (ACCESS_COOKIE, data['access_token'], int(data.get('expires_in', 3600))),
        (REFRESH_COOKIE, data['refresh_token'], 30 * 24 * 3600),
    ):
        response.set_cookie(name, token, httponly=True, secure=secure,
                            samesite='strict', max_age=max(1, duration), path='/')


def clear_session(response: Response):
    for name in (ACCESS_COOKIE, REFRESH_COOKIE):
        response.delete_cookie(name, path='/', samesite='strict')


def assert_origin(request: Request):
    """Mutaciones basadas en cookies exigen origen de navegador coincidente."""
    actual = request.headers.get('origin')
    expected = request.app.state.settings.public_origin.rstrip('/') or str(request.base_url).rstrip('/')
    if not actual or actual.rstrip('/') != expected:
        raise HTTPException(status_code=403, detail='Origen no permitido.')


def get_identity(request: Request, *, required=True) -> Identity | None:
    if not request.app.state.settings.enable_history:
        if required:
            raise HTTPException(503, 'El historial no está habilitado.')
        return None
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        if required:
            raise HTTPException(401, 'Inicia sesión para ver tu historial.')
        return None
    try:
        uid = request.app.state.identity.user(token)
        return Identity(uid, token)
    except UpstreamFailure:
        if required:
            raise HTTPException(401, 'La sesión ha caducado o no es válida.') from None
        return None


class AttemptLimiter:
    """Límite mínimo en memoria para laboratorio, no distribuido ni persistente."""
    def __init__(self):
        self.calls: dict[str, list[float]] = {}

    def check(self, key: str, *, count: int = 3, window: int = 600):
        now = time.monotonic()
        # Evita crecimiento ilimitado de las claves antiguas en un proceso largo.
        self.calls = {k: [t for t in v if now - t < window]
                      for k, v in self.calls.items() if any(now - t < window for t in v)}
        attempts = self.calls.setdefault(key, [])
        if len(attempts) >= count:
            raise HTTPException(429, 'Demasiados intentos. Intenta más tarde.')
        attempts.append(now)
