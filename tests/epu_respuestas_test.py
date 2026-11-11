#!/usr/bin/env python3
"""Pruebas de las respuestas del Estado a las recomendaciones del EPU (T75): «apoyada» / «tomó nota» desde el informe del Grupo de
Trabajo o desde el adendo, y null cuando no está escrito de forma inequívoca para ese número. Los fragmentos son trozos reales y
cortos de los informes (A/HRC/…), recortados a pocas recomendaciones. Sin red.
  python3 -I tests/epu_respuestas_test.py"""
import os, sys, unittest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import epu_recomendaciones as E  # noqa: E402
import epu_respuestas as P  # noqa: E402

A, N = 'apoyada', 'tomó nota'

# Ciclo 2 (A/HRC/26/4, Afganistán, recortado): apoyadas, «se examinarán» y «did not enjoy the support»; «138.» va solo en su línea
INFORME_C2 = """Contents
II. Conclusions and/or recommendations ....................................................................
II. Conclusions and/or recommendations**
136. The recommendations formulated during the interactive dialogue and listed
below have been examined by Afghanistan and enjoy its support:
136.1. Ratify the Optional Protocol (Denmark);
136.2. Continue its efforts (Pakistan);
137. The following recommendations will be examined by Afghanistan, which will
provide responses in due time, but no later than the twenty-sixth session of the Human Rights Council in June 2014:
137.1. Consider ratifying the Convention (Uruguay);
137.2. Establish a moratorium (Spain);
137.3. Strengthen (Norway);
138.

The recommendations below did not enjoy the support of Afghanistan:
138.1
Re-establish the moratorium on executions (France);
139. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State(s).
"""

# Ciclo 4 (A/HRC/63/10, Dinamarca, recortado): todo «se examinará»; la respuesta va en el adendo
INFORME_C4 = """II. Conclusions and/or recommendations
125. The following recommendations will be examined by Denmark, which will provide responses in due time, but no later
than the sixty-third session of the Human Rights Council:
125.1 Ratify (Chile);
125.2 Ratify (Iraq);
125.3 Withdraw (Ukraine);
125.4 Accede (Spain);
125.5 Consider (Mexico);
125.6 Continue (Benin);
126. All conclusions and/or recommendations contained in the present report reflect the position of the submitting State(s).
"""
NUM_C4 = [f'125.{k}' for k in range(1, 7)]

# Adendo con cabeceras y listas (A/HRC/29/8/Add.1, España)
ADENDO_LISTAS = """Recommendations accepted
4.
Spain supports the following recommendations: 125.1, 125.2
and 125.4.
5.
Spain supports the following recommendations in part: 125.3, 125.5.
6.
Spain takes note of the following recommendations: 125.6.
"""

# Adendo con «(a) Accepted.» / «(b) Noted.» (A/HRC/63/10/Add.1, Dinamarca)
ADENDO_ENUMERADO = """The Government of the Kingdom of Denmark
accepts 4 recommendations and notes 2 as follows:
(a)

Accepted.

125.1, 125.3, 125.4,
125.6.
(b)

Noted.

125.2, 125.5.
"""

# Adendo en tabla: número y, en la línea siguiente, la posición (A/HRC/44/17/Add.1, Kuwait)
ADENDO_TABLA = """Recommendation No.
Position of Kuwait
125.1

Rejected

125.2

Accepted

125.3

Partially supported

125.4

10

Accepted

125.5

Note taken

125.6

Accepted
"""


