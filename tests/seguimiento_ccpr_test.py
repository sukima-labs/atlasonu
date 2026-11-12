#!/usr/bin/env python3
"""T75 fase 2a: el analizador de los informes de seguimiento del Comité de Derechos Humanos lee las notas tal como
están escritas (fragmentos copiados de CCPR/C/144/2/Add.1, CCPR/C/120/2 y CCPR/C/129/2/Add.2) y los datos generados
son coherentes con la leyenda oficial."""
import json, os, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import seguimiento_ccpr as s

REG = {'simbolo': 'X', 'fecha': '2025-07-24', 'registro': '1'}
ARM = """
              Concluding observations (133rd session): CCPR/C/ARM/CO/3, 3 November 2021
              Follow-up paragraphs:                     16, 40 and 42
              Committee’s evaluation:                   16 [B], 40 [C] [B] and 42 [B]


              Paragraph 16: Violence against women
"""
ISL = """
     Concluding observations:            CCPR/C/ISL/CO/5, 24 July 2012
     Committee’s evaluation              Additional information required on paragraphs 7 [B2]
     (see CCPR/C/116/2):                 and 15 [C1][B1]
     Second reply:15                     8 July 2016
     Committee’s evaluation:             Additional information required on paragraphs 7 [B][C]
                                         and 15 [A][C]

     Paragraph 7
"""
THA = """
              Concluding observations             CCPR/C/THA/CO/2, 25 April 2017
              Committee’s evaluation:                   Additional information required on paragraphs
                                                        8[C], 22[B][C] and 34[B]
              Information from non-governmental Centre for Civil and Political Rights

"""
VIEJA = """
     Concluding observations:            CCPR/C/CHL/CO/6, 22 July 2014
     Committee’s evaluation:             Additional information required on paragraphs 8 [B2][C1]

"""
fallos = 0
def ok(n, c):
    global fallos
    print(('✓ ' if c else '✗ ') + n); fallos += not c

f = []
a = s.evaluaciones(ARM, REG, f)
ok('formato de un país por addendum (Armenia): párrafos 16, 40 y 42 con sus notas y el tema',
   len(a) == 1 and a[0]['pais'] == 'ARM' and [(p['n'], p['notas']) for p in a[0]['parrafos']] == [(16, ['B']), (40, ['C', 'B']), (42, ['B'])] and a[0]['parrafos'][0]['tema'] == 'Violence against women')
i = s.evaluaciones(ISL, REG, f)
ok('informe con varios países (Islandia): se toma la evaluación de ese informe, no la anterior con subnotas',
   len(i) == 1 and [(p['n'], p['notas']) for p in i[0]['parrafos']] == [(7, ['B', 'C']), (15, ['A', 'C'])])
t = s.evaluaciones(THA, REG, f)
ok('cabecera sin dos puntos (Tailandia) y la evaluación literal acaba en la última nota',
   len(t) == 1 and [(p['n'], p['notas']) for p in t[0]['parrafos']] == [(8, ['C']), (22, ['B', 'C']), (34, ['B'])] and t[0]['evaluacion'].endswith('34[B]'))
f = []
ok('la escala anterior (B2, C1…) no se mezcla: queda anotada como no incluida', s.evaluaciones(VIEJA, REG, f) == [] and len(f) == 1 and 'escala anterior' in f[0])

d = json.load(open(os.path.join(RAIZ, 'data', 'seguimiento_comites', 'ccpr.json'), encoding='utf-8'))
ok('los datos traen la leyenda oficial A–E y su informe', sorted(k for k in d['leyenda'] if len(k) == 1) == list('ABCDE') and d['leyenda']['informe'].startswith('CCPR/C/'))
ok('cada nota de los datos es A, B, C, D o E, y cada evaluación cita su informe y sus observaciones finales',
   all(n in 'ABCDE' and len(n) == 1 for e in d['evaluaciones'] for p in e['parrafos'] for n in p['notas'])
   and all(e['informe'].startswith('CCPR/C/') and e['observaciones'].startswith('CCPR/C/' + e['pais'] + '/CO/') and e['url'].startswith('https://digitallibrary.un.org/record/') for e in d['evaluaciones']))
sys.exit(1 if fallos else 0)
