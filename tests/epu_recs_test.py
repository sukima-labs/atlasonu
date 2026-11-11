#!/usr/bin/env python3
"""Pruebas del texto de cada recomendación del EPU (T75, scripts/epu_recs.py), con fragmentos reales copiados de los
informes del Grupo de Trabajo: Argentina 2012 (A/HRC/22/4), Congo 2014 (A/HRC/25/16), Togo 2016 (A/HRC/34/4) y
Afganistán 2019 (A/HRC/41/5, en inglés y en español). Sin red. Si están los textos completos (ATLAS_TEXTOS_DIR, en
ct/129 sk-atlas), comprueba además todos los informes de los ciclos 2 a 4.
  python3 -I tests/epu_recs_test.py"""
import json, os, sys, unittest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import epu_recomendaciones as E  # noqa: E402
import epu_recs as R  # noqa: E402

# A/HRC/22/4 (Argentina, 2012): número con punto final, Estados separados por comas, y entre 99.1 y 99.2 un salto de
# página con la nota «**» del título, el número de página y la cabecera. El párrafo final no es del original.
ARGENTINA = """II. Conclusions and/or recommendations**
99.
The following recommendations will be examined by Argentina which will
provide responses in due time, but no later than the 22nd session of the Human Rights
Council in March 2013.
99.1. Ratify the new optional protocol to the Convention on the Rights of the
Child (Portugal);

**

14

Conclusions and recommendations have not been edited.

A/HRC/22/4

99.2. Accede to/ratify the 1961 Convention on the Reduction of Statelessness
(Hungary, Portugal, Iraq);
100. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State(s).
"""

# A/HRC/22/4, 99.11 y 99.18 tal cual: llamada de nota pegada («;1») y el cuerpo de la nota (lo que se leyó en el
# diálogo) metido detrás de la recomendación siguiente, antes del número de página
ARG_99_11 = """ Establish and appoint an Ombudsman on the rights of girls, boys and
adolescents (Honduras, Russian Federation, Trinidad and Tobago);1
"""
ARG_99_18 = """ Continue efforts to provide attention to the most disadvantaged sectors
(Cuba);
1

The recommendations as read during the interactive dialogue:
Complete the process of establishment of an Ombudsman on the rights of girls, boys and adolescents
(Honduras);
Continue to improve the legislative system of Argentina with a view to establishing the institution of
the Ombudsman for children and adolescents (Russian Federation);
Appoint an Ombudsman for child and adolescent rights (Trinidad and Tobago).

15

A/HRC/22/4

"""

# A/HRC/25/16 (Congo, 2014): número solo en su línea, salto de página con «GE.14-10049» dentro de 113.4, un paréntesis
# que no es un Estado antes del Estado («(APIC) (Estonia)») y, en 113.7, el PDF puso el número del párrafo siguiente
# («114.») antes del texto. En el original la sección empieza con la lista 112; aquí se pone el título justo antes de la
# 113, se cortó en 114.1 y se añadió el párrafo final.
CONGO = """II. Conclusions and/or recommendations
113. The following recommendations will be examined by the Congo which will
provide responses in due time, but no later than the twenty-fifth session of the Human
Rights Council in March 2014:
113.1
Ratify the Kampala amendments to the Rome Statute, if possible with
a view to contributing to the activation of the jurisdiction of the International
Criminal Court over the crime of aggression at the beginning of 2017
(Liechtenstein);
113.2
Ratify the Agreement on the Privileges and Immunities of the ICC
(APIC) (Estonia);
113.3
Consider becoming a party to the Optional Protocol to the CRC on a
communications procedure (Thailand);
113.4
Fully implement all obligations under the Rome Statute in its
national legislation, including by incorporating provisions to cooperate
promptly and fully with the ICC, and to investigate and prosecute genocide,
crimes against humanity and war crimes effectively before its national courts
(Netherlands);

22

GE.14-10049

\fA/HRC/25/16

113.5
Extend a standing invitation to all thematic special procedures
(Montenegro);
113.6
Consider issuing a standing invitation to the special procedures
(Slovenia);
113.7
114.

Extend a standing invitation for all mandate holders (Hungary).

Congo considers that the recommendations below cannot be accepted:
114.1
Guarantee equal rights for all citizens, and fight against all forms of
discrimination based on sexual orientation or gender identity (France);
115. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State(s).
"""

