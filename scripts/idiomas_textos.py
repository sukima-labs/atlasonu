#!/usr/bin/env python3
"""Textos de la interfaz de index.html que traduce assets/idiomas.js (T26).

Sigue el MISMO recorrido que el motor del navegador: un elemento cuyos descendientes son solo etiquetas en línea
(b, a, code…) es una «frase» y su clave es su contenido canónico (texto con espacios colapsados y etiquetas sin
atributos: «Pulsa <b>Ver ficha</b> para…»); si no, se baja a sus hijos y cada texto suelto es su propia clave.
También placeholder, aria-label, title y alt, y el <title> de la página.

  python3 -I scripts/idiomas_textos.py                 # lista las claves (JSON)
  python3 -I scripts/idiomas_textos.py --comprobar     # falla si algún diccionario (en, fr, ar, zh, ru) no cubre alguna clave o
                                                       # alguna traducción no conserva las etiquetas
  python3 -I scripts/idiomas_textos.py --faltan en     # claves sin traducir en en.js (JSON)
Además de los textos de index.html, los diccionarios llevan los que dibuja el JavaScript (fichas, resultados…);
en esos, {n} es una cifra que cambia y {fecha} una fecha escrita («17 de marzo de 2003»). --comprobar exige que los cinco diccionarios tengan las mismas claves.
"""
import html.parser, json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_LINEA = {"a", "abbr", "b", "br", "cite", "code", "em", "i", "kbd", "mark", "q", "s", "small", "span", "strong",
            "sub", "sup", "u"}
VACIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SALTAR = {"script", "style", "svg", "noscript", "template"}
SOLO_ATRS = {"input", "textarea"}  # de un campo se traducen los atributos, nunca lo escrito
ATRIBUTOS = ("placeholder", "aria-label", "title", "alt")
LETRA = re.compile(r"[A-Za-zÀ-ÿ]{2}")
IDIOMAS = ("en", "fr", "ar", "zh", "ru")


class Nodo:
    def __init__(self, tag, attrs, padre):
        self.tag, self.attrs, self.padre, self.hijos = tag, dict(attrs), padre, []


class Arbol(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raiz = self.actual = Nodo("#raiz", [], None)

    def handle_starttag(self, tag, attrs):
        n = Nodo(tag, attrs, self.actual)
        self.actual.hijos.append(n)
        if tag not in VACIOS:
            self.actual = n

    def handle_startendtag(self, tag, attrs):
        self.actual.hijos.append(Nodo(tag, attrs, self.actual))

    def handle_endtag(self, tag):
        n = self.actual
        while n is not None and n.tag != tag:
            n = n.padre
        if n is not None and n.padre is not None:
            self.actual = n.padre

    def handle_data(self, data):
        self.actual.hijos.append(data)


def colapsa(t):
    return re.sub(r"\s+", " ", t)


def solo_en_linea(n):
    return all(isinstance(h, str) or (h.tag in EN_LINEA and solo_en_linea(h)) for h in n.hijos)


def canon(n):
    out = []
    for h in n.hijos:
        if isinstance(h, str):
            out.append(colapsa(h))
        elif h.tag == "br":
            out.append("<br>")
        elif h.tag == "abbr":  # lo pone el glosario de siglas (T63); en el navegador tampoco cuenta
            out.append(canon(h))
        else:
            out.append(f"<{h.tag}>{canon(h)}</{h.tag}>")
    return "".join(out)


def excluido(n):
    return n.tag in SALTAR or n.attrs.get("translate") == "no" or "data-sin-traducir" in n.attrs


def claves(fichero=os.path.join(RAIZ, "index.html")):
    p = Arbol()
    p.feed(open(fichero, encoding="utf-8").read())
    vistas = {}

    def anota(k):
        k = k.strip()
        if LETRA.search(re.sub(r"<[^>]+>", "", k)):
            vistas.setdefault(k, None)

    def recorre(n):
        if excluido(n):
            return
        for a in ATRIBUTOS:
            if n.attrs.get(a):
                anota(colapsa(n.attrs[a]))
        if n.tag in SOLO_ATRS:
            return
        if n.tag == "title":
            anota(colapsa(canon(n)))
            return
        if n.tag not in EN_LINEA and n.tag != "#raiz" and n.hijos and solo_en_linea(n):
            anota(canon(n))
            for d in descendientes(n):
                for a in ATRIBUTOS:
                    if d.attrs.get(a):
                        anota(colapsa(d.attrs[a]))
            return
        for h in n.hijos:
            if isinstance(h, str):
                anota(colapsa(h))
            else:
                recorre(h)

    recorre(p.raiz)
    return list(vistas)


def descendientes(n):
    for h in n.hijos:
        if not isinstance(h, str):
            yield h
            yield from descendientes(h)


def etiquetas(t):
    return sorted(re.findall(r"</?[a-z]+>", t))


def diccionario(ln):
    f = os.path.join(RAIZ, "data", "idiomas", ln + ".js")
    s = open(f, encoding="utf-8").read()
    i = s.index("{")
    return json.loads(s[i:s.rindex("}") + 1])


def main():
    args = sys.argv[1:]
    ks = claves()
    if not args:
        json.dump(ks, sys.stdout, ensure_ascii=False, indent=0)
        return
    if args[0] == "--faltan":
        d = diccionario(args[1])
        json.dump([k for k in ks if k not in d], sys.stdout, ensure_ascii=False, indent=0)
        return
    if args[0] == "--comprobar":
        fallos = []
        for ln in IDIOMAS:
            d = diccionario(ln)
            falta = [k for k in ks if k not in d]
            if falta:
                fallos.append(f"{ln}: {len(falta)} textos sin traducir, p. ej. {falta[:3]}")
            for k, v in d.items():
                if not isinstance(v, str) or not v.strip():
                    fallos.append(f"{ln}: traducción vacía de {k!r}")
                elif etiquetas(k) != etiquetas(v):
                    fallos.append(f"{ln}: la traducción de {k!r} no conserva las etiquetas: {v!r}")
                elif k.count("{n}") != v.count("{n}") or k.count("{fecha}") != v.count("{fecha}"):
                    fallos.append(f"{ln}: la traducción de {k!r} no conserva las cifras {{n}}: {v!r}")
        dics = {ln: set(diccionario(ln)) for ln in IDIOMAS}
        for a in IDIOMAS:
            for b in IDIOMAS:
                solo = sorted(dics[a] - dics[b])
                if solo:
                    fallos.append(f"{b}: le faltan {len(solo)} textos que sí tiene {a}, p. ej. {solo[:3]}")
        print("\n".join(fallos) or f"idiomas: {len(ks)} textos, {', '.join(IDIOMAS)} completos")
        sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
