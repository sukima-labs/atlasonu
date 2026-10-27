#!/usr/bin/env python3
"""Compara el catálogo anterior con el nuevo y registra qué cambió (se muestra en la plataforma).
Uso: detectar_cambios.py <catalogo_anterior.json> <catalogo_nuevo.json> <fecha> → actualiza data/historial_cambios.json
Devuelve por stdout el número de cambios."""
import json, sys, os
prev, new, fecha = json.load(open(sys.argv[1], encoding='utf-8')), json.load(open(sys.argv[2], encoding='utf-8')), sys.argv[3]
cambios = []
pm = {m['nameEN']: m for m in prev['mandatos']}; nm = {m['nameEN']: m for m in new['mandatos']}
for k in nm.keys() - pm.keys(): cambios.append({'tipo': 'mandato_nuevo', 'texto': f"Nuevo mandato: {nm[k]['nombre']} ({nm[k]['creacion']})"})
for k in pm.keys() - nm.keys(): cambios.append({'tipo': 'mandato_retirado', 'texto': f"Mandato que ya no figura en el índice vigente: {pm[k]['nombre']}"})
for k in nm.keys() & pm.keys():
    a, b = pm[k], nm[k]
    if a['renovacion'] != b['renovacion'] or a['renovacion_anio'] != b['renovacion_anio']:
        cambios.append({'tipo': 'prorroga', 'texto': f"{b['nombre']}: prórroga vigente {a['renovacion'] or '—'} ({a['renovacion_anio'] or '—'}) → {b['renovacion'] or '—'} ({b['renovacion_anio'] or '—'})"})
    ta, tb = {h['nombre'] for h in a['titulares']}, {h['nombre'] for h in b['titulares']}
    if ta != tb: cambios.append({'tipo': 'titular', 'texto': f"{b['nombre']}: titulares {', '.join(sorted(ta)) or 'sin titular'} → {', '.join(sorted(tb)) or 'sin titular'}"})
    if a['actos_total'] != b['actos_total']: cambios.append({'tipo': 'actos', 'texto': f"{b['nombre']}: {a['actos_total']} → {b['actos_total']} actos jurídicos registrados"})
pa, pn = {p['id']: p for p in prev.get('paises', [])}, {p['id']: p for p in new.get('paises', [])}
for k in pn.keys() & pa.keys():
    if pa[k]['invitacion']['si'] != pn[k]['invitacion']['si']:
        cambios.append({'tipo': 'invitacion', 'texto': f"{pn[k]['es']}: invitación permanente {'cursada' if pn[k]['invitacion']['si'] else 'retirada'}"})
    if pa[k]['visitas']['programadas'] != pn[k]['visitas']['programadas']:
        cambios.append({'tipo': 'visita', 'texto': f"{pn[k]['es']}: visita {'programada' if pn[k]['visitas']['programadas'] else 'ya no figura como programada'}"})
ia, i2 = prev['indice_actos'], new['indice_actos']
nuevas = [k for k in i2 if not k.startswith('~') and k not in ia]
if nuevas: cambios.append({'tipo': 'resoluciones', 'texto': f"{len(nuevas)} resolución(es) nueva(s) localizada(s): {', '.join(sorted(nuevas)[:6])}{'…' if len(nuevas) > 6 else ''}"})
for k in i2:
    if k.startswith('~') or k not in ia: continue
    ea, eb = ia[k].get('texto', {}).get('estado'), i2[k].get('texto', {}).get('estado')
    if ea != eb and eb == 'TEXTO_DIRECTO': cambios.append({'tipo': 'texto', 'texto': f"{k}: ya hay PDF propio (antes: {ea})"})
path = 'data/historial_cambios.json'
hist = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else []
if cambios: hist.insert(0, {'fecha': fecha, 'cambios': cambios})
json.dump(hist[:120], open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(cambios))
