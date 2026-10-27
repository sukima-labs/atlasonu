#!/usr/bin/env python3
"""Descarga el mapa oficial país → grupo regional de la ONU que usa la base de comunicaciones de procedimientos
especiales de OHCHR (https://spcommreports.ohchr.org/Tmsearch/TMDocuments). Salida: data/fuentes/regiones_ohchr.json"""
import re, json, html, sys, urllib.request, datetime
t = urllib.request.urlopen(urllib.request.Request('https://spcommreports.ohchr.org/Tmsearch/TMDocuments', headers={'User-Agent': 'ATLAS-ONU/1.0 (academic)'}), timeout=60).read().decode('utf-8', 'ignore')
regs = {k: html.unescape(v).strip() for k, v in re.findall(r'name="Regions" value="(\d+)"\s*/>\s*<label[^>]*>(.*?)</label>', t)}
cs = re.findall(r'data-parentID="(\d+)"\s*>\s*<input[^>]*name="Countries"\s+value="(\d+)"\s*/>\s*<label[^>]*>(.*?)</label>', t, re.S)
out = {'fuente': 'https://spcommreports.ohchr.org/Tmsearch/TMDocuments', 'consultado': sys.argv[1] if len(sys.argv) > 1 else str(datetime.date.today()),
       'grupos': regs, 'paises': {html.unescape(n).strip(): regs[p] for p, _, n in cs}}
json.dump(out, open('data/fuentes/regiones_ohchr.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out['paises']), 'países;', sorted(set(out['paises'].values())))
