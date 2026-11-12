#!/usr/bin/env python3
"""Localiza el TEXTO de cada resolución del catálogo y comprueba que el PDF sea el documento citado.
Rutas, en orden: (1) PDF del registro de la Biblioteca Digital; (2) API de documentos de la ONU (ODS) por símbolo;
(3) archivo de OHCHR (ap.ohchr.org); (4) informe de sesión que contiene la resolución, con páginas.
Un PDF solo se marca validado si su primera página contiene el símbolo.
T56: las rutas 2 y 3 y la búsqueda de la 4 están prohibidas en los robots.txt de esos sitios. Por defecto el script
no usa la red (función sin_red); con BIBLIOTECA_SEARCH=si vuelve a buscar en la Biblioteca Digital, nunca en ODS ni OHCHR. Uso: resolve_texts.py <catalogo.json> <salida.json>"""
import json, re, sys, subprocess, tempfile, os, time, urllib.request, urllib.parse, concurrent.futures as cf
UA = {'User-Agent': 'ATLAS-ONU-verifier/1.0 (academic)'}
DL = 'https://digitallibrary.un.org/search?ln=en&of=xm&rg=100&p='

def get(url, n=12_000_000, method='GET'):
    req = urllib.request.Request(url, headers=UA, method=method)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.headers.get('content-type', ''), (r.read(n) if method == 'GET' else b''), r.geturl()

def pdf_has_symbol(data, sym):
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f: f.write(data); p = f.name
    try:
        t = subprocess.run(['pdftotext', '-l', '2', p, '-'], capture_output=True, text=True, timeout=60).stdout
    finally: os.unlink(p)
    norm = lambda x: re.sub(r'[\s ]', '', x).upper()
    if len(t.strip()) < 200: return None   # escaneo sin capa de texto: no se puede validar
    if norm(sym) in norm(t): return True
    # encabezados sin símbolo completo: «Resolution 7/22.», «Resolución 1982/35»
    m = re.fullmatch(r'A/HRC/RES/((?:S-)?\d+/\d+)', sym) or re.fullmatch(r'(?:E/RES|E/CN\.4/RES)/(\d{4}/\d+)', sym)
    return bool(m and re.search(r'(?:Resolution|Resoluci[oó]n|R[ée]solution)\s+' + re.escape(m[1]) + r'(?!\d)', t, re.I))

def ods(sym, lang):
    return None   # T56: documents.un.org prohíbe /api en su robots.txt; no se consulta (el código queda como historia)
    if '(' in sym: return None
    u = f'https://documents.un.org/api/symbol/access?s={urllib.parse.quote(sym, safe="/")}&l={lang}&t=pdf'
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    try: urllib.request.build_opener(NoRedir).open(urllib.request.Request(u, headers=UA), timeout=40)
    except urllib.error.HTTPError as e:
        loc = e.headers.get('location', '')
        if e.code in (301, 302) and '/error' not in loc:
            try:
                st, ct, data, _ = get(u)
                if 'pdf' in ct.lower() or data[:4] == b'%PDF': return {'url': u, 'validado': pdf_has_symbol(data, sym)}
            except Exception: return None
    except Exception: return None
    return None

def ohchr(sym):
    return None   # T56: ap.ohchr.org prohíbe todo en su robots.txt (Disallow: /); no se consulta
    m = re.fullmatch(r'A/HRC/RES/(S-)?(\d+)/(\d+)', sym)
    if m: u, kind = f"https://ap.ohchr.org/documents/E/HRC/resolutions/A_HRC_RES_{(m[1] or '')}{m[2]}_{m[3]}.pdf", 'pdf'
    else:
        m = re.fullmatch(r'E/CN\.4/RES/(\d{4})/(\d+)', sym)
        if not m: return None
        u, kind = f'https://ap.ohchr.org/documents/E/CHR/resolutions/E-CN_4-RES-{m[1]}-{m[2]}.doc', 'doc'
    try:
        st, ct, data, _ = get(u)
    except Exception: return None
    if st != 200 or 'html' in ct.lower() or len(data) < 5000: return None
    return {'url': u, 'formato': kind, 'validado': pdf_has_symbol(data, sym) if kind == 'pdf' else None}

def dl_record_pdfs(sym, cache):
    if sym in cache: return cache[sym]
    out = {}
    try:
        _, _, data, _ = get(DL + urllib.parse.quote(f'191__a:"{sym}"'))
        for rec in re.findall(r'<record>(.*?)</record>', data.decode('utf-8', 'ignore'), re.S):
            if sym in re.findall(r'<datafield tag="191"[^>]*>.*?<subfield code="a">(.*?)</subfield>', rec, re.S):
                for y, u in re.findall(r'<datafield tag="856"[^>]*>.*?<subfield code="y">(.*?)</subfield>.*?<subfield code="u">(.*?)</subfield>', rec, re.S):
                    out[{'English': 'en', 'Español': 'es', 'Français': 'fr'}.get(y, y)] = u
                rid = re.search(r'<controlfield tag="001">(\d+)', rec)
                out['_registro'] = f'https://digitallibrary.un.org/record/{rid[1]}' if rid else ''
                break
    except Exception: pass
    cache[sym] = out; return out

