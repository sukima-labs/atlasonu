#!/usr/bin/env python3
"""T76 fase 1: la base de reglas de «Tengo un caso: ¿adónde acudo?» (data/vias.js) cumple la regla de fuentes
de docs/FUENTES_OFICIALES_VIAS.md: cada requisito trae sus cuatro campos (en palabras simples, lo que dice la ONU,
dónde lo dice y estado); lo «leído en el original» lleva cita y enlace; y las citas de los tratados cuyo texto
guarda ATLAS (data/tratados/) están, letra a letra, en ese texto."""
import json, os, re, unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_S = open(os.path.join(RAIZ, "data", "vias.js"), encoding="utf-8").read()
VIAS = json.loads(_S[_S.index("={") + 1:].rstrip().rstrip(";"))["vias"]
TRATADOS = {t["mtdsg"] for t in json.load(open(os.path.join(RAIZ, "data", "fuentes", "tratados_untc.json"), encoding="utf-8"))["tratados"]}
ESTADOS = {"leído en el original", "por verificar"}
TEMAS = {"quien", "acepta", "recursos", "plazo", "fechas", "otra_via", "forma", "urgente", "funciona"}


def textos():
    """Símbolo de la resolución → texto completo de sus artículos, de data/tratados/*.js."""
    t = {}
    d = os.path.join(RAIZ, "data", "tratados")
    for f in os.listdir(d):
        s = open(os.path.join(d, f), encoding="utf-8").read()
        j = json.loads(s[s.index("={") + 1:].rstrip().rstrip(";"))
        t.setdefault(j.get("simbolo", ""), []).append(" ".join(" ".join(a["texto"] for a in j["articulos"]).split()))
    return t


class Vias(unittest.TestCase):
    def test_estructura(self):
        ids = [v["id"] for v in VIAS]
        self.assertEqual(len(ids), len(set(ids)), "id repetido")
        for v in VIAS:
            for k in ("id", "organo", "tipo", "acepta", "derechos", "requisitos"):
                self.assertIn(k, v, v.get("id"))
            if v["acepta"].get("mtdsg"):
                self.assertIn(v["acepta"]["mtdsg"], TRATADOS, v["id"])
            self.assertTrue(v["requisitos"], v["id"])

    def test_cuatro_campos(self):
        for v in VIAS:
            for q in v["requisitos"]:
                ctx = f'{v["id"]}/{q.get("tema")}'
                self.assertIn(q["tema"], TEMAS, ctx)
                self.assertIn(q["estado"], ESTADOS, ctx)
                self.assertRegex(q["fecha"], r"^\d{4}-\d{2}-\d{2}$", ctx)
                self.assertGreater(len(q["simple"]), 10, ctx)
                self.assertTrue(q["donde"]["documento"].strip(), ctx)
                self.assertIn("articulo", q["donde"], ctx)
                self.assertIn("onu", q, ctx)
                self.assertLessEqual(len(q.get("corto", "")), 60, ctx + ": el resumen corto va en una celda")
                if q["estado"] == "leído en el original":
                    self.assertTrue(q["onu"].strip(), ctx + ": lo leído lleva la cita")
                    self.assertTrue(q["donde"]["articulo"].strip(), ctx)
                    self.assertTrue(q["donde"]["url"].startswith("https://"), ctx)
                # En palabras simples: sin siglas sin explicar (dos o más mayúsculas seguidas).
                self.assertIsNone(re.search(r"\b[A-Z]{2,}\b", q["simple"]), ctx + ": sigla en el texto simple")

    def test_citas_en_el_texto_oficial(self):
        t = textos()
        n = 0
        for v in VIAS:
            for q in v["requisitos"]:
                simb = q["donde"]["documento"].split(",")[0].strip()
                if q["estado"] != "leído en el original" or simb not in t:
                    continue
                cita = " ".join(q["onu"].split())
                self.assertTrue(any(cita in x for x in t[simb]), f'{v["id"]}/{q["tema"]}: la cita no está en {simb}')
                n += 1
        self.assertGreaterEqual(n, 25)

    def test_vias_minimas(self):
        ids = {v["id"] for v in VIAS}
        for i in ("ccpr", "cerd", "cescr", "cedaw", "cat", "crc", "crpd", "ced", "ced-urgente", "cmw", "procedimientos-especiales"):
            self.assertIn(i, ids)


if __name__ == "__main__":
    unittest.main()
