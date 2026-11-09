#!/usr/bin/env python3
"""Texto completo de las resoluciones de ATLAS ONU: descarga, extracción e índice.

Toma las rutas al texto ya verificadas (`data/fuentes/textos.json`), descarga los PDF oficiales en español e
inglés, extrae el texto con `pdftotext` (poppler, libre) y lo trocea en párrafos dentro de un índice SQLite FTS5.
La búsqueda en vivo (`scripts/mini_pc/busqueda_servicio.py`, ruta `/texto`) consulta ese índice.

Nada de esto va al repositorio: PDF, textos e índice viven en ATLAS_TEXTOS_DIR (por defecto
~/.local/share/atlas-onu/textos). Solo biblioteca estándar + pdftotext.

  python3 scripts/texto_completo.py todo [--limite N]   # descargar + extraer + indexar
  python3 scripts/texto_completo.py descargar|extraer|indexar [--limite N]
  python3 scripts/texto_completo.py buscar "visitas sin previo aviso" [--ln es]
"""
import argparse, json, os, re, sqlite3, subprocess, sys, tempfile, time, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTOS_JSON = os.path.join(RAIZ, "data", "fuentes", "textos.json")
DIR = os.environ.get("ATLAS_TEXTOS_DIR", os.path.expanduser("~/.local/share/atlas-onu/textos"))
UA = "ATLAS-ONU/1.0 (+https://github.com/sukima-labs/atlasonu)"
PAUSA = 5.0            # segundos entre descargas: el Crawl-Delay del robots.txt de la Biblioteca Digital
LENGUAS = ("es", "en")
MIN_PARRAFO = 40       # caracteres; lo más corto suele ser cabecera o número de página


def ruta_db(d=None):
    return os.path.join(d or DIR, "indice.sqlite")


def slug(simbolo):
    return re.sub(r"[^A-Za-z0-9]+", "_", simbolo).strip("_")


def fuentes_por_lengua(entrada):
    """{lengua: url} de la Biblioteca Digital, solo si el fichero es de esa lengua (…-ES.pdf / …-EN.pdf).
    documents.un.org no: su robots.txt prohíbe /api. Lo que no cumple, se queda fuera (no se adivina)."""
    out = {}
    for f in entrada.get("fuentes", []):
        ln, url = f.get("lengua"), (f.get("url") or "").replace("http://", "https://", 1)
        if (ln in LENGUAS and ln not in out and f.get("validado") is not False
                and url.startswith("https://digitallibrary.un.org/record/")
                and re.search(r"-" + ln.upper() + r"\.pdf$", url, re.I)):
            out[ln] = url
    return out


PAISES_DIR = os.path.join(RAIZ, "data", "paises")
TIPOS_PAIS = {"co": "Observaciones finales", "epu": "Examen Periódico Universal", "visitas": "Informe de visita"}


def _docs_pais():
    """Documentos por país (data/paises/<ISO>.js): observaciones finales, EPU e informes de visita."""
    out = []
    for f in sorted(os.listdir(PAISES_DIR)) if os.path.isdir(PAISES_DIR) else []:
        if not f.endswith(".js"):
            continue
        s = open(os.path.join(PAISES_DIR, f), encoding="utf-8").read()
        try:
            d = json.loads(s[s.index("]=") + 2:].rstrip().rstrip(";"))
        except ValueError:
            continue
        for cat, tipo in TIPOS_PAIS.items():
            for x in d.get(cat, []):
                urls = fuentes_por_lengua({"fuentes": [{"lengua": ln, "url": x[ln]} for ln in LENGUAS if x.get(ln)]})
                if x.get("s") and urls:
                    out.append((x["s"], {"tipo": tipo, "titulo": x.get("t", ""), "pais": f[:-3], "fecha": x.get("d", ""),
                                         "urls": urls}))
    return out


def catalogo():
    """{símbolo: {tipo, titulo, pais, fecha, urls{lengua: url}}}: resoluciones primero, luego lo más reciente."""
    cat = {}
    try:
        with open(TEXTOS_JSON, encoding="utf-8") as f:
            d = json.load(f)
    except OSError:
        d = {}
    for s in sorted(d):
        urls = fuentes_por_lengua(d[s])
        if d[s].get("estado") == "TEXTO_DIRECTO" and urls:
            cat[s] = {"tipo": "Resolución", "titulo": "", "pais": "", "fecha": "", "urls": urls}
    for s, v in sorted(_docs_pais(), key=lambda x: x[1]["fecha"], reverse=True):
        cat.setdefault(s, v)
    return cat


