from artifact_tool import Workbook,SpreadsheetFile
from datetime import datetime
wb=Workbook.create(); dash=wb.worksheets.add('TABLERO'); idx=wb.worksheets.add('MANDATOS'); nom=wb.worksheets.add('NOMENCLATURA'); issues=wb.worksheets.add('CONTROL Y FUENTES')
NAVY='#102A43'; TEAL='#087E8B'; LIGHT='#EAF3F5'; WHITE='#FFFFFF'; GRAY='#64748B'; GOLD='#D09C38'; RED='#FEE2E2'; GREEN='#E2F4EA'
ES='https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=es'; EN='https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?Type=TM&lang=en'
COUNTRY='https://spinternet.ohchr.org/ViewAllCountryMandates.aspx?lang=es'
def row(t,es,en,year,creator,doc,new,upd,kind='Temático',status='Comprobar documento',comment=''):
 return [t,es,en,kind,year,creator,doc,new,upd,status,comment,ES,EN]
rows=[
row('Desapariciones forzadas','Grupo de Trabajo sobre las Desapariciones Forzadas o Involuntarias','Working Group on Enforced or Involuntary Disappearances',1980,'Comisión de Derechos Humanos','E/CN.4/RES/1980/20/(XXXVI)','A/HRC/RES/54/14','https://docs.un.org/A/HRC/WGEID/1',status='Símbolo histórico especial',comment='El documento A/HRC/WGEID/1 (2023) son métodos de trabajo, NO resolución creadora; la base registra renovación 2026 diferente según fecha de consulta.'),
row('Tortura','Relator Especial sobre la tortura','Special Rapporteur on torture',1985,'Comisión de Derechos Humanos','E/CN.4/RES/1985/33','','https://docs.un.org/E/CN.4/2003/68',status='Creación verificada',comment='Antiguo código E/CN.4: NO atribuir la resolución a ECOSOC sin comprobar el acto.'),
row('Ejecuciones extrajudiciales','Relator Especial sobre ejecuciones extrajudiciales, sumarias o arbitrarias','Special Rapporteur on extrajudicial, summary or arbitrary executions',1982,'ECOSOC / Comisión: revisar autoría','E/CN.4/1982/35','A/HRC/RES/53/4','',status='ALERTA: informe ≠ resolución',comment='El índice OHCHR muestra E/CN.4/1982/35 bajo etiqueta ECOSOC: verificar acto de creación; E/CN.4/1982/35 no lleva RES.'),
row('Mercenarios','Grupo de Trabajo sobre la utilización de mercenarios','Working Group on the use of mercenaries',2005,'Comisión de Derechos Humanos','E/CN.4/RES/2005/2','A/HRC/RES/60/5','https://www.ohchr.org/es/special-procedures/wg-mercenaries/methods-work-working-group-use-mercenaries',status='Creación identificada',comment='La página OHCHR puede mostrar código de resolución E/CN.4/2005/2 sin segmento RES; verificar texto oficial.'),
row('Detención arbitraria','Grupo de Trabajo sobre la Detención Arbitraria','Working Group on Arbitrary Detention',1991,'Comisión de Derechos Humanos','1991/42 (verificar símbolo formal)','','https://docs.un.org/A/HRC/36/38',status='Pendiente cotejo',comment='A/HRC/36/38 (2017) fija métodos de trabajo, NO crea mandato.'),
row('Derecho al agua','Relator Especial sobre los derechos humanos al agua potable y al saneamiento','Special Rapporteur on the human rights to safe drinking water and sanitation',2008,'Consejo de Derechos Humanos','A/HRC/RES/7/22','A/HRC/RES/51/19','',status='Comparar ampliación 2011',comment='Creado como experto independiente; título y alcance evolucionaron, evitar equiparar sin cronología.'),
row('Alimentación','Relator Especial sobre el derecho a la alimentación','Special Rapporteur on the right to food',2000,'Comisión de Derechos Humanos','E/CN.4/RES/2000/10','A/HRC/RES/58/10','',status='Símbolo mostrado variable',comment='La base muestra E/CN.4/2000/10 sin RES en la referencia de establecimiento.'),
row('Educación','Relator Especial sobre el derecho a la educación','Special Rapporteur on the right to education',1998,'Comisión de Derechos Humanos','E/CN.4/RES/1998/33','A/HRC/RES/53/7','',status='Comprobar documento',comment='En OHCHR el código original puede aparecer abreviado E/CN.4/1998/33.'),
row('Defensores','Relator Especial sobre la situación de los defensores de derechos humanos','Special Rapporteur on the situation of human rights defenders',2000,'Comisión de Derechos Humanos','E/CN.4/RES/2000/61','A/HRC/RES/61/22','',status='Comprobar documento',comment='Originalmente Representante Especial; registrar evolución de la denominación.'),
row('Minorías','Relator Especial sobre cuestiones de las minorías','Special Rapporteur on minority issues',2005,'Comisión de Derechos Humanos','E/CN.4/RES/2005/79','A/HRC/RES/52/5','',status='Comprobar documento',comment='Origen experto independiente; denominación revisada.'),
row('Derechos culturales','Relator Especial en la esfera de los derechos culturales','Special Rapporteur in the field of cultural rights',2009,'Consejo de Derechos Humanos','A/HRC/RES/10/23','A/HRC/RES/55/5','',status='Comprobar documento',comment='Base: resolución de constitución 10/23.'),
row('Medio ambiente','Relator Especial sobre el derecho a un medio ambiente limpio, saludable y sostenible','Special Rapporteur on the human right to a clean, healthy and sustainable environment',2012,'Consejo de Derechos Humanos','A/HRC/RES/19/10','A/HRC/RES/55/2','',status='Comprobar evolución',comment='Mandato creado en 2012 como experto independiente sobre medio ambiente y derechos humanos.'),
row('Cambio climático','Relator Especial sobre la promoción y protección de los derechos humanos en el contexto del cambio climático','Special Rapporteur on human rights in the context of climate change',2021,'Consejo de Derechos Humanos','A/HRC/RES/48/14','A/HRC/RES/57/31','',status='Comprobar documento',comment='Mandato de 2021.'),
row('Albinismo','Experto independiente sobre los derechos humanos de las personas con albinismo','Independent Expert on the enjoyment of human rights by persons with albinism',2015,'Consejo de Derechos Humanos','A/HRC/RES/28/6','A/HRC/RES/55/18','',status='Anomalías en extensiones',comment='La base OHCHR repite algunas renovaciones y variantes A/RES/HRC vs A/HRC/RES.'),
row('Afrodescendientes','Grupo de Trabajo de Expertos sobre los Afrodescendientes','Working Group of Experts on People of African Descent',2002,'Comisión de Derechos Humanos','E/CN.4/2002/WP.2','A/HRC/RES/54/26','',status='ALERTA: WP ≠ RES',comment='OHCHR expone E/CN.4/2002/WP.2 bajo rótulo resolución: NO certificar acto creador desde esa referencia.'),
row('Campesinos','Grupo de Trabajo sobre los derechos de los campesinos','Working Group on the rights of peasants and rural workers',2023,'Consejo de Derechos Humanos','A/HRC/RES/54/9','','',status='Comprobar documento',comment='Mandato temático relativamente reciente.'),
row('Discapacidad','Relator Especial sobre los derechos de las personas con discapacidad','Special Rapporteur on the rights of persons with disabilities',2014,'Consejo de Derechos Humanos','A/HRC/RES/26/20','A/HRC/RES/53/14','',status='Comprobar renovación',comment='El portal muestra renovaciones distintas según actualización de idioma.'),
row('Solidaridad internacional','Experto independiente sobre derechos humanos y solidaridad internacional','Independent Expert on human rights and international solidarity',2005,'Comisión de Derechos Humanos','E/CN.4/RES/2005/55','A/HRC/RES/53/5','',status='Comprobar documento',comment='La referencia de origen se muestra abreviada en el portal.'),
row('Afganistán','Relator Especial sobre situación de derechos humanos en Afganistán','Special Rapporteur on human rights in Afghanistan',2021,'Consejo de Derechos Humanos','A/HRC/RES/48/1','A/HRC/RES/60/2','',kind='País',status='Comprobar actualizaciones',comment='Mandato por país; fuente general de mandatos por país.'),
row('Belarús','Relator Especial sobre situación de derechos humanos en Belarús','Special Rapporteur on human rights in Belarus',2012,'Consejo de Derechos Humanos','A/HRC/RES/20/13','A/HRC/RES/61/26','',kind='País',status='Comprobar actualizaciones',comment='Mandato por país; fuente general de mandatos por país.'),
]
headers=['Clave temática','Denominación ES','Denominación EN','Alcance','Año inicial','Órgano atribuido','Código histórico observado','Resolución posterior (muestra)','Material de trabajo / metodología','Control de calidad','Nota de cautela','Índice ES','Índice EN']
idx.get_range('A1:M1').values=[headers];idx.get_range(f'A2:M{len(rows)+1}').values=rows
# tweak sources per rows country
for i in (19,20):idx.get_range(f'L{i}:M{i}').values=[[COUNTRY,'https://spinternet.ohchr.org/ViewAllCountryMandates.aspx']]
idx.tables.add(f'A1:M{len(rows)+1}',True,'CatalogoMandatos')
idx.freeze_panes.freeze_rows(1)
for col,width in {'A':24,'B':48,'C':49,'D':14,'E':13,'F':32,'G':31,'H':31,'I':49,'J':29,'K':64,'L':56,'M':56}.items():idx.get_range(f'{col}:{col}').format.column_width=width
idx.get_range('A1:M1').format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':32,'wrap_text':True}
idx.get_range(f'A2:M{len(rows)+1}').format.row_height=36
idx.get_range(f'A2:M{len(rows)+1}').format.wrap_text=True
idx.get_range(f'J2:J{len(rows)+1}').conditional_formats.add_custom('=LEFT(J2,6)="ALERTA"',{'fill':RED})
idx.get_range(f'E2:E{len(rows)+1}').format.number_format='0'

