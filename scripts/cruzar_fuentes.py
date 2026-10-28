#!/usr/bin/env python3
"""Cruza el catálogo con las listas oficiales ya descargadas (T4) y sale con error si hay diferencias."""
import json, re, sys, unicodedata


def norm(s):
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", "", s).strip()


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


cat = cargar("data/catalogo.json")
diferencias = []

en_catalogo = {norm(m["nombre"]) for m in cat["mandatos"]}
for sigla in ("CM", "TM"):
    fuente = cargar(f"data/fuentes/ohchr_{sigla}_es.json")
    faltan = [m["titulo"] for m in fuente["mandatos"] if norm(m["titulo"]) not in en_catalogo]
    print(f"Mandatos {sigla}: {fuente['n']} en OHCHR, {len(faltan)} sin coincidencia")
    diferencias += [f"mandato {sigla}: {t}" for t in faltan]

paises_oficial = {p["iso3"] for p in cargar("data/fuentes/paises_ohchr.json")["paises"]} - {"OTH"}
paises_catalogo = {p["id"] for p in cat["paises"]}
print(f"Países: {len(paises_oficial)} en OHCHR (sin «Otros»), {len(paises_catalogo)} en el catálogo")
diferencias += [f"país: {i}" for i in sorted(paises_oficial ^ paises_catalogo)]

untc = {t["es"] for t in cargar("data/fuentes/tratados_untc.json")["tratados"]}
print(f"Tratados: {len(untc)} en la Colección de Tratados, {len(cat['tratados'])} en el catálogo")
if len(untc) != len(cat["tratados"]):
    diferencias.append("tratados: distinto número")

for d in diferencias:
    print("DIFERENCIA", d)
sys.exit(1 if diferencias else 0)
