#!/usr/bin/env python3
"""T75 fase 2c: el analizador de los informes de seguimiento del Comité contra la Desaparición Forzada lee las notas
tal como están escritas (fragmentos copiados de CED/C/28/2 y CED/C/11/2) y los datos generados citan su informe."""
import json, os, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import seguimiento_ced as s

REG = {'simbolo': 'CED/C/28/2', 'fecha': '2025-05-20', 'registro': '1'}
PAN = """
             Concluding observations:         CED/C/PAN/CO/1, adopted 24 September 2021
                                              (twenty-first session)
             Recommendations to be            Paragraphs 11 (compilation of the centralized register of
             followed up on:                  missing and disappeared persons), 27 (communication by
                                              persons deprived of liberty) and 37 (search for disappeared
                                              persons and return of their remains)

             Paragraph 11: The Committee recommends that the State Party expedite the
             compilation of the centralized, permanent register.

              Committee’s evaluation
              5.     [C]: The Committee notes that the State Party repeats the figures concerning

              Paragraph 27: The Committee recommends that the State Party take the necessary

              Committee’s evaluation
              7.       [B]: The Committee takes note of the information provided by the State Party. This
"""
NLD = """
             Concluding observations:              CED/C/NLD/CO/1, adopted 26 March 2014

             Recommendations to be                 Paragraphs 25, 33 and 35
             followed up:

             Paragraph 25: The Committee recommends that the State party remove the

             Committee’s evaluation
             [C]: The Committee takes note of the information provided by the State party and

             A letter should be sent to the State party communicating the Committee’s evaluation.
"""
LEY = """
             Assessment criteria

             A       Reply/action satisfactory: The State Party has provided evidence of significant
                     action taken towards implementing the Committee’s recommendation.

             B       Reply/action partially satisfactory: The State Party has taken steps towards
                     implementing the recommendation, but additional information or action is
                     necessary.



         * Adopted by the Committee
"""
fallos = 0
def ok(n, c):
    global fallos
    print(('✓ ' if c else '✗ ') + n); fallos += not c

f = []
p = s.evaluaciones(PAN, REG, f)
ok('Panamá: párrafos 11 [C] y 27 [B], con el tema de la lista en dos columnas y la fecha completa',
   len(p) == 1 and p[0]['pais'] == 'PAN' and [(x['n'], x['notas']) for x in p[0]['parrafos']] == [(11, ['C']), (27, ['B'])]
   and p[0]['parrafos'][1]['tema'] == 'communication by persons deprived of liberty' and p[0]['observaciones_fecha'] == '24 September 2021')
n = s.evaluaciones(NLD, REG, f)
ok('formato antiguo sin número de párrafo (Países Bajos): 25 [C]; la frase de la carta no se lee como nota',
   len(n) == 1 and [(x['n'], x['notas']) for x in n[0]['parrafos']] == [(25, ['C'])] and n[0]['parrafos'][0]['tema'] == '')
l = s.leyenda(LEY)
ok('la leyenda se copia letra a letra sin arrastrar la siguiente', sorted(l) == ['A', 'B'] and l['B'].endswith('action is necessary.') and 'Reply' not in l['A'][20:])

d = json.load(open(os.path.join(RAIZ, 'data', 'seguimiento_comites', 'ced.json'), encoding='utf-8'))
ok('los datos traen la leyenda oficial A–E y su informe', sorted(k for k in d['leyenda'] if len(k) == 1) == list('ABCDE') and d['leyenda']['informe'].startswith('CED/C/'))
ok('cada nota es A–E y cada evaluación cita su informe y sus observaciones finales',
   all(x in 'ABCDE' and len(x) == 1 for e in d['evaluaciones'] for p in e['parrafos'] for x in p['notas'])
   and all(e['informe'].startswith('CED/C/') and e['observaciones'].startswith('CED/C/' + e['pais'] + '/CO/') and e['url'].startswith('https://digitallibrary.un.org/record/') for e in d['evaluaciones']))
ok('T56: los scripts de seguimiento no usan /search (prohibido en el robots.txt de la Biblioteca Digital); leen informes.json',
   all('digitallibrary.un.org/search' not in open(os.path.join(RAIZ, 'scripts', f), encoding='utf-8').read() for f in ('seguimiento_ccpr.py', 'seguimiento_ced.py'))
   and {r['comite'] for r in json.load(open(os.path.join(RAIZ, 'data', 'seguimiento_comites', 'informes.json'), encoding='utf-8'))['informes']} == {'CCPR', 'CED'})
sys.exit(1 if fallos else 0)
