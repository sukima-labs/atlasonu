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
        # A/HRC/37/12/Add.1: «initially supported, is now noted»; A/HRC/22/16/Add.1: «Upon reconsideration …, the following enjoy
        # the support of Sri Lanka: 3.1 With regard to 128.54, … able to support»: el cambio es explícito y dice la posición final
        self.assertEqual(self.r('As a result of the consultation process, recommendation 136.2, which was initially supported, is now noted.',
                                INFORME_C2)[:2], [A, N])
        self.assertEqual(self.r('3.\nUpon reconsideration of the recommendations received, the following enjoy the\nsupport of Afghanistan:\n'
                                '3.1\nWith regard to 138.1, given that X, Afghanistan is able to support this\nrecommendation;', INFORME_C2)[-1], A)
        # sin decir que cambia, una frase que contradice al informe solo lo pone en duda
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


class Cobertura2026(unittest.TestCase):
    """Segunda revisión (noviembre de 2026): respuestas que el documento da con claridad y salían null. Un caso por causa, con un
    trozo real y corto; y, junto a cada uno, la salvaguarda que no se afloja."""
    def r(self, a, informe=INFORME_C4):
        res = P.respuestas(informe, a, E.numeros(informe))
        return [res[n]['r'] for n in E.numeros(informe)]

    # (1) el informe ya lo dice y el adendo solo comenta, o habla de otras
    def test_adendo_que_solo_comenta_no_anula_el_informe(self):
        # A/HRC/56/13/Add.1 (Mónaco): comenta las apoyadas; el título del apartado siguiente («examined and noted») no es de ellas
        a = ('Comments by the Principality of Monaco on the recommendations which enjoyed its support\n'
             'Recommendations 136.1 to 136.2 on the prohibition of corporal\npunishment of children\n37.\n'
             'While corporal punishment is already expressly prohibited in Monegasque law, the penalties were increased.\n\n'
             'Comments by the Principality of Monaco on the\nrecommendations formulated during the interactive dialogue,\n'
             'examined and noted by Monaco (A/HRC/56/13, para. 98)\nRecommendation 138.1 on improving conditions inside prisons\n')
        self.assertEqual(self.r(a, INFORME_C2), [A, A, None, None, None, N])
        # A/HRC/24/13/Add.1 (Azerbaiyán): «… all recommendations except 110.1» habla de las demás; luego «rejects the recommendations»
        a = ('The Government of Azerbaijan accepts totally and partially all recommendations\nexcept 138.1. The accepted '
             'recommendations will be implemented.\n2.\nAzerbaijan rejects the recommendations\n138.1 presented by the Republic of Armenia.\n')
        self.assertEqual(self.r(a, INFORME_C2)[-1], N)
        # A/HRC/63/9/Add.1 (Bélgica): «… makes them impossible to accept» no es «accept»
        self.assertEqual(self.r('The absence of such a distinction in recommendations 138.1 makes them impossible to accept.', INFORME_C2)[-1], N)

    def test_la_parte_es_de_otro_numero(self):
        # A/HRC/30/15/Add.1 (Jamaica): «Recommendations 119.18, 119.19 and the first part of 120.20»: la parte es de la 120.20
        a = 'Jamaica accepts, as having already been implemented:\n• Recommendations 136.1, 136.2 and the first part of 138.1 regarding discrimination\n'
        self.assertEqual(self.r(a, INFORME_C2), [A, A, None, None, None, None])
        self.assertNotEqual(P.clase('126.35 (in part of Article 400 and 403 of the Criminal Code)'), 'parcial')   # A/HRC/28/10/Add.1

    def test_adendo_que_numera_mal_no_cuenta(self):
        # A/HRC/25/4/Add.1 (Senegal): su «124.13 Eliminate the caste system … (Romania)» es la 125.13 del informe; la 124.13 sigue
        # con la respuesta del informe. Si el texto copiado no es el de otra recomendación, la duda sigue en pie (null)
        inf = INFORME_C2.replace('137.3. Strengthen (Norway);', '137.3. Eliminate the caste system, which leads to stigmatization and\n'
                                 'ostracism of certain groups of the Senegalese society (Romania);')
        a = ('136.2 Eliminate the caste system, which leads to stigmatization and ostracism\nof certain groups of the Senegalese society (Romania)\n'
             '18.\nIn Senegal, discrimination is not tolerated. This recommendation is rejected.\n')
        self.assertEqual(self.r(a, inf)[:2], [A, A])
        self.assertEqual(self.r(a.replace('Eliminate the caste system, which leads to stigmatization and ostracism\nof certain groups of '
                                          'the Senegalese society', 'Abolish castes'), inf)[:2], [A, None])

    # (2) tablas: el salto de página, la etiqueta de otra fila, la última fila, la columna de comentarios suelta
    def test_tabla_partida_por_el_salto_de_pagina(self):
        # A/HRC/58/7/Add.1 (Côte d’Ivoire): encima de «135.66 / Accepted» queda el trozo «Noted: …» de la fila partida de antes
        a = ''.join(f'125.{k}\n\nAccepted\n\n' for k in (1, 2, 3)) + (
            'Recommendation\nnumber\n\nPosition of Côte d’Ivoire\n\nComments\n\nNoted: and transitional justice\nmechanisms\n\n\n\n'
            '125.4\n\nAccepted\n\n125.5\n\nNoted\n\n125.6\n\nAccepted\n\nComments\n\n5.\nIn total, of the 6 recommendations received, '
            '4 were accepted by Côte d’Ivoire,\n1 was noted and 1 was partially accepted.\n')
        self.assertEqual(self.r(a), [A, A, A, A, N, A])   # la última fila no se lleva el recuento de debajo
        # A/HRC/58/15/Add.1 (Etiopía): «58.33. Noted – …» es la etiqueta de la fila de antes, no un comentario de «58.34. Supported.»
        a = ('125.1.\n\nSupported.\n\n125.2.\nNoted – Access to international and local human rights monitors should be allowed.\n'
             '125.3.\n\nSupported.\n\n125.4.\n\nSupported.\n\n125.5.\n\nSupported.\n\n125.6.\n\nNoted – See the response to Rec. 125.2.\n')
        self.assertEqual(self.r(a), [A, N, A, A, A, N])

    def test_columna_de_comentarios_suelta(self):
        # A/HRC/59/16/Add.1 (Egipto): los comentarios de varias filas salen juntos detrás de la última: manda la etiqueta
        a = ''.join(f'125.{k}\n\nAccepted\n\n' for k in (1, 2, 3, 4)) + (
            '125.5\n\nAccepted\n\nAlready implemented.\n\nAlready implemented.\n\nEgypt rejects the erroneous references in this\n'
            'recommendation.\n\nAlready implemented.\n\n125.6\n\nNoted\n\n')
        self.assertEqual(self.r(a), [A, A, A, A, A, N])
        # pero un solo comentario que dice otra cosa sigue anulando la fila (A/HRC/29/7/Add.1, Laos)
        a = ''.join(f'125.{k}\n\nAccepted\n\n' for k in range(1, 6)) + '125.6\n\nNoted\n\nThe Lao PDR accepts this recommendation in part.\n'
        self.assertIsNone(self.r(a)[-1])

    def test_etiqueta_de_la_fila_siguiente_encima_de_su_numero(self):
        # A/HRC/44/13/Add.1 (Granada): la fila 94.105 lleva su «Noted» encima del número; no es de la 94.104
        a = ('125.1\n\nAccepted\n\nGrenada accepts this recommendation.\n\n125.2, 125.3\n\nNoted\n\nGrenada notes these recommendations.\n\n'
             '125.4\n\nAccepted\n\nGrenada supports this recommendation.\n\nNoted\n\nGrenada notes this recommendation.\n\n'
             'Decriminalize abortion\n125.5\n\nThematic area 17: Right to education\n125.6\n\nAccepted\n\nGrenada supports this recommendation.\n')
        self.assertEqual(self.r(a), [A, N, N, A, None, A])

    def test_comentario_que_se_alinea_con_una_parte_no_es_parcial(self):
        # A/HRC/22/11/Add.1 (Suiza): «Rejected» y «aligns itself with the first part of the recommendation. However, … rejects the
        # recommendation»: la posición es la de la etiqueta. En cambio «notes the first part of the recommendation» sí es en parte
        a = ''.join(f'125.{k}.\n\nAccepted\n\n' for k in range(1, 6)) + (
            '125.6.\n\nRejected\n\nSwitzerland aligns itself with the first part of the recommendation. However, Switzerland sees no\n'
            'need for a specific law and therefore rejects the recommendation.\n')
        self.assertEqual(self.r(a)[-1], N)
        self.assertEqual(P._frases_sobre('The Philippines accepts recommendation 131.32. The Philippines notes the first part of the recommendation.'),
                         {'parcial'})

    # (3) erratas de separador
    def test_dos_puntos_por_punto_y_coma_y_listas_que_siguen_en_otra_linea(self):
        # A/HRC/57/6/Add.1 (Chile): «24.305; 24.306:\n24.307: 24.308; 24.309»
        self.assertEqual(self.r('Accepted:\n125.1; 125.2; 125.3:\n125.4: 125.5; 125.6.\n'), [A] * 6)
        # A/HRC/59/4/Add.1 (Italia): «No. 34.6, 7, 8, …, 31,\n32, 33, …»; A/HRC/30/10/Add.1 (Bulgaria): «Rec.123.86–123.90»
        self.assertEqual(self.r('Recommendations accepted\nNo. 125.1, 2,\n3, 4.\n\nRecommendations noted\nRec.125.5–125.6\n'), [A, A, A, A, N, N])
        # un número de párrafo tras la coma no es parte de la lista: «125.3,\n4.\nThe Government …»
        self.assertEqual(self.r('Accepted: 125.1, 125.2, 125.3,\n4.\nThe Government will report.\n')[3], None)

    def test_recuento_no_es_cabecera_parcial(self):
        # A/HRC/60/16/Add.1 (Guyana): «Of the following 60 recommendations …, 58 have been noted and 2 partially noted …» y «103.01 / Noted»
        a = ('9.\nOf the following 6 recommendations formulated during the interactive dialogue and\non which a position had not been '
             'taken yet, 5 have been noted and 1 partially noted and\npartially supported by the State.\nPara. # of Rec.\n\nState position\n\n' +
             ''.join(f'125.0{k}\n\nNoted\n\n' for k in range(1, 6)) + '125.06\n\nSupported/Noted\n\n')
        self.assertEqual(self.r(a), [N, N, N, N, N, None])

    # (4) apartados con etiqueta, frases «X notes this recommendation», «Rejected.», el número que abre su apartado
    def test_apartados_support_note(self):
        # A/HRC/55/10/Add.1 (Alemania): «A. Support» … «B. Note»; una fila sin comentario va en su apartado
        a = ('Responses to the recommendations\nA.\n\nSupport\n125.1\nGermany supports this recommendation.\n125.2\n125.3\n'
             'Germany supports this recommendation.\n\nB.\n\nNote\n125.4\nRefer to 125.3.\n125.5\nGermany notes the recommendation.\n'
             '125.6\nGermany takes note of the recommendation.\n')
        self.assertEqual(self.r(a), [A, A, A, N, N, N])
        # dos títulos de columna seguidos (A/HRC/58/14/Add.1): no se hereda ninguno
        a = ('Accepted recommendations\n\nNoted recommendations\n\n' + ''.join(f'Recommendation 125.{k}, made by Togo, is noted.\n\n' for k in range(1, 6)) +
             'Accepted recommendations\n\nNoted recommendations\n\n125.6\n')
        self.assertIsNone(self.r(a)[-1])

    def test_frases_por_numero(self):
        # A/HRC/31/10/Add.1 (Santa Lucía), A/HRC/52/15/Add.1 (Polonia), A/HRC/29/11/Add.1 (Armenia)
        a = ('125.1. Saint Lucia accepts this recommendation.\n125.2. Saint Lucia notes this recommendation and reiterates its stance.\n'
             '125.3: Rejected. As for the amendment of Article 152(2), there are no grounds to support the Recommendation.\n'
             '125.4. – Supported, under implementation.\n125.5. Saint Lucia accepts this recommendation.\n'
             '125.6. Saint Lucia notes this recommendation.\n')
        self.assertEqual(self.r(a), [A, N, N, A, A, N])
        # la frase sin cerrar que abre la lista siguiente no es de la fila de antes («120.179. – Supported, under implementation.\n\n3.\n
        # Armenia rejects the recommendations» 120.180, …)
        self.assertEqual(P._frases_sobre('. – Supported, under implementation.\n\n3.\nArmenia rejects the recommendations\n'), set())
        self.assertEqual(P.clase('Bhutan is currently not in the position to accept this recommendation'), N)   # A/HRC/27/8/Add.1

    def test_el_numero_abre_su_apartado(self):
        # A/HRC/34/13/Add.1 (Sudán del Sur): «128.33: The recommendation is in conflict with … as such cannot be supported.»;
        # A/HRC/33/6/Add.1 (Samoa): «Recommendation 96.26» y, párrafos abajo, «Samoa notes this recommendation»
        a = ('125.3: The recommendation is in conflict with South Sudan customs and beliefs as such\ncannot be supported.\n'
             'Recommendation 125.5\n11.\nSamoa recently enacted the Crimes Act 2013.\n12.\nSamoa notes this recommendation on the grounds that '
             'the Government will continue its assessment.\n')
        self.assertEqual(self.r(a), [None, None, N, None, N, None])
        # no vale una etiqueta que no se entiende (A/HRC/30/9/Add.1: «84.57 / Taken into consideration»), ni lo que se dice de otra
        # recomendación más abajo (A/HRC/33/4/Add.1: «The recommendation on the Convention against Torture … enjoys support.»)
        self.assertIsNone(self.r('125.1\n\nTaken into consideration\n\nAndorra is negotiating. The recommendation enjoys support.\n')[0])
        self.assertIsNone(self.r('125.1.\nSuriname supports the recommendation related to legislation. In addition, Suriname supports the part '
                                 'of the recommendation related to disability.\n')[0])

    # (5) cambio de posición explícito
    def test_cambio_de_posicion_explicito(self):
        # A/HRC/46/9/Add.1 (Mongolia): «decided to move the recommendation 117.18 into the category of supported recommendations»
        a = ('Mongolia observed that there had occurred a misplacement of 2 recommendations, namely, 136.2 and 138.1 and decided to move '
             'the recommendation 138.1 into the category of supported recommendations and the recommendation 136.2 to the category of noted '
             'recommendations accordingly.\n3.\nTo be precise, the supported recommendations are 136.1 and 138.1 as most of them are in the '
             'process of implementation. And the recommendations that are noted are 136.2.\n')
        self.assertEqual(self.r(a, INFORME_C2)[-1], A)   # (la 136.2 sale también en la frase de las dos: queda null, sin forzar)
        # A/HRC/49/17/Add.1 (Tailandia): «not in a position to support recommendation 51.1» y, en la nota, «had to change its position
        # on this recommendation from immediately accepting to note the recommendation»
        a = ('At the same time, Thailand is not in a position to support recommendation 136.1, as the\nrecommendation requests the '
             'removal of the law.\n\nInitially Thailand had immediately supported 194 recommendations. However, Thailand was later on\n'
             'drawn to the attention regarding the clarification for recommendation 136.1 with explicit reference to the Penal Code. '
             'Thailand, therefore, had to change\nits position on this recommendation from immediately accepting to note the recommendation.\n')
        self.assertEqual(self.r(a, INFORME_C2)[0], N)

    def test_salvaguardas_que_siguen(self):
        # «cannot be accepted in its entirety» (A/HRC/62/12/Add.1) y «The aspect of the Recommendation … is Rejected» (A/HRC/33/12/Add.1)
        self.assertEqual(P.clase('Therefore, the recommendation cannot be accepted in its entirety.'), 'parcial')
        self.assertIsNone(self.r('136.1. Accelerates moves to end child marriage (UK)\n\nThe aspect of the Recommendation on the Law of\n'
                                 'Marriage Act, 1971 is Rejected pending outcome of the Court of Appeal decision.\n', INFORME_C2.replace(
                                     '136.1. Ratify the Optional Protocol (Denmark);', '136.1. Accelerates moves to end child marriage (UK);'))[0])
        # «Following the ratification of ILO Conventions…, Italy has accepted to be reviewed…» no es la cabecera de la fila siguiente
        a = ('Recommendations noted\n125.1, 125.2\n7.\nFollowing the ratification of ILO Conventions C 143 and C189,\nItaly has accepted to be '
             'periodically reviewed.\n125.3\n8.\nItaly does not believe that new treaties are needed.\n125.4\n9.\nNo comment.\n125.5\n10.\nNo comment.\n'
             '125.6\n11.\nNo comment.\n')
        self.assertNotEqual(self.r(a)[2], A)
        # «All the recommendations enjoy support of Montenegro,\nexcept recommendations number: 119.2, …» (A/HRC/23/12/Add.1)
        a = 'I. All the recommendations enjoy support of Montenegro,\nexcept recommendations number: 125.2, 125.4.\nReasons are as follows:\n125.2 – Not in accordance with the law.\n'
        self.assertNotEqual(self.r(a)[1], A)
        # «With regard to the recommendations noted above in 123.28» = mencionadas (A/HRC/31/9/Add.1): no es «tomó nota»
        self.assertEqual(P._frases_sobre('With regard to the recommendations noted above in 125.1, the GoN pursues a policy.'), set())


    # Tercera revisión: valores falsos que encontró la verificación adversarial; cada uno con la regla que lo producía
    def test_falsos_de_la_verificacion(self):
        # A/HRC/23/5/Add.1 (Rumanía): «109.8. Not accepted with respect to ICRMW (see recommendation 2); accepted\nconcerning CPED.»:
        # la etiqueta de la fila no acaba en el «;», la frase sigue y dice lo contrario
        a = ('125.1. Accepted.\n125.2. Not accepted with respect to ICRMW (see recommendation 1); accepted\nconcerning CPED.\n'
             '125.3. Accepted.\n125.4. Not accepted.\n125.5. Accepted.\n125.6. Accepted.\n')
        self.assertEqual(self.r(a), [A, None, A, N, A, A])
        # A/HRC/33/11/Add.1 (Tayikistán): «welcomes the technical support offered in fulfilling this recommendation» no es «support»
        # como respuesta (y acepta un tratado y no el otro); «accepts this recommendation only with regard to CRPD» es en parte
        a = ('125.1\n\nTajikistan accepts this recommendation.\n\n125.2\n\nAt present, Tajikistan considers it feasible to accede to '
             'CRPD and welcomes the\ntechnical support offered in fulfilling this recommendation.\nTajikistan is not ready at this stage '
             'to accede to ICPPED.\n\n125.3\n\nTajikistan accepts this recommendation only with regard to CRPD\nand ICCPR-OP2.\n\n'
             '125.4\n\nTajikistan does not accept this recommendation.\n\n125.5\n\nAnswered in 125.4.\n\n125.6\n\nTajikistan accepts this '
             'recommendation.\n')
        self.assertEqual(self.r(a)[1:3], [None, None])
        self.assertEqual(P.clase('welcomes the technical support offered in fulfilling this recommendation', estricto=True), None)
        self.assertEqual(P.clase('Sri Lanka is able to support this recommendation', estricto=True), A)
        # A/HRC/33/6/Add.1 (Samoa): «Recommendation 96.2 / … Samoa accepts this recommendation» y, más abajo, «Recommendations 96.1,
        # 96.2, 96.3 … / … Samoa notes this recommendation»: el número que abre su apartado solo vale si no sale en otro sitio
        a = ('Recommendation 125.2\n10.\nSamoa will ratify CRPD by December 2016. Therefore Samoa accepts this recommendation.\n\n'
             'Recommendations 125.1, 125.2, 125.3\n13.\nWith respect to the accession to ICESCR, the Government will continue its '
             'assessment. Thus far, Samoa notes this recommendation.\n')
        self.assertIsNone(self.r(a)[1])
        # A/HRC/41/6/Add.1 (Chile): «has decided not to consider recommendations 125.86, …» en una «Additional note» que va debajo
        # de «Recommendations not accepted»: no toma posición, y la fila no hereda el apartado
        self.assertTrue(P._SIN_POSICION.search('The Government of Chile has decided not to consider recommendations 125.86'))
        a = ('Recommendations not accepted by the Government\n125.5\n30.\nThe recommendation is not accepted.\n\nAdditional note\n41.\n'
             'The Government has decided not to consider recommendations 125.1,\n125.2 and 125.3, which were issued by the representatives '
             'of a regime whose\nlegitimacy it does not recognize.\n')
        ap = P._paginas(a)
        i = ap.find('125.1,')
        self.assertFalse(P._hereda_fila(ap, i, i + 5, N))
        self.assertEqual(self.r(a)[:3], [None, None, None])

