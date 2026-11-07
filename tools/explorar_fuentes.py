"""Exploración prudente de publicaciones de OGCRI, sin importar datos automáticamente.

Consulta feeds Atom públicos del blog y usa su archivo HTML como respaldo si
los feeds no responden. Comprueba robots.txt antes de cada origen; nunca infiere
plazos ni disponibilidad. Solo guarda candidatos para revisión humana.

Desde la raíz del proyecto:
  python -m tools.explorar_fuentes --historical-pages 2
"""
import argparse
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = 'ConectaUNMSM-Fuentes/1.1 (uso informativo; revision humana)'
MAX_BYTES = 1_500_000
ALLOWED_HOSTS = {
    'cooperacion-unmsm.blogspot.com',
    'cooperacion.unmsm.edu.pe',
    'viceacademico.unmsm.edu.pe',
    'vrip.unmsm.edu.pe',
}
BLOG = 'https://cooperacion-unmsm.blogspot.com'
SOURCES = {
    'OGCRI: últimas publicaciones': BLOG + '/feeds/posts/default?alt=atom&max-results=50',
    'OGCRI: publicaciones etiquetadas CONVENIOS': BLOG + '/feeds/posts/default/-/CONVENIOS?alt=atom&max-results=20',
}
TOPIC = re.compile(r'beca|convocator|movilidad|intercambio|convenio|posgrado|investiga|pasant|programa|taller|subvenci|cooperaci', re.I)
COUNTRY_MENTION = re.compile(r'francia|m[eé]xico|corea del sur|alemania|espa[nñ]a|china|jap[oó]n|argentina|brasil', re.I)
BLOG_POST_PATH = re.compile(r'^/20\d{2}/\d{2}/[a-z0-9_-]+\.html$', re.I)


def safe_link(url: str) -> bool:
    parsed = urlparse(url)
    return (parsed.scheme == 'https' and parsed.hostname in ALLOWED_HOSTS
            and parsed.username is None and parsed.password is None)


def annotate(row: dict) -> dict:
    match = COUNTRY_MENTION.search(row['title'])
    row['country_hint'] = match.group(0) if match else None
    row['open_status'] = 'sin_verificar'
    row['review_status'] = 'pendiente_revision'
    return row


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def plain(html: str, limit: int = 380) -> str:
    parser = PlainText()
    parser.feed(html or '')
    return re.sub(r'\s+', ' ', unescape(' '.join(parser.parts))).strip()[:limit]


def parse_atom(raw: bytes, source: str) -> list[dict]:
    root = ET.fromstring(raw)
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    items = []
    for entry in root.findall('a:entry', ns):
        title = (entry.findtext('a:title', default='', namespaces=ns) or '').strip()
        published = entry.findtext('a:published', default='', namespaces=ns) or ''
        summary = (entry.findtext('a:summary', default='', namespaces=ns)
                   or entry.findtext('a:content', default='', namespaces=ns) or '')
        link = next((tag.attrib.get('href', '') for tag in entry.findall('a:link', ns)
                     if tag.attrib.get('rel') == 'alternate'), '')
        if title and safe_link(link) and TOPIC.search(title + ' ' + plain(summary)):
            items.append(annotate({
                'title': title, 'url': link, 'published_at': published[:10] or None,
                'excerpt': plain(summary), 'source': source,
            }))
    return items


def parse_rss(raw: bytes, source: str) -> list[dict]:
    root = ET.fromstring(raw)
    items = []
    for node in root.findall('./channel/item'):
        title = (node.findtext('title') or '').strip()
        link = (node.findtext('link') or '').strip()
        summary = node.findtext('description') or ''
        if title and safe_link(link) and TOPIC.search(title + ' ' + plain(summary)):
            items.append(annotate({
                'title': title, 'url': link, 'published_at': node.findtext('pubDate'),
                'excerpt': plain(summary), 'source': source,
            }))
    return items


