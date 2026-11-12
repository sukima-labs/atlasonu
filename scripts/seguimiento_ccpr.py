#!/usr/bin/env python3
"""T75 fase 2a: notas del Comité de Derechos Humanos (CCPR) en su procedimiento de seguimiento de las observaciones finales.

Fuente: los informes finales «Report on follow-up to the concluding observations of the Human Rights Committee»
(CCPR/C/<sesión>/2 o /3 y sus addenda) de la Biblioteca Digital de la ONU. Los borradores (R.1) no se usan.
Cada addendum evalúa uno o varios países y trae una línea «Committee's evaluation: 16 [B], 40 [C] [B] and 42 [B]»;
luego cada párrafo con su tema. Se guarda lo que el informe dice, sin interpretar: país (de la signatura de las
observaciones finales), párrafo, tema y notas. La leyenda de las notas se copia del propio documento principal.

  python3 -I scripts/seguimiento_ccpr.py --cache /var/tmp/t75fu   # baja lo que falta (5 s entre peticiones) y escribe
                                                                  # data/seguimiento_comites/ccpr.json y ccpr.js (la web)
Robots.txt de la Biblioteca Digital: Crawl-delay 5. Nunca a la vez que otro cliente (texto_completo.py, 03:30).
"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'ATLAS-ONU/1.0 (academic)'}
BUSCA = 'https://digitallibrary.un.org/search?ln=en&of=xm&rg=100&jrec=%d&p=%s'
CONSULTA = '"Report on follow-up to the concluding observations of the Human Rights Committee"'
SIMBOLO = re.compile(r'^CCPR/C/(\d+)/[23](/Add\.\d+)?$')
_ult = [0.0]


def pide(url):
    espera = 5 - (time.time() - _ult[0])
    if espera > 0: time.sleep(espera)
    _ult[0] = time.time()
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: return r.read()


def registros():
    out, jrec = [], 1
    while True:
        xml = pide(BUSCA % (jrec, urllib.parse.quote_plus(CONSULTA))).decode('utf-8')
        recs = xml.split('<record>')[1:]
        for r in recs:
            sim = re.findall(r'tag="191".*?code="a">([^<]+)', r, re.S)
            if not sim or not SIMBOLO.match(sim[0]) or 'draft' in r: continue
            pdf = [u for u in re.findall(r'code="u">([^<]+)', r) if u.endswith('-EN.pdf')]
            fecha = re.findall(r'tag="269".*?code="a">([^<]+)', r, re.S)
            if pdf: out.append({'simbolo': sim[0], 'registro': re.findall(r'tag="001">(\d+)', r)[0], 'fecha': fecha[0] if fecha else '', 'pdf': pdf[0]})
        if len(recs) < 100: return out
        jrec += 100


def texto(reg, cache):
    base = os.path.join(cache, reg['simbolo'].replace('/', '_'))
    if not os.path.exists(base + '.txt'):
        url = reg['pdf'].replace('digitallibrary.un.org/record/', 'digitallibrary.un.org/nanna/record/') + '?withWatermark=0&withMetadata=0&version=1'
        datos = pide(url)
        if not datos.startswith(b'%PDF'): raise RuntimeError('no es un PDF: ' + reg['pdf'])
        open(base + '.pdf', 'wb').write(datos)
        subprocess.run(['pdftotext', '-layout', base + '.pdf', base + '.txt'], check=True, capture_output=True)
    return open(base + '.txt', encoding='utf-8', errors='replace').read()


NOTA = re.compile(r'\[([A-E]\d?)\*?\]')
CABECERA = re.compile(r'Concluding observations[^\n]{0,40}?(CCPR/C/([A-Z]{3})/CO/[\w/.-]+),\s*([^\n]+)')


def evaluaciones(txt, reg, fuera):
    """Un bloque por país, de una cabecera «Concluding observations … CCPR/C/XXX/CO/n» a la siguiente. Sirve para los
    addenda de un país (desde 2019) y para los informes que reunían varios países (2013-2018). Solo se guardan las
    evaluaciones con la escala actual (A, B, C, D, E); las de la escala anterior (B1, C2…) se anotan en «fuera»."""
    cab = list(CABECERA.finditer(txt))
    out = []
    for k, co in enumerate(cab):
        p = txt[co.end():cab[k + 1].start() if k + 1 < len(cab) else len(txt)]
        evs = [' '.join(m.group(1).split()) for m in re.finditer(r'Committee.s evaluation[^:\n]*:\s*(.+?)\n\s*\n', p, re.S)]
        if not evs: continue
        linea = ' | '.join(evs)
        if any(len(g) > 1 for g in NOTA.findall(linea)):
            fuera.append(f"{reg['simbolo']} {co.group(2)}: escala anterior (subnotas como B1 o C2)"); continue
        notas = {}
        for m in re.finditer(r'(\d+)\s*((?:\[[A-E]\*?\]\s*)+)', linea): notas.setdefault(m.group(1), []).extend(NOTA.findall(m.group(2)))
        if not notas:
            fuera.append(f"{reg['simbolo']} {co.group(2)}: sin notas por párrafo ({linea[:80]})"); continue
        temas = {}
        for m in re.finditer(r'\n\s*Paragraph (\d+):\s*([^\n]+)', p):
            t = ' '.join(m.group(2).split())
            if len(t) < 90 and not t.startswith('The State'): temas.setdefault(m.group(1), t)
        out.append({'pais': co.group(2), 'observaciones': co.group(1), 'observaciones_fecha': co.group(3).strip(),
                    'informe': reg['simbolo'], 'informe_fecha': reg['fecha'],
                    'url': 'https://digitallibrary.un.org/record/' + reg['registro'],
                    'evaluacion': linea[:linea.rfind(']') + 1],
                    'parrafos': [{'n': int(n), 'tema': temas.get(n, ''), 'notas': v} for n, v in notas.items()]})
    return out


def leyenda(txt):
    """Copia literal de la leyenda de notas (A, B, C, D, E) de la portada del informe."""
    L = {}
    for k in 'ABCDE':
        m = re.search(r'\n\s*' + k + r'\s{2,}([A-Z][^\n]+(?:\n\s{12,}[^\s][^\n]+)*)', txt)
        if m: L[k] = ' '.join(m.group(1).split())
    return L


def main():
    cache = sys.argv[sys.argv.index('--cache') + 1] if '--cache' in sys.argv else '/var/tmp/t75fu'
    os.makedirs(cache, exist_ok=True)
    regs = sorted(registros(), key=lambda r: r['simbolo'])
    paises, ley, fallos, fuera = [], {}, [], []
    for r in sorted(regs, key=lambda r: r['fecha'], reverse=True):
        try: t = texto(r, cache)
        except Exception as e: fallos.append(f"{r['simbolo']}: {e}"); continue
        if '/Add.' not in r['simbolo'] and len(ley) < 5:
            l = leyenda(t)
            if len(l) == 5: ley = dict(l, informe=r['simbolo'])
        paises += evaluaciones(t, r, fuera)
    paises.sort(key=lambda e: (e['pais'], e['informe_fecha']))
    os.makedirs(os.path.join(RAIZ, 'data', 'seguimiento_comites'), exist_ok=True)
    out = {'comite': 'CCPR', 'fuente': 'Biblioteca Digital de la ONU: ' + CONSULTA, 'consultado': time.strftime('%Y-%m-%d'),
           'informes': len(regs), 'leyenda': ley, 'evaluaciones': paises, 'no_incluidas': fuera, 'fallos': fallos}
    json.dump(out, open(os.path.join(RAIZ, 'data', 'seguimiento_comites', 'ccpr.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # La web lo carga como .js (con <script>) para que la copia descargada funcione abierta como fichero, sin servidor.
    web = {k: out[k] for k in ('comite', 'consultado', 'leyenda')}
    web['evaluaciones'] = [{k: e[k] for k in ('pais', 'observaciones', 'observaciones_fecha', 'informe', 'informe_fecha', 'url', 'parrafos')} for e in paises]
    open(os.path.join(RAIZ, 'data', 'seguimiento_comites', 'ccpr.js'), 'w', encoding='utf-8').write(
        '/* T75 fase 2: generado por scripts/seguimiento_ccpr.py; no se edita a mano. */\nwindow.SEG_CCPR=' + json.dumps(web, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f"{len(regs)} informes, {len(paises)} evaluaciones de país, {sum(len(p['parrafos']) for p in paises)} párrafos, leyenda {sorted(ley)}, no incluidas {len(fuera)}, fallos {len(fallos)}")


if __name__ == '__main__':
    main()
