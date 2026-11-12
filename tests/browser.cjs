// Prueba real en Chromium (Playwright). Uso: node tests/browser.cjs
const { chromium } = require('playwright');
const path = require('path'), assert = require('assert');
const URL = process.env.ATLAS_URL || 'file://' + path.resolve(__dirname, '..', 'index.html');
// T75: algunas pantallas leen JSON con fetch, que file:// no permite. Servidor estático del repositorio, solo en 127.0.0.1 y solo mientras corre la prueba.
let _srv = null;
function servidorEstatico() {
  if (_srv) return _srv;
  const http = require('http'), fs = require('fs'), raiz = path.resolve(__dirname, '..');
  const tipos = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.webmanifest': 'application/manifest+json' };
  _srv = new Promise(res => {
    const s = http.createServer((q, r) => {
      const f = path.join(raiz, decodeURIComponent(q.url.split('?')[0]));
      if (!f.startsWith(raiz + path.sep)) { r.writeHead(403); r.end(); return; }
      fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': tipos[path.extname(f)] || 'application/octet-stream' }); r.end(d); });
    });
    s.listen(0, '127.0.0.1', () => { s.unref(); res('http://127.0.0.1:' + s.address().port); });
  });
  return _srv;
}
const esperaReposo = async page => { let a = -1; for (let i = 0; i < 40; i++) { await page.waitForTimeout(150); const y = await page.evaluate(() => scrollY); if (y === a) return; a = y; } }; // espera a que acabe el desplazamiento suave
const todosLosPaises = async page => { while (await page.locator('#pBody .mas button').count()) await page.locator('#pBody .mas button').click(); }; // pulsa «Mostrar más» hasta ver la lista entera
(async () => {
  const browser = await chromium.launch();
  // Las pruebas no deben salir a internet: la búsqueda en vivo (servicio del mini PC) se simula siempre vacía.
  const sinBusquedaReal = r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ consulta: '', total: 0, resultados: [] }) });
  const BUSQ = /sk-atlas\.pig-mimosa\.ts\.net/;
  const _newPage = browser.newPage.bind(browser), _newContext = browser.newContext.bind(browser);
  browser.newPage = async o => { const p = await _newPage(o); await p.route(BUSQ, sinBusquedaReal); return p; };
  browser.newContext = async o => { const c = await _newContext(o); await c.route(BUSQ, sinBusquedaReal); return c; };
  const res = { url: URL, checks: [], errors: [] };
  const ok = (n, c) => { res.checks.push({ n, ok: !!c }); };
  for (const vp of [{ name: 'escritorio', width: 1366, height: 800 }, { name: 'movil', width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport: vp });
    if (!process.env.ATLAS_CAPTURAS) { const orig = page.screenshot.bind(page); page.screenshot = (o) => orig({ ...o, path: undefined }); } // las capturas de audit/ solo se regeneran con ATLAS_CAPTURAS=1
    page.on('pageerror', e => res.errors.push(vp.name + ': ' + e.message));
    page.on('console', m => { if (m.type() === 'error') res.errors.push(vp.name + ' console: ' + m.text()); });
    await page.goto(URL);
    ok(vp.name + ': carga con título', (await page.title()).includes('Atlas ONU'));
    ok(vp.name + ': sin desbordamiento horizontal', await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
    ok(vp.name + ': KPIs renderizados', (await page.textContent('#kpis')).trim().length > 0);
    for (const id of ['explorar', 'arqueologia', 'recuperar', 'seleccion', 'auditoria', 'fuentes']) {
      await page.evaluate(i => showPage(i), id);
      ok(vp.name + ': sección ' + id + ' visible', await page.isVisible('#' + id));
    }
    // Accesibilidad básica (T34)
    await page.goto(URL);
    await page.keyboard.press('Tab');
    ok(vp.name + ': «Saltar al contenido» es lo primero que recibe el foco', await page.evaluate(() => document.activeElement.classList.contains('skip')));
    await page.keyboard.press('Enter');
    ok(vp.name + ': «Saltar al contenido» lleva el foco al contenido', await page.evaluate(() => document.activeElement.id === 'contenido'));
    await page.evaluate(() => showPage('tratados'));
    ok(vp.name + ': el menú marca la pantalla actual (aria-current)', await page.evaluate(() => { const c = document.querySelectorAll('.nav button[aria-current]'); return c.length === 1 && c[0].dataset.page === 'tratados'; }));
    ok(vp.name + ': T78 el menú tiene 5 bloques con título fijo y cada botón cuelga de uno', await page.evaluate(() => { const g = [...document.querySelectorAll('#nav .nav-grupo')].map(x => x.textContent.trim()); const botones = document.querySelectorAll('#nav button[data-page]').length; const sueltos = [...document.querySelectorAll('#nav > button')].length; const primero = document.querySelector('#nav').firstElementChild; return g.join('|') === 'Inicio|Explorar datos|Entender la ONU|Herramientas de consulta|Sobre el proyecto' && botones === sueltos && primero.classList.contains('nav-grupo') && !document.querySelector('#nav .nav-grupo button') && !document.querySelector('#nav .nav-grupo[tabindex]'); }));
    // T88 (#234): nada importante queda escondido. Las 21 entradas del menú anterior a T78 siguen alcanzables con un toque en el menú (o dos si viven en una pestaña de otra pantalla), y los 17 ODS tienen pestaña propia.
    ok(vp.name + ': T88 las 21 entradas del menú anterior siguen alcanzables en ≤2 toques', await page.evaluate(() => { const viejo = ['inicio','noticias','explorar','relatores','sistema','historia','paises','mapa','tratados','siglas','codigos','arqueologia','recuperar','mecanismos','codificacion','seleccion','auditoria','hojaruta','defensores','descargas','fuentes']; const menu = new Set([...document.querySelectorAll('#nav button[data-page]')].map(b => b.dataset.page)); const pestanas = new Set([...document.querySelectorAll('.sc-tabs button')].map(b => (/showPage\('([a-z]+)'\)/.exec(b.getAttribute('onclick')) || [])[1])); return viejo.every(p => menu.has(p) || pestanas.has(p)) && viejo.every(p => document.getElementById(p)); }));
    ok(vp.name + ': T88 los 17 ODS tienen pestaña propia en «Cómo funciona la ONU»', await page.evaluate(() => { showPage('sistema'); const b = document.getElementById('sisT6'); if (!b || !/ODS/.test(b.textContent)) return false; b.click(); const r = document.getElementById('sisP6').style.display !== 'none' && document.querySelectorAll('#sisOdsBox .listline').length === 17; sisTab(5); const dec = !/Objetivos de Desarrollo Sostenible/.test(document.getElementById('sisDec').innerHTML); sisTab(1); return r && dec; }));
    ok(vp.name + ': T81 «Siglas y códigos» es una sola entrada del menú con tres pestañas, y las tres direcciones siguen vivas', await (async () => { const ent = await page.evaluate(() => ({ botones: [...document.querySelectorAll('#nav button')].filter(b => ['siglas', 'codigos', 'codificacion'].includes(b.dataset.page)).map(b => b.dataset.page), sueltas: [...document.querySelectorAll('#nav button')].some(b => ['codigos', 'codificacion'].includes(b.dataset.page)) })); const res = []; for (const id of ['siglas', 'codigos', 'codificacion']) { await page.evaluate(i => showPage(i), id); res.push(await page.evaluate(i => { const sec = document.getElementById(i), t = [...sec.querySelectorAll('.sc-tabs button')], act = document.querySelector('#nav button[aria-current]'); return sec.classList.contains('visible') && t.length === 3 && t.filter(b => b.getAttribute('aria-pressed') === 'true').length === 1 && act && act.dataset.page === 'siglas'; }, id)); } return ent.botones.length === 1 && ent.botones[0] === 'siglas' && !ent.sueltas && res.every(Boolean); })());
    ok(vp.name + ': todas las cabeceras de tabla llevan scope', await page.evaluate(() => [...document.querySelectorAll('th')].every(t => t.hasAttribute('scope'))));
    ok(vp.name + ': ningún role=tablist sin pestañas', await page.evaluate(() => !document.querySelector('[role=tablist]')));
    await page.evaluate(() => showPage('explorar'));
    await page.fill('#q', 'tortura'); await page.evaluate(() => filterMandates());
    ok(vp.name + ': búsqueda "tortura"', /tortura/i.test(await page.textContent('#mandBody')));
    await page.fill('#q', 'enforced disappearance'); await page.evaluate(() => filterMandates());
    ok(vp.name + ': búsqueda EN con sinónimos', /desaparici/i.test(await page.textContent('#mandBody')));
    await page.fill('#q', ''); await page.evaluate(() => filterMandates());
    // P6: de 20 en 20 en escritorio; en el celular (≤650 px) las listas de tarjetas largas van de menos en menos (paso() en index.html)
    const pMand = await page.evaluate(() => paso('mand'));
    ok(vp.name + ': ' + pMand + ' mandatos y «Mostrar más»', pMand === (vp.width <= 650 ? 8 : 20) && (await page.locator('#mandBody tr:not(.mas)').count()) === pMand && (await page.locator('#mandBody tr.mas button').count()) === 1);
    while (await page.locator('#mandBody tr.mas button').count()) await page.locator('#mandBody tr.mas button').click();
    ok(vp.name + ': 57 mandatos tras mostrar más', (await page.locator('#mandBody tr:not(.mas)').count()) === 57);
    ok(vp.name + ': P6 tras el último «Mostrar más» el foco va al primer mandato nuevo, no al principio de la página', await page.evaluate(() => document.activeElement !== document.body && !!document.activeElement.closest('#mandBody')));
    await page.fill('#q', 'agua'); await page.evaluate(() => filterMandates());
    await page.locator('#mandBody button', { hasText: 'Ver ficha' }).first().click();
    ok(vp.name + ': clic en «Ver ficha» abre cronología', /Cadena de actos jurídicos/.test(await page.textContent('#cardsResults')) && /A\/HRC\/RES\/60\/9/.test(await page.textContent('#cardsResults')));
    await page.evaluate(() => showPage('inicio'));
    await page.selectOption('#guiadaSel', { index: 1 }); await page.getByRole('button', { name: 'Ver mandatos' }).click();
    ok(vp.name + ': búsqueda guiada lleva a mandatos de tortura/detención', await page.isVisible('#explorar') && /tortura|detenci/i.test(await page.textContent('#mandBody')));
    await page.evaluate(() => showPage('inicio'));
    await page.fill('#quick', 'mi hijo desapareció'); await page.waitForTimeout(500);
    ok(vp.name + ': búsqueda inteligente muestra resultados al escribir', /Desapariciones/.test(await page.textContent('#smartOut')) && /Quisiste decir/.test(await page.textContent('#smartOut')));
    await page.locator('#smartOut button', { hasText: 'Ver ficha' }).first().click();
    ok(vp.name + ': desde el resultado se abre la ficha', /Cadena de actos/.test(await page.textContent('#cardsResults')));
    await page.evaluate(() => showPage('inicio')); await page.fill('#quick', 'comida');  await page.waitForTimeout(500);
    await page.locator('#smartOut button', { hasText: 'Ver texto y ruta' }).first().click();
    ok(vp.name + ': desde el resultado se abre la recuperación del texto', await page.isVisible('#recuperar') && /LOCALIZADO/.test(await page.textContent('#recoverResult')));
    if (await page.isVisible('#burger')) { await page.click('#burger'); await page.waitForTimeout(350); }
    await page.getByRole('button', { name: /Países/ }).first().click();
    ok(vp.name + ': sección Países visible con 196 filas', await page.isVisible('#paises') && (await page.locator('#pBody tr').count()) === (await page.evaluate(() => paso('paises'))) + 1 && new RegExp((await page.evaluate(() => paso('paises'))) + ' de 196').test(await page.textContent('#pBody')) && new RegExp('Mostrar ' + (await page.evaluate(() => paso('paises'))) + ' más').test(await page.textContent('#pBody')) && (await todosLosPaises(page), (await page.locator('#pBody tr').count()) === 196));
    await page.getByRole('button', { name: /^América Latina y el Caribe \(\d+\)/ }).click(); await page.waitForTimeout(200);
    ok(vp.name + ': chip «América Latina y el Caribe» → 33 países', (await todosLosPaises(page), (await page.locator('#pBody tr').count()) === 33) && /Colombia/.test(await page.textContent('#pBody')));
    await page.getByRole('button', { name: /^Todos \(\d+\)/ }).click(); await page.waitForTimeout(200);
    await page.fill('#pQ', 'India'); await page.getByRole('button', { name: 'Buscar' }).first().click(); await page.waitForTimeout(500);
    const box = await page.locator('#pOut .detail h2').boundingBox();
    ok(vp.name + ': al buscar India su ficha queda a la vista (sin tener que desplazarse a ciegas)', box && box.y < (vp.height * 0.9) && /Adhesión 10 abr 1979/.test(await page.textContent('#pOut')) && /Firmó 14 oct 1997/.test(await page.textContent('#pOut')));
    await page.fill('#pQ', 'India'); await page.getByRole('button', { name: 'Buscar' }).first().click(); await page.waitForFunction(() => /CCPR\/C\/IND\/CO\/4/.test(document.getElementById('pDocs').textContent), null, { timeout: 8000 }).catch(() => {});
    await page.waitForFunction(() => document.querySelector('#pVotos svg'), null, { timeout: 8000 }).catch(() => {});
    const vb = await page.evaluate(() => { const b = document.getElementById('pVotos'); return b.querySelectorAll('svg rect').length > 4 && /cada grupo de barras/.test(b.textContent) && !!b.querySelector('details.datos table'); });
    await page.evaluate(() => votosCambia('linea')); await page.waitForFunction(() => !/cada grupo de barras/.test(document.getElementById('pVotos').textContent) && document.querySelector('#pVotos svg'), null, { timeout: 8000 }).catch(() => {});
    const vl = await page.evaluate(() => !/cada grupo de barras/.test(document.getElementById('pVotos').textContent) && !!document.querySelector('#pVotos svg'));
    await page.evaluate(() => votosCambia('barras')); await page.waitForFunction(() => document.querySelectorAll('#pVotos svg rect').length > 4, null, { timeout: 8000 }).catch(() => {});
    ok(vp.name + ': votos en la Asamblea: por defecto barras por década con su tabla, y se puede volver a la línea (#186)', vb && vl && (await page.evaluate(() => document.querySelectorAll('#pVotos svg rect').length > 4)));
    await page.evaluate(() => votosCambia('sino')); await page.waitForFunction(() => /cada barra es un año/.test(document.getElementById('pVotos').textContent), null, { timeout: 8000 }).catch(() => {});
    const vs = await page.evaluate(() => { const b = document.getElementById('pVotos'); return b.querySelectorAll('svg rect').length > 20 && !!b.querySelector('details.datos table') && b.querySelectorAll('.toolbar button').length === 3; });
    ok(vp.name + ': votos en la Asamblea: tercera vista sí/no/abstención con su tabla y tres botones (#186, opción B)', vs);
    await page.evaluate(() => votosCambia('barras'));
    const dd = await page.textContent('#pDocs');
    ok(vp.name + ': la ficha tiene el menú «Qué quieres ver» con 10 saltos y el botón de comparar', (await page.locator('#pNav button[onclick^="irSeccion"]').count()) === 10 && (await page.locator('#pNav button[onclick^="compararCon"]').count()) === 1);
    await page.locator('#pNav button', { hasText: 'EPU' }).click(); await esperaReposo(page);
    const epuY = await page.evaluate(() => document.getElementById('ps-epu').getBoundingClientRect().top);
    ok(vp.name + ': «EPU» lleva a su bloque', epuY >= -5 && epuY < vp.height * 0.5);
    ok(vp.name + ': con la ficha abajo aparece «↑ Qué quieres ver» y vuelve al menú', await page.isVisible('#pTop') && (await page.click('#pTop'), await esperaReposo(page), await page.evaluate(() => Math.abs(document.getElementById('pNav').getBoundingClientRect().top) < 90)));
    ok(vp.name + ': el menú de la ficha no desborda horizontalmente', await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
    // T62: línea de tiempo de India (tratados, comités, EPU, visitas), con filtros y orden
    await page.locator('#pNav button', { hasText: 'Línea de tiempo' }).click(); await esperaReposo(page);
    const lnY = await page.evaluate(() => document.getElementById('ps-linea').getBoundingClientRect().top), lnAnios = await page.locator('#pLinea .tl li.tl-y').allTextContents(), lnN = await page.locator('#pLinea .tl li.tl-e').count();
    ok(vp.name + ': «Línea de tiempo» lleva a su bloque: años del más reciente al más antiguo y con los documentos ya cargados', lnY >= -5 && lnY < vp.height * 0.5 && lnN > 0 && lnAnios.length > 1 && lnAnios[0] >= lnAnios[lnAnios.length - 1] && (await page.locator('#pLinea .tl-comite').count()) > 0 && /Fuentes:/.test(await page.textContent('#pLinea')));
    if (await page.locator('#pLinea .mas button').count()) { await page.click('#pLinea .mas button'); await page.waitForTimeout(150); ok(vp.name + ': «Ver más» en la línea de tiempo añade hechos', (await page.locator('#pLinea .tl li.tl-e').count()) > lnN); }
    await page.locator('#pLinea button', { hasText: /^Tratados \(\d+\)/ }).click(); await page.waitForTimeout(150);
    const lnTr = await page.locator('#pLinea .tl li.tl-e').count();
    ok(vp.name + ': filtro «Tratados» de la línea de tiempo: solo firmas y ratificaciones, y queda pulsado', lnTr > 0 && lnTr === (await page.locator('#pLinea .tl li.tl-tratado').count()) && (await page.getAttribute('#pLinea button[aria-pressed="true"]', 'onclick')) === "setLn('tratado')" && /Adhesión: pasa a ser parte en PIDCP/.test(await page.textContent('#pLinea')));
    await page.click('#lnOrden'); await page.waitForTimeout(150);
    ok(vp.name + ': «Más antiguos primero» empieza en 1967 (firma de la CERD) y la línea no desborda', (await page.locator('#pLinea .tl li.tl-y').first().textContent()) === '1967' && /Firma: CERD/.test(await page.locator('#pLinea .tl li.tl-e').first().textContent()) && await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
    await page.click('#lnOrden'); await page.locator('#pLinea button', { hasText: /^Todo \(\d+\)/ }).click();
    // T63: glosario de siglas al tocar (en la ficha de India, sin salir de la página). T91: el título del EPU va en un <summary> plegable,
    //      donde no se marcan siglas (tocarla abriría o cerraría el bloque): se usa el «EPU» del texto de la ficha
    await page.waitForTimeout(250);
    ok(vp.name + ': las siglas del texto de la ficha quedan marcadas y las de botones y enlaces no', (await page.locator('#pOut abbr.sg[data-k="EPU"]').count()) > 0 && (await page.locator('#pNav abbr.sg, #pDocs a abbr.sg, #paises button abbr.sg').count()) === 0);
    const sgA = page.locator('#pOut abbr.sg[data-k="EPU"]').first(); await sgA.scrollIntoViewIfNeeded(); await sgA.click(); await page.waitForTimeout(150);
    const sgBox = await page.locator('#sgPop').boundingBox();
    ok(vp.name + ': tocar «EPU» abre su significado junto a la sigla, dentro de la pantalla', await page.isVisible('#sgPop') && /Examen Peri[oó]dico Universal/.test(await page.textContent('#sgPop')) && /Universal Periodic Review/.test(await page.textContent('#sgPop')) && sgBox && sgBox.x >= 0 && sgBox.x + sgBox.width <= vp.width + 1 && sgBox.y >= 0 && sgBox.y + sgBox.height <= vp.height + 1 && await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.keyboard.press('Escape'); await page.waitForTimeout(100);
    ok(vp.name + ': Escape cierra la tarjeta de la sigla', !(await page.isVisible('#sgPop')));
    await sgA.click(); await page.waitForTimeout(100); await page.click('#sgPop button:has-text("Ver en «Siglas»")'); await page.waitForTimeout(300);
    ok(vp.name + ': «Ver en Siglas» abre el diccionario con la sigla buscada', await page.isVisible('#siglas') && (await page.inputValue('#sigQ')) === 'EPU' && !(await page.isVisible('#sgPop')) && (await page.locator('#siglas abbr.sg').count()) === 0);
    await page.evaluate(() => showPage('paises'));
    // T40: Relatores y relatoras
    await page.evaluate(() => showPage('relatores')); await page.waitForTimeout(250);
    // P6: de 20 en 20; «Mostrar 20 más» hasta tenerlos todos
    const rN0 = await page.locator('#rOut .rel-card').count(), relN = await page.evaluate(() => REL.length), pRel = await page.evaluate(() => paso('rel'));
    ok(vp.name + ': P6 «Relatores y relatoras» abre con ' + pRel + ' tarjetas, el recuento «' + pRel + ' de N» y «Mostrar ' + pRel + ' más»', rN0 === pRel && relN > pRel && new RegExp(pRel + ' de ' + relN).test(await page.textContent('#rOut .mas')) && (await page.locator('#rOut .mas button', { hasText: 'Mostrar ' + pRel + ' más' }).count()) === 1);
    await page.locator('#rOut .mas button').click(); await page.waitForTimeout(100);
    ok(vp.name + ': P6 al pulsar «Mostrar más» el foco se queda en el botón, que baja con la lista', (await page.locator('#rOut .rel-card').count()) === 2 * pRel && await page.evaluate(() => document.activeElement && !!document.activeElement.closest('#rOut .mas')));
    while (await page.locator('#rOut .mas button').count()) { await page.locator('#rOut .mas button').click(); await page.waitForTimeout(50); }
    const rN = await page.locator('#rOut .rel-card').count();
    ok(vp.name + ': «Relatores y relatoras» muestra una tarjeta por titular, con mandato y nacionalidad, sin desbordar', rN >= 60 && rN === relN && /Nacionalidad:/.test(await page.textContent('#rOut')) && await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.selectOption('#rCargo', 'gt'); await page.waitForTimeout(150);
    const rGt = await page.locator('#rOut .rel-card').count(), rGtTag = await page.locator('#rOut .rel-card .tag', { hasText: 'Grupo de trabajo' }).count();
    ok(vp.name + ': filtro «Grupo de trabajo» deja solo miembros de grupos de trabajo', rGt > 0 && rGt < rN && rGtTag === rGt);
    await page.selectOption('#rCargo', ''); await page.waitForTimeout(150);
    await page.locator('#rOut .rel-card').first().getByRole('button', { name: 'Ver el mandato' }).click(); await page.waitForTimeout(300);
    ok(vp.name + ': desde una tarjeta, «Ver el mandato» abre su ficha en Explorar', await page.isVisible('#explorar'));
    await page.evaluate(() => showPage('paises'));
    // T75: Seguimiento de recomendaciones (EPU). Colombia, 3 exámenes y 602 recomendaciones (160 + 211 + 231) en data/seguimiento/COL.json.
    //      Con file:// el navegador no deja leer el JSON del país: la pantalla avisa. El resto se prueba en otra pestaña servida por HTTP.
    await page.evaluate(() => showPage('seguimiento')); await page.waitForFunction(() => document.querySelectorAll('#segPais option').length > 150);
    let sp = page;
    if (URL.startsWith('file:')) {
      await page.selectOption('#segPais', 'COL'); await page.waitForSelector('#segOut .notice');
      ok(vp.name + ': T75 desde una copia en el disco (file://) avisa de que se abra la web publicada', /web publicada/.test(await page.textContent('#segOut')));
      sp = await browser.newPage({ viewport: vp }); await sp.goto(await servidorEstatico() + '/index.html#seguimiento');
      await sp.waitForFunction(() => document.querySelectorAll('#segPais option').length > 150);
    }
    await sp.selectOption('#segPais', 'COL'); await sp.waitForSelector('.seg-recs li');
    const seg = await sp.evaluate(() => ({ ex: document.querySelectorAll('.seg-ex').length, li: document.querySelectorAll('.seg-recs li').length, desborda: document.documentElement.scrollWidth > window.innerWidth + 1, fuente: [...document.querySelectorAll('.seg-recs .pill-ok a')].every(a => /^https:\/\/digitallibrary\.un\.org\//.test(a.href)) }));
    ok(vp.name + ': T75 «Seguimiento» de Colombia: 3 exámenes, 40 recomendaciones a la vista, cada «Apoyada» enlaza a la Biblioteca Digital y no desborda', seg.ex === 3 && seg.li === 40 && seg.fuente && !seg.desborda, seg);
    await sp.selectOption('#segCiclo', '4'); await sp.selectOption('#segResp', 'nd');
    const segNd = await sp.evaluate(() => [document.querySelectorAll('.seg-recs li').length, document.querySelectorAll('.seg-recs .pill-nd').length, document.querySelectorAll('.seg-recs .pill-ok,.seg-recs .pill-neutro').length]);
    ok(vp.name + ': T75 filtro «Sin información» del 4.º ciclo: solo pastillas «Sin información», nunca un estado inventado', segNd[0] === 40 && segNd[1] === 40 && segNd[2] === 0, segNd);
    await sp.selectOption('#segCmpSel', 'MEX'); await sp.selectOption('#segCmpSel', 'ARG');
    ok(vp.name + ': T75 comparador con 3 países (columna fija + 3) y 15 filas', await sp.evaluate(() => document.querySelectorAll('#segCmp thead th').length === 4 && document.querySelectorAll('#segCmp tbody tr').length === 15));
    if (sp !== page) await sp.close();
    // T76 fase 1: «Tengo un caso: ¿adónde acudo?». data/vias.js se carga con <script>: funciona también desde file://.
    await page.evaluate(() => showPage('vias')); await page.waitForFunction(() => document.querySelectorAll('#viaOut .cmpx tbody tr').length >= 11 && document.querySelectorAll('#viaPais option').length > 150);
    ok(vp.name + ': T76 la tabla de vías trae 11 vías con su franja «En pruebas» y los requisitos plegados', await page.evaluate(() => document.querySelectorAll('#viaOut .cmpx tbody tr').length === 11 && !!document.querySelector('#vias .asis-franja') && document.querySelectorAll('#viaOut details[data-plg^="via-"]').length === 11));
    await page.selectOption('#viaPais', 'COL'); await page.waitForTimeout(150);
    const via = await page.evaluate(() => { const fila = t => [...document.querySelectorAll('#viaOut .cmpx tbody tr')].find(r => r.querySelector('th').textContent.includes(t)); const c = t => fila(t).querySelector('td').textContent; return { ccpr: c('Derechos Humanos'), cerd: c('Discriminación Racial'), cat: c('contra la Tortura'), cmw: c('Trabajadores Migratorios'), plazoCerd: fila('Discriminación Racial').querySelectorAll('td')[1].textContent, desborda: document.documentElement.scrollWidth > window.innerWidth + 1 }; });
    ok(vp.name + ': T76 para Colombia: Comité de Derechos Humanos «Sí», CERD «Sí, con su declaración» (10-07-2026) con 6 meses leídos en el original, CAT «Es parte, pero no hizo la declaración», trabajadores migratorios «Aún no funciona» con 6 de 10 declaraciones, sin desbordar', /^Sí/.test(via.ccpr) && /Sí, con su declaración/.test(via.cerd) && /no hizo la declaración/.test(via.cat) && /6 de 10 declaraciones/.test(via.cmw) && /6 meses/.test(via.plazoCerd) && /Leído en el original/.test(via.plazoCerd) && /Aún no funciona/.test(via.cmw) && !via.desborda, via);
    await page.evaluate(() => viaAbrir('cescr')); await page.waitForTimeout(150);
    ok(vp.name + ': T76 al abrir una vía se ve cada requisito con la cita del tratado y dónde lo dice', await page.evaluate(() => { const d = document.querySelector('details[data-plg="via-cescr"]'); return d.open && d.querySelectorAll('.via-req li').length === 7 && d.querySelectorAll('blockquote').length === 7 && /A\/RES\/63\/117/.test(d.textContent); }));
    // T11/T24: Mapa del mundo con capas
    await page.evaluate(() => showPage('mapa')); await page.waitForSelector('#mpSvg path.mp-p');
    const mpDesborda = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    ok(vp.name + ': «Mapa del mundo» dibuja los 196 países y no desborda la pantalla', (await page.locator('#mpSvg path.mp-p').count()) === 196 && !mpDesborda);
    await page.selectOption('#mpCapa', 'tratado'); await page.selectOption('#mpTrat', 'IV-2');
    const mpLey = (await page.textContent('#mpLeyenda')).match(/\((\d+)\)/g).map(x => +x.slice(1, -1)).reduce((a, b) => a + b, 0);
    ok(vp.name + ': Mapa: con «Un tratado concreto» aparece su selector y la leyenda cuenta los 196 países', await page.isVisible('#mpTrat') && mpLey === 196);
    await page.locator('#mpSvg path[data-id="ESP"]').dispatchEvent('click');
    ok(vp.name + ': Mapa: tocar un país muestra su dato y lo marca', /España/.test(await page.textContent('#mpInfo')) && /Es parte/.test(await page.textContent('#mpInfo')) && (await page.locator('#mpSvg path.sel').count()) === 1 && (await page.inputValue('#mpPais')) === 'ESP');
    await page.selectOption('#mpCapa', 'invitacion');
    ok(vp.name + ': Mapa: al cambiar de capa se conserva el país y cambia su dato', /invitación permanente/.test(await page.textContent('#mpInfo')) && !(await page.isVisible('#mpTrat')));
    // T68: capas de conflictos armados (UCDP) y de comunicaciones de los relatores
    await page.selectOption('#mpCapa', 'conflictos'); await page.waitForFunction(() => /Fuente: UCDP/.test(document.getElementById('mpLeyenda').textContent));
    const sumaLey = async () => (await page.textContent('#mpLeyenda')).match(/\((\d+)\)/g).map(x => +x.slice(1, -1)).reduce((a, b) => a + b, 0);
    ok(vp.name + ': Mapa: capa «Conflictos armados» muestra el selector de año, la fuente y la leyenda cuenta los 196 países', await page.isVisible('#mpAnio') && (await page.locator('#mpAnio option').count()) > 70 && /CC BY 4.0/.test(await page.textContent('#mpLeyenda')) && (await sumaLey()) === 196);
    await page.evaluate(() => mpElegir('UKR')); await page.selectOption('#mpAnio', '2023');
    ok(vp.name + ': Mapa: conflictos 2023: Ucrania tiene un conflicto armado estatal con 1000 o más muertes en combate', /Conflictos armados estatales en 2023: 1/.test(await page.textContent('#mpInfo')) && /1000 o más/.test(await page.textContent('#mpInfo')));
    await page.selectOption('#mpAnio', '1950'); await page.evaluate(() => mpElegir('ESP'));
    ok(vp.name + ': Mapa: conflictos: al cambiar de año cambian los colores y España en 1950 sale sin conflicto', /UCDP no registra en 1950/.test(await page.textContent('#mpInfo')) && (await sumaLey()) === 196);
    await page.selectOption('#mpCapa', 'comunicaciones'); await page.waitForFunction(() => !/Cargando/.test(document.getElementById('mpLeyenda').textContent));
    ok(vp.name + ': Mapa: capa «Comunicaciones» oculta el año, y la leyenda cuenta los 196 países', !(await page.isVisible('#mpAnio')) && (await sumaLey()) === 196);
    await page.evaluate(() => mpElegir('COL'));
    ok(vp.name + ': Mapa: comunicaciones: el dato de un país es la suma de sus informes', await page.evaluate(() => { const n = window.COMUNICACIONES.paises.COL.reduce((a, x) => a + x[1], 0); return document.getElementById('mpInfo').textContent.includes(': ' + n); }));
    // T68 (c): capa de recomendaciones del EPU por ciclo (cifras de data/epu.js, contadas de los informes del Grupo de Trabajo)
    await page.selectOption('#mpCapa', 'epu'); await page.waitForFunction(() => !/Cargando/.test(document.getElementById('mpLeyenda').textContent));
    ok(vp.name + ': Mapa: capa «EPU» muestra el selector de ciclo (2, 3 y 4; abre en el último), oculta el año y cita la fuente', await page.isVisible('#mpCiclo') && !(await page.isVisible('#mpAnio')) && (await page.locator('#mpCiclo option').count()) === 3 && (await page.inputValue('#mpCiclo')) === '4' && /Grupo de Trabajo del EPU/.test(await page.textContent('#mpLeyenda')));
    ok(vp.name + ': Mapa: EPU: la leyenda cuenta los 196 países en cada ciclo', await (async () => { for (const c of ['4', '3', '2']) { await page.selectOption('#mpCiclo', c); if ((await sumaLey()) !== 196) return false; } return true; })());
    await page.selectOption('#mpCiclo', '3'); await page.evaluate(() => mpElegir('COL'));
    ok(vp.name + ': Mapa: EPU: el dato de Colombia es la cifra contada del informe del ciclo 3', await page.evaluate(() => { const f = window.EPU.p.COL.find(x => x[0] === 3); return !!f && document.getElementById('mpInfo').textContent.includes('ciclo 3 del EPU (' + f[3] + '): ' + f[1]); }));
    await page.selectOption('#mpCiclo', '4'); await page.evaluate(() => mpElegir(PAISES.find(p => !(window.EPU.p[p.id] || []).some(x => x[0] === 4)).id));   // el ciclo 4 aún no ha examinado a todos
    ok(vp.name + ': Mapa: EPU: un país sin informe de ese ciclo sale «sin cifra», no con un cero', /Sin cifra de este ciclo/.test(await page.textContent('#mpInfo')) && !/: 0\b/.test(await page.textContent('#mpInfo')));
    // #185: línea de tiempo (deslizador de años + animación) y fecha del dato en cada capa
    await page.selectOption('#mpCapa', 'tratado'); await page.selectOption('#mpTrat', 'IV-2'); await page.evaluate(() => mpElegir('ESP'));
    ok(vp.name + ': Mapa: «Un tratado concreto» tiene deslizador de años (1948 a hoy) y cita la fecha del dato', await page.isVisible('#mpDesliza') && (await page.$eval('#mpDesliza', e => e.min + '-' + e.max)).startsWith('1948-') && /Datos al 20\d\d-\d\d-\d\d/.test(await page.textContent('#mpLeyenda')));
    await page.$eval('#mpDesliza', e => { e.value = 1960; e.dispatchEvent(new Event('input', { bubbles: true })); });
    ok(vp.name + ': Mapa: tratado a 1960: España aún no era parte, la leyenda sigue sumando 196 y el texto dice el año', /En 1960 no era parte/.test(await page.textContent('#mpInfo')) && (await sumaLey()) === 196);
    await page.$eval('#mpDesliza', e => { e.value = e.max; e.dispatchEvent(new Event('input', { bubbles: true })); });
    ok(vp.name + ': Mapa: tratado en el último año vuelve al dato de hoy (España es parte)', /Es parte/.test(await page.textContent('#mpInfo')));
    await page.selectOption('#mpCapa', 'basicos');
    const cero = async y => { await page.$eval('#mpDesliza', (e, y) => { e.value = y; e.dispatchEvent(new Event('input', { bubbles: true })); }, y); return page.evaluate(() => PAISES.filter(p => mpValor(p).n === 0).length); };
    const c1970 = await cero(1970), c2026 = await cero(await page.$eval('#mpDesliza', e => e.max));
    ok(vp.name + ': Mapa: tratados básicos por año: en 1970 hay muchos más países sin ningún tratado que hoy', c1970 > c2026 + 50 && (await page.evaluate(() => PAISES.length)) === 196);
    await page.selectOption('#mpCapa', 'invitacion');
    ok(vp.name + ': Mapa: invitación permanente por año: antes de 1999 nadie la había cursado y hoy sí', await (async () => { await page.$eval('#mpDesliza', e => { e.value = e.min; e.dispatchEvent(new Event('input', { bubbles: true })); }); const a = await page.evaluate(() => PAISES.filter(p => mpValor(p).k === 'si').length); await page.$eval('#mpDesliza', e => { e.value = e.max; e.dispatchEvent(new Event('input', { bubbles: true })); }); const b = await page.evaluate(() => PAISES.filter(p => mpValor(p).k === 'si').length); return a < 10 && b > 100; })());
    await page.selectOption('#mpCapa', 'mandato');
    ok(vp.name + ': Mapa: capas sin años ocultan el deslizador', !(await page.isVisible('#mpTiempo')));
    await page.selectOption('#mpCapa', 'conflictos'); await page.waitForFunction(() => document.getElementById('mpAnio').options.length > 50);
    ok(vp.name + ': Mapa: conflictos: el deslizador va de 1946 a 2025 y sigue al selector de año', (await page.$eval('#mpDesliza', e => e.min + '-' + e.max)) === '1946-2025' && await (async () => { await page.selectOption('#mpAnio', '1999'); return (await page.$eval('#mpDesliza', e => e.value)) === '1999' })());
    await page.$eval('#mpDesliza', e => { e.value = 2003; e.dispatchEvent(new Event('input', { bubbles: true })); });
    ok(vp.name + ': Mapa: mover el deslizador cambia el año del mapa', (await page.$eval('#mpAnio', e => e.value)) === '2003');
    await page.click('#mpPlay'); await page.waitForTimeout(1500);
    const anAnim = +(await page.$eval('#mpDesliza', e => e.value));
    ok(vp.name + ': Mapa: «Animar» recorre los años solo (sigue desde el año del deslizador, queda pulsado y cambia el botón a «Pausar»)', anAnim > 2003 && anAnim <= 2025 && (await page.getAttribute('#mpPlay', 'aria-pressed')) === 'true' && /Pausar/.test(await page.textContent('#mpPlay')));
    await page.click('#mpPlay'); const anPar = await page.$eval('#mpDesliza', e => e.value); await page.waitForTimeout(1100);
    ok(vp.name + ': Mapa: «Pausar» detiene la animación en el año en que está', (await page.$eval('#mpDesliza', e => e.value)) === anPar && /Animar/.test(await page.textContent('#mpPlay')));
    await page.click('#mpPlay'); await page.selectOption('#mpCapa', 'basicos'); const anCap = await page.$eval('#mpDesliza', e => e.value); await page.waitForTimeout(1200);
    ok(vp.name + ': Mapa: cambiar de capa con la animación en marcha la detiene', (await page.$eval('#mpDesliza', e => e.value)) === anCap && (await page.getAttribute('#mpPlay', 'aria-pressed')) === 'false');
    await page.selectOption('#mpCapa', 'epu'); await page.waitForFunction(() => !/Cargando/.test(document.getElementById('mpLeyenda').textContent));
    ok(vp.name + ': Mapa: EPU: el deslizador recorre los ciclos 2 a 4 y sigue al selector', (await page.$eval('#mpDesliza', e => e.min + '-' + e.max)) === '2-4' && await (async () => { await page.$eval('#mpDesliza', e => { e.value = 3; e.dispatchEvent(new Event('input', { bubbles: true })); }); return (await page.$eval('#mpCiclo', e => e.value)) === '3'; })());
    await page.selectOption('#mpCapa', 'basicos');
    ok(vp.name + ': Mapa: al dejar la capa del EPU se oculta el ciclo', !(await page.isVisible('#mpCiclo')));
    await page.evaluate(() => mpElegir('ESP'));
    // #184: el zoom cambia el recuadro visible (viewBox), no el ancho de la caja; centra, arrastra y no atrapa el scroll
    const vbW = () => page.$eval('#mpSvg', e => e.viewBox.baseVal.width), vbX = () => page.$eval('#mpSvg', e => e.viewBox.baseVal.x);
    const caja0 = await page.$eval('#mpSvg', e => Math.round(e.getBoundingClientRect().width)), vb0 = await vbW();
    await page.evaluate(() => mpZoomar(0)); await page.evaluate(() => mpElegir('ESP')); await page.click('#mapa .mp-zoom button:has-text("Acercar")');
    const centroEsp = await page.evaluate(() => { const v = document.getElementById('mpSvg').viewBox.baseVal, b = document.querySelector('#mpSvg path[data-id="ESP"]').getBBox(); return Math.abs(v.x + v.width / 2 - (b.x + b.width / 2)) < v.width * 0.06; });
    ok(vp.name + ': Mapa: «Acercar» reduce el recuadro visible, no ensancha la caja ni desborda la página, y se centra en el país elegido', (await vbW()) < vb0 && Math.round(await page.$eval('#mpSvg', e => e.getBoundingClientRect().width)) === caja0 && centroEsp && !(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)));
    await page.click('#mapa .mp-zoom button:has-text("Acercar")'); await page.click('#mapa .mp-zoom button:has-text("Acercar")');
    await page.locator('#mpMapa').scrollIntoViewIfNeeded(); await page.waitForTimeout(200); const x1 = await vbX(), cj = await page.locator('#mpMapa').boundingBox();
    await page.mouse.move(cj.x + cj.width / 2, cj.y + cj.height / 2); await page.mouse.down(); await page.mouse.move(cj.x + cj.width / 2 + 90, cj.y + cj.height / 2 + 10, { steps: 6 }); await page.mouse.up();
    const x2 = await vbX();
    ok(vp.name + ': Mapa: arrastrar con el ratón mueve el mapa acercado y no cambia el país elegido', x2 < x1 && (await page.evaluate(() => mpSel)) === 'ESP');
    await page.click('#mapa .mp-pan button[aria-label="Mover a la derecha"]');
    ok(vp.name + ': Mapa: las flechas de «Mover el mapa» lo desplazan', (await vbX()) > x2);
    await page.click('#mapa .mp-zoom button:has-text("Ver todo")');
    ok(vp.name + ': Mapa: «Ver todo el mapa» vuelve al recuadro completo y centrado', Math.abs((await vbW()) - vb0) < 1 && await page.evaluate(() => { const v = document.getElementById('mpSvg').viewBox.baseVal, W = window.MAPA.vb[0]; return Math.abs(v.x + v.width / 2 - W / 2) < 2; }));
    ok(vp.name + ': Mapa: el marco no atrapa el scroll de la página (sin barras internas; un dedo vertical pasa de largo)', await page.evaluate(() => { const w = document.getElementById('mpWrap'), c = getComputedStyle(w); return c.overflow === 'hidden' && /pan-y/.test(c.touchAction) && c.overscrollBehaviorY !== 'contain'; }));
    // #183: colores propios (no los dorados de la plantilla) y con contraste ≥ 3:1 sobre el fondo del mapa en todas las capas
    const lum = h => { const c = h.match(/\d+/g).slice(0, 3).map(n => { n /= 255; return n <= .03928 ? n / 12.92 : ((n + .055) / 1.055) ** 2.4; }); return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]; };
    const malos = [];
    for (const modo of ['dark', 'light']) { // #228: la paleta del mapa se mide en los dos modos
    await page.evaluate(m => atlasTema(m), modo);
    const bgMapa = await page.$eval('#mpWrap', e => getComputedStyle(e).backgroundColor);
    for (const capa of ['basicos', 'tratado', 'invitacion', 'mandato', 'comision', 'conflictos', 'comunicaciones', 'epu']) {
      await page.selectOption('#mpCapa', capa); await page.waitForFunction(() => !/Cargando/.test(document.getElementById('mpLeyenda').textContent));
      const cols = await page.evaluate(() => [...document.querySelectorAll('#mpLeyenda .mp-sw, #mpLeyenda .mp-esc i')].map(e => getComputedStyle(e).backgroundColor));
      for (const c of cols) { const [a, b] = [lum(c), lum(bgMapa)].sort((x, y) => y - x); const cr = (a + .05) / (b + .05); const [r, g, bl] = c.match(/\d+/g).map(Number); const dorado = r > 150 && g > 100 && bl < 130 && r > g && g > bl; if (cr < 1.8 && c !== 'rgb(50, 56, 65)') malos.push(modo + ' ' + capa + ' ' + c + ' contraste ' + cr.toFixed(2)); if (dorado) malos.push(modo + ' ' + capa + ' ' + c + ' dorado de la plantilla'); }
    }
    }
    await page.evaluate(() => atlasTema('auto'));
    ok(vp.name + ': Mapa: ningún color de las leyendas se confunde con el fondo del mapa ni con el dorado de la plantilla' + (malos.length ? ' → ' + malos.join('; ') : ''), !malos.length);
    await page.selectOption('#mpCapa', 'basicos');
    await page.click('#mpInfo button'); await page.waitForTimeout(300);
    ok(vp.name + ': Mapa: «Ver ficha del país» abre la ficha del país tocado', await page.isVisible('#paises') && (await page.inputValue('#pSel')) === 'ESP');
    // T86 (caso Colombia, 11-11-2026): el panel del mapa resume el país en TODAS las capas, igual para los 196, y se conecta con la ficha y con la capa de cada cosa
    await page.evaluate(() => showPage('mapa')); await page.waitForSelector('#mpSvg path.mp-p');
    const r86 = await page.evaluate(async () => { await Promise.all([cargarCon(), cargarCom(), cargarEpu()]); const malos = []; for (const p of PAISES) { mpElegir(p.id); const li = [...document.querySelectorAll('#mpInfo li[data-capa]')]; if (li.length !== 7 || li.some(x => /Cargando|undefined|NaN/.test(x.textContent))) malos.push(p.id); } mpElegir('COL'); return { malos, col: document.getElementById('mpInfo').innerText }; });
    ok(vp.name + ': T86 Mapa: el panel de cada país trae las 7 capas, ninguna en blanco ni «Cargando»' + (r86.malos.length ? ' → ' + r86.malos.slice(0, 8).join(' ') : ''), !r86.malos.length);
    ok(vp.name + ': T86 Mapa: Colombia muestra a la vez conflicto, comunicaciones y EPU, y dice por qué no hay mandato propio', /Conflictos armados estatales en 2025: 1/.test(r86.col) && /: 40/.test(r86.col) && /ciclo 4 del EPU \(2023\): 231/.test(r86.col) && /Solo algunos países tienen un mandato de relator propio/.test(r86.col));
    await page.click('#mpInfo li[data-capa="epu"] a'); await page.waitForFunction(() => { const h = document.getElementById('ps-epu'); return h && h.getBoundingClientRect().top < innerHeight; }, null, { timeout: 5000 }).catch(() => {});
    ok(vp.name + ': T86 Mapa: «Ver en la ficha» abre la ficha del país en su sección del EPU', await page.isVisible('#paises') && (await page.inputValue('#pSel')) === 'COL' && await page.evaluate(() => { const h = document.getElementById('ps-epu'); return !!h && h.getBoundingClientRect().top < innerHeight; }));
    await page.click('#pNav button:has-text("Ver en el mapa")'); await page.waitForTimeout(300);
    ok(vp.name + ': T86 Mapa: «Ver en el mapa» de la ficha vuelve al mapa con ese país elegido', await page.isVisible('#mapa') && (await page.evaluate(() => mpSel)) === 'COL');
    await page.evaluate(() => showPage('paises'));
    await page.evaluate(() => showPage('sistema')); await page.click('.org-node:has-text("Examen Periódico")');
    ok(vp.name + ': Cómo funciona la ONU: al pulsar un recuadro aparece su detalle y de quién depende', /Examen Periódico Universal/.test(await page.textContent('#sisDetalle')) && /Depende de/.test(await page.textContent('#sisDetalle')));
    await page.click('#sisT3'); await page.fill('#sisSim', 'CCPR/C/IND/CO/4');
    ok(vp.name + ': Cómo funciona la ONU: el descifrador explica un símbolo', /Observaciones finales/.test(await page.textContent('#sisSimOut')));
    await page.evaluate(() => showPage('sistema')); await page.click('#sisT4'); await page.click('.org-node:has-text("ONU Mujeres")');
    ok(vp.name + ': Familia de la ONU: ONU Mujeres aclara que no es el comité de la CEDAW y enlaza con él', /No es el comité de la CEDAW/.test(await page.textContent('#sisDetalle')) && (await page.locator('#sisDetalle button:has-text("CEDAW")').count()) > 0);
    await page.click('#sisT1'); await page.click('.org-node:has-text("Secretaría")');
    ok(vp.name + ': Mapa: la Secretaría muestra ACNUDH, OCHA y UNODC', /ACNUDH/.test(await page.textContent('#sisDetalle')) && /UNODC/.test(await page.textContent('#sisDetalle')));
    await page.evaluate(() => showPage('tratados')); await page.click('#trSel .org-node:has-text("CEDAW")'); await page.click('button:has-text("Texto del tratado")'); await page.waitForSelector('#trTexto .detail');
    ok(vp.name + ': Tratados: CEDAW art. 1 literal con buscador', /exclusión o restricción basada en el sexo/.test(await page.textContent('#trTexto')));
    await page.fill('#trBus', 'estereotipadas'); ok(vp.name + ': Tratados: el buscador del texto resalta coincidencias', (await page.locator('#trTexto mark').count()) > 0 || /artículo\(s\) contienen/.test(await page.textContent('#trTexto')));
    await page.click('button:has-text("Observaciones generales")'); await page.waitForSelector('#trJur table');
    ok(vp.name + ': Tratados: CEDAW lista recomendaciones generales con enlace oficial y aviso de cobertura parcial', (await page.locator('#trJur tbody tr').count()) >= 10 && (await page.locator('#trJur a[href^="https://digitallibrary.un.org/record/"]').count()) >= 10 && /Cobertura parcial/.test(await page.textContent('#trJur')));
    await page.click('button:has-text("Estados parte y ratificaciones")');
    ok(vp.name + ': Tratados: lista de Estados parte con país clicable', /Son parte/.test(await page.textContent('#trDetalle')) && (await page.locator('#trDetalle button.trat').count()) > 150);
    await page.locator('#trDetalle button.trat:has-text("India")').first().click(); await page.waitForTimeout(300);
    ok(vp.name + ': Tratados → ficha del país (India)', /India/.test(await page.textContent('#pOut')));
    await page.evaluate(() => showPage('siglas')); await page.fill('#sigQ', 'cat');
    ok(vp.name + ': Siglas: «cat» da inglés y español', /Committee against Torture/.test(await page.textContent('#sigOut')) && /Comité contra la Tortura/.test(await page.textContent('#sigOut')));
    await page.fill('#sigQ', 'cedaw'); await page.locator('#sigOut button:has-text("Ver tratado y comité")').first().click();
    ok(vp.name + ': Siglas → tratado: CEDAW abre el módulo de tratados', /Comité para la Eliminación de la Discriminación contra la Mujer/.test(await page.textContent('#trDetalle')));
    await page.evaluate(() => showPage('siglas')); await page.fill('#sigQ', 'A/HRC/RES/54/6');
    ok(vp.name + ': Siglas: un símbolo documental se descifra', /Este parece un símbolo/.test(await page.textContent('#sigOut')));
    // T73 (#198): «Cómo leer un código de la ONU»: cuatro formas de ver lo mismo
    await page.evaluate(() => showPage('codigos'));
    ok(vp.name + ': Códigos: el tutorial trae los 9 pasos', (await page.locator('#codTut .panel').count()) === 9 && /Primer segmento/.test(await page.textContent('#codTut')));
    await page.click('#codB_despiezador'); await page.fill('#codQ', 'A/HRC/RES/5/2');
    ok(vp.name + ': Códigos: despieza A/HRC/RES/5/2 (Consejo, resolución, sesión 5)', /Consejo de Derechos Humanos/.test(await page.textContent('#codDespOut')) && /Resolución/.test(await page.textContent('#codDespOut')) && /Sesión n\.º 5/.test(await page.textContent('#codDespOut')));
    for (const [c, re] of [['S/RES/1325 (2000)', /Consejo de Seguridad[^]*Número de la resolución/], ['A/RES/3314 (XXIX)', /septiembre de 1974/], ['CCPR/C/IND/CO/4', /India[^]*Observaciones finales/], ['CCPR/C/110/D/1234/2003', /comunicación/], ['A/HRC/34/51/Add.1', /visita a un país/], ['A/CONF.157/23', /Viena/], ['E/CN.4/2005/12', /antigua Comisión de Derechos Humanos/]]) {
      await page.fill('#codQ', c); ok(vp.name + ': Códigos: despieza ' + c, re.test(await page.textContent('#codDespOut'))); }
    await page.fill('#codQ', 'XYZ/1/2'); ok(vp.name + ': Códigos: un código desconocido no rompe y lo dice', /No lo reconozco/.test(await page.textContent('#codDespOut')));
    await page.click('#codB_tabla');
    const filas = await page.locator('#codTabOut tbody tr').count();
    await page.fill('#codFiltro', 'acta');
    const filas2 = await page.locator('#codTabOut tbody tr').count();
    ok(vp.name + ': Códigos: la tabla de referencia (' + filas + ' filas) se filtra (' + filas2 + ')', filas > 40 && filas2 > 1 && filas2 < filas);
    await page.fill('#codFiltro', ''); await page.locator('#codTabOut button.btn').first().click();
    ok(vp.name + ': Códigos: un ejemplo de la tabla pasa al despiezador', await page.isVisible('#codP_despiezador') && (await page.inputValue('#codQ')).length > 3);
    await page.click('#codB_repaso'); await page.click('#codRepOut button:has-text("Ver cómo se lee")');
    ok(vp.name + ': Códigos: el repaso enseña la lectura', /En una línea/.test(await page.textContent('#codRepOut')));
    await page.evaluate(() => showPage('siglas')); await page.fill('#sigQ', 'A/HRC/RES/54/6'); await page.click('#sigOut button:has-text("Aprender a leer cualquier código")');
    ok(vp.name + ': Siglas → Códigos: el descifrador lleva al tutorial con el código puesto', await page.isVisible('#codigos') && (await page.inputValue('#codQ')) === 'A/HRC/RES/54/6');
    await page.evaluate(() => showPage('fuentes'));
    ok(vp.name + ': Créditos visibles: los datos son de la ONU', /Créditos: de quién son los datos/.test(await page.textContent('#fuentes')) && /Naciones Unidas/.test(await page.textContent('#fuentes')));
    await page.evaluate(() => showPage('paises'));
    ok(vp.name + ': ficha de India carga bajo demanda sus observaciones finales, EPU y misiones', /CCPR\/C\/IND\/CO\/4/.test(dd) && /A\/HRC\/WG\.6\/41\/IND\/1/.test(dd) && /A\/HRC\/34\/51\/Add\.1/.test(dd));
    await page.fill('#pQ', 'siria'); await page.waitForTimeout(250);
    ok(vp.name + ': buscar «siria» muestra mandato y comisión', /Siria/.test(await page.textContent('#pBody')) && /S-17\/1/.test(await page.textContent('#pBody')) && (await page.locator('#pBody tr').count()) === 1);
    await page.fill('#pQ', ''); await page.selectOption('#pSel', 'COL'); await page.waitForTimeout(250);
    ok(vp.name + ': elegir Colombia lista 6 titulares y el aviso de independencia', (await page.locator('#pExtra .kv a').count()) === 6 && /no representan a su Estado/.test(await page.textContent('#pExtra')));
    if (vp.name === 'escritorio') await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_paises.png') });
    // T91: en el celular la lista de mandatos (con sus subtemas) empieza plegada; se abre con un toque y sigue abierta al filtrar
    const plgTemas = page.locator('details[data-plg="ps-temas"]');
    ok(vp.name + ': T91 la lista de mandatos empieza ' + (vp.width <= 650 ? 'plegada' : 'abierta'), (await plgTemas.evaluate(d => d.open)) === (vp.width > 650));
    if (vp.width <= 650) { await page.click('details[data-plg="ps-temas"] > summary'); await page.waitForTimeout(150); }
    await page.getByRole('button', { name: /^Tortura, malos tratos y detención \(\d+\)/ }).click(); await page.waitForTimeout(250);
    ok(vp.name + ': T91 al filtrar por subtema la lista sigue abierta', await page.locator('details[data-plg="ps-temas"]').evaluate(d => d.open));
    ok(vp.name + ': subtema «Tortura…» → lista corta de mandatos temáticos aplicables', (await page.locator('#pTemasTabla tbody tr').count()) < 10 && /tortura/i.test(await page.textContent('#pTemasTabla')));
    await page.locator('#pTema').click(); await page.keyboard.type('agua', { delay: 40 }); await page.waitForTimeout(250);
    ok(vp.name + ': escribir un tema libre mantiene el foco del campo y filtra', (await page.evaluate(() => document.activeElement.id)) === 'pTema' && /agua/i.test(await page.textContent('#pTemasTabla')));
    await page.fill('#pTema', ''); await page.getByRole('button', { name: /^Todos \(44\)/ }).click(); await page.waitForTimeout(200);
    ok(vp.name + ': sin tema → los 44 mandatos temáticos aplicables', (await page.locator('#pTemasTabla tbody tr').count()) === 44);
    // T61: comparador de dos países (desde la ficha de Colombia)
    await page.getByRole('button', { name: 'Comparar con otro país' }).click(); await page.waitForTimeout(400);
    ok(vp.name + ': «Comparar con otro país» abre el comparador con Colombia y el foco en el segundo país', await page.evaluate(() => $('pComp').open && $('cmpA').value === 'COL' && document.activeElement.id === 'cmpB') && /Elige dos países/.test(await page.textContent('#cmpOut')));
    await page.selectOption('#cmpB', 'ESP'); await page.waitForTimeout(250);
    const cmpN = await page.locator('#cmpOut tbody tr').count(), cmpT = await page.textContent('#cmpOut');
    ok(vp.name + ': Colombia frente a España: tabla con los 18 tratados y los datos de ficha, cabeceras con los dos nombres', cmpN === 28 && /Colombia/.test(await page.textContent('#cmpOut thead')) && /España/.test(await page.textContent('#cmpOut thead')) && /CEDAW/.test(cmpT) && /Invitación permanente/.test(cmpT) && /Fuentes:/.test(cmpT));
    const nDif = await page.locator('#cmpOut tbody tr.cmp-dif').count();
    await page.click('#cmpDif'); await page.waitForTimeout(200);
    ok(vp.name + ': «Solo lo que cambia» deja solo las filas distintas y lo marca pulsado', nDif > 0 && nDif < cmpN && (await page.locator('#cmpOut tbody tr').count()) === nDif && (await page.getAttribute('#cmpDif', 'aria-pressed')) === 'true' && new RegExp(nDif + ' de 28 aspectos cambian').test(await page.textContent('#cmpOut')));
    // P8: el comparador usa el componente de varios países (docs/DISENO.md): cada fila lleva su aspecto como cabecera fija
    // y, con dos países, la tabla cabe entera también en el celular (antes cada fila era una tarjeta de tres casillas).
    ok(vp.name + ': el comparador no desborda la pantalla; el aspecto es la cabecera fija de cada fila y con dos países cabe sin deslizar', await page.evaluate(n => { const c = document.querySelector('#cmpOut .cmpx'); return document.documentElement.scrollWidth <= innerWidth + 1 && c && c.classList.contains('cmpx-pocas') && c.scrollWidth <= c.clientWidth + 2 && document.querySelectorAll('#cmpOut tbody th.cmpx-fija[scope=row]').length === n && getComputedStyle(document.querySelector('#cmpOut tbody th')).position === 'sticky'; }, nDif));
    await page.click('#cmpDif'); await page.selectOption('#cmpB', 'COL'); await page.waitForTimeout(150);
    ok(vp.name + ': elegir el mismo país dos veces pide dos distintos', /dos países distintos/.test(await page.textContent('#cmpOut')));
    await page.evaluate(() => { $('pComp').open = false; });
    await page.evaluate(() => showPage('inicio')); await page.selectOption('#guiadaSel', { index: 4 }); await page.selectOption('#guiadaPais', 'COL'); await page.getByRole('button', { name: 'Ver mandatos' }).click(); await page.waitForTimeout(300);
    ok(vp.name + ': búsqueda guiada con país (Colombia + agua/alimentación…) abre Países con mandatos aplicables', await page.isVisible('#paises') && /Colombia/.test(await page.textContent('#pOut')) && (await page.locator('#pTemasTabla tbody tr').count()) > 0);
    if (vp.name === 'escritorio') { await page.evaluate(() => document.getElementById('pOut').scrollIntoView()); await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_pais_temas.png') }); }
    await page.evaluate(() => showPage('explorar')); await page.selectOption('#modal', 'País'); if (!(await page.evaluate(() => document.getElementById('masFiltros').open))) await page.click('#masFiltros summary'); await page.selectOption('#pais', 'COL'); await page.waitForTimeout(250);
    ok(vp.name + ': Explorador País+Colombia explica la ausencia (no una pantalla en blanco)', /no tiene mandato por país vigente/.test(await page.textContent('#count')) && /Países/.test(await page.textContent('#count')));
    await page.evaluate(() => clearFilters());
    await page.evaluate(() => showPage('inicio')); await page.fill('#quick', 'xqzvbn'); await page.waitForTimeout(500);
    const href = await page.locator('#smartOut a', { hasText: 'Solicitar verificación' }).getAttribute('href');
    ok(vp.name + ': búsqueda sin resultado ofrece solicitud prellenada en GitHub', /issues\/new\?template=solicitud-verificacion\.yml/.test(href) && /busqueda=xqzvbn/.test(href));
    await page.evaluate(() => showPage('explorar')); if (!(await page.evaluate(() => document.getElementById('masFiltros').open))) await page.click('#masFiltros summary'); await page.selectOption('#pais', 'BLR'); await page.waitForTimeout(250);
    ok(vp.name + ': filtro de país en el explorador (Belarús → 1 mandato)', (await page.locator('#mandBody tr').count()) === 1);
    await page.evaluate(() => clearFilters());
    await page.evaluate(() => showPage('inicio')); await page.fill('#quick', 'Camboya'); await page.waitForTimeout(500);
    await page.locator('#smartOut button', { hasText: 'Ver país' }).first().click();
    ok(vp.name + ': la búsqueda inteligente lleva a la sección del país', await page.isVisible('#paises') && /Camboya/.test(await page.textContent('#pOut')));
    for (const id of ['inicio', 'explorar', 'paises', 'sistema', 'arqueologia', 'recuperar', 'mecanismos', 'codificacion', 'seleccion', 'auditoria', 'fuentes']) {
      await page.evaluate(i => showPage(i), id);
      ok(vp.name + ': «Para qué sirve» visible en ' + id, (await page.isVisible('#' + id + ' .about') || await page.isVisible('#' + id + ' .ay-chip.ay-about')) && /Para qué sirve esta pantalla/.test(await page.textContent('#' + id + ' .about')));
    }
    await page.evaluate(() => showPage('arqueologia')); await page.fill('#qt', 'agua'); await page.waitForTimeout(250);
    ok(vp.name + ': Arqueología lista actos reales del agua (A/HRC/RES/60/9)', /A\/HRC\/RES\/60\/9/.test(await page.textContent('#traceBody')));
    await page.fill('#qt', '');
    await page.evaluate(() => showPage('inicio')); await page.waitForTimeout(1200);
    const nov = await page.textContent('#novedades');
    if (vp.name === 'escritorio') ok('escritorio: no aparece la barra móvil ni el botón de menú', !(await page.isVisible('#burger')) && !(await page.isVisible('#appbar')));
    ok(vp.name + ': panel de novedades (' + (URL.startsWith('http') ? 'en línea: última revisión' : 'sin conexión: aviso') + ')', URL.startsWith('http') ? /Última revisión/.test(nov) : /sin conexión/.test(nov));
    await page.evaluate(() => showPage('datoscalidad')); ok(vp.name + ': «Novedades detectadas» llega plegada y se abre al tocar', !(await page.locator('#novedadesBox').evaluate(e => e.open)) && !(await page.isVisible('#novedades')) && (await page.click('#novedadesBox>summary'), await page.isVisible('#novedades')));
    const sinHueco = await page.evaluate(() => { const k = [...document.querySelectorAll('#inicio>.panel')].filter(e => e.offsetHeight); return k.every((e, i) => { if (!i) return true; const p = k[i - 1]; return e.getBoundingClientRect().top - p.getBoundingClientRect().bottom >= 10 || p.nextElementSibling !== e; }); });
    ok(vp.name + ': las cajas de la portada no van pegadas unas a otras', sinHueco);
    // #199: en TODAS las pantallas, dos cajas (borde o fondo) una encima de otra o una junto a otra deben dejar al menos 8 px
    const secciones = await page.evaluate(() => [...document.querySelectorAll('section.section')].map(s => s.id));
    const pegadas = [];
    for (const id of secciones) {
      await page.evaluate(i => showPage(i), id); await page.waitForTimeout(120);
      const malas = await page.evaluate(sid => { const out = [], s = document.getElementById(sid); if (!s || s.offsetParent === null) return out;
        const caja = e => { const c = getComputedStyle(e); return (c.borderTopWidth !== '0px' && c.borderTopStyle !== 'none') || (c.backgroundColor !== 'rgba(0, 0, 0, 0)' && e.getBoundingClientRect().height > 30); };
        const fila = /^(TH|TD|TR|BUTTON|A|SPAN|OPTION)$/;
        s.querySelectorAll('*').forEach(e => { const n = e.nextElementSibling; if (!n || fila.test(e.tagName) || fila.test(n.tagName) || /\b(kv|btn|chip|tag)\b/.test(e.className + ' ' + n.className) || !caja(e) || !caja(n)) return;
          const a = e.getBoundingClientRect(), c = n.getBoundingClientRect(); if (a.height < 20 || c.height < 20 || a.width < 50) return;
          const dy = c.top - a.bottom, dx = c.left - a.right;
          if ((Math.abs(a.left - c.left) < 4 && dy < 8 && dy > -1) || (Math.abs(a.top - c.top) < 4 && dx < 8 && dx > -1 && dx < c.width)) out.push(sid + ': ' + e.tagName + '.' + e.className + ' → ' + n.tagName + '.' + n.className); });
        return out; }, id);
      pegadas.push(...malas);
    }
    ok(vp.name + ': en ninguna pantalla hay cajas pegadas (' + secciones.length + ' revisadas)' + (pegadas.length ? ' — ' + [...new Set(pegadas)].slice(0, 5).join(' | ') : ''), pegadas.length === 0);
    await page.evaluate(() => showPage('inicio'));
    ok(vp.name + ': últimas resoluciones visibles', (await page.locator('#recientes .listline').count()) === 8);
    await page.evaluate(() => showPage('paises')); await page.evaluate(() => window.scrollTo(0, 1500));
    await page.evaluate(() => showPage('seleccion')); await page.waitForTimeout(150);
    ok(vp.name + ': tras ir de Países (lista larga) a Selección, solo se ve Selección y el scroll vuelve arriba', (await page.evaluate(() => [...document.querySelectorAll('.section')].filter(s => getComputedStyle(s).display !== 'none').map(s => s.id).join())) === 'seleccion' && (await page.evaluate(() => window.scrollY)) === 0 && !/Etapa \d: \d/.test(await page.textContent('#selectionList')));
    await page.evaluate(() => showPage('mecanismos'));
    const pMec = await page.evaluate(() => paso('mec'));
    ok(vp.name + ': otros mecanismos: ' + pMec + ' filas y «' + pMec + ' de 33»', (await page.locator('#mecBody tr:not(.mas)').count()) === pMec && new RegExp(pMec + ' de 33').test(await page.textContent('#mecBody tr.mas')) && /CERD/.test(await page.textContent('#mecBody')));
    while (await page.locator('#mecBody tr.mas button').count()) await page.locator('#mecBody tr.mas button').click();
    ok(vp.name + ': otros mecanismos (CERD…CED) visibles', (await page.locator('#mecBody tr').count()) === 33 && /CERD/.test(await page.textContent('#mecBody')));
    await page.evaluate(() => showPage('recuperar'));
    await page.getByRole('button', { name: /caso real de 1980/i }).click();
    const rr = await page.textContent('#recoverResult');
    ok(vp.name + ': clic «caso real de 1980» → E/1980/13 pp. 180–181', rr.includes('E/1980/13') && rr.includes('180–181'));
    await page.fill('#recoverQuery', 'A/HRC/51/L.40'); await page.getByRole('button', { name: /Reconstruir ruta/i }).click();
    ok(vp.name + ': borrador L.40 → A/HRC/RES/51/19', (await page.textContent('#recoverResult')).includes('A/HRC/RES/51/19'));
    ok(vp.name + ': enlaces externos con rel=noopener', await page.evaluate(() => [...document.querySelectorAll('a[target=_blank]')].every(a => /noopener/.test(a.rel))));
    if (vp.name === 'escritorio') { await page.evaluate(() => showPage('explorar')); await page.fill('#q', 'agua'); await page.evaluate(() => filterMandates()); await page.locator('#mandBody button').first().click(); await page.waitForTimeout(400); await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_escritorio.png') }); }
    else await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_movil.png') });
    await page.close();
  }
  {
    // Escenario: la descarga de datos falla → debe verse un aviso útil, no una pantalla en blanco
    const ctx2 = await browser.newContext(); const pg = await ctx2.newPage();
    await pg.route(/atlas-data\.js/, r => r.abort());
    await pg.goto(URL); await pg.waitForTimeout(500);
    ok('fallo de datos: se muestra el aviso con instrucciones al instante', await pg.isVisible('#aviso-carga') && /Ctrl \+ F5/.test(await pg.textContent('#aviso-carga')) && /ZIP del repositorio/.test(await pg.textContent('#aviso-carga')));
    ok('fallo de datos: el detalle técnico indica qué falló', /no se pudo descargar|Sin datos/.test(await pg.textContent('#aviso-detalle') + (await pg.evaluate(() => String(window.__datosFallo)))));
    // Escenario normal: el aviso no estorba y la app queda marcada como lista
    const pg2 = await ctx2.newPage(); await pg2.goto(URL); await pg2.waitForTimeout(500);
    ok('carga normal: aviso oculto y aplicación lista', !(await pg2.isVisible('#aviso-carga')) && (await pg2.evaluate(() => window.__atlasListo === true)));
    // T58: el índice de actos llega aparte (atlas-actos.js). Si falla, la página arranca igual y lo dice
    const pg3 = await ctx2.newPage(); await pg3.route(/atlas-actos\.js/, r => r.abort());
    await pg3.goto(URL); await pg3.waitForFunction(() => window.__atlasListo, null, { timeout: 5000 });
    ok('sin atlas-actos.js: la página arranca y avisa en «recientes»', /No se pudo descargar el índice/.test(await pg3.textContent('#recientes')) && await pg3.evaluate(() => DATA.mandatos.length > 0));
    // Con el índice lento: una búsqueda por símbolo espera y se resuelve al llegar
    const pg4 = await ctx2.newPage(); await pg4.route(/atlas-actos\.js/, async r => { await new Promise(f => setTimeout(f, 1500)); r.continue(); });
    await pg4.goto(URL, { waitUntil: 'domcontentloaded' }); await pg4.waitForFunction(() => typeof smartRun === 'function' && window.__actosListo);
    await pg4.evaluate(() => { document.getElementById('quick').value = 'A/HRC/RES/51/19'; smartRun(); });
    ok('índice lento: la búsqueda muestra «Cargando el índice»', /Cargando el índice/.test(await pg4.textContent('#smartOut')));
    await pg4.waitForFunction(() => window.__atlasListo, null, { timeout: 8000 });
    ok('índice lento: al llegar, la búsqueda pendiente se resuelve sola', /A\/HRC\/RES\/51\/19/.test(await pg4.textContent('#smartOut')) && !/Cargando el índice/.test(await pg4.textContent('#smartOut')));
    ok('con índice: «recientes» lista resoluciones', (await pg4.locator('#recientes .listline').count()) > 0);
    await ctx2.close();
  }
  // Portada e historia
  {
    const pg = await browser.newPage({ viewport: { width: 1366, height: 900 } }); await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo);
    ok('portada: buscador, ocho caminos y «un día como hoy» a la vista', (await pg.isVisible('#quick')) && (await pg.locator('.tile').count()) === 8 && /en la (historia de la )?ONU/.test(await pg.textContent('#hoyHistoria')));
    ok('portada despejada (T80): sin cifras ni novedades, y DIGNITYOS en una franja al final', await pg.evaluate(() => { const i = document.getElementById('inicio'), f = i.querySelector('.franja-dig'), g = document.getElementById('guiada'); return !i.querySelector('details.datos, #kpis, #novedades') && !!f && !!g && (g.compareDocumentPosition(f) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0 && i.lastElementChild === f; }));
    ok('«Datos y calidad» (T80): reúne cifras, calidad, últimas resoluciones y modalidades, con las novedades plegadas', await pg.evaluate(() => { showPage('datoscalidad'); const d = document.getElementById('datoscalidad'); const ok = !!d.querySelector('#kpis') && !!d.querySelector('#calidad') && !!d.querySelector('#recientes') && !!d.querySelector('#chartKinds') && !d.querySelector('#novedadesBox').open && !!document.querySelector('#nav button[data-page="datoscalidad"][aria-current]'); showPage('inicio'); return ok; }));
    await pg.click('.tile:has-text("Su historia")'); await pg.waitForSelector('.hi-card');
    ok('historia: se ven las tarjetas de la línea de tiempo y el detalle', (await pg.locator('.hi-card').count()) >= 50 && /Por qué importa/.test(await pg.textContent('#hiDetalle')));
    await pg.click('.hi-card:has-text("Declaración Universal")');
    ok('historia: al tocar un hecho se muestra su detalle (DUDH, 10 de diciembre de 1948)', /10 de diciembre de 1948/.test(await pg.textContent('#hiDetalle')) && /217 A/.test(await pg.textContent('#hiDetalle')));
    await pg.fill('#hiSlider', '1993'); await pg.waitForTimeout(250);
    ok('historia: el control del año salta al hecho más cercano y muestra mandatos creados ese año', /199[3-4]/.test(await pg.textContent('#hiDetalle')) && /Mandatos vigentes creados en 1993/.test(await pg.textContent('#hiDetalle')));
    await pg.click('button:has-text("Fundación y descolonización")');
    ok('historia: el filtro por época oculta lo posterior', (await pg.locator('.hi-card').count()) < 30 && !(await pg.textContent('#hiTrack')).includes('Agenda 2030'));
    await pg.click('button:has-text("Toda la historia")'); await pg.click('#hiPlay'); await pg.waitForTimeout(6600);
    ok('historia: el recorrido guiado avanza solo y se puede pausar', /Pausar/.test(await pg.textContent('#hiPlay')) && (await pg.evaluate(() => hiSelI)) !== 0);
    await pg.click('#hiPlay'); ok('historia: pausar detiene el recorrido', /Recorrido guiado/.test(await pg.textContent('#hiPlay')));
    await pg.click('.hi-card:has-text("Convención contra la Tortura")'); await pg.click('#hiDetalle button:has-text("Ver en el tablero")');
    ok('historia → tratado: el botón abre el tratado correspondiente (CAT)', /Comité contra la Tortura/.test(await pg.textContent('#trDetalle')));
    await pg.close();
  }
  // Exactitud de números y sugerencias
  {
    const pg = await browser.newPage({ viewport: { width: 1366, height: 900 } }); await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo);
    await pg.evaluate(() => showPage('auditoria'));
    ok('exactitud: el panel muestra cuántos números son exactos y cuáles se corrigieron, con los dos números', /Números exactos/.test(await pg.textContent('#numAudit')) && /A\/HRC\/36\/L\.16/.test(await pg.textContent('#numAudit')) && /A\/HRC\/RES\/36\/23/.test(await pg.textContent('#numAudit')));
    await pg.click('#numAudit button:has-text("Por mandato")');
    ok('exactitud: la vista por mandato lista los mandatos con dudas', (await pg.locator('#numAudit tbody tr').count()) >= 30);
    await pg.evaluate(() => showPage('recuperar')); await pg.fill('#recoverQuery', 'A/HRC/RES/36/24'); await pg.evaluate(() => recoverDocument());
    ok('recuperar: un número equivocado propone el parecido con su título', /¿Quisiste decir…\?/.test(await pg.textContent('#recoverResult')) && /A\/HRC\/RES\/36\/23/.test(await pg.textContent('#recoverResult')));
    await pg.close();
  }
  // P6: «Qué falta y qué viene» pagina cada bloque por su cuenta (los 4 títulos salen siempre); el menú abierto no deja la página inerte al pasar de 1080 px
  for (const [nom, vp, extra] of [['escritorio', { width: 1440, height: 900 }, {}], ['celular', { width: 390, height: 844 }, { hasTouch: true, isMobile: true }]]) {
    const pg = await browser.newPage({ viewport: vp, ...extra }); await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo);
    await pg.evaluate(() => showPage('hojaruta'));
    const hr = await pg.evaluate(() => { const o = document.getElementById('hojaOut'); return { h3: [...o.querySelectorAll('h3')].filter(h => h.offsetParent).length, pend: [...o.querySelectorAll('.hr-est')].filter(e => /Pendiente/.test(e.textContent)).length, botones: o.querySelectorAll('.mas button').length }; });
    ok('P6 ' + nom + ': «Qué falta» con «Todos» enseña los 4 bloques y ya hay pendientes a la vista, cada bloque con su «Mostrar más»', hr.h3 === 4 && hr.pend > 0 && hr.botones >= 1, hr);
    await pg.close();
  }
  {
    const pg = await browser.newPage({ viewport: { width: 820, height: 1180 }, hasTouch: true }); await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo);
    await pg.click('#burger'); await pg.waitForTimeout(300);
    const antes = await pg.evaluate(() => document.getElementById('contenido').inert);
    await pg.setViewportSize({ width: 1180, height: 820 }); await pg.waitForTimeout(300);
    const r = await pg.evaluate(() => ({ cont: document.getElementById('contenido').inert, barra: document.getElementById('bnav').inert }));
    let clic = true; try { await pg.click('#quick', { timeout: 3000 }); } catch (e) { clic = false; }
    ok('P6 tableta: con el menú abierto y la pantalla girada a más de 1080 px, el contenido deja de estar inerte y se puede tocar', antes === true && !r.cont && !r.barra && clic, { antes, ...r, clic });
    await pg.close();
  }
  // Navegación móvil: menú lateral con botón, se cierra al navegar; sin desbordes en ningún tamaño de teléfono/tableta
  for (const [nom, w, h] of [['Android 320', 320, 658], ['iPhone SE', 375, 667], ['Android 412', 412, 915], ['tableta 768', 768, 1024]]) {
    const pg = await browser.newPage({ viewport: { width: w, height: h }, hasTouch: true, isMobile: true }); await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo);
    ok(nom + ': hay barra superior con botón de menú y el menú está cerrado', (await pg.isVisible('#burger')) && !(await pg.isVisible('#side')));
    ok(nom + ': se ve la etiqueta «Menú» y la barra inferior con sus 5 accesos (ya no hay pista de las tres líneas)', (await pg.isVisible('.burger-t')) && (await pg.isVisible('#bnav')) && (await pg.locator('#bnav button').count()) === 5 && !(await pg.$('#menuHint')));
    { const bn = await pg.evaluate(() => { const r = document.getElementById('bnav').getBoundingClientRect(), bs = [...document.querySelectorAll('#bnav button')].map(b => b.getBoundingClientRect()); return { alto: r.height, abajo: Math.round(r.bottom), H: innerHeight, minimo: Math.min(...bs.map(b => Math.min(b.width, b.height))), libre: parseFloat(getComputedStyle(document.body).paddingBottom) }; });
      ok(nom + ': P6 la barra inferior mide 56–64 px, va pegada abajo, sus botones miden 44 px o más y la página deja su alto libre', bn.alto >= 56 && bn.alto <= 64 && bn.abajo === bn.H && bn.minimo >= 44 && bn.libre >= bn.alto, bn); }
    await pg.tap('#burger'); await pg.waitForTimeout(350);
    ok(nom + ': el botón abre el menú', (await pg.isVisible('#side')) && (await pg.getAttribute('#burger', 'aria-expanded')) === 'true');
    // T28: con el menú abierto, deslizar el dedo mueve el menú (hasta su último elemento) y no la página de atrás; al cerrar, la página vuelve a donde estaba
    { const cdp = await pg.context().newCDPSession(pg);
      const desliza = async (x, y0, y1) => { await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y: y0 }] }); for (let i = 1; i <= 12; i++) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y: y0 + (y1 - y0) * i / 12 }] }); await pg.waitForTimeout(16); } await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await pg.waitForTimeout(300); };
      await pg.evaluate(() => { menu(false); scrollTo({ top: 120, behavior: 'instant' }); }); await pg.waitForTimeout(150);
      await pg.evaluate(() => menu(true)); await pg.waitForTimeout(350);
      for (let i = 0; i < 4; i++) await desliza(Math.min(150, w / 3), h - 80, 80);
      const e = await pg.evaluate(() => { const s = document.getElementById('side'); return { fin: s.scrollTop + s.clientHeight >= s.scrollHeight - 2, fondo: Math.round(scrollY), fijo: getComputedStyle(document.body).position }; });
      ok(nom + ': el menú abierto se desliza hasta el final y el fondo no se mueve', e.fin && e.fondo === 0 && e.fijo === 'fixed');
      await pg.evaluate(() => { document.getElementById('side').scrollTop = 0; }); await desliza(w - 20, h - 80, 160);
      ok(nom + ': arrastrar desde fuera del menú (el velo) también mueve el menú', (await pg.evaluate(() => document.getElementById('side').scrollTop)) > 100);
      await pg.evaluate(() => { document.getElementById('side').scrollTop = 0; }); await desliza(Math.min(120, w / 4), h - 120, 120);
      ok(nom + ': arrastrar sobre los botones del menú lo mueve', (await pg.evaluate(() => document.getElementById('side').scrollTop)) > 100);
      await pg.evaluate(() => menu(false)); await pg.waitForTimeout(250);
      ok(nom + ': al cerrar el menú la página vuelve a su posición', (await pg.evaluate(() => Math.round(scrollY))) === 120);
      await pg.evaluate(() => { scrollTo({ top: 0, behavior: 'instant' }); menu(true); }); await pg.waitForTimeout(350); }
    await pg.tap('.nav button[data-page="tratados"]'); await pg.waitForTimeout(350);
    ok(nom + ': al elegir una pantalla se cierra el menú y se muestra', !(await pg.isVisible('#side')) && (await pg.isVisible('#tratados')));
    const malos = []; for (const id of ['inicio', 'explorar', 'sistema', 'paises', 'tratados', 'siglas', 'codigos', 'arqueologia', 'recuperar', 'mecanismos', 'codificacion', 'seleccion', 'auditoria', 'fuentes']) { await pg.evaluate(x => showPage(x), id); const d = await pg.evaluate(() => [document.documentElement.scrollWidth, innerWidth]); if (d[0] > d[1] + 1) malos.push(id); }
    ok(nom + ': ninguna pantalla se desborda en horizontal ' + malos.join(','), malos.length === 0);
    const peq = await pg.evaluate(() => [...document.querySelectorAll('input.field')].filter(e => e.offsetParent && parseFloat(getComputedStyle(e).fontSize) < 16).length);
    ok(nom + ': los campos de texto usan 16 px (iOS no hace zoom al escribir)', peq === 0);
    // Si algo es más ancho que la pantalla, el móvil encoge la página entera y los toques caen en otro botón (pasó con «Invitación permanente…» a 320 px)
    await pg.evaluate(() => showPage('paises')); await pg.fill('#pQ', 'Colombia'); await pg.getByRole('button', { name: 'Buscar' }).first().click(); await pg.waitForTimeout(400);
    ok(nom + ': con la ficha de Colombia abierta la página mide lo que la pantalla (el móvil no la encoge)', await pg.evaluate(W => innerWidth === W && document.documentElement.scrollWidth <= W, w));
    await pg.close();
  }
  // Contador de visitas: servido como https falso, con el servicio simulado y sin la marca de automatización
  {
    const fs = require('fs'), root = path.resolve(__dirname, '..');
    const mime = { '.html': 'text/html', '.js': 'application/javascript', '.json': 'application/json' };
    const ctx = await browser.newContext({ timezoneId: 'America/Bogota', locale: 'es-CO' }); const pv = await ctx.newPage();
    await pv.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => false }));
    const llamadas = [];
    await pv.route('https://sk-atlas.pig-mimosa.ts.net/**', r => { const u = new globalThis.URL(r.request().url()); llamadas.push(u.pathname + u.search); r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ total: 1234, pais: 1234 }) }); });
    await pv.route('https://atlas.test/**', r => { let p = new globalThis.URL(r.request().url()).pathname; if (p === '/') p = '/index.html'; const f = path.join(root, decodeURIComponent(p)); if (!f.startsWith(root) || !fs.existsSync(f)) return r.fulfill({ status: 404, body: '' }); r.fulfill({ status: 200, contentType: mime[path.extname(f)] || 'application/octet-stream', body: fs.readFileSync(f) }); });
    await pv.goto('https://atlas.test/'); await pv.waitForFunction(() => window.__atlasListo); await pv.waitForTimeout(1500);
    ok('visitas: la barra muestra el total, el país del visitante (Colombia) y sus visitas', (await pv.textContent('#visTotal')).replace(/\D/g, '') === '1234' && /Colombia/.test(await pv.textContent('#visPais')) && (await pv.textContent('#visPaisN')).replace(/\D/g, '') === '1234');
    ok('visitas: la barra no se queda pegada al desplazarse (estática arriba)', await pv.evaluate(() => getComputedStyle(document.getElementById('visBar')).position === 'static'));
    ok('visitas: la primera visita suma al total y al país; una recarga inmediata no vuelve a sumar', llamadas.filter(x => x.startsWith('/visita?')).length === 1 && llamadas.some(x => x === '/visita?pais=CO'));
    const antes = llamadas.filter(x => x.startsWith('/visita?')).length; await pv.reload(); await pv.waitForFunction(() => window.__atlasListo); await pv.waitForTimeout(800);
    ok('visitas: la recarga solo consulta (/visitas), no suma', llamadas.filter(x => x.startsWith('/visita?')).length === antes && llamadas.some(x => x.startsWith('/visitas?')));
    await pv.screenshot({ path: '/tmp/claude-0/visitas.png', clip: { x: 0, y: 0, width: 1280, height: 120 } }).catch(() => {});
    await ctx.close();
  }
  // Texto completo: la ruta /texto simulada con un párrafo; se resalta lo encontrado y no se inyecta HTML del fragmento
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } }); const pt = await ctx.newPage();
    const pedidas = [];
    await pt.route(/sk-atlas\.pig-mimosa\.ts\.net/, r => { const u = new globalThis.URL(r.request().url()); pedidas.push(u.pathname); const tx = u.pathname === '/texto'; if (u.pathname === '/preguntar') return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ pregunta: 'x', modelo: 'glm-5.3-flash', respuesta: 'Los Estados deben aceptar las visitas [1] y responder [9].\n- Invitar al relator [1] <img src=x onerror="window.__xss2=1">', citas: [1], motivo: '', parrafos: [{ simbolo: 'A/HRC/RES/16/16', lengua: 'es', parrafo: 7, fragmento: 'visitas', url: 'https://digitallibrary.un.org/record/1/files/x.pdf' }] }) }); r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(tx ? { consulta: 'visitas', total: 1, documentos: 377, resultados: [{ simbolo: 'A/HRC/RES/16/16', lengua: 'es', parrafo: 7, fragmento: 'responder a las solicitudes de \u0002visitas\u0003 <img src=x onerror="window.__xss=1"> a los países', url: 'https://digitallibrary.un.org/record/1/files/x.pdf' }, { simbolo: 'A/HRC/RES/15/22', lengua: 'en', parrafo: 9, fragmento: 'To conduct country visits', url: '', por_significado: true }, { simbolo: 'CAT/C/COL/CO/5', lengua: 'es', parrafo: 12, fragmento: 'El Comité \u0002visitas\u0003', url: '', tipo: 'Observaciones finales', titulo: 'Observaciones finales sobre el quinto informe periódico de Colombia', pais: 'COL', fecha: '2015-05-29' }], semantica: true } : { consulta: '', total: 0, resultados: [] }) }); });
    pt.on('pageerror', e => res.errors.push('texto: ' + e.message));
    await pt.goto(URL); await pt.waitForFunction(() => window.__atlasListo);
    await pt.fill('#quick', 'visitas'); await pt.waitForSelector('#textos h3', { timeout: 5000 }).catch(() => {});
    ok('texto: la búsqueda pide /texto y muestra «Dentro de los textos»', pedidas.includes('/texto') && /Dentro de los textos \(1\)/.test(await pt.textContent('#textos')) && /por significado/.test(await pt.textContent('#textos')) && /tratan de lo mismo/.test(await pt.textContent('#textos')));
    ok('texto: lo encontrado sale resaltado y el HTML del fragmento no se ejecuta', await pt.evaluate(() => document.querySelector('#textos mark')?.textContent === 'visitas' && !document.querySelector('#textos img') && !window.__xss));
    ok('texto: el resultado enlaza el PDF oficial y cabe en 390 px', await pt.evaluate(() => !!document.querySelector('#textos a[href$="x.pdf"]') && document.documentElement.scrollWidth <= 390));
    { const t = await pt.textContent('#textos'), bs = await pt.evaluate(() => [...document.querySelectorAll('#textos button')].map(b => b.textContent + '|' + b.getAttribute('onclick')));
      ok('texto: un documento de país muestra tipo y país', /Observaciones finales · Colombia/.test(t));
      ok('texto: un documento de país muestra su título', /quinto informe periódico/.test(t));
      ok('texto: un documento de país lleva a la ficha del país', bs.some(b => /Ver país\|irPais\('COL'\)/.test(b))); }
    await pt.evaluate(() => smartRun()); await pt.waitForTimeout(100);
    ok('texto: si la búsqueda se redibuja con la misma consulta, los párrafos se conservan sin volver a pedirlos', /Dentro de los textos/.test(await pt.textContent('#textos')) && pedidas.filter(x => x === '/texto').length === 1);
    await pt.fill('#quick', 'qué dicen sobre las visitas'); await pt.waitForSelector('.preg button', { timeout: 5000 }).catch(() => {});
    ok('preguntar: el botón aparece con aviso de que la pregunta va a un servicio externo, y nada se envía sin pulsarlo', /servicio de IA externo/.test(await pt.textContent('#textos')) && !pedidas.includes('/preguntar'));
    await pt.click('.preg button'); await pt.waitForSelector('#pregOut .ia', { timeout: 5000 }).catch(() => {});
    ok('preguntar: muestra la respuesta con la cita [1] enlazada a su documento y quita la cita inventada [9]', await pt.evaluate(() => { const o = document.getElementById('pregOut'); return !!o.querySelector('a.cita[href="#cita-1"]') && !/\[9\]/.test(o.textContent) && /A\/HRC\/RES\/16\/16/.test(o.querySelector('.citas').textContent) && !!o.querySelector('.ia li'); }));
    ok('preguntar: el HTML de la respuesta no se ejecuta y cabe en 390 px', await pt.evaluate(() => !document.querySelector('#pregOut img') && !window.__xss2 && document.documentElement.scrollWidth <= 390));
    await pt.fill('#quick', 'vi'); await pt.waitForTimeout(800);
    ok('texto: con menos de 3 letras no se pide /texto', pedidas.filter(x => x === '/texto').length === 2);
    await ctx.close();
  }
  { // P1 (plan de diseño, fase 0): aviso del menú una sola vez y solo en la portada; un solo selector de idioma en el celular; 44 px
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true }), pg = await ctx.newPage();
    await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo);
    // P6 (plan de diseño, fase 5): barra inferior en lugar del aviso del menú
    ok('P6 celular: «Inicio» de la barra inferior está marcado en la portada', (await pg.getAttribute('#bnav button[data-page="inicio"]', 'aria-current')) === 'page');
    await pg.tap('#bnav button[data-page="paises"]'); await pg.waitForTimeout(250);
    ok('P6 celular: «Países» de la barra inferior abre Países y queda marcado (y solo él)', (await pg.isVisible('#paises')) && (await pg.getAttribute('#bnav button[data-page="paises"]', 'aria-current')) === 'page' && (await pg.locator('#bnav [aria-current]').count()) === 1);
    await pg.tap('#bnav button[data-page="mapa"]'); await pg.waitForTimeout(400);
    ok('P6 celular: «Mapa» de la barra inferior abre el mapa', await pg.isVisible('#mapa'));
    await pg.tap('#bnav button[data-busca]'); await pg.waitForTimeout(300);
    ok('P6 celular: «Buscar» abre la portada con el cursor en la búsqueda inteligente', (await pg.isVisible('#inicio')) && await pg.evaluate(() => document.activeElement && document.activeElement.id === 'quick'));
    await pg.tap('#bnavMenu'); await pg.waitForTimeout(350);
    ok('P6 celular: «Menú» de la barra inferior abre el menú lateral y lo dice (aria-expanded)', (await pg.isVisible('#side')) && (await pg.getAttribute('#bnavMenu', 'aria-expanded')) === 'true' && (await pg.getAttribute('#burger', 'aria-expanded')) === 'true');
    await pg.evaluate(() => menu(false)); await pg.waitForTimeout(250);
    ok('P6 celular: al cerrar el menú la barra inferior lo refleja', (await pg.getAttribute('#bnavMenu', 'aria-expanded')) === 'false');
    await pg.focus('#bnavMenu'); await pg.keyboard.press('Enter'); await pg.waitForTimeout(350);
    { const dentro = await pg.evaluate(() => document.getElementById('side').contains(document.activeElement)); await pg.keyboard.press('Escape'); await pg.waitForTimeout(250);
      const foco = await pg.evaluate(() => document.activeElement && document.activeElement.id);
      ok('P6 celular: con teclado, «Menú» de la barra lleva el foco al menú y Escape lo devuelve a «Menú»', dentro && foco === 'bnavMenu', { dentro, foco }); }
    { const r = await pg.evaluate(() => { showPage('explorar'); const v = document.getElementById('visBar').getBoundingClientRect(), f = document.querySelector('#explorar .ayudas'), ch = [...f.querySelectorAll('.ay-chip')]; return { vis: Math.round(v.height), chips: ch.length, fila: new Set(ch.map(c => Math.round(c.getBoundingClientRect().top))).size, alto: Math.min(...ch.map(c => c.getBoundingClientRect().height)), cerradas: [...f.querySelectorAll('details')].every(d => !d.open && !d.offsetParent) }; });
      ok('P6 celular: el contador de visitas va en una sola línea (menos de 50 px)', r.vis < 50, r);
      ok('P6 celular: Explorar junta Lectura fácil, Para qué sirve e Instantánea en una fila de pastillas de 44 px, todas cerradas', r.chips === 3 && r.fila <= 2 && r.alto >= 44 && r.cerradas, r); }
    await pg.tap('#explorar .ay-chip.ay-about'); await pg.waitForTimeout(150);
    ok('P6 celular: tocar «Para qué sirve» despliega su explicación debajo y lo dice (aria-expanded)', (await pg.isVisible('#explorar .about p')) && (await pg.getAttribute('#explorar .ay-chip.ay-about', 'aria-expanded')) === 'true');
    { const r = await pg.evaluate(() => { const su = document.querySelector('#explorar .ayudas .about>summary'); return { tras: getComputedStyle(su, '::after').display, letra: getComputedStyle(su, '::first-letter').textTransform }; });
      ok('P6 celular: abierta desde la pastilla, la ayuda no pinta «Ocultar» encima del texto y empieza en mayúscula', r.tras === 'none' && r.letra === 'uppercase', r); }
    await pg.tap('#explorar .ay-chip.ay-about'); await pg.waitForTimeout(150);
    ok('P6 celular: tocarla otra vez la pliega', !(await pg.isVisible('#explorar .about p')) && (await pg.getAttribute('#explorar .ay-chip.ay-about', 'aria-expanded')) === 'false');
    ok('P6 celular: Explorar enseña 3 filtros y guarda 7 en «Más filtros (7)»', await pg.evaluate(() => { const vis = ['q', 'modal', 'figura', 'origin', 'yearfrom', 'yearto', 'order', 'region', 'pais', 'verif'].filter(i => document.getElementById(i).checkVisibility()); return vis.join() === 'q,modal,figura' && /Más filtros \(7\)/.test(document.querySelector('#masFiltros summary').textContent); }));
    await pg.evaluate(() => { document.getElementById('masFiltros').open = false; document.getElementById('region').value = document.getElementById('region').options[1].value; filterMandates(); });
    ok('P6 celular: con un filtro de «Más filtros» puesto, el resumen dice «1 en uso» y se abre', await pg.evaluate(() => document.getElementById('masFiltros').open && document.getElementById('mfUso').textContent === '1 en uso'));
    await pg.evaluate(() => clearFilters());
    ok('P6 celular: Su historia pone las épocas en una sola fila que se desliza en horizontal', await pg.evaluate(() => { showPage('historia'); const e = document.getElementById('hiEras'), bs = [...e.querySelectorAll('.btn')]; return new Set(bs.map(b => Math.round(b.getBoundingClientRect().top))).size === 1 && e.scrollWidth > e.clientWidth && getComputedStyle(e).overflowX === 'auto' && bs.every(b => b.getBoundingClientRect().height >= 44); }));
    ok('P6 celular: Tratados y comités en una columna, con barra de ratificación', await pg.evaluate(() => { showPage('tratados'); const L = [...document.querySelectorAll('#trSel .tr-card')]; return L.length === 9 && new Set(L.map(c => Math.round(c.getBoundingClientRect().left))).size === 1 && L.every(c => c.querySelector('.tr-barra i')); }));
    ok('P6 celular: Otros mecanismos y Arqueología, en tarjetas sin enlaces ni botones de menos de 44 px', await pg.evaluate(() => ['mecanismos', 'arqueologia', 'auditoria'].every(id => { showPage(id); return [...document.querySelectorAll('#' + id + ' .tablewrap a, #' + id + ' .tablewrap button')].filter(e => e.offsetParent).every(e => e.getBoundingClientRect().height >= 44); })));
    await pg.evaluate(() => showPage('inicio')); await pg.waitForTimeout(200);
    ok('P1 celular: la nota de la portada da la instrucción del celular con el número real de secciones', await pg.evaluate(() => { const n = document.querySelectorAll('.nav button').length, c = document.querySelector('.mn-cel'), e = document.querySelector('.mn-esc'); return n >= 15 && !!c.offsetParent && !e.offsetParent && c.textContent.includes(n + ' secciones'); }));
    ok('P1 celular: «Empieza por aquí» en 2 columnas sin fila suelta', await pg.evaluate(() => { const L = [...document.querySelectorAll('#inicio .tile')], xs = new Set(L.map(t => Math.round(t.getBoundingClientRect().left))), ys = new Set(L.map(t => Math.round(t.getBoundingClientRect().top))); return xs.size === 2 && ys.size === L.length / 2; }));
    await pg.evaluate(() => menu(true)); await pg.waitForTimeout(350);
    ok('P1 celular: en el menú no se repiten los botones de idioma; arriba queda el desplegable', !(await pg.isVisible('.side .idioma')) && (await pg.isVisible('.appbar .idioma select')));
    await pg.evaluate(() => menu(false));
    ok('P1 celular: «Para qué sirve esta pantalla», el selector de idioma y los enlaces sueltos miden al menos 44 px de alto', await pg.evaluate(() => { showPage('inicio'); const hs = [...document.querySelectorAll('.section.visible .about summary, .section.visible details.lf summary, .section.visible .linkline a, .appbar .idioma select')].filter(e => e.offsetParent).map(e => e.getBoundingClientRect().height); return hs.length >= 3 && hs.every(h => h >= 43.5); }));
    await ctx.close();
    const pd = await browser.newPage({ viewport: { width: 1440, height: 900 } }); await pd.goto(URL); await pd.waitForFunction(() => window.__atlasListo);
    ok('P1 escritorio: «Empieza por aquí» en 4 columnas y 2 filas', await pd.evaluate(() => { const L = [...document.querySelectorAll('#inicio .tile')]; return new Set(L.map(t => Math.round(t.getBoundingClientRect().left))).size === 4 && new Set(L.map(t => Math.round(t.getBoundingClientRect().top))).size === 2; }));
    ok('P1 escritorio: la nota no da la instrucción del celular y cuenta las secciones', await pd.evaluate(() => { const e = document.querySelector('.mn-esc'); return !!e.offsetParent && !document.querySelector('.mn-cel').offsetParent && e.textContent.includes(document.querySelectorAll('.nav button').length + ' secciones'); }));
    await pd.click('#nav button[data-page="paises"]'); await pd.waitForTimeout(200);
    ok('P1 escritorio: al cambiar de pantalla el título recibe el foco pero sin marco', await pd.evaluate(() => { const h = document.querySelector('#paises h1'); return document.activeElement === h && getComputedStyle(h).outlineStyle === 'none'; }));
    ok('P1 escritorio: el contador muestra el código del país en una pastilla, sin emoji de bandera', await pd.evaluate(() => !/[\u{1F1E6}-\u{1F1FF}]/u.test(document.getElementById('visBar').textContent)));
    await pd.close();
  }
  { // P1: con la interfaz en inglés, las etiquetas del contador van traducidas y lo que solo existe en español lo dice
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } }); await ctx.addInitScript(() => { try { localStorage.setItem('atlas_idioma', 'en'); } catch (e) {} });
    const pg = await ctx.newPage(); await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo && window.ATLAS_IDIOMA_en); await pg.waitForTimeout(500);
    const r = await pg.evaluate(() => ({ vis: document.getElementById('visBar').textContent, hoy: document.getElementById('hoyHistoria').innerHTML }));
    ok('P1 inglés: las etiquetas del contador de visitas están en inglés', /total visits/.test(r.vis) && /visits from your country/.test(r.vis) && !/visitas/i.test(r.vis));
    ok('P1 inglés: el hecho del mes lleva lang="es" y la marca «(in Spanish)»', /lang="es"/.test(r.hoy) && /\(in Spanish\)/.test(r.hoy));
    await ctx.close();
  }
  { // T26: idiomas de la interfaz (diccionario propio; los datos oficiales no se traducen)
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } }), pi = await ctx.newPage(), errs = [];
    pi.on('pageerror', e => errs.push(e.message));
    await pi.goto(URL + '#explorar'); await pi.waitForFunction(() => window.__atlasListo);
    ok('idiomas: en español no se carga ningún diccionario y hay selector ES/EN/FR/AR/ZH/RU', await pi.evaluate(() => !window.ATLAS_IDIOMA_en && !window.ATLAS_IDIOMA_fr && document.querySelectorAll('.side .idioma button').length === 6 && document.querySelectorAll('.appbar .idioma select option').length === 6));
    await pi.selectOption('.appbar .idioma select', 'en'); await pi.waitForFunction(() => window.__atlasListo && window.ATLAS_IDIOMA_en);
    await pi.waitForTimeout(300);
    const en = await pi.evaluate(() => ({ lang: document.documentElement.lang, nav: document.querySelector('#nav button').textContent, h1: document.querySelector('#explorar h1').textContent, ph: document.getElementById('q').placeholder, vis: document.querySelector('.section.visible')?.id, opt: [...document.querySelectorAll('#modal option')].find(o => o.value === 'Temático')?.textContent, w: document.documentElement.scrollWidth }));
    ok('idiomas: al elegir English se recarga en la misma pantalla con lang="en"', en.lang === 'en' && en.vis === 'explorar');
    ok('idiomas: menú, título, placeholder y opciones traducidos', /Overview/.test(en.nav) && en.h1 === 'Mandate explorer' && /^E\.g\. torture/.test(en.ph) && en.opt === 'Thematic');
    ok('idiomas: en inglés la pantalla cabe en 390 px', en.w <= 390);
    await pi.selectOption('#modal', 'Temático'); await pi.evaluate(() => filterMandates());
    ok('idiomas: los filtros siguen funcionando con las opciones traducidas', await pi.evaluate(() => filtered.length > 0 && filtered.every(m => m.alcance === 'Temático')));
    { // Fase 2: lo que dibuja el JavaScript. Un texto pendiente cuyos trozos están todos escritos en el código de la
      // página (no en los datos) es interfaz sin traducir: debe estar en idiomas/es.json (T94) y, traducido, en idiomas/en.json…
      for (const js of ["showPage('inicio')", "showPage('explorar')", "irPais('COL')", "showPage('tratados')", "showPage('relatores')", "showPage('sistema')", "showPage('mapa')", "mpElegir('ESP')", "mpCapaCambia()", "document.getElementById('mpCapa').value='epu';mpCapaCambia()", "mpElegir('COL')", "document.getElementById('mpCapa').value='basicos';mpCapaCambia()"]) { await pi.evaluate(js); await pi.waitForTimeout(400); }
      const fuente = require('fs').readFileSync(path.resolve(__dirname, '..', 'index.html'), 'utf8').match(/<script[^>]*>[\s\S]*?<\/script>/g).join(' ').replace(/&amp;/g, '&').replace(/\s+/g, ' ');
      // Palabra entera: «Spain» de un dato oficial no cuenta como interfaz por estar dentro de «America/Port_of_Spain».
      const enCodigo = x => new RegExp('(^|[^A-Za-zÀ-ÿ0-9_])' + x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[^A-Za-zÀ-ÿ0-9_])').test(fuente);
      const sinTraducir = (await pi.evaluate(() => ATLAS_IDIOMA.pendientes())).filter(k => { const t = k.split(/<[^>]+>|\{n\}|\{fecha\}/).map(x => x.replace(/[\s↗→←·…]+$/, '').trim()).filter(x => /[A-Za-zÀ-ÿ]{2}/.test(x)); return t.length && t.some(x => x.length >= 4) && t.every(x => enCodigo(x)) && !/^(<a>)?[A-Z]+(\/[A-Z0-9.{}n()XVI]+)+( ↗)?(<\/a>)?$/.test(k); }); // los símbolos de documentos no se traducen
      // T94: un texto que ya está en la plantilla idiomas/es.json y espera su traducción en Weblate sale en español a propósito.
      const esPlant = JSON.parse(require('fs').readFileSync(path.resolve(__dirname, '..', 'idiomas', 'es.json'), 'utf8')), enDic = JSON.parse(require('fs').readFileSync(path.resolve(__dirname, '..', 'idiomas', 'en.json'), 'utf8'));
      const enteros = sinTraducir.filter(k => !(k in esPlant && !(enDic[k] || '').trim()));
      if (enteros.length) console.error('idiomas: sin traducir', JSON.stringify(enteros));
      ok('idiomas: en inglés no queda texto de interfaz sin traducir en Panorama, Mandatos, una ficha de país, Tratados, Relatores, Mapa y Cómo funciona', enteros.length === 0);
      // T74: «Cómo leer un código» entera en inglés: tutorial, despiezador (con códigos de todo tipo), tabla y repaso. Se ignoran los
      // textos que son solo códigos (A/HRC/{n}/{n}, <code>Add.{n}</code>): no hay nada que traducir.
      { await pi.evaluate("showPage('codigos')"); await pi.waitForTimeout(300);
        const antes = await pi.evaluate(() => ATLAS_IDIOMA.pendientes());
        await pi.evaluate(() => { for (const v of ['tutorial', 'tabla', 'repaso']) codVista(v); for (let i = 0; i < COD_QUIZ.length; i++) { codQz = i; codRepaso(true); }
          for (const g of Object.keys(COD_GRUPOS)) { codVista('tabla'); codGrupo = g; codTabla(); } codGrupo = ''; $('codFiltro').value = 'zzzzqq'; codTabla(); $('codFiltro').value = ''; codTabla();
          codVista('despiezador'); for (const c of ['A/RES/217 A (III)', 'S/RES/1325 (2000)', 'A/HRC/RES/5/2', 'CCPR/C/GC/36', 'A/HRC/WG.6/41/IND/1', 'A/CONF.157/23', 'E/CN.4/2005/10/Add.1/Rev.1', 'ST/SG/AC.1/2', 'CAT/C/GC/4', 'HRI/GEN/1/Rev.9', 'A/C.3/78/L.12', 'CRC/C/GBR/CO/6', 'S/PV.8000', 'A/78/PV.5', 'XYZ/foo', 'A/HRC/NGO/12', 'A/HRC/RES/54/6/Corr.1', 'A/RES/S-27/2', 'E/2023/45', 'A/AC.109/5', 'UNEP/GC/1', 'A/HRC/52/CRP.3', 'A/HRC/52/INF/2', 'CRPD/C/GC/1', 'CED/C/ARG/Q/1', 'CERD/C/IND/CO/19-21', 'T/RES/1', 'SG/SM/123', 'ST/SGB/2003/13', 'E/CN.4/RES/2005/10', 'A/HRC/DEC/5/101', 'A/RES/3379 (XXX)']) { $('codQ').value = c; codDespiezador(); }
          $('codQ').value = ''; codDespiezador(); });
        await pi.waitForTimeout(300);
        const fuenteCod = require('fs').readFileSync(path.resolve(__dirname, '..', 'index.html'), 'utf8').replace(/&amp;/g, '&').replace(/\s+/g, ' '); // lo que ya salió en inglés al volver a pasar el traductor no cuenta: solo lo que está escrito en español en la página
        const nuevos = (await pi.evaluate(() => ATLAS_IDIOMA.pendientes())).filter(k => !antes.includes(k)).map(k => k.replace(/<[^>]+>/g, '')).filter(t => /[a-zà-ÿ]{4,}/.test(t.replace(/\{n\}/g, '')) && /\s/.test(t.trim()) || /^[A-ZÁÉÍÓÚa-zà-ÿ]{5,}$/.test(t.trim())).filter(t => t.split('{n}').map(x => x.trim()).filter(x => /[A-Za-zÀ-ÿ]{2}/.test(x)).every(x => fuenteCod.includes(x))).filter(t => !/^(presidential statement|conference room paper|ad hoc committee|information series|General Committee)$/.test(t.trim())); // términos en inglés que la propia explicación cita en cursiva
        if (nuevos.length) console.error('idiomas: Códigos sin traducir', JSON.stringify(nuevos));
        ok('idiomas: «Cómo leer un código» no deja texto sin traducir en inglés (T74)', nuevos.length === 0);
        ok('idiomas: ya no avisa de que la explicación solo está en español (T74)', await pi.evaluate(() => !/solo en español/.test(document.getElementById('codigos').innerText)));
      }
      // T67: frases con el nombre del país o la fecha de los datos dentro, y fechas cortas de la ficha, traducidas enteras
      await pi.evaluate("irPais('COL')"); await pi.waitForTimeout(1500);
      const f67 = await pi.evaluate(() => { document.querySelectorAll('#paises details.pf-pleg').forEach(d => { d.open = true }); return document.querySelector('#paises').innerText }); // T91: en el celular los bloques largos empiezan plegados
      ok('idiomas: en la ficha de país las frases con su nombre y las fechas cortas salen en inglés (T67)', /The history of Colombia/.test(f67) && /send to Colombia/.test(f67) && /Ratification \d{1,2} [A-Z][a-z]{2} \d{4}/.test(f67) && !/Son las cartas|Ratificación \d/.test(f67));
      await pi.evaluate("showPage('explorar')"); await pi.waitForTimeout(400);
      ok('idiomas: «Datos del …» con su fecha no parte la explicación de la pantalla (T67)', await pi.evaluate(() => /Data as of/.test(document.querySelector('#explorar .about').textContent) && !/Datos del/.test(document.querySelector('#explorar .about').textContent)));
    }
    await pi.selectOption('.appbar .idioma select', 'fr'); await pi.waitForFunction(() => window.__atlasListo && window.ATLAS_IDIOMA_fr); await pi.waitForTimeout(300);
    ok('idiomas: Français se recuerda y traduce', await pi.evaluate(() => document.documentElement.lang === 'fr' && localStorage.getItem('atlas_idioma') === 'fr' && /Explorer les mandats/.test(document.getElementById('nav').textContent)));
    await pi.selectOption('.appbar .idioma select', 'es'); await pi.waitForFunction(() => window.__atlasListo); await pi.waitForTimeout(300);
    ok('idiomas: volver a Español deja la página original', await pi.evaluate(() => document.documentElement.lang === 'es' && localStorage.getItem('atlas_idioma') === null && /Panorama/.test(document.querySelector('#nav button').textContent)));
    ok('idiomas: sin errores de JavaScript', errs.length === 0);
    await ctx.close();
  }
  // #188: celular con el navegador en «sitio de computador» (ancho de página ~980 px, pantalla de 412): la página se abre en vista móvil
  {
    const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';
    const abre = async (opt, pre) => { const c = await browser.newContext(opt); const pg = await c.newPage(); const er = []; pg.on('pageerror', e => er.push(e.message)); if (pre) await pg.addInitScript(pre); await pg.goto(URL + '#paises'); await pg.waitForTimeout(1500); return { c, pg, er }; };
    const a = await abre({ viewport: { width: 980, height: 1740 }, screen: { width: 412, height: 915 }, hasTouch: true, isMobile: false, userAgent: UA });
    const fr = a.pg.frames().find(f => f !== a.pg.mainFrame());
    const info = fr ? await fr.evaluate(() => ({ w: innerWidth, menu: getComputedStyle(document.getElementById('menuBtn') || document.body).display, opc: !document.getElementById('vistaOpc').hidden, pais: !!document.getElementById('paises') })) : null;
    ok('vista móvil forzada (#188): en un celular con «sitio de computador» la página se abre en un marco de 412 px con el diseño de celular', !!info && info.w === 412 && info.menu !== 'none' && info.opc && info.pais && a.er.length === 0);
    ok('vista móvil forzada (#188): el marco llena el ancho de la pantalla (sin franjas ni desplazamiento lateral)', await a.pg.evaluate(() => { const f = document.getElementById('marcoMovil'); const r = f && f.getBoundingClientRect(); return !!r && Math.abs(r.width - innerWidth) < 2 && document.documentElement.scrollWidth <= innerWidth; }));
    await a.c.close();
    const b = await abre({ viewport: { width: 980, height: 1740 }, screen: { width: 412, height: 915 }, hasTouch: true, isMobile: false, userAgent: UA }, () => { try { localStorage.setItem('atlas-vista', 'ancho'); } catch (e) {} });
    ok('vista móvil forzada (#188): si la persona eligió «ver en ancho completo», se respeta (y se ofrece volver)', (await b.pg.locator('#marcoMovil').count()) === 0 && (await b.pg.evaluate(() => !document.getElementById('vistaOpc').hidden && !document.getElementById('vistaMovil').hidden && document.getElementById('vistaAncho').hidden)));
    await b.c.close();
    const d = await abre({ viewport: { width: 1280, height: 800 }, userAgent: UA });
    ok('vista móvil forzada (#188): en un computador no cambia nada', (await d.pg.locator('#marcoMovil').count()) === 0 && (await d.pg.evaluate(() => document.getElementById('vistaOpc').hidden)));
    await d.c.close();
    const e = await abre({ viewport: { width: 412, height: 915 }, screen: { width: 412, height: 915 }, hasTouch: true, isMobile: true, userAgent: UA });
    ok('vista móvil forzada (#188): un celular en modo normal tampoco cambia (sin marco ni enlaces de vista)', (await e.pg.locator('#marcoMovil').count()) === 0 && (await e.pg.evaluate(() => document.getElementById('vistaOpc').hidden)));
    await e.c.close();
  }
  // #228 (T85 fase 3): modo claro y oscuro. «Automático» sigue al aparato; «Claro» u «Oscuro» se guardan en el navegador y aguantan la recarga
  {
    const tema = pg => pg.evaluate(() => ({ t: document.documentElement.dataset.theme, e: document.documentElement.dataset.temaElegido, tc: [...document.querySelectorAll('meta[name="theme-color"]')].map(m => m.content), cs: getComputedStyle(document.documentElement).colorScheme, fondo: getComputedStyle(document.body).backgroundColor, guardado: (() => { try { return localStorage.getItem('atlas-tema'); } catch (e) { return 'sin-almacenamiento'; } })() }));
    const c1 = await browser.newContext({ viewport: { width: 1366, height: 800 }, colorScheme: 'light' });
    const p1 = await c1.newPage(); const er1 = []; p1.on('pageerror', e => er1.push(e.message));
    await p1.goto(URL); await p1.waitForTimeout(400);
    let t = await tema(p1);
    ok('modo de color (#228): sin elegir nada sigue al aparato (claro) con fondo marfil y theme-color marfil', t.t === 'light' && t.e === 'auto' && t.cs === 'light' && t.fondo === 'rgb(245, 244, 240)' && t.tc.includes('#F5F4F0'));
    await p1.emulateMedia({ colorScheme: 'dark' }); await p1.waitForTimeout(150);
    t = await tema(p1);
    ok('modo de color (#228): en «Automático», si el aparato pasa a oscuro la página también (sin recargar)', t.t === 'dark' && t.cs === 'dark' && t.fondo === 'rgb(16, 19, 28)');
    const botones = await p1.locator('.side .tema-sel button').allTextContents();
    ok('modo de color (#228): el menú lateral tiene el selector Automático / Claro / Oscuro, con su nombre accesible', botones.join('|') === 'Automático|Claro|Oscuro' && await p1.isVisible('.side .tema-sel') && await p1.evaluate(() => document.getElementById(document.querySelector('.tema-sel').getAttribute('aria-labelledby')).textContent === 'Modo de color'));
    await p1.click('.side .tema-sel button[data-tema="light"]'); await p1.waitForTimeout(100);
    t = await tema(p1);
    ok('modo de color (#228): elegir «Claro» con el aparato en oscuro cambia data-theme, theme-color y el botón pulsado, y se guarda', t.t === 'light' && t.e === 'light' && t.guardado === 'light' && t.tc.every(x => x === '#F5F4F0') && await p1.evaluate(() => document.querySelector('.tema-sel button[data-tema="light"]').getAttribute('aria-pressed') === 'true' && document.querySelectorAll('.tema-sel button[aria-pressed="true"]').length === 1));
    await p1.reload(); await p1.waitForTimeout(400);
    t = await tema(p1);
    ok('modo de color (#228): «Claro» sigue después de recargar', t.t === 'light' && t.e === 'light' && await p1.evaluate(() => document.querySelector('.tema-sel button[data-tema="light"]').getAttribute('aria-pressed') === 'true'));
    await p1.evaluate(() => showPage('mapa')); await p1.waitForTimeout(1200);
    const antes = await p1.evaluate(() => [...document.querySelectorAll('#mpSvg .mp-p')].slice(0, 40).map(x => x.style.fill).join());
    await p1.click('.side .tema-sel button[data-tema="dark"]'); await p1.waitForTimeout(200);
    const despues = await p1.evaluate(() => [...document.querySelectorAll('#mpSvg .mp-p')].slice(0, 40).map(x => x.style.fill).join());
    t = await tema(p1);
    ok('modo de color (#228): «Oscuro» se aplica y el mapa se repinta con la escala de su modo', t.t === 'dark' && t.guardado === 'dark' && antes.length > 0 && antes !== despues);
    await p1.click('.side .tema-sel button[data-tema="auto"]'); await p1.waitForTimeout(100);
    t = await tema(p1);
    ok('modo de color (#228): volver a «Automático» borra lo guardado y sigue al aparato', t.e === 'auto' && t.guardado === null && t.t === 'dark' && t.tc.includes('#F5F4F0') && t.tc.includes('#10131C'));
    ok('modo de color (#228): sin errores de JavaScript', er1.length === 0);
    await c1.close();
    // celular: el desplegable de la barra superior
    const c2 = await browser.newContext({ viewport: { width: 390, height: 844 }, colorScheme: 'dark', hasTouch: true });
    const p2 = await c2.newPage();
    await p2.goto(URL); await p2.waitForTimeout(400);
    const caja = await p2.locator('.appbar .tema-cel').boundingBox();
    ok('modo de color (#228): en el celular el selector está en la barra superior, con 44 px', !!caja && caja.width >= 44 && caja.height >= 44 && await p2.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1 && document.getElementById('temaCel').getAttribute('aria-label') === 'Modo de color'));
    await p2.selectOption('#temaCel', 'light'); await p2.waitForTimeout(100);
    await p2.reload(); await p2.waitForTimeout(400);
    t = await tema(p2);
    ok('modo de color (#228): en el celular, «Claro» se elige arriba y sigue después de recargar', t.t === 'light' && t.e === 'light' && await p2.evaluate(() => document.getElementById('temaCel').value === 'light'));
    await c2.close();
    // Barra superior estrecha: ningún control se encoge ni se sale. «Menú» (si se ve) queda dentro de su botón, y la marca, el selector de modo
    // y el de idioma no se pisan entre sí ni salen de la pantalla (la marca solo puede ocultarse por debajo de 340 px). scrollWidth no basta: overflow-x:hidden y el desborde a la izquierda en árabe lo esconden.
    for (const ln of ['es', 'ar', 'ru']) {
      for (const ancho of [320, 360, 390, 412]) {
        const cb = await browser.newContext({ viewport: { width: ancho, height: 800 }, hasTouch: true, isMobile: true });
        await cb.addInitScript(l => { try { localStorage.setItem('atlas_idioma', l); } catch (e) {} }, ln);
        const pb = await cb.newPage();
        await pb.goto(URL); await pb.waitForTimeout(400);
        const fallo = await pb.evaluate(() => {
          const rc = e => { const r = document.createRange(); r.selectNodeContents(e); return r.getBoundingClientRect(); };
          const caja = s => { const e = document.querySelector(s); return e && e.getClientRects().length ? e.getBoundingClientRect() : null; };
          const cruza = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5;
          const bt = document.querySelector('.burger-t'), burger = caja('.burger');
          const ab = document.querySelector('.appbrand'); const partes = { marca: getComputedStyle(ab).display === 'none' ? (innerWidth <= 340 ? undefined : null) : rc(ab), modo: caja('.appbar .tema-cel'), idioma: caja('.appbar .idioma'), menu: burger };
          const err = [];
          if (bt && getComputedStyle(bt).display !== 'none') { const t = rc(bt); if (t.left < burger.left || t.right > burger.right) err.push('«Menú» fuera de su botón'); if (partes.marca && cruza(t, partes.marca)) err.push('«Menú» pisa la marca'); }
          for (const [k, r] of Object.entries(partes)) { if (r === undefined) continue; if (!r) { err.push('falta ' + k); continue; } if (r.left < -0.5 || r.right > innerWidth + 0.5) err.push(k + ' sale de la pantalla'); }
          const ks = Object.keys(partes); for (let i = 0; i < ks.length; i++) for (let j = i + 1; j < ks.length; j++) if (partes[ks[i]] && partes[ks[j]] && cruza(partes[ks[i]], partes[ks[j]])) err.push(ks[i] + ' pisa ' + ks[j]);
          return err.join(', ');
        });
        ok(`barra superior (#228) a ${ancho} px en ${ln}: menú, marca, modo de color e idioma sin pisarse ni salir de la pantalla${fallo ? ' → ' + fallo : ''}`, !fallo);
        if (ancho >= 390) { // en los celulares comunes «ATLAS ONU» va en una sola línea aunque esté el botón del modo de color
          const m = await pb.evaluate(() => { const e = document.querySelector('.appbrand'), cs = getComputedStyle(e); return { alto: e.getBoundingClientRect().height, letra: parseFloat(cs.fontSize), modo: !!document.querySelector('.appbar .tema-cel') && getComputedStyle(document.querySelector('.appbar .tema-cel')).display !== 'none', desborda: e.scrollWidth > e.clientWidth + 1 }; });
          ok(`barra superior (#228) a ${ancho} px en ${ln}: «ATLAS ONU» en una línea y entero, con el selector de modo presente (alto ${m.alto.toFixed(0)} px, letra ${m.letra} px)`, m.modo && m.alto <= m.letra * 1.3 && !m.desborda);
        }
        await cb.close();
      }
    }
    // sin almacenamiento (navegador que lo bloquea): funciona igual, sin errores
    const c3 = await browser.newContext({ viewport: { width: 1366, height: 800 }, colorScheme: 'light' });
    await c3.addInitScript(() => { Object.defineProperty(window, 'localStorage', { get() { throw new Error('bloqueado'); } }); });
    const p3 = await c3.newPage(); const er3 = []; p3.on('pageerror', e => er3.push(e.message));
    await p3.goto(URL); await p3.waitForTimeout(400);
    await p3.click('.side .tema-sel button[data-tema="dark"]'); await p3.waitForTimeout(100);
    t = await tema(p3);
    ok('modo de color (#228): con el almacenamiento bloqueado el selector funciona y no hay errores', t.t === 'dark' && t.guardado === 'sin-almacenamiento' && er3.length === 0);
    await c3.close();
    // #188 + #228: el marco del celular con «sitio de computador» toma el color del modo antes de pintar y lo sigue
    const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';
    const c4 = await browser.newContext({ viewport: { width: 980, height: 1740 }, screen: { width: 412, height: 915 }, hasTouch: true, isMobile: false, userAgent: UA, colorScheme: 'light' });
    const p4 = await c4.newPage();
    await p4.goto(URL); await p4.waitForTimeout(1500);
    const fr4 = p4.frames().find(f => f !== p4.mainFrame());
    const ext = () => p4.evaluate(() => ({ fondo: getComputedStyle(document.body).backgroundColor, tc: (document.querySelector('meta[name="theme-color"]') || {}).content }));
    let e4 = await ext();
    ok('modo de color (#228): el marco del celular nace en claro si el aparato está en claro', !!fr4 && e4.fondo === 'rgb(245, 244, 240)' && e4.tc === '#F5F4F0' && await fr4.evaluate(() => document.documentElement.dataset.theme === 'light'));
    if (fr4) { await fr4.evaluate(() => atlasTema('dark')); await p4.waitForTimeout(200); }
    e4 = await ext();
    ok('modo de color (#228): al elegir «Oscuro» dentro del marco, el fondo y la barra del navegador también pasan a oscuro', e4.fondo === 'rgb(16, 19, 28)' && e4.tc === '#10131C');
    await c4.close();
  }
  // P9 (#226, plan de diseño fase 8): las metas medibles del celular, en modo oscuro y en claro, en todas las pantallas del menú:
  // controles de 44 px o más fuera del texto corrido, texto de 13 px o más, sin desborde lateral y ninguna de más de unas 8 pantallas de alto
  {
    const { METAS, medirPantalla, cumple } = require('./metas_ux.cjs');
    const c5 = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
    const p5 = await c5.newPage();
    p5.on('pageerror', e => res.errors.push('metas P9: ' + e.message));
    await p5.goto(URL + (URL.includes('?') ? '&' : '?') + 'movil=1');
    await p5.waitForFunction(() => window.__atlasListo, null, { timeout: 20000 }).catch(() => {});
    const ids = await p5.evaluate(() => [...document.querySelectorAll('.main .section')].map(x => x.id));
    for (const modo of ['dark', 'light']) {
      await p5.evaluate(m => atlasTema(m), modo);
      const malas = [];
      for (const id of ids) { await p5.evaluate(i => showPage(i), id); await p5.waitForTimeout(150); const m = await p5.evaluate(medirPantalla, METAS); if (!cumple(m)) malas.push(`${id} (largo ${m.largo}, ancho ${m.ancho}, controles ${m.controles} ${m.controlesEj.join(' ')}, texto ${m.textos} ${m.textosEj.join(' ')})`); }
      ok(`metas P9 (#226), modo ${modo === 'dark' ? 'oscuro' : 'claro'}: las ${ids.length} pantallas a 390 px sin controles < ${METAS.control} px, sin texto < ${METAS.texto} px, sin desborde y ≤ ${METAS.largo} pantallas de alto ${malas.join('; ')}`, ids.length >= 20 && malas.length === 0 && await p5.evaluate(m => document.documentElement.dataset.theme === m, modo));
    }
    await p5.evaluate(() => atlasTema('auto'));
    await c5.close();
  }
  await browser.close();
  const failed = res.checks.filter(c => !c.ok);
  console.log(JSON.stringify({ ...res, passed: res.checks.length - failed.length, failed: failed.length }, null, 1));
  process.exit(failed.length || res.errors.length ? 1 : 0);
})();
