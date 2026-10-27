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
    await page.evaluate(() => showPage('recuperar'));
    await page.fill('#recoverQuery', 'E/CN.4/RES/20(XXXVI)'); await page.evaluate(() => recoverDocument());
    ok(vp.name + ': recuperación res. 20 (XXXVI)', (await page.textContent('#recoverResult')).includes('E/1980/13'));
    if (vp.name === 'escritorio') await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_escritorio.png') });
    else await page.screenshot({ path: path.resolve(__dirname, '..', 'audit', 'captura_movil.png') });
    await page.close();
  }
  await browser.close();
  const failed = res.checks.filter(c => !c.ok);
  console.log(JSON.stringify({ ...res, passed: res.checks.length - failed.length, failed: failed.length }, null, 1));
  process.exit(failed.length || res.errors.length ? 1 : 0);
})();
