#!/usr/bin/env python3
"""Genera data/paises_es.json (ISO3 → nombre en español) UNA vez, con la base ISO (pycountry) y el diccionario ICU de Node.
Requiere: pip install pycountry; node. Los nombres ya generados se guardan en el repositorio; la actualización diaria no lo necesita."""
import json, subprocess, sys
import pycountry
iso3 = json.load(open('data/fuentes/paises_ohchr_codigos.json', encoding='utf-8'))
a2 = {}
for c in iso3:
    p = pycountry.countries.get(alpha_3=c)
    a2[c] = p.alpha_2 if p else None
js = "const L=JSON.parse(require('fs').readFileSync(0,'utf8'));const d=new Intl.DisplayNames(['es'],{type:'region'});const o={};for(const [k,v] of Object.entries(L)){try{o[k]=v?d.of(v):null}catch(e){o[k]=null}}console.log(JSON.stringify(o))"
es = json.loads(subprocess.run(['node', '-e', js], input=json.dumps(a2), capture_output=True, text=True).stdout)
json.dump({k: v for k, v in es.items() if v}, open('data/paises_es.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print(len(es), "códigos;", sum(1 for v in es.values() if v), "con nombre ISO; faltan:", [k for k, v in es.items() if not v], "(se completan a mano en data/paises_es.json: CRO, RKS, OTH)")