# A/HRC/34/4 (Togo, 2016): título con asteriscos de nota en caracteres privados del PDF, Estado partido entre líneas
# («(Côte\\nd’Ivoire)») y un punto que agrupa tres recomendaciones con su Estado cada una
TOGO = """\fA/HRC/34/4

II. Conclusions and/or recommendations
128. The recommendations formulated during the interactive dialogue/listed below
have been examined by Togo and enjoy the support of Togo:
128.1 Continue its efforts to ratify international human rights treaties (Côte
d’Ivoire);
128.2 Accede to those international legal instruments to which Togo is not yet a
party, in particular the Optional Protocol to the Convention on the Elimination
of All Forms of Discrimination against Women (Gabon);
128.3 Speed up the process of ratification of the Optional Protocol to the
Convention on the Elimination of All Forms of Discrimination against Women
(Georgia); Expedite action on the ratification process of the Optional Protocol
to the Convention on the Elimination of All Forms of Discrimination against
Women (Ghana); Accelerate its ratification process of the Optional Protocol to
the Convention on the Elimination of All Forms of Discrimination against
Women (Mongolia);
129. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State(s).
"""

# A/HRC/41/5 (Afganistán, 2019): dos Estados en paréntesis seguidos («(Kyrgyzstan) (Croatia)»), puntos que agrupan
# recomendaciones de varios Estados; en español, el salto de página («12», «GE.19-05622», cabecera) cae entre 136.6 y 136.7
AFGANISTAN_EN = """II. Conclusions and/or recommendations
136. The following recommendations will be examined by Afghanistan, which will
provide responses in due time, but no later than the forty-first session of the Human
Rights Council:
136.1
Ratify the main instruments related to human rights to which it is not
yet a party (Senegal); Consider acceding to the international instruments to
which it is not a party (Honduras);
136.2
Ratify the International Convention for the Protection of All Persons
from Enforced Disappearance (France);
136.3
Launch a process of accession to the International Convention for the
Protection of All Persons from Enforced Disappearance (Ukraine);
136.4
Consider acceding to the International Convention on the Protection
of the Rights of All Migrant Workers and Members of Their Families
(Honduras);
136.5
Consider acceding to the ILO Indigenous and Tribal Peoples
Convention, among others (Honduras);
136.6
Ratify the Optional Protocol to the Convention on the Elimination of
All Forms of Discrimination against Women (Kyrgyzstan) (Croatia); Sign the
Optional Protocol to the Convention on the Elimination of All Forms of
Discrimination against Women (Portugal);
136.7
Sign the Optional Protocol to the International Covenant on
Economic, Social and Cultural Rights (Portugal);
137. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State(s).
"""
AFGANISTAN_ES = """II. Conclusiones y/o recomendaciones
136. El Afganistán examinará las recomendaciones que figuran a continuación y les
dará respuesta a su debido tiempo, pero a más tardar en el 41 er período de sesiones del
Consejo de Derechos Humanos:
136.1 Ratificar los principales instrumentos relativos a los derechos humanos
en los que aún no es parte (Senegal); considerar la posibilidad de adherirse a
los instrumentos internacionales en los que no es parte (Honduras);
136.2 Ratificar la Convención Internacional para la Protección de Todas las
Personas contra las Desapariciones Forzadas (Francia);
136.3 Iniciar el proceso de adhesión a la Convención Internacional para la
Protección de Todas las Personas contra las Desapariciones Forzadas
(Ucrania);
136.4 Considerar la posibilidad de adherirse a la Convención Internacional
sobre la Protección de los Derechos de Todos los Trabajadores Migratorios y de
Sus Familiares (Honduras);
136.5 Considerar la posibilidad de adherirse al Convenio sobre pueblos
indígenas y tribales, 1989 (núm. 169) de la OIT, entre otros (Honduras);
136.6 Ratificar el Protocolo Facultativo de la Convención sobre la
Eliminación de Todas las Formas de Discriminación contra la Mujer
(Kirguistán) (Croacia); firmar el Protocolo Facultativo de la Convención sobre
la Eliminación de Todas las Formas de Discriminación contra la Mujer
(Portugal);

12

GE.19-05622

\fA/HRC/41/5

136.7 Firmar el Protocolo Facultativo del Pacto Internacional de Derechos
Económicos, Sociales y Culturales (Portugal);
137. Todas las conclusiones y/o recomendaciones que figuran en el presente informe reflejan la posición de los Estados.
"""