def pendientes(limite=None):
    items = list(CATALOGO.items())
    return [(s, v["urls"]) for s, v in (items[:limite] if limite else items)]


def descargar(limite=None, cada=0, al_avanzar=None):
    """Baja lo que falta. Con `cada`, llama a `al_avanzar()` cada tantos PDF nuevos (para ir indexando)."""
    os.makedirs(os.path.join(DIR, "pdf"), exist_ok=True)
    nuevos = fallos = 0
    for sim, urls in pendientes(limite):
        for ln, url in urls.items():
            dest = os.path.join(DIR, "pdf", f"{slug(sim)}-{ln}.pdf")
            if os.path.exists(dest):
                continue
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as r:
                    datos = r.read()
                if not datos.startswith(b"%PDF"):
                    raise ValueError("no es un PDF")
                fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dest))
                with os.fdopen(fd, "wb") as f:
                    f.write(datos)
                os.replace(tmp, dest)
                nuevos += 1
                if cada and al_avanzar and nuevos % cada == 0:
                    al_avanzar()
            except Exception as e:
                fallos += 1
                print(f"  fallo {sim} [{ln}]: {e}", file=sys.stderr)
            time.sleep(PAUSA)
    print(f"descarga: {nuevos} nuevos, {fallos} fallos")


def extraer(limite=None):
    os.makedirs(os.path.join(DIR, "txt"), exist_ok=True)
    hechos = 0
    for sim, urls in pendientes(limite):
        for ln in urls:
            pdf = os.path.join(DIR, "pdf", f"{slug(sim)}-{ln}.pdf")
            txt = os.path.join(DIR, "txt", f"{slug(sim)}-{ln}.txt")
            if os.path.exists(pdf) and not os.path.exists(txt):
                subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, txt], check=False, timeout=120,
                               stderr=subprocess.DEVNULL)
                hechos += 1
    print(f"extracción: {hechos} textos")


_RUIDO = re.compile(r"^(GE\.\d|\*\d{5,}|Distr\.|Original:|Página \d|Page \d|\d{1,3}$|[A-Z]/[A-Z0-9./]+$)")


def parrafos(texto):
    """Trocea el texto de pdftotext en párrafos: une líneas, quita cabeceras y números de página."""
    bloques, actual = [], []
    for linea in texto.replace("\f", "\n\n").splitlines():
        l = linea.strip()
        if not l:
            if actual:
                bloques.append(" ".join(actual))
                actual = []
            continue
        if _RUIDO.match(l):
            continue
        actual.append(l)
    if actual:
        bloques.append(" ".join(actual))
    out = []
    for b in bloques:
        b = re.sub(r"(\w)- (\w)", r"\1\2", re.sub(r"\s+", " ", b)).strip()
        if len(b) >= MIN_PARRAFO:
            out.append(b)
    return out


ESQUEMA = """
CREATE VIRTUAL TABLE parrafos USING fts5(
  simbolo UNINDEXED, lengua UNINDEXED, n UNINDEXED, texto,
  tokenize = "unicode61 remove_diacritics 2");
CREATE TABLE documentos (simbolo TEXT, lengua TEXT, n_parrafos INTEGER, url TEXT,
  tipo TEXT, titulo TEXT, pais TEXT, fecha TEXT, PRIMARY KEY (simbolo, lengua));
CREATE TABLE vectores (id INTEGER PRIMARY KEY, v BLOB);   -- id = rowid del párrafo; vacía si no hay modelo
"""


