#!/usr/bin/env python3
"""Pruebas del seguimiento de recomendaciones del EPU (T75): la unión de texto, Estados y respuesta con fragmentos
incrustados (adaptados de A/HRC/26/4, Afganistán, y A/HRC/29/8/Add.1, España), y los datos ya generados en data/seguimiento:
estructura, que cada examen tenga exactamente las recomendaciones que publica data/epu.js, que «r» solo tome sus tres
valores y que en/es no arrastren cabeceras del PDF (GE.xx-xxxxx). No necesita los textos de /var/lib/atlas ni red.
  python3 -I tests/epu_seguimiento_test.py"""
import glob, json, os, re, sys, unittest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import epu_recomendaciones as E  # noqa: E402
import epu_seguimiento as S  # noqa: E402

INFORME = """Contents
II. Conclusions and/or recommendations ....................................................................
II. Conclusions and/or recommendations**
136. The recommendations formulated during the interactive dialogue and listed
below have been examined by Afghanistan and enjoy its support:
136.1. Ratify the Optional Protocol to the Convention against Torture (Denmark);
136.2. Continue its efforts to protect the rights of
women (Pakistan) (Sri
Lanka);

14

GE.14-12345

\fA/HRC/26/4

137. The following recommendations will be examined by Afghanistan, which will
provide responses in due time, but no later than the twenty-sixth session of the Human Rights Council in June 2014:
137.1. Consider ratifying the Convention on migrant workers (Uruguay);
137.2. Establish a moratorium on the death penalty (Spain);
137.3. Strengthen the national human rights institution (Norway);
138. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State(s).
"""
INFORME_ES = """II. Conclusiones y/o recomendaciones
136. El Afganistán examinó las recomendaciones y cuentan con su apoyo:
136.1 Ratificar el Protocolo Facultativo de la Convención contra la Tortura (Dinamarca);
136.2 Proseguir sus esfuerzos para proteger los derechos de las mujeres (Pakistán) (Sri Lanka);
137. El Afganistán examinará las recomendaciones siguientes:
137.1 Considerar la posibilidad de ratificar la Convención sobre los trabajadores migratorios (Uruguay);
137.2 Establecer una moratoria de la pena de muerte (España);
137.3 Fortalecer la institución nacional de derechos humanos (Noruega);
138. Todas las conclusiones y/o recomendaciones que figuran en el presente informe reflejan la posición de los Estados.
"""
ADENDO = """Recommendations accepted
4.
Afghanistan supports the following recommendations: 137.3.
5.
Afghanistan takes note of the following recommendations: 137.1.
6.
Afghanistan supports the following recommendations in part: 137.2.
"""

GE = re.compile(r'GE\.\d{2}-\d{4,6}')
FECHA = re.compile(r'^\d{4}-\d{2}-\d{2}$')
N = re.compile(r'^\d{2,3}\.\d{1,3}$')


def leer(p):
    with open(p, encoding='utf-8') as fh: return json.load(fh)


def efectivas(ex):
    """[(rec, fuente efectiva)] de un examen ya compactado."""
    return [(r, S.fuente(ex, r)) for r in ex['recs']]


class Union(unittest.TestCase):
    def setUp(self):
        self.recs, self.motivo = S.recomendaciones(INFORME, INFORME_ES, ADENDO)
        self.por_n = {r['n']: r for r in self.recs}

    def test_tantas_como_contar(self):
        self.assertEqual(self.motivo, '')
        self.assertEqual(len(self.recs), E.contar(INFORME)[0])
        self.assertEqual([r['n'] for r in self.recs], ['136.1', '136.2', '137.1', '137.2', '137.3'])

    def test_respuesta_y_fuente(self):
        r = self.por_n
        self.assertEqual((r['136.1']['r'], r['136.1']['f']), ('apoyada', 'informe'))
        self.assertEqual((r['137.3']['r'], r['137.3']['f']), ('apoyada', 'adendo'))
        self.assertEqual((r['137.1']['r'], r['137.1']['f']), ('tomó nota', 'adendo'))
        # «in part»: no se fuerza, y sin respuesta no hay fuente
        self.assertNotIn('r', r['137.2']); self.assertNotIn('f', r['137.2'])

    def test_sin_adendo_queda_null(self):
        recs, _ = S.recomendaciones(INFORME, None, None)
        self.assertTrue(all('r' not in x for x in recs if x['n'].startswith('137.')))

    def test_texto_estados_y_espanol(self):
        r = self.por_n['136.2']
        self.assertEqual(r['en'], 'Continue its efforts to protect the rights of women')
        self.assertEqual(r['por'], ['Pakistan', 'Sri Lanka'])
        self.assertEqual(r['es'], 'Proseguir sus esfuerzos para proteger los derechos de las mujeres')
        for x in self.recs:
            self.assertFalse(GE.search(x['en']) or '\f' in x['en'] or 'A/HRC/26/4' in x['en'], x)

    def test_claves_vacias_se_omiten(self):
        recs, _ = S.recomendaciones(INFORME, None, ADENDO)
        self.assertTrue(all('es' not in x for x in recs))
        self.assertTrue(all(set(x) <= set(S.CLAVES) for x in recs))

    def test_informe_sin_lista(self):
        recs, motivo = S.recomendaciones(INFORME.replace('137.2.', '137.4.'), None, None)
        self.assertIsNone(recs); self.assertIn('salta', motivo)
        self.assertEqual(S.recomendaciones('nada', None, None), (None, 'sin sección de recomendaciones'))

    def test_compactar_no_pierde_la_fuente(self):
        ex = S.compactar(self.recs)
        self.assertEqual(ex['f'], 'adendo')   # 2 del adendo, 1 del informe
        self.assertEqual([S.fuente(ex, r) for r in ex['recs']], [x.get('f') for x in self.recs])
        self.assertEqual(S.compactar([{'n': '1.1', 'en': 'x'}]), {'f': None, 'recs': [{'n': '1.1', 'en': 'x'}]})


