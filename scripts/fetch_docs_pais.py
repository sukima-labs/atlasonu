#!/usr/bin/env python3
"""Documentos oficiales POR PAÍS desde la Biblioteca Digital de la ONU, sin descargar los documentos (solo metadatos y enlaces):
 - Observaciones finales de los 9 comités de tratados (símbolo con código ISO: CCPR/C/IND/CO/4, E/C.12/IND/CO/5…)
 - Examen Periódico Universal (A/HRC/WG.6/<sesión>/<ISO>/<n>)
 - Informes de misiones/visitas de procedimientos especiales (búsqueda por título, filtrada)
Salida: data/paises/<ISO>.js (carga bajo demanda) y data/fuentes/docs_paises.json (resumen). Uso: fetch_docs_pais.py [ISO ...]"""
import re, sys, json, time, urllib.parse, urllib.request, concurrent.futures as cf
UA = {'User-Agent': 'ATLAS-ONU/1.0 (academic)'}
DL = 'https://digitallibrary.un.org/search?ln=en&of=xm&rg=100&p='
CO_BODIES = [('CERD', 'CERD/C/{i}/CO/'), ('CCPR', 'CCPR/C/{i}/CO/'), ('CESCR', 'E/C.12/{i}/CO/'), ('CEDAW', 'CEDAW/C/{i}/CO/'), ('CAT', 'CAT/C/{i}/CO/'),
             ('CRC', 'CRC/C/{i}/CO/'), ('CMW', 'CMW/C/{i}/CO/'), ('CRPD', 'CRPD/C/{i}/CO/'), ('CED', 'CED/C/{i}/CO/')]
UNBIS = {'IRN': ['IRAN (ISLAMIC REPUBLIC OF)', 'IRAN'], 'GBR': ['UNITED KINGDOM'], 'USA': ['UNITED STATES'], 'RUS': ['RUSSIAN FEDERATION'], 'KOR': ['REPUBLIC OF KOREA'], 'PRK': ["DEMOCRATIC PEOPLE'S REPUBLIC OF KOREA"],
         'COD': ['DEMOCRATIC REPUBLIC OF THE CONGO'], 'TZA': ['UNITED REPUBLIC OF TANZANIA'], 'VEN': ['VENEZUELA', 'VENEZUELA (BOLIVARIAN REPUBLIC OF)'], 'BOL': ['BOLIVIA', 'BOLIVIA (PLURINATIONAL STATE OF)'], 'PSE': ['PALESTINE', 'OCCUPIED PALESTINIAN TERRITORY'],
         'SYR': ['SYRIAN ARAB REPUBLIC'], 'MDA': ['REPUBLIC OF MOLDOVA', 'MOLDOVA'], 'LAO': ["LAO PEOPLE'S DEMOCRATIC REPUBLIC"], 'TUR': ['TURKEY', 'TURKIYE'], 'CZE': ['CZECHIA', 'CZECH REPUBLIC'], 'NLD': ['NETHERLANDS'],
         'FSM': ['MICRONESIA (FEDERATED STATES OF)'], 'MKD': ['NORTH MACEDONIA', 'THE FORMER YUGOSLAV REPUBLIC OF MACEDONIA'], 'SWZ': ['ESWATINI', 'SWAZILAND'], 'CPV': ['CABO VERDE', 'CAPE VERDE'], 'CIV': ["COTE D'IVOIRE"],
         'VNM': ['VIET NAM'], 'BRN': ['BRUNEI DARUSSALAM'], 'COG': ['CONGO'], 'KNA': ['SAINT KITTS AND NEVIS'], 'LCA': ['SAINT LUCIA'], 'VCT': ['SAINT VINCENT AND THE GRENADINES'], 'GMB': ['GAMBIA'], 'BHS': ['BAHAMAS']}
NOMBRES = {'IRN': ['Iran'], 'GBR': ['United Kingdom'], 'USA': ['United States'], 'RUS': ['Russian Federation'], 'KOR': ['Republic of Korea'], 'PRK': ["Democratic People's Republic of Korea"],
           'COD': ['Democratic Republic of the Congo'], 'TZA': ['United Republic of Tanzania', 'Tanzania'], 'VEN': ['Venezuela'], 'BOL': ['Bolivia'], 'PSE': ['Palestine', 'Occupied Palestinian'],
           'SYR': ['Syrian Arab Republic'], 'MDA': ['Republic of Moldova', 'Moldova'], 'LAO': ["Lao People's Democratic Republic"], 'TUR': ['Türkiye', 'Turkey'], 'CZE': ['Czechia', 'Czech Republic'],
           'NLD': ['Netherlands'], 'FSM': ['Micronesia'], 'MKD': ['North Macedonia'], 'SWZ': ['Eswatini', 'Swaziland'], 'CPV': ['Cabo Verde', 'Cape Verde'], 'CIV': ["Côte d'Ivoire", "Cote d'Ivoire"],
           'BHS': ['Bahamas'], 'GMB': ['Gambia'], 'VNM': ['Viet Nam', 'Vietnam'], 'BRN': ['Brunei Darussalam'], 'TLS': ['Timor-Leste'], 'COG': ['Congo'], 'KNA': ['Saint Kitts and Nevis'], 'LCA': ['Saint Lucia'], 'VCT': ['Saint Vincent and the Grenadines']}
def consulta(p, tries=3):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(DL + urllib.parse.quote(p), headers=UA), timeout=60).read().decode('utf-8', 'ignore')
        except Exception as e:
            err = e; time.sleep(1.5 * (k + 1))
    raise RuntimeError(f'red: {err}')
