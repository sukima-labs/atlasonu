// Prueba real en Chromium (Playwright). Uso: node tests/browser.cjs
const { chromium } = require('playwright');
const path = require('path'), assert = require('assert');
const URL = process.env.ATLAS_URL || 'file://' + path.resolve(__dirname, '..', 'index.html');
(async () => {
  const browser = await chromium.launch();
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
    await page.evaluate(() => showPage('explorar'));
    await page.fill('#q', 'tortura'); await page.evaluate(() => filterMandates());
    ok(vp.name + ': búsqueda "tortura"', /tortura/i.test(await page.textContent('#mandBody')));
    await page.fill('#q', 'enforced disappearance'); await page.evaluate(() => filterMandates());
    ok(vp.name + ': búsqueda EN con sinónimos', /desaparici/i.test(await page.textContent('#mandBody')));
    await page.fill('#q', ''); await page.evaluate(() => filterMandates());
    ok(vp.name + ': 57 mandatos listados', (await page.locator('#mandBody tr').count()) === 57);
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
    await page.getByRole('button', { name: /Países/ }).first().click();
    ok(vp.name + ': sección Países visible con 196 filas', await page.isVisible('#paises') && (await page.locator('#pBody tr').count()) === 196);
    await page.getByRole('button', { name: /^América Latina y el Caribe \(\d+\)/ }).click(); await page.waitForTimeout(200);
    ok(vp.name + ': chip «América Latina y el Caribe» → 33 países', (await page.locator('#pBody tr').count()) === 33 && /Colombia/.test(await page.textContent('#pBody')));
    await page.getByRole('button', { name: /^Todos \(\d+\)/ }).click(); await page.waitForTimeout(200);
    await page.fill('#pQ', 'India'); await page.getByRole('button', { name: 'Buscar' }).first().click(); await page.waitForTimeout(500);
    const box = await page.locator('#pOut .detail h2').boundingBox();
    ok(vp.name + ': al buscar India su ficha queda a la vista (sin tener que desplazarse a ciegas)', box && box.y < (vp.height * 0.9) && /Adhesión 10 abr 1979/.test(await page.textContent('#pOut')) && /Firmó 14 oct 1997/.test(await page.textContent('#pOut')));
    await page.fill('#pQ', 'India'); await page.getByRole('button', { name: 'Buscar' }).first().click(); await page.waitForFunction(() => /CCPR\/C\/IND\/CO\/4/.test(document.getElementById('pDocs').textContent), null, { timeout: 8000 }).catch(() => {});
    const dd = await page.textContent('#pDocs');
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
    ok(vp.name + ': panel de novedades (' + (URL.startsWith('http') ? 'en línea: última revisión' : 'sin conexión: aviso') + ')', URL.startsWith('http') ? /Última revisión/.test(nov) : /sin conexión/.test(nov));
    ok(vp.name + ': últimas resoluciones visibles', (await page.locator('#recientes .listline').count()) === 8);
    await page.evaluate(() => showPage('paises')); await page.evaluate(() => window.scrollTo(0, 1500));
    await page.evaluate(() => showPage('seleccion')); await page.waitForTimeout(150);
    ok(vp.name + ': tras ir de Países (lista larga) a Selección, solo se ve Selección y el scroll vuelve arriba', (await page.evaluate(() => [...document.querySelectorAll('.section')].filter(s => getComputedStyle(s).display !== 'none').map(s => s.id).join())) === 'seleccion' && (await page.evaluate(() => window.scrollY)) === 0 && !/Etapa \d: \d/.test(await page.textContent('#selectionList')));
    await page.evaluate(() => showPage('mecanismos'));
    ok(vp.name + ': otros mecanismos (CERD…CED) visibles', (await page.locator('#mecBody tr').count()) === 25 && /CERD/.test(await page.textContent('#mecBody')));
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
  // Contador de visitas: servido como https falso, con el servicio simulado y sin la marca de automatización
  {
    const fs = require('fs'), root = path.resolve(__dirname, '..');
    const mime = { '.html': 'text/html', '.js': 'application/javascript', '.json': 'application/json' };
    const ctx = await browser.newContext({ timezoneId: 'America/Bogota', locale: 'es-CO' }); const pv = await ctx.newPage();
    await pv.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => false }));
    const llamadas = [];
    await pv.route('https://abacus.jasoncameron.dev/**', r => { llamadas.push(new globalThis.URL(r.request().url()).pathname); r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ value: 1234 }) }); });
    await pv.route('https://atlas.test/**', r => { let p = new globalThis.URL(r.request().url()).pathname; if (p === '/') p = '/index.html'; const f = path.join(root, decodeURIComponent(p)); if (!f.startsWith(root) || !fs.existsSync(f)) return r.fulfill({ status: 404, body: '' }); r.fulfill({ status: 200, contentType: mime[path.extname(f)] || 'application/octet-stream', body: fs.readFileSync(f) }); });
    await pv.goto('https://atlas.test/'); await pv.waitForFunction(() => window.__atlasListo); await pv.waitForTimeout(1500);
    ok('visitas: la barra muestra el total, el país del visitante (Colombia) y sus visitas', (await pv.textContent('#visTotal')).replace(/\D/g, '') === '1234' && /Colombia/.test(await pv.textContent('#visPais')) && (await pv.textContent('#visPaisN')).replace(/\D/g, '') === '1234');
    ok('visitas: la primera visita suma al total y al país; una recarga inmediata no vuelve a sumar', llamadas.filter(x => x.startsWith('/hit/')).length === 2 && llamadas.some(x => x.endsWith('/pais-CO')));
    const antes = llamadas.filter(x => x.startsWith('/hit/')).length; await pv.reload(); await pv.waitForFunction(() => window.__atlasListo); await pv.waitForTimeout(800);
    ok('visitas: la recarga solo consulta (/get), no suma', llamadas.filter(x => x.startsWith('/hit/')).length === antes && llamadas.some(x => x.startsWith('/get/')));
    await pv.screenshot({ path: '/tmp/claude-0/visitas.png', clip: { x: 0, y: 0, width: 1280, height: 120 } }).catch(() => {});
    await ctx.close();
  }
  await browser.close();
  const failed = res.checks.filter(c => !c.ok);
  console.log(JSON.stringify({ ...res, passed: res.checks.length - failed.length, failed: failed.length }, null, 1));
  process.exit(failed.length || res.errors.length ? 1 : 0);
})();
