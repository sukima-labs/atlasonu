#!/usr/bin/env python3
"""País por país, desde fuentes oficiales de OHCHR (sin descargar documentos):
 - invitación permanente y estado de visitas: https://spinternet.ohchr.org/ViewCountryVisits.aspx
 - grupo regional: data/fuentes/regiones_ohchr.json (base de comunicaciones de OHCHR)
 - nombre en español: data/paises_es.json (generado una vez con scripts/generar_nombres_paises.py)
Salida: data/fuentes/paises_ohchr.json. Uso: fetch_paises.py <fecha>"""
import re, json, html, sys, urllib.request
UA = {'User-Agent': 'ATLAS-ONU/1.0 (academic)'}
def page(vt):
    u = f'https://spinternet.ohchr.org/ViewCountryVisits.aspx?visitType={vt}&Lang=en'
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read().decode('utf-8', 'ignore')
ROW = re.compile(r'alt="([A-Z]{3})"[^>]*/>.*?lblImgText1">(.*?)</span>.*?</td><td>(YES|NO)</td><td>(.*?)</td>', re.S)
def parse(t):
    out = {}
    for iso, nm, inv, dt in ROW.findall(t):
        out[iso] = {'en': html.unescape(nm).strip(), 'inv': inv == 'YES', 'fecha': html.unescape(dt).replace('&nbsp;', '').strip()}
    return out
allc = parse(page('all'))
sets = {k: set(parse(page(v))) for k, v in {'realizadas': 'completed', 'pendientes': 'pending', 'programadas': 'forthcoming', 'en_curso': 'underway', 'otras': 'other'}.items()}
reg = json.load(open('data/fuentes/regiones_ohchr.json', encoding='utf-8'))
es = json.load(open('data/paises_es.json', encoding='utf-8'))
# Países sin comunicaciones en la base de OHCHR (no figuran allí): grupo regional completado a mano según los grupos regionales de la ONU
MANUAL = {'Bolivia': 'Latin American and Caribbean Group', 'Congo (Republic of the)': 'African Group', 'Micronesia (Federated States of)': 'Asia-Pacific Group',
          'Monaco': 'Western European and Others Group', 'San Marino': 'Western European and Others Group', 'Tonga': 'Asia-Pacific Group', 'Tuvalu': 'Asia-Pacific Group', 'Vanuatu': 'Asia-Pacific Group'}
res, sin_region = [], []
for iso, c in sorted(allc.items(), key=lambda x: x[1]['en']):
    en = c['en']
    r = reg['paises'].get(en) or reg['paises'].get(en.replace('Türkiye', 'Turkey')) or None
    origen = 'oficial (base de comunicaciones de OHCHR)' if r else None
    if r is None and en in MANUAL: r, origen = MANUAL[en], 'completado a mano (grupos regionales de la ONU)'
    if r is None: sin_region.append(en)
    res.append({'iso3': iso, 'en': en, 'es': es.get(iso, en), 'region_en': r, 'region_origen': origen, 'invitacion_permanente': c['inv'], 'fecha_invitacion': c['fecha'],
                'visitas': {k: iso in v for k, v in sets.items()}})
json.dump({'fuente': 'https://spinternet.ohchr.org/ViewCountryVisits.aspx?visitType=all', 'fuente_regiones': reg['fuente'], 'consultado': sys.argv[1] if len(sys.argv) > 1 else '',
           'paises': res}, open('data/fuentes/paises_ohchr.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(res), 'países;', sum(1 for r in res if r['invitacion_permanente']), 'con invitación permanente; sin grupo regional:', sin_region)
