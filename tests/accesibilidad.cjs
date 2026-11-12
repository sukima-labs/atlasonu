// T27 · Accesibilidad: pasa axe-core (reglas WCAG 2.0, 2.1 y 2.2 A y AA) por cada pantalla del menú, a 390 px
// (celular) y a 1280 px (escritorio), en español, en inglés y en árabe (de derecha a izquierda). Falla si encuentra cualquier incumplimiento.
// #228 (T85 fase 3): cada pantalla se mide en los DOS modos, oscuro y claro (se cambia con atlasTema sin recargar).
// Uso: npm i --no-save playwright axe-core && node tests/accesibilidad.cjs
// Lo que axe no puede medir solo (lector de pantalla real, lenguaje claro, lectura fácil) está en docs/ACCESIBILIDAD.md.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const AXE = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const INDEX = 'file://' + path.resolve(__dirname, '..', 'index.html');
const REGLAS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
const MODOS = ['dark', 'light'];
const CASOS = [
  { ancho: 390, alto: 844, idioma: 'es' },
  { ancho: 1280, alto: 900, idioma: 'es' },
  { ancho: 390, alto: 844, idioma: 'en' },
  { ancho: 390, alto: 844, idioma: 'ar' }, // T66: de derecha a izquierda
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
    if (c.idioma === 'ar' && await p.evaluate(() => document.documentElement.dir) !== 'rtl') { fallos++; console.log('✗ ar: la página no está de derecha a izquierda'); }
    const pantallas = await p.evaluate(() => [...document.querySelectorAll('.main .section')].map(x => x.id));
    for (const id of pantallas) {
      await p.evaluate(i => { showPage(i, true); document.querySelectorAll('details.lf').forEach(d => { d.open = true; }); }, id); // T65: la lectura fácil se mide abierta
      await p.waitForTimeout(400);
      for (const modo of MODOS) {
        await p.evaluate(m => { atlasTema(m); }, modo);
        if (await p.evaluate(() => document.documentElement.dataset.theme) !== modo) { fallos++; console.log(`✗ ${c.idioma} ${c.ancho}px #${id}: no se pudo poner el modo ${modo}`); }
        // Dos fotogramas tras el cambio de modo. Ningún color ni fondo lleva transición (solo transform, borde y sombra): si se añadiera una, axe podría medir a medias.
        await p.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
        const v = await p.evaluate(async r => (await axe.run(document, { runOnly: r })).violations
          .map(x => ({ id: x.id, n: x.nodes.length, ej: x.nodes[0].target.join(' ') })), REGLAS);
        for (const x of v) {
          fallos += x.n;
          console.log(`✗ ${c.idioma} ${c.ancho}px ${modo} #${id}: ${x.id} (${x.n}) p. ej. ${x.ej}`);
        }
        if (id === 'mapa') { // las capas con selector propio (conflictos por año, EPU por ciclo) también se miden
          for (const capa of ['conflictos', 'epu']) {
            await p.evaluate(k => { document.getElementById('mpCapa').value = k; mpCapaCambia(); }, capa);
            await p.waitForTimeout(700);
            const w = await p.evaluate(async r => (await axe.run(document, { runOnly: r })).violations.map(x => ({ id: x.id, n: x.nodes.length, ej: x.nodes[0].target.join(' ') })), REGLAS);
            for (const x of w) { fallos += x.n; console.log(`✗ ${c.idioma} ${c.ancho}px ${modo} #mapa capa ${capa}: ${x.id} (${x.n}) p. ej. ${x.ej}`); }
          }
          await p.evaluate(() => { document.getElementById('mpCapa').value = 'basicos'; mpCapaCambia(); });
        }
      }
    }
    // Gráfica de votos de un país (barras y marcas de hitos) y logotipo de Sukima: axe no mide el SVG, así que se comprueba aparte.
    await p.evaluate(() => irPais('COL'));
    await p.waitForFunction(() => document.querySelector('#pVotos svg'), null, { timeout: 8000 }).catch(() => { fallos++; console.log(`✗ ${c.idioma} ${c.ancho}px: no apareció la gráfica de votos de Colombia`); });
    for (const vista of ['barras', 'linea']) {
    await p.evaluate(v => votosCambia(v), vista);
    await p.waitForTimeout(500);
    for (const modo of MODOS) {
      await p.evaluate(m => { atlasTema(m); }, modo);
      await p.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
      const v = await p.evaluate(async r => (await axe.run(document, { runOnly: r })).violations.map(x => ({ id: x.id, n: x.nodes.length, ej: x.nodes[0].target.join(' ') })), REGLAS);
      for (const x of v) { fallos += x.n; console.log(`✗ ${c.idioma} ${c.ancho}px ${modo} país COL votos ${vista}: ${x.id} (${x.n}) p. ej. ${x.ej}`); }
      const malos = await p.evaluate(() => {
        const rgb = t => { const m = t.match(/[\d.]+/g); return m ? m.slice(0, 4).map(Number) : null; };
        const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
        const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
        const fondo = e => { for (let n = e.parentElement; n; n = n.parentElement) { const c = rgb(getComputedStyle(n).backgroundColor); if (c && (c.length < 4 || c[3] > 0.5)) return c; } return rgb(getComputedStyle(document.body).backgroundColor); };
        const out = [];
        // Logotipo de Sukima (menú lateral y pie): objeto gráfico que es todo el contenido de un enlace, 3:1 como mínimo
        document.querySelectorAll('.isotipo-sk').forEach(e => { const r = ratio(rgb(getComputedStyle(e).fill), fondo(e)); if (r < 3) out.push('logotipo ' + r.toFixed(2)); });
        // Texto de las marcas de hitos (A, B, C) de la gráfica de votos: 4,5:1
        document.querySelectorAll('#pVotos svg text').forEach(e => { if (!/grafica-marca/.test(e.getAttribute('style') || '')) return; const r = ratio(rgb(getComputedStyle(e).fill), fondo(e)); if (r < 4.5) out.push('hito ' + e.textContent + ' ' + r.toFixed(2)); });
        return out;
      });
      for (const x of malos) { fallos++; console.log(`✗ ${c.idioma} ${c.ancho}px ${modo} votos ${vista}: contraste bajo, ${x}`); }
    }
    }
    console.log(`${c.idioma} ${c.ancho}px: ${pantallas.length} pantallas y la gráfica de votos revisadas en modo oscuro y claro`);
    await ctx.close();
  }
  await b.close();
  if (fallos) { console.log(`accesibilidad: ${fallos} incumplimientos`); process.exit(1); }
  console.log('accesibilidad: 0 incumplimientos WCAG A/AA detectables por axe, en modo oscuro y en claro');
})().catch(e => { console.error(e); process.exit(1); });
