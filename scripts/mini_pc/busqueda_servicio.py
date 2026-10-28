#!/usr/bin/env python3
"""Servicio de búsqueda en vivo de ATLAS ONU (corre en el mini PC).

El navegador no puede leer la Biblioteca Digital ONU (no envía CORS), así que la página pregunta
aquí cuando el catálogo no encuentra nada. Escucha solo en 127.0.0.1; se publica con Tailscale Funnel.
  GET /buscar?q=<texto>[&ln=es|en]  ->  {"consulta":..., "total":N, "resultados":[{recid,simbolo,titulo,fecha,url,archivos:[{idioma,url}]}]}
Sin dependencias: solo biblioteca estándar. Caché en memoria y límite de consultas para no saturar a la ONU."""
import json, os, re, time, threading, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PUERTO = int(os.environ.get("ATLAS_BUSQUEDA_PUERTO", "8787"))
ORIGENES = {"https://sukima-labs.github.io"}
FUENTE = "https://digitallibrary.un.org/search"
TTL = 3600           # segundos que se reutiliza una respuesta
MAX_CACHE = 500
MAX_POR_MIN = 20     # consultas nuevas a la ONU por minuto (todas las visitas juntas)
UA = "ATLAS-ONU/1.0 (+https://github.com/sukima-labs/onu-arqueologia-documental)"

NS = "{http://www.loc.gov/MARC21/slim}"
_cache, _veces, _lock = {}, [], threading.Lock()


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


class H(BaseHTTPRequestHandler):
    server_version = "AtlasBusqueda"

    def _cors(self):
        o = self.headers.get("Origin", "")
        if o in ORIGENES:
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")

    def _json(self, cod, obj):
        cuerpo = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(cod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "public, max-age=600")
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
        if u.path != "/buscar":
            return self._json(404, {"error": "no existe"})
        p = urllib.parse.parse_qs(u.query)
        q = re.sub(r"\s+", " ", (p.get("q") or [""])[0]).strip()
        ln = "es" if (p.get("ln") or ["es"])[0] == "es" else "en"
        if len(q) < 2 or len(q) > 120:
            return self._json(400, {"error": "consulta inválida"})
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
