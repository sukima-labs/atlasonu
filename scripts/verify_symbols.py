#!/usr/bin/env python3
"""Verifica símbolos ONU contra la Biblioteca Digital de la ONU (MARCXML, búsqueda por 191__a / 993__a).
Uso: verify_symbols.py <ohchr_TM_en.json> <ohchr_CM_en.json> <salida_cache.json>
Un símbolo solo se marca VERIFICADO si existe un registro con ese 191$a (o es borrador 993$a de una resolución).
No se infiere nada: lo no encontrado queda NO_ENCONTRADO."""
import re, sys, json, time, urllib.parse, urllib.request, concurrent.futures as cf, os

DL = 'https://digitallibrary.un.org/search?ln=en&of=xm&rg=100&p='
TOK = re.compile(r'(?:[AES]/[A-Za-z0-9.()\-]+(?:/[A-Za-z0-9.()\-]+)*|\b\d{4}/\d+\b)')

def clean(sym, por=''):
    s = (sym or '').strip()
    m = TOK.search(s)
    s = m.group(0) if m else ''
    if not s:
        m = re.search(r'(?:resolution|resolución)\s+(\d+/\d+)', por or '', re.I)
        if m and re.search(r'HRC|Human Rights Council|Consejo', por or ''): s = 'A/HRC/RES/' + m.group(1)
    return s.rstrip('.,;')

def candidates(s, por=''):
    out = []
    def add(x):
        if x and x not in out: out.append(x)
    if not s: return out
    s = re.sub(r'/res/', '/RES/', s, flags=re.I)
    m = re.fullmatch(r'(A/HRC/(?:S-)?\d+/L\.\d+)/Rev\.\d+', s)
    if m: add(m[1])   # los registros de borrador no siempre existen con /Rev.N
    m = re.fullmatch(r'A/HRC/(\d+)/(\d+)', s)
    if m: add(f'A/HRC/RES/{m[1]}/{m[2]}')
    m = re.fullmatch(r'E/CN\.4/(\d{4})/(\d+)', s)
    if m: add(f'E/CN.4/RES/{m[1]}/{m[2]}')   # primero la forma de resolución: sin RES el símbolo suele ser un informe
    add(s)
    add(re.sub(r'^A/RES/HRC/', 'A/HRC/RES/', s))
    m = re.fullmatch(r'E/CN\.4/(\d{4})/(\d+)', s)
    if m: add(f'E/RES/{m[1]}/{m[2]}')   # el acto puede ser del ECOSOC y no de la Comisión
    m = re.fullmatch(r'E/CN\.4/RES/(\d{4})/(\d+)/?\((X[XLVI]+)\)', s)
    if m: add(f'E/CN.4/RES/{m[2]}({m[3]})')   # forma histórica: número(sesión en romanos)
    m = re.fullmatch(r'(\d{4})/(\d+)', s)
    if m:
        if re.search(r'Commission|Comisi', por or ''): add(f'E/CN.4/RES/{m[1]}/{m[2]}')
        add(f'E/RES/{m[1]}/{m[2]}')
    m = re.fullmatch(r'A/HRC/RES/((?:19|20)\d{2})/(\d+)', s)
    if m and int(m[1]) < 2006: add(f'E/CN.4/RES/{m[1]}/{m[2]}')
    m = re.fullmatch(r'E/CN\.4/RES/(\d{4})/(\d+)/\(.*\)', s)
    if m: add(f'E/CN.4/RES/{m[1]}/{m[2]}')
    return out

STOP = set('the of and on in for to a an human rights right special rapporteur working group independent expert situation promotion protection mandate resolution question issue other persons people with by or as'.split())
def kw(t):
    return {w[:5] for w in re.findall(r'[a-z]{4,}', (t or '').lower()) if w not in STOP}
def overlap(mand, rec):
    a, b = kw(mand), kw(rec)
    return round(len(a & b) / max(1, min(len(a), len(b))), 2) if a and b else 0.0