class ArchiveLinks(HTMLParser):
    """Lee únicamente enlaces a publicaciones del blog, nunca a destinos externos."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        href = dict(attrs).get('href', '')
        candidate = urljoin(BLOG, href)
        url = urlparse(candidate)
        if (safe_link(candidate) and url.hostname == 'cooperacion-unmsm.blogspot.com'
                and BLOG_POST_PATH.match(url.path)):
            self.current = [urlunparse((url.scheme, url.netloc, url.path, '', '', '')), []]

    def handle_data(self, data):
        if self.current is not None:
            self.current[1].append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            title = ' '.join(''.join(self.current[1]).split())
            if TOPIC.search(title) and len(title) >= 8:
                self.links.append((self.current[0], title))
            self.current = None


def parse_archive_html(raw: bytes, source: str) -> list[dict]:
    """Respaldo HTML: ninguna fecha ni estado se infiere del enlace o del año."""
    parser = ArchiveLinks()
    parser.feed(raw.decode('utf-8', errors='replace'))
    return [annotate({'title': title, 'url': url, 'published_at': None,
                      'excerpt': '', 'source': source}) for url, title in parser.links]


def _robots_allowed(url: str, timeout: int = 10) -> bool:
    uri = urlparse(url)
    robots_url = f'{uri.scheme}://{uri.netloc}/robots.txt'
    # La comprobación robots fallida no permite asumir autorización.
    robot = RobotFileParser(robots_url)
    try:
        with urlopen(Request(robots_url, headers={'User-Agent': USER_AGENT}), timeout=timeout) as response:
            if not safe_link(response.geturl()):
                raise ValueError('robots.txt redirigió a un dominio no autorizado')
            data = response.read(250_000).decode('utf-8', errors='replace').splitlines()
        robot.parse(data)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise ValueError(f'No se pudo consultar robots.txt ({type(exc).__name__})') from exc
    if not robot.can_fetch(USER_AGENT, url):
        raise ValueError('robots.txt no autoriza consultar esta ruta')
    return True


def fetch(url: str, timeout: int = 12) -> bytes:
    if not safe_link(url):
        raise ValueError('URL no HTTPS o fuera de la lista de dominios permitidos')
    _robots_allowed(url, timeout=timeout)
    request = Request(url, headers={
        'User-Agent': USER_AGENT,
        'Accept': 'application/atom+xml, application/rss+xml, application/xml, text/html',
    })
    with urlopen(request, timeout=timeout) as response:
        if not safe_link(response.geturl()):
            raise ValueError('Redirección a un dominio no permitido')
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError('Contenido mayor que el máximo permitido')
    return body


def scan(sources=None, pause: float = 1.0, *, allow_html_fallback: bool = True) -> dict:
    if sources is None:
        sources = SOURCES
    seen = {}
    errors = []
    for label, url in sources.items():
        try:
            raw = fetch(url)
            # Los feeds Blogger no siempre están disponibles; detectar HTML y usar
            # el parser limitado, sin tratar una página HTML como RSS válido.
            prefix = raw[:1000].lstrip(b'\xef\xbb\xbf\t\r\n ').lower()
            if b'<feed' in prefix or b':feed' in prefix:
                rows = parse_atom(raw, label)
            elif b'<rss' in prefix or b'<rdf' in prefix:
                rows = parse_rss(raw, label)
            elif b'<html' in prefix or b'<!doctype html' in prefix:
                rows = parse_archive_html(raw, label + ' (HTML)')
            else:
                raise ValueError('La respuesta no es un feed Atom/RSS reconocible')
            for row in rows:
                seen.setdefault(row['url'], row)
        except (HTTPError, URLError, TimeoutError, ValueError, ET.ParseError,
                UnicodeError, OSError) as exc:
            errors.append(f'{label} ({url}): {type(exc).__name__}: {str(exc)[:170]}')
        if pause > 0:
            time.sleep(pause)

    # Si todo el feed falla, consultar un archivo HTML oficial y permitido.
    # No sustituye la validación de la convocatoria ni inventa fechas.
    if not seen and allow_html_fallback:
        url = BLOG + '/2026/'
        try:
            for row in parse_archive_html(fetch(url), 'OGCRI: archivo HTML 2026'):
                seen.setdefault(row['url'], row)
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            errors.append(f'Respaldo HTML OGCRI ({url}): {type(exc).__name__}: {str(exc)[:170]}')

    return {
        'captured_at': datetime.now(timezone.utc).isoformat(),
        'status': 'pendiente_revision_humana',
        'rules': 'No importar automáticamente. Verificar universidad, perfil, plazo, vigencia y requisitos individuales.',
        'items': sorted(seen.values(), key=lambda item: (item['published_at'] or '', item['title']), reverse=True),
        'errors': errors,
    }


def main():
    parser = argparse.ArgumentParser(description='Encontrar anuncios OGCRI pendientes de revisión')
    parser.add_argument('--out', default=str(ROOT / 'data/discovered.pending.json'))
    parser.add_argument('--historical-pages', type=int, choices=(0, 1, 2, 3), default=2,
                        help='Páginas adicionales del archivo OGCRI; máximo tres')
    args = parser.parse_args()
    sources = dict(SOURCES)
    for offset in range(args.historical_pages):
        start = 51 + 50 * offset
        sources[f'OGCRI: anteriores {offset + 1}'] = (
            BLOG + f'/feeds/posts/default?alt=atom&max-results=50&start-index={start}')
    document = scan(sources)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Publicaciones candidatas: {len(document["items"])}')
    print(f'Archivo para revisión: {destination}')
    if document['errors']:
        print('Avisos de fuentes (las demás fuentes pueden haber funcionado):')
        for error in document['errors']:
            print(' - ' + error)
    if not document['items']:
        print('No hubo resultados verificables. Comprueba conexión, robots.txt y acceso al blog; no se generaron convocatorias.')


if __name__ == '__main__':
    main()
