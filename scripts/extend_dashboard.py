from artifact_tool import Blob,SpreadsheetFile
from datetime import datetime
import os
src='/mnt/data/Tablero_ONU_Procedimientos_Especiales_Nomenclatura_ES_EN.xlsx'
wb=SpreadsheetFile.import_xlsx(Blob.load(src))
NAVY='#102A43'; TEAL='#087E8B'; WHITE='#FFFFFF'; LIGHT='#EAF3F5'; WARN='#FFF3D6'
# existing master inventory
idx=wb.worksheets.get_item('MANDATOS')
# Expand existing 20 to 28 with explicitly marked verification needed; separate from verified facts
extra=[
['Libertad de expresión','Relator Especial sobre la promoción y protección del derecho a la libertad de opinión y de expresión','Special Rapporteur on freedom of opinion and expression','Temático',1993,'Comisión de Derechos Humanos','E/CN.4/1993/45','','','Símbolo requiere contraste','En el listado OHCHR aparece la referencia E/CN.4/1993/45 sin RES; no tratarla automáticamente como resolución adoptada.','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'],
['Violencia contra mujeres','Relatora Especial sobre la violencia contra las mujeres y las niñas, sus causas y consecuencias','Special Rapporteur on violence against women and girls','Temático',1994,'Comisión de Derechos Humanos','E/CN.4/1994/45','A/HRC/RES/59/20','','Símbolo requiere contraste','Referencia histórica exhibida sin segmento RES; 2025 renovación requiere cotejo primario.','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'],
['Justicia transicional','Relator Especial sobre verdad, justicia, reparación y garantías de no repetición','Special Rapporteur on truth, justice, reparation and guarantees of non-recurrence','Temático',2011,'Consejo de Derechos Humanos','A/HRC/RES/18/7','A/HRC/RES/54/8','','Creación identificada','Cotejar última renovación, variable según fecha de consulta.','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'],
['Orden internacional','Experto independiente sobre un orden internacional democrático y equitativo','Independent Expert on a democratic and equitable international order','Temático',2011,'Consejo de Derechos Humanos','A/HRC/RES/18/6','A/HRC/RES/57/7','','Creación identificada','Mantener diferenciado de relatores especiales.','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'],
['Deuda externa','Experta independiente sobre las consecuencias de la deuda externa para el goce de los derechos humanos','Independent Expert on foreign debt and human rights','Temático',2000,'Comisión de Derechos Humanos','E/CN.4/2000/82','A/HRC/RES/52/17','','ALERTA: referencia indexada','OHCHR muestra símbolos discordantes como A/HRC/RES/2000/82. Requiere excavación documental.','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'],
['Salud','Relator Especial sobre el derecho de toda persona al disfrute del más alto nivel posible de salud','Special Rapporteur on the right to health','Temático',2002,'Comisión de Derechos Humanos','E/CN.4/2002/31','','','Símbolo requiere contraste','No certificar como acto fundador sin obtener copia primaria de resolución.','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'],
['Libertad religiosa','Relator Especial sobre la libertad de religión o de creencias','Special Rapporteur on freedom of religion or belief','Temático',1986,'Comisión de Derechos Humanos','1986/20','','','Símbolo histórico abreviado','Revisar órgano, serie oficial y contexto de 1986 antes de atribuir código completo.','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'],
['Orientación e identidad','Experto independiente sobre orientación sexual e identidad de género','Independent Expert on sexual orientation and gender identity','Temático',2016,'Consejo de Derechos Humanos','A/HRC/RES/32/2','','','Creación identificada','Aclarar que examina protección contra violencia y discriminación; cotejar renovación vigente.','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'],
]
idx.get_range('A22:M29').values=extra
# overwrite historic opening no misleading invented symbol
idx.get_range('G2').values=[['Comisión de Derechos Humanos, resolución 20 (XXXVI), 1980']]
idx.get_range('J2').values=[['Verificar copia primaria de la resolución']]
# New tabs
home=wb.worksheets.add('INICIO Y AVISO')
rows=[
('PLATAFORMA DE ARQUEOLOGÍA DOCUMENTAL | ONU',''),
('VERSIÓN','0.2 · Prototipo evaluable · 27/10/2026'),
('ESTADO DE ENTREGA','Uso académico piloto. NO distribuir como catálogo oficial exhaustivo.'),
('ACTUALIZACIÓN POR INTERNET','Este archivo NO extrae automáticamente datos web al abrir. Los enlaces oficiales permiten consultar versiones actuales.'),
('PERMISOS DE MICROSOFT 365','Para conectar y refrescar consultas externas hay que autorizar conexiones en Excel de escritorio y configurar Power Query. No hay actualización silenciosa universal en Excel web.'),
('SEGURIDAD','No habilites macros ni contenido externo de procedencia desconocida. La hoja no necesita macros para consultar datos.'),
('RUTA SIMPLE','Escribe una palabra en BUSCAR!B4; ve a RESULTADOS y filtra la columna COINCIDE por 1.'),
('RUTA EXPERTA','Usa BUSCAR!B5:B8 para órgano, tipo, período y símbolo. Los filtros se aplican en RESULTADOS.'),
('ARQUEOLOGÍA','Abre TRAZABILIDAD. Diferencia ACTO creador, INFORME que lo menciona, método de trabajo y documento de renovación.'),
('VERIFICACIÓN','Fuente oficial no implica que el índice esté correctamente etiquetado. Revisar texto primario antes de citar.'),
('PROTECCIÓN','La protección de hoja no sustituye los permisos de OneDrive/SharePoint. Se recomienda compartir como solo lectura.'),
('QUÉ FALTA','Automatizar ingesta web, cobertura exhaustiva, controles de persistencia, protección de autor y geodatos verificables.'),
]
home.get_range('A1:B12').values=[[a,b] for a,b in rows]
home.get_range('A1:B1').format={'fill':NAVY,'font':{'color':WHITE,'bold':True,'size':16},'row_height':40}
home.get_range('A2:A12').format={'fill':TEAL,'font':{'color':WHITE,'bold':True},'wrap_text':True}
home.get_range('B2:B12').format={'wrap_text':True,'row_height':42}
home.get_range('A:A').format.column_width=37;home.get_range('B:B').format.column_width=115
home.freeze_panes.freeze_rows(1)
# Search parameters and instructions
search=wb.worksheets.add('BUSCAR')
search.get_range('A1:H2').values=[['BUSCADOR GUIADO · ONU','','','','','','',''],['Comienza con una palabra (ej. tortura, mercenarios, ambiente) o filtra por símbolos.','','','','','','','']]
search.merge_cells('A1:H1');search.merge_cells('A2:H2')
search.get_range('A1:H1').format={'fill':NAVY,'font':{'color':WHITE,'bold':True,'size':17}}
search.get_range('A2:H2').format={'fill':'#EAF3F5','font':{'color':NAVY}}
search.get_range('A4:A8').values=[['Palabra libre'],['Órgano contiene'],['Alcance (Temático / País)'],['Año desde'],['Símbolo contiene']]
search.get_range('B4:B8').values=[['desapariciones'],[''],[''],[''],['']]
search.get_range('A4:A8').format={'fill':TEAL,'font':{'color':WHITE,'bold':True}}
search.get_range('B4:B8').format={'fill':'#E4F8EA','font':{'color':NAVY},'row_height':28}
search.get_range('B6').data_validation={'rule':{'type':'list','values':['','Temático','País']}}
search.merge_cells('A11:H11');search.get_range('A11').values=[['Los RESULTADOS se muestran en otra hoja. Filtra COINCIDE = 1 para ver solo correspondencias.']]
search.get_range('A11:H11').format={'fill':WARN,'font':{'bold':True,'color':NAVY}}
search.merge_cells('A13:H13');search.get_range('A13').values=[['Si no conoces la sigla, busca por palabras cotidianas; después inspecciona símbolo, fuente y ALERTA DE CALIDAD.']]
for c in 'ABCDEFGH':search.get_range(f'{c}:{c}').format.column_width=20
search.get_range('A:A').format.column_width=27;search.get_range('B:B').format.column_width=35
# Flagged results, 28 mandates
result=wb.worksheets.add('RESULTADOS')
result.get_range('A1:H1').values=[['COINCIDE','Tema','Mandato','Tipo','Año','Órgano','Símbolo observado','Estado de control']]
result.get_range('A1:H1').format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':30}
for c,w in {'A':15,'B':26,'C':68,'D':19,'E':13,'F':34,'G':38,'H':30}.items():result.get_range(f'{c}:{c}').format.column_width=w
# Explicit references ensure portable Excel formulas; full-text combined search for words in title, English title, theme, and notes
for row in range(2,30):
 result.get_range(f'B{row}:H{row}').formulas=[[f"=MANDATOS!A{row}",f"=MANDATOS!B{row}",f"=MANDATOS!D{row}",f"=MANDATOS!E{row}",f"=MANDATOS!F{row}",f"=MANDATOS!G{row}",f"=MANDATOS!J{row}"]]
 formula=(f'=IF(AND(OR(BUSCAR!$B$4="",ISNUMBER(SEARCH(BUSCAR!$B$4,MANDATOS!A{row}&" "&MANDATOS!B{row}&" "&MANDATOS!C{row}&" "&MANDATOS!K{row}))),'
          f'OR(BUSCAR!$B$5="",ISNUMBER(SEARCH(BUSCAR!$B$5,MANDATOS!F{row}))),'
          f'OR(BUSCAR!$B$6="",MANDATOS!D{row}=BUSCAR!$B$6),'
          f'OR(BUSCAR!$B$7="",MANDATOS!E{row}>=BUSCAR!$B$7),'
          f'OR(BUSCAR!$B$8="",ISNUMBER(SEARCH(BUSCAR!$B$8,MANDATOS!G{row}&" "&MANDATOS!H{row})))),1,0)')
 result.get_range(f'A{row}').formulas=[[formula]]
