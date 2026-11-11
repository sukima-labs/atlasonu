#!/usr/bin/env python3
"""Servicio de búsqueda en vivo de ATLAS ONU (corre en sk-atlas, el servidor de sukima-labs).

El navegador no puede leer la Biblioteca Digital ONU (no envía CORS), así que la página pregunta
aquí cuando el catálogo no encuentra nada. Escucha solo en 127.0.0.1; se publica con Tailscale Funnel.
  GET /buscar?q=<texto>[&ln=es|en]  ->  {"consulta":..., "total":N, "resultados":[{recid,simbolo,titulo,fecha,url,archivos:[{idioma,url}]}]}
  GET /texto?q=<texto>[&ln=es|en]   ->  {"consulta":..., "total":N, "documentos":D, "resultados":[{simbolo,lengua,parrafo,fragmento,url,por_significado}]}
                                       párrafos del texto completo de las resoluciones (índice de scripts/texto_completo.py;
                                       el fragmento marca lo encontrado entre \x02 y \x03). Con /opt/atlas-venv (fastembed) mezcla
                                       palabras y significado; sin él, solo palabras. 503 si aún no hay índice.
  GET /preguntar?q=<pregunta>       ->  {"respuesta","citas":[n…],"parrafos":[…],"modelo","motivo"}: respuesta con citas
                                       redactada por IA (OpenCode Go) SOLO con párrafos del índice. Solo si el Origin es
                                       la página; 503 sin clave o sin índice; 429 si se pasa el límite global.
  GET /visitas?pais=XX              ->  {"total":N, "pais":M}              (solo lee)
  GET /visita?pais=XX               ->  igual, pero suma una visita        (solo si el Origin es la página)
El contador guarda únicamente dos números agregados (total y por código de país): ni IP, ni cookies, ni identificadores.
Sin dependencias: solo biblioteca estándar. Caché en memoria y límite de consultas para no saturar a la ONU."""
import json, os, re, sqlite3, sys, tempfile, time, threading, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PUERTO = int(os.environ.get("ATLAS_BUSQUEDA_PUERTO", "8787"))
ORIGENES = {"https://sukima-labs.github.io", "https://sukimalabs.com", "https://www.sukimalabs.com"}   # 11-11-2026: la web pasa a sukimalabs.com/atlasonu/ (la antigua redirige con 301)
FUENTE = "https://digitallibrary.un.org/search"
TTL = 3600           # segundos que se reutiliza una respuesta
MAX_CACHE = 500
MAX_POR_MIN = 20     # consultas nuevas a la ONU por minuto (todas las visitas juntas)
UA = "ATLAS-ONU/1.0 (+https://github.com/sukima-labs/atlasonu)"

VISITAS_ARCHIVO = os.environ.get("ATLAS_VISITAS_ARCHIVO", os.path.expanduser("~/.local/share/atlas-onu/visitas.json"))
MAX_VISITAS_POR_MIN = 120   # tope global de visitas sumadas por minuto (frena abusos sin identificar a nadie)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import texto_completo  # noqa: E402  (scripts/texto_completo.py)
import preguntar  # noqa: E402  (scripts/preguntar.py)

NS = "{http://www.loc.gov/MARC21/slim}"
_cache, _veces, _lock = {}, [], threading.Lock()
_vis_lock, _vis_veces = threading.Lock(), []


def _leer_visitas():
    try:
        with open(VISITAS_ARCHIVO, encoding="utf-8") as f:
            d = json.load(f)
        return {"total": int(d.get("total", 0)), "paises": {k: int(v) for k, v in d.get("paises", {}).items()}}
    except (OSError, ValueError, AttributeError):
        return {"total": 0, "paises": {}}


def visitas(pais, sumar):
    """Devuelve {"total", "pais"}; si sumar, incrementa ambos y guarda de forma atómica."""
    pais = pais if re.fullmatch(r"[A-Z]{2}", pais or "") else "XX"
    with _vis_lock:
        d = _leer_visitas()
        ahora = time.time()
        _vis_veces[:] = [t for t in _vis_veces if ahora - t < 60]
        if sumar and len(_vis_veces) < MAX_VISITAS_POR_MIN:
            _vis_veces.append(ahora)
            d["total"] += 1
            d["paises"][pais] = d["paises"].get(pais, 0) + 1
            os.makedirs(os.path.dirname(VISITAS_ARCHIVO), exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(VISITAS_ARCHIVO))
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(d, f)
            os.replace(tmp, VISITAS_ARCHIVO)
        return {"total": d["total"], "pais": d["paises"].get(pais, 0)}


def consultar(q, ln):
    clave = (q.lower(), ln)
    ahora = time.time()
    with _lock:
        hit = _cache.get(clave)
        if hit and ahora - hit[0] < TTL:
            return hit[1]
        _veces[:] = [t for t in _veces if ahora - t < 60]
        if len(_veces) >= MAX_POR_MIN:
            raise RuntimeError("limite")
        _veces.append(ahora)
    url = FUENTE + "?" + urllib.parse.urlencode({"ln": ln, "p": q, "of": "xm", "rg": 12})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        raiz = ET.fromstring(r.read())
    res = [x for x in (normalizar(rec) for rec in raiz.iter(NS + "record")) if x]
    salida = {"consulta": q, "total": len(res), "resultados": res}
    with _lock:
        if len(_cache) >= MAX_CACHE:
            _cache.clear()
        _cache[clave] = (ahora, salida)
    return salida


