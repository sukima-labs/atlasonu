#!/usr/bin/env python3
"""Diccionarios de la interfaz: de idiomas/<ln>.json (lo que se edita, también desde Weblate) a data/idiomas/<ln>.js (T94).

La web carga data/idiomas/<ln>.js con <script> (y no el JSON con fetch) para que la copia descargada siga funcionando
abierta como fichero. Esos .js se GENERAN aquí; no se editan a mano.

  idiomas/es.json   plantilla: cada texto en español es su propia clave y su valor (lo pide Weblate).
  idiomas/en.json…  traducciones. Un texto que falta o está vacío no entra en el .js y la web lo enseña en español.

  python3 -I scripts/idiomas.py               # genera data/idiomas/<ln>.js
  python3 -I scripts/idiomas.py --comprobar   # dice si algún .js no corresponde a su JSON (sale con 1)
  python3 -I scripts/idiomas.py --nuevos      # añade a idiomas/es.json los textos de index.html que no tiene
"""
import json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTE = os.path.join(RAIZ, "idiomas")
SALIDA = os.path.join(RAIZ, "data", "idiomas")
IDIOMAS = ("en", "fr", "ar", "zh", "ru")
CABECERA = "/* Generado por scripts/idiomas.py desde idiomas/%s.json: no se edita a mano (T94). */\n"


def lee(ln):
    with open(os.path.join(FUENTE, ln + ".json"), encoding="utf-8") as f:
        return json.load(f)


def escribe_json(ln, d):
    with open(os.path.join(FUENTE, ln + ".json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")


def genera(ln, plantilla=None):
    """El .js de un idioma: las claves en el orden de la plantilla, solo las traducidas."""
    plantilla = plantilla if plantilla is not None else lee("es")
    d = lee(ln)
    filas = [json.dumps(k, ensure_ascii=False) + ":" + json.dumps(d[k], ensure_ascii=False)
             for k in plantilla if isinstance(d.get(k), str) and d[k].strip()]
    return CABECERA % ln + "window.ATLAS_IDIOMA_%s={\n" % ln + ",\n".join(filas) + "\n};\n"


def main():
    args = sys.argv[1:]
    if args[:1] == ["--nuevos"]:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from idiomas_textos import claves
        es = lee("es")
        nuevos = [k for k in claves() if k not in es]
        es.update({k: k for k in nuevos})
        escribe_json("es", es)
        print(f"idiomas/es.json: {len(nuevos)} textos nuevos" + "".join(f"\n  {k}" for k in nuevos))
        return
    plantilla = lee("es")
    distintos = []
    for ln in IDIOMAS:
        ruta = os.path.join(SALIDA, ln + ".js")
        texto = genera(ln, plantilla)
        actual = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else ""
        if texto == actual:
            continue
        if args[:1] == ["--comprobar"]:
            distintos.append(ln)
        else:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(texto)
            print(f"data/idiomas/{ln}.js regenerado")
    if args[:1] == ["--comprobar"]:
        if distintos:
            print("Sin regenerar: " + ", ".join(f"data/idiomas/{ln}.js" for ln in distintos)
                  + ". Ejecuta python3 -I scripts/idiomas.py (en main lo hace solo el workflow «Idiomas»).")
            sys.exit(1)
        print(f"idiomas: data/idiomas/*.js al día con idiomas/*.json ({len(plantilla)} textos)")


if __name__ == "__main__":
    main()
