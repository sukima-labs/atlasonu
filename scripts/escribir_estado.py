#!/usr/bin/env python3
"""Escribe data/estado.json (lo consulta la página para avisar de datos más recientes).
Uso: escribir_estado.py <catalogo.json> <huboCambios 0|1>"""
import json, sys, datetime, os
d = json.load(open(sys.argv[1], encoding='utf-8')); hubo = sys.argv[2] == '1'
ahora = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
prev = json.load(open('data/estado.json', encoding='utf-8')) if os.path.exists('data/estado.json') else {}
hist = json.load(open('data/historial_cambios.json', encoding='utf-8')) if os.path.exists('data/historial_cambios.json') else []
acts = [x for m in d['mandatos'] for x in m['actos']]
est = {'revisado_el': ahora, 'datos_del': d['consultado'], 'hubo_cambios_en_esta_revision': hubo,
       'ultimo_cambio_el': (ahora if hubo else prev.get('ultimo_cambio_el', ahora)),
       'contadores': {'mandatos': len(d['mandatos']), 'actos': len(acts), 'localizados': sum(1 for x in acts if x['estado'] in ('VERIFICADO', 'VERIFICADO_NORMALIZADO')), 'paises': len(d['paises']), 'mecanismos': len(d['mecanismos'])},
       'fuentes': [{'nombre': 'Índice de mandatos de OHCHR', 'url': d['fuentes'][0]}, {'nombre': 'Biblioteca Digital de la ONU', 'url': 'https://digitallibrary.un.org/'},
                   {'nombre': 'Colección de Tratados de la ONU (ratificaciones)', 'url': d['tratados_fuente']['url']}, {'nombre': 'Base de visitas de OHCHR', 'url': d['paises_fuente']['url']}, {'nombre': 'Base de comunicaciones de OHCHR (grupos regionales)', 'url': d['regiones_fuente']['url']}],
       'ultimos_cambios': [{'fecha': h['fecha'], 'n': len(h['cambios']), 'ejemplos': [c['texto'] for c in h['cambios'][:3]]} for h in hist[:8]]}
json.dump(est, open('data/estado.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('estado:', est['revisado_el'], 'cambios' if hubo else 'sin cambios')