result.get_range('A2:H29').format.row_height=28
result.get_range('B2:H29').format.wrap_text=True
result.tables.add('A1:H29',True,'BuscadorResultado')
result.freeze_panes.freeze_rows(1)
result.get_range('A2:A29').conditional_formats.add_cell_is({'operator':'equal','formula':1,'format':{'fill':'#CDEDDD'}})
# source chain registry
trace=wb.worksheets.add('TRAZABILIDAD')
trace_rows=[
['T-001','Desapariciones forzadas','1980','CREACIÓN','Comisión de Derechos Humanos','Resolución 20 (XXXVI)','Referencia histórica, localizar texto adoptado; la fuente puede estar incorporada en informe de sesión','https://digitallibrary.un.org/','Cotejo primario pendiente'],
['T-002','Desapariciones forzadas','2014','MÉTODOS','WGEID','A/HRC/WGEID/102/2','Métodos de trabajo, NO resolución de creación','https://docs.un.org/A/HRC/WGEID/102/2','Documento identificado'],
['T-003','Desapariciones forzadas','2023','MÉTODOS REVISADOS','WGEID','A/HRC/WGEID/1','Sustituye métodos previos; NO constituye un mandato nuevo','https://docs.un.org/A/HRC/WGEID/1','Documento identificado'],
['T-004','Tortura','1985','CREACIÓN','Comisión de Derechos Humanos','1985/33','Acto creador, la ficha indexa dentro de serie histórica de Comisión','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en','Confirmación en texto primario pendiente'],
['T-005','Tortura','2002','INFORME','Relator Especial','E/CN.4/2003/68','Incluye métodos de trabajo; no es acto creador','https://docs.un.org/E/CN.4/2003/68','Documento identificado'],
['T-006','Detención arbitraria','1991','CREACIÓN','Comisión de Derechos Humanos','1991/42','Referencia original exhibida en índice OHCHR; precisar edición de texto primario','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en','Cotejo primario pendiente'],
['T-007','Detención arbitraria','2017','MÉTODOS','Grupo de Trabajo','A/HRC/36/38','Métodos de trabajo y reglas del mandato, NO resolución de creación','https://docs.un.org/A/HRC/36/38','Documento identificado'],
['T-008','Mercenarios','2005','CREACIÓN','Comisión de Derechos Humanos','2005/2','Establecimiento Grupo de Trabajo; localización primaria pendiente','https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en','Cotejo primario pendiente'],
['T-009','Mercenarios','vigente','MÉTODOS','Grupo de Trabajo','Página oficial OHCHR','Descripción operativa y métodos; NO acto normativo originario','https://www.ohchr.org/es/special-procedures/wg-mercenaries/methods-work-working-group-use-mercenaries','Página oficial identificada'],
['T-010','Consejo de Derechos Humanos','2006','CREACIÓN INSTITUCIONAL','Asamblea General','A/RES/60/251','Asamblea General establece Consejo como órgano subsidiario, no ECOSOC','https://docs.un.org/A/RES/60/251','Documento identificado'],
['T-011','Selección de titulares','2007','REGLAS INSTITUCIONALES','Consejo de Derechos Humanos','A/HRC/RES/5/1','Establece criterios de selección y marco del Grupo Consultivo','https://docs.un.org/A/HRC/RES/5/1','Documento identificado'],
]
trace.get_range('A1:I1').values=[['ID','Asunto','Año','Clase documental','Órgano emisor','Símbolo','Interpretación y ruta de arqueología','Fuente oficial','Resultado de auditoría']]
trace.get_range(f'A2:I{len(trace_rows)+1}').values=trace_rows
trace.tables.add(f'A1:I{len(trace_rows)+1}',True,'CadenaDocumental');trace.freeze_panes.freeze_rows(1)
trace.get_range('A1:I1').format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':30}
for c,w in {'A':10,'B':25,'C':13,'D':25,'E':30,'F':37,'G':85,'H':65,'I':29}.items():trace.get_range(f'{c}:{c}').format.column_width=w
trace.get_range(f'A2:I{len(trace_rows)+1}').format={'wrap_text':True,'row_height':43}
# appointment workflow, accurate basics
sel=wb.worksheets.add('SELECCIÓN')
selrows=[
['1','Vacante / Convocatoria','OHCHR abre candidaturas','Identificar mandato, elegibilidad, incompatibilidades','https://www.ohchr.org/en/hr-bodies/hrc/sp/nominations'],
['2','Presentación de candidaturas','Personas candidatas / nominadoras','Información y trayectoria profesional verificable','https://www.ohchr.org/en/hr-bodies/hrc/sp/nominations'],
['3','Grupo Consultivo','Cinco integrantes, uno por grupo regional; actúan a título personal','Examinar criterios: pericia, experiencia, independencia, imparcialidad, integridad, objetividad','https://docs.un.org/A/HRC/RES/5/1'],
['4','Entrevistas y lista de prioridad','Grupo Consultivo','Evaluar candidaturas y remitir recomendaciones motivadas','https://docs.un.org/A/HRC/RES/5/1'],
['5','Consultas y propuesta','Presidencia del Consejo','Propuesta con consultas institucionales y motivación cuando corresponda','https://docs.un.org/A/HRC/RES/5/1'],
['6','Nombramiento','Consejo de Derechos Humanos','Designación formal, no la decide el Grupo Consultivo','https://docs.un.org/A/HRC/RES/5/1'],
['7','Ejercicio del mandato','Titular individual o Grupo de Trabajo','Independencia funcional, comunicaciones, visitas, informes, según mandato','https://unsdg.un.org/2030-agenda/strengthening-international-human-rights/un-special-procedures'],
]
sel.get_range('A1:E1').values=[['Etapa','Trámite','Responsable','Punto de control','Base / consulta']]
sel.get_range('A2:E8').values=selrows
sel.tables.add('A1:E8',True,'SeleccionTitulares')
sel.get_range('A1:E1').format={'fill':NAVY,'font':{'bold':True,'color':WHITE}}
for c,w in {'A':12,'B':30,'C':46,'D':89,'E':77}.items():sel.get_range(f'{c}:{c}').format.column_width=w
sel.get_range('A2:E8').format={'wrap_text':True,'row_height':41}
sel.freeze_panes.freeze_rows(1)
# Stats documented no fabricated geostatistics
stats=wb.worksheets.add('INDICADORES')
stats.get_range('A1:D1').values=[['Indicador','Valor','Corte / alcance','Fuente y cautela']]
stats.get_range('A2:D7').values=[
['Mandatos temáticos ONU (corte histórico)',46,'Abril de 2026','https://europe.ohchr.org/human-rights/human-rights-mechanism'],
['Mandatos por país ONU (corte histórico)',13,'Abril de 2026','https://europe.ohchr.org/human-rights/human-rights-mechanism'],
['Registros del prototipo',28,'Catálogo selectivo, NO totalidad','Este archivo, hoja MANDATOS'],
['Temáticos de muestra',None,'Cálculo sobre el catálogo, NO dato global','MANDATOS columna D'],
['Por país de muestra',None,'Cálculo sobre el catálogo, NO dato global','MANDATOS columna D'],
['Mapas geográficos',None,'No se incluyen hasta disponer de datos país/año, procedencia y método homogéneos','https://spinternet.ohchr.org/ViewCountryVisits.aspx?Lang=en&visitType=all'],
]
stats.get_range('B5').formulas=[['=COUNTIF(MANDATOS!D2:D29,"Temático")']]
stats.get_range('B6').formulas=[['=COUNTIF(MANDATOS!D2:D29,"País")']]
stats.get_range('A1:D1').format={'fill':NAVY,'font':{'bold':True,'color':WHITE}}
for c,w in {'A':44,'B':16,'C':49,'D':100}.items():stats.get_range(f'{c}:{c}').format.column_width=w
stats.get_range('A2:D7').format={'wrap_text':True,'row_height':32}
try:
 chart=stats.charts.add('bar',stats.get_range('A2:B3'))
 chart.title_text='Mandatos ONU · corte abril 2026'
 chart.set_position('F2','L17')
