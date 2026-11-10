#!/usr/bin/env python3
"""Cifras de ATLAS ONU para las piezas de marketing, sacadas de data/ (nunca escritas a mano).

Uso (desde la raíz del repo):
  python3 -I marketing/cifras.py                      # escribe marketing/kit_prensa/CIFRAS.md
  python3 -I marketing/cifras.py --aplicar FICHERO    # imprime FICHERO con {{marcas}} sustituidas
  python3 -I marketing/cifras.py --json               # imprime las cifras en JSON

Las marcas son {{mandatos}}, {{actos}}, {{localizados}}, {{paises}}, {{tratados}}, {{mecanismos}},
{{siglas}}, {{historia}}, {{entidades}}, {{idiomas}} y {{fecha}} (fecha de los datos de la revisión).
Una marca desconocida detiene el proceso: no se publica un texto con un hueco.
"""
import glob
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cargar(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        return json.load(f)


def cifras():
    estado = cargar("data/estado.json")
    cont = estado["contadores"]
    cat = cargar("data/catalogo.json")
    return {
        "mandatos": cont["mandatos"],
        "actos": cont["actos"],
        "localizados": cont["localizados"],
        "paises": cont["paises"],
        "mecanismos": cont["mecanismos"],
        "tratados": len(cat["tratados"]),
        "siglas": len(cargar("data/siglas.json")["entradas"]),
        "historia": len(cargar("data/historia.json")["eventos"]),
        "entidades": len(cargar("data/sistema_onu.json")["entidades"]),
        # español, inglés, francés, árabe, chino y ruso: es, y un diccionario por cada uno de los otros cinco
        "idiomas": 1 + len(glob.glob(os.path.join(RAIZ, "data", "idiomas", "*.js"))),
        "fecha": estado["datos_del"],
    }


def aplicar(texto, c):
    def sustituir(m):
        k = m.group(1)
        if k not in c:
            sys.exit("Marca desconocida: {{%s}}" % k)
        return str(c[k])

    return re.sub(r"\{\{(\w+)\}\}", sustituir, texto)


PLANTILLA = """# Cifras de ATLAS ONU para piezas públicas

Generado con `python3 -I marketing/cifras.py` a partir de `data/` (datos de la revisión del **{fecha}**).
No editar a mano. Antes de publicar, regenerar y citar la fecha.

| Qué | Cifra |
|---|---|
| Mandatos vigentes de procedimientos especiales | {mandatos} |
| Actos jurídicos (creación, prórrogas) | {actos} |
| …de ellos localizados en la Biblioteca Digital de la ONU | {localizados} |
| Fichas de país | {paises} |
| Tratados de derechos humanos | {tratados} |
| Mecanismos conexos | {mecanismos} |
| Siglas y acrónimos | {siglas} |
| Hechos en la línea de tiempo de la historia | {historia} |
| Entidades del sistema ONU | {entidades} |
| Idiomas de la interfaz | {idiomas} |

Cómo contarlo: «localizado» significa que existe un registro con ese símbolo exacto; no equivale a haber leído el texto.
"""


def main(argv):
    c = cifras()
    if "--json" in argv:
        print(json.dumps(c, ensure_ascii=False, indent=2))
    elif "--aplicar" in argv:
        ruta = argv[argv.index("--aplicar") + 1]
        with open(ruta, encoding="utf-8") as f:
            sys.stdout.write(aplicar(f.read(), c))
    else:
        destino = os.path.join(RAIZ, "marketing", "kit_prensa", "CIFRAS.md")
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(PLANTILLA.format(**c))
        print("escrito", os.path.relpath(destino, RAIZ), c)


if __name__ == "__main__":
    main(sys.argv[1:])
