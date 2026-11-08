#!/usr/bin/env python3
"""Observaciones y recomendaciones generales de los nueve comités de tratados (jurisprudencia interpretativa), desde la Biblioteca Digital ONU.
Consulta por símbolo (191$a = <comité>/GC/<n>) en MARCXML, ruta permitida por robots.txt, 5 s entre consultas. Se descartan borradores (CRP, Rev., R.),
correcciones y adiciones. NO incluye los dictámenes sobre comunicaciones individuales (miles; solo se enlaza la base oficial) ni las observaciones
generales anteriores a la numeración /GC/ (HRI/GEN/1/Rev.), que la Biblioteca Digital cataloga de otro modo. Los huecos de numeración se registran.
Salida: data/fuentes/jurisprudencia.json y data/jurisprudencia.js (carga diferida). Si falla la red o salen pocos documentos, ABORTA sin tocar los anteriores."""
import gzip, json, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

NS = "{http://www.loc.gov/MARC21/slim}"
UA = "ATLAS-ONU/1.0 (proyecto academico sin fines de lucro; +https://github.com/sukima-labs/atlasonu)"
COMITES = {"CCPR": "CCPR/C/GC", "CESCR": "E/C.12/GC", "CERD": "CERD/C/GC", "CAT": "CAT/C/GC", "CEDAW": "CEDAW/C/GC",
           "CRC": "CRC/C/GC", "CMW": "CMW/C/GC", "CRPD": "CRPD/C/GC", "CED": "CED/C/GC"}
SIMB = re.compile(r"^(?P<pre>.+)/(?P<n>\d+)$")


def consultar(prefijo):
    url = "https://digitallibrary.un.org/search?" + urllib.parse.urlencode({"ln": "en", "p": '191__a:"%s/*"' % prefijo, "of": "xm", "rg": 200})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90) as r:
        crudo = r.read()
    if crudo[:2] == b"\x1f\x8b":
        crudo = gzip.decompress(crudo)
    return list(ET.fromstring(crudo).iter(NS + "record"))


def valores(rec, tag, code):
    return [sf.text.strip() for df in rec.iter(NS + "datafield") if df.get("tag") == tag
            for sf in df.iter(NS + "subfield") if sf.get("code") == code and sf.text]


def main():
    salida, huecos = {}, {}
    for k, (cid, pre) in enumerate(COMITES.items()):
        if k:
            time.sleep(5)
        docs = {}
        for rec in consultar(pre):
            rid = next((c.text for c in rec.iter(NS + "controlfield") if c.get("tag") == "001"), None)
            for sim in valores(rec, "191", "a"):
                m = SIMB.match(sim)
                if not rid or not m or m.group("pre") != pre:
                    continue   # borradores (/CRP.n, /R.n, /Rev.n), correcciones y símbolos de otro comité (conjuntas)
                titulo = " ".join(p.strip(" :/") for p in (valores(rec, "245", "a") + valores(rec, "245", "b")[:1]) if p.strip(" :/"))
                fecha = (valores(rec, "269", "a") or [""])[0]
                conj = [s for s in valores(rec, "191", "a") if s != sim]
                docs[int(m.group("n"))] = {"n": int(m.group("n")), "s": sim, "t": titulo, "f": fecha, "r": rid, "c": conj}
        lista = sorted(docs.values(), key=lambda d: -d["n"])
        if lista:
            hasta = lista[0]["n"]
            huecos[cid] = [n for n in range(1, hasta + 1) if n not in docs]
        salida[cid] = lista
        print(cid, len(lista), "huecos:", huecos.get(cid, []))
    total = sum(len(v) for v in salida.values())
    if total < 60 or any(not salida[c] for c in COMITES):
        sys.exit("ABORTA: se recuperaron muy pocos documentos (%d)" % total)
    fuente = "Biblioteca Digital de la ONU (consulta por símbolo)"
    json.dump({"fuente": fuente, "huecos": huecos, "comites": salida},
              open("data/fuentes/jurisprudencia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    open("data/jurisprudencia.js", "w", encoding="utf-8").write(
        "window.JURIS=" + json.dumps({"huecos": huecos, "comites": salida}, ensure_ascii=False, separators=(",", ":")) + ";")
    print("Jurisprudencia:", total, "documentos")


main()
