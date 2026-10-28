#!/usr/bin/env python3
"""Noticias ONU (español) para la pantalla «Noticias del mundo». Escribe data/noticias.js.
Fuente: RSS público de Noticias ONU (news.un.org). Si la red falla, NO toca el archivo anterior (sale con 1)."""
import gzip, html, json, re, sys, urllib.request
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


def main():
    datos = {k: leer(u) for k, u in TEMAS.items()}
    if not all(datos.values()):
        print("Alguna sección de noticias llegó vacía: no se escribe nada.")
        return 1
    cuerpo = json.dumps({"fuente": "Noticias ONU (news.un.org)", "temas": datos}, ensure_ascii=False, indent=1)
    open("data/noticias.js", "w", encoding="utf-8").write("window.NOTICIAS=" + cuerpo + ";\n")
    print("Noticias:", {k: len(v) for k, v in datos.items()})
    return 0


sys.exit(main())
