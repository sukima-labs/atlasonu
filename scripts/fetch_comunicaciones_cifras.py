#!/usr/bin/env python3
"""Cifras de comunicaciones de los procedimientos especiales POR PAÍS, de los informes conjuntos (A/HRC/NN/NN) de la Biblioteca Digital.
Solo rutas permitidas por robots.txt (/record/<id>/files/…), 5 s entre descargas. El texto de cada comunicación NO está en estos informes: solo en
spcommreports.ohchr.org, que prohíbe el acceso automatizado (no se consulta). Requiere pdftotext (poppler).
Salida: data/fuentes/comunicaciones_cifras.json. Uso: fetch_comunicaciones_cifras.py"""
import re, sys, json, time, subprocess, tempfile, os, urllib.request
UA = {'User-Agent': 'ATLAS-ONU/1.0 (proyecto academico sin fines de lucro; +https://github.com/sukima-labs/onu-arqueologia-documental)'}
ALIAS = {'türkiye': 'TUR', 'turkey': 'TUR', 'viet nam': 'VNM', 'czechia': 'CZE', "côte d'ivoire": 'CIV', "cote d'ivoire": 'CIV', 'republic of korea': 'KOR',
         'state of palestine': 'PSE', 'palestine': 'PSE', 'russian federation': 'RUS', 'united states of america': 'USA', 'iran (islamic republic of)': 'IRN',
         'united kingdom of great britain and northern ireland': 'GBR', 'venezuela (bolivarian republic of)': 'VEN', 'bolivia (plurinational state of)': 'BOL',
         'united republic of tanzania': 'TZA', 'lao people\'s democratic republic': 'LAO', 'syrian arab republic': 'SYR', 'republic of moldova': 'MDA',
         'democratic republic of the congo': 'COD', "democratic people's republic of korea": 'PRK', 'micronesia (federated states of)': 'FSM', 'netherlands (kingdom of the)': 'NLD'}
for q in json.load(open('data/fuentes/paises_ohchr.json', encoding='utf-8'))['paises']:
    ALIAS.setdefault(q['en'].lower(), q['iso3'])
ALIAS.update({'bolivia': 'BOL', 'bolivia (plurinational state of)': 'BOL', 'cabo verde': 'CPV', 'bosnia and herzegovina': 'BIH', 'north macedonia': 'MKD', 'eswatini': 'SWZ', 'timor-leste': 'TLS', 'congo': 'COG', 'republic of the congo': 'COG'})
FILA = re.compile(r'^\s*(\S.*?)\s{2,}(\d+)\s{2,}(\d+)\s{2,}(\d+)\s{2,}(\d+)\s*$')
def norm(n): return re.sub(r'\s+', ' ', n).strip().lower()
def analizar(txt):
    filas, ult = [], None
    for l in txt.split('\n'):
        m = FILA.match(l)
        if m:
            ult = [m.group(1).strip(), *map(int, m.groups()[1:])]; filas.append(ult)
        elif ult is not None and l.strip() and not re.search(r'\d{2}|A/HRC|\*|Number|Name of|period', l) and len(l.strip()) < 40 and l.startswith(' '):
            ult[0] += ' ' + l.strip()
        else:
            ult = None
    return filas
def main():
    inf = json.load(open('data/fuentes/comunicaciones_informes.json', encoding='utf-8'))['informes']
    res, ok = [], 0
    for i in inf:
        try:
            time.sleep(5)
            req = urllib.request.Request(i['pdf'], headers=UA)
            data = urllib.request.urlopen(req, timeout=120).read()
        except Exception as e:
            print('ERROR descarga', i['simbolo'], e, file=sys.stderr); continue
        with tempfile.TemporaryDirectory() as t:
            open(os.path.join(t, 'a.pdf'), 'wb').write(data)
            txt = subprocess.run(['pdftotext', '-layout', os.path.join(t, 'a.pdf'), '-'], capture_output=True, text=True).stdout
        periodo = re.search(r'Communications sent[^\n]*\n?[^\n]*?(\d+ \w+ (?:to|and) \d+ \w+ \d{4})', txt)
        paisesf, sin = {}, []
        for n, a, b, c, d in analizar(txt):
            k = norm(re.sub(r'(?<=[a-z\)])\d+$', '', n.strip()))
            iso = ALIAS.get(k)
            if not iso and len(k) > 4:  # nombre partido en varias líneas: prefijo único
                cand = {v for al, v in ALIAS.items() if al.startswith(k)}
                iso = cand.pop() if len(cand) == 1 else None
            if iso: paisesf[iso] = {'enviadas': a, 'con_respuesta': b, 'respuestas_de_fondo': c, 'acuses': d}
            else: sin.append(n)
        print(i['simbolo'], 'países', len(paisesf), 'sin ISO', sin[:6])
        tot = re.search(r'sent during this reporting period to (\d+)\s+countries', re.sub(r'\s+', ' ', txt))
        if tot and abs(len(paisesf) - int(tot.group(1))) > 3:
            print('  DESCARTADO (recuento %d frente a %s declarado)' % (len(paisesf), tot.group(1)), file=sys.stderr); continue
        if tot and len(paisesf) >= 20:
            ok += 1
            res.append({'simbolo': i['simbolo'], 'registro': i['registro'], 'url': 'https://digitallibrary.un.org/record/%s' % i['registro'], 'periodo': periodo.group(1) if periodo else None, 'paises_declarados': int(tot.group(1)), 'paises': paisesf})
    if ok < 3: sys.exit('ABORTA: se analizaron muy pocos informes (%d)' % ok)
    json.dump({'fuente': 'Informes conjuntos de comunicaciones de los procedimientos especiales (Biblioteca Digital de la ONU)', 'nota': 'Solo cifras por país; el texto de cada comunicación está en spcommreports.ohchr.org (no se consulta: robots.txt).', 'informes': res}, open('data/fuentes/comunicaciones_cifras.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    inf2 = [{'s': r['simbolo'], 'p': r['periodo'], 'u': r['url']} for r in res]
    por = {}
    for k, r in enumerate(res):
        for iso, v in r['paises'].items():
            por.setdefault(iso, []).append([k, v['enviadas'], v['con_respuesta'], v['respuestas_de_fondo']])
    open('data/comunicaciones.js', 'w', encoding='utf-8').write('window.COMUNICACIONES=' + json.dumps({'informes': inf2, 'paises': por}, ensure_ascii=False, separators=(',', ':')) + ';')

main()