FICHEROS = sorted(glob.glob(os.path.join(RAIZ, 'data/seguimiento/*.json')))


class Datos(unittest.TestCase):
    """Los JSON ya generados (están en el repositorio, así que esto corre también en la CI)."""
    @classmethod
    def setUpClass(cls):
        cls.datos = {os.path.basename(p)[:-5]: leer(p) for p in FICHEROS}
        cls.aud = leer(S.AUDITORIA)
        cls.pub = S.publicadas()

    def examenes(self):
        for d in self.datos.values():
            yield from d['examenes']

    def test_hay_datos(self):
        self.assertGreater(len(self.datos), 150)

    def test_estructura(self):
        for iso, d in self.datos.items():
            self.assertEqual(set(d), {'iso', 'examenes'}); self.assertEqual(d['iso'], iso); self.assertTrue(d['examenes'])
            for ex in d['examenes']:
                self.assertEqual(set(ex), {'s', 'ciclo', 'fecha', 'add', 'enlace', 'enlace_add', 'f', 'recs'}, ex['s'])
                self.assertIn(ex['ciclo'], (2, 3, 4)); self.assertRegex(ex['fecha'], FECHA)
                self.assertEqual(E.ciclo(ex['fecha']), ex['ciclo'])
                self.assertRegex(ex['enlace'], r'^https?://')
                self.assertTrue((ex['add'] is None) or ex['add'].startswith(ex['s'] + '/Add'), ex['s'])
                if ex['enlace_add'] is not None: self.assertRegex(ex['enlace_add'], r'^https?://')
                self.assertIn(ex['f'], ('informe', 'adendo', None))
                ns = [r['n'] for r in ex['recs']]
                self.assertEqual(len(ns), len(set(ns)), ex['s'])
                for r in ex['recs']:
                    self.assertLessEqual(set(r), set(S.CLAVES), (ex['s'], r['n']))
                    self.assertRegex(r['n'], N); self.assertTrue(r['en'].strip(), (ex['s'], r['n']))
                    if 'por' in r: self.assertTrue(r['por'] and all(isinstance(x, str) and x for x in r['por']))
                    if 'revisar' in r: self.assertIs(r['revisar'], True)

    def test_coherente_con_epu_js(self):
        aqui = {ex['s']: len(ex['recs']) for ex in self.examenes()}
        self.assertEqual(aqui, self.pub)   # mismos exámenes y misma cifra que el mapa
        self.assertEqual(self.aud['distintas_de_epu_js'], [])

    def test_r_solo_tres_valores(self):
        for ex in self.examenes():
            for r, f in efectivas(ex):
                self.assertIn(r.get('r'), S.RESPUESTAS, (ex['s'], r['n']))
                self.assertIsNot(r.get('r'), '')
                if r.get('r') is None: self.assertNotIn('f', r)
                else: self.assertIn(f, ('informe', 'adendo'), (ex['s'], r['n']))
                if 'f' in r: self.assertNotEqual(r['f'], ex['f'])   # compactado: solo se repite si es distinta

    def test_sin_cabeceras_del_pdf(self):
        for ex in self.examenes():
            for r in ex['recs']:
                for k in ('en', 'es'):
                    if k in r:
                        self.assertFalse(GE.search(r[k]), (ex['s'], r['n'], k))
                        self.assertNotIn('\f', r[k]); self.assertNotIn('\n', r[k])

    def test_auditoria_cuadra(self):
        a, t = self.aud, self.aud['total']
        recs = [(ex, r, f) for ex in self.examenes() for r, f in efectivas(ex)]
        self.assertEqual(t['recomendaciones'], len(recs))
        self.assertEqual(t['con_lista'], sum(1 for _ in self.examenes()))
        self.assertEqual(t['con_es'], sum('es' in r for _, r, _ in recs))
        self.assertEqual(t['desde_informe'], sum(f == 'informe' for _, _, f in recs))
        self.assertEqual(t['desde_adendo'], sum(f == 'adendo' for _, _, f in recs))
        self.assertEqual(t['null'], sum('r' not in r for _, r, _ in recs))
        self.assertEqual(t['informes'], t['con_lista'] + t['sin_lista'])
        self.assertEqual(t['sin_lista'], len([x for x in a['sin_lista'] if x['iso']]))
        self.assertTrue(all(x['motivo'] for x in a['sin_lista']))
        for x in t: self.assertEqual(t[x], sum(c[x] for c in a['ciclos'].values()), x)

    def test_fecha_reproducible(self):
        inf = leer(os.path.join(RAIZ, 'data/fuentes/epu_informes.json'))
        fechas = [x['d'][:10] for l in inf['paises'].values() for f in l if E.ciclo(f['d']) > 1
                  for x in [f] + ([f['add']] if (f.get('add') or {}).get('d') else [])]
        self.assertEqual(self.aud['generado'], max(fechas))


if __name__ == '__main__':
    unittest.main()
