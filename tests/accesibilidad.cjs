// T27 · Accesibilidad: pasa axe-core (reglas WCAG 2.0, 2.1 y 2.2 A y AA) por cada pantalla del menú, a 390 px
// (celular) y a 1280 px (escritorio), en español y en inglés. Falla si encuentra cualquier incumplimiento.
// Uso: npm i --no-save playwright axe-core && node tests/accesibilidad.cjs
// Lo que axe no puede medir solo (lector de pantalla real, lenguaje claro, lectura fácil) está en docs/ACCESIBILIDAD.md.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const AXE = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const INDEX = 'file://' + path.resolve(__dirname, '..', 'index.html');
const REGLAS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
const CASOS = [
  { ancho: 390, alto: 844, idioma: 'es' },
  { ancho: 1280, alto: 900, idioma: 'es' },
  { ancho: 390, alto: 844, idioma: 'en' },
];

(async () => {
  const b = await chromium.launch();
  let fallos = 0;
  for (const c of CASOS) {
    const ctx = await b.newContext({ viewport: { width: c.ancho, height: c.alto } });
    await ctx.addInitScript(ln => { try { localStorage.setItem('atlas_idioma', ln); } catch (e) {} }, c.idioma);
    const p = await ctx.newPage();
    // La búsqueda en vivo no se toca desde la prueba: respuesta vacía.
    await p.route(/sk-atlas\.pig-mimosa/, r => r.fulfill({ status: 200, contentType: 'application/json',
      headers: { 'access-control-allow-origin': '*' }, body: '{"resultados":[]}' }));
    await p.goto(INDEX);
    await p.waitForTimeout(500);
    await p.addScriptTag({ content: AXE });
    const pantallas = await p.evaluate(() => [...document.querySelectorAll('.nav button[data-page]')].map(x => x.dataset.page));
    for (const id of pantallas) {
      await p.evaluate(i => showPage(i, true), id);
      await p.waitForTimeout(400);
      const v = await p.evaluate(async r => (await axe.run(document, { runOnly: r })).violations
        .map(x => ({ id: x.id, n: x.nodes.length, ej: x.nodes[0].target.join(' ') })), REGLAS);
      for (const x of v) {
        fallos += x.n;
        console.log(`✗ ${c.idioma} ${c.ancho}px #${id}: ${x.id} (${x.n}) p. ej. ${x.ej}`);
      }
    }
    console.log(`${c.idioma} ${c.ancho}px: ${pantallas.length} pantallas revisadas`);
    await ctx.close();
  }
  await b.close();
  if (fallos) { console.log(`accesibilidad: ${fallos} incumplimientos`); process.exit(1); }
  console.log('accesibilidad: 0 incumplimientos WCAG A/AA detectables por axe');
})().catch(e => { console.error(e); process.exit(1); });
