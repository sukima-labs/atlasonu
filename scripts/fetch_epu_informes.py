#!/usr/bin/env python3
"""T68 (c) · Lista de los informes del Grupo de Trabajo del Examen Periódico Universal (A/HRC/<sesión>/<n>) y de sus
adiciones (A/HRC/<sesión>/<n>/Add.1, la respuesta del Estado), por país, desde la Biblioteca Digital de la ONU.
Solo metadatos y enlaces; los PDF los baja `texto_completo.py`. Respeta el Crawl-Delay de 5 s y va de uno en uno.
T56: la Biblioteca Digital prohíbe /search, así que no se busca: se conservan los informes ya anotados y se bajan los
registros nuevos de data/fuentes/registros_biblioteca.json (/record/N). Con --refrescar se bajan otra vez todos (~2 h).
Salida: data/fuentes/epu_informes.json  {iso3: [{ciclo?, s, d, r, en, es, add:{s,d,r,en,es}}]}
Uso: fetch_epu_informes.py [--refrescar]"""
import re, sys, json, time
sys.path.insert(0, __import__('os').path.dirname(__file__))
import fetch_docs_pais as F
import biblioteca as B
def nombre_pais(t):
    m = re.fullmatch(r'Report of the Working Group on the Universal Periodic Review\s*:\s*(.+)', t.strip())
    if not m: return None
    n = re.split(r'\s*:\s*', m[1])[0]                        # «Vanuatu: addendum», «Saudi Arabia : [addendum]»
    n = re.sub(r'\s+UN,?$', '', n.strip())                     # «Algeria UN,»
    return re.sub(r'^the\s+', '', n, flags=re.I)              # «the Philippines»
def norm(x): return re.sub(r'[^a-z]+', ' ', x.lower().replace('&', 'and')).strip()
ALIAS = {'Federated States of Micronesia': 'FSM', 'Islamic Republic of Iran': 'IRN', 'Plurinational State of Bolivia': 'BOL', 'Kingdom of Saudi Arabia': 'SAU',
         'Kingdom of the Netherlands': 'NLD', 'Bolivarian Republic of Venezuela': 'VEN', 'State of Qatar': 'QAT',
         'Libyan Arab Jamahiriya': 'LBY', 'China (including Hong Kong, China and Macao, China)': 'CHN', 'Republic of the Marshall Islands': 'MHL', 'former Yugoslav Republic of Macedonia': 'MKD'}
def mapa_nombres():
    OH = {p['iso3']: p for p in json.load(open('data/fuentes/paises_ohchr.json', encoding='utf-8'))['paises'] if p['iso3'] != 'OTH'}
    d = {}
    for iso, p in OH.items():
        for n in [p['en']] + F.NOMBRES.get(iso, []) + [c.title() for c in F.UNBIS.get(iso, [])]:
            d.setdefault(norm(n), iso)
    for n, iso in ALIAS.items(): d.setdefault(norm(n), iso)
    return d, OH
CAMPOS = ('s', 't', 'd', 'r', 'en', 'es')
def main():
    try: antes = json.load(open('data/fuentes/epu_informes.json', encoding='utf-8'))
    except FileNotFoundError: antes = {'paises': {}}
    todos = {}
    for l in antes['paises'].values():
        for f in l:
            for x in [f] + ([f['add']] if 'add' in f else []): todos[x['r']] = {k: x[k] for k in CAMPOS if k in x}
    pedir = (list(todos) if '--refrescar' in sys.argv else []) + [n for n in B.nuevos('fetch_epu_informes') if n not in todos]
    for n in dict.fromkeys(pedir):
        for x in F.registros(B.marc(n)): todos[x['r']] = x
        print('registro', n, flush=True)
    todos = list(todos.values())
    por_nombre, OH = mapa_nombres()
    out, sin = {}, {}
    for x in todos:
        m = re.fullmatch(r'A/HRC/(\d+)/(\d+)(?:/Add\.(\d+))?', x['s'])
        n = nombre_pais(x['t'])
        if not m or not n: continue
        iso = por_nombre.get(norm(n))
        if not iso:
            sin[n] = sin.get(n, 0) + 1; continue
        ficha = {k: x[k] for k in ('s', 't', 'd', 'r', 'en', 'es') if k in x}
        ficha['ses'] = int(m[1])
        lista = out.setdefault(iso, [])
        if m[3]:
            lista.append({'_add': ficha, '_base': f'A/HRC/{m[1]}/{m[2]}'})
        else:
            lista.append(ficha)
    res = {}
    for iso, l in out.items():
        base = {f['s']: f for f in l if '_add' not in f}
        for f in l:
            if '_add' in f and f['_base'] in base: base[f['_base']]['add'] = f['_add']
        res[iso] = sorted(base.values(), key=lambda f: f['d'])
    json.dump({'fuente': 'https://digitallibrary.un.org/', 'obtenido': time.strftime('%Y-%m-%d') if pedir else antes.get('obtenido', ''), 'paises': res}, open('data/fuentes/epu_informes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print(len(todos), 'registros;', len(res), 'países;', sum(len(v) for v in res.values()), 'informes;', sum(1 for v in res.values() for f in v if 'add' in f), 'con adición')
    if sin: print('SIN PAÍS:', json.dumps(sin, ensure_ascii=False))
if __name__ == '__main__': main()