# Dashboard
for a,b in [('A1:H2','ÍNDICE JURÍDICO | PROCEDIMIENTOS ESPECIALES ONU'),('A4:H4','Búsqueda rápida, contraste bilingüe y control de nomenclatura histórica'),('A8:B8','MANDATOS CATALOGADOS'),('D8:E8','TEMÁTICOS'),('G8:H8','POR PAÍS'),('A13:H13','CÓMO UTILIZAR ESTE TABLERO'),('A20:H20','ACCESOS DIRECTOS A FUENTES PRIMARIAS'),('A28:H28','ALERTAS METODOLÓGICAS')]:
 dash.merge_cells(a);cell=a.split(':')[0];dash.get_range(cell).values=[[b]]
dash.get_range('A1:H2').format={'fill':NAVY,'font':{'color':WHITE,'bold':True,'size':19},'row_height':33}
dash.get_range('A4:H4').format={'fill':LIGHT,'font':{'color':TEAL,'bold':True,'size':12},'row_height':28}
for rng in ['A8:B8','D8:E8','G8:H8']:
 dash.get_range(rng).format={'fill':TEAL,'font':{'bold':True,'color':WHITE},'row_height':25}
dash.merge_cells('A9:B11');dash.merge_cells('D9:E11');dash.merge_cells('G9:H11')
dash.get_range('A9').formulas=[['=COUNTA(MANDATOS!A2:A200)']];dash.get_range('D9').formulas=[['=COUNTIF(MANDATOS!D2:D200,"Temático")']];dash.get_range('G9').formulas=[['=COUNTIF(MANDATOS!D2:D200,"País")']]
for rng in ['A9:B11','D9:E11','G9:H11']:dash.get_range(rng).format={'fill':LIGHT,'font':{'bold':True,'size':25,'color':NAVY},'vertical_alignment':'center','horizontal_alignment':'center'}
for row_,text_ in [(15,'1  MANDATOS: activa filtros de encabezado y localiza una temática, año, órgano o código.'),(16,'2  Verifica en fuente ES y EN; no des por válida una sigla solo porque figura en la página.'),(17,'3  NOMENCLATURA: interpreta RES, DEC, L., E/CN.4, A/HRC, E/RES y A/RES.'),(18,'4  CONTROL Y FUENTES: revisa anomalías antes de citar un documento en una exposición.')]:
 dash.merge_cells(f'A{row_}:H{row_}');dash.get_range(f'A{row_}').values=[[text_]]
