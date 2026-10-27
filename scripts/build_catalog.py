#!/usr/bin/env python3
"""Genera data/atlas-data.js y data/catalogo.json a partir de las fuentes oficiales descargadas.
Uso: build_catalog.py <verif.json> <fecha>   (lee data/fuentes/ohchr_{TM,CM}_{en,es}.json y data/contexto_v06.json)"""
import json, re, sys
verif_path, fecha = sys.argv[1], sys.argv[2]
L = lambda n: json.load(open(f'data/fuentes/{n}.json', encoding='utf-8'))
V = json.load(open(verif_path, encoding='utf-8'))['resultados']
ctx = json.load(open('data/contexto_v06.json', encoding='utf-8'))
vmap = {}
for r in V: vmap.setdefault((r['mandato'], r['acto']), []).append(r)

ORG = {'HRC resolution': 'Consejo de Derechos Humanos', 'Commission on Human Rights resolution': 'Comisión de Derechos Humanos',
       'Resolución del Consejo': 'Consejo de Derechos Humanos'}
def organo(es, en):
    if en in ORG: return ORG[en]
    if re.search(r'Commission', en or '') or re.search(r'Comisi', es or ''): return 'Comisión de Derechos Humanos'
    if re.search(r'ECOSOC|Economic', en or '') or re.search(r'Econ', es or ''): return 'Consejo Económico y Social'
    if re.search(r'General Assembly|Asamblea', (en or '') + (es or '')): return 'Asamblea General'
    if re.search(r'HRC|Human Rights Council|Consejo', (en or '') + (es or '')): return 'Consejo de Derechos Humanos'
    return es or en or 'No consta en la fuente'

def holders(txt):
    out = []
    for t, nm, pais in re.findall(r'(Mr\.|Ms\.|Mrs\.|Dr\.|Sr\.|Sra\.|Prof\.|Sr\.|Sra)\s+(.+?)\s*\(([^)]+)\)', txt):
        out.append({'tratamiento': t, 'nombre': nm.strip(), 'pais': pais.strip()})
    return out

def acto_from(r, rol, anio, por_en, por_es, sym_src):
    a = {'rol': rol, 'anio': anio, 'organo': organo(por_es, por_en), 'simbolo_fuente': sym_src, 'estado': r['estado']}
    if r.get('registro'):
        h = r['registro']
        a.update({'simbolo': h['simbolo'], 'titulo_oficial': h['titulo'], 'adoptada': h['adoptada'] or h['fecha'], 'sesion_nota': h.get('sesion_nota',''), 'ubicacion': h.get('ubicacion',[]), 'padres': h.get('padres',[]),
                  'borradores': h['borradores'], 'votacion': h['votacion'], 'registro': h['url'], 'pdf': h['pdf'],
                  'via_borrador': r['consultado'].startswith('D:') or (r['limpio'] != h['simbolo'] and r['limpio'] in h['borradores'])})
        if r['estado'] == 'VERIFICADO_NORMALIZADO' or a['via_borrador']:
            a['aviso'] = f"La fuente OHCHR cita «{sym_src}»; el documento oficial es «{h['simbolo']}» (equivalencia inferida por símbolo y título; no se ha leído el texto)."
        elif r['estado'] == 'REVISAR_TITULO':
            a['aviso'] = f"«{h['simbolo']}» existe, pero el título del registro («{h['titulo']}») no menciona el mandato; en resoluciones antiguas suele ser el punto del orden del día. Cotejar el texto antes de citar."
        elif r['estado'] == 'DOCUMENTO_NO_RESOLUCION':
            a['aviso'] = f"«{sym_src}» existe, pero es «{h['titulo']}», no el texto de una resolución. No tomarlo como acto creador sin cotejo."
        elif r['estado'] == 'SOLO_BORRADOR':
            a['aviso'] = f"«{sym_src}» es un borrador (L.); la Biblioteca Digital no lo vincula a la resolución adoptada."
    if r['estado'] == 'NO_ENCONTRADO':
        a['aviso'] = f"«{sym_src}» no tiene registro exacto en la Biblioteca Digital ONU a {fecha}; puede ser un texto aún no publicado, un error de la fuente o un acto incorporado a un informe de sesión."
    elif r['estado'] == 'SIN_SIMBOLO':
        a['aviso'] = 'La fuente no indica símbolo para este acto.'
    return a

