"""T56 · Acceso a la Biblioteca Digital de la ONU por registro concreto (/record/N?of=xm, MARCXML).

Su robots.txt prohíbe /search (y /rss y /record/*/export/*), así que ningún script de ATLAS busca ahí: los registros
que se leen están anotados. Los que ya están en los datos se conservan; uno nuevo se añade a mano (número de registro)
en data/fuentes/registros_biblioteca.json, bajo el nombre del script, y el script lo baja y lo clasifica.
Crawl-Delay de 5 s y de uno en uno. Nunca a la vez que otro cliente (texto_completo.py corre a las 03:30)."""
import gzip, json, os, time, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'ATLAS-ONU/1.0 (+https://github.com/sukima-labs/atlasonu)'}
CADA = 5.0
NUEVOS = os.path.join(RAIZ, 'data', 'fuentes', 'registros_biblioteca.json')
_ultima = [0.0]


def marc(n, tries=3):
    """MARCXML de un registro (texto). Respeta el Crawl-Delay entre peticiones."""
    n = str(n).strip()
    if not n.isdigit():
        raise ValueError('número de registro no válido: %r' % n)
    url = 'https://digitallibrary.un.org/record/%s?of=xm' % n
    err = None
    for k in range(tries):
        espera = _ultima[0] + CADA - time.time()
        if espera > 0:
            time.sleep(espera)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                crudo = r.read()
            _ultima[0] = time.time()
            if crudo[:2] == b'\x1f\x8b':
                crudo = gzip.decompress(crudo)
            return crudo.decode('utf-8', 'ignore')
        except Exception as e:
            _ultima[0] = time.time(); err = e; time.sleep(CADA * (k + 1))
    raise RuntimeError('red (registro %s): %s' % (n, err))


def nuevos(script):
    """Números de registro anotados a mano para `script` (sin duplicados, en orden)."""
    try:
        d = json.load(open(NUEVOS, encoding='utf-8'))
    except FileNotFoundError:
        return []
    return list(dict.fromkeys(str(x) for x in d.get(script, [])))
