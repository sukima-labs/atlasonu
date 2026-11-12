#!/usr/bin/env python3
"""Documentos marco de los procedimientos especiales (comunes a todos los mandatos, p. ej. el Código de conducta).
No salen de ningún mandato concreto, así que no entran por el índice de OHCHR. T56: la Biblioteca Digital prohíbe
/search, así que no se buscan por símbolo: se baja su registro anotado (/record/N, MARCXML, 5 s) y se comprueba que el
símbolo (191$a) coincide. Escribe data/fuentes/documentos_marco.json. Si algún símbolo no se localiza,
sale con 1 y NO toca el archivo anterior."""
import json, os, re, sys
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import biblioteca as B

NS = "{http://www.loc.gov/MARC21/slim}"
# símbolo -> (nombre corto, palabras clave en español para la búsqueda, informe de sesión donde está el texto adoptado)
# Números de registro de la Biblioteca Digital (/record/N) de cada símbolo, anotados a mano (T56).
REGISTRO = {"A/RES/60/251": "571575", "A/HRC/RES/5/1": "603041", "A/HRC/RES/5/2": "603044", "A/HRC/5/21": "610953"}
MARCO = {
    "A/RES/60/251": ("Creación del Consejo de Derechos Humanos", "consejo de derechos humanos creacion asamblea general", None),
    "A/HRC/RES/5/1": ("Construcción institucional del Consejo (procedimientos especiales, EPU, comité asesor)", "construccion institucional institution building procedimientos especiales epu", "A/HRC/5/21"),
    "A/HRC/RES/5/2": ("Código de conducta de los titulares de mandatos", "codigo de conducta code of conduct titulares relatores independencia imparcialidad", "A/HRC/5/21"),
}


def registro(n):
    return next(ET.fromstring(B.marc(n).encode("utf-8")).iter(NS + "record"))


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


def exacto(simbolo):
    """El registro anotado de `simbolo`, si de verdad lleva ese símbolo."""
    rec = registro(REGISTRO[simbolo])
    return rec if simbolo in todos(rec, "191", "a") else None


def main():
    salida = {}
    for sim, (nombre, claves, informe) in MARCO.items():
        en = exacto(sim)
        if en is None:
            print("No se localiza", sim)
            return 1
        recid = next(c.text for c in en.iter(NS + "controlfield") if c.get("tag") == "001")
        borr = todos(en, "993", "a")
        reg = {
            "simbolo": sim, "nombre": nombre, "claves": claves,
            "titulo": " ".join(p.strip(" :/") for p in (campo(en, "245", "a"), campo(en, "245", "b")) if p),
            "titulo_es": " ".join(p.strip(" :/") for p in (campo(en, "245", "a"), campo(en, "245", "b")) if p),  # el catálogo solo da el título en inglés
            "adoptada": campo(en, "269", "a"), "votacion": "",
            "registro": "https://digitallibrary.un.org/record/" + recid,
            "pdf": pdfs(en), "borradores": borr, "informe_sesion": None,
        }
        if informe:
            ri = exacto(informe)
            if ri is None:
                print("No se localiza el informe", informe)
                return 1
            reg["informe_sesion"] = {"simbolo": informe, "registro": "https://digitallibrary.un.org/record/" + next(c.text for c in ri.iter(NS + "controlfield") if c.get("tag") == "001"), "pdf": pdfs(ri)}
        salida[sim] = reg
    json.dump({"fuente": "Biblioteca Digital ONU (registro anotado de cada símbolo)", "documentos": salida},
              open("data/fuentes/documentos_marco.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Documentos marco:", ", ".join(salida))
    return 0


sys.exit(main())