DIR = os.environ.get('ATLAS_TEXTOS_DIR', '/var/lib/atlas/textos')


class Condicionadas(unittest.TestCase):
    """T75 r3: una aceptación con condiciones no es «apoyada» (A/HRC/30/10/Add.1, A/HRC/55/10/Add.1, A/HRC/25/7/Add.1)."""
    def test_aceptacion_condicionada_no_es_apoyada(self):
        for s in ('Rec.123.46 – accepted under the stipulation that “prohibiting” is an incorrect term;',
                  'Rec.123.76 – accepted with the reservation that the word “increase” represents a',
                  'The recommendation is supported on the understanding that training and service in',
                  'Mexico accepts the recommendation on the understanding that',
                  'accepted subject to the clarification that'):
            self.assertNotEqual(P.clase(s), 'apoyada', s)

    def test_aceptacion_sin_condiciones_sigue_apoyada(self):
        for s in ('Accepted', 'Rec.123.31 – accepted.', 'enjoy the support of Bulgaria'):
            self.assertEqual(P.clase(s), 'apoyada', s)


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

    def uno(self, s, *nums):
        with open(os.path.join(DIR, 'txt', s + '-en.txt'), encoding='utf-8', errors='ignore') as f: t = f.read()
        with open(os.path.join(DIR, 'txt', s + '_Add_1-en.txt'), encoding='utf-8', errors='ignore') as f: a = f.read()
        r = P.respuestas(t, a, E.numeros(t))
        return [r[n]['r'] for n in nums]

    def test_falsos_de_la_verificacion(self):
        # comprobados en el texto: «decided not to consider» (Chile), respuesta mixta en la fila (Rumanía), prosa mixta y «only with
        # regard to» (Tayikistán), el mismo número con dos respuestas en dos apartados (Samoa)
        self.assertEqual(self.uno('A_HRC_41_6', '125.86', '125.123', '125.190', '125.215'), [None] * 4)
        self.assertEqual(self.uno('A_HRC_23_5', '109.8', '109.7', '109.1'), [None, N, A])
        self.assertEqual(self.uno('A_HRC_33_11', '118.7', '118.8', '118.15'), [None, None, N])
        self.assertEqual(self.uno('A_HRC_33_6', '96.2', '96.20', '96.26'), [None, None, N])
        # y lo que sigue valiendo junto a ellos: «Malaysia is unable to support this recommendation» (146.126)
        self.assertEqual(self.uno('A_HRC_25_10', '146.126'), [N])


if __name__ == '__main__':
    unittest.main()
