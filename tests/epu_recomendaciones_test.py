#!/usr/bin/env python3
"""Pruebas del contador de recomendaciones del EPU (T68 c): los tres formatos de informe, las remisiones que no cuentan,
los huecos (se descartan en vez de dar una cifra falsa) y que los datos publicados (data/epu.js) cuadran. Sin red.
  python3 -I tests/epu_recomendaciones_test.py"""
import json, os, re, sys, unittest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import epu_recomendaciones as E  # noqa: E402

CICLO2 = """Contents
II. Conclusions and/or recommendations ......... 20
II. Conclusions and/or recommendations**
115. The recommendations listed below have been examined by X and enjoy the support of X:
115.1.
Ratify the Convention (A);
115.2. Continue its work (B);
116. The following recommendations enjoy the support of X:
116.1.
Share good practices (C);
117. The following recommendations were noted by X:
117.1
Do something (D);
118. The following recommendations did not enjoy the support of X.
118.1.
Abolish (E);
118.2. Another (F);
119. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State.
119.1. esto ya no cuenta
"""
CICLO3 = """Contents
II. CONCLUSIONS AND/OR RECOMMENDATIONS ..........
II. CONCLUSIONS AND/OR RECOMMENDATIONS
120. The recommendations formulated during the interactive dialogue have been examined by X:
120.1 Continue (A);
120.2 Strengthen (B)
(C);
120.3 In follow up to the recommendations in paragraphs 116.28 and
116.111 of the report from the second cycle, increase investments (D);
121. The following recommendations have been noted:
121.1 Ratify (E);
122. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State.
"""


class Contador(unittest.TestCase):
    def test_ciclo2_cuatro_parrafos(self):
        self.assertEqual(E.contar(CICLO2), (6, ''))

    def test_ciclo3_ignora_remision_a_otro_informe(self):
        self.assertEqual(E.contar(CICLO3), (4, ''))   # 3 apoyadas + 1 tomada nota; «116.111» es una remisión

    def test_numero_pegado_al_final_de_la_linea_anterior(self):
        self.assertEqual(E.contar(CICLO3.replace('(C);\n120.3', '(C);120.3')), (4, ''))

    def test_encabezado_con_errata_del_pdf(self):
        self.assertEqual(E.contar(CICLO3.replace('II. CONCLUSIONS AND/OR RECOMMENDATIONS\n120', 'II. Conclusions and/or recomm6endations\n120')), (4, ''))

    def test_huecos_no_dan_cifra(self):
        n, motivo = E.contar(CICLO3.replace('120.2 Strengthen (B)\n(C);\n', ''))
        self.assertIsNone(n); self.assertIn('salta', motivo)

    def test_errata_en_el_prefijo_del_original_no_importa(self):
        self.assertEqual(E.contar(CICLO3.replace('120.2 Strengthen', '121.2 Strengthen')), (4, ''))   # «127.10» por «126.10»

    def test_errata_en_el_numero_da_dudoso(self):
        n, motivo = E.contar(CICLO3.replace('120.3 In follow', '120.33 In follow'))
        self.assertIsNone(n); self.assertIn('salta', motivo)   # «60.513» por «60.153»

    def test_encabezado_sin_and_o(self):
        self.assertEqual(E.contar(CICLO3.replace('CONCLUSIONS AND/OR RECOMMENDATIONS\n120', 'Conclusions and recommendations\n120')), (4, ''))

    def test_sin_seccion_o_sin_numeracion(self):
        self.assertIsNone(E.contar('Texto cualquiera')[0])
        self.assertIsNone(E.contar('II. Conclusions and/or recommendations\nNada numerado\n')[0])

    def test_ciclos_por_fecha(self):
        for fecha, c in [('2009-01-09', 1), ('2012-03-20', 1), ('2013-07-04', 2), ('2017-03-20', 2), ('2018-07-09', 3), ('2022-04-10', 3), ('2023-12-29', 4)]:
            self.assertEqual(E.ciclo(fecha), c, fecha)


class DatosPublicados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s = open(os.path.join(RAIZ, 'data/epu.js'), encoding='utf-8').read()
        cls.d = json.loads(s[len('window.EPU='):].rstrip().rstrip(';'))
        cls.inf = json.load(open(os.path.join(RAIZ, 'data/fuentes/epu_informes.json'), encoding='utf-8'))['paises']

    def test_forma(self):
        self.assertEqual([c[0] for c in self.d['c']], [2, 3, 4])
        for iso, lista in self.d['p'].items():
            self.assertRegex(iso, r'^[A-Z]{3}$')
            for c, n, sim, anio in lista:
                self.assertIn(c, (2, 3, 4)); self.assertGreater(n, 0); self.assertLess(n, 1000)
                self.assertRegex(sim, r'^A/HRC/\d+/\d+$'); self.assertRegex(anio, r'^\d{4}$')

    def test_cada_cifra_sale_de_un_informe_de_la_lista(self):
        for iso, lista in self.d['p'].items():
            simbolos = {f['s'] for f in self.inf[iso]}
            for _, _, sim, _ in lista: self.assertIn(sim, simbolos, iso)

    def test_cobertura(self):
        n = sum(len(v) for v in self.d['p'].values())
        self.assertGreater(len(self.d['p']), 180)   # casi todos los países tienen al menos un informe contado
        self.assertGreater(n, 450)                  # y la mayoría de los informes de los ciclos 2 a 4


if __name__ == '__main__':
    unittest.main()
