#!/usr/bin/env python3
"""Corrige los enlaces PDF de data/paises/<ISO>.js que no son de la lengua que dicen.

Por un fallo del parser de fetch_docs_pais.py (ya corregido), unos 950 enlaces «inglés» o «español» apuntaban al
PDF en francés, chino, ruso o árabe del mismo registro. Para cada uno se prueba el fichero de la lengua correcta
EN EL MISMO REGISTRO (…/record/N/files/<base>-EN.pdf): si la Biblioteca Digital lo sirve y es un PDF, se pone;
si no, se quita el enlace (la ficha sigue enlazando el registro). No se adivina nada que no se haya comprobado.
Respeta el robots.txt: solo /record/…/files, 5 s entre peticiones. Reanudable: guarda lo comprobado en --cache.
  python3 -I scripts/corregir_lenguas_pdf.py [--cache fichero.json] [--solo-contar]"""
import argparse, glob, json, os, re, time, urllib.request

UA = "ATLAS-ONU/1.0 (+https://github.com/sukima-labs/atlasonu)"
PAUSA = 5.0
CAB = re.compile(r"^(window\.PAIS_DOCS=window\.PAIS_DOCS\|\|\{\};window\.PAIS_DOCS\['([A-Z]{3})'\]=)(.*);\s*$", re.S)


def mal(ln, u):
    return bool(u) and not re.search(r"-" + ln.upper() + r"\.pdf$", u, re.I)


def candidata(ln, u):
    m = re.fullmatch(r"https?://digitallibrary\.un\.org(/record/\d+/files/.+)-[A-Za-z]{2}\.pdf", u)
    return "https://digitallibrary.un.org" + m.group(1) + "-" + ln.upper() + ".pdf" if m else None


def existe(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-7"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read(8).startswith(b"%PDF")
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="corregir_lenguas_cache.json")
    ap.add_argument("--solo-contar", action="store_true")
    a = ap.parse_args()
    cache = json.load(open(a.cache)) if os.path.exists(a.cache) else {}
    puestos = quitados = 0
    for f in sorted(glob.glob("data/paises/*.js")):
        m = CAB.match(open(f, encoding="utf-8").read())
        d, cambio = json.loads(m.group(3)), False
        for lista in d.values():
            for x in lista if isinstance(lista, list) else []:
                for ln in ("es", "en"):
                    if not mal(ln, x.get(ln)):
                        continue
                    c = candidata(ln, x[ln])
                    if a.solo_contar:
                        puestos += 1
                        continue
                    if c and c not in cache:
                        cache[c] = existe(c)
                        json.dump(cache, open(a.cache, "w"))
                        time.sleep(PAUSA)
                    if c and cache[c]:
                        x[ln] = c
                        puestos += 1
                    else:
                        del x[ln]
                        quitados += 1
                    cambio = True
        if cambio:
            with open(f, "w", encoding="utf-8") as o:
                o.write(m.group(1) + json.dumps(d, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + ";\n")
    print(f"{'por revisar' if a.solo_contar else 'corregidos'}: {puestos}" + ("" if a.solo_contar else f", quitados: {quitados}"))


if __name__ == "__main__":
    main()
