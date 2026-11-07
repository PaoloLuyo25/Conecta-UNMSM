"""T05: esquema estricto de servicio institucional para el laboratorio.

Este módulo NO almacena registros ni decide elegibilidad de facultad.
Los valores de un registro deben provenir de evidencia, nunca de Gemini.
"""

from datetime import date
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, model_validator


NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
FacultyCode = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[A-Z][A-Z0-9_]*$")
]


class CategoryCode(str, Enum):
    BIENESTAR = "bienestar"
    UNAYOE = "unayoe"
    CLINICA_GENERAL = "clinica_general"
    SALUD_MENTAL = "salud_mental"
    TRANSPORTE_EXTERNO = "transporte_externo"
    BECAS = "becas"
    MOVILIDAD_ACADEMICA = "movilidad_academica"
    OPORTUNIDADES_ACADEMICAS = "oportunidades_academicas"


class EvidenceType(str, Enum):
    OFFICIAL_WEB = "web_oficial"
    OFFICIAL_DOCUMENT = "documento_oficial"
    DIRECT_INFORMATION = "informacion_directa"
    TEST = "prueba_ficticia"


class AvailabilityStatus(str, Enum):
    CONFIRMED = "confirmado_documentalmente"
    NEEDS_CONFIRMATION = "vigencia_por_confirmar"
    CLOSED = "cerrado_documentado"
    INSUFFICIENT = "datos_insuficientes"


class RouteRegion(str, Enum):
    NORTH = "norte"
    SOUTH = "sur"
    CENTER = "centro"
    EAST = "este"


class ContactInfo(BaseModel):
    """Solo canales publicados y confirmados; ningún dato se deduce."""

    model_config = ConfigDict(extra="forbid")

    email: NonBlank | None = None
    phone: NonBlank | None = None


class Service(BaseModel):
    """Contrato de catálogo según docs/catalog-contract.md, sin datos reales."""

    model_config = ConfigDict(extra="forbid")

    id: NonBlank
    name: NonBlank
    faculty_code: FacultyCode
    # Solo si hay evidencia de cobertura común a TODAS las facultades.
    # El valor por defecto es conservador: no se comparte.
    accessible_to_all_faculties: bool = False
    category_code: CategoryCode
    description: NonBlank
    needs_tags: list[NonBlank] = Field(default_factory=list)
    audience: NonBlank | None = None
    modality: list[NonBlank] = Field(default_factory=list)
    requirements: list[NonBlank] = Field(default_factory=list)
    official_steps: list[NonBlank] = Field(default_factory=list)
    contact: ContactInfo | None = None
    location: NonBlank | None = None
    hours: NonBlank | None = None
    route_region: RouteRegion | None = None
    stops: list[NonBlank] = Field(default_factory=list)
    source_url: HttpUrl | None = None
    evidence_type: EvidenceType
    source_published_at: date | None = None
    verified_at: date | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    availability_status: AvailabilityStatus
    warnings: list[NonBlank] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_context(self) -> "Service":
        if self.accessible_to_all_faculties and self.faculty_code != "CENTRAL":
            raise ValueError("La cobertura universal solo es válida para servicios centrales.")
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        if self.category_code != CategoryCode.TRANSPORTE_EXTERNO and (self.route_region or self.stops):
            raise ValueError("Las zonas y paradas solo corresponden a transporte externo.")
        return self


def service_warnings(service: Service, *, as_of: date) -> list[str]:
    """Advertencias deterministas sin reinterpretar el estado de la fuente.

    `as_of` es explícito para obtener tests reproducibles. Las advertencias
    complementan `availability_status` pero no crean disponibilidad en vivo.
    """
    warnings = list(service.warnings)

    if service.evidence_type == EvidenceType.TEST:
        warnings.append("Registro ficticio exclusivo para pruebas; no es un servicio real.")

    if service.availability_status == AvailabilityStatus.NEEDS_CONFIRMATION:
        warnings.append("Vigencia por confirmar")
    elif service.availability_status == AvailabilityStatus.CLOSED:
        warnings.append("Cerrado según la documentación disponible.")
    elif service.availability_status == AvailabilityStatus.INSUFFICIENT:
        warnings.append("Datos insuficientes para confirmar la disponibilidad.")

    if service.valid_until is not None and service.valid_until < as_of:
        warnings.append("Periodo de vigencia vencido; no anunciar como disponible.")
    elif service.valid_from is not None and service.valid_from > as_of:
        warnings.append("Periodo de vigencia aún no iniciado.")

    return warnings