def indexar(limite=None, d=None):
    """Reconstruye el índice entero en un fichero nuevo y lo cambia de golpe (el servicio nunca ve uno a medias)."""
    d = d or DIR
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".sqlite")
    os.close(fd)
    os.unlink(tmp)
    con = sqlite3.connect(tmp)
    con.executescript(ESQUEMA)
    docs = 0
    txtdir = os.path.join(d, "txt")
    for nombre in sorted(os.listdir(txtdir)) if os.path.isdir(txtdir) else []:
        m = re.fullmatch(r"(.+)-(es|en)\.txt", nombre)
        if not m:
            continue
        with open(os.path.join(txtdir, nombre), encoding="utf-8", errors="replace") as f:
            ps = parrafos(f.read())
        sim = SIMBOLOS.get(m.group(1), m.group(1))
        url = URLS.get((sim, m.group(2)), "")
        if URLS and not url:   # ya no es una fuente admisible (p. ej. venía de documents.un.org): fuera
            continue
        con.executemany("INSERT INTO parrafos VALUES (?,?,?,?)",
                        [(sim, m.group(2), i, p) for i, p in enumerate(ps, 1)])
        meta = CATALOGO.get(sim, {})
        con.execute("INSERT OR REPLACE INTO documentos VALUES (?,?,?,?,?,?,?,?)",
                    (sim, m.group(2), len(ps), url, meta.get("tipo", ""), meta.get("titulo", ""), meta.get("pais", ""),
                     meta.get("fecha", "")))
        docs += 1
    con.execute("INSERT INTO parrafos(parrafos) VALUES ('optimize')")
    con.commit()
    vectorizar(con, d)
    con.close()
    os.replace(tmp, ruta_db(d))
    print(f"índice: {docs} documentos")


CATALOGO = catalogo()
SIMBOLOS = {slug(s): s for s in CATALOGO}
URLS = {(s, ln): u for s, v in CATALOGO.items() for ln, u in v["urls"].items()}
INI, FIN = "\x02", "\x03"   # marcas del fragmento resaltado (no aparecen en los textos de la ONU)


def consulta_fts(q, o=False):
    """Convierte lo que escribe una persona en una consulta FTS5 segura: palabras sueltas, frases entre comillas.
    Con o=True, cualquiera de las palabras con contenido (para preguntas largas)."""
    frases = re.findall(r'"([^"]+)"', q)
    resto = re.sub(r'"[^"]*"', " ", q)
    terminos = [f'"{f.strip()}"' for f in frases if f.strip()]
    if o:
        terminos += [f'"{w}"' for w in palabras(resto)]
        return " OR ".join(terminos)
    terminos += [f'"{w}"' for w in re.findall(r"\w+", resto) if len(w) > 1]
    return " ".join(terminos)


def _meta(m):
    return dict(zip(("tipo", "titulo", "pais", "fecha"), (x or "" for x in m)))


def buscar(con, q, ln=None, limite=10, por_doc=2, o=False):
    """Párrafos que contienen la consulta, los mejores primero, como mucho `por_doc` por documento y lengua.
    Si ningún párrafo tiene todas las palabras, se reintenta con cualquiera de ellas."""
    fts = consulta_fts(q, o)
    if not fts:
        return []
    sql = ("SELECT parrafos.simbolo, parrafos.lengua, parrafos.n, snippet(parrafos, 3, ?, ?, ' … ', 40), d.url, "
           "d.tipo, d.titulo, d.pais, d.fecha "
           "FROM parrafos LEFT JOIN documentos d ON d.simbolo = parrafos.simbolo AND d.lengua = parrafos.lengua "
           "WHERE parrafos MATCH ?" + (" AND parrafos.lengua = ?" if ln else "") + " ORDER BY bm25(parrafos) LIMIT 200")
    out, cuenta = [], {}
    for s, l, n, t, u, *meta in con.execute(sql, [INI, FIN, fts] + ([ln] if ln else [])):
        if cuenta.get((s, l), 0) >= por_doc:
            continue
        cuenta[(s, l)] = cuenta.get((s, l), 0) + 1
        out.append({"simbolo": s, "lengua": l, "parrafo": n, "fragmento": t, "url": u or "", **_meta(meta)})
        if len(out) >= limite:
            break
    if not out and not o and len(palabras(q)) > 1:
        return buscar(con, q, ln, limite, por_doc, o=True)
    return out