class Informe(unittest.TestCase):
    def test_ciclo2_cada_lista_su_respuesta(self):
        nums = E.numeros(INFORME_C2)
        self.assertEqual(nums, ['136.1', '136.2', '137.1', '137.2', '137.3', '138.1'])
        r = P.respuestas(INFORME_C2, None, nums)
        self.assertEqual({n: v['r'] for n, v in r.items()}, {'136.1': A, '136.2': A, '137.1': None, '137.2': None, '137.3': None, '138.1': N})
        self.assertEqual(r['136.1']['fuente'], 'informe'); self.assertIsNone(r['137.1']['fuente'])

    def test_frases_del_informe(self):
        for frase, c in [('have been examined by Ghana and enjoy the support of Ghana:', A),
                         ('have been examined by Greece and enjoyed the support of Greece:', A),
                         ('have been examined by Ghana and have been noted by Ghana:', N),
                         ('The recommendations below did not enjoy the support of Israel and would thus be noted:', N),
                         ('Recommendations which did not enjoy TGoNU support', N),
                         ('Lebanon rejects the recommendations below:', N),
                         ('Partially supported', 'parcial'),
                         ('Canada accepts 222 recommendations and notes 78.', 'mixta'),
                         ('Uzbekistan considers that recommendations below are already implemented:', None)]:
            self.assertEqual(P.clase(frase), c, frase)

    def test_frase_ausente_o_desordenada_no_da_respuesta(self):
        roto = INFORME_C2.replace('below have been examined by Afghanistan and enjoy its support:', '24 GE.14-02963 see 130.2 and 130.3 above:')
        self.assertIsNone(P.del_informe(roto)['136.1'])

    def test_numeros_igual_que_contar(self):
        self.assertEqual(len(E.numeros(INFORME_C4)), E.contar(INFORME_C4)[0])
        self.assertIsNone(E.numeros('Texto cualquiera'))

    def test_indice_con_puntos_no_es_la_seccion(self):
        # A/HRC/29/16 (Guyana): el índice casaba como encabezado y «19.1 per cent» se contaba como una recomendación
        t = 'II. Conclusions and/or recommendations . . . . . . . . 20\nThe rate fell from\n19.1 per cent in 1990.\n' + INFORME_C4
        self.assertEqual(E.contar(t), (6, ''))


