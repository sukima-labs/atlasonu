#!/usr/bin/env python3
"""Documentos marco de los procedimientos especiales (comunes a todos los mandatos, p. ej. el Código de conducta).
No salen de ningún mandato concreto, así que no entran por el índice de OHCHR: se piden por símbolo exacto a la
Biblioteca Digital ONU (MARCXML, 191$a). Escribe data/fuentes/documentos_marco.json. Si algún símbolo no se localiza,
sale con 1 y NO toca el archivo anterior."""
import gzip, json, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

NS = "{http://www.loc.gov/MARC21/slim}"
UA = "ATLAS-ONU/1.0 (+https://github.com/cataplum1414/onu-arqueologia-documental)"
# símbolo -> (nombre corto, palabras clave en español para la búsqueda, informe de sesión donde está el texto adoptado)
MARCO = {
    "A/RES/60/251": ("Creación del Consejo de Derechos Humanos", "consejo de derechos humanos creacion asamblea general", None),
    "A/HRC/RES/5/1": ("Construcción institucional del Consejo (procedimientos especiales, EPU, comité asesor)", "construccion institucional institution building procedimientos especiales epu", "A/HRC/5/21"),
    "A/HRC/RES/5/2": ("Código de conducta de los titulares de mandatos", "codigo de conducta code of conduct titulares relatores independencia imparcialidad", "A/HRC/5/21"),
}


def consultar(q, ln):
    url = "https://digitallibrary.un.org/search?" + urllib.parse.urlencode({"ln": ln, "p": q, "of": "xm", "rg": 5})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
        crudo = r.read()
    if crudo[:2] == b"\x1f\x8b":
        crudo = gzip.decompress(crudo)
    return list(ET.fromstring(crudo).iter(NS + "record"))


def campo(rec, tag, code):
    for df in rec.iter(NS + "datafield"):
        if df.get("tag") == tag:
            for sf in df.iter(NS + "subfield"):
                if sf.get("code") == code and sf.text:
                    return sf.text.strip()
    return ""


def todos(rec, tag, code):
    return [sf.text.strip() for df in rec.iter(NS + "datafield") if df.get("tag") == tag
            for sf in df.iter(NS + "subfield") if sf.get("code") == code and sf.text]


def pdfs(rec):
    out = {}
    for df in rec.iter(NS + "datafield"):
        if df.get("tag") == "856":
            sf = {s.get("code"): (s.text or "").strip() for s in df.iter(NS + "subfield")}
            m = re.search(r"-([A-Z]{2})\.pdf$", sf.get("u", ""))
            if m and sf["u"].startswith("https://digitallibrary.un.org/"):
                out[m.group(1).lower()] = sf["u"]
    return out


def exacto(simbolo, ln):
    for rec in consultar('191__a:"%s"' % simbolo, ln):
        if campo(rec, "191", "a") == simbolo:
            return rec
    return None


def main():
    salida = {}
    for sim, (nombre, claves, informe) in MARCO.items():
        en, es = exacto(sim, "en"), exacto(sim, "es")
        if en is None:
            print("No se localiza", sim)
            return 1
        recid = next(c.text for c in en.iter(NS + "controlfield") if c.get("tag") == "001")
        borr = todos(en, "993", "a")
        reg = {
            "simbolo": sim, "nombre": nombre, "claves": claves,
            "titulo": " ".join(p.strip(" :/") for p in (campo(en, "245", "a"), campo(en, "245", "b")) if p),
            "titulo_es": " ".join(p.strip(" :/") for p in (campo(es, "245", "a"), campo(es, "245", "b")) if p) if es is not None else "",
            "adoptada": campo(en, "269", "a"), "votacion": "",
            "registro": "https://digitallibrary.un.org/record/" + recid,
            "pdf": pdfs(en), "borradores": borr, "informe_sesion": None,
        }
        if informe:
            ri = exacto(informe, "en")
            if ri is None:
                print("No se localiza el informe", informe)
                return 1
            reg["informe_sesion"] = {"simbolo": informe, "registro": "https://digitallibrary.un.org/record/" + next(c.text for c in ri.iter(NS + "controlfield") if c.get("tag") == "001"), "pdf": pdfs(ri)}
        salida[sim] = reg
    json.dump({"fuente": "Biblioteca Digital ONU (consulta por símbolo exacto)", "documentos": salida},
              open("data/fuentes/documentos_marco.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Documentos marco:", ", ".join(salida))
    return 0


sys.exit(main())
