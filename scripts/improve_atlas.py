from pathlib import Path
import re,json,zipfile,hashlib,datetime,subprocess
root=Path('/mnt/data/ATLAS_ONU_publicacion')
p=root/'index.html';s=p.read_text()
# Improve honest public version, clear independent scope and convenient authoritative queries
s=s.replace('ATLAS <b>ONU</b><span style="color:#b0d6e0;font-size:12px"> / β</span>','ATLAS <b>ONU</b><span style="color:#b0d6e0;font-size:12px"> / 0.6</span>')
s=s.replace('Consulta del catálogo académico local','Buscador académico · Catálogo documental de muestra')
s=s.replace('La referencia no equivale a un texto primario hasta que se coteje.','La referencia no equivale a un texto primario hasta que se coteje.')
# improved onboarding: add quick checks and explicit reference links and limitations
marker='<section id="explorar" class="section">'
if marker in s and 'id="ruta-inicio"' not in s:
 addon='''<div class="panel" id="ruta-inicio"><h3>Cómo investigar sin conocer las siglas</h3><p>1. Busca un tema en lenguaje común. 2. Abre una ficha del mandato. 3. Comprueba el acto creador y su órgano. 4. Si llegas a un informe o enlace roto, entra a <a href="#" onclick="showPage('recuperar');return false">Recuperar documentos</a> y sigue la ruta hasta el texto primario. 5. Cita solo documentos cotejados.</p><div class="notice"><b>Datos locales, no feed en vivo:</b> La información mostrada es una muestra de investigación, no el registro oficial actualizado. <a href="https://www.ohchr.org/es/special-procedures-human-rights-council" target="_blank" rel="noopener noreferrer">Consultar índice oficial vigente ↗</a> · <a href="https://digitallibrary.un.org/" target="_blank" rel="noopener noreferrer">Biblioteca Digital ONU ↗</a>.</div></div>'''
 # add after first opening section and title block? put at beginning of explorar after intro paragraph
 a=s.find(marker)
 after=s.find('</p>',a)
 if after>0:s=s[:after+4]+addon+s[after+4:]
# Add accurate credits in page footer
s=s.replace('Autoría: Jeisson Arley Osorio Mesa','Autoría y coordinación académica: Jeisson Arley Osorio Mesa')
# Avoid false impression of fully working automated syncing
s=s.replace('Última actualización: 27/10/2026','Datos de muestra: 27/10/2026 · sin sincronización automática')
# Freshness button opens official source instead of pretending to sync
if 'id="checkSource"' not in s:
 s=s.replace('<section id="recuperar" class="section">','<section id="recuperar" class="section">')
# Sanitize outgoing links from dataset by allowing only https (function link definition)
old="function link(url,title){return url?`<a href=\"${esc(url)}\" target=\"_blank\" rel=\"noopener noreferrer\">${esc(title)} ↗</a>`:'—'}"
new="function link(url,title){return /^https:\/\//i.test(String(url||''))?`<a href=\"${esc(url)}\" target=\"_blank\" rel=\"noopener noreferrer\">${esc(title)} ↗</a>`:'—'}"
if old in s:s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
# derive code sample for standalone test
script=re.search(r'<script>([\s\S]*?)</script>',s).group(1)
(root/'tests'/'atlas.js').write_text(script)
print('HTML',len(s),'JS',len(script))