def parse(xml):
    n = re.search(r'Number-Of-Results: (\d+)', xml)
    recs = re.findall(r'<record>(.*?)</record>', xml, re.S)
    res = []
    for r in recs:
        def f(tag, code):
            return [re.sub(r'\s+', ' ', x).strip() for x in re.findall(
                rf'<datafield tag="{tag}"[^>]*>.*?<subfield code="{code}">(.*?)</subfield>', r, re.S)]
        rid = (re.search(r'<controlfield tag="001">(\d+)', r) or [None, ''])[1]
        pdfs = {}
        for y, u in re.findall(r'<datafield tag="856"[^>]*>.*?<subfield code="y">(.*?)</subfield>.*?<subfield code="u">(.*?)</subfield>', r, re.S):
            if y in ('English', 'Español', 'Français'): pdfs[{'English': 'en', 'Español': 'es', 'Français': 'fr'}[y]] = u
        res.append({'id': rid, 'simbolo': (f('191', 'a') or [''])[0], 'simbolos': f('191', 'a'),
                    'titulo': ' '.join(f('245', 'a')[:1]).rstrip(' /:.'), 'fecha': (f('269', 'a') or [''])[0],
                    'adoptada': (f('992', 'a') or [''])[0], 'borradores': f('993', 'a'), 'votacion': (f('996', 'a') or [''])[0],
                    'pdf': pdfs, 'url': f'https://digitallibrary.un.org/record/{rid}',
                    'sesion_nota': ' '.join(f('500', 'a')), 'ubicacion': f('580', 'a') + f('593', 'a'),
                    'padres': [x for x in f('993', 'a') if not re.search(r'/L\.\d|/SR\.|/RES/', x)]})
    return res

def query(field, sym, tries=6):
    url = DL + urllib.parse.quote(f'{field}:"{sym}"')
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'ATLAS-ONU-verifier/1.0 (academic)'}), timeout=40) as r:
                return parse(r.read().decode('utf-8', 'ignore'))
        except Exception as e:
            time.sleep(4 * (i + 1)); err = str(e)
    return {'error': err}

def verify(orig, por, cache, mtitle=''):
    s = clean(orig, por)
    if not s: return {'original': orig, 'estado': 'SIN_SIMBOLO'}
    tried = []
    for c in candidates(s, por):
        key = c if isinstance(c, str) else 'D:' + c[1]
        if key not in cache:
            cache[key] = query('993__a' if not isinstance(c, str) else '191__a', c if isinstance(c, str) else c[1])
            time.sleep(0.25)
        r = cache[key]; tried.append(key)
        want = c if isinstance(c, str) else c[1]
        exact = [h for h in r if want in h['simbolos'] or want in h['borradores']] if isinstance(r, list) else []
        if exact:
            hit = exact[0]
            if re.search(r'/L\.\d+', hit['simbolo']):
                # el campo 993 del borrador remite a la resolución adoptada
                for rs in [b for b in hit['borradores'] if '/RES/' in b]:
                    if rs not in cache: cache[rs] = query('191__a', rs); time.sleep(0.25)
                    rr = [h for h in cache[rs] if rs in h['simbolos']] if isinstance(cache[rs], list) else []
                    if rr:
                        rr[0] = dict(rr[0]); rr[0]['borradores'] = sorted(set(rr[0]['borradores'] + [hit['simbolo']]))
                        return {'original': orig, 'limpio': s, 'estado': 'VERIFICADO_NORMALIZADO', 'consultado': rs, 'via_borrador': hit['simbolo'], 'registro': rr[0]}
                return {'original': orig, 'limpio': s, 'estado': 'SOLO_BORRADOR', 'consultado': key, 'registro': hit}
            es_res = bool(re.search(r'/RES/|/DEC/|RES/\d+\(', hit['simbolo'])) or key.startswith('D:')
            ov = overlap(mtitle, hit['titulo'])
            if es_res and ov < 0.2 and not re.search(r'situation of human rights|mandate', hit['titulo'], re.I) and 'borradores' in hit:
                pend = {'original': orig, 'limpio': s, 'estado': 'REVISAR_TITULO', 'consultado': key, 'coincidencia': ov, 'registro': hit}
                rest = [c2 for c2 in candidates(s, por) if (c2 if isinstance(c2, str) else c2[1]) != key]
                tried_pending = pend
                for c2 in rest:
                    k2 = c2 if isinstance(c2, str) else 'D:' + c2[1]
                    r2 = cache.get(k2)
                    if r2 is None:
                        r2 = cache[k2] = query('191__a', c2 if isinstance(c2, str) else c2[1]); time.sleep(0.25)
                    h2 = [h for h in r2 if k2 in h['simbolos']] if isinstance(r2, list) else []
                    if h2 and overlap(mtitle, h2[0]['titulo']) >= 0.2:
                        return {'original': orig, 'limpio': s, 'estado': 'VERIFICADO_NORMALIZADO', 'consultado': k2, 'coincidencia': overlap(mtitle, h2[0]['titulo']), 'registro': h2[0]}
                return tried_pending
            if not es_res:
                # existe un documento con ese símbolo, pero no es el texto de una resolución
                return {'original': orig, 'limpio': s, 'estado': 'DOCUMENTO_NO_RESOLUCION', 'consultado': key, 'registro': hit}
            return {'original': orig, 'limpio': s, 'estado': 'VERIFICADO' if key == s else 'VERIFICADO_NORMALIZADO',
                    'consultado': key, 'registro': hit}
    return {'original': orig, 'limpio': s, 'estado': 'NO_ENCONTRADO', 'probados': tried}

