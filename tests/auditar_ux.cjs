// Mide a 390 px (celular táctil) cada pantalla del menú: desborde lateral, controles de menos de 44 px fuera del texto corrido,
// texto de menos de 13 px y largo de la página en pantallas. Uso: node tests/auditar_ux.cjs [--comprobar]
// Con --comprobar falla (código 1) si alguna pantalla no cumple las metas de tests/metas_ux.cjs (P9, #226).
// Informe y tabla de antes y después en docs/INFORME_UX.md.
const { chromium } = require('playwright');
const { METAS, medirPantalla, cumple } = require('./metas_ux.cjs');
const ruta = require('path').resolve(__dirname, '..', 'index.html');
const comprobar = process.argv.includes('--comprobar');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
  await ctx.route(/sk-atlas\.pig-mimosa/, r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: '{"resultados":[]}' }));
  const p = await ctx.newPage();
  await p.goto('file://' + ruta + '?movil=1');
  await p.waitForFunction(() => window.__atlasListo, null, { timeout: 20000 }).catch(() => {});
  const pantallas = await p.evaluate(() => [...document.querySelectorAll('.main .section')].map(x => x.id));
  let malas = 0;
  for (const id of pantallas) {
    await p.evaluate(i => showPage(i), id); await p.waitForTimeout(300);
    const m = await p.evaluate(medirPantalla, METAS);
    const bien = cumple(m);
    if (!bien) malas++;
    console.log(`${bien ? '✓' : '✗'} ${id.padEnd(13)} largo ${String(m.largo).padStart(4)} pantallas · ancho ${m.ancho}/${m.W} · controles < ${METAS.control} px: ${m.controles}${m.controles ? ' ' + m.controlesEj.join(' | ') : ''} · texto < ${METAS.texto} px: ${m.textos}${m.textos ? ' ' + m.textosEj.join(' | ') : ''}`);
  }
  await b.close();
  console.log(`${pantallas.length} pantallas medidas a 390 px; ${malas ? malas + ' no cumplen' : 'todas cumplen'} las metas (controles ≥ ${METAS.control} px, texto ≥ ${METAS.texto} px, ≤ ${METAS.largo} pantallas de alto, sin desborde lateral)`);
  if (comprobar && malas) process.exit(1);
})();
