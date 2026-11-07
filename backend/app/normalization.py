"""Normalización geográfica conservadora; no interpreta necesidades personales."""
from dataclasses import dataclass
import re
import unicodedata
from difflib import get_close_matches

REGIONS = ('norte', 'sur', 'centro', 'este')
# Abreviaturas deliberadamente limitadas; nuevas equivalencias requieren tests.
_ALIASES = {'nte': 'norte', 'nort': 'norte', 'nortr': 'norte', 'n': 'norte',
            's': 'sur', 'sur': 'sur', 'ctr': 'centro', 'ctro': 'centro',
            'cent': 'centro', 'est': 'este'}
_TRANSPORT = re.compile(r'\b(transport\w*|bus|buses|rutas?|paraderos?)\b')


def fold(text: str) -> str:
    base = ''.join(c for c in unicodedata.normalize('NFD', text.casefold())
                   if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', base).strip()


@dataclass(frozen=True)
class NormalizedQuery:
    original_text: str
    region_code: str | None = None
    district_name: str | None = None
    district_unmapped: bool = False
    ambiguous: bool = False
    # Solo es un dato complementario validado; Gemini sigue recibiendo texto del usuario.
    context_line: str = ''


def canonical_region(token: str, *, transport_context: bool) -> str | None:
    if not transport_context:
        return None
    token = fold(token)
    if token in REGIONS:
        return token
    # Alias de un carácter únicamente en respuesta aislada, no en mensaje libre.
    if token in _ALIASES and len(token) >= 3:
        return _ALIASES[token]
    if len(token) >= 5:
        similar = get_close_matches(token, REGIONS, n=2, cutoff=0.85)
        if len(similar) == 1:
            return similar[0]
    return None


def normalize_query(message: str, clarification_answer: str | None = None,
                    *, clarification_used: bool = False, directory=None) -> NormalizedQuery:
    text = fold(message)
    answer = fold(clarification_answer or '')
    is_transport = bool(_TRANSPORT.search(text))
    # Una aclaración aislada de región es contexto suficiente únicamente si la consulta era transporte.
    tokens = answer.split() if clarification_used and answer else text.split()
    found = {region for token in tokens
             if (region := canonical_region(token, transport_context=is_transport))}
    region = next(iter(found)) if len(found) == 1 else None
    district_name = None
    district_unmapped = False
    if directory is not None and directory.available:
        match = directory.lookup((clarification_answer or '') if clarification_used else message)
        if match is not None:
            district_name = match.name
            district_unmapped = match.region is None
            if match.region and not found and is_transport:
                region = match.region
            elif match.region and found and match.region not in found:
                region = None
                found.add(match.region)
    ambiguous = len(found) > 1
    context = f'ZONA_VERIFICADA={region}' if region and not ambiguous else ''
    return NormalizedQuery(message, region, district_name, district_unmapped, ambiguous, context)
