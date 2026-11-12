#!/usr/bin/env python3
"""Texto LITERAL (español) de los tratados, artículo por artículo, solo desde copias con capa de texto fiable.
Fuentes: (a) anexo de la resolución de la Asamblea General que adoptó el instrumento, vía API de documentos de la ONU
(solo resoluciones de 1999 en adelante, que tienen texto nativo); (b) la página de la Convención de la CEDAW del sitio
de la ONU. Las copias antiguas escaneadas (OCR con erratas) NO se transcriben: el tablero enlaza al PDF oficial.
Cada instrumento se valida: numeración 1..N contigua y N igual al número de artículos del tratado; si falla, no se publica.
Uso: fetch_tratados_texto.py [salida.json]"""
import json, re, sys, subprocess, tempfile, os, html, hashlib, urllib.request, urllib.parse
UA = {'User-Agent': 'ATLAS-ONU-verifier/1.0 (academic)'}
# id (mtdsg del catálogo) -> (símbolo de la resolución, índice de anexo dentro de ella, artículos esperados)
RES = {'IV-15': ('A/RES/61/106', 0, 50), 'IV-15-a': ('A/RES/61/106', 1, 18), 'IV-16': ('A/RES/61/177', 0, 45),
       'IV-8-b': ('A/RES/54/4', 0, 21), 'IV-3-a': ('A/RES/63/117', 0, 22), 'IV-11-d': ('A/RES/66/138', 0, 24), 'IV-9-b': ('A/RES/57/199', 0, 37)}
CEDAW_URL = 'https://www.un.org/womenwatch/daw/cedaw/text/sconvention.htm'

def get(url, n=40_000_000):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
        return r.read(n)

def pdf_texto(sym):
    raise RuntimeError('T56: documents.un.org prohíbe /api en su robots.txt; incorporar a mano desde /record/N de la Biblioteca Digital')
    u = f'https://documents.un.org/api/symbol/access?s={urllib.parse.quote(sym, safe="/")}&l=es&t=pdf'
    data = get(u)
    if data[:4] != b'%PDF': raise RuntimeError('no es PDF: ' + sym)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f: f.write(data); p = f.name
    try: t = subprocess.run(['pdftotext', p, '-'], capture_output=True, text=True, timeout=120).stdout
    finally: os.unlink(p)
    return u, t

def limpiar(lines, sym):
    out = []
    for l in lines:
        s = l.strip().replace('\x0c', '')
        if not s: out.append(''); continue
        if re.fullmatch(r'\d{1,3}', s) or s == sym or re.fullmatch(r'\d{2}-\d{4,6}\s*\(S\)(\s*\*[\d*]+\*)?', s) or re.fullmatch(r'\*[\d*]+\*', s): continue
        out.append(re.sub(r'\s+', ' ', s))
    return out

MARC = r'(?:\d{1,2}\.|[a-z]{1,3}\)|[ivx]+\))'

def reflujo(lines):
    """Une las líneas físicas del PDF en párrafos: nuevo párrafo si empieza con «1.», «a)», «i)»."""
    par, cur = [], ''
    for l in lines:
        if not l:
            if cur and not re.fullmatch(MARC, cur): par.append(cur); cur = ''
            continue
        if re.match(MARC + r'(?: |$)', l):
            if cur and not re.fullmatch(MARC, cur): par.append(cur)
            cur = l; continue
        if cur.endswith('-') and l[:1].islower(): cur = cur[:-1] + l
        else: cur = (cur + ' ' + l) if cur else l
    if cur: par.append(cur)
    return '\n\n'.join(par)

def articulos(lines, esperado, idx):
    cab = [(i, int(m[1])) for i, l in enumerate(lines) if (m := re.fullmatch(r'Art[íi]culo (\d{1,3})', l))]
    runs, cur = [], []
    for i, n in cab:
        if n == 1 and cur: runs.append(cur); cur = []
        if (not cur and n == 1) or (cur and n == cur[-1][1] + 1): cur.append((i, n))
    if cur: runs.append(cur)
    if len(runs) <= idx: raise RuntimeError(f'no hay anexo {idx}')
    run = runs[idx]
    if [n for _, n in run] != list(range(1, esperado + 1)): raise RuntimeError(f'numeración {len(run)} != {esperado}')
    fin = len(lines)
    for j in range(run[-1][0] + 1, len(lines)):
        if re.match(r'Anexo [IVX]+$', lines[j]): fin = j; break
    arts = []
    for k, (i, n) in enumerate(run):
        f = run[k + 1][0] if k + 1 < len(run) else fin
        cuerpo = [l for l in lines[i + 1:f]]
        titulo = ''
        sig = next((l for l in cuerpo[1:] if l), '')
        if cuerpo and cuerpo[0] and len(cuerpo[0]) < 80 and not re.search(r'[.:;,]$', cuerpo[0]) and cuerpo[0][0].isupper() and ',' not in cuerpo[0] and not re.match(r'(El|La|Los|Las|Todo|Todos|Cada|Si|Se) ', cuerpo[0]) and sig and (sig[0].isdigit() or sig[0].isupper()) and not (len(sig) < 20 and sig.endswith('.')):
            titulo = cuerpo.pop(0)
            while re.search(r'\b(y|o|e|de|del|a|en|con|para|por|la|el|los|las|al)$', titulo) and cuerpo and cuerpo[0] and len(cuerpo[0]) < 80:
                titulo += ' ' + cuerpo.pop(0)   # título que continúa en la línea siguiente
        txt = reflujo(cuerpo)
        arts.append({'n': n, 'titulo': titulo, 'texto': txt})
    pre = ''
    for j in range(run[0][0] - 1, -1, -1):
        if lines[j] == 'Preámbulo':
            pre = '\n'.join(lines[j + 1:run[0][0]]).strip(); break
        if re.match(r'Anexo [IVX]+$', lines[j]): break
    return arts, pre

