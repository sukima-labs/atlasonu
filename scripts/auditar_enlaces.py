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
for e in d.get('sistema', {}).get('entidades', []): add(e.get('url'), 'entidad ' + e['id'])
for c in d.get('sistema', {}).get('comites', []): add('https://www.ohchr.org/es/treaty-bodies/' + c['slug'], 'comité ' + c['id'])
for t in d['tratados']:
    add(t.get('url'), 'tratado ' + t['siglas'])
    if t.get('texto'): add(t['texto']['fuente'], 'texto literal ' + t['siglas'])
# T77 fase C: guías de «Tengo un caso» y enlaces del ACNUDH de las vías (formularios, portal de envío). Las páginas de la
# Colección de Tratados y de la Biblioteca Digital no se repiten aquí: las lee fetch_tratados.py respetando su Crawl-delay.
_v = open('data/vias.js', encoding='utf-8').read()
vias = json.loads(_v[_v.index('{'):_v.rindex('}') + 1])
for g in vias['guias']: add(g.get('url'), 'guía ' + g['id'])
def _urls(x):
    if isinstance(x, dict):
        for k, y in x.items():
            if k == 'url' and isinstance(y, str): yield y
            else: yield from _urls(y)
    elif isinstance(x, list):
        for y in x: yield from _urls(y)
for u in _urls(vias['vias']):
    if 'ohchr.org' in u: add(u, 'vía (ACNUDH)')
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
# Solo 404/410 son definitivos; un tiempo agotado (la guía de México no responde a la descarga automática) queda en el informe sin fallar.
rotas = [o for o in out if o['estado'] in (404, 410) and o['origen'].startswith(('guía ', 'vía '))]
if rotas:
    md.append("\n## Enlaces de «Tengo un caso» rotos (hay que corregir `data/vias.js`)\n")
    md += [f"- `{o['estado']}` {o['url']} — {o['origen']}" for o in rotas]
open('audit/ENLACES.md', 'w').write('\n'.join(md) + '\n'); print(dict(c))
# Un enlace roto de una guía o de una vía hace fallar el workflow: GitHub avisa y no se queda en un artefacto sin leer.
if rotas: print('ROTOS en «Tengo un caso»:', *[o['url'] for o in rotas], sep='\n  '); sys.exit(1)