def por_n(lista): return {x['n']: x for x in lista}


class Extraer(unittest.TestCase):
    def test_tantos_como_contar(self):
        for t in (ARGENTINA, CONGO, TOGO, AFGANISTAN_EN):
            r = R.extraer(t)
            self.assertEqual(len(r), E.contar(t)[0])
            self.assertEqual([x['n'] for x in r], [x['n'] for x in r if x['n']])   # todos con número

    def test_argentina_2012_salto_de_pagina_y_comas(self):
        r = por_n(R.extraer(ARGENTINA))
        self.assertEqual(list(r), ['99.1', '99.2'])
        self.assertEqual(r['99.1']['en'], 'Ratify the new optional protocol to the Convention on the Rights of the Child')
        self.assertEqual(r['99.1']['por'], ['Portugal'])          # sin «**», «14», la nota ni «A/HRC/22/4»
        self.assertEqual(r['99.2']['en'], 'Accede to/ratify the 1961 Convention on the Reduction of Statelessness')
        self.assertEqual(r['99.2']['por'], ['Hungary', 'Portugal', 'Iraq'])
        self.assertFalse(any(x['revisar'] for x in r.values()))

    def test_argentina_notas_al_pie(self):
        llamadas = {'1'}
        cuerpo, por, k, limpio = R._separar(R._limpiar(ARG_99_11, llamadas))
        self.assertEqual(cuerpo, 'Establish and appoint an Ombudsman on the rights of girls, boys and adolescents')
        self.assertEqual(por, ['Honduras', 'Russian Federation', 'Trinidad and Tobago']); self.assertTrue(limpio)
        cuerpo, por, k, limpio = R._separar(R._limpiar(ARG_99_18, llamadas))
        self.assertEqual(cuerpo, 'Continue efforts to provide attention to the most disadvantaged sectors')
        self.assertEqual(por, ['Cuba']); self.assertTrue(limpio)
        # aunque la llamada no se haya visto, la nota «The recommendations as read during the interactive dialogue» se quita
        self.assertEqual(R._separar(R._limpiar(ARG_99_18, set()))[:2], (cuerpo, ['Cuba']))

    def test_congo_2014(self):
        r = por_n(R.extraer(CONGO))
        self.assertEqual(len(r), 8)
        self.assertEqual(r['113.2']['en'], 'Ratify the Agreement on the Privileges and Immunities of the ICC (APIC)')   # «(APIC)» no es un Estado
        self.assertEqual(r['113.2']['por'], ['Estonia'])
        self.assertTrue(r['113.4']['en'].endswith('before its national courts'))          # sin «22», «GE.14-10049» ni cabecera
        self.assertNotIn('GE.', r['113.4']['en']); self.assertEqual(r['113.4']['por'], ['Netherlands'])
        self.assertEqual(r['113.7']['en'], 'Extend a standing invitation for all mandate holders')
        self.assertEqual(r['113.7']['por'], ['Hungary'])
        self.assertTrue(r['113.7']['revisar'])        # texto reordenado por el PDF: se avisa
        self.assertEqual(r['114.1']['por'], ['France']); self.assertFalse(r['114.1']['revisar'])
        self.assertNotIn('Congo considers', r['113.7']['en'] + r['114.1']['en'])

    def test_togo_2016_estado_partido_y_punto_agrupado(self):
        r = R.extraer(TOGO)
        self.assertEqual([x['n'] for x in r], ['128.1', '128.2', '128.3'])
        self.assertEqual(r[0]['en'], 'Continue its efforts to ratify international human rights treaties')
        self.assertEqual(r[0]['por'], ['Côte d’Ivoire'])           # tal como viene, con su apóstrofo
        self.assertEqual(r[2]['por'], ['Georgia', 'Ghana', 'Mongolia'])
        self.assertTrue(r[2]['en'].startswith('Speed up the process of ratification'))
        self.assertIn('(Georgia); Expedite action', r[2]['en'])    # los Estados de en medio se quedan
        self.assertFalse(r[2]['en'].endswith('(Mongolia)'))

    def test_afganistan_2019_en_y_es(self):
        r = por_n(R.extraer(AFGANISTAN_EN, AFGANISTAN_ES))
        self.assertEqual(len(r), 7)
        self.assertEqual(r['136.1']['por'], ['Senegal', 'Honduras'])
        self.assertEqual(r['136.6']['por'], ['Kyrgyzstan', 'Croatia', 'Portugal'])
        self.assertEqual(r['136.2']['es'], 'Ratificar la Convención Internacional para la Protección de Todas las Personas contra las Desapariciones Forzadas')
        self.assertEqual(r['136.6']['es'], 'Ratificar el Protocolo Facultativo de la Convención sobre la Eliminación de Todas las Formas de '
                         'Discriminación contra la Mujer (Kirguistán) (Croacia); firmar el Protocolo Facultativo de la Convención '
                         'sobre la Eliminación de Todas las Formas de Discriminación contra la Mujer')   # sin «12», «GE.19-05622» ni cabecera
        self.assertEqual(r['136.7']['es'], 'Firmar el Protocolo Facultativo del Pacto Internacional de Derechos Económicos, Sociales y Culturales')
        self.assertEqual(r['136.5']['es'], 'Considerar la posibilidad de adherirse al Convenio sobre pueblos indígenas y tribales, 1989 (núm. 169) de la OIT, entre otros')

    def test_es_null_si_no_hay_o_no_cuadra(self):
        self.assertTrue(all(x['es'] is None for x in R.extraer(AFGANISTAN_EN)))
        roto = AFGANISTAN_ES.replace('136.4 Considerar', '136.44 Considerar')   # errata de numeración en el español
        self.assertTrue(all(x['es'] is None for x in R.extraer(AFGANISTAN_EN, roto)))
        falta = AFGANISTAN_ES.replace('136.7 Firmar el Protocolo Facultativo del Pacto Internacional de Derechos\nEconómicos, Sociales y Culturales (Portugal);\n', '')
        self.assertTrue(all(x['es'] is None for x in R.extraer(AFGANISTAN_EN, falta)))   # 6 de 7 (menos del 90 %): nada
        self.assertTrue(all(x['es'] is None for x in R.extraer(AFGANISTAN_EN, 'texto sin la sección')))

    def test_none_si_contar_no_da_cifra(self):
        self.assertIsNone(R.extraer('Texto cualquiera'))
        self.assertIsNone(R.extraer(CONGO.replace('113.3\n', '113.33\n')))   # numeración que salta
        self.assertIsNone(R.extraer(CONGO.replace('113.6\nConsider issuing', 'Consider issuing')))

    def test_errata_de_prefijo_se_normaliza_como_contar(self):
        r = R.extraer(CONGO.replace('113.5\nExtend', '114.5\nExtend'))   # «127.10» por «126.10» en el original
        self.assertEqual(E.contar(CONGO.replace('113.5\nExtend', '114.5\nExtend'))[0], len(r))
        self.assertIn('113.5', [x['n'] for x in r]); self.assertNotIn('114.5', [x['n'] for x in r])

    def test_sin_estados_reconocibles_no_se_adivina(self):
        cuerpo, por, k, limpio = R._separar('Ratify the Convention on the Rights of the Child (CRC);')
        self.assertIsNone(por); self.assertFalse(limpio); self.assertEqual(k, 0)


