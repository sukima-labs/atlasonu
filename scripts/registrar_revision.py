#!/usr/bin/env python3
"""Añade esta ejecución a data/revisiones.json (más reciente primero, máximo 100).
Uso: registrar_revision.py <inicio_epoch> <huboCambios 0|1> <documentos_marco ok|conservado> <noticias ok|conservado>
Quién la hizo: variable ATLAS_EJECUTOR (el mini PC la define); en GitHub Actions se toma de GITHUB_ACTIONS."""
import json, sys, os, time, datetime
inicio, cambio, marco, noticias = int(sys.argv[1]), sys.argv[2] == '1', sys.argv[3], sys.argv[4]
fin = int(time.time())
iso = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).replace(microsecond=0).isoformat()
quien = os.environ.get('ATLAS_EJECUTOR') or ('GitHub Actions' if os.environ.get('GITHUB_ACTIONS') else 'Ejecución manual')
est = json.load(open('data/estado.json', encoding='utf-8')) if os.path.exists('data/estado.json') else {}
revisado = ['Índice de mandatos de OHCHR', 'Biblioteca Digital de la ONU (símbolos)', 'Colección de Tratados (ratificaciones)',
            'Visitas y comunicaciones de OHCHR (países y regiones)', 'Textos literales de tratados', 'Documentos oficiales por país']
reg = {'inicio': iso(inicio), 'fin': iso(fin), 'duracion_s': fin - inicio, 'quien': quien,
       'revisado': revisado, 'documentos_marco': marco, 'noticias': noticias,
       'resultado': 'cambios en los datos' if cambio else 'sin cambios', 'contadores': est.get('contadores', {})}
path = 'data/revisiones.json'
hist = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else []
json.dump([reg] + hist[:99], open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('registro de revisión:', reg['quien'], reg['resultado'], f"{reg['duracion_s']} s")
