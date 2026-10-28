#!/usr/bin/env python3
"""Mecanismos distintos de los procedimientos especiales: órganos de tratados, EPU, procedimiento de denuncia,
comisiones de investigación y otros. Las semillas (símbolo, nombre) son curadas; cada símbolo se verifica en la
Biblioteca Digital ONU con las mismas reglas que el catálogo (coincidencia exacta + título). Lo no verificado se marca.
Datos de tratados (adopción / entrada en vigor / miembros): diapositiva 8 del curso «Órganos de Tratados» (UAH, oct-2026)."""
import json, sys, importlib.util, concurrent.futures as cf
def load(n):
    sp = importlib.util.spec_from_file_location(n, f'scripts/{n}.py'); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
V, R = load('verify_symbols'), load('resolve_texts')
T = 'Órgano de tratado'
SEM = [
 # categoría, siglas, nombre ES, nameEN, símbolo (acto en la ONU), qué crea el símbolo, adopción, entrada en vigor, miembros, palabras clave de título
 (T,'CERD','Comité para la Eliminación de la Discriminación Racial','Committee on the Elimination of Racial Discrimination','A/RES/2106(XX)','Adopción de la Convención ICERD (AG)',1965,1969,18,'racial discrimination'),
 (T,'CCPR','Comité de Derechos Humanos','Human Rights Committee','A/RES/2200(XXI)','Adopción del PIDCP y del PIDESC (AG)',1966,1976,18,'covenants human rights'),
 (T,'CESCR','Comité de Derechos Económicos, Sociales y Culturales','Committee on Economic, Social and Cultural Rights','E/RES/1985/17','Creación del Comité por el ECOSOC (el PIDESC no lo crea)',1966,1976,18,'review composition organization administrative arrangements'),
 (T,'CEDAW','Comité para la Eliminación de la Discriminación contra la Mujer','Committee on the Elimination of Discrimination against Women','A/RES/34/180','Adopción de la Convención CEDAW (AG)',1979,1981,23,'discrimination against women'),
 (T,'CAT','Comité contra la Tortura','Committee against Torture','A/RES/39/46','Adopción de la Convención CAT (AG)',1984,1987,10,'torture'),
 (T,'SPT','Subcomité para la Prevención de la Tortura','Subcommittee on Prevention of Torture','A/RES/57/199','Adopción del Protocolo Facultativo OPCAT (AG)',2002,2006,25,'torture protocol'),
 (T,'CRC','Comité de los Derechos del Niño','Committee on the Rights of the Child','A/RES/44/25','Adopción de la Convención sobre los Derechos del Niño (AG)',1989,1990,18,'child'),
 (T,'CMW','Comité de Trabajadores Migratorios','Committee on Migrant Workers','A/RES/45/158','Adopción de la Convención ICRMW (AG)',1990,2003,14,'migrant workers'),
 (T,'CRPD','Comité sobre los Derechos de las Personas con Discapacidad','Committee on the Rights of Persons with Disabilities','A/RES/61/106','Adopción de la Convención CRPD (AG)',2006,2008,18,'disabilities'),
 (T,'CED','Comité contra la Desaparición Forzada','Committee on Enforced Disappearances','A/RES/61/177','Adopción de la Convención CED (AG)',2006,2010,10,'enforced disappearance'),
 ('Mecanismo conexo del Consejo de Derechos Humanos','EPU','Examen Periódico Universal','Universal Periodic Review','A/RES/60/251','Creación del Consejo de DDHH y mandato del EPU (AG)',None,None,None,'human rights council'),
 ('Mecanismo conexo del Consejo de Derechos Humanos','EPU / Denuncia','Construcción institucional: EPU, procedimientos especiales, Comité Asesor y procedimiento de denuncia','Institution-building of the Human Rights Council','A/HRC/RES/5/1','Paquete de construcción institucional (CDH)',None,None,None,'institution-building'),
 ('Mecanismo conexo del Consejo de Derechos Humanos','EMRIP','Mecanismo de Expertos sobre los Derechos de los Pueblos Indígenas','Expert Mechanism on the Rights of Indigenous Peoples','A/HRC/RES/6/36','Creación del Mecanismo (CDH)',None,None,5,'indigenous'),
 ('Mecanismo conexo del Consejo de Derechos Humanos','Foro Minorías','Foro sobre Cuestiones de las Minorías','Forum on Minority Issues','A/HRC/RES/6/15','Creación del Foro (CDH)',None,None,None,'minority'),
 ('Grupo de trabajo intergubernamental','GT EPU','Grupo de Trabajo sobre el Examen Periódico Universal','Working Group on the Universal Periodic Review','A/HRC/RES/5/1','Modalidades del EPU: lo forman los 47 miembros del Consejo (CDH, cap. I)',None,None,47,'institution-building'),
 ('Grupo de trabajo intergubernamental','GT Comunicaciones','Grupo de Trabajo sobre las Comunicaciones (procedimiento de denuncia)','Working Group on Communications','A/HRC/RES/5/1','Procedimiento de denuncia: examina las comunicaciones recibidas (CDH, cap. IV)',None,None,5,'institution-building'),
 ('Grupo de trabajo intergubernamental','GT Situaciones','Grupo de Trabajo sobre las Situaciones (procedimiento de denuncia)','Working Group on Situations','A/HRC/RES/5/1','Procedimiento de denuncia: señala al Consejo patrones de violaciones graves (CDH, cap. IV)',None,None,5,'institution-building'),
 ('Grupo de trabajo intergubernamental','GT Derecho al desarrollo','Grupo de Trabajo de composición abierta sobre el derecho al desarrollo','Open-ended Working Group on the Right to Development','E/CN.4/RES/1998/72','Creación del Grupo de Trabajo (Comisión de Derechos Humanos)',None,None,None,'right to development'),
 ('Grupo de trabajo intergubernamental','GTIG Empresas','Grupo de Trabajo intergubernamental de composición abierta sobre las empresas transnacionales y otras empresas con respecto a los derechos humanos','Open-ended Intergovernmental Working Group on Transnational Corporations and Other Business Enterprises','A/HRC/RES/26/9','Creación del Grupo para elaborar un instrumento vinculante (CDH)',None,None,None,'transnational corporations'),
 ('Grupo de trabajo intergubernamental','GTIG Campesinos','Grupo de Trabajo intergubernamental de composición abierta sobre los derechos de los campesinos y de otras personas que trabajan en las zonas rurales','Open-ended Intergovernmental Working Group on the rights of peasants and other people working in rural areas','A/HRC/RES/21/19','Creación del Grupo para negociar una declaración (CDH)',None,None,None,'peasants'),
 ('Grupo de trabajo intergubernamental','GTIG Empresas de seguridad','Grupo de Trabajo intergubernamental de composición abierta sobre las empresas militares y de seguridad privadas','Open-ended Intergovernmental Working Group on Private Military and Security Companies','A/HRC/RES/15/26','Creación del Grupo para estudiar un marco regulatorio (CDH)',None,None,None,'private military security'),
 ('Grupo de trabajo intergubernamental','GTCA Envejecimiento','Grupo de Trabajo de composición abierta sobre el envejecimiento (Asamblea General)','Open-ended Working Group on Ageing','A/RES/65/182','Creación del Grupo de Trabajo (AG)',None,None,None,'ageing'),
 ('Procedimiento confidencial (histórico)','1503','Procedimiento confidencial «1503»','Confidential procedure 1503','E/RES/1503(XLVIII)','Creación del procedimiento (ECOSOC, 1970)',None,None,None,'procedure dealing communications human rights'),
 ('Procedimiento público (histórico)','1235','Procedimiento público «1235»','Public procedure 1235','E/RES/1235(XLII)','Autorización a examinar violaciones graves (ECOSOC, 1967)',None,None,None,'violations human rights'),
 ('Oficina','ACNUDH','Alto Comisionado para los Derechos Humanos','High Commissioner for Human Rights','A/RES/48/141','Creación del cargo (AG)',None,None,None,'high commissioner'),
 ('Comisión de investigación / misión de determinación de hechos','COI Siria','Comisión Internacional Independiente de Investigación sobre Siria','Independent International Commission of Inquiry on Syria','A/HRC/RES/S-17/1','Creación (CDH, sesión especial)',None,None,None,'syrian'),
 ('Comisión de investigación / misión de determinación de hechos','COI Libia','Comisión Internacional de Investigación sobre Libia (2011)','International Commission of Inquiry on Libya','A/HRC/RES/S-15/1','Creación (CDH, sesión especial)',None,None,None,'libya'),
 ('Comisión de investigación / misión de determinación de hechos','COI RPDC','Comisión de Investigación sobre la República Popular Democrática de Corea','Commission of Inquiry on the DPRK','A/HRC/RES/22/13','Creación (CDH)',None,None,None,'korea'),
 ('Comisión de investigación / misión de determinación de hechos','COI Burundi','Comisión de Investigación sobre Burundi','Commission of Inquiry on Burundi','A/HRC/RES/33/24','Creación (CDH)',None,None,None,'burundi'),
 ('Comisión de investigación / misión de determinación de hechos','MDH Myanmar','Misión Internacional Independiente de Determinación de los Hechos sobre Myanmar','Independent International Fact-Finding Mission on Myanmar','A/HRC/RES/34/22','Creación (CDH)',None,None,None,'myanmar'),
 ('Comisión de investigación / misión de determinación de hechos','MDH Venezuela','Misión Internacional Independiente de Determinación de los Hechos sobre Venezuela','Independent International Fact-Finding Mission on Venezuela','A/HRC/RES/42/25','Creación (CDH)',None,None,None,'venezuela'),
 ('Comisión de investigación / misión de determinación de hechos','COI Israel/TPO','Comisión de Investigación sobre el Territorio Palestino Ocupado, incluida Jerusalén Oriental, e Israel','Commission of Inquiry on the Occupied Palestinian Territory and Israel','A/HRC/RES/S-30/1','Creación (CDH, sesión especial)',None,None,None,'palestinian'),
 ('Comisión de investigación / misión de determinación de hechos','COI Ucrania','Comisión de Investigación sobre Ucrania','Commission of Inquiry on Ukraine','A/HRC/RES/49/1','Creación (CDH, sesión especial)',None,None,None,'ukraine'),
]
def one(s, cache):
    cat, sig, es, en, sym, que, ad, ev, mi, kws = s
    out = dict(categoria=cat, siglas=sig, nombre=es, nameEN=en, simbolo_semilla=sym, acto=que, adopcion=ad, entrada_vigor=ev, miembros=mi)
    r = V.verify(sym, 'HRC' if sym.startswith('A/HRC') else '', cache, '')
    if r.get('registro') and r['estado'] in ('VERIFICADO', 'VERIFICADO_NORMALIZADO', 'REVISAR_TITULO') :
        h = r['registro']; ov = V.overlap(kws, h['titulo']) if kws else 1
        out.update(estado='VERIFICADO' if (ov >= 0.15 or sig in ('EPU', 'ACNUDH', '1503', '1235')) else 'REVISAR_TITULO', simbolo=h['simbolo'], titulo_oficial=h['titulo'],
                   adoptada=h['adoptada'] or h['fecha'], registro=h['url'], coincidencia_titulo=ov,
                   texto=R.resolve(h['simbolo'], {**h, 'padres': h.get('padres', []), 'ubicacion': h.get('ubicacion', [])}, {}))
    else:
        out.update(estado='NO_VERIFICADO', motivo=r['estado'])
    return out
if __name__ == '__main__':
    cache = {}
    with cf.ThreadPoolExecutor(4) as ex: res = list(ex.map(lambda s: one(s, cache), SEM))
    json.dump(res, open('data/fuentes/mecanismos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r['estado'] for r in res))
    for r in res: print(r['estado'][:6], r['siglas'], '|', r.get('simbolo', r['simbolo_semilla']), '|', (r.get('titulo_oficial') or r.get('motivo'))[:70], '|', r.get('coincidencia_titulo'))
