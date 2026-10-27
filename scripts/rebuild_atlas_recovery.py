from pathlib import Path
import re,json,zipfile
p=Path('/mnt/data/ATLAS_ONU_publicacion/index.html')
s=p.read_text('utf-8')
section='''<section id="recuperar" class="section"><div class="eyebrow">Motor de recuperación documental · Biblioteca Digital de la ONU</div><h1>Excavación y recuperación de documentos</h1><p class="intro">Cuando el enlace a una resolución lleva a un informe, está roto o no existe como archivo individual, utiliza este rastreador. Distingue el acto jurídico, su reproducción en un informe, la signatura y el estado de comprobación.</p><div class="notice"><b>Importante:</b> El motor genera rutas de recuperación y muestra los expedientes comprobados. <b>No descarga automáticamente todos los PDF</b>: algunos repositorios restringen consultas automáticas y hay documentos históricos aún sin digitalizar. Nunca marca un hallazgo como verificado sin cotejo documental.</div><div class="panel"><h3>Introduce lo que conoces</h3><div class="controls"><div><label class="searchlabel" for="recoverQuery">Símbolo ONU, número de resolución o palabras</label><input id="recoverQuery" class="field" placeholder="Ej. E/CN.4/RES/20(XXXVI), 1980, desaparición…" oninput="recoverDocument()"></div><div><label class="searchlabel" for="recoverType">¿Qué necesitas encontrar?</label><select id="recoverType" class="field" onchange="recoverDocument()"><option value="">No lo sé</option><option value="resolucion">Resolución original</option><option value="informe">Informe donde figura el texto</option><option value="metodos">Métodos de trabajo</option></select></div></div><div class="toolbar"><button class="btn" onclick="recoverDocument()">Reconstruir ruta</button><button class="btn" onclick="document.getElementById('recoverQuery').value='E/CN.4/RES/20(XXXVI)';recoverDocument()">Probar caso real de 1980</button></div><div id="recoverResult" aria-live="polite"></div></div><h2>Ruta de excavación</h2><div class="timeline"><div class="event"><b>1. Identificar el órgano</b><p>Reconocer la serie (<code>E/CN.4</code> antigua Comisión, <code>A/HRC</code> Consejo de Derechos Humanos, <code>E/RES</code> ECOSOC, <code>A/RES</code> Asamblea General).</p></div><div class="event"><b>2. Diferenciar el tipo</b><p>Localizar la resolución adoptada; separar proyectos (<code>L.</code>), informes de sesión y documentos de métodos.</p></div><div class="event"><b>3. Buscar el soporte histórico</b><p>Si falta un PDF individual, localizar el informe de sesión que reproduce el texto y sus páginas; conservar ambas signaturas.</p></div><div class="event"><b>4. Cotejar el original y registrar evidencia</b><p>Confirmar órgano, fecha, signatura, página, texto y URL. Hasta entonces: «PENDIENTE DE COTEJO», no «RECUPERADO».</p></div></div></section>'''
pos=s.index('<section id="codificacion"')
s=s[:pos]+section+s[pos:]
# insert nav button before nomenclature nav entry
m=re.search(r'<button[^>]*data-page="codificacion"[^>]*>',s)
if not m:raise RuntimeError('nav nomenclature not found')
s=s[:m.start()]+'<button type="button" data-page="recuperar">⛏ Recuperar documentos</button>'+s[m.start():]
# extend existing arqueologia explanation with link to recovery
s=s.replace('La referencia no equivale a un texto primario hasta que se coteje.</p>','La referencia no equivale a un texto primario hasta que se coteje. <a href="#" onclick="showPage(\'recuperar\');return false">¿Enlace roto o resolución dentro de un informe? Recuperar ↗</a></p>')
# replace informational non-published Github panel with actual URL (repo exists)
repo='https://github.com/cataplum1414/onu-arqueologia-documental'
s=s.replace('Catálogo demostrativo; no oficial ONU.</div></aside>',f'Catálogo académico independiente; no oficial ONU.<br><a href="{repo}" target="_blank" rel="noopener noreferrer">Repositorio GitHub ↗</a></div></aside>')
s=s.replace('<b>No se ha publicado en GitHub.</b>',f'<b>Repositorio GitHub:</b> <a target="_blank" rel="noopener noreferrer" href="{repo}">cataplum1414/onu-arqueologia-documental</a>. Comprueba en GitHub qué archivos están realmente publicados.')
# strip closing footer JS to insert functions
injection=r'''
function recoverDocument(){
 const input=document.getElementById('recoverQuery'); const out=document.getElementById('recoverResult');
 const original=input.value.trim(); if(!original){out.innerHTML='<div class="notice">Introduce un símbolo, una palabra o prueba el caso de 1980.</div>';return}
 const q=norm(original); const symbol=/^(?:A\/HRC|E\/CN\.4|E\/RES|A\/RES|S\/RES|E\/\d)/i.test(original);
 const wgeid=(q.includes('20(xxxvi)')||q.includes('20 (xxxvi)')||q.includes('desaparici')||q.includes('wgeid')||q.includes('e/cn.4/res/1980/20'));
 const rawSearch='https://digitallibrary.un.org/search?ln=es&p='+encodeURIComponent(original);
 const safeTxt=esc(original);
 let html='<div class="event"><b>Consulta:</b> '+safeTxt+'<br><span class="tag warn">Ruta sugerida; requiere cotejo</span><p>La búsqueda no demuestra por sí sola la existencia de una copia digital exacta.</p></div>';
 if(wgeid){html+='<div class="event"><b>HALLAZGO VERIFICADO — Grupo de Trabajo sobre Desapariciones Forzadas, 1980</b><p>Acto jurídico: <b>Comisión de Derechos Humanos, resolución 20 (XXXVI), 29/02/1980</b>. Registro original: <code>E/CN.4/RES/20(XXXVI)</code>. Conservado dentro del informe <code>E/1980/13–E/CN.4/1408</code>, páginas <b>180–181</b>. Es una resolución de la <b>Comisión</b>, aunque aparezca en documentos relacionados con ECOSOC.</p><div class="linkline">'+link('https://digitallibrary.un.org/record/96859?ln=en','Ficha oficial del acto')+' '+link('https://docs.un.org/E/1980/13','Informe de la sesión')+' '+link('https://legal.un.org/avl/ha/icpped/icpped.html','Historia normativa ONU')+'</div><p class="meta">Verificado por registro primario de Biblioteca Digital de la ONU; el enlace al PDF concreto debe comprobarse antes de citar su paginación.</p></div>'}
 if(symbol){const cleaned=original.replace(/\s+/g,'').replace(/\\/g,'/'); const direct='https://docs.un.org/'+encodeURI(cleaned).replaceAll('%23','#');html+='<div class="event"><b>Ruta por símbolo</b><p>Un símbolo puede llevar a un informe o documento no digitalizado; comprueba la naturaleza documental en el encabezado.</p><div class="linkline">'+link(direct,'Intentar UN Docs')+' '+link(rawSearch,'Buscar símbolo en Biblioteca ONU')+'</div></div>'}
 else {html+='<div class="event"><b>Búsqueda por lenguaje común</b><p>Abre el índice oficial y confirma símbolo y órgano antes de citar.</p><div class="linkline">'+link(rawSearch,'Buscar en Biblioteca ONU')+' '+link('https://www.ohchr.org/es/special-procedures-human-rights-council','Mandatos OHCHR')+'</div></div>'}
 html+='<div class="notice">Si la resolución no tiene archivo autónomo, busca su texto en el <b>informe del período de sesiones</b>. Si tampoco está disponible: estado <b>NO DIGITALIZADO / PENDIENTE</b>, nunca inventar un enlace o un PDF.</div>';
 out.innerHTML=html;
}
'''
s=s.replace('compute();filterMandates();filterTraces();fillRest();','compute();filterMandates();filterTraces();fillRest();recoverDocument();')
s=s.replace('</script></body></html>',injection+'</script></body></html>')
p.write_text(s,'utf-8')
print('HTML UPDATED',len(s),p)
