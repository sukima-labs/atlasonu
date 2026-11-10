#!/usr/bin/env python3
"""T68 (c) · Lista de los informes del Grupo de Trabajo del Examen Periódico Universal (A/HRC/<sesión>/<n>) y de sus
adiciones (A/HRC/<sesión>/<n>/Add.1, la respuesta del Estado), por país, desde la Biblioteca Digital de la ONU.
Solo metadatos y enlaces; los PDF los baja `texto_completo.py`. Respeta el Crawl-Delay de 5 s y va de uno en uno.
Salida: data/fuentes/epu_informes.json  {iso3: [{ciclo?, s, d, r, en, es, add:{s,d,r,en,es}}]}
Uso: fetch_epu_informes.py"""
import re, sys, json, time, urllib.parse, urllib.request
sys.path.insert(0, __import__('os').path.dirname(__file__))
import fetch_docs_pais as F
CADA = 5.0
Q = 'title:"Report of the Working Group on the Universal Periodic Review"'
def pagina(jrec, anio, tries=3):
    url = 'https://digitallibrary.un.org/search?ln=en&of=xm&rg=100&jrec=%d&p=%s' % (jrec, urllib.parse.quote(f'{Q} AND year:{anio}'))
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=F.UA), timeout=60).read().decode('utf-8', 'ignore')
        except Exception as e:
            err = e; time.sleep(5 * (k + 1))
    raise RuntimeError(f'red: {err}')
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
def main():
    todos, vistos = [], set()
    for anio in range(2008, time.gmtime().tm_year + 1):   # una búsqueda por año: la Biblioteca Digital corta cada búsqueda en ~600 resultados
        jrec = 1
        while jrec < 1000:
            regs = [x for x in F.registros(pagina(jrec, anio)) if x['r'] not in vistos]   # sin repetidos: si se pasa del final devuelve la última página otra vez
            print(anio, 'jrec', jrec, 'nuevos', len(regs), flush=True)
            time.sleep(CADA)
            if not regs: break
            vistos.update(x['r'] for x in regs); todos += regs; jrec += 100
            if len(regs) < 100: break
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
    json.dump({'fuente': 'https://digitallibrary.un.org/', 'obtenido': time.strftime('%Y-%m-%d'), 'paises': res}, open('data/fuentes/epu_informes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print(len(todos), 'registros;', len(res), 'países;', sum(len(v) for v in res.values()), 'informes;', sum(1 for v in res.values() for f in v if 'add' in f), 'con adición')
    if sin: print('SIN PAÍS:', json.dumps(sin, ensure_ascii=False))
if __name__ == '__main__': main()
