#!/usr/bin/env python3
"""T95: la comprobación de scripts/traducir_local.py (sin modelo): etiquetas y marcadores, alfabeto, nombre y notas."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
import traducir_local as T
fallos = 0
def ok(n, c):
    global fallos
    print(('✓ ' if c else '✗ ') + n); fallos += not c
es = 'Los <b>relatores</b> son otra vía: {n} casos.'
ok('vale una traducción con las mismas marcas', T.valida(es, 'The <b>rapporteurs</b> are another way: {n} cases.', 'en') is None)
ok('falla si pierde una etiqueta', T.valida(es, 'The rapporteurs are another way: {n} cases.', 'en') is not None)
ok('falla si cambia el orden o pierde un marcador', T.valida(es, 'The <b>rapporteurs</b> are another way.', 'en') is not None)
ok('falla si el árabe sale en letras latinas', T.valida('Comisiones y misiones', 'MISIONES Y COMISIONES', 'ar') is not None)
ok('vale el árabe en su alfabeto', T.valida('Comisiones y misiones', 'لجان وبعثات', 'ar') is None)
ok('vale un símbolo que no se traduce (CEDAW) en chino', T.valida('CEDAW', 'CEDAW', 'zh') is None)
ok('falla si traduce el nombre ATLAS ONU', T.valida('Datos de ATLAS ONU', 'Данные ATLAS ООН', 'ru') is not None)
ok('falla si copia una nota entre corchetes', T.valida('Lista de comprobación', '[Screen: x] Checklist', 'en') is not None)
ok('falla si repite el español', T.valida('Lista de comprobación', 'Lista de comprobación', 'fr') is not None)
ok('una marca (Chrome) puede quedarse igual en inglés y en ruso', T.valida('Chrome', 'Chrome', 'en') is None and T.valida('Chrome', 'Chrome', 'ru') is None)
ok('falla si está vacía', T.valida('Lista', ' ', 'en') is not None)
sys.exit(1 if fallos else 0)