def campo(rec, tag, code):
    for df in rec.iter(NS + "datafield"):
        if df.get("tag") == tag:
            for sf in df.iter(NS + "subfield"):
                if sf.get("code") == code and sf.text:
                    return sf.text.strip()
    return ""


def normalizar(rec):
    recid = next((c.text for c in rec.iter(NS + "controlfield") if c.get("tag") == "001"), "")
    if not recid:
        return None
    titulo = " ".join(p.strip(" :/") for p in (campo(rec, "245", "a"), campo(rec, "245", "b")) if p)
    archivos, vistos = [], set()
    for df in rec.iter(NS + "datafield"):
        if df.get("tag") == "856":
            sf = {s.get("code"): (s.text or "").strip() for s in df.iter(NS + "subfield")}
            u = sf.get("u", "")
            if u.startswith("https://digitallibrary.un.org/") and u.lower().endswith(".pdf") and u not in vistos:
                vistos.add(u)
                archivos.append({"idioma": sf.get("y") or "PDF", "url": u})
    return {
        "recid": int(recid),
        "simbolo": campo(rec, "191", "a"),
        "titulo": titulo or "(sin título en el registro)",
        "fecha": campo(rec, "269", "a") or campo(rec, "260", "c"),
        "url": "https://digitallibrary.un.org/record/" + recid,
        "archivos": archivos[:6],
    }


def buscar_texto(q, ln):
    """Consulta el índice local (solo lectura); no toca la red. Devuelve None si aún no hay índice."""
    db = texto_completo.ruta_db()
    if not os.path.exists(db):
        return None
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        res = texto_completo.buscar_hibrido(con, q, ln, clave=os.path.getmtime(db))
        docs = con.execute("SELECT COUNT(DISTINCT simbolo) FROM documentos").fetchone()[0]
    finally:
        con.close()
    return {"consulta": q, "total": len(res), "documentos": docs, "semantica": texto_completo.semantica_disponible(),
            "resultados": res}


def preguntar_docs(q):
    db = texto_completo.ruta_db()
    if not os.path.exists(db) or not preguntar.disponible():
        return None
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return preguntar.responder(con, q, clave=os.path.getmtime(db))
    finally:
        con.close()


class H(BaseHTTPRequestHandler):
    server_version = "AtlasBusqueda"

    def _cors(self):
        o = self.headers.get("Origin", "")
        if o in ORIGENES:
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")

    def _json(self, cod, obj, cache="public, max-age=600"):
        cuerpo = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(cod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", cache)
        self._cors()
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "GET")
        # Chrome exige este permiso si el visitante resuelve el servicio a una IP privada (p. ej. con Tailscale activo)
        if self.headers.get("Access-Control-Request-Private-Network") == "true":
            self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/salud":
            return self._json(200, {"ok": True})
        if u.path in ("/visita", "/visitas"):
            pais = (urllib.parse.parse_qs(u.query).get("pais") or [""])[0].upper()
            # solo suma si la petición viene de la página (el navegador envía Origin); abrir la URL a mano no suma
            sumar = u.path == "/visita" and self.headers.get("Origin", "") in ORIGENES
            return self._json(200, visitas(pais, sumar), cache="no-store")
        if u.path == "/preguntar":
            q = re.sub(r"\s+", " ", (urllib.parse.parse_qs(u.query).get("q") or [""])[0]).strip()
            if self.headers.get("Origin", "") not in ORIGENES and not os.environ.get("ATLAS_PREGUNTAR_SIN_ORIGEN"):
                return self._json(403, {"error": "solo desde la página"}, cache="no-store")
            if len(q) < 8 or len(q) > 300:
                return self._json(400, {"error": "pregunta inválida"}, cache="no-store")
            try:
                r = preguntar_docs(q)
            except RuntimeError:
                return self._json(429, {"error": "demasiadas preguntas; inténtalo en un minuto"}, cache="no-store")
            except Exception:
                return self._json(502, {"error": "el servicio de IA no respondió"}, cache="no-store")
            if r is None:
                return self._json(503, {"error": "no disponible"}, cache="no-store")
            return self._json(200, r, cache="no-store")
        if u.path not in ("/buscar", "/texto"):
            return self._json(404, {"error": "no existe"})
        p = urllib.parse.parse_qs(u.query)
        q = re.sub(r"\s+", " ", (p.get("q") or [""])[0]).strip()
        ln = "es" if (p.get("ln") or ["es"])[0] == "es" else "en"
        if len(q) < 2 or len(q) > 120:
            return self._json(400, {"error": "consulta inválida"})
        if u.path == "/texto":
            ln_t = (p.get("ln") or [""])[0]
            try:
                r = buscar_texto(q, ln_t if ln_t in ("es", "en") else None)
            except sqlite3.Error:
                return self._json(400, {"error": "consulta inválida"})
            return self._json(503, {"error": "índice en preparación"}, cache="no-store") if r is None else self._json(200, r)
        try:
            self._json(200, consultar(q, ln))
        except RuntimeError:
            self._json(429, {"error": "demasiadas consultas; inténtalo en un minuto"})
        except Exception:
            self._json(502, {"error": "la Biblioteca Digital no respondió"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PUERTO), H).serve_forever()
