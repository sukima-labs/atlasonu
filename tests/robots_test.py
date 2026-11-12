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
os.chdir(RAIZ)
import build_mecanismos as m, fetch_tratados_texto as t
sem = m.SEM[0]; ant = {(sem[1], sem[4]): {'estado': 'VERIFICADO', 'simbolo': 'X', 'miembros': 99}}
a, b = m.sin_red(sem, ant), m.sin_red(m.SEM[1], {})
ok('build_mecanismos sin red: copia la verificación anterior, los datos curados salen de SEM y lo nuevo queda sin cotejar',
   a['estado'] == 'VERIFICADO' and a['simbolo'] == 'X' and a['miembros'] == sem[8] and b['estado'] == 'NO_VERIFICADO' and b['motivo'] == 'SIN_CONSULTAR')
try: t.pdf_texto('A/RES/1'); nored = False
except RuntimeError as e: nored = 'T56' in str(e)
ok('fetch_tratados_texto no consulta documents.un.org/api', nored)
import re, glob
URL = re.compile(r'digitallibrary\.un\.org/(search|rss|record/[^/\s]+/export)')
cuatro = ['fetch_docs_pais', 'fetch_epu_informes', 'fetch_jurisprudencia', 'fetch_documentos_marco', 'biblioteca']
ok('T56: los scripts de datos por registro no tocan /search, /rss ni /export',
   not [n for n in cuatro if URL.search(open('scripts/%s.py' % n, encoding='utf-8').read())])
import biblioteca as B, urllib.request
pedidas = []
class R:
    def __init__(s, u): pedidas.append(u)
    def __enter__(s): return s
    def __exit__(s, *a): pass
    def read(s): return b'<collection><record></record></collection>'
orig, B.CADA = urllib.request.urlopen, 0
urllib.request.urlopen = lambda req, timeout=0: R(req.full_url)
try: B.marc('571575'); malo = False
finally: urllib.request.urlopen = orig
try: B.marc('1 OR x'); malo = True
except ValueError: pass
ok('biblioteca.marc solo pide /record/N?of=xm y rechaza lo que no es un número', pedidas == ['https://digitallibrary.un.org/record/571575?of=xm'] and not malo)
sys.exit(1 if fallos else 0)
