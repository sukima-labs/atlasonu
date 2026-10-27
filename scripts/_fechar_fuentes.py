#!/usr/bin/env python3
"""Pone la fecha de consulta en los JSON de fuentes cuando hubo cambios reales. Uso: _fechar_fuentes.py <fecha>"""
import json, sys, glob
for p in glob.glob('data/fuentes/ohchr_*.json') + ['data/fuentes/regiones_ohchr.json', 'data/fuentes/paises_ohchr.json']:
    d = json.load(open(p, encoding='utf-8')); d['consultado'] = sys.argv[1]
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
