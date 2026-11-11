#!/usr/bin/env python3
"""T90 · Pruebas de scripts/hoja_ruta_github.py: el estado de cada elemento de «Qué falta y qué viene» sale de sus issues."""
import json, os, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import hoja_ruta_github as h

def iss(n, estado='open', motivo=None, etiquetas=(), cuerpo=''):
    return {'number': n, 'state': estado, 'state_reason': motivo, 'labels': [{'name': e} for e in etiquetas], 'body': cuerpo}

def hoja(**bloques):
    return {'actualizado': '2026-01-01', 'bloques': [{'id': b, 'titulo': b, 'intro': '', 'items': bloques.get(b, [])} for b in h.BLOQUES]}

def donde(salida):
    return {it['t']: b['id'] for b in salida['bloques'] for it in b['items']}

fallos = 0
def ok(nombre, cond):
    global fallos
    print(('ok   ' if cond else 'FALLO ') + nombre)
    fallos += not cond

base = hoja(pendiente=[{'t': 'A', 'x': '.', 'issues': [1]}, {'t': 'B', 'x': '.', 'issues': [2, 3]}, {'t': 'Fijo', 'x': '.'}],
            evaluacion=[{'t': 'C', 'x': '.', 'issues': [4], 'tag': 'en evaluación'}],
            disponible=[{'t': 'Viejo', 'x': '.'}])
issues = h.normalizar([iss(1, 'closed', 'completed'), iss(2, 'closed', 'completed'), iss(3), iss(4, 'closed', 'completed'),
                       iss(5, cuerpo='texto\n<!-- web\nt: Nuevo\nx: Algo nuevo.\n-->'), iss(6), iss(7, etiquetas=['interno'], cuerpo='<!-- web\nt: Oculto\nx: No.\n-->'),
                       {'number': 8, 'state': 'open', 'pull_request': {}, 'labels': [], 'body': ''}])
s, cambios, avisos = h.sincronizar(json.loads(json.dumps(base)), issues, '2026-11-11')
d = donde(s)
ok('cerrado como hecho -> Ya disponible', d['A'] == 'disponible')
ok('con un issue aún abierto sigue en Pendiente', d['B'] == 'pendiente')
ok('sin issues no se mueve', d['Fijo'] == 'pendiente' and d['Viejo'] == 'disponible')
ok('al salir de evaluación pierde la etiqueta vieja', d['C'] == 'disponible' and not any(it.get('tag') for b in s['bloques'] for it in b['items'] if it['t'] == 'C'))
ok('issue nuevo con bloque web entra en Pendiente con su texto', d.get('Nuevo') == 'pendiente')
ok('«interno» y PR nunca entran', 'Oculto' not in d and len(d) == 6)
ok('issue abierto sin texto para la web: aviso, no se publica', any('#6' in a for a in avisos))
ok('con cambios se pone la fecha', s['actualizado'] == '2026-11-11')
ok('idempotente: segunda pasada sin cambios', h.sincronizar(s, issues, '2026-11-12')[1] == [])

s2 = h.sincronizar(hoja(pendiente=[{'t': 'D', 'x': '.', 'issues': [9]}, {'t': 'E', 'x': '.', 'issues': [10]}, {'t': 'F', 'x': '.', 'issues': [11]}, {'t': 'G', 'x': '.', 'issues': [99]}]),
                   h.normalizar([iss(9, 'closed', 'not_planned'), iss(10, etiquetas=['en-evaluacion']), iss(11, etiquetas=['idea'])]), '2026-11-11')
d2 = donde(s2[0])
ok('cerrado como «no se hará» -> fuera', 'D' not in d2)
ok('etiqueta en-evaluacion -> En evaluación', d2['E'] == 'evaluacion')
ok('etiqueta idea -> Ideas', d2['F'] == 'ideas')
ok('issue que no existe: se queda donde está y avisa', d2['G'] == 'pendiente' and any('no existe' in a for a in s2[2]))
ok('bloque web incompleto no vale', h.texto_web('<!-- web\nt: Solo título\n-->') is None)

real = json.load(open(os.path.join(RAIZ, 'data', 'hoja_ruta.json'), encoding='utf-8'))
ok('data/hoja_ruta.json: cuatro bloques y "issues" son listas de números', [b['id'] for b in real['bloques']] == list(h.BLOQUES)
   and all(isinstance(n, int) for b in real['bloques'] for it in b['items'] for n in it.get('issues', [])))
ok('data/hoja_ruta.json: ningún elemento pendiente o en evaluación sin issue', all(it.get('issues') for b in real['bloques'] if b['id'] in ('pendiente', 'evaluacion') for it in b['items']))

print(f'{fallos} fallos')
sys.exit(1 if fallos else 0)
