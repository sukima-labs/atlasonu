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
