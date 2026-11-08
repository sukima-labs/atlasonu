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
    const malos = []; for (const id of ['inicio', 'explorar', 'sistema', 'paises', 'tratados', 'siglas', 'arqueologia', 'recuperar', 'mecanismos', 'codificacion', 'seleccion', 'auditoria', 'fuentes']) { await pg.evaluate(x => showPage(x), id); const d = await pg.evaluate(() => [document.documentElement.scrollWidth, innerWidth]); if (d[0] > d[1] + 1) malos.push(id); }
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
  await browser.close();
  const failed = res.checks.filter(c => !c.ok);
  console.log(JSON.stringify({ ...res, passed: res.checks.length - failed.length, failed: failed.length }, null, 1));
  process.exit(failed.length || res.errors.length ? 1 : 0);
})();
