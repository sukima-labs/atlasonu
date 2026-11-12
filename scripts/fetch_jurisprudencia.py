#!/usr/bin/env python3
"""Observaciones y recomendaciones generales de los nueve comités de tratados (jurisprudencia interpretativa), desde la Biblioteca Digital ONU.
T56: la Biblioteca Digital prohíbe /search, así que no se busca: se conservan los documentos ya anotados y se bajan los
registros nuevos de data/fuentes/registros_biblioteca.json (/record/N, MARCXML, 5 s). Con --refrescar se bajan otra vez
todos los conocidos. Se clasifican por símbolo (191$a = <comité>/GC/<n>). Se descartan borradores (CRP, Rev., R.),
correcciones y adiciones. NO incluye los dictámenes sobre comunicaciones individuales (miles; solo se enlaza la base oficial) ni las observaciones
generales anteriores a la numeración /GC/ (HRI/GEN/1/Rev.), que la Biblioteca Digital cataloga de otro modo. Los huecos de numeración se registran.
Salida: data/fuentes/jurisprudencia.json y data/jurisprudencia.js (carga diferida). Si falla la red o salen pocos documentos, ABORTA sin tocar los anteriores."""
import json, os, re, sys
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import biblioteca as B

NS = "{http://www.loc.gov/MARC21/slim}"
COMITES = {"CCPR": "CCPR/C/GC", "CESCR": "E/C.12/GC", "CERD": "CERD/C/GC", "CAT": "CAT/C/GC", "CEDAW": "CEDAW/C/GC",
           "CRC": "CRC/C/GC", "CMW": "CMW/C/GC", "CRPD": "CRPD/C/GC", "CED": "CED/C/GC"}
SIMB = re.compile(r"^(?P<pre>.+)/(?P<n>\d+)$")


def registro(n):
    return next(ET.fromstring(B.marc(n).encode("utf-8")).iter(NS + "record"))


def valores(rec, tag, code):
    return [sf.text.strip() for df in rec.iter(NS + "datafield") if df.get("tag") == tag
            for sf in df.iter(NS + "subfield") if sf.get("code") == code and sf.text]


def main():
    try:
        antes = json.load(open("data/fuentes/jurisprudencia.json", encoding="utf-8"))["comites"]
    except FileNotFoundError:
        antes = {}
    docs = {cid: {d["n"]: {k: d[k] for k in ("n", "s", "t", "f", "r", "c")} for d in antes.get(cid, [])} for cid in COMITES}
    conocidos = [d["r"] for v in antes.values() for d in v]
    pedir = (conocidos if "--refrescar" in sys.argv else []) + [n for n in B.nuevos("fetch_jurisprudencia") if n not in conocidos]
    for n in dict.fromkeys(pedir):
        rec = registro(n)
        rid = next((c.text for c in rec.iter(NS + "controlfield") if c.get("tag") == "001"), None)
        for sim in valores(rec, "191", "a"):
            m = SIMB.match(sim)
            cid = next((c for c, pre in COMITES.items() if m and m.group("pre") == pre), None)
            if not rid or not cid:
                continue   # borradores (/CRP.n, /R.n, /Rev.n), correcciones y símbolos de otros documentos
            titulo = " ".join(p.strip(" :/") for p in (valores(rec, "245", "a") + valores(rec, "245", "b")[:1]) if p.strip(" :/"))
            fecha = (valores(rec, "269", "a") or [""])[0]
            conj = [s for s in valores(rec, "191", "a") if s != sim]
            docs[cid][int(m.group("n"))] = {"n": int(m.group("n")), "s": sim, "t": titulo, "f": fecha, "r": rid, "c": conj}
    salida, huecos = {}, {}
    for cid in COMITES:
        lista = sorted(docs[cid].values(), key=lambda d: -d["n"])
        if lista:
            hasta = lista[0]["n"]
            huecos[cid] = [n for n in range(1, hasta + 1) if n not in docs[cid]]
        salida[cid] = lista
        print(cid, len(lista), "huecos:", huecos.get(cid, []))
    total = sum(len(v) for v in salida.values())
    if total < 60 or any(not salida[c] for c in COMITES):
        sys.exit("ABORTA: se recuperaron muy pocos documentos (%d)" % total)
    fuente = "Biblioteca Digital de la ONU (registros anotados)"
    json.dump({"fuente": fuente, "huecos": huecos, "comites": salida},
              open("data/fuentes/jurisprudencia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    open("data/jurisprudencia.js", "w", encoding="utf-8").write(
        "window.JURIS=" + json.dumps({"huecos": huecos, "comites": salida}, ensure_ascii=False, separators=(",", ":")) + ";")
    print("Jurisprudencia:", total, "documentos")


main()
