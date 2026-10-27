#!/usr/bin/env python3
"""Salvaguarda antes de publicar: compara con el catálogo anterior y aborta (exit 1) si los datos se degradan.
Uso: validar_datos.py <catalogo_anterior.json> <catalogo_nuevo.json>"""
import json, sys
a, b = json.load(open(sys.argv[1], encoding='utf-8')), json.load(open(sys.argv[2], encoding='utf-8'))
def cuenta(d):
    acts = [x for m in d['mandatos'] for x in m['actos']]
    idx = [e for k, e in d['indice_actos'].items() if not k.startswith('~') and e.get('texto')]
    return {'mandatos': len(d['mandatos']), 'actos': len(acts), 'localizados': sum(1 for x in acts if x['estado'] in ('VERIFICADO', 'VERIFICADO_NORMALIZADO')),
            'texto_directo': sum(1 for e in idx if e['texto']['estado'] == 'TEXTO_DIRECTO'), 'con_ruta': sum(1 for e in idx if e['texto']['fuentes'] or e['texto']['informe_sesion']),
            'paises': len(d['paises']), 'mecanismos': len(d['mecanismos']), 'titulares': sum(len(m['titulares']) for m in d['mandatos'])}
ca, cb = cuenta(a), cuenta(b); fallos = []
if not 45 <= cb['mandatos'] <= 90: fallos.append(f"mandatos fuera de rango: {cb['mandatos']}")
if cb['paises'] < 185: fallos.append(f"países < 185: {cb['paises']}")
if cb['mecanismos'] < 20: fallos.append(f"mecanismos < 20: {cb['mecanismos']}")
for k in ('mandatos', 'actos', 'localizados', 'texto_directo', 'con_ruta', 'titulares'):
    if ca[k] and cb[k] < ca[k] * (0.9 if k in ('mandatos', 'titulares') else 0.95): fallos.append(f"{k} cae de {ca[k]} a {cb[k]}")
if cb['con_ruta'] < cb['texto_directo']: fallos.append('rutas inconsistentes')
print(json.dumps({'antes': ca, 'despues': cb}, ensure_ascii=False))
if fallos: print('DATOS DEGRADADOS, NO SE PUBLICA:', fallos); sys.exit(1)
