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
    ok(vp.name + ': sección Países visible con 62 filas', await page.isVisible('#paises') && (await page.locator('#pBody tr').count()) === 62);
    await page.fill('#pQ', 'siria'); await page.waitForTimeout(250);
    ok(vp.name + ': buscar «siria» muestra mandato y comisión', /Siria/.test(await page.textContent('#pBody')) && /S-17\/1/.test(await page.textContent('#pBody')) && (await page.locator('#pBody tr').count()) === 1);
    await page.fill('#pQ', ''); await page.selectOption('#pSel', 'COL'); await page.waitForTimeout(250);
    ok(vp.name + ': elegir Colombia lista 6 titulares y el aviso de independencia', (await page.locator('#pBody a').count()) === 6 && /no representan a su Estado/.test(await page.textContent('#pOut')));
    if (vp.name === 'escritorio') await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_paises.png') });
    await page.fill('#pTema', 'tortura'); await page.waitForTimeout(250);
    ok(vp.name + ': país + tema «tortura» → lista corta de mandatos temáticos aplicables', /cualquier Estado/.test(await page.textContent('#pTemas')) && (await page.locator('#pTemas tbody tr').count()) < 10 && /tortura/i.test(await page.textContent('#pTemas')));
    await page.fill('#pTema', '');
    ok(vp.name + ': sin tema → los 44 mandatos temáticos aplicables', (await page.locator('#pTemas tbody tr').count()) === 44);
    await page.evaluate(() => showPage('inicio')); await page.selectOption('#guiadaSel', { index: 4 }); await page.selectOption('#guiadaPais', 'COL'); await page.getByRole('button', { name: 'Ver mandatos' }).click(); await page.waitForTimeout(300);
    ok(vp.name + ': búsqueda guiada con país (Colombia + agua/alimentación…) abre Países con mandatos aplicables', await page.isVisible('#paises') && /Colombia/.test(await page.textContent('#pTemas')) && (await page.locator('#pTemas tbody tr').count()) > 0);
    if (vp.name === 'escritorio') { await page.evaluate(() => document.getElementById('pTemas').scrollIntoView()); await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_pais_temas.png') }); }
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
  await browser.close();
  const failed = res.checks.filter(c => !c.ok);
  console.log(JSON.stringify({ ...res, passed: res.checks.length - failed.length, failed: failed.length }, null, 1));
  process.exit(failed.length || res.errors.length ? 1 : 0);
})();
