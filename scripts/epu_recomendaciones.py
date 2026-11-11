#!/usr/bin/env python3
"""T68 (c) · Cuenta las recomendaciones que cada país recibió en el Examen Periódico Universal, leyendo el texto de los
informes del Grupo de Trabajo (A/HRC/<sesión>/<n>, en inglés) que baja `texto_completo.py` (lista en data/fuentes/epu_informes.json).
Una «recomendación» es cada punto numerado de la sección «Conclusions and/or recommendations» (116.1, 116.2…): un mismo
punto puede estar formulado por varios Estados. Ciclos 2, 3 y 4 (desde 2012): el ciclo 1 numera de otra manera y no se cuenta.
Un informe solo entra si la numeración sale completa y seguida (1, 2, 3… sin huecos); si no, se lista como dudoso y no se publica cifra.
Salida: data/epu.js (carga bajo demanda) y data/fuentes/epu_recomendaciones.json (auditoría: lo contado y lo dudoso).
Uso: epu_recomendaciones.py [--dir DIR_TEXTOS]"""
import json, os, re, sys, time
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.environ.get('ATLAS_TEXTOS_DIR', os.path.expanduser('~/.local/share/atlas-onu/textos'))
CICLOS = [(1, '2008–2011', ''), (2, '2012–2016', '2012-04-01'), (3, '2017–2022', '2017-04-01'), (4, 'desde 2022', '2022-09-01')]
def ciclo(fecha):
    c = 1
    for n, _, desde in CICLOS:
        if desde and fecha >= desde: c = n
    return c
def slug(s): return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')
def seccion(t):
    """Texto entre el encabezado «Conclusions and/or recommendations» (no el del índice, que lleva puntos) y el párrafo final.
    Los informes de 2014 a 2017 escriben «Conclusions and recommendations», y algún PDF tiene una errata en la palabra."""
    m = re.search(r'(?im)^[ \t]*(?:[IVX]+\.[ \t]*)?conclusions and(?:/or)? recomm\w{0,3}endations(?![^\n]*\.[ \t]?\.[ \t]?\.)[^\w\n]*$', t)   # el título puede llevar asteriscos de nota («∗∗»); el del índice lleva puntos («....») y no casa
    if not m: return None
    fin = re.search(r'(?i)all conclusions and(?:/or)? recommendations contained in the present report', t[m.end():])
    return t[m.end():m.end() + fin.start()] if fin else t[m.end():]
def listas(s):
    """Las listas numeradas de la sección `s` (texto de seccion()), en el orden del texto: ([(prefijo, inicio, [(k, pos)…])…], saltos).
    Se sigue la secuencia 1, 2, 3… de cada lista (el prefijo del párrafo, 116.x, a veces trae erratas en el original: «127.10» por
    «126.10»; el número que se publica lleva el prefijo de la lista). `inicio` es dónde empieza el primer punto, para leer la frase
    que introduce la lista («… enjoy the support of …», «… will be examined by …»)."""
    primero, pre_run, ultimo, salida, saltos = None, None, 0, [], []
    # a veces el número se pega al final de la línea anterior: «(Spain);144.50 Redouble…»
    for m in re.finditer(r'(?m)(?:^|(?<=;))[ \t]*(\d{2,3})\.(\d{1,3})\.?(?=[ \t]|$)', s):
        pre, k = int(m[1]), int(m[2])
        if primero is None: primero = pre
        if not (primero <= pre <= primero + 3 or (pre_run is not None and abs(pre - pre_run) <= 3)):
            continue   # una remisión a otro informe («paragraphs 116.28 and 116.111…») al principio de línea no es una recomendación
        if k == 1 and primero <= pre <= primero + 3:
            pre_run, ultimo = pre, 1      # empieza una lista (apoyadas; en el ciclo 2 también tomadas en nota y no apoyadas)
            salida.append((pre, m.start(1), [(1, m.start(1))]))
        elif pre_run is not None and k == ultimo + 1:
            ultimo = k; salida[-1][2].append((k, m.start(1)))
        elif pre_run is not None and k != ultimo:
            saltos.append(f'{pre}.{k} tras {ultimo}')
    return salida, saltos
def numeros(t):
    """Los números de recomendación de un informe («116.1», …, «116.243»), o None si contar() no da cifra (mismo criterio)."""
    s = seccion(t)
    if s is None: return None
    ls, saltos = listas(s)
    if saltos or not ls: return None
    return [f'{pre}.{k}' for pre, _, ks in ls for k, _ in ks]
def contar(t):
    """(n, motivo): n = recomendaciones numeradas; None si no se puede contar con seguridad.
    Si la secuencia de una lista salta (falta un número o hay uno mal escrito), no se da cifra."""
    s = seccion(t)
    if s is None: return None, 'sin sección de recomendaciones'
    ls, saltos = listas(s)
    n = sum(len(ks) for _, _, ks in ls)
    if n == 0: return None, 'sin numeración NNN.M'
    if saltos: return None, 'la numeración salta: ' + ', '.join(saltos[:3])
    return n, ''
def main():
    d = DIR
    if '--dir' in sys.argv: d = sys.argv[sys.argv.index('--dir') + 1]
    inf = json.load(open(os.path.join(RAIZ, 'data/fuentes/epu_informes.json'), encoding='utf-8'))
    p, aud, sin_texto = {}, {'contados': 0, 'dudosos': [], 'ciclo1': 0}, []
    for iso, lista in sorted(inf['paises'].items()):
        for f in lista:
            c = ciclo(f['d'])
            if c == 1: aud['ciclo1'] += 1; continue
            ruta = os.path.join(d, 'txt', f"{slug(f['s'])}-en.txt")
            if not os.path.exists(ruta): sin_texto.append(f['s']); continue
            n, motivo = contar(open(ruta, encoding='utf-8', errors='ignore').read())
            if n is None: aud['dudosos'].append({'iso': iso, 's': f['s'], 'motivo': motivo}); continue
            p.setdefault(iso, []).append([c, n, f['s'], f['d'][:4]]); aud['contados'] += 1
    aud['sin_texto'] = sin_texto
    for l in p.values(): l.sort()
    salida = {'v': inf.get('obtenido', ''), 'c': [[n, t] for n, t, _ in CICLOS if n > 1], 'p': p}
    open(os.path.join(RAIZ, 'data/epu.js'), 'w', encoding='utf-8').write('window.EPU=' + json.dumps(salida, ensure_ascii=False, separators=(',', ':'), sort_keys=True) + ';\n')
    json.dump(aud, open(os.path.join(RAIZ, 'data/fuentes/epu_recomendaciones.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(aud['contados'], 'informes contados;', len(aud['dudosos']), 'dudosos;', len(sin_texto), 'sin texto todavía;', aud['ciclo1'], 'del ciclo 1 (no se cuentan);', len(p), 'países')
if __name__ == '__main__': main()