class Adendo(unittest.TestCase):
    def test_listas_con_cabecera(self):
        r = P.respuestas(INFORME_C4, ADENDO_LISTAS, NUM_C4)
        self.assertEqual({n: v['r'] for n, v in r.items()}, {'125.1': A, '125.2': A, '125.3': None, '125.4': A, '125.5': None, '125.6': N})
        self.assertEqual(r['125.1']['fuente'], 'adendo'); self.assertIsNone(r['125.3']['fuente'])   # «in part»: no se fuerza

    def test_cabeceras_enumeradas(self):
        r = P.respuestas(INFORME_C4, ADENDO_ENUMERADO, NUM_C4)
        self.assertEqual({n: v['r'] for n, v in r.items()}, {'125.1': A, '125.2': N, '125.3': A, '125.4': A, '125.5': N, '125.6': A})

    def test_tabla(self):
        r = P.respuestas(INFORME_C4, ADENDO_TABLA, NUM_C4)   # «10» es el número de página, entre la fila y su etiqueta
        self.assertEqual({n: v['r'] for n, v in r.items()}, {'125.1': N, '125.2': A, '125.3': None, '125.4': A, '125.5': N, '125.6': A})

    def test_tabla_con_celda_de_pais(self):
        # A/HRC/36/10/Add.1 (India): número, país y posición en líneas separadas
        a = 'Recommendation made by\nResponse by the Government of India\n' + ''.join(
            f'125.{k}\n\n{p}\n\n{e}\n\n' for k, p, e in [(1, 'Estonia', 'Noted'), (2, 'Portugal', 'Noted'), (3, 'Botswana', 'Accepted'),
                                                       (4, 'Norway', 'Accepted'), (5, 'Czechia', 'Accepted'), (6, 'Rwanda', 'Noted')])
        r = P.respuestas(INFORME_C4, a, NUM_C4)
        self.assertEqual([r[n]['r'] for n in NUM_C4], [N, N, A, A, A, N])

    def test_filas_en_linea_y_rangos(self):
        # A/HRC/44/15/Add.1: «80.15–16 Noted. 80.17 Accepted.»; A/HRC/61/5/Add.1: «117.84, 85, 86 Supported»
        a = '125.1–3 Noted. 125.4 Accepted. 125.5 Noted. 125.6 Accepted. 125.2 Noted. 125.4 Accepted.'
        r = P.respuestas(INFORME_C4, a, NUM_C4)
        self.assertEqual([r[n]['r'] for n in NUM_C4], [N, N, N, A, N, A])
        r = P.respuestas(INFORME_C4, 'Supported: 125.1–125.3.\n\nNoted: 125.4, 5, 6.', NUM_C4)
        self.assertEqual([r[n]['r'] for n in NUM_C4], [A, A, A, N, N, N])

    def test_frase_detras_del_numero(self):
        a = ('29. Recommendation 125.4 is not accepted. This is because the law guarantees it.\n'
             '30. Recommendations 125.1 and 125.2 enjoy the support of the Government of Sierra Leone.\n')
        r = P.respuestas(INFORME_C4, a, NUM_C4)
        self.assertEqual((r['125.1']['r'], r['125.2']['r'], r['125.4']['r'], r['125.3']['r']), (A, A, N, None))

    def test_dos_respuestas_distintas_es_null(self):
        a = 'Spain supports the following recommendations: 125.1, 125.2.\nSpain takes note of the following recommendations: 125.2, 125.3.'
        r = P.respuestas(INFORME_C4, a, NUM_C4)
        self.assertEqual((r['125.1']['r'], r['125.2']['r'], r['125.3']['r']), (A, None, N))

    def test_informe_y_adendo_en_desacuerdo_es_null(self):
        # A/HRC/56/10/Add.1: «it supports eight additional recommendations that it initially took note of»
        r = P.respuestas(INFORME_C2, 'The following recommendations are supported: 138.1; 137.2.', E.numeros(INFORME_C2))
        self.assertIsNone(r['138.1']['r']); self.assertEqual(r['137.2'], {'r': A, 'fuente': 'adendo'}); self.assertEqual(r['136.1']['r'], A)

    def test_texto_libre_sin_numeros_es_null(self):
        a = ('Burundi welcomes the 287 recommendations addressed to it, especially those concerning the promotion of socioeconomic '
             'development. Effective measures have been taken. The Government accepts most of them.')
        self.assertTrue(all(v == {'r': None, 'fuente': None} for v in P.respuestas(INFORME_C4, a, NUM_C4).values()))

    def test_todas_excepto_no_se_deduce(self):
        a = 'The Government of Azerbaijan accepts totally and partially all recommendations\nexcept 125.1, 125.2, 125.3 and 125.4.'
        self.assertTrue(all(v['r'] is None for v in P.respuestas(INFORME_C4, a, NUM_C4).values()))

    def test_etiqueta_de_la_recomendacion_anterior_no_pasa_a_la_siguiente(self):
        # A/HRC/25/4/Add.1 (Senegal): la explicación de la anterior acaba en «is rejected» y empieza la siguiente
        a = ('3.\nSenegal has thus demonstrated its commitment. The recommendation is therefore irrelevant and is rejected.\n\n'
             '125.3 Accede to the Second Optional Protocol (Benin)\n4.\nSenegal has signed the principal instruments.\n')
        self.assertIsNone(P.respuestas(INFORME_C4, a, NUM_C4)['125.3']['r'])

    def test_dos_columnas_seguidas_no_se_adivinan(self):
        # A/HRC/36/7/Add.1 (Indonesia): las dos cabeceras de columna van juntas y luego todos los números
        a = 'the complete list appears on the table below.\nRecommendations Supported\n\nRecommendations Noted\n\n125.1; 125.2; 125.3;\n125.4.\n\n125.5; 125.6.'
        self.assertTrue(all(v['r'] is None for v in P.respuestas(INFORME_C4, a, NUM_C4).values()))

    def test_titulo_a_medias_no_se_hereda(self):
        # A/HRC/55/17/Add.1 (Cuba): «taken / under advisement» no es un título; la lista de debajo no hereda «supported»
        a = ('Recommendations supported by the Government of Cuba\n(4)\n13.\n125.1; 125.2; 125.3; 125.4.\n'
             'Recommendations that the Government of Cuba has taken\nunder advisement (2)\n14.\n125.5; 125.6.\n')
        r = P.respuestas(INFORME_C4, a, NUM_C4)
        self.assertEqual([r[n]['r'] for n in NUM_C4], [A, A, A, A, None, None])

    def test_titulo_de_apartado_se_hereda(self):
        # A/HRC/61/4/Add.1 (Belarús): listas sueltas bajo «Recommendations that are accepted»
        a = ('Recommendations that are accepted\n125.1 accepted as implemented: Belarus ratified the Optional Protocol in 2004.\n'
             '125.2–125.4\n\nRecommendations that are not supported and are thus noted\n125.5–125.6\nBelarus will continue to study it.\n')
        r = P.respuestas(INFORME_C4, a, NUM_C4)
        self.assertEqual([r[n]['r'] for n in NUM_C4], [A, A, A, A, N, N])

    def test_remision_no_es_respuesta(self):
        a = 'which appear in paragraphs 125.1–125.6 of the draft UPR outcome report. Malaysia accepts the following recommendations: 125.2.'
        r = P.respuestas(INFORME_C4, a, NUM_C4)
        self.assertEqual([r[n]['r'] for n in NUM_C4], [None, A, None, None, None, None])

    def test_devuelve_todos_los_numeros(self):
        r = P.respuestas('', '', ['1.1', '1.2'])
        self.assertEqual(r, {'1.1': {'r': None, 'fuente': None}, '1.2': {'r': None, 'fuente': None}})