def paginas(ubic):
    for u in ubic:
        m = re.search(r'p\.\s*(\d+(?:\s*-\s*\d+)?)', u)
        if m: return re.sub(r'\s', '', m[1]).replace('-', '–')
    return ''

def resolve(sym, e, cache):
    fuentes = []
    for lang, u in e['pdf'].items(): fuentes.append({'tipo': 'registro', 'lengua': lang, 'url': u, 'validado': None})
    if not ({'es', 'en'} <= set(e['pdf'])):
        for lang in ('es', 'en'):
            if lang in e['pdf']: continue
            r = ods(sym, lang)
            if r: fuentes.append({'tipo': 'ods', 'lengua': lang, **r})
        r = ohchr(sym)
        if r: fuentes.append({'tipo': 'ohchr', 'lengua': 'en', **r})
    directo = any(f['validado'] is True or f['tipo'] == 'registro' for f in fuentes)
    informe = []
    for par in e.get('padres', []):
        pdfs = dl_record_pdfs(par, cache)
        if pdfs:
            informe.append({'simbolo': par, 'paginas': paginas(e.get('ubicacion', [])), 'registro': pdfs.get('_registro', ''),
                            'pdf': {k: v for k, v in pdfs.items() if not k.startswith('_')}})
    fals = [f for f in fuentes if f['validado'] is False]  # texto legible pero con otro documento
    if directo: est = 'TEXTO_DIRECTO'
    elif informe: est = 'TEXTO_EN_INFORME'
    elif any(f['tipo'] == 'ohchr' for f in fuentes): est = 'ARCHIVO_OHCHR_SIN_VALIDAR'
    else: est = 'SIN_COPIA_LOCALIZADA'
    return {'estado': est, 'fuentes': [f for f in fuentes if f['validado'] is not False], 'descartadas_por_no_coincidir': fals, 'informe_sesion': informe}

def sin_red(sym, e, ant):
    """T56: documents.un.org/api (Disallow: /api), ap.ohchr.org (Disallow: /) y digitallibrary.un.org/search (Disallow:
    /search) están prohibidos en sus robots.txt. Sin red: las copias del propio registro (e['pdf']) y lo que ya se había
    localizado antes; un acto nuevo sin copia en su registro queda SIN_COPIA_LOCALIZADA."""
    fuentes = [{'tipo': 'registro', 'lengua': l, 'url': u, 'validado': None} for l, u in e['pdf'].items()]
    if not ({'es', 'en'} <= set(e['pdf'])):
        fuentes += [f for f in ant.get('fuentes', []) if f['tipo'] != 'registro' and f['lengua'] not in e['pdf']]
    informe = [i for i in ant.get('informe_sesion', []) if i['simbolo'] in e.get('padres', [])]
    directo = any(f['validado'] is True or f['tipo'] == 'registro' for f in fuentes)
    est = 'TEXTO_DIRECTO' if directo else 'TEXTO_EN_INFORME' if informe else 'ARCHIVO_OHCHR_SIN_VALIDAR' if any(f['tipo'] == 'ohchr' for f in fuentes) else 'SIN_COPIA_LOCALIZADA'
    return {'estado': est, 'fuentes': fuentes, 'descartadas_por_no_coincidir': ant.get('descartadas_por_no_coincidir', []), 'informe_sesion': informe}

def main(cat, out):
    idx = {k: v for k, v in json.load(open(cat, encoding='utf-8'))['indice_actos'].items() if not k.startswith('~')}
    cache, res = {}, {}
    if os.environ.get('BIBLIOTECA_SEARCH') != 'si':   # T56: por defecto, sin red
        ant = json.load(open(out, encoding='utf-8')) if os.path.exists(out) else {}
        res = {k: sin_red(k, v, ant.get(k, {})) for k, v in idx.items()}
    else:
        with cf.ThreadPoolExecutor(6) as ex:
            futs = {ex.submit(resolve, k, v, cache): k for k, v in idx.items()}
            for f in cf.as_completed(futs): res[futs[f]] = f.result()
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    from collections import Counter
    print(len(res), 'resoluciones;', Counter(r['estado'] for r in res.values()), '; descartadas:', sum(len(r['descartadas_por_no_coincidir']) for r in res.values()))
if __name__ == '__main__': main(*sys.argv[1:3])
