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
            'paises': len(d['paises']), 'mecanismos': len(d['mecanismos']), 'paises_con_tratados': sum(1 for p in d['paises'] if p.get('tratados')), 'paises_con_docs': sum(1 for p in d['paises'] if (p.get('docs') or {}).get('co') or (p.get('docs') or {}).get('epu')), 'docs_co': sum((p.get('docs') or {}).get('co', 0) for p in d['paises']), 'titulares': sum(len(m['titulares']) for m in d['mandatos'])}
ca, cb = cuenta(a), cuenta(b); fallos = []
if not 45 <= cb['mandatos'] <= 90: fallos.append(f"mandatos fuera de rango: {cb['mandatos']}")
if cb['paises'] < 185: fallos.append(f"países < 185: {cb['paises']}")
if cb['paises_con_tratados'] < 180: fallos.append(f"países con tratados < 180: {cb['paises_con_tratados']}")
if cb['paises_con_docs'] < 170: fallos.append(f"países con documentos < 170: {cb['paises_con_docs']}")
for t in b['tratados']:   # un nombre de país mal leído (p. ej. con nota al pie) haría perder ratificaciones
    n = sum(1 for p in b['paises'] if (p.get('tratados') or {}).get(t['mtdsg']))
    if t['participantes'] - n > 4: fallos.append(f"{t['siglas']}: {n} países emparejados de {t['participantes']} participantes")
if sum(1 for t in b['tratados'] if t.get('texto')) < 8: fallos.append('tratados con texto literal < 8')
if ca.get('docs_co') and cb['docs_co'] < ca['docs_co'] * 0.95: fallos.append(f"observaciones finales caen de {ca['docs_co']} a {cb['docs_co']}")
if cb['mecanismos'] < 20: fallos.append(f"mecanismos < 20: {cb['mecanismos']}")
for k in ('mandatos', 'actos', 'localizados', 'texto_directo', 'con_ruta', 'titulares'):
    if ca[k] and cb[k] < ca[k] * (0.9 if k in ('mandatos', 'titulares') else 0.95): fallos.append(f"{k} cae de {ca[k]} a {cb[k]}")
if cb['con_ruta'] < cb['texto_directo']: fallos.append('rutas inconsistentes')
print(json.dumps({'antes': ca, 'despues': cb}, ensure_ascii=False))
if fallos: print('DATOS DEGRADADOS, NO SE PUBLICA:', fallos); sys.exit(1)
