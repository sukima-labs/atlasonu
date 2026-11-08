#!/usr/bin/env python3
"""Pruebas del texto completo: troceo, consulta segura, índice y la ruta /texto del servicio. Sin red.
  python3 -I tests/texto_completo_test.py"""
import json, os, sys, tempfile, threading, unittest, urllib.error, urllib.request

TMP = tempfile.mkdtemp()
os.environ["ATLAS_TEXTOS_DIR"] = TMP
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "mini_pc"))
import texto_completo as tc  # noqa: E402
import busqueda_servicio as bs  # noqa: E402

ES = """Naciones Unidas A/HRC/RES/16/16
GE.11-12345
Resolución aprobada por el Consejo de Derechos Humanos

16/16 Desapariciones forzadas o involuntarias

1. Exhorta a los Estados a que cooperen con el Grupo de Trabajo y respon-
dan favorablemente a sus solicitudes de visitas a los países;

2. Pide a los Gobiernos que garanticen la investigación de toda desaparición forzada denunciada.
3
"""
EN = """1. Calls upon States to respond favourably to requests for country visits by the Working Group on Enforced or Involuntary Disappearances;
"""


def construir():
    os.makedirs(os.path.join(TMP, "txt"), exist_ok=True)
    for nombre, txt in (("A_HRC_RES_16_16-es.txt", ES), ("A_HRC_RES_16_16-en.txt", EN),
                        ("A_HRC_RES_15_22-es.txt", "Realice visitas a los países y responda con prontitud a las invitaciones.")):
        with open(os.path.join(TMP, "txt", nombre), "w", encoding="utf-8") as f:
            f.write(txt)
    tc.indexar(d=TMP)


class Pruebas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        construir()
        cls.srv = bs.ThreadingHTTPServer(("127.0.0.1", 0), bs.H)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def get(self, ruta):
        try:
            with urllib.request.urlopen(self.base + ruta, timeout=5) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def test_parrafos_quita_cabeceras_y_une_guiones(self):
        ps = tc.parrafos(ES)
        self.assertFalse(any(p.startswith("GE.") for p in ps))
        self.assertTrue(any("respondan favorablemente" in p for p in ps), ps)
        self.assertFalse(any(p.strip() == "3" for p in ps))

    def test_consulta_no_rompe_fts(self):
        for q in ['"', "AND OR NOT", "a*b) NEAR(", "'; DROP TABLE x", "«tortura»"]:
            tc.consulta_fts(q)  # no lanza
        self.assertEqual(tc.consulta_fts('"visitas a los países" tortura'), '"visitas a los países" "tortura"')

    def test_ruta_texto_encuentra_y_marca(self):
        cod, d = self.get("/texto?q=visitas")
        self.assertEqual(cod, 200)
        self.assertEqual(d["documentos"], 2)
        sims = {r["simbolo"] for r in d["resultados"]}
        self.assertEqual(sims, {"A/HRC/RES/16/16", "A/HRC/RES/15_22".replace("_", "/")})
        self.assertTrue(all("\x02" in r["fragmento"] and "\x03" in r["fragmento"] for r in d["resultados"]))

    def test_sin_tildes_y_por_lengua(self):
        _, d = self.get("/texto?q=desaparicion&ln=es")
        self.assertTrue(d["total"] >= 1 and all(r["lengua"] == "es" for r in d["resultados"]))
        _, d = self.get("/texto?q=enforced%20disappearances&ln=en")
        self.assertEqual([r["lengua"] for r in d["resultados"]], ["en"])

    def test_consulta_rara_no_da_500(self):
        for q in ['"', "NEAR(", "*", "AND"]:
            cod, _ = self.get("/texto?q=" + urllib.request.quote(q + " x"))
            self.assertIn(cod, (200, 400))

    def test_resaltar_ignora_palabras_vacias(self):
        t = "Pide la detención de los responsables y la protección de los periodistas."
        f = tc._resaltar(t, "protección de periodistas")
        self.assertIn("\x02protección\x03", f)
        self.assertIn("\x02periodistas\x03", f)
        self.assertNotIn("\x02de", f)
        self.assertEqual(tc.palabras("la protección de los niños"), ["proteccion", "ninos"])

    def test_hibrido_sin_modelo_es_igual_que_palabras(self):
        import sqlite3
        con = sqlite3.connect(tc.ruta_db())
        if tc.semantica_disponible():
            self.skipTest("hay modelo: se prueba en test_hibrido_cruza_idiomas")
        self.assertEqual(tc.buscar_hibrido(con, "visitas"), tc.buscar(con, "visitas"))

    def test_hibrido_cruza_idiomas(self):
        if not tc.semantica_disponible():
            self.skipTest("sin fastembed/modelo (la CI no lo tiene)")
        import sqlite3
        con = sqlite3.connect(tc.ruta_db())
        r = tc.buscar_hibrido(con, "country visits", ln="es", clave=1)
        self.assertTrue(r and all(x["lengua"] == "es" for x in r))

    def test_sin_indice_da_503(self):
        viejo = tc.DIR
        tc.DIR = tempfile.mkdtemp()
        try:
            cod, d = self.get("/texto?q=visitas")
        finally:
            tc.DIR = viejo
        self.assertEqual(cod, 503)


if __name__ == "__main__":
    unittest.main(verbosity=2)
