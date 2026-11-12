#!/usr/bin/env python3
"""T75: índice pequeño de data/seguimiento/<ID>.json para la pantalla «Seguimiento de recomendaciones».

Escribe data/seguimiento.js (window.SEGUIMIENTO) con, por país y examen del EPU:
[ciclo, fecha, símbolo, total, apoyadas, tomó nota, sin información]. La pantalla lo usa para el selector y el
comparador sin bajar los ficheros de cada país (41 MB en total); el fichero del país se carga al elegirlo.
«Sin información» se cuenta aparte: nunca se suma como «tomó nota» ni como cero.
Se rehace cada vez que cambie data/seguimiento/ (lo llama scripts/epu_seguimiento.py al terminar).
Uso: python3 -I scripts/seguimiento_indice.py [--comprobar]
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR = RAIZ / "data" / "seguimiento"
SALIDA = RAIZ / "data" / "seguimiento.js"


def construir():
    p = {}
    for f in sorted(DIR.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        filas = []
        for e in d["examenes"]:
            rs = [r.get("r") for r in e["recs"]]
            filas.append([e["ciclo"], e.get("fecha") or "", e["s"], len(rs),
                          rs.count("apoyada"), rs.count("tomó nota"), sum(1 for r in rs if r is None)])
        filas.sort(key=lambda x: (x[0], x[1]))
        p[f.stem] = filas
    return "window.SEGUIMIENTO=" + json.dumps({"p": p}, ensure_ascii=False, separators=(",", ":")) + ";\n"


def main():
    texto = construir()
    if "--comprobar" in sys.argv:
        if not SALIDA.exists() or SALIDA.read_text(encoding="utf-8") != texto:
            sys.exit("data/seguimiento.js no está al día: python3 -I scripts/seguimiento_indice.py")
        print("data/seguimiento.js al día")
        return
    SALIDA.write_text(texto, encoding="utf-8")
    print(f"data/seguimiento.js: {len(texto)//1024} KB")


if __name__ == "__main__":
    main()