# Erratas de la página web de la ONU detectadas al contrastarla, palabra a palabra, con la copia depositaria de la Colección de Tratados
# (https://treaties.un.org/doc/Treaties/1981/09/19810903%2005-18%20AM/Ch_IV_8p.pdf, texto en español). (antes, después, veces)
CEDAW_ERRATAS = [('Preocupados par el hecho', 'Preocupados por el hecho', 1), ('la máximo participación', 'la máxima participación', 1),
  ('exclusión a restricción', 'exclusión o restricción', 1), ('acto a práctica', 'acto o práctica', 1), ('Adaptar todos las', 'Adoptar todas las', 1),
  ('garantizando, en igualdad', 'garantizarán, en igualdad', 1), ('ser elegibles para', 'ser elegible para', 1),
  ('métodos en enseñanza', 'métodos de enseñanza', 1), ('selección de cuestiones', 'selección en cuestiones', 1),
  ('calidad de trabajo', 'calidad del trabajo', 1), ('base de estado civil', 'base del estado civil', 1), ('Los Estado Partes', 'Los Estados Partes', 1),
  ('miembros de Comité', 'miembros del Comité', 3), ('Presidente de Comité', 'Presidente del Comité', 1), ('Sede de as Naciones', 'Sede de las Naciones', 1),
  ('El mandado de dos', 'El mandato de dos', 1), ('carácter general basados', 'carácter general basadas', 1), ('Estado Parta', 'Estado Parte', 1)]

def cedaw():
    raw = get(CEDAW_URL).decode('latin-1')
    t = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</tr>|</h\d>', '\n', raw); t = html.unescape(re.sub(r'<[^>]+>', '', t))
    t = re.sub(r'[ \t\xa0]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n', t)
    i = t.index('Los Estados Partes en la presente Convención'); body = t[i:t.index('-------', i)] if '-------' in t[i:] else t[i:]
    lines = [l.strip() for l in body.split('\n')]
    cab = [(k, int(m[1])) for k, l in enumerate(lines) if (m := re.fullmatch(r'Art[íi]culo (\d{1,2})', l))]
    run = [];
    for k, n in cab:
        if n == len(run) + 1: run.append((k, n))
    if [n for _, n in run] != list(range(1, 31)): raise RuntimeError('CEDAW: numeración')
    arts = []
    for j, (k, n) in enumerate(run):
        f = run[j + 1][0] if j + 1 < len(run) else len(lines)
        cuerpo = [l for l in lines[k + 1:f] if l and not re.fullmatch(r'PARTE [IVX]+', l)]
        arts.append({'n': n, 'titulo': '', 'texto': '\n\n'.join(cuerpo)})
    pre = '\n'.join(l for l in lines[:run[0][0]] if l and not re.fullmatch(r'PARTE [IVX]+', l))
    todo = '\x00'.join([pre] + [a['texto'] for a in arts]); hechas = []
    for antes, despues, veces in CEDAW_ERRATAS:
        if todo.count(antes) != veces: print('CEDAW: errata no encontrada/cambiada:', antes, todo.count(antes)); continue
        todo = todo.replace(antes, despues); hechas.append(antes + ' → ' + despues)
    partes = todo.split('\x00'); pre = partes[0]
    for a, t in zip(arts, partes[1:]): a['texto'] = t
    return arts, pre, hechas

def main(out='data/fuentes/tratados_texto.json'):
    res = json.load(open(out, encoding='utf-8')) if os.path.exists(out) else {}  # un fallo de red no borra lo ya validado
    try:
        if 'IV-8' in res: raise RuntimeError('ya incorporado; el texto de un tratado no cambia')   # T56: sin pedirlo otra vez
        arts, pre, hechas = cedaw()
        res['IV-8'] = {'fuente': CEDAW_URL, 'calidad': 'texto web de la ONU (sin OCR)', 'articulos': arts, 'preambulo': pre,
                       'erratas_corregidas': hechas, 'nota': 'Transcripción de la página de la ONU sobre la Convención, con ' + str(len(hechas)) + ' erratas evidentes corregidas contrastando con la copia depositaria (lista abajo). Cite siempre el texto auténtico depositado.'}
    except Exception as e: print('CEDAW:', e)
    cache = {}
    for mt, (sym, idx, n) in RES.items():
        if mt in res: continue   # T56: ya incorporado; el texto adoptado no cambia
        try:
            if sym not in cache: cache[sym] = pdf_texto(sym)
            u, t = cache[sym]
            arts, pre = articulos(limpiar(t.split('\n'), sym), n, idx)
            res[mt] = {'fuente': u, 'simbolo': sym, 'calidad': 'anexo de la resolución de la Asamblea General (texto nativo del PDF)', 'articulos': arts, 'preambulo': pre}
        except Exception as e: print(mt, sym, 'NO INCORPORADO:', e)
    for v in res.values():
        v['sha1'] = hashlib.sha1(json.dumps(v['articulos'], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print({k: len(v['articulos']) for k, v in sorted(res.items())})

if __name__ == '__main__': main(*sys.argv[1:2])
