"""T05: pruebas del esquema de catálogo y de las señales de vigencia."""

from datetime import date

import pytest
from pydantic import ValidationError

from backend.app.schemas import (
    AvailabilityStatus,
    EvidenceType,
    Service,
    service_warnings,
)


@pytest.fixture
def synthetic_service():
    # Datos enteramente ficticios; no representan servicios de la UNMSM.
    return {
        "id": "TEST-SERVICE-01",
        "name": "Servicio ficticio de prueba",
        "faculty_code": "FISI",
        "category_code": "bienestar",
        "description": "Registro sintético para verificar el contrato del catálogo.",
        "needs_tags": ["orientacion"],
        "evidence_type": "prueba_ficticia",
        "availability_status": "vigencia_por_confirmar",
    }


@pytest.mark.parametrize("missing", ["id", "name", "faculty_code", "category_code", "description", "evidence_type", "availability_status"])
def test_required_fields_cannot_be_missing(synthetic_service, missing):
    synthetic_service.pop(missing)
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)


@pytest.mark.parametrize("field", ["id", "name", "description", "faculty_code"])
def test_required_text_cannot_be_whitespace(synthetic_service, field):
    synthetic_service[field] = " \t "
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)


def test_unsupported_category_is_rejected(synthetic_service):
    synthetic_service["category_code"] = "inventada"
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)


def test_evidence_and_status_are_limited_to_contract_enums(synthetic_service):
    synthetic_service["evidence_type"] = "blog"
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)
    synthetic_service["evidence_type"] = EvidenceType.TEST
    synthetic_service["availability_status"] = "abierto_ahora"
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)


def test_scope_is_not_forced_to_fisi(synthetic_service):
    synthetic_service["faculty_code"] = "OTRA_FACULTAD"
    assert Service.model_validate(synthetic_service).faculty_code == "OTRA_FACULTAD"
    # La exclusión de otras facultades la aplicará el Repository (T06).


def test_transport_region_is_not_attributed_to_other_categories(synthetic_service):
    synthetic_service["route_region"] = "norte"
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)


def test_transport_accepts_documented_region_without_creating_stops(synthetic_service):
    synthetic_service["category_code"] = "transporte_externo"
    synthetic_service["route_region"] = "norte"
    service = Service.model_validate(synthetic_service)
    assert service.route_region.value == "norte"
    assert service.stops == []
    assert service.hours is None


def test_invalid_transport_region_is_rejected(synthetic_service):
    synthetic_service.update(category_code="transporte_externo", route_region="oeste")
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)


def test_missing_optional_fields_are_never_filled_in(synthetic_service):
    service = Service.model_validate(synthetic_service)
    assert service.contact is None
    assert service.location is None
    assert service.hours is None
    assert service.source_url is None
    assert service.official_steps == []
    assert service.requirements == []
    assert service.warnings == []


def test_source_url_only_accepts_http_or_https(synthetic_service):
    synthetic_service["source_url"] = "javascript:alert(1)"
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)
    synthetic_service["source_url"] = "https://example.invalid/registro-ficticio"
    assert Service.model_validate(synthetic_service).source_url is not None


def test_dates_cannot_be_inverted(synthetic_service):
    synthetic_service.update(valid_from="2026-12-01", valid_until="2026-11-01")
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)


def test_expired_service_is_flagged_without_changing_source_status(synthetic_service):
    synthetic_service.update(valid_until="2026-10-01", availability_status=AvailabilityStatus.CONFIRMED)
    service = Service.model_validate(synthetic_service)
    warnings = service_warnings(service, as_of=date(2026, 11, 5))
    assert any("vencid" in message.lower() for message in warnings)
    assert service.availability_status == AvailabilityStatus.CONFIRMED


def test_uncertain_state_is_reported(synthetic_service):
    service = Service.model_validate(synthetic_service)
    assert "Vigencia por confirmar" in service_warnings(service, as_of=date(2026, 11, 5))


def test_fictitious_evidence_is_always_labeled_as_test(synthetic_service):
    synthetic_service["availability_status"] = AvailabilityStatus.CONFIRMED
    service = Service.model_validate(synthetic_service)
    warnings = service_warnings(service, as_of=date(2026, 11, 5))
    assert any("fictici" in message.lower() for message in warnings)


def test_undocumented_fields_are_not_silently_accepted(synthetic_service):
    synthetic_service["opening_now"] = True
    with pytest.raises(ValidationError):
        Service.model_validate(synthetic_service)


def test_valid_record_serializes_expected_enums(synthetic_service):
    service = Service.model_validate(synthetic_service)
    payload = service.model_dump(mode="json")
    assert payload["evidence_type"] == "prueba_ficticia"
    assert payload["availability_status"] == "vigencia_por_confirmar"
    assert payload["source_url"] is None