# ---------------------------------------------------------------------------------------------------------------
# Búsqueda por significado (fase 2). Opcional: si no están fastembed y numpy (entorno /opt/atlas-venv), todo sigue
# funcionando solo con palabras. Modelo libre (Apache-2.0), en local, en CPU: no se envía nada a terceros.
MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODELOS_DIR = os.environ.get("ATLAS_MODELOS_DIR", os.path.expanduser("~/modelos"))
try:
    import warnings
    warnings.filterwarnings("ignore", message=".*mean pooling.*")
    import numpy as np
    from fastembed import TextEmbedding
except ImportError:            # sin entorno semántico
    np = TextEmbedding = None
UMBRAL = 0.5   # coseno mínimo para que un párrafo entre solo por significado
_modelo, _vecs, _mlock = None, {}, __import__("threading").Lock()


def semantica_disponible():
    return TextEmbedding is not None and os.path.isdir(MODELOS_DIR)


def _emb(textos):
    global _modelo
    with _mlock:
        if _modelo is None:
            _modelo = TextEmbedding(MODELO, cache_dir=MODELOS_DIR, local_files_only=True, threads=os.cpu_count())
    m = np.array(list(_modelo.embed(textos, batch_size=32)), dtype=np.float32)
    return m / np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-9)


def vectorizar(con, d):
    """Guarda el vector de cada párrafo dentro del mismo índice. Reutiliza los ya calculados (caché por texto)."""
    if not semantica_disponible():
        print("semántica: sin modelo, solo palabras")
        return
    import hashlib
    cache = sqlite3.connect(os.path.join(d, "vectores_cache.sqlite"))
    cache.execute("CREATE TABLE IF NOT EXISTS c (h TEXT PRIMARY KEY, v BLOB)")
    filas = con.execute("SELECT rowid, texto FROM parrafos").fetchall()
    hs = [hashlib.sha1((MODELO + t).encode()).hexdigest() for _, t in filas]
    tengo = {}
    for i in range(0, len(hs), 500):
        lote = hs[i:i + 500]
        tengo.update(cache.execute(f"SELECT h, v FROM c WHERE h IN ({','.join('?' * len(lote))})", lote).fetchall())
    faltan = [(i, filas[i][1]) for i, h in enumerate(hs) if h not in tengo]
    for k in range(0, len(faltan), 256):
        lote = faltan[k:k + 256]
        for (i, _), v in zip(lote, _emb([t for _, t in lote])):
            tengo[hs[i]] = v.tobytes()
            cache.execute("INSERT OR REPLACE INTO c VALUES (?,?)", (hs[i], tengo[hs[i]]))
        cache.commit()
    con.executemany("INSERT INTO vectores VALUES (?,?)", [(filas[i][0], tengo[h]) for i, h in enumerate(hs)])
    con.commit()
    cache.close()
    print(f"semántica: {len(filas)} párrafos ({len(faltan)} nuevos)")


def _matriz(con, clave):
    """Vectores del índice en memoria; se recargan cuando el índice cambia (clave = mtime del fichero)."""
    if _vecs.get("clave") != clave:
        filas = con.execute("SELECT id, v FROM vectores ORDER BY id").fetchall()
        _vecs.update(clave=clave, ids=np.array([i for i, _ in filas], dtype=np.int64),
                     m=np.frombuffer(b"".join(v for _, v in filas), dtype=np.float32).reshape(len(filas), -1).astype(np.float16)
                     if filas else np.zeros((0, 384), np.float32))
    return _vecs["ids"], _vecs["m"]


