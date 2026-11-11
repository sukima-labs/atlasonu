// Prueba real en Chromium (Playwright). Uso: node tests/browser.cjs
const { chromium } = require('playwright');
const path = require('path'), assert = require('assert');
const URL = process.env.ATLAS_URL || 'file://' + path.resolve(__dirname, '..', 'index.html');
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
    ok(vp.name + ': T81 «Siglas y códigos» es una sola entrada del menú con tres pestañas, y las tres direcciones siguen vivas', await (async () => { const ent = await page.evaluate(() => ({ botones: [...document.querySelectorAll('#nav button')].filter(b => ['siglas', 'codigos', 'codificacion'].includes(b.dataset.page)).map(b => b.dataset.page), sueltas: [...document.querySelectorAll('#nav button')].some(b => ['codigos', 'codificacion'].includes(b.dataset.page)) })); const res = []; for (const id of ['siglas', 'codigos', 'codificacion']) { await page.evaluate(i => showPage(i), id); res.push(await page.evaluate(i => { const sec = document.getElementById(i), t = [...sec.querySelectorAll('.sc-tabs button')], act = document.querySelector('#nav button[aria-current]'); return sec.classList.contains('visible') && t.length === 3 && t.filter(b => b.getAttribute('aria-pressed') === 'true').length === 1 && act && act.dataset.page === 'siglas'; }, id)); } return ent.botones.length === 1 && ent.botones[0] === 'siglas' && !ent.sueltas && res.every(Boolean); })());
    ok(vp.name + ': todas las cabeceras de tabla llevan scope', await page.evaluate(() => [...document.querySelectorAll('th')].every(t => t.hasAttribute('scope'))));
    ok(vp.name + ': ningún role=tablist sin pestañas', await page.evaluate(() => !document.querySelector('[role=tablist]')));
    await page.evaluate(() => showPage('explorar'));
    await page.fill('#q', 'tortura'); await page.evaluate(() => filterMandates());
    ok(vp.name + ': búsqueda "tortura"', /tortura/i.test(await page.textContent('#mandBody')));
    await page.fill('#q', 'enforced disappearance'); await page.evaluate(() => filterMandates());
    ok(vp.name + ': búsqueda EN con sinónimos', /desaparici/i.test(await page.textContent('#mandBody')));
    await page.fill('#q', ''); await page.evaluate(() => filterMandates());
    ok(vp.name + ': 20 mandatos y «Mostrar más»', (await page.locator('#mandBody tr:not(.mas)').count()) === 20 && (await page.locator('#mandBody tr.mas button').count()) === 1);
    await page.locator('#mandBody tr.mas button').click();
    await page.locator('#mandBody tr.mas button').click();
    ok(vp.name + ': 57 mandatos tras mostrar más', (await page.locator('#mandBody tr:not(.mas)').count()) === 57);
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
    ok(vp.name + ': sección Países visible con 196 filas', await page.isVisible('#paises') && (await page.locator('#pBody tr').count()) === 21 && /quedan 176/.test(await page.textContent('#pBody')) && (await todosLosPaises(page), (await page.locator('#pBody tr').count()) === 196));
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
    ok(vp.name + ': la ficha tiene el menú «Qué quieres ver» con 9 saltos y el botón de comparar', (await page.locator('#pNav button[onclick^="irSeccion"]').count()) === 9 && (await page.locator('#pNav button[onclick^="compararCon"]').count()) === 1);
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
    // T63: glosario de siglas al tocar (en la ficha de India, sin salir de la página)
    await page.waitForTimeout(250);
    ok(vp.name + ': las siglas del texto de la ficha quedan marcadas y las de botones y enlaces no', (await page.locator('#pDocs abbr.sg[data-k="EPU"]').count()) > 0 && (await page.locator('#pNav abbr.sg, #pDocs a abbr.sg, #paises button abbr.sg').count()) === 0);
    const sgA = page.locator('#pDocs abbr.sg[data-k="EPU"]').first(); await sgA.scrollIntoViewIfNeeded(); await sgA.click(); await page.waitForTimeout(150);
    const sgBox = await page.locator('#sgPop').boundingBox();
    ok(vp.name + ': tocar «EPU» abre su significado junto a la sigla, dentro de la pantalla', await page.isVisible('#sgPop') && /Examen Peri[oó]dico Universal/.test(await page.textContent('#sgPop')) && /Universal Periodic Review/.test(await page.textContent('#sgPop')) && sgBox && sgBox.x >= 0 && sgBox.x + sgBox.width <= vp.width + 1 && sgBox.y >= 0 && sgBox.y + sgBox.height <= vp.height + 1 && await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.keyboard.press('Escape'); await page.waitForTimeout(100);
    ok(vp.name + ': Escape cierra la tarjeta de la sigla', !(await page.isVisible('#sgPop')));
    await sgA.click(); await page.waitForTimeout(100); await page.click('#sgPop button:has-text("Ver en «Siglas»")'); await page.waitForTimeout(300);
    ok(vp.name + ': «Ver en Siglas» abre el diccionario con la sigla buscada', await page.isVisible('#siglas') && (await page.inputValue('#sigQ')) === 'EPU' && !(await page.isVisible('#sgPop')) && (await page.locator('#siglas abbr.sg').count()) === 0);
    await page.evaluate(() => showPage('paises'));
    // T40: Relatores y relatoras
    await page.evaluate(() => showPage('relatores')); await page.waitForTimeout(250);
    const rN = await page.locator('#rOut .rel-card').count();
    ok(vp.name + ': «Relatores y relatoras» muestra una tarjeta por titular, con mandato y nacionalidad, sin desbordar', rN >= 60 && rN === (await page.evaluate(() => REL.length)) && /Nacionalidad:/.test(await page.textContent('#rOut')) && await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.selectOption('#rCargo', 'gt'); await page.waitForTimeout(150);
    const rGt = await page.locator('#rOut .rel-card').count(), rGtTag = await page.locator('#rOut .rel-card .tag', { hasText: 'Grupo de trabajo' }).count();
    ok(vp.name + ': filtro «Grupo de trabajo» deja solo miembros de grupos de trabajo', rGt > 0 && rGt < rN && rGtTag === rGt);
    await page.selectOption('#rCargo', ''); await page.waitForTimeout(150);
    await page.locator('#rOut .rel-card').first().getByRole('button', { name: 'Ver el mandato' }).click(); await page.waitForTimeout(300);
    ok(vp.name + ': desde una tarjeta, «Ver el mandato» abre su ficha en Explorar', await page.isVisible('#explorar'));
    await page.evaluate(() => showPage('paises'));
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
    const bgMapa = await page.$eval('#mpWrap', e => getComputedStyle(e).backgroundColor);
    const malos = [];
    for (const capa of ['basicos', 'tratado', 'invitacion', 'mandato', 'comision', 'conflictos', 'comunicaciones', 'epu']) {
      await page.selectOption('#mpCapa', capa); await page.waitForFunction(() => !/Cargando/.test(document.getElementById('mpLeyenda').textContent));
      const cols = await page.evaluate(() => [...document.querySelectorAll('#mpLeyenda .mp-sw, #mpLeyenda .mp-esc i')].map(e => getComputedStyle(e).backgroundColor));
      for (const c of cols) { const [a, b] = [lum(c), lum(bgMapa)].sort((x, y) => y - x); const cr = (a + .05) / (b + .05); const [r, g, bl] = c.match(/\d+/g).map(Number); const dorado = r > 150 && g > 100 && bl < 130 && r > g && g > bl; if (cr < 1.8 && c !== 'rgb(50, 56, 65)') malos.push(capa + ' ' + c + ' contraste ' + cr.toFixed(2)); if (dorado) malos.push(capa + ' ' + c + ' dorado de la plantilla'); }
    }
    ok(vp.name + ': Mapa: ningún color de las leyendas se confunde con el fondo del mapa ni con el dorado de la plantilla' + (malos.length ? ' → ' + malos.join('; ') : ''), !malos.length);
    await page.selectOption('#mpCapa', 'basicos');
    await page.click('#mpInfo button'); await page.waitForTimeout(300);
    ok(vp.name + ': Mapa: «Ver ficha del país» abre la ficha del país tocado', await page.isVisible('#paises') && (await page.inputValue('#pSel')) === 'ESP');
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
    await page.getByRole('button', { name: /^Tortura, malos tratos y detención \(\d+\)/ }).click(); await page.waitForTimeout(250);
    ok(vp.name + ': subtema «Tortura…» → lista corta de mandatos temáticos aplicables', (await page.locator('#pTemasTabla tbody tr').count()) < 10 && /tortura/i.test(await page.textContent('#pTemasTabla')));
    await page.locator('#pTema').click(); await page.keyboard.type('agua', { delay: 40 }); await page.waitForTimeout(250);
    ok(vp.name + ': escribir un tema libre mantiene el foco del campo y filtra', (await page.evaluate(() => document.activeElement.id)) === 'pTema' && /agua/i.test(await page.textContent('#pTemasTabla')));
    await page.fill('#pTema', ''); await page.getByRole('button', { name: /^Todos \(44\)/ }).click(); await page.waitForTimeout(200);
    ok(vp.name + ': sin tema → los 44 mandatos temáticos aplicables', (await page.locator('#pTemasTabla tbody tr').count()) === 44);
    // T61: comparador de dos países (desde la ficha de Colombia)
    await page.getByRole('button', { name: '⇄ Comparar con otro país' }).click(); await page.waitForTimeout(400);
    ok(vp.name + ': «Comparar con otro país» abre el comparador con Colombia y el foco en el segundo país', await page.evaluate(() => $('pComp').open && $('cmpA').value === 'COL' && document.activeElement.id === 'cmpB') && /Elige dos países/.test(await page.textContent('#cmpOut')));
    await page.selectOption('#cmpB', 'ESP'); await page.waitForTimeout(250);
    const cmpN = await page.locator('#cmpOut tbody tr').count(), cmpT = await page.textContent('#cmpOut');
    ok(vp.name + ': Colombia frente a España: tabla con los 18 tratados y los datos de ficha, cabeceras con los dos nombres', cmpN === 28 && /Colombia/.test(await page.textContent('#cmpOut thead')) && /España/.test(await page.textContent('#cmpOut thead')) && /CEDAW/.test(cmpT) && /Invitación permanente/.test(cmpT) && /Fuentes:/.test(cmpT));
    const nDif = await page.locator('#cmpOut tbody tr.cmp-dif').count();
    await page.click('#cmpDif'); await page.waitForTimeout(200);
    ok(vp.name + ': «Solo lo que cambia» deja solo las filas distintas y lo marca pulsado', nDif > 0 && nDif < cmpN && (await page.locator('#cmpOut tbody tr').count()) === nDif && (await page.getAttribute('#cmpDif', 'aria-pressed')) === 'true' && new RegExp(nDif + ' de 28 aspectos cambian').test(await page.textContent('#cmpOut')));
    ok(vp.name + ': el comparador no desborda la pantalla y en celular cada fila es una tarjeta con etiquetas', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1) && (vp.name !== 'movil' || (await page.locator('#cmpOut td[data-label="España"]').count()) === nDif));
    await page.click('#cmpDif'); await page.selectOption('#cmpB', 'COL'); await page.waitForTimeout(150);
    ok(vp.name + ': elegir el mismo país dos veces pide dos distintos', /dos países distintos/.test(await page.textContent('#cmpOut')));
    await page.evaluate(() => { $('pComp').open = false; });
    await page.evaluate(() => showPage('inicio')); await page.selectOption('#guiadaSel', { index: 4 }); await page.selectOption('#guiadaPais', 'COL'); await page.getByRole('button', { name: 'Ver mandatos' }).click(); await page.waitForTimeout(300);
    ok(vp.name + ': búsqueda guiada con país (Colombia + agua/alimentación…) abre Países con mandatos aplicables', await page.isVisible('#paises') && /Colombia/.test(await page.textContent('#pOut')) && (await page.locator('#pTemasTabla tbody tr').count()) > 0);
    if (vp.name === 'escritorio') { await page.evaluate(() => document.getElementById('pOut').scrollIntoView()); await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_pais_temas.png') }); }
    await page.evaluate(() => showPage('explorar')); await page.selectOption('#modal', 'País'); await page.selectOption('#pais', 'COL'); await page.waitForTimeout(250);
    ok(vp.name + ': Explorador País+Colombia explica la ausencia (no una pantalla en blanco)', /no tiene mandato por país vigente/.test(await page.textContent('#count')) && /Países/.test(await page.textContent('#count')));
    await page.evaluate(() => clearFilters());
    await page.evaluate(() => showPage('inicio')); await page.fill('#quick', 'xqzvbn'); await page.waitForTimeout(500);
    const href = await page.locator('#smartOut a', { hasText: 'Solicitar verificación' }).getAttribute('href');
    ok(vp.name + ': búsqueda sin resultado ofrece solicitud prellenada en GitHub', /issues\/new\?template=solicitud-verificacion\.yml/.test(href) && /busqueda=xqzvbn/.test(href));
    await page.evaluate(() => showPage('explorar')); await page.selectOption('#pais', 'BLR'); await page.waitForTimeout(250);
    ok(vp.name + ': filtro de país en el explorador (Belarús → 1 mandato)', (await page.locator('#mandBody tr').count()) === 1);
    await page.evaluate(() => clearFilters());
    await page.evaluate(() => showPage('inicio')); await page.fill('#quick', 'Camboya'); await page.waitForTimeout(500);
    await page.locator('#smartOut button', { hasText: 'Ver país' }).first().click();
    ok(vp.name + ': la búsqueda inteligente lleva a la sección del país', await page.isVisible('#paises') && /Camboya/.test(await page.textContent('#pOut')));
    for (const id of ['inicio', 'explorar', 'paises', 'sistema', 'arqueologia', 'recuperar', 'mecanismos', 'codificacion', 'seleccion', 'auditoria', 'fuentes']) {
      await page.evaluate(i => showPage(i), id);
      ok(vp.name + ': «Para qué sirve» visible en ' + id, await page.isVisible('#' + id + ' .about') && /Para qué sirve esta pantalla/.test(await page.textContent('#' + id + ' .about')));
    }
    await page.evaluate(() => showPage('arqueologia')); await page.fill('#qt', 'agua'); await page.waitForTimeout(250);
    ok(vp.name + ': Arqueología lista actos reales del agua (A/HRC/RES/60/9)', /A\/HRC\/RES\/60\/9/.test(await page.textContent('#traceBody')));
    await page.fill('#qt', '');
    await page.evaluate(() => showPage('inicio')); await page.waitForTimeout(1200);
    const nov = await page.textContent('#novedades');
    if (vp.name === 'escritorio') ok('escritorio: no aparece la barra móvil ni el botón de menú', !(await page.isVisible('#burger')) && !(await page.isVisible('#appbar')));
    ok(vp.name + ': panel de novedades (' + (URL.startsWith('http') ? 'en línea: última revisión' : 'sin conexión: aviso') + ')', URL.startsWith('http') ? /Última revisión/.test(nov) : /sin conexión/.test(nov));
    ok(vp.name + ': «Novedades detectadas» llega plegada y se abre al tocar', !(await page.locator('#novedadesBox').evaluate(e => e.open)) && !(await page.isVisible('#novedades')) && (await page.click('#novedadesBox>summary'), await page.isVisible('#novedades')));
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
    ok('portada: el panel de datos (cifras) está plegado por defecto', !(await pg.evaluate(() => document.querySelector('details.datos').open)));
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
  // Navegación móvil: menú lateral con botón, se cierra al navegar; sin desbordes en ningún tamaño de teléfono/tableta
  for (const [nom, w, h] of [['Android 320', 320, 658], ['iPhone SE', 375, 667], ['Android 412', 412, 915], ['tableta 768', 768, 1024]]) {
    const pg = await browser.newPage({ viewport: { width: w, height: h }, hasTouch: true, isMobile: true }); await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo);
    ok(nom + ': hay barra superior con botón de menú y el menú está cerrado', (await pg.isVisible('#burger')) && !(await pg.isVisible('#side')));
    ok(nom + ': se ve la pista de las tres líneas y la etiqueta «Menú»', (await pg.isVisible('#menuHint')) && (await pg.isVisible('.burger-t')));
    await pg.tap('#burger'); await pg.waitForTimeout(350);
    ok(nom + ': al abrir el menú la pista se oculta y no vuelve', !(await pg.isVisible('#menuHint')) && (await pg.evaluate(() => localStorage.getItem('atlas_pista_menu'))) === '1');
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
      // página (no en los datos) es interfaz sin traducir: debe estar en data/idiomas/en.js, fr.js, ar.js, zh.js y ru.js.
      for (const js of ["showPage('inicio')", "showPage('explorar')", "irPais('COL')", "showPage('tratados')", "showPage('relatores')", "showPage('sistema')", "showPage('mapa')", "mpElegir('ESP')", "mpCapaCambia()", "document.getElementById('mpCapa').value='epu';mpCapaCambia()", "mpElegir('COL')", "document.getElementById('mpCapa').value='basicos';mpCapaCambia()"]) { await pi.evaluate(js); await pi.waitForTimeout(400); }
      const fuente = require('fs').readFileSync(path.resolve(__dirname, '..', 'index.html'), 'utf8').match(/<script[^>]*>[\s\S]*?<\/script>/g).join(' ').replace(/&amp;/g, '&').replace(/\s+/g, ' ');
      // Palabra entera: «Spain» de un dato oficial no cuenta como interfaz por estar dentro de «America/Port_of_Spain».
      const enCodigo = x => new RegExp('(^|[^A-Za-zÀ-ÿ0-9_])' + x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[^A-Za-zÀ-ÿ0-9_])').test(fuente);
      const sinTraducir = (await pi.evaluate(() => ATLAS_IDIOMA.pendientes())).filter(k => { const t = k.split(/<[^>]+>|\{n\}|\{fecha\}/).map(x => x.replace(/[\s↗→←·…]+$/, '').trim()).filter(x => /[A-Za-zÀ-ÿ]{2}/.test(x)); return t.length && t.some(x => x.length >= 4) && t.every(x => enCodigo(x)) && !/^(<a>)?[A-Z]+(\/[A-Z0-9.{}n()XVI]+)+( ↗)?(<\/a>)?$/.test(k); }); // los símbolos de documentos no se traducen
      const enteros = sinTraducir;
      if (enteros.length) console.error('idiomas: sin traducir', JSON.stringify(enteros));
      ok('idiomas: en inglés no queda texto de interfaz sin traducir en Panorama, Mandatos, una ficha de país, Tratados, Relatores, Mapa y Cómo funciona', enteros.length === 0);
      // T67: frases con el nombre del país o la fecha de los datos dentro, y fechas cortas de la ficha, traducidas enteras
      await pi.evaluate("irPais('COL')"); await pi.waitForTimeout(1500);
      const f67 = await pi.evaluate(() => document.querySelector('#paises').innerText);
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
  await browser.close();
  const failed = res.checks.filter(c => !c.ok);
  console.log(JSON.stringify({ ...res, passed: res.checks.length - failed.length, failed: failed.length }, null, 1));
  process.exit(failed.length || res.errors.length ? 1 : 0);
})();
