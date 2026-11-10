#!/usr/bin/env python3
"""Genera data/conflictos.js (capa «Conflictos armados» del mapa, T68) a partir del UCDP/PRIO Armed Conflict Dataset.

Fuente: Uppsala Conflict Data Program (UCDP), https://ucdp.uu.se/downloads/ — licencia CC BY 4.0, sin cuenta, robots.txt permite el acceso.
Cita: Davies, Pettersson y Öberg (UCDP/PRIO Armed Conflict Dataset); Gleditsch et al. (2002), Journal of Peace Research 39(5).
Se descarga una vez (45 KB) y se agrega por país y año. UCDP publica una versión al año: no hace falta repetirlo a diario.

Uso: python3 -I scripts/fetch_ucdp.py [--version 261] [--origen fichero.zip]
Con --origen se usa un zip ya descargado (no toca la red)."""
import argparse, csv, io, json, re, sys, urllib.request, zipfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# Nombres de UCDP que no coinciden con el nombre en inglés de ATLAS. Los territorios o Estados históricos sin ficha
# (Hyderabad, Vietnam del Sur, Yemen del Sur, Taiwán) no se dibujan: se cuentan aparte.
NOMBRES = {
    'Bosnia-Herzegovina': 'BIH', 'Brunei': 'BRN', 'Cambodia (Kampuchea)': 'KHM', 'Congo': 'COG', 'DR Congo (Zaire)': 'COD',
    'Iran': 'IRN', 'Ivory Coast': 'CIV', 'Laos': 'LAO', 'Madagascar (Malagasy)': 'MDG', 'Moldova': 'MDA',
    'Myanmar (Burma)': 'MMR', 'North Korea': 'PRK', 'Russia (Soviet Union)': 'RUS', 'Serbia (Yugoslavia)': 'SRB',
    'South Korea': 'KOR', 'Syria': 'SYR', 'Tanzania': 'TZA', 'Turkey': 'TUR', 'United Kingdom': 'GBR',
    'Venezuela': 'VEN', 'Vietnam (North Vietnam)': 'VNM', 'Yemen (North Yemen)': 'YEM', 'Zimbabwe (Rhodesia)': 'ZWE',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', default='261', help='versión de UCDP sin punto (261 = 26.1)')
    ap.add_argument('--origen', help='zip ya descargado')
    a = ap.parse_args()
    if a.origen:
        datos = Path(a.origen).read_bytes()
    else:
        url = f'https://ucdp.uu.se/downloads/ucdpprio/ucdp-prio-acd-{a.version}-csv.zip'
        req = urllib.request.Request(url, headers={'User-Agent': 'atlas-onu (sukima-labs; datos abiertos)'})
        datos = urllib.request.urlopen(req, timeout=60).read()
    z = zipfile.ZipFile(io.BytesIO(datos))
    nombre = next(n for n in z.namelist() if n.endswith('.csv'))
    filas = list(csv.DictReader(io.TextIOWrapper(z.open(nombre), encoding='utf-8')))
    cat = json.loads((RAIZ / 'data' / 'catalogo.json').read_text(encoding='utf-8'))
    por_nombre = {p['en']: p['id'] for p in cat['paises']}
    por_nombre.update(NOMBRES)
    acum, sin_ficha = {}, set()
    for f in filas:
        for loc in f['location'].split(', '):
            pid = por_nombre.get(loc)
            if not pid:
                sin_ficha.add(loc)
                continue
            e = acum.setdefault(pid, {}).setdefault(int(f['year']), {'ids': set(), 'max': 0})
            e['ids'].add(f['conflict_id'])
            e['max'] = max(e['max'], int(f['intensity_level']))
    anios = sorted({int(f['year']) for f in filas})
    version = filas[0]['version']
    # El caso de prueba que no puede fallar: ningún nombre «con ficha» se pierde por un error de tabla
    esperados = {'Afghanistan', 'Ukraine', 'Colombia', 'Myanmar (Burma)', 'Russia (Soviet Union)'}
    perdidos = esperados & sin_ficha
    if perdidos:
        sys.exit(f'ERROR: nombres de UCDP sin emparejar que deberían tenerlo: {sorted(perdidos)}')
    sal = {'v': version, 'c': date.today().isoformat(), 'a': [anios[0], anios[-1]],
           'p': {pid: [[y, len(e['ids']), e['max']] for y, e in sorted(porano.items())] for pid, porano in sorted(acum.items())}}
    (RAIZ / 'data' / 'conflictos.js').write_text(
        'window.CONFLICTOS=' + json.dumps(sal, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    print(f'UCDP/PRIO ACD v{version}: {len(filas)} filas, años {anios[0]}-{anios[-1]}, {len(acum)} países con ficha;'
          f' sin ficha: {sorted(sin_ficha)}')


if __name__ == '__main__':
    main()
