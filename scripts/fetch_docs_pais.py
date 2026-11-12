#!/usr/bin/env python3
"""Documentos oficiales POR PAÍS desde la Biblioteca Digital de la ONU, sin descargar los documentos (solo metadatos y enlaces):
 - Observaciones finales de los 9 comités de tratados (símbolo con código ISO: CCPR/C/IND/CO/4, E/C.12/IND/CO/5…)
 - Examen Periódico Universal (A/HRC/WG.6/<sesión>/<ISO>/<n>)
 - Informes de misiones/visitas de procedimientos especiales (búsqueda por título, filtrada)
T56: la Biblioteca Digital prohíbe /search, así que no se busca: se conservan los documentos ya anotados en cada ficha y
se bajan los registros nuevos de data/fuentes/registros_biblioteca.json (/record/N, 5 s), que se clasifican por país con
las mismas reglas de siempre. Con --refrescar se bajan otra vez todos los conocidos (~6.700 registros, ~9 h).
Salida: data/paises/<ISO>.js (carga bajo demanda) y data/fuentes/docs_paises.json (resumen). Uso: fetch_docs_pais.py [--refrescar] [ISO ...]"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import biblioteca as B
UA = B.UA
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
CAMPOS = ('s', 't', 'd', 'r', 'es', 'en')
def candidatos(iso, en):
    return UNBIS.get(iso) or [re.sub(r'\s*\(.*?\)', '', en).replace('the ', '').strip().upper(), en.upper()]
def clasifica(x, iso, en):
    """(«co»|«epu»|«visitas», ficha) si el registro `x` (de registros()) es de `iso`; si no, None."""
    campos = {k: x[k] for k in CAMPOS if k in x}
    for cuerpo, pre in CO_BODIES:
        if re.fullmatch(re.escape(pre.format(i=iso)) + r'[\d-]+', x['s']): return 'co', {'c': cuerpo, **campos}
    m = re.fullmatch(r'A/HRC/WG\.6/(\d+)/' + iso + r'/(\d)(?:/Corr\.\d+)?', x['s'])
    if m: return 'epu', {'ses': int(m[1]), 'n': int(m[2]), **campos}
    cands = candidatos(iso, en)
    if 'FACT-FINDING MISSIONS' in x['sub'] and re.fullmatch(r'(A/HRC/\d+/\d+/Add\.\d+|E/CN\.4/\d{4}/[\w.\-]+/Add\.\d+|A/\d+/\d+/Add\.\d+)', x['s']) \
            and any(c.upper() in x['sub'] for c in cands):   # materia EXACTA: «GUINEA» no debe traer «GUINEA-BISSAU» ni «EQUATORIAL GUINEA»
        return 'visitas', campos
    return None
def leer(iso):
    try: t = open(f'data/paises/{iso}.js', encoding='utf-8').read()
    except FileNotFoundError: return {'co': [], 'epu': [], 'visitas': []}
    return json.loads(t[t.index('=', t.index("['" + iso + "']")) + 1:t.rindex(';')])
def doc_pais(iso, en, antes, regs):
    """Ficha de `iso`: lo anotado en `antes`, con los registros bajados (`regs`, r -> registro) puestos al día o añadidos."""
    d = {k: list(antes.get(k, [])) for k in ('co', 'epu', 'visitas')}
    conocidos = {f['r'] for v in d.values() for f in v}
    for k, lista in d.items():
        for j, f in enumerate(lista):
            c = clasifica(regs[f['r']], iso, en) if f['r'] in regs else None
            if c and c[0] == k: lista[j] = c[1]
    for r, x in regs.items():
        c = None if r in conocidos else clasifica(x, iso, en)
        if c and all(f['s'] != c[1]['s'] for f in d[c[0]]): d[c[0]].append(c[1])
    key = lambda f: (f.get('d', ''), f['s'])
    d['co'].sort(key=key, reverse=True); d['epu'].sort(key=lambda f: (-f['ses'], f['n'], f['s'])); d['visitas'].sort(key=key, reverse=True)
    return d
def main(args):
    OH = {p['iso3']: p for p in json.load(open('data/fuentes/paises_ohchr.json', encoding='utf-8'))['paises'] if p['iso3'] not in ('OTH',)}
    isos = [a for a in args if not a.startswith('--')] or sorted(OH)
    antes = {i: leer(i) for i in isos}
    conocidos = list(dict.fromkeys(f['r'] for a in antes.values() for v in a.values() for f in v))
    pedir = (conocidos if '--refrescar' in args else []) + [n for n in B.nuevos('fetch_docs_pais') if n not in conocidos]
    regs = {}
    for n in dict.fromkeys(pedir):
        for x in registros(B.marc(n)): regs[x['r']] = x
        print('registro', n, flush=True)
    res = {i: doc_pais(i, OH[i]['en'], antes[i], regs) for i in isos}
    resumen = {}
    for i, d in sorted(res.items()):
        open(f'data/paises/{i}.js', 'w', encoding='utf-8').write(f"window.PAIS_DOCS=window.PAIS_DOCS||{{}};window.PAIS_DOCS['{i}']=" + json.dumps(d, ensure_ascii=False, separators=(',', ':'), sort_keys=True) + ';\n')
        resumen[i] = {'co': len(d['co']), 'epu': len(d['epu']), 'visitas': len(d['visitas']), 'ultima_co': ({'s': d['co'][0]['s'], 'd': d['co'][0]['d']} if d['co'] else None)}
    if not [a for a in args if not a.startswith('--')]:
        json.dump({'fuente': 'https://digitallibrary.un.org/', 'paises': resumen}, open('data/fuentes/docs_paises.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print(len(res), 'países;', sum(v['co'] for v in resumen.values()), 'observaciones finales;', sum(v['epu'] for v in resumen.values()), 'documentos EPU;', sum(v['visitas'] for v in resumen.values()), 'informes de visitas')
if __name__ == '__main__': main(sys.argv[1:])
