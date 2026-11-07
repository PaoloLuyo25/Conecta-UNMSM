"""Descubre anuncios de fuentes públicas permitidas. NO publica ni valida convocatorias.

Uso desde la raíz: python -m tools.explorar_fuentes
Mantiene robots.txt, 1 solicitud por feed, tiempo de espera y lista cerrada de hosts.
El archivo de salida es una cola de revisión humana, no el catálogo.
"""
import argparse
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
USER_AGENT='ConectaUNMSM-ConsultaFuentes/1.0 (acceso informativo, revision humana)'
MAX_BYTES=1_500_000
ALLOWED_HOSTS={
 'cooperacion-unmsm.blogspot.com','cooperacion.unmsm.edu.pe',
 'viceacademico.unmsm.edu.pe','vrip.unmsm.edu.pe',
}
SOURCES={
 'OGCRI Blog — convenios':'https://cooperacion-unmsm.blogspot.com/feeds/posts/default/-/CONVENIOS?alt=atom&max-results=20',
 'OGCRI Blog — anuncios recientes':'https://cooperacion-unmsm.blogspot.com/feeds/posts/default?alt=atom&max-results=35',
 'OGCRI — novedades':'https://cooperacion.unmsm.edu.pe/feed/',
 'VRAP — novedades':'https://viceacademico.unmsm.edu.pe/feed/',
 'VRIP — novedades':'https://vrip.unmsm.edu.pe/feed/',
}
TOPIC=re.compile(r'beca|convocator|movilidad|intercambio|convenio|posgrado|investiga|pasant|programa|taller|subvenci|cooperaci', re.I)

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
    def handle_endtag(self, tag):
        if tag in ('script','style') and self.skip: self.skip-=1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def plain(html: str, limit:int=380) -> str:
    p=PlainText();p.feed(html or '')
    return re.sub(r'\s+',' ',unescape(' '.join(p.parts))).strip()[:limit]

def safe_link(url: str) -> bool:
    u=urlparse(url)
    return u.scheme=='https' and (u.hostname or '').lower() in ALLOWED_HOSTS and not u.username and not u.password

def parse_atom(raw: bytes, source: str) -> list[dict]:
    root=ET.fromstring(raw)
    ns={'a':'http://www.w3.org/2005/Atom'}
    result=[]
    for entry in root.findall('a:entry',ns):
        title=entry.findtext('a:title',default='',namespaces=ns).strip()
        date=entry.findtext('a:published',default='',namespaces=ns)
        summary=entry.findtext('a:summary',default='',namespaces=ns) or entry.findtext('a:content',default='',namespaces=ns)
        link=next((x.attrib.get('href','') for x in entry.findall('a:link',ns) if x.attrib.get('rel')=='alternate'), '')
        if title and safe_link(link) and TOPIC.search(title+' '+plain(summary)):
            result.append({'title':title,'url':link,'published_at':date[:10] or None,
                           'excerpt':plain(summary),'source':source,'review_status':'pendiente_revision'})
    return result

def parse_rss(raw:bytes, source:str) ->list[dict]:
    root=ET.fromstring(raw)
    items=root.findall('./channel/item')
    result=[]
    for item in items:
        title=(item.findtext('title') or '').strip()
        url=(item.findtext('link') or '').strip()
        summary=item.findtext('description') or ''
        date=item.findtext('pubDate')
        if title and safe_link(url) and TOPIC.search(title+' '+plain(summary)):
            result.append({'title':title,'url':url,'published_at':date,
                           'excerpt':plain(summary),'source':source,'review_status':'pendiente_revision'})
    return result

def fetch(url: str, timeout:int=10)->bytes:
    if not safe_link(url): raise ValueError('Origen fuera de lista permitida')
    parsed=urlparse(url)
    robots=RobotFileParser(f'{parsed.scheme}://{parsed.netloc}/robots.txt')
    try: robots.read()
    except Exception as exc: raise ValueError('No se pudo comprobar robots.txt; se omite el origen') from exc
    if not robots.can_fetch(USER_AGENT,url): raise ValueError('robots.txt no permite consultar esta ruta')
    with urlopen(Request(url,headers={'User-Agent':USER_AGENT,'Accept':'application/atom+xml, application/rss+xml, application/xml'}),timeout=timeout) as r:
        if not safe_link(r.geturl()): raise ValueError('Redirección fuera de dominios permitidos')
        data=r.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise ValueError('Respuesta demasiado grande')
    return data

def scan(sources=SOURCES, pause=1.0):
    found={}; errors=[]
    for name,url in sources.items():
        try:
            raw=fetch(url)
            parsed=parse_atom(raw,name) if b'<feed' in raw[:500] or b':feed' in raw[:500] else parse_rss(raw,name)
            for row in parsed:
                found.setdefault(row['url'],row)
        except (HTTPError,URLError,TimeoutError,ValueError,ET.ParseError) as exc:
            errors.append(f'{name}: {type(exc).__name__}; no se inventaron resultados')
        time.sleep(max(0,pause))
    return {'captured_at':datetime.now(timezone.utc).isoformat(),
            'status':'pendiente_revision_humana',
            'rules':'No publicar ninguna entrada sin cotejar destinatarios, plazos, bases y disponibilidad.',
            'items':sorted(found.values(),key=lambda x:(x['published_at'] or '',x['title']),reverse=True),
            'errors':errors}

def main():
    ap=argparse.ArgumentParser(description='Descubrir publicaciones académicas; NO publica automáticamente')
    ap.add_argument('--out',default=str(ROOT/'data/discovered.pending.json'))
    opts=ap.parse_args()
    doc=scan()
    dest=Path(opts.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'Encontradas {len(doc["items"])} publicaciones candidatas; pendientes de revisión: {dest}')
    if doc['errors']:
        print('Fuentes no accesibles (sin datos inventados):')
        for error in doc['errors']:print(' - '+error)
if __name__=='__main__': main()
