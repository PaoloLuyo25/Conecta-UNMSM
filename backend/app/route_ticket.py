"""Comprobante temporal de ruta. Solo IDs públicos; no texto de la consulta.

La clave se genera por proceso (laboratorio monoproceso). Reiniciar invalida
comprobantes anteriores; no invalida historiales ya persistidos.
"""
import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any


class InvalidRouteTicket(ValueError):
    pass


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def unb64(value: str) -> bytes:
    return base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True)


class RouteTicketSigner:
    """Autentica la selección de la API sin usar token del usuario."""

    def __init__(self, secret: bytes | None = None, *, ttl: int = 1800, clock=None):
        self.secret = secret if secret is not None else os.urandom(32)
        if len(self.secret) < 32:
            raise ValueError('Se necesitan al menos 32 bytes de secreto.')
        self.ttl = ttl
        self.clock = clock or time.time

    def issue(self, *, faculty: str, ids: list[str], source: str) -> str:
        if source not in {'primary', 'local_snapshot'} or not 1 <= len(ids) <= 3 or len(set(ids)) != len(ids):
            raise InvalidRouteTicket('Selección no apta para guardar.')
        body = {'v': 1, 'f': faculty, 'i': ids, 's': source, 't': int(self.clock())}
        data = b64(json.dumps(body, separators=(',', ':'), ensure_ascii=True, sort_keys=True).encode())
        signature = b64(hmac.digest(self.secret, data.encode(), hashlib.sha256))
        return data + '.' + signature

    def verify(self, token: str) -> dict[str, Any]:
        if not isinstance(token, str) or len(token) > 2048 or '.' not in token:
            raise InvalidRouteTicket('Comprobante inválido.')
        try:
            payload, signature = token.split('.')
            check = b64(hmac.digest(self.secret, payload.encode('ascii'), hashlib.sha256))
            if not hmac.compare_digest(check, signature):
                raise InvalidRouteTicket('Comprobante no auténtico.')
            body = json.loads(unb64(payload))
            age = self.clock() - body['t']
            if (set(body) != {'v', 'f', 'i', 's', 't'} or body['v'] != 1
                or type(body['t']) is not int or not 0 <= age <= self.ttl
                or not isinstance(body['f'], str) or not body['f']
                or not isinstance(body['i'], list) or not 1 <= len(body['i']) <= 3
                or not all(isinstance(i, str) and 0 < len(i) <= 80 for i in body['i'])
                or len(set(body['i'])) != len(body['i'])
                or body['s'] not in {'primary', 'local_snapshot'}):
                raise InvalidRouteTicket('Comprobante vencido o inválido.')
            return body
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError) as exc:
            raise InvalidRouteTicket('Comprobante vencido o inválido.') from exc