def buscar_hibrido(con, q, ln=None, limite=10, por_doc=2, clave=None):
    """Palabras (BM25) + significado (coseno), mezclados por rango recíproco. Sin modelo, igual que buscar()."""
    if not semantica_disponible():
        return buscar(con, q, ln, limite, por_doc)
    ids, m = _matriz(con, clave)
    if not len(ids):
        return buscar(con, q, ln, limite, por_doc)
    rr = {}
    fts = consulta_fts(q, o=len(palabras(q)) > 1)
    if fts:
        sql = ("SELECT rowid FROM parrafos WHERE parrafos MATCH ?" + (" AND lengua = ?" if ln else "") +
               " ORDER BY bm25(parrafos) LIMIT 100")
        for r, (pid,) in enumerate(con.execute(sql, [fts] + ([ln] if ln else []))):
            rr[pid] = rr.get(pid, 0) + 1 / (60 + r)
    sim = (m @ _emb([q])[0].astype(np.float16)).astype(np.float32)
    for r, j in enumerate(np.argsort(-sim)[:100]):
        if sim[j] >= UMBRAL:
            rr[int(ids[j])] = rr.get(int(ids[j]), 0) + 1 / (60 + r)
    out, cuenta = [], {}
    for pid in sorted(rr, key=rr.get, reverse=True):
        fila = con.execute(
            "SELECT p.simbolo, p.lengua, p.n, p.texto, d.url, d.tipo, d.titulo, d.pais, d.fecha "
            "FROM parrafos p LEFT JOIN documentos d "
            "ON d.simbolo = p.simbolo AND d.lengua = p.lengua WHERE p.rowid = ?", (pid,)).fetchone()
        s, l, n, t, u, *meta = fila
        if (ln and l != ln) or cuenta.get((s, l), 0) >= por_doc:
            continue
        cuenta[(s, l)] = cuenta.get((s, l), 0) + 1
        out.append({"simbolo": s, "lengua": l, "parrafo": n, "fragmento": _resaltar(t, q), "url": u or "",
                    "por_significado": not _contiene(t, q), **_meta(meta)})
        if len(out) >= limite:
            break
    return out


def _sin_tildes(x):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", x.lower()) if unicodedata.category(c) != "Mn")


VACIAS = set("""de del la las el los un una unos unas y o u e a al en con sin por para que se su sus lo le les como
mas pero sobre entre the of and or to in on for with by an as at from is are be its this that""".split())


def palabras(q):
    """Palabras con contenido de la consulta (sin tildes, sin artículos ni preposiciones)."""
    return [w for w in (_sin_tildes(x) for x in re.findall(r"\w{3,}", q)) if w not in VACIAS]


def _contiene(t, q):
    tt = _sin_tildes(t)
    return any(re.search(r"\b" + re.escape(w), tt) for w in palabras(q))


def _resaltar(t, q, ancho=320):
    """Recorta el párrafo alrededor de la primera palabra buscada y la marca; si no aparece, el principio."""
    tt, ps = _sin_tildes(t), palabras(q)
    pos = min([m.start() for m in (re.search(r"\b" + re.escape(w), tt) for w in ps) if m] or [0])
    ini = max(0, pos - ancho // 3)
    frag = ("… " if ini else "") + t[ini:ini + ancho] + (" …" if ini + ancho < len(t) else "")
    for w in sorted(set(ps), key=len, reverse=True):
        fs = _sin_tildes(frag)   # misma longitud que frag: las tildes se quitan carácter a carácter
        if len(fs) != len(frag):
            break
        out, k = [], 0
        for mt in re.finditer(r"\b" + re.escape(w) + (r"\w*" if len(w) >= 5 else r"\b"), fs):
            out += [frag[k:mt.start()], INI, frag[mt.start():mt.end()], FIN]
            k = mt.end()
        frag = "".join(out) + frag[k:]
    return frag


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["descargar", "extraer", "indexar", "todo", "buscar"])
    ap.add_argument("consulta", nargs="?")
    ap.add_argument("--limite", type=int)
    ap.add_argument("--ln", choices=LENGUAS)
    a = ap.parse_args()
    if a.accion == "descargar":
        descargar(a.limite)
    if a.accion == "todo":   # la primera descarga dura horas: se va indexando cada 300 PDF nuevos
        descargar(a.limite, cada=300, al_avanzar=lambda: (extraer(a.limite), indexar(a.limite)))
    if a.accion in ("extraer", "todo"):
        extraer(a.limite)
    if a.accion in ("indexar", "todo"):
        indexar(a.limite)
    if a.accion == "buscar":
        con = sqlite3.connect(f"file:{ruta_db()}?mode=ro", uri=True)
        for r in buscar_hibrido(con, a.consulta or "", a.ln, clave=os.path.getmtime(ruta_db())):
            print(f"{r['simbolo']} [{r['lengua']}] §{r['parrafo']}: " + r["fragmento"].replace(INI, "«").replace(FIN, "»"))


if __name__ == "__main__":
    main()
