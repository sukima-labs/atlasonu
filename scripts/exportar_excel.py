#!/usr/bin/env python3
"""Exporta data/catalogo.json a data/atlas-onu-catalogo-v07.xlsx (utilizable sin conexión)."""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
d = json.load(open('data/catalogo.json', encoding='utf-8'))
wb = Workbook()
def sheet(name, head, rows, widths=None, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = name; ws.append(head)
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='17394A'); c.alignment = Alignment(wrap_text=True, vertical='top')
    for r in rows: ws.append([('\'' + v if isinstance(v, str) and v[:1] in '=+@-' else v) for v in r])
    for i, w in enumerate(widths or [], 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'A2'; ws.auto_filter.ref = ws.dimensions
    return ws
leeme = [['ATLAS ONU — catálogo v0.7'], ['Autor y titular: Sukima-Labs · © 2026. Iniciativa académica independiente; no es un producto oficial de la ONU ni de la Universidad de Alcalá.'],
 [f"Datos del {d['consultado']}. Fuentes: índice oficial de mandatos de OHCHR (spinternet.ohchr.org) y Biblioteca Digital de la ONU (digitallibrary.un.org)."],
 ['«Localizado» significa que existe un registro con ese símbolo exacto en la Biblioteca Digital; no sustituye leer el texto. Una resolución no es el informe que la reproduce.'],
 ['Hojas: Mandatos · Actos (cadena de creación y prórrogas con estado de verificación) · Titulares · Textos (ruta al texto de cada resolución) · Mecanismos · Alertas.'],
 ['Cubre solo mandatos vigentes. Faltan mandatos extinguidos y mapas.']]
ws = wb.active; ws.title = 'LEEME'
for r in leeme: ws.append(r)
ws['A1'].font = Font(bold=True, size=14); ws.column_dimensions['A'].width = 150
sheet('Mandatos', ['Mandato (ES)', 'Mandate (EN)', 'Alcance', 'Año de creación', 'Órgano creador', 'Símbolo del acto de creación', 'Prórroga vigente (año)', 'Prórroga vigente (símbolo)', 'Actos localizados', 'Actos totales', 'Control de calidad', 'Nota'],
 [[m['nombre'], m['nameEN'], m['alcance'], m['anio'], m['organo'], m['creacion'], m['renovacion_anio'], m['renovacion'], m['actos_verificados'], m['actos_total'], m['revision'], m['nota']] for m in d['mandatos']], [60, 60, 11, 10, 28, 24, 10, 22, 10, 10, 45, 80])
sheet('Actos', ['Mandato', 'Año', 'Función', 'Órgano', 'Símbolo según OHCHR', 'Símbolo oficial', 'Título oficial', 'Adoptada', 'Estado', 'Aviso', 'Registro'],
 [[m['nameEN'], a['anio'], a['rol'], a['organo'], a['simbolo_fuente'], a.get('simbolo', ''), a.get('titulo_oficial', ''), a.get('adoptada', ''), a['estado'], a.get('aviso', ''), a.get('registro', '')] for m in d['mandatos'] for a in m['actos']], [45, 8, 18, 26, 26, 24, 55, 12, 24, 70, 40])
sheet('Titulares', ['Mandato', 'Tratamiento', 'Nombre', 'País', 'Fuente'],
 [[m['nameEN'], h['tratamiento'], h['nombre'], h['pais'], 'OHCHR ' + d['consultado']] for m in d['mandatos'] for h in m['titulares']] , [60, 12, 40, 28, 20])
tx = []
for k, e in d['indice_actos'].items():
    if k.startswith('~') or 'texto' not in e: continue
    t = e['texto']; pdf = {f['lengua']: f['url'] for f in t['fuentes']}
    inf = t['informe_sesion'][0] if t['informe_sesion'] else {}
    tx.append([k, e['titulo'], e['adoptada'], t['estado'], pdf.get('es', ''), pdf.get('en', ''), inf.get('simbolo', ''), inf.get('paginas', ''), e['registro']])
sheet('Textos', ['Símbolo', 'Título', 'Adoptada', 'Estado del texto', 'PDF español', 'PDF inglés', 'Informe de sesión que lo contiene', 'Páginas (impresas)', 'Registro'], tx, [26, 60, 12, 20, 60, 60, 22, 12, 40])
sheet('Mecanismos', ['Categoría', 'Siglas', 'Nombre', 'Name', 'Símbolo', 'Qué es el acto', 'Adopción', 'Entrada en vigor', 'Miembros', 'Estado', 'Registro'],
 [[m['categoria'], m['siglas'], m['nombre'], m['nameEN'], m.get('simbolo', m['simbolo_semilla']), m['acto'], m['adopcion'], m['entrada_vigor'], m['miembros'], m['estado'], m.get('registro', '')] for m in d['mecanismos']], [34, 14, 60, 60, 22, 50, 10, 12, 10, 14, 40])
sheet('Alertas', ['ID', 'Nivel', 'Referencia', 'Tema', 'Problema', 'Acción'], [[a['id'], a.get('nivel', ''), a.get('simbolo', ''), a.get('tema', ''), a.get('problema', ''), a.get('accion', '')] for a in d['alertas']], [8, 8, 28, 60, 100, 60])
wb.save('data/atlas-onu-catalogo-v07.xlsx'); print('xlsx ok', [ws.title + ':' + str(ws.max_row - 1) for ws in wb.worksheets[1:]])
