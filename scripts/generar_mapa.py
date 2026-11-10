#!/usr/bin/env python3
"""Genera data/mapa.js: contornos de los países para el mapa de ATLAS ONU (T11/T24).

Fuente: Natural Earth, «Admin 0 – Countries», escala 1:50 millones (dominio público,
https://www.naturalearthdata.com/about/terms-of-use/). Se baja una vez y se simplifica aquí:
el sitio no carga nada de fuera.

Uso:
    python3 scripts/generar_mapa.py [--origen ne_50m_admin_0_countries.geojson] [--salida data/mapa.js]
Sin --origen descarga el GeoJSON de github.com/nvkelso/natural-earth-vector.

Salida: window.MAPA = {vb:[ancho,alto], p:{ID:"trazado"}, m:[ID,…], f:"trazado de fondo"}
  p  países de ATLAS (los 196 del catálogo), con el id de ATLAS
  m  los que son tan pequeños que se dibujan como un círculo (marcador)
  f  tierra sin país en ATLAS (territorios, Taiwán…): solo fondo gris, sin clic
"""
import argparse
import json
import math
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
       "geojson/ne_50m_admin_0_countries.geojson")
ANCHO = 2000          # unidades del viewBox
TOLERANCIA = 1.3      # Douglas-Peucker, en unidades del viewBox
AREA_MIN = 14.0       # polígono más pequeño que esto (u²) se descarta si el país tiene otro mayor
MARCADOR_R = 4        # radio del círculo de los países diminutos
LAT_MIN, LAT_MAX = -56.0, 84.0

# Códigos de ATLAS que no son el ISO_A3 de Natural Earth
ATLAS_A_NE = {"CRO": "HRV", "RKS": "KOS"}
NE_A_ATLAS = {v: k for k, v in ATLAS_A_NE.items()}


def miller(lon, lat):
    y = 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))
    return math.radians(lon), y


def proyectar_todo(anillo, esc, x0, y0):
    out = []
    for lon, lat in anillo:
        lat = max(LAT_MIN, min(LAT_MAX, lat))
        x, y = miller(lon, lat)
        out.append(((x - x0) * esc, (y0 - y) * esc))
    return out


def simplificar(pts, tol):
    """Douglas-Peucker iterativo."""
    if len(pts) < 4:
        return pts
    marca = [False] * len(pts)
    marca[0] = marca[-1] = True
    pila = [(0, len(pts) - 1)]
    t2 = tol * tol
    while pila:
        a, b = pila.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        dmax, imax = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            if l2 == 0:
                d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
                d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if d > dmax:
                dmax, imax = d, i
        if dmax > t2:
            marca[imax] = True
            pila.append((a, imax))
            pila.append((imax, b))
    return [p for p, m in zip(pts, marca) if m]


def area(pts):
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def trazado(anillos):
    partes = []
    for r in anillos:
        pts = [(round(x), round(y)) for x, y in r]
        ded = [pts[0]]
        for p in pts[1:]:
            if p != ded[-1]:
                ded.append(p)
        if len(ded) > 1 and ded[0] == ded[-1]:
            ded.pop()
        if len(ded) < 3:
            continue
        partes.append("M" + "L".join(f"{x} {y}" for x, y in ded) + "Z")
    return "".join(partes)


def poligonos(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    return geom["coordinates"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origen")
    ap.add_argument("--salida", default=str(RAIZ / "data" / "mapa.js"))
    a = ap.parse_args()

    if a.origen:
        gj = json.loads(Path(a.origen).read_text(encoding="utf-8"))
    else:
        with urllib.request.urlopen(URL, timeout=60) as r:
            gj = json.load(r)

    # Los 196 países de ATLAS salen del catálogo (data/paises.json solo trae los que tienen mandato)
    txt = (RAIZ / "data" / "atlas-data.js").read_text(encoding="utf-8")
    cat = json.loads(txt.split("=", 1)[1].strip().rstrip(";"))
    ids = {p["id"] for p in cat["paises"]}

    x0 = miller(-180, 0)[0]
    xmax = miller(180, 0)[0]
    esc = ANCHO / (xmax - x0)
    y_top = miller(0, LAT_MAX)[1]
    y_bot = miller(0, LAT_MIN)[1]
    alto = round((y_top - y_bot) * esc)

    por_pais, fondo, marcadores = {}, [], []
    for ft in gj["features"]:
        pr = ft["properties"]
        if pr.get("ADM0_A3") == "ATA":
            continue
        iso = pr["ISO_A3_EH"] if pr["ISO_A3"] == "-99" else pr["ISO_A3"]
        if pr.get("ADM0_A3") == "KOS":
            iso = "KOS"
        aid = NE_A_ATLAS.get(iso, iso)
        anillos_pais = []
        for poli in poligonos(ft["geometry"]):
            ext = proyectar_todo([c[:2] for c in poli[0]], esc, x0, y_top)
            ar = area(ext)
            anillos_pais.append((ar, simplificar(ext, TOLERANCIA)))
        mayor = max(ar for ar, _ in anillos_pais)
        utiles = [r for ar, r in anillos_pais if ar >= AREA_MIN or ar == mayor]
        if aid in ids:
            if aid in por_pais:  # varias entidades con el mismo código (p. ej. islas Ashmore y Cartier)
                m0, u0, t0 = por_pais[aid]
                por_pais[aid] = (max(m0, mayor), u0 + utiles, t0 + anillos_pais)
            else:
                por_pais[aid] = (mayor, utiles, anillos_pais)
        else:
            fondo.extend(utiles)

    faltan = sorted(ids - set(por_pais))
    if faltan:
        print("AVISO: sin contorno en Natural Earth:", faltan, file=sys.stderr)

    p = {}
    for aid, (mayor, utiles, todos) in sorted(por_pais.items()):
        if mayor < AREA_MIN:
            # país diminuto: un círculo en su centro
            _, r = max(todos, key=lambda t: t[0])
            cx = round(sum(x for x, _ in r) / len(r))
            cy = round(sum(y for _, y in r) / len(r))
            R = MARCADOR_R
            p[aid] = (f"M{cx - R} {cy}a{R} {R} 0 1 0 {2 * R} 0a{R} {R} 0 1 0 {-2 * R} 0Z")
            marcadores.append(aid)
        else:
            p[aid] = trazado(utiles)

    salida = {"vb": [ANCHO, alto], "p": p, "m": sorted(marcadores), "f": trazado(fondo)}
    js = ("/* Contornos: Natural Earth (dominio público), escala 1:50 M, proyección Miller, simplificados.\n"
          "   Generado por scripts/generar_mapa.py; no editar a mano. */\n"
          "window.MAPA=" + json.dumps(salida, ensure_ascii=False, separators=(",", ":")) + ";\n")
    Path(a.salida).write_text(js, encoding="utf-8")
    print(f"{a.salida}: {len(js) / 1024:.0f} KB, {len(p)} países, {len(marcadores)} marcadores, alto {alto}")


if __name__ == "__main__":
    main()
