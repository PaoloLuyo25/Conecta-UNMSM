"""Control determinista de IDs y códigos de razones de la IA."""
from datetime import date
from backend.app.repository import public_service
from backend.app.schemas import Service

REASON_CODES = {'matches_need', 'matches_modality', 'matches_location', 'requires_confirmation'}


def validate_selection(ids: list[str], reason_codes: dict[str, str],
                       eligible: list[Service], *, as_of: date):
    by_id = {item.id: item for item in eligible}
    selected, warnings, seen = [], [], set()
    for service_id in ids:
        if service_id in seen:
            continue
        seen.add(service_id)
        if service_id not in by_id:
            warnings.append('La selección incluyó un identificador no permitido; fue descartado.')
            continue
        reason = reason_codes.get(service_id)
        if reason not in REASON_CODES:
            warnings.append('Se descartó una selección sin código de justificación válido.')
            continue
        service = by_id[service_id]
        data = public_service(service, as_of=as_of)
        explanation = {
            'matches_need': 'La ficha fue seleccionada por su relación con la necesidad descrita.',
            'matches_modality': 'La ficha incluye una modalidad documentada; comprueba su disponibilidad.',
            'matches_location': 'La ficha pertenece al ámbito o zona indicada; confirma sus detalles.',
            'requires_confirmation': 'La ficha requiere confirmar información antes de utilizar el servicio.',
        }[reason]
        data.update(why_code=reason, why_text=explanation)
        selected.append(data)
        if len(selected) == 3:
            break
    return selected, warnings
