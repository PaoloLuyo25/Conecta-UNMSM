"""Crea SQL de importación SOLO a partir del catálogo revisado, nunca del scraping bruto.

Ejecución: python -m tools.generar_sql_catalogo
La ejecución de SQL debe realizarla un administrador en Supabase SQL Editor.
"""
import json
from pathlib import Path
from backend.app.schemas import Service, EvidenceType
from backend.app.config import BASE_DIR

JSON_COLUMNS={'needs_tags','modality','requirements','official_steps','contact','stops','warnings'}
DATE_COLUMNS={'source_published_at','verified_at','valid_from','valid_until'}
COLUMNS=list(Service.model_fields)

def sql_value(key, value):
    if value is None: return 'NULL'
    if key in JSON_COLUMNS: return "'"+json.dumps(value,ensure_ascii=False).replace("'","''")+"'::jsonb"
    if isinstance(value,bool): return 'TRUE' if value else 'FALSE'
    if key in DATE_COLUMNS: return "DATE '"+str(value)+"'"
    return "'"+str(value).replace("'","''")+"'"

def generate(document: dict) ->str:
    records=[Service.model_validate(item) for item in document['services']]
    if not records or any(x.evidence_type==EvidenceType.TEST for x in records):
        raise ValueError('El catálogo para publicación no puede ser vacío ni contener registros ficticios.')
    if any(not x.source_url and x.evidence_type==EvidenceType.OFFICIAL_WEB for x in records):
        raise ValueError('Falta URL para un registro web')
    lines=['-- Conecta UNMSM: registros revisados. Ejecutar en SQL Editor administrador.','-- NO importar data/discovered.pending.json: contiene solo candidatos sin revisar.','BEGIN;']
    for rec in records:
        data=rec.model_dump(mode='json')
        columns=COLUMNS+['is_public']
        values=[sql_value(k,data[k]) for k in COLUMNS]+['TRUE']
        assignments=', '.join(f'{k}=EXCLUDED.{k}' for k in COLUMNS[1:]+['is_public'])
        lines.append('INSERT INTO public.services ('+', '.join(columns)+') VALUES (\n  '+',\n  '.join(values)+'\n) ON CONFLICT (id) DO UPDATE SET '+assignments+';')
    lines.append('COMMIT;')
    return '\n'.join(lines)+'\n'

def main():
    file=BASE_DIR/'data/catalog.academico.json'
    doc=json.loads(file.read_text(encoding='utf8'))
    dest=BASE_DIR/'supabase/007_catalogo_revisado.sql'
    dest.write_text(generate(doc),encoding='utf8')
    print(f'{len(doc["services"])} registros exportados a {dest}')
if __name__=='__main__': main()