except Exception as e: print('chart_warning',str(e)[:100])
# Navigation top of original dashboard note as legacy
orig=wb.worksheets.get_item('TABLERO')
orig.merge_cells('A35:H35')
orig.get_range('A35').values=[['IMPORTANTE: inicia en INICIO Y AVISO. La hoja TABLERO corresponde al resumen de la versión 0.1.']]
orig.get_range('A35:H35').format={'fill':WARN,'font':{'bold':True,'color':NAVY}}
# Tests documented
qa=wb.worksheets.add('PRUEBAS Y LÍMITES')
checks=[
['Q01','Desapariciones','Usar BUSCAR B4 = desapariciones; ver RESULTADOS','Flag = 1 en la fila de WGEID','Pendiente prueba de interfaz Excel'],
['Q02','Consulta ambigua','Usar BUSCAR B4 = agua; ver RESULTADOS','Relator derecho al agua entre resultados','Pendiente prueba de interfaz Excel'],
['Q03','Símbolo técnico','Usar BUSCAR B8 = E/CN.4','Filtrar COINCIDE = 1; filas con coincidencia en G/H','Pendiente prueba de interfaz Excel'],
['Q04','Resolución vs informe','TRAZABILIDAD T-001..T-003','No confundir 1980 y A/HRC/WGEID/1','Control estructural'],
['Q05','Nombre órgano','NOMENCLATURA E/CN.4 y E/RES','Comisión ≠ resolución ECOSOC','Control estructural'],
['Q06','Conexión externa','Abrir estando conectado','Solo hipervínculos; SIN sincronización automática al abrir','Limitación expresamente declarada'],
['Q07','Protección de autor','Abrir como lector en OneDrive','Permisos deben configurarse en OneDrive; no garantía por contraseña local','Limitación expresamente declarada'],
['Q08','Mapas geográficos','Inspeccionar INDICADORES','No hay estadísticas de países inventadas','Control estructural'],
]
qa.get_range('A1:E1').values=[['ID','Caso','Acción','Resultado esperado','Estado']]
qa.get_range('A2:E9').values=checks
qa.get_range('A1:E1').format={'fill':NAVY,'font':{'bold':True,'color':WHITE}}
for c,w in {'A':12,'B':30,'C':65,'D':75,'E':44}.items():qa.get_range(f'{c}:{c}').format.column_width=w
qa.get_range('A2:E9').format={'wrap_text':True,'row_height':40}
qa.freeze_panes.freeze_rows(1)
# Export
out='/mnt/data/Plataforma_ONU_Arqueologia_Documental_PILOTO_2026-10-27.xlsx'
SpreadsheetFile.export_xlsx(wb).save(out)
print('EXPORTED',out,os.path.getsize(out))
print('SHEETS',wb.inspect({'kind':'sheet','include':'id,name'}).ndjson[:1800])
print('SEARCH',wb.inspect({'kind':'table','range':'BUSCAR!A4:B8','include':'values,formulas','table_max_rows':7,'table_max_cols':2}).ndjson[:1200])