dash.get_range('A15:H18').format.row_height=24
links=[('Portal temático ES',ES),('Thematic mandates EN',EN),('Mandatos por país ES',COUNTRY),('Documentos ONU', 'https://docs.un.org/'),('Biblioteca Digital ONU','https://digitallibrary.un.org/'),('Comunicaciones especiales','https://spsubmission.ohchr.org/es')]
for i,(label,url) in enumerate(links,start=22):
 dash.merge_cells(f'A{i}:D{i}');dash.get_range(f'A{i}').values=[[label]];dash.merge_cells(f'E{i}:H{i}');dash.get_range(f'E{i}').formulas=[[f'=HYPERLINK("{url}","Abrir fuente oficial")']]
for r,txt in [(30,'No toda referencia E/CN.4 es resolución del ECOSOC: identifica el órgano y el tipo documental.'),(31,'Los códigos originales, proyectos L. y documentos de informe pueden aparecer mezclados en el índice web.'),(32,'Actualización temporal: la base bilingüe presenta cambios y duplicados; revisar la fecha de consulta.'),(33,'Este es un catálogo de trabajo selectivo, NO inventario exhaustivo de todos los mandatos y renovaciones.')]:
 dash.merge_cells(f'A{r}:H{r}');dash.get_range(f'A{r}').values=[[txt]]
