#!/usr/bin/env python3
"""T75 · Seguimiento de las recomendaciones del Examen Periódico Universal, país a país: el texto de cada recomendación
(inglés y, si cuadra, español), los Estados que la formularon y qué respondió el Estado examinado. Ciclos 2, 3 y 4.
Junta lo que ya sacan los demás scripts, sin volver a decidir nada:
  - epu_recomendaciones.py: qué es una recomendación (cada punto NNN.M de «Conclusions and/or recommendations») y cuándo
    vale un informe (numeración completa y seguida). Las cifras deben ser exactamente las de data/epu.js;
  - epu_recs.py: texto (en, es), Estados (por) y aviso de maquetación dudosa (revisar);
  - epu_respuestas.py: respuesta (r = «apoyada» | «tomó nota» | null) y dónde está escrita (f = «informe» | «adendo» | null).
Nunca se supone una respuesta: si no está escrita de forma inequívoca para ESE número, r es null y se enlaza el documento.
Salida:
  data/seguimiento/<ISO3>.json   {"iso", "examenes": [{"s", "ciclo", "fecha", "add", "enlace", "enlace_add", "f", "recs": [...]}]}
      Solo los exámenes cuya lista salió completa. Para que pese menos (todo junto pasaba de 40 MB) no se pierde nada, pero
      en cada recomendación se omiten las claves vacías: falta «es» = sin español alineado; falta «por» = Estados no
      reconocidos; falta «r» = sin respuesta inequívoca (null); «revisar»: true solo si el PDF descolocó el texto. Las claves
      n y en van siempre. La fuente («informe» | «adendo») más frecuente del examen va una vez en el examen («f») y solo la
      llevan las recomendaciones que la tienen distinta: fuente = rec.f si está; si no, examen.f cuando hay «r»; si no, null.
  data/fuentes/epu_seguimiento.json   auditoría: totales por ciclo, informes con y sin lista (con motivo), y la fecha de
      generación, que es la más reciente de los informes y adendos (no la del reloj: así la salida es reproducible).
Sin red: solo lee los textos locales de texto_completo.py.
Uso: epu_seguimiento.py [--dir DIR_TEXTOS]"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epu_recomendaciones as E  # noqa: E402
import epu_recs as T  # noqa: E402
import epu_respuestas as P  # noqa: E402

SALIDA = os.path.join(E.RAIZ, 'data/seguimiento')
AUDITORIA = os.path.join(E.RAIZ, 'data/fuentes/epu_seguimiento.json')
CLAVES = ('n', 'en', 'es', 'por', 'r', 'f', 'revisar')
RESPUESTAS = (P.APOYADA, P.NOTA, None)


def _lee(ruta):
    if not os.path.exists(ruta): return None
    with open(ruta, encoding='utf-8', errors='ignore') as fh: return fh.read()


def publicadas():
    """{símbolo: n} del contador ya publicado en el mapa (data/epu.js)."""
    with open(os.path.join(E.RAIZ, 'data/epu.js'), encoding='utf-8') as fh: s = fh.read()
    p = json.loads(re.sub(r'^window\.EPU=|;\s*$', '', s.strip()))['p']
    return {simb: n for l in p.values() for _, n, simb, _ in l}


def recomendaciones(texto_en, texto_es, texto_add):
    """(lista de recs compactas, motivo): lista None si el informe no vale (motivo dice por qué)."""
    n, motivo = E.contar(texto_en)
    if n is None: return None, motivo
    recs, nums = T.extraer(texto_en, texto_es), E.numeros(texto_en)
    if recs is None or nums is None or [x['n'] for x in recs] != nums or len(nums) != n:
        return None, 'el texto de las recomendaciones no cuadra con la numeración'
    resp = P.respuestas(texto_en, texto_add, nums)
    salida = []
    for x in recs:
        a = resp[x['n']]
        d = {'n': x['n'], 'en': x['en'], 'es': x['es'], 'por': x['por'], 'r': a['r'], 'f': a['fuente'] if a['r'] else None,
             'revisar': x['revisar']}
        salida.append({k: v for k, v in d.items() if k in ('n', 'en') or v not in (None, False, '', [])})
    return salida, ''


def compactar(recs):
    """{'f': fuente más frecuente, 'recs': …} quitando «f» de las recomendaciones que la comparten (sin perder datos:
    la fuente de una recomendación es su «f» si la lleva; si no, la del examen cuando tiene «r»; si no tiene «r», null)."""
    cuenta = {}
    for x in recs:
        if 'f' in x: cuenta[x['f']] = cuenta.get(x['f'], 0) + 1
    if not cuenta: return {'f': None, 'recs': recs}
    f = max(sorted(cuenta), key=cuenta.get)
    return {'f': f, 'recs': [{k: v for k, v in x.items() if not (k == 'f' and v == f)} for x in recs]}


def fuente(examen, rec):
    """La fuente de la respuesta de `rec` («informe», «adendo» o None), deshaciendo compactar()."""
    return rec.get('f', examen.get('f')) if 'r' in rec else None


def main():
    d = E.DIR
    if '--dir' in sys.argv: d = sys.argv[sys.argv.index('--dir') + 1]
    inf = json.load(open(os.path.join(E.RAIZ, 'data/fuentes/epu_informes.json'), encoding='utf-8'))
    pub = publicadas()
    ciclos = {c: dict(informes=0, con_lista=0, sin_lista=0, recomendaciones=0, con_es=0, desde_informe=0, desde_adendo=0,
                      null=0, apoyada=0, tomo_nota=0, revisar=0) for c in (2, 3, 4)}
    sin_lista, distintas, fechas, paises = [], [], [], {}
    for iso, lista in sorted(inf['paises'].items()):
        for f in sorted(lista, key=lambda f: f['d']):
            c = E.ciclo(f['d'])
            if c == 1: continue
            add = f.get('add') or {}
            fechas += [f['d'][:10]] + ([add['d'][:10]] if add.get('d') else [])
            k = ciclos[c]; k['informes'] += 1
            sl = E.slug(f['s'])
            te = _lee(os.path.join(d, 'txt', f'{sl}-en.txt'))
            if te is None:
                recs, motivo = None, 'sin texto en inglés todavía'
            else:
                ta = _lee(os.path.join(d, 'txt', f"{E.slug(add['s'])}-en.txt")) if add.get('s') else None
                recs, motivo = recomendaciones(te, _lee(os.path.join(d, 'txt', f'{sl}-es.txt')), ta)
            if recs is None:
                k['sin_lista'] += 1
                sin_lista.append({'iso': iso, 's': f['s'], 'ciclo': c, 'motivo': motivo})
                if f['s'] in pub: distintas.append({'s': f['s'], 'epu_js': pub[f['s']], 'aqui': None})
                continue
            if pub.get(f['s']) != len(recs): distintas.append({'s': f['s'], 'epu_js': pub.get(f['s']), 'aqui': len(recs)})
            k['con_lista'] += 1; k['recomendaciones'] += len(recs)
            for x in recs:
                k['con_es'] += 'es' in x; k['revisar'] += 'revisar' in x
                k['desde_informe'] += x.get('f') == 'informe'; k['desde_adendo'] += x.get('f') == 'adendo'
                k['null'] += 'r' not in x
                k['apoyada'] += x.get('r') == P.APOYADA; k['tomo_nota'] += x.get('r') == P.NOTA
            paises.setdefault(iso, []).append({'s': f['s'], 'ciclo': c, 'fecha': f['d'][:10], 'add': add.get('s'),
                                               'enlace': f.get('en'), 'enlace_add': add.get('en'), **compactar(recs)})
    sin_lista += [{'iso': None, 's': s, 'ciclo': None, 'motivo': 'publicado en data/epu.js pero no está en epu_informes.json'}
                  for s in sorted(set(pub) - {e['s'] for l in paises.values() for e in l} - {x['s'] for x in sin_lista})]
    os.makedirs(SALIDA, exist_ok=True)
    for viejo in os.listdir(SALIDA):
        if viejo.endswith('.json') and viejo[:-5] not in paises: os.remove(os.path.join(SALIDA, viejo))
    for iso, ex in paises.items():
        with open(os.path.join(SALIDA, f'{iso}.json'), 'w', encoding='utf-8') as fh:
            json.dump({'iso': iso, 'examenes': ex}, fh, ensure_ascii=False, separators=(',', ':'))
    total = {x: sum(k[x] for k in ciclos.values()) for x in ciclos[2]}
    aud = {'generado': max(fechas), 'fuente': inf.get('obtenido', ''), 'paises': len(paises), 'total': total,
           'ciclos': {str(c): k for c, k in ciclos.items()}, 'distintas_de_epu_js': distintas, 'sin_lista': sin_lista}
    with open(AUDITORIA, 'w', encoding='utf-8') as fh:
        json.dump(aud, fh, ensure_ascii=False, indent=1); fh.write('\n')
    print(f"{total['con_lista']} informes con lista ({total['recomendaciones']} recomendaciones, {len(paises)} países);"
          f" {total['sin_lista']} sin lista; distintas de data/epu.js: {len(distintas)}")
    print(f"  con español {total['con_es']}; respuesta desde el informe {total['desde_informe']}, desde el adendo"
          f" {total['desde_adendo']}, null {total['null']}")
    if distintas: sys.exit('ERROR: las cifras no cuadran con data/epu.js: ' + json.dumps(distintas[:5], ensure_ascii=False))


if __name__ == '__main__': main()