class Verificacion2026(unittest.TestCase):
    """Textos que la revisión a mano encontró descolocados por las columnas del PDF (noviembre de 2026): un caso por patrón."""
    def limpio(self, t):
        return R._separar(R._limpiar(t, set()))[:2]

    def test_estado_delante_del_texto(self):
        # A/HRC/24/16 170.23 (Cuba): «(Iraq);» sale antes que el texto
        self.assertEqual(self.limpio('\n(Iraq);\n\nReview legislation in conformity with international commitments\n\n'),
                         ('Review legislation in conformity with international commitments', ['Iraq']))

    def test_estado_partido_en_dos_lineas(self):
        # A/HRC/29/8 131.77 (España) y A/HRC/24/16 170.58 (Cuba)
        self.assertEqual(self.limpio('\nLeste);\n\nStrengthen the measures to combat violence against women (Timor-\n\n'),
                         ('Strengthen the measures to combat violence against women', ['Timor-Leste']))
        self.assertEqual(self.limpio('\nof));\n\nPromote and protect all human rights for all (Iran (Islamic Republic\n\n'),
                         ('Promote and protect all human rights for all', ['Iran (Islamic Republic of)']))

    def test_columna_del_medio_detras_del_estado(self):
        # A/HRC/62/15 134.129 (San Cristóbal y Nieves) y A/HRC/24/16 170.122 (Cuba)
        self.assertEqual(self.limpio(' Continue implementing\nframework, 2023–2037 (Cuba);\n\nthe\n\nnational\n\ndevelopment\n\nplanning\n\n'),
                         ('Continue implementing the national development planning framework, 2023–2037', ['Cuba']))
        self.assertEqual(self.limpio(' Continue to maintain\nempowerment of women (Nigeria);\n\nits\n\nsignificant\n\nachievements\n\nin\n\nthe\n\n'),
                         ('Continue to maintain its significant achievements in the empowerment of women', ['Nigeria']))

    def test_nota_al_pie_detras_se_quita(self):
        # A/HRC/44/9 142.41 (Kenia): la nota al pie de otra recomendación sigue al cambiar de página
        self.assertEqual(self.limpio('\nContinue developing public policies, including through special\nmeasures (Ecuador);\n\n'
                                     'request of the Independent Expert on protection against violence and discrimination based on sexual\n'
                                     'orientation and gender identity.”\n\n11\n\n\x0cA/HRC/44/9\n\n'),
                         ('Continue developing public policies, including through special measures', ['Ecuador']))

    def test_recomendacion_agrupada_no_se_reordena(self):
        # «… (Cabo Verde);\nComplete the ratification…»: con mayúscula detrás es otra parte del punto, no una columna
        t = ' Accelerate the ratification of the ICCPR (Cabo Verde);\nComplete the ratification of the ICCPR'
        self.assertEqual(R._reordenar(R._limpiar(t, set(), False).replace(' Complete', '\nComplete')), 
                         R._limpiar(t, set(), False).replace(' Complete', '\nComplete'))

    def test_cada_estado_una_vez(self):
        # A/HRC/24/16 170.2 (Cuba): «Ratify the ICESCR (Romania, …, Poland, …)/ … as soon as possible (Poland)»
        self.assertEqual(R._separar('Ratify the ICESCR (Romania, Poland)/ as soon as possible (Poland)/ at an early stage (Japan);')[1],
                         ['Romania', 'Poland', 'Japan'])

    def test_espanol_con_un_numero_perdido(self):
        # A/HRC/34/12 (Moldova): el español no trae 2 de 209 números; los demás sí van, y el anterior al perdido no
        en = AFGANISTAN_EN
        n = len(R.extraer(en))
        extra = ''.join(f'136.{k} Ratify instrument {k} (Chile);\n' for k in range(8, 31))
        en2 = en.replace('137. All conclusions', extra + '137. All conclusions') if '137. All conclusions' in en else None
        if en2 is None: self.skipTest('fragmento sin párrafo final')
        es2 = AFGANISTAN_ES.replace('137. Todas las conclusiones', ''.join(f'136.{k} Ratificar el instrumento {k} (Chile);\n'
                                                                           for k in range(8, 31) if k != 20) + '137. Todas las conclusiones')
        r = por_n(R.extraer(en2, es2))
        self.assertEqual(len(r), n + 23)
        self.assertIsNone(r['136.20']['es']); self.assertIsNone(r['136.19']['es'])   # el perdido y el de antes (se llevaría su texto)
        self.assertEqual(r['136.21']['es'], 'Ratificar el instrumento 21'); self.assertEqual(r['136.18']['es'], 'Ratificar el instrumento 18')


