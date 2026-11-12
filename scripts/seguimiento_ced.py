#!/usr/bin/env python3
"""T75 fase 2c: notas del Comité contra la Desaparición Forzada (CED) en su seguimiento de las observaciones finales.

Fuente: los informes finales «Report on follow-up to (the) concluding observations of the Committee on Enforced
Disappearances» (CED/C/<sesión>/2) de la Biblioteca Digital de la ONU. Los borradores (R.n) no se usan. Cada país trae
«Concluding observations: CED/C/XXX/CO/n», luego cada «Paragraph N: …» con la respuesta del Estado y un «Committee's
evaluation» que empieza por la nota: «[B]: The Committee takes note…». Se guarda lo que el informe dice, sin
interpretar. La leyenda se copia del informe más reciente.

Comprobado el 12-11-2026: de los demás comités, en la Biblioteca Digital solo el CED publica notas por párrafo. El CRPD
publica un informe de seguimiento (CRPD/C/33/3) sin notas, en texto; del CERD, la CEDAW y el CESCR solo están las
respuestas de los Estados (…/FCO/…), y sus valoraciones van en cartas.

  python3 -I scripts/seguimiento_ced.py --cache /var/tmp/t75fu   # baja lo que falta (5 s entre peticiones) y escribe
                                                                 # data/seguimiento_comites/ced.json y ced.js (la web)
La lista de informes está en data/seguimiento_comites/informes.json (el robots.txt prohíbe /search). Crawl-delay 5. Nunca a la vez que otro cliente (texto_completo.py, 03:30).
"""
import json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seguimiento_ccpr as S
from seguimiento_ccpr import RAIZ, texto

CONSULTAS = ['"Report on follow-up to the concluding observations of the Committee on Enforced Disappearances"',
             '"Report on follow-up to concluding observations of the Committee on Enforced Disappearances"']
CABECERA = re.compile(r'Concluding observations:\s*(CED/C/([A-Z]{3})/CO/[\w/.-]+),?\s*(?:adopted\s*)?(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})')
NOTAS = re.compile(r'Committee.s evaluation\s*\n\s*(?:\d+\.\s*)?((?:\[[A-E]\]\s*)+):')


def registros(fuera):
    """Los informes de data/seguimiento_comites/informes.json (no se busca: /search está prohibido en el robots.txt)."""
    out = []
    for r in S.registros('CED'):
        if r.get('nota'): fuera.append(f"{r['simbolo']}: {r['nota']}")
        else: out.append(r)
    return out


def temas(bloque):
    """«Recommendations to be followed up on: Paragraphs 11 (register), 27 (…) and 37 (…)», en dos columnas."""
    m = re.search(r'Recommendations to be(.+?)\n\s*\n', bloque, re.S)
    if not m: return {}
    t = ' '.join(re.sub(r'followed up( on)?:', ' ', m.group(1)).split())
    return {n: ' '.join(x.split()) for n, x in re.findall(r'(\d+) \(([^)]+)\)', t)}


def leyenda(txt):
    """Copia literal de los «Assessment criteria» (A a E): cada letra hasta la línea en blanco o la letra siguiente."""
    m = re.search(r'Assessment criteria\s*\n(.+?)\n\s*\n\s*\n', txt, re.S)
    if not m: return {}
    return {k: ' '.join(v.split()) for k, v in re.findall(r'(?m)^\s*([A-E])\s{2,}(.+?)(?=\n\s*\n|\n\s*[A-E]\s{2,}|\Z)', m.group(1), re.S)}


def evaluaciones(txt, reg, fuera):
    cab = list(CABECERA.finditer(txt))
    out = []
    for k, co in enumerate(cab):
        b = txt[co.end():cab[k + 1].start() if k + 1 < len(cab) else len(txt)]
        tem, par = temas(b), list(re.finditer(r'\n\s*Paragraph (\d+):', b))
        parrafos = []
        for j, p in enumerate(par):
            trozo = b[p.end():par[j + 1].start() if j + 1 < len(par) else len(b)]
            m = NOTAS.search(trozo)
            if m: parrafos.append({'n': int(p.group(1)), 'tema': tem.get(p.group(1), ''), 'notas': re.findall(r'\[([A-E])\]', m.group(1))})
            else: fuera.append(f"{reg['simbolo']} {co.group(2)} párrafo {p.group(1)}: sin nota legible")
        if not parrafos: continue
        out.append({'pais': co.group(2), 'observaciones': co.group(1), 'observaciones_fecha': ' '.join(co.group(3).split()),
                    'informe': reg['simbolo'], 'informe_fecha': reg['fecha'],
                    'url': 'https://digitallibrary.un.org/record/' + reg['registro'], 'parrafos': parrafos})
    return out


def main():
    cache = sys.argv[sys.argv.index('--cache') + 1] if '--cache' in sys.argv else '/var/tmp/t75fu'
    os.makedirs(cache, exist_ok=True)
    fuera, fallos = [], []
    regs = registros(fuera)
    paises, ley = [], {}
    for r in sorted(regs, key=lambda r: r['fecha'], reverse=True):
        try: t = texto(r, cache)
        except Exception as e: fallos.append(f"{r['simbolo']}: {e}"); continue
        if not ley:
            l = leyenda(t)
            if len(l) == 5: ley = dict(l, informe=r['simbolo'])
        paises += evaluaciones(t, r, fuera)
    paises.sort(key=lambda e: (e['pais'], e['informe_fecha']))
    os.makedirs(os.path.join(RAIZ, 'data', 'seguimiento_comites'), exist_ok=True)
    out = {'comite': 'CED', 'fuente': 'Biblioteca Digital de la ONU: ' + ' / '.join(CONSULTAS) + ' (lista en informes.json)', 'consultado': time.strftime('%Y-%m-%d'),
           'informes': len(regs), 'leyenda': ley, 'evaluaciones': paises, 'no_incluidas': fuera, 'fallos': fallos}
    json.dump(out, open(os.path.join(RAIZ, 'data', 'seguimiento_comites', 'ced.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    web = {k: out[k] for k in ('comite', 'consultado', 'leyenda', 'evaluaciones')}
    open(os.path.join(RAIZ, 'data', 'seguimiento_comites', 'ced.js'), 'w', encoding='utf-8').write(
        '/* T75 fase 2c: generado por scripts/seguimiento_ced.py; no se edita a mano. */\nwindow.SEG_CED=' + json.dumps(web, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f"{len(regs)} informes, {len(paises)} evaluaciones de país, {sum(len(p['parrafos']) for p in paises)} párrafos, leyenda {sorted(ley)}, no incluidas {len(fuera)}, fallos {len(fallos)}")


if __name__ == '__main__':
    main()