class Verificacion2026(unittest.TestCase):
    """Casos que encontró la revisión a mano de data/seguimiento contra los textos (noviembre de 2026): un caso por patrón."""
    def r(self, a, informe=INFORME_C4):
        res = P.respuestas(informe, a, E.numeros(informe))
        return [res[n]['r'] for n in E.numeros(informe)]

    def test_adendo_retira_la_respuesta_del_informe(self):
        # A/HRC/49/17/Add.1 (Tailandia): el informe la daba por apoyada y el adendo dice lo contrario
        self.assertEqual(self.r('22.\nAt the same time, Thailand is not in a position to support recommendation 136.1, as the\n'
                                'recommendation requests the removal of the law.', INFORME_C2)[:2], [None, A])
        # A/HRC/37/12/Add.1: «initially supported, is now noted»; A/HRC/22/16/Add.1: «With regard to 128.54, … able to support»
        self.assertEqual(self.r('As a result of the consultation process, recommendation 136.2, which was initially supported, is now noted.',
                                INFORME_C2)[:2], [A, None])
        self.assertIsNone(self.r('3.1\nWith regard to 138.1, given that X, Afghanistan is able to support this\nrecommendation;', INFORME_C2)[-1])

    def test_explicacion_detras_del_numero_contradice_al_informe(self):
        # A/HRC/25/4/Add.1 (Senegal): el informe dice «enjoy the support» y el adendo, debajo del número, «is rejected»
        a = '136.2 Eliminate the caste system (Romania)\n18.\nIn Senegal, discrimination is not tolerated. This\nrecommendation is rejected.\n'
        self.assertEqual(self.r(a, INFORME_C2)[:2], [A, None])

    def test_etiqueta_mixta_es_null(self):
        # A/HRC/54/10/Add.1 (Bahamas): «Note/Support»
        a = 'Recommendation\nPosition\n' + ''.join(f'125.{k}\n\n{e}\n\n' for k, e in
                                                   [(1, 'Support'), (2, 'Note/Support'), (3, 'Note'), (4, 'Support'), (5, 'Supported/noted'), (6, 'Note')])
        self.assertEqual(self.r(a), [A, None, N, A, None, N])

    def test_celda_partida_por_el_salto_de_pagina(self):
        # A/HRC/62/15/Add.1 (San Cristóbal y Nieves): la celda acaba en «;», la etiqueta va en medio y sigue en la página siguiente;
        # «125.7\n125.8» sin «;» son dos filas
        inf = INFORME_C4.replace('125.6 Continue (Benin);\n', ''.join(f'125.{k} Continue (Benin);\n' for k in range(6, 11)))
        a = ('Recommendations\n\nPosition\n\n125.1\n\nNoted\n\n125.2\n\nNoted\n\n125.3; 125.4;\n\nSupported\n\nA/HRC/62/15/Add.1\n\n'
             'Recommendations\n\nPosition of X\n\n125.5; 125.6\n125.7\n\nNoted\n\n125.8\n\nSupported\n\n125.9; 125.10; Noted\n125.11\n\nSupported\n\n')
        self.assertEqual(self.r(a, inf), [N, N, A, A, A, A, N, A, N, N])

    def test_cabecera_con_dos_verbos_vale_la_de_la_lista(self):
        # A/HRC/47/17/Add.1 (Nauru) y A/HRC/55/7/Add.1 (Colombia)
        a = ('In light of paragraph 17, the Republic ACCEPTS 3 recommendations and NOTES\nthe 2 below:\n(a)\nRecommendation 125.1 (Spain);\n'
             '(b)\nRecommendation 125.2 (Argentina).\n')
        self.assertEqual(self.r(a)[:2], [N, N])
        a = ('the Colombian State accepts 223 and, therefore, takes note of\nthe following three recommendations:\nRecommendations\n\n'
             '125.4\n\nRatify the Convention\n(France);\n\n125.5\n\nConsider ratifying the Convention\n(Mauritius) (Senegal);\n\n125.6\n\nAbolish it (Costa Rica).\n')
        self.assertEqual(self.r(a), [None, None, None, N, N, N])

    def test_titulo_parcial_manda_sobre_la_fila(self):
        # A/HRC/46/5/Add.1 (Belarús): «Recommendations that are partially accepted» / «138.32 is accepted in respect of …»
        a = ('Recommendations that are accepted\n25.\n125.1–125.2.\n\nRecommendations that are partially accepted\n26.\n'
             '125.3 is accepted in respect of the criminalization of domestic violence.\n27.\n125.4 is accepted, in respect of the enactment of legislation.\n')
        self.assertEqual(self.r(a)[:4], [A, A, None, None])
        # A/HRC/62/9/Add.1 (Nepal): cabecera «… in part and notes the following part:» y, en la tabla, «Supported»
        a = ('4.\n\nNepal supports the following recommendation in part and notes the following part:\n\nPara. no.\n\nState position\n\n'
             'Comments (optional)\n\n125.1\n\nSupported\n\nGuarantee an independent body\n\nNoted\n\nRemove the limit\n\n' +
             ''.join(f'125.{k}\n\nSupported\n\n' for k in range(2, 7)))
        self.assertIsNone(self.r(a)[0])

    def test_remision_con_with_regard_to(self):
        # A/HRC/31/9/Add.1 (Nepal): «With regard to the recommendations noted in 123.26 and 123.27, the GoN has accepted the visit…»
        a = ('16. Recommendations which don’t enjoy the support of Nepal and thus be noted are given below:\n125.1. Ratify it\n'
             '25. With regard to the recommendations noted in 125.5 and 125.6, the GoN has accepted the visit requests of various mandate holders.')
        self.assertEqual(self.r(a), [N, None, None, None, None, None])

    def test_comentario_contrario_junto_a_la_fila(self):
        # A/HRC/54/10/Add.1 (Bahamas): «Noted – See Anti-Violence Bill 2023» justo antes de «122.187 / Support»
        a = ''.join(f'125.{k}\n\nSupport\n\nThe Government works on it.\n\n' for k in range(1, 4)) + \
            'Noted – See Anti-Violence Bill 2023\n(Protection Against Violence Bill 2023).\n\n125.4\n\nSupport\n\n125.5\n\nNote\n\n125.6\n\nNote\n\n'
        self.assertEqual(self.r(a), [A, A, None, None, N, N])   # el comentario puede ser de la de antes o de la de después
        # A/HRC/29/7/Add.1 (Laos): la etiqueta dice «Noted» y su comentario «accepts this recommendation in part»
        a = ''.join(f'125.{k}\n\nAccepted\n\n' for k in range(1, 6)) + '125.6\n\nNoted\n\nThe Lao PDR accepts this recommendation in part.\n'
        self.assertEqual(self.r(a)[-1], None)

    def test_frases_nuevas(self):
        for frase, c in [('We note recommendations', N), ('Note has been taken of the following recommendations', N),
                         ('The following 132 recommendations have been approved', A), ('These recommendations failed to enjoy Kenya’s support', N),
                         ('Recommendations which don’t enjoy the support of Nepal', N), ('Thailand is not in a position to support recommendation', N),
                         ('Seychelles notes the recommendation', N), ('Recommendation 125.193 is noted only in respect of the phrase', 'parcial')]:
            self.assertEqual(P.clase(frase), c, frase)
        self.assertEqual(P._etiqueta_linea('Note/Support'), 'mixta')
        self.assertIsNone(P._etiqueta_linea('Noted: “Abolish the death penalty…”'))

    def test_lista_que_sigue_tras_punto_y_coma(self):
        # A/HRC/44/9/Add.1 (Kenia): «… acceptance of the following recommendations: Recommendation 143.3: … (Germany);
        # Recommendation 143.4: …»
        a = ('the State now indicates its acceptance of the following recommendations:\nRecommendation 125.3: Review the 2018 Bill and ensure\n'
             'that laws are in line with the right (Germany);\nRecommendation 125.4: Ensure that a human rights approach is reflected\n(Fiji).\n\n'
             'B.\n\nNoted recommendations\n')
        self.assertEqual(self.r(a), [None, None, A, A, None, None])

    def test_respuesta_de_la_fila_anterior_no_es_cabecera(self):
        # A/HRC/63/13/Add.1 (Seychelles): «108.8 / Seychelles accepts the recommendation. / 108.9 / Seychelles notes the recommendation.»
        a = ''.join(f'125.{k}\n\nSeychelles {v} the recommendation.\n\n' for k, v in
                    [(1, 'accepts'), (2, 'notes'), (3, 'accepts'), (4, 'accepts'), (5, 'notes'), (6, 'accepts')])
        self.assertEqual(self.r(a), [A, N, A, A, N, A])

    def test_remision_suelta_no_se_lleva_la_fila_siguiente(self):
        # A/HRC/25/5/Add.1 (China): «See 186.1» y, tras una línea en blanco, la fila «186.14.»
        a = 'No.\nPosition\n125.1.\n\nAccepted\n\n125.2.\n\nNot Accepted\nSee 125.1\n\n125.3.\n\nAccepted\n\n125.4.\n\nNot Accepted\nSee 125.1\n\n125.5.\n\nAccepted\n\n125.6.\n\nAccepted\n'
        self.assertEqual(self.r(a), [A, N, A, N, A, A])

    def test_parte_de_respuesta_mixta_no_es_etiqueta(self):
        # A/HRC/57/5/Add.1 (Afganistán): «109.51 – Partially accepted: … (a) Accepted: “…” (b) Noted: “Abolish…”»
        a = ''.join(f'{k + 10}.\n125.{k} – Accepted.\n' for k in range(1, 6)) + \
            '16.\n125.6 – Partially accepted: This recommendation contains two issues, as follows:\n(a)\nAccepted: “…and put an end to it, in particular the stoning\nof women.”\n(b)\nNoted: “Abolish the death penalty…”\n'
        self.assertIsNone(self.r(a)[-1])

    def test_vineta_y_lista_cerrada(self):
        # A/HRC/52/14/Add.1 (Brasil): «it will take note of the following two recommendations: • 149.127 …»
        a = 'Brazil supports 125.1, 125.2, 125.3 and 125.4.\n6.\nThe Government will take note of the following\ntwo recommendations:\n• 125.5 Promote policies (Egypt); and\n• 125.6 Provide support (Iran).\n'
        self.assertEqual(self.r(a)[4:], [N, N])
        # A/HRC/57/12/Add.1 (Comoras): «Recommendations / Accepted / 133.1, … 133.237.» y debajo «Noted / 133.8, …»
        self.assertEqual(self.r('Recommendations\nAccepted\n125.1, 125.2, 125.3, 125.4.\n\nNoted\n125.5, 125.6.\n'), [A, A, A, A, N, N])