recs, index = [], {}
for kind in ('TM', 'CM'):
    en, es = L(f'ohchr_{kind}_en')['mandatos'], L(f'ohchr_{kind}_es')['mandatos']
    assert len(en) == len(es), (kind, len(en), len(es))
    key = lambda m: (m['creado_anio'], m['creado_simbolo'].upper(), m['prorrogado_anio'], m['prorrogado_simbolo'].upper(),
                     re.sub(r'\W+', '', m['titulares_texto'])[:40], len(m['prorrogas_intermedias']))
    pool = {}
    for m in es: pool.setdefault(key(m), []).append(m)
    pairs = []
    for me in en:
        lst = pool.get(key(me))
        assert lst, ('sin pareja ES', me['titulo'], key(me))
        pairs.append((me, lst.pop(0)))
    for me, ms in pairs:
        t = me['titulo']; actos = []
        c = vmap.get((t, 'creado'))
        if c: actos.append(acto_from(c[0], 'creación', me['creado_anio'], me['creado_por'], ms['creado_por'], me['creado_simbolo']))
        for x, xs in zip(me['prorrogas_intermedias'], ms['prorrogas_intermedias'] or me['prorrogas_intermedias']):
            rr = vmap.get((t, 'intermedia:' + x['anio']), [])
            cand = next((q for q in rr if q['original'] == x['simbolo']), None)
            if cand: actos.append(acto_from(cand, 'prórroga intermedia', x['anio'], x['por'], xs['por'], x['simbolo']))
        p = vmap.get((t, 'prorrogado'))
        if p and (me['prorrogado_anio'] or me['prorrogado_simbolo']):
            actos.append(acto_from(p[0], 'prórroga vigente', me['prorrogado_anio'], me['prorrogado_por'], ms['prorrogado_por'], me['prorrogado_simbolo']))
        # elimina duplicados exactos (la fuente repite filas)
        seen, ded = set(), []
        for a in actos:
            k = (a['rol'], a['anio'], a.get('simbolo', a['simbolo_fuente']))
            if k not in seen: seen.add(k); ded.append(a)
        actos = ded
        cre = next((a for a in actos if a['rol'] == 'creación'), None)
        if cre and cre['estado'] == 'VERIFICADO':
            rev = 'Acto de creación localizado en la Biblioteca Digital ONU'
        elif cre and cre['estado'] == 'VERIFICADO_NORMALIZADO':
            rev = 'Acto de creación localizado con símbolo corregido (ver nota)'
        elif cre and cre['estado'] in ('REVISAR_TITULO', 'DOCUMENTO_NO_RESOLUCION', 'SOLO_BORRADOR'):
            rev = 'Acto de creación con reservas: cotejar texto (ver nota)'
        elif False:
            rev = 'Acto de creación verificado en la Biblioteca Digital ONU'
        elif cre and cre['estado'] == 'NO_ENCONTRADO':
            rev = 'Acto de creación SIN registro exacto: cotejar en informe de sesión'
        else:
            rev = 'Acto de creación sin símbolo en la fuente'
        ver = sum(1 for a in actos if a['estado'] in ('VERIFICADO', 'VERIFICADO_NORMALIZADO'))
        nota = ' '.join(dict.fromkeys(a['aviso'] for a in actos if a.get('aviso')))
        rec = {'tema': me['etiqueta'] and ms['etiqueta'] or ms['titulo'], 'nombre': ms['titulo'], 'nameEN': me['titulo'],
               'alcance': 'Temático' if kind == 'TM' else 'País', 'anio': int(me['creado_anio']) if me['creado_anio'].isdigit() else 0,
               'organo': organo(ms['creado_por'], me['creado_por']),
               'creacion': (cre or {}).get('simbolo') or me['creado_simbolo'] or '—',
               'renovacion': next((a.get('simbolo') or a['simbolo_fuente'] for a in reversed(actos) if a['rol'] == 'prórroga vigente'), ''),
               'renovacion_anio': me['prorrogado_anio'], 'metodos': '', 'revision': rev, 'nota': nota,
               'actos': actos, 'actos_verificados': ver, 'actos_total': len(actos),
               'titulares': holders(ms['titulares_texto']), 'titulares_texto': ms['titulares_texto'],
               'observaciones': ms['observaciones'],
               'indiceES': L(f'ohchr_{kind}_es')['fuente'], 'indiceEN': L(f'ohchr_{kind}_en')['fuente']}
        recs.append(rec)
        for a in actos:
            if a['estado'] in ('VERIFICADO', 'VERIFICADO_NORMALIZADO'):
                e = index.setdefault(a['simbolo'], {'simbolo': a['simbolo'], 'titulo': a['titulo_oficial'], 'adoptada': a['adoptada'],
                    'borradores': a['borradores'], 'votacion': a['votacion'], 'registro': a['registro'], 'pdf': a['pdf'], 'sesion_nota': a.get('sesion_nota',''), 'ubicacion': a.get('ubicacion',[]), 'padres': a.get('padres',[]), 'mandatos': []})
                if me['titulo'] not in e['mandatos']: e['mandatos'].append(me['titulo'])
                for b in a['borradores']: index.setdefault('~' + b, {'ref': a['simbolo']})

