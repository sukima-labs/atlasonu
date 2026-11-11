#!/usr/bin/env python3
"""T90 · La pantalla «Qué falta y qué viene» toma el ESTADO de los issues de GitHub; el texto en lenguaje claro sigue en
data/hoja_ruta.json.

Cada elemento de data/hoja_ruta.json puede llevar "issues": [n, …]. Con ellos se decide en qué bloque va:
  - todos cerrados como «no se hará» (state_reason not_planned)  -> sale de la pantalla;
  - alguno abierto con la etiqueta «en-evaluacion»                -> «En evaluación»;
  - alguno abierto                                               -> «Pendiente» (o «Ideas» si TODOS los abiertos llevan «idea»);
  - todos cerrados como hechos                                   -> «Ya disponible».
Un elemento sin "issues" no se mueve (lo ya hecho de antes de T90 y las ideas sin issue).

Un issue que no está en ningún elemento entra solo si su cuerpo trae el texto para la web en un bloque oculto:
    <!-- web
    t: Título en lenguaje claro
    x: Una o dos frases para quien visita la página, sin jerga ni nombres de personas.
    -->
Sin ese bloque no se publica nada (la web no muestra títulos técnicos): se lista en la salida como «sin texto para la web».
Los issues con «interno», «infra» o «duplicate», y los PR, no entran nunca.

Uso:  hoja_ruta_github.py [--issues fichero.json] [--hoy AAAA-MM-DD] [--comprobar]
  Sin --issues lee la API pública de GitHub (GITHUB_TOKEN opcional; GITHUB_REPOSITORY o sukima-labs/atlasonu).
  --comprobar no escribe: sale con código 1 si la pantalla no está al día con los issues."""
import json, os, re, sys, urllib.request, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOJA = os.path.join(RAIZ, 'data', 'hoja_ruta.json')
NUNCA = {'interno', 'infra', 'duplicate'}
BLOQUES = ('disponible', 'evaluacion', 'pendiente', 'ideas')
RE_WEB = re.compile(r'<!--\s*web\s*\n(.*?)-->', re.S)


def leer_issues_api():
    repo = os.environ.get('GITHUB_REPOSITORY', 'sukima-labs/atlasonu')
    cab = {'Accept': 'application/vnd.github+json', 'User-Agent': 'atlas-onu-hoja-ruta'}
    if os.environ.get('GITHUB_TOKEN'):
        cab['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    todos, pagina = [], 1
    while True:
        url = f'https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={pagina}'
        with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=30) as r:
            lote = json.load(r)
        todos += lote
        if len(lote) < 100:
            return todos
        pagina += 1


def normalizar(raw):
    """De la respuesta de la API (o de un fichero de pruebas con el mismo formato) a {n: issue}."""
    out = {}
    for i in raw:
        if i.get('pull_request'):
            continue
        out[i['number']] = {
            'n': i['number'],
            'abierto': i['state'] == 'open',
            'motivo': i.get('state_reason') or '',
            'etiquetas': {(e['name'] if isinstance(e, dict) else e) for e in i.get('labels', [])},
            'cuerpo': i.get('body') or '',
        }
    return out


def texto_web(cuerpo):
    m = RE_WEB.search(cuerpo)
    if not m:
        return None
    campos = {}
    for linea in m.group(1).splitlines():
        k, _, v = linea.partition(':')
        if k.strip() in ('t', 'x') and v.strip():
            campos[k.strip()] = v.strip()
    return campos if 't' in campos and 'x' in campos else None


def bloque_de(nums, issues):
    """Bloque que toca según los issues; None = quitar de la pantalla; '' = no se sabe (issue que no existe)."""
    ii = [issues.get(n) for n in nums]
    if any(i is None for i in ii):
        return ''
    abiertos = [i for i in ii if i['abierto']]
    if not abiertos:
        return None if all(i['motivo'] == 'not_planned' for i in ii) else 'disponible'
    if any('en-evaluacion' in i['etiquetas'] for i in abiertos):
        return 'evaluacion'
    if all('idea' in i['etiquetas'] for i in abiertos):
        return 'ideas'
    return 'pendiente'


def sincronizar(hoja, issues, hoy):
    """Devuelve (hoja_nueva, cambios, avisos). No toca el texto de ningún elemento."""
    bloques = {b['id']: b for b in hoja['bloques']}
    assert set(bloques) == set(BLOQUES), 'data/hoja_ruta.json debe tener los cuatro bloques'
    nuevos = {b: [] for b in BLOQUES}
    cambios, avisos, citados = [], [], set()
    for b in BLOQUES:
        for it in bloques[b]['items']:
            nums = it.get('issues') or []
            citados.update(nums)
            if not nums:
                nuevos[b].append(it)
                continue
            destino = bloque_de(nums, issues)
            if destino == '':
                avisos.append(f"«{it['t']}» cita un issue que no existe: {nums}")
                nuevos[b].append(it)
            elif destino is None:
                cambios.append(f"«{it['t']}»: {b} -> fuera (cerrado como «no se hará»)")
            elif destino == b:
                nuevos[b].append(it)
            else:
                it = dict(it)
                if it.get('tag') in ('en evaluación', 'propuesto', 'parcial'):
                    del it['tag']           # la etiqueta del bloque viejo ya no dice la verdad
                cambios.append(f"«{it['t']}»: {b} -> {destino}")
                nuevos[destino].append(it)
    for n, i in sorted(issues.items()):
        if n in citados or i['etiquetas'] & NUNCA:
            continue
        destino = bloque_de([n], issues)
        if destino is None:
            continue
        web = texto_web(i['cuerpo'])
        if not web:
            if i['abierto']:
                avisos.append(f'#{n} abierto sin texto para la web (bloque <!-- web … -->) ni elemento que lo cite')
            continue
        nuevos[destino].append({'t': web['t'], 'x': web['x'], 'issues': [n]})
        cambios.append(f"«{web['t']}» (#{n}): nuevo en {destino}")
    salida = dict(hoja)
    salida['bloques'] = [dict(bloques[b], items=nuevos[b]) for b in BLOQUES]
    if cambios:
        salida['actualizado'] = hoy
    return salida, cambios, avisos


def main(argv):
    hoy = argv[argv.index('--hoy') + 1] if '--hoy' in argv else datetime.date.today().isoformat()
    raw = json.load(open(argv[argv.index('--issues') + 1], encoding='utf-8')) if '--issues' in argv else leer_issues_api()
    hoja = json.load(open(HOJA, encoding='utf-8'))
    nueva, cambios, avisos = sincronizar(hoja, normalizar(raw), hoy)
    for c in cambios:
        print('cambio:', c)
    for a in avisos:
        print('aviso:', a)
    if '--comprobar' in argv:
        if cambios:
            print(f'La pantalla no está al día con los issues ({len(cambios)} cambios). Corre scripts/hoja_ruta_github.py.')
            return 1
        print('La pantalla está al día con los issues.')
        return 0
    if cambios:
        with open(HOJA, 'w', encoding='utf-8') as f:
            json.dump(nueva, f, ensure_ascii=False, indent=1)
            f.write('\n')
    print(f'{len(cambios)} cambios, {len(avisos)} avisos')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
