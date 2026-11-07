"""Distritos exclusivamente desde Markdown canónico, sin catálogo geográfico embebido."""
from dataclasses import dataclass
from pathlib import Path
import re
from backend.app.normalization import fold, REGIONS


class DistrictSourceError(ValueError):
    pass


@dataclass(frozen=True)
class DistrictMatch:
    name: str
    region: str | None


class DistrictDirectory:
    """Admite únicamente tablas Markdown con columnas Distrito, Zona, Alias(es).

    Si no hay archivo canónico, la integración queda vacía y sin zonas inferidas.
    """
    def __init__(self, aliases: dict[str, DistrictMatch] | None = None, *, available=False):
        self._aliases = dict(aliases or {})
        self.available = available

    @classmethod
    def from_markdown(cls, path: Path):
        path = Path(path)
        if not path.is_file():
            return cls(available=False)
        lines = path.read_text(encoding='utf-8').splitlines()
        aliases: dict[str, DistrictMatch] = {}
        header = None
        count = 0
        for raw in lines:
            line = raw.strip()
            if not line.startswith('|') or not line.endswith('|'):
                continue
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-{3,}:?', cell) for cell in cells):
                continue
            normalized = [fold(cell) for cell in cells]
            if 'distrito' in normalized and 'zona' in normalized:
                header = normalized
                if len(set(header)) != len(header):
                    raise DistrictSourceError('Columnas duplicadas en el encabezado de distritos.')
                continue
            if header is None:
                continue
            if len(cells) != len(header):
                raise DistrictSourceError('Fila de distritos mal formada.')
            row = dict(zip(header, cells))
            name = row['distrito'].strip()
            zone = fold(row['zona']) or None
            if not name:
                raise DistrictSourceError('Distrito sin nombre.')
            if zone and zone not in REGIONS:
                raise DistrictSourceError('Zona fuera del contrato norte/sur/centro/este.')
            match = DistrictMatch(name=name, region=zone)
            aliases_raw = row.get('alias') or row.get('aliases') or ''
            for alias in [name, *re.split(r'[,;]', aliases_raw)]:
                key = fold(alias)
                if not key:
                    continue
                if key in aliases:
                    raise DistrictSourceError('Distrito o alias duplicado/ambiguo en la fuente.')
                aliases[key] = match
            count += 1
        if header is None or count == 0:
            raise DistrictSourceError('La fuente no contiene una tabla válida de distritos.')
        return cls(aliases, available=True)

    def lookup(self, text: str) -> DistrictMatch | None:
        words = fold(text)
        if not words:
            return None
        hits = []
        for alias, district in self._aliases.items():
            if re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', words):
                hits.append(district)
        unique = {(d.name, d.region) for d in hits}
        if len(unique) == 1:
            return hits[0]
        return None

    def region_of(self, name: str) -> str | None:
        item = self._aliases.get(fold(name))
        return item.region if item else None
