#!/usr/bin/env python3
"""Audita los enlaces externos del catálogo. Salida: audit/ENLACES.md y audit/enlaces.json.
Clasificación: OK (200) · ANTIRROBOT (202/403/429: el sitio bloquea o desafía a scripts; no concluyente) · ROTO (404/410/5xx/error)."""
import json, re, sys, urllib.request, urllib.error, concurrent.futures as cf, datetime
d = json.load(open('data/catalogo.json', encoding='utf-8'))
urls = {}
def add(u, origen):
    if isinstance(u, str) and u.startswith('http'): urls.setdefault(u, origen)
for k, e in d['indice_actos'].items():
    if k.startswith('~'): continue
    add(e.get('registro'), 'registro ' + k)
    for f in e.get('texto', {}).get('fuentes', []):
        if f['tipo'] != 'registro': add(f['url'], f"texto {f['tipo']} {k}")
    for i in e.get('texto', {}).get('informe_sesion', []): add(i.get('registro'), f"informe {i['simbolo']}")
for m in d['mecanismos']: add(m.get('registro'), 'mecanismo ' + m['siglas'])
for sec in ('trazas', 'alertas', 'codigos', 'seleccion'):
    for r in d[sec]:
        for key in ('url',): add(r.get(key), f'{sec} {r.get("id") or r.get("simbolo") or r.get("paso")}')
for u in d['fuentes']: add(u, 'fuente oficial')
def chk(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (ATLAS-ONU link audit)', 'Range': 'bytes=0-2048'})
    try:
        with urllib.request.urlopen(req, timeout=40) as r: return u, r.status
    except urllib.error.HTTPError as e: return u, e.code
    except Exception as e: return u, type(e).__name__
with cf.ThreadPoolExecutor(8) as ex: res = dict(ex.map(chk, urls))
cls = lambda s: 'OK' if s in (200, 206) else 'ANTIRROBOT' if s in (202, 403, 429, 401) else 'ROTO'
out = [{'url': u, 'estado': s, 'clase': cls(s), 'origen': urls[u]} for u, s in res.items()]
json.dump(out, open('audit/enlaces.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
c = Counter(o['clase'] for o in out)
md = [f"# Auditoría de enlaces externos ({datetime.date.today()})\n", f"Total: {len(out)} · OK {c['OK']} · anti-robot (no concluyente) {c['ANTIRROBOT']} · rotos {c['ROTO']}\n",
      "Los PDF del registro de la Biblioteca Digital no se auditan aquí: se validaron leyendo su contenido (ver `muestreo_pdfs_registro.json` y `scripts/resolve_texts.py`).\n"]
for cl in ('ROTO', 'ANTIRROBOT'):
    rows = [o for o in out if o['clase'] == cl]
    if rows:
        md.append(f"\n## {cl} ({len(rows)})\n")
        for o in sorted(rows, key=lambda x: x['origen'])[:60]: md.append(f"- `{o['estado']}` {o['url']} — {o['origen']}")
open('audit/ENLACES.md', 'w').write('\n'.join(md) + '\n'); print(dict(c))