def main(tm, cm, out):
    cache_path = out + '.cache'
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    jobs = []
    for p in (tm, cm):
        for m in json.load(open(p))['mandatos']:
            jobs.append((m['titulo'], 'creado', m['creado_simbolo'], m['creado_por']))
            jobs.append((m['titulo'], 'prorrogado', m['prorrogado_simbolo'], m['prorrogado_por']))
            for x in m['prorrogas_intermedias']:
                jobs.append((m['titulo'], 'intermedia:' + x['anio'], x['simbolo'], x['por']))
    # una pasada previa en paralelo para rellenar caché
    uniq = {}
    for _, _, s, por in jobs:
        for c in candidates(clean(s, por), por): uniq[c if isinstance(c, str) else 'D:' + c[1]] = c
    todo = [(k, c) for k, c in uniq.items() if k not in cache]
    print(len(jobs), 'actos;', len(uniq), 'símbolos únicos;', len(todo), 'por consultar', flush=True)
    def run(kc):
        k, c = kc
        return k, query('993__a' if not isinstance(c, str) else '191__a', c if isinstance(c, str) else c[1])
    with cf.ThreadPoolExecutor(4) as ex:
        for k, r in ex.map(run, todo): cache[k] = r
    fallidas = [(k, uniq[k]) for k, v in cache.items() if isinstance(v, dict) and 'error' in v and k in uniq]
    if fallidas:   # segunda pasada: en serie y tras una pausa, por si la Biblioteca Digital limitó el ritmo
        print(len(fallidas), 'consultas fallidas; reintento en serie tras una pausa de 45 s', flush=True); time.sleep(45)
        for kc in fallidas:
            k, r = run(kc); cache[k] = r; time.sleep(1.5)
    json.dump(cache, open(cache_path, 'w'))
    errores = [k for k, v in cache.items() if isinstance(v, dict) and 'error' in v]
    if errores:   # un fallo de red no debe degradar datos ya verificados: se aborta sin publicar nada
        print('ABORTA: errores de red en', len(errores), 'consultas, p. ej.', errores[:3]); sys.exit(2)
    res = [dict(mandato=t, acto=a, **verify(s, por, cache, t)) for t, a, s, por in jobs]
    json.dump({'fuente': DL, 'resultados': res}, open(out, 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r['estado'] for r in res))

if __name__ == '__main__': main(*sys.argv[1:4])