alertas, seen_a = [], set()
for r in recs:
    for a in r['actos']:
        st = a['estado']
        if st in ('VERIFICADO', 'SIN_SIMBOLO'): continue
        k = (r['nameEN'], a['rol'], a['anio'], a['simbolo_fuente'])
        if k in seen_a: continue
        seen_a.add(k)
        via_l = bool(a.get('via_borrador'))
        nivel = 'BAJA' if via_l else ('MEDIA' if st == 'VERIFICADO_NORMALIZADO' else 'ALTA')
        accion = {'VERIFICADO_NORMALIZADO': 'Usar el símbolo oficial indicado; la fuente cita otra forma.',
                  'REVISAR_TITULO': 'Leer el texto del documento antes de citarlo como acto del mandato.',
                  'DOCUMENTO_NO_RESOLUCION': 'No citar como resolución; localizar el acto creador real.',
                  'SOLO_BORRADOR': 'Localizar la resolución adoptada; el borrador no tiene efectos.',
                  'NO_ENCONTRADO': 'Reintentar más adelante o buscar en el informe de sesión.'}.get(st, '')
        alertas.append({'id': f'V-{len(alertas)+1:03d}', 'simbolo': a['simbolo_fuente'] or '—', 'tema': f"{r['nombre']} ({a['anio']}, {a['rol']})",
                        'problema': a.get('aviso', st), 'nivel': nivel, 'accion': accion, 'url': a.get('registro') or 'https://digitallibrary.un.org/'})
alertas.sort(key=lambda x: {'ALTA': 0, 'MEDIA': 1, 'BAJA': 2}[x['nivel']])
alertas += [a for a in ctx['alertas'] if a['id'] == 'A-08']
ctx['alertas'] = alertas
import os
if os.path.exists('data/fuentes/textos.json'):
    for k, v in json.load(open('data/fuentes/textos.json', encoding='utf-8')).items():
        if k in index: index[k]['texto'] = v
ev = json.load(open('data/evidencias.json', encoding='utf-8'))
for k, v in ev.items():
    if k in index: index[k]['evidencia'] = v
data = {'version': '0.7', 'consultado': fecha,
        'fuentes': ['https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM', 'https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=CM',
                    'https://digitallibrary.un.org/'],
        'mandatos': recs, 'indice_actos': index,
        'trazas': ctx['trazas'], 'alertas': ctx['alertas'], 'codigos': ctx['codigos'], 'seleccion': ctx['seleccion']}
json.dump(data, open('data/catalogo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open('data/atlas-data.js', 'w', encoding='utf-8').write('window.ATLAS_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
from collections import Counter
print(len(recs), 'mandatos;', len(index), 'entradas índice;', Counter(a['estado'] for r in recs for a in r['actos']))
