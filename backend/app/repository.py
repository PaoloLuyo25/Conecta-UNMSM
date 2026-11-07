"""Interfaz de catálogo de solo lectura; alcance por facultad verificable."""
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from backend.app.schemas import AvailabilityStatus, EvidenceType, Service, service_warnings


class CatalogUnavailable(Exception):
    """Los datos no se pudieron recuperar o no cumplen el contrato."""


@dataclass(frozen=True)
class CatalogSnapshot:
    services: tuple[Service, ...]
    source: str
    verified_at: date | None = None


class CatalogRepository(Protocol):
    def read(self) -> CatalogSnapshot: ...


def list_eligible(snapshot: CatalogSnapshot, *, faculty_code: str, as_of: date,
                  allow_demo_records: bool) -> list[Service]:
    """Facultad elegida: propios + centrales universales; FISI conserva centrales legados."""
    eligible = []
    seen = set()
    for service in snapshot.services:
        if service.id in seen:
            raise CatalogUnavailable('Identificadores de catálogo duplicados.')
        seen.add(service.id)
        if service.faculty_code == faculty_code:
            pass
        elif service.faculty_code == 'CENTRAL' and (
                service.accessible_to_all_faculties or faculty_code == 'FISI'):
            # Excepción FISI conserva los registros centrales del piloto previo.
            pass
        else:
            # No mezclar procedimientos de una facultad con otra.
            continue
        if service.evidence_type == EvidenceType.TEST and not allow_demo_records:
            continue
        if service.evidence_type == EvidenceType.OFFICIAL_WEB and not service.source_url:
            continue
        if service.availability_status == AvailabilityStatus.CLOSED:
            continue
        if service.valid_until and service.valid_until < as_of:
            continue
        if service.valid_from and service.valid_from > as_of:
            continue
        eligible.append(service)
    return eligible


def public_service(service: Service, *, as_of: date) -> dict:
    """Devuelve solo campos contractuales, sin inventar los opcionales."""
    data = service.model_dump(mode='json')
    data['warnings'] = service_warnings(service, as_of=as_of)
    if not service.verified_at:
        data['warnings'].append('Fecha de revisión de la fuente por confirmar.')
    if not service.source_url:
        data['warnings'].append('Enlace de fuente pública no disponible; confirmar evidencia institucional.')
    return data


def list_historical(snapshot: CatalogSnapshot, *, faculty_code: str, as_of: date,
                    country_code: str, profile: str | None, allow_demo_records: bool, limit: int = 3) -> list[Service]:
    """Antecedentes revisados por país, no convocatorias disponibles.

    No se extrapola la cobertura de una facultad específica a `OTROS`.
    """
    from backend.app.targeting import audience_codes
    matched = []
    for s in snapshot.services:
        if s.faculty_code != faculty_code and not (s.faculty_code == 'CENTRAL'
                and (s.accessible_to_all_faculties or faculty_code == 'FISI')):
            continue
        if s.category_code.value != 'movilidad_academica':
            continue
        if 'pais_' + country_code not in s.needs_tags:
            continue
        if s.evidence_type == EvidenceType.TEST and not allow_demo_records:
            continue
        if not s.source_url:
            continue
        audiences = audience_codes(s)
        if profile and audiences and profile not in audiences:
            continue
        if s.availability_status != AvailabilityStatus.CLOSED and not (s.valid_until and s.valid_until < as_of):
            continue
        matched.append(s)
    return sorted(matched, key=lambda s: (s.valid_until or date.min, s.source_published_at or date.min), reverse=True)[:limit]