DIR = os.environ.get('ATLAS_TEXTOS_DIR', '/var/lib/atlas/textos')


@unittest.skipUnless(os.path.exists(os.path.join(DIR, 'txt', 'A_HRC_29_8_Add_1-en.txt')), 'sin los textos de la ONU en este equipo')
class TextosReales(unittest.TestCase):
    """Comprobado a mano contra el PDF: España (lista), Dinamarca (enumerada) y Kuwait (tabla)."""
    def lee(self, s):
        with open(os.path.join(DIR, 'txt', s + '-en.txt'), encoding='utf-8', errors='ignore') as f: t = f.read()
        with open(os.path.join(DIR, 'txt', s + '_Add_1-en.txt'), encoding='utf-8', errors='ignore') as f: a = f.read()
        n = E.numeros(t)
        r = P.respuestas(t, a, n)
        return [sum(1 for v in r.values() if v['r'] == x) for x in (A, N, None)]

    def test_espana_2015(self): self.assertEqual(self.lee('A_HRC_29_8'), [138, 15, 36])     # 36 «in part»
    def test_dinamarca_2026(self): self.assertEqual(self.lee('A_HRC_63_10'), [174, 91, 0])  # «accepts 174 … and notes 91»
    def test_kuwait_2020(self): self.assertEqual(self.lee('A_HRC_44_17'), [230, 66, 6])     # 6 «Partially supported»


if __name__ == '__main__':
    unittest.main()