def registros(xml):
    out = []
    for r in re.findall(r'<record>(.*?)</record>', xml, re.S):
        f = lambda tag, c: [re.sub(r'\s+', ' ', x).strip() for x in re.findall(r'<datafield tag="' + tag + r'"[^>]*>.*?<subfield code="' + c + r'">(.*?)</subfield>', r, re.S)]
        sims = f('191', 'a'); rid = re.search(r'<controlfield tag="001">(\d+)', r)
        pdf = {}
        # Cada campo 856 por separado: con un único patrón, un 856 sin «y» emparejaba la lengua del siguiente con su URL
        # y salían como «inglés» PDF en francés o chino. Además, el nombre del fichero tiene que ser de esa lengua.
        for campo in re.findall(r'<datafield tag="856"[^>]*>(.*?)</datafield>', r, re.S):
            y = re.search(r'<subfield code="y">(.*?)</subfield>', campo); u = re.search(r'<subfield code="u">(.*?)</subfield>', campo)
            ln = {'English': 'en', 'Español': 'es'}.get(y.group(1) if y else '')
            if ln and u and re.search(r'-' + ln.upper() + r'\.pdf$', u.group(1), re.I): pdf[ln] = u.group(1)
        out.append({'s': sims[0] if sims else '', 'ss': sims, 'sub': [x.upper() for x in f('650', 'a')], 't': ' '.join(f('245', 'a')[:1] + f('245', 'b')[:1]).strip(' /:'), 'd': (f('269', 'a') or [''])[0],
                    'r': rid.group(1) if rid else '', **({'es': pdf['es']} if 'es' in pdf else {}), **({'en': pdf['en']} if 'en' in pdf else {})})
    return out
def doc_pais(iso, en):
    co, epu, vis = [], [], []
    q = ' OR '.join(f'191__a:"{pre.format(i=iso)}*"' for _, pre in CO_BODIES)
    for x in registros(consulta(q)):
        for cuerpo, pre in CO_BODIES:
            if re.fullmatch(re.escape(pre.format(i=iso)) + r'[\d-]+', x['s']):
                co.append({'c': cuerpo, **{k: x[k] for k in ('s', 't', 'd', 'r', 'es', 'en') if k in x}}); break
    for x in registros(consulta(f'191__a:"A/HRC/WG.6/*/{iso}/*"')):
        m = re.fullmatch(r'A/HRC/WG\.6/(\d+)/' + iso + r'/(\d)(?:/Corr\.\d+)?', x['s'])
        if m: epu.append({'ses': int(m[1]), 'n': int(m[2]), **{k: x[k] for k in ('s', 't', 'd', 'r', 'es', 'en') if k in x}})
    cands = UNBIS.get(iso) or [re.sub(r'\s*\(.*?\)', '', en).replace('the ', '').strip().upper(), en.upper()]
    q = '(' + ' OR '.join(f'subject:"{c}"' for c in dict.fromkeys(cands)) + ') AND subject:"FACT-FINDING MISSIONS"'
    seen = set()
    for x in registros(consulta(q)):
        if not re.fullmatch(r'(A/HRC/\d+/\d+/Add\.\d+|E/CN\.4/\d{4}/[\w.\-]+/Add\.\d+|A/\d+/\d+/Add\.\d+)', x['s']) or x['s'] in seen: continue
        if not any(c.upper() in x['sub'] for c in cands): continue   # materia EXACTA: «GUINEA» no debe traer «GUINEA-BISSAU» ni «EQUATORIAL GUINEA»
        seen.add(x['s']); vis.append({k: x[k] for k in ('s', 't', 'd', 'r', 'es', 'en') if k in x})
    key = lambda d: (d.get('d', ''), d['s'])
    co.sort(key=key, reverse=True); epu.sort(key=lambda d: (-d['ses'], d['n'], d['s'])); vis.sort(key=key, reverse=True)
    return {'co': co, 'epu': epu, 'visitas': vis}
def main(isos):
    OH = {p['iso3']: p for p in json.load(open('data/fuentes/paises_ohchr.json', encoding='utf-8'))['paises'] if p['iso3'] not in ('OTH',)}
    isos = isos or sorted(OH)
    def uno(i):
        return i, doc_pais(i, OH[i]['en'])
    res = {}
    with cf.ThreadPoolExecutor(4) as ex:
        for i, d in ex.map(uno, isos): res[i] = d
    resumen = {}
    for i, d in sorted(res.items()):
        open(f'data/paises/{i}.js', 'w', encoding='utf-8').write(f"window.PAIS_DOCS=window.PAIS_DOCS||{{}};window.PAIS_DOCS['{i}']=" + json.dumps(d, ensure_ascii=False, separators=(',', ':'), sort_keys=True) + ';\n')
        resumen[i] = {'co': len(d['co']), 'epu': len(d['epu']), 'visitas': len(d['visitas']), 'ultima_co': ({'s': d['co'][0]['s'], 'd': d['co'][0]['d']} if d['co'] else None)}
    if len(sys.argv) <= 1:
        json.dump({'fuente': 'https://digitallibrary.un.org/', 'paises': resumen}, open('data/fuentes/docs_paises.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print(len(res), 'países;', sum(v['co'] for v in resumen.values()), 'observaciones finales;', sum(v['epu'] for v in resumen.values()), 'documentos EPU;', sum(v['visitas'] for v in resumen.values()), 'informes de visitas')
if __name__ == '__main__': main(sys.argv[1:])
