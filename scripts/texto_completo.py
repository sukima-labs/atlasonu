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
PAUSA = 2.0            # segundos entre descargas: no saturar a la ONU
LENGUAS = ("es", "en")
MIN_PARRAFO = 40       # caracteres; lo más corto suele ser cabecera o número de página


def ruta_db(d=None):
    return os.path.join(d or DIR, "indice.sqlite")


def slug(simbolo):
    return re.sub(r"[^A-Za-z0-9]+", "_", simbolo).strip("_")


def fuentes_por_lengua(entrada):
    """{lengua: url} prefiriendo la Biblioteca Digital (registro), luego documents.un.org (ods)."""
    orden = {"registro": 0, "ods": 1, "ohchr": 2}
    out = {}
    for f in sorted(entrada.get("fuentes", []), key=lambda f: orden.get(f.get("tipo"), 9)):
        ln, url = f.get("lengua"), (f.get("url") or "").replace("http://", "https://", 1)
        if ln in LENGUAS and ln not in out and f.get("validado") is not False and url:
            out[ln] = url
    return out


def pendientes(limite=None):
    with open(TEXTOS_JSON, encoding="utf-8") as f:
        d = json.load(f)
    sims = sorted(s for s, v in d.items() if v.get("estado") == "TEXTO_DIRECTO")
    if limite:
        sims = sims[:limite]
    return [(s, fuentes_por_lengua(d[s])) for s in sims]


def descargar(limite=None):
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
                subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, txt], check=False, timeout=120)
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
CREATE TABLE documentos (simbolo TEXT, lengua TEXT, n_parrafos INTEGER, url TEXT, PRIMARY KEY (simbolo, lengua));
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
        con.executemany("INSERT INTO parrafos VALUES (?,?,?,?)",
                        [(sim, m.group(2), i, p) for i, p in enumerate(ps, 1)])
        con.execute("INSERT OR REPLACE INTO documentos VALUES (?,?,?,?)", (sim, m.group(2), len(ps), url))
        docs += 1
    con.execute("INSERT INTO parrafos(parrafos) VALUES ('optimize')")
    con.commit()
    con.close()
    os.replace(tmp, ruta_db(d))
    print(f"índice: {docs} documentos")


def _cargar():
    try:
        with open(TEXTOS_JSON, encoding="utf-8") as f:
            d = json.load(f)
    except OSError:
        return {}, {}
    return ({slug(s): s for s in d},
            {(s, ln): u for s, v in d.items() for ln, u in fuentes_por_lengua(v).items()})


SIMBOLOS, URLS = _cargar()
INI, FIN = "\x02", "\x03"   # marcas del fragmento resaltado (no aparecen en los textos de la ONU)


def consulta_fts(q):
    """Convierte lo que escribe una persona en una consulta FTS5 segura: palabras sueltas, frases entre comillas."""
    frases = re.findall(r'"([^"]+)"', q)
    resto = re.sub(r'"[^"]*"', " ", q)
    terminos = [f'"{f.strip()}"' for f in frases if f.strip()]
    terminos += [f'"{w}"' for w in re.findall(r"\w+", resto) if len(w) > 1]
    return " ".join(terminos)


def buscar(con, q, ln=None, limite=10, por_doc=2):
    """Párrafos que contienen la consulta, los mejores primero, como mucho `por_doc` por documento y lengua."""
    fts = consulta_fts(q)
    if not fts:
        return []
    sql = ("SELECT parrafos.simbolo, parrafos.lengua, parrafos.n, snippet(parrafos, 3, ?, ?, ' … ', 40), d.url "
           "FROM parrafos LEFT JOIN documentos d ON d.simbolo = parrafos.simbolo AND d.lengua = parrafos.lengua "
           "WHERE parrafos MATCH ?" + (" AND parrafos.lengua = ?" if ln else "") + " ORDER BY bm25(parrafos) LIMIT 200")
    out, cuenta = [], {}
    for s, l, n, t, u in con.execute(sql, [INI, FIN, fts] + ([ln] if ln else [])):
        if cuenta.get((s, l), 0) >= por_doc:
            continue
        cuenta[(s, l)] = cuenta.get((s, l), 0) + 1
        out.append({"simbolo": s, "lengua": l, "parrafo": n, "fragmento": t, "url": u or ""})
        if len(out) >= limite:
            break
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["descargar", "extraer", "indexar", "todo", "buscar"])
    ap.add_argument("consulta", nargs="?")
    ap.add_argument("--limite", type=int)
    ap.add_argument("--ln", choices=LENGUAS)
    a = ap.parse_args()
    if a.accion in ("descargar", "todo"):
        descargar(a.limite)
    if a.accion in ("extraer", "todo"):
        extraer(a.limite)
    if a.accion in ("indexar", "todo"):
        indexar(a.limite)
    if a.accion == "buscar":
        con = sqlite3.connect(f"file:{ruta_db()}?mode=ro", uri=True)
        for r in buscar(con, a.consulta or "", a.ln):
            print(f"{r['simbolo']} [{r['lengua']}] §{r['parrafo']}: " + r["fragmento"].replace(INI, "«").replace(FIN, "»"))


if __name__ == "__main__":
    main()