class Estados(unittest.TestCase):
    def test_nombres(self):
        self.assertEqual(R._nombres('Venezuela (Bolivarian Republic of); Bolivia (Plurinational State of)'),
                         ['Venezuela (Bolivarian Republic of)', 'Bolivia (Plurinational State of)'])
        self.assertEqual(R._nombres('Namibia and Togo'), ['Namibia', 'Togo'])
        self.assertEqual(R._nombres('Trinidad and Tobago'), ['Trinidad and Tobago'])
        self.assertEqual(R._nombres('Denmark 2'), ['Denmark'])       # llamada de nota

    def test_reconoce_erratas_pequenas_y_no_otros_parentesis(self):
        for x in ('United Sates of America', 'Holly See', 'the Netherlands', 'Bolivia(Plurinational State of)', 'Côte d’Ivoire'):
            self.assertTrue(R.es_estado(x), x)
        for x in ('ICCPR', 'Istanbul Convention', 'Paris Principles', '2015–2020', 'No. 189', 'A status'):
            self.assertFalse(R.es_estado(x), x)

    def test_paréntesis_anidados(self):
        cuerpo, por, k, limpio = R._separar('Continue its efforts (Venezuela (Bolivarian Republic of)).')
        self.assertEqual((cuerpo, por, k), ('Continue its efforts', ['Venezuela (Bolivarian Republic of)'], 1))


