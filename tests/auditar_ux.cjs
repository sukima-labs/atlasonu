// Mide a 390 px (celular táctil) cada pantalla del menú: desborde lateral, controles de menos de 44 px fuera del texto corrido,
// texto de menos de 13 px y largo de la página en pantallas. Uso: node tests/auditar_ux.cjs [--comprobar]
// Con --comprobar falla (código 1) si alguna pantalla no cumple las metas de tests/metas_ux.cjs (P9, #226).
// Informe y tabla de antes y después en docs/INFORME_UX.md.
const { chromium } = require('playwright');
const { METAS, medirPantalla, cumple } = require('./metas_ux.cjs');
const ruta = require('path').resolve(__dirname, '..', 'index.html');
const comprobar = process.argv.includes('--comprobar');
const LARGO_FICHA = 9; // ficha de país de Colombia en el celular: 48,9 pantallas el 12-11-2026; 8,8 con los bloques largos plegados (#285, T91)
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
  // La ficha de un país (Colombia) cumple como las demás (#285, T91: bloques plegados; #286, T92: enlaces y desplegables de 44 px,
  // letra de las gráficas de votos a 13,5 px en pantalla). Se mide plegada (largo) y otra vez con todos los bloques abiertos.
  await p.evaluate(() => irPais('COL')); await p.waitForTimeout(1500);
  const f = await p.evaluate(medirPantalla, METAS);
  await p.evaluate(() => document.querySelectorAll('#paises details.pf-pleg').forEach(d => { d.open = true })); await p.waitForTimeout(300);
  const fa = await p.evaluate(medirPantalla, METAS);
  const fichaMal = f.largo > LARGO_FICHA || f.ancho > f.W + 1 || f.controles || f.textos || fa.controles || fa.textos || fa.ancho > fa.W + 1;
  const ej = x => (x.controles ? ' ' + x.controlesEj.join(' | ') : '') + (x.textos ? ' ' + x.textosEj.join(' | ') : '');
  console.log(`${fichaMal ? '✗' : '✓'} ficha COL     largo ${String(f.largo).padStart(4)} pantallas (tope ${LARGO_FICHA}) · ancho ${f.ancho}/${f.W} · controles < ${METAS.control} px: ${f.controles} (con los bloques abiertos: ${fa.controles}) · texto < ${METAS.texto} px: ${f.textos} (abiertos: ${fa.textos})${ej(f)}${ej(fa)}`);
  if (fichaMal) malas++;
  await b.close();
  console.log(`${pantallas.length} pantallas medidas a 390 px; ${malas ? malas + ' no cumplen' : 'todas cumplen'} las metas (controles ≥ ${METAS.control} px, texto ≥ ${METAS.texto} px, ≤ ${METAS.largo} pantallas de alto, sin desborde lateral)`);
  if (comprobar && malas) process.exit(1);
})();
