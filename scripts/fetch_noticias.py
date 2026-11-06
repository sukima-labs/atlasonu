#!/usr/bin/env python3
"""Noticias ONU (español) para la pantalla «Noticias del mundo». Escribe data/noticias.js.
Fuente: RSS público de Noticias ONU (news.un.org). Si la red falla, NO toca el archivo anterior (sale con 1).
Además acumula todo lo visto en data/noticias_archivo.json (sin duplicados, por enlace) y marca como destacadas
las que aparecen en la sección de derechos humanos de Noticias ONU."""
import datetime, gzip, html, json, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

BASE = "https://news.un.org/feed/subscribe/es/news/"
TEMAS = {
    "todas": BASE + "all/rss.xml",
    "derechos": BASE + "topic/human-rights/feed/rss.xml",
    "americas": BASE + "region/americas/feed/rss.xml",
}
UA = "ATLAS-ONU/1.0 (+https://github.com/sukima-labs/onu-arqueologia-documental)"
MAX = 20


def limpio(t, n):
    t = re.sub(r"<[^>]+>", " ", html.unescape(t or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"


def leer(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        crudo = r.read()
    if crudo[:2] == b"\x1f\x8b":
        crudo = gzip.decompress(crudo)
    raiz = ET.fromstring(crudo)
    out = []
    for it in raiz.findall(".//item"):
        enlace = (it.findtext("link") or "").strip()
        if not enlace.startswith("https://news.un.org/"):
            continue
        try:
            fecha = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception:
            continue
        enc = it.find("enclosure")
        img = enc.get("url") if enc is not None and (enc.get("url") or "").startswith("https://") else ""
        out.append({"titulo": limpio(it.findtext("title"), 200), "fecha": fecha, "enlace": enlace,
                    "resumen": limpio(it.findtext("description"), 260), "imagen": img})
    return out[:MAX]


ARCHIVO = "data/noticias_archivo.json"


def archivar(datos, ahora):
    """Suma las notas nuevas al archivo; una nota de la sección de derechos humanos queda destacada para siempre."""
    previo = {}
    if os.path.exists(ARCHIVO):
        previo = {n["enlace"]: n for n in json.load(open(ARCHIVO, encoding="utf-8"))["notas"]}
    dh = {n["enlace"] for n in datos["derechos"]}
    am = {n["enlace"] for n in datos["americas"]}
    for lista in datos.values():
        for n in lista:
            a = previo.setdefault(n["enlace"], {"titulo": n["titulo"], "fecha": n["fecha"], "enlace": n["enlace"],
                                                "resumen": n["resumen"], "visto": ahora[:10]})
            a["derechos"] = bool(a.get("derechos")) or n["enlace"] in dh
            a["americas"] = bool(a.get("americas")) or n["enlace"] in am
    notas = sorted(previo.values(), key=lambda n: (n["fecha"], n["enlace"]), reverse=True)
    cuerpo = {"fuente": "Noticias ONU (news.un.org)", "actualizado": ahora, "total": len(notas), "notas": notas}
    open(ARCHIVO, "w", encoding="utf-8").write(json.dumps(cuerpo, ensure_ascii=False, indent=0) + "\n")
    return len(notas)


def main():
    datos = {k: leer(u) for k, u in TEMAS.items()}
    if not all(datos.values()):
        print("Alguna sección de noticias llegó vacía: no se escribe nada.")
        return 1
    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dh = {n["enlace"] for n in datos["derechos"]}
    for n in datos["todas"]:
        n["destacada"] = n["enlace"] in dh
    total = archivar(datos, ahora)
    cuerpo = json.dumps({"fuente": "Noticias ONU (news.un.org)", "actualizado": ahora, "temas": datos}, ensure_ascii=False, indent=1)
    open("data/noticias.js", "w", encoding="utf-8").write("window.NOTICIAS=" + cuerpo + ";\n")
    print("Noticias:", {k: len(v) for k, v in datos.items()}, "· archivo:", total)
    return 0


sys.exit(main())