DIR = os.environ.get('ATLAS_TEXTOS_DIR', '')


@unittest.skipUnless(DIR and os.path.isdir(os.path.join(DIR, 'txt')), 'sin los textos completos (solo en ct/129 sk-atlas)')
class Corpus(unittest.TestCase):
    def test_todos_los_informes(self):
        inf = json.load(open(os.path.join(RAIZ, 'data/fuentes/epu_informes.json'), encoding='utf-8'))['paises']
        leer = lambda p: open(p, encoding='utf-8', errors='ignore').read() if os.path.exists(p) else None
        listas = 0
        for iso, lista in inf.items():
            for f in lista:
                if E.ciclo(f['d']) == 1: continue
                sl = E.slug(f['s'])
                te = leer(os.path.join(DIR, 'txt', f'{sl}-en.txt'))
                if te is None: continue
                r, n = R.extraer(te, leer(os.path.join(DIR, 'txt', f'{sl}-es.txt'))), E.contar(te)[0]
                if n is None: self.assertIsNone(r, f['s']); continue
                listas += 1
                self.assertEqual(len(r), n, f['s'])
                self.assertEqual(len({x['n'] for x in r}), n, f['s'])
                es = [x['es'] is None for x in r]
                self.assertTrue(all(es) or sum(es) <= 0.1 * n + 1, f['s'])   # el español va entero, casi entero o no va
        self.assertGreater(listas, 500)


if __name__ == '__main__':
    unittest.main()
