#!/usr/bin/env python3
"""T56: la revisión diaria (scripts/actualizar_datos.sh, dos veces al día en GitHub Actions) no consulta lo que prohíben
los robots.txt: digitallibrary.un.org/search, documents.un.org/api y ap.ohchr.org. Sin BIBLIOTECA_SEARCH=si, la
verificación de símbolos y la localización de textos trabajan sin red sobre su resultado anterior."""
import os, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
os.environ.pop('BIBLIOTECA_SEARCH', None)
import verify_symbols as v, resolve_texts as r

fallos = 0
def ok(n, c):
    global fallos
    print(('✓ ' if c else '✗ ') + n); fallos += not c

try: v.query('191__a', 'A/HRC/RES/1/1'); q = False
except v.SinConsulta: q = True
ok('verify_symbols: sin BIBLIOTECA_SEARCH=si no busca en /search (SinConsulta)', not v.BUSCAR and q)
ok('resolve_texts: no consulta documents.un.org/api ni ap.ohchr.org', r.ods('A/HRC/RES/1/1', 'es') is None and r.ohchr('A/HRC/RES/1/1') is None)
e = {'pdf': {'en': 'https://digitallibrary.un.org/record/1/files/x-EN.pdf'}, 'padres': ['A/1']}
ant = {'fuentes': [{'tipo': 'ods', 'lengua': 'es', 'url': 'u', 'validado': True}], 'informe_sesion': [{'simbolo': 'A/1'}, {'simbolo': 'A/2'}]}
s = r.sin_red('X', e, ant)
ok('resolve_texts sin red: el registro, más lo localizado antes que siga valiendo', s['estado'] == 'TEXTO_DIRECTO' and [f['tipo'] for f in s['fuentes']] == ['registro', 'ods'] and s['informe_sesion'] == [{'simbolo': 'A/1'}])
ok('resolve_texts sin red: un acto nuevo sin copia en su registro queda SIN_COPIA_LOCALIZADA', r.sin_red('Y', {'pdf': {}}, {})['estado'] == 'SIN_COPIA_LOCALIZADA')
sys.exit(1 if fallos else 0)