for rng in ['A13:H13','A20:H20','A28:H28']:dash.get_range(rng).format={'fill':NAVY,'font':{'color':WHITE,'bold':True},'row_height':25}
dash.get_range('A30:H33').format={'fill':'#FFF5DF','row_height':25,'wrap_text':True}
for c in 'ABCDEFGH':dash.get_range(f'{c}:{c}').format.column_width=18
# nomenclature
rules=[
('A/RES/60/251','Asamblea General','Resolución adoptada','Creación del Consejo de Derechos Humanos en 2006','No es resolución del Consejo de Derechos Humanos','https://docs.un.org/A/RES/60/251'),
('A/HRC/RES/5/1','Consejo de Derechos Humanos','Resolución adoptada','Paquete de construcción institucional (2007)','A/HRC/5/1 SIN RES no identifica el mismo tipo','https://docs.un.org/A/HRC/RES/5/1'),
('A/HRC/DEC/25/116','Consejo de Derechos Humanos','Decisión adoptada','Ejemplo de decisión, diferente de resolución','No convertir DEC en RES','https://docs.un.org/A/HRC/DEC/25/116'),
('A/HRC/51/L.40','Consejo de Derechos Humanos','Proyecto de texto','Ejemplo de proyecto presentado a negociación','L. no es necesariamente texto final adoptado','https://docs.un.org/A/HRC/51/L.40'),
('A/HRC/RES/51/19','Consejo de Derechos Humanos','Resolución adoptada','Ejemplo de texto final de mandato de agua y saneamiento','Comparar con L.40','https://docs.un.org/A/HRC/RES/51/19'),
('E/CN.4/RES/1985/33','Comisión de Derechos Humanos','Resolución histórica','Creación del mandato del Relator Especial sobre la tortura','La Comisión dependía de ECOSOC: NO equivale a autoría ECOSOC','https://ap.ohchr.org/documents/alldocs.aspx?doc_id=9918'),
('E/CN.4/2003/68','Comisión de Derechos Humanos','Informe/documento','Informe del Relator sobre tortura con métodos de trabajo','No es resolución por no llevar RES','https://docs.un.org/E/CN.4/2003/68'),
('A/HRC/WGEID/102/2','Grupo de Trabajo sobre Desapariciones','Métodos de trabajo','Versión de 2014','No es acto de creación ni sentencia','https://docs.un.org/A/HRC/WGEID/102/2'),
('A/HRC/WGEID/1','Grupo de Trabajo sobre Desapariciones','Métodos de trabajo','Revisión de 2023','No inferir cronología por el 1 del código','https://docs.un.org/A/HRC/WGEID/1'),
('A/HRC/36/38','Consejo de Derechos Humanos','Informe','Incluye métodos del Grupo sobre Detención Arbitraria','No es resolución pese a empezar A/HRC','https://docs.un.org/A/HRC/36/38'),
('E/RES/####','Consejo Económico y Social','Resolución de ECOSOC','Familia de resoluciones ECOSOC','Diferente de E/CN.4/RES de Comisión','https://digitallibrary.un.org/'),
('A/HRC/##/L.##','Consejo de Derechos Humanos','Proyecto de resolución','Texto presentado antes de su adopción','No atribuir efectos del texto final a un proyecto','https://docs.un.org/'),
]
nom.get_range('A1:F1').values=[['Patrón / ejemplo','Órgano','Naturaleza documental','Qué significa','Error frecuente','Enlace oficial']]
nom.get_range(f'A2:F{len(rules)+1}').values=[list(x) for x in rules]
nom.tables.add(f'A1:F{len(rules)+1}',True,'DiccionarioSimbolos');nom.freeze_panes.freeze_rows(1)
for c,w in {'A':32,'B':35,'C':29,'D':58,'E':64,'F':57}.items():nom.get_range(f'{c}:{c}').format.column_width=w
nom.get_range('A1:F1').format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':29}
nom.get_range(f'A2:F{len(rules)+1}').format={'wrap_text':True,'row_height':42}
# issues
alerts=[
('A-01','E/CN.4/1982/35','Ejecuciones extrajudiciales','La ficha temática califica la fuente como ECOSOC y cita símbolo de documento sin RES.','ALTA','Revisar el acto de creación en Biblioteca Digital ONU; no copiar autoría sin contraste',EN),
('A-02','E/CN.4/2002/WP.2','Expertos afrodescendientes','La ficha oficial muestra un documento de trabajo WP bajo etiqueta de resolución.','ALTA','Comprobar resoluciones efectivamente adoptadas antes de citar',ES),
('A-03','A/RES/HRC/46/12','Albinismo','La ficha contiene símbolo inusual y varias entradas duplicadas para 2021.','ALTA','Cotejar A/HRC/RES/46/12 en docs.un.org',ES),
('A-04','A/HRC/51/L.40','Agua y saneamiento','Aparece un proyecto L. al lado de la resolución adoptada.','MEDIA','Utilizar la versión RES cuando la intención sea citar decisión final',ES),
('A-05','E/CN.4/2000/10','Derecho a la alimentación','Referencia histórica abreviada sin RES; puede confundirse con informe.','MEDIA','Comparar ficha y copia primaria del acto',ES),
('A-06','Renovaciones 2026','Diversos mandatos','Las versiones idiomas o cachés pueden reflejar diferentes fechas de renovación.','MEDIA','Anotar fecha de consulta y cotejar versión adoptada',ES),
('A-07','A/HRC/WGEID/1','Desapariciones','Métodos de trabajo revisados, no nueva resolución de mandato.','BAJA','Separar creación, renovación y métodos en columnas distintas','https://docs.un.org/A/HRC/WGEID/1'),
('A-08','Soft law vs tratado','Vinculatoriedad','No es preciso decir que todas las resoluciones de órganos ONU son siempre no vinculantes.','ALTA','Calificar según órgano, competencia, Carta, tipo de decisión y objeto','https://www.un.org/es/about-us/un-charter'),
]
issues.get_range('A1:G1').values=[['ID','Símbolo o asunto','Mandato','Problema detectable','Nivel','Regla de control','Fuente']]
issues.get_range(f'A2:G{len(alerts)+1}').values=[list(x) for x in alerts]
issues.tables.add(f'A1:G{len(alerts)+1}',True,'AlertasArchivo');issues.freeze_panes.freeze_rows(1)
for c,w in {'A':12,'B':30,'C':31,'D':72,'E':15,'F':72,'G':60}.items():issues.get_range(f'{c}:{c}').format.column_width=w
issues.get_range('A1:G1').format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':29}
issues.get_range(f'A2:G{len(alerts)+1}').format={'wrap_text':True,'row_height':45}
issues.get_range(f'E2:E{len(alerts)+1}').conditional_formats.add_custom('=E2="ALTA"',{'fill':RED})
# detail dates
issues.get_range('A13').values=[['Consultado: 27-10-2026 | Fuente: OHCHR, portal de procedimientos especiales ES/EN + documentos ONU']]
issues.merge_cells('A13:G13');issues.get_range('A13:G13').format={'fill':LIGHT,'font':{'color':GRAY}}
# verification
out='/mnt/data/Tablero_ONU_Procedimientos_Especiales_Nomenclatura_ES_EN.xlsx'
SpreadsheetFile.export_xlsx(wb).save(out)
print('GUARDADO',out,'filas',len(rows))
try:
 print('INSPECT',wb.inspect({'kind':'table','range':'TABLERO!A8:H11','include':'values,formulas','table_max_rows':5,'table_max_cols':8}).ndjson[:1700])
except Exception as e: print('inspection error',str(e)[:300])
