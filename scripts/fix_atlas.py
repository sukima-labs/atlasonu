from pathlib import Path
import re, json, zipfile, shutil
root=Path('/mnt/data/ATLAS_ONU_publicacion'); p=root/'index.html'; s=p.read_text()
repo='https://github.com/sukima-labs/onu-arqueologia-documental'
s=s.replace('Catálogo demostrativo; no oficial ONU.</div></aside>',f'Catálogo académico no oficial.<br><a href="{repo}" target="_blank" rel="noopener noreferrer">GitHub · autoría y código ↗</a></div></aside>')
s=s.replace('Versión experimental · 27.10.2026','Versión 0.4 auditada · 27.10.2026')
s=s.replace('Búsqueda inteligente local','Consulta del catálogo académico local')
s=s.replace('<p class="intro">Busca por denominación en español o inglés, tema, órgano o símbolo. Aplica filtros adicionales y abre una ficha detallada de cada mecanismo.</p>', '<p class="intro">Busca términos comunes, sinónimos, nombres en inglés o símbolos ONU. Usa los filtros para acotar el resultado; las fichas distinguen actos creador, renovaciones, métodos y advertencias de cotejo.</p>')
s=s.replace('<option>ECOSOC</option></select></div></div><div class="toolbar">','<option>ECOSOC</option></select></div></div><div class="controls advanced"><div><label class="searchlabel" for="yearfrom">Desde el año</label><input id="yearfrom" type="number" class="field" min="1945" max="2100" placeholder="Ej. 1980"></div><div><label class="searchlabel" for="yearto">Hasta el año</label><input id="yearto" type="number" class="field" min="1945" max="2100" placeholder="Ej. 2006"></div><div><label class="searchlabel" for="order">Orden de resultados</label><select id="order" class="field"><option value="name">Tema A–Z</option><option value="oldest">Más antiguo primero</option><option value="newest">Más reciente primero</option></select></div><div><label class="searchlabel">Alcance del catálogo</label><div class="notice" style="margin:0;padding:10px">Muestra, no cobertura exhaustiva</div></div></div><div class="toolbar">')
s=s.replace('La actualización por internet <b>no está implementada</b>.','La actualización automática por internet <b>no está implementada</b>.')
s=s.replace('<b>No se ha publicado en GitHub.</b>',f'<b>Repositorio creado:</b> <a href="{repo}" target="_blank" rel="noopener noreferrer">ver proyecto en GitHub ↗</a>. La presencia de este enlace no certifica que esta revisión del tablero ya esté subida al repositorio.')
s=s.replace('Versión local 0.3','Versión local 0.4')
s=s.replace('</style>', '.sidefooter a{display:inline-block;margin-top:8px;color:#79e4e0;font-weight:700}.notice a{color:#b2fcff}.field[type=number]{appearance:textfield}@media(max-width:650px){.pill{display:none}} </style>')
# Repair categorizations (exclusive)
start=s.index('function compute(){const cats=')
end=s.index(";$('kpis')",start)
s=s[:start]+'''function compute(){const classify=r=>{const n=norm(r.nombre);if(n.includes('grupo de trabajo'))return 'Grupo';if(n.includes('experto independiente'))return 'Experto';if(n.includes('relator'))return 'Relator';return 'Otros'};const cats={Relator:D.filter(x=>classify(x)==='Relator').length,Experto:D.filter(x=>classify(x)==='Experto').length,Grupo:D.filter(x=>classify(x)==='Grupo').length,Otros:D.filter(x=>classify(x)==='Otros').length}'''+s[end:]
# Widen search with aliases and trace data, then year range and sorting
start=s.index('function filterMandates(){')
end=s.index('function renderMandates(){',start)
s=s[:start]+'''const ALIASES={'desapariciones':['desaparicion','desapariciones','enforced disappearance','wgeid'],'desaparicion':['desaparicion','desapariciones','enforced disappearance','wgeid'],'tortura':['tortura','torture'],'mercenarios':['mercenarios','mercenary','mercenaries'],'detencion':['detencion','detention','arbitraria'],'agua':['agua','water','saneamiento'],'medio ambiente':['medio ambiente','environment'],'relatores':['relator','special rapporteur'],'relator':['relator','special rapporteur']};
function searchTerms(q){let normalized=norm(q);return ALIASES[normalized]||[normalized]}
function searchText(r){let related=T.filter(t=>norm(t.tema).includes(norm(r.tema))||norm(r.tema).includes(norm(t.tema)));return norm([r.tema,r.nombre,r.nameEN,r.creacion,r.renovacion,r.organo,r.nota,r.metodos,...related.flatMap(t=>[t.simbolo,t.clase,t.nota])].join(' '))}
function filterMandates(){const q=norm($('q').value.trim()),modal=$('modal').value,fig=$('figura').value,org=$('origin').value;const from=Number($('yearfrom').value)||0,to=Number($('yearto').value)||9999;const terms=searchTerms(q);filtered=D.filter(r=>(!q||terms.some(t=>searchText(r).includes(t)))&&(!modal||r.alcance===modal)&&(!fig||norm(r.nombre).includes(norm(fig)))&&(!org||norm(r.organo).includes(norm(org)))&&r.anio>=from&&r.anio<=to);const order=$('order').value;filtered.sort((a,b)=>order==='oldest'?a.anio-b.anio:order==='newest'?b.anio-a.anio:a.tema.localeCompare(b.tema,'es'));renderMandates()}
''' +s[end:]
s=s.replace("['q','modal','figura','origin'].forEach(x=>$(x).value='');filterMandates()","['q','modal','figura','origin','yearfrom','yearto'].forEach(x=>$(x).value='');$('order').value='name';filterMandates()")
s=s.replace("$('q').addEventListener('input',filterMandates);", "$('q').addEventListener('input',filterMandates);['yearfrom','yearto','modal','figura','origin','order'].forEach(id=>$(id).addEventListener('change',filterMandates));")
# fix csv formula injection with prefixed apostrophe for unsafe string fields
s=s.replace("String(v??'').replace(/\"/g,'\"\"')", "(String(v??'').match(/^[=+@\\-\\t\\r]/)?'\\''+String(v??''):String(v??'')).replace(/\"/g,'\"\"')")
# Make official source provenance explicit and present project link
s=s.replace('Proyecto no afiliado ni avalado por Naciones Unidas o la Universidad de Alcalá.','Proyecto no afiliado ni avalado por Naciones Unidas o la Universidad de Alcalá. <a href="'+repo+'" target="_blank" rel="noopener noreferrer">Repositorio del autor ↗</a>.')
p.write_text(s,encoding='utf-8')
# Rework README that reports exact features
(root/'README.md').write_text('''# ATLAS ONU — Arqueología documental de procedimientos especiales

**Autor y dirección del proyecto:** Sukima-Labs (2026). Repositorio: https://github.com/sukima-labs/onu-arqueologia-documental

## Uso

Abre `index.html` en un navegador moderno o publícalo mediante GitHub Pages. No necesita instalar programas ni claves. Los enlaces a documentos oficiales requieren internet.

## Funciones implementadas (versión 0.4)

- Panel visual con indicadores y distribución **de la muestra local**.
- Búsqueda por tema, sinónimos comunes, nombres en inglés y referencias de las fichas y trazas.
- Filtros por figura, modalidad, órgano, intervalo de años y orden de presentación.
- Fichas de mandatos, antecedentes documentales, nomenclatura, selección de titulares y alertas de verificación.
- Exportación local CSV con protección básica contra fórmulas de hojas de cálculo.
- Archivo HTML autocontenido que abre sin conexión (excepto enlaces externos).

## Alcance y limitaciones **obligatorias**

Este es un **catálogo demostrativo** de 28 mandatos y 11 trazas, **no el inventario vigente completo de la ONU**. Los gráficos muestran únicamente la muestra; no representan estadísticas oficiales de Naciones Unidas. Algunas referencias históricas tienen alertas y requieren verificación en el acto original. No se ha implementado sincronización automática por internet, visualizaciones geográficas ni validación en todas las versiones de Office. Ninguna ficha sustituye al documento primario.

Un símbolo `E/CN.4/...` identifica una serie documental, **no demuestra por sí mismo que el acto sea una resolución de ECOSOC**. Un informe que reproduce una resolución no debe citarse como si fuese la resolución independiente.

## Pruebas

Ejecuta `node tests/atlas.test.js`. Evalúa estructura, símbolos, clasificación, búsquedas y límites; no realiza una auditoría jurídica exhaustiva de contenido ni verifica HTTP en vivo. Consultar `tests/RESULTADOS.md`.

## Autoría y reutilización

© 2026 Sukima-Labs. Todos los derechos reservados. Publicar públicamente no equivale a conceder licencia de modificación o redistribución. Marcas, símbolos y documentos de la ONU mantienen sus condiciones propias.

Proyecto académico independiente; no representa ni cuenta con aval de Naciones Unidas ni de la Universidad de Alcalá.
''',encoding='utf-8')
print('READY',len(s),'HTML',p)
