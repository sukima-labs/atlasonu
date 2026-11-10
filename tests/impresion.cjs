// T58 · Impresión: cada pantalla del menú, con los estilos de impresión, debe sacar SOLO esa pantalla,
// en claro (texto negro, sin fondo oscuro), sin menú, barra, botones ni avisos, sin desbordar el ancho
// y en pocas hojas A4. Antes de T58 salían las 20 pantallas juntas sobre fondo oscuro (63 a 74 hojas).
// Uso: npm i --no-save playwright && node tests/impresion.cjs
const { chromium } = require('playwright');
const path = require('path');
const INDEX = 'file://' + path.resolve(__dirname, '..', 'index.html');
const MAX_HOJAS = 15;

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  await p.route(/sk-atlas\.pig-mimosa/, r => r.fulfill({ status: 200, contentType: 'application/json',
    headers: { 'access-control-allow-origin': '*' }, body: '{"resultados":[]}' }));
  await p.goto(INDEX);
  await p.waitForTimeout(600);
  const pantallas = await p.evaluate(() => [...document.querySelectorAll('.nav button[data-page]')].map(x => x.dataset.page));
  let fallos = 0;
  const mal = (id, t) => { fallos++; console.log(`✗ imprimir #${id}: ${t}`); };
  for (const id of pantallas) {
    await p.emulateMedia({ media: 'screen' });
    await p.evaluate(i => showPage(i, true), id);
    await p.waitForTimeout(400);
    await p.emulateMedia({ media: 'print' });
    const m = await p.evaluate(() => {
      const visible = e => e && getComputedStyle(e).display !== 'none';
      const secciones = [...document.querySelectorAll('.section')].filter(visible).map(s => s.id);
      const oculto = ['.side', '.appbar', '#arriba', '.menu-hint', '.visbar', '#sgPop'].filter(s => visible(document.querySelector(s)));
      const luz = c => { const m = c.match(/\d+(\.\d+)?/g).map(Number); return m.length > 3 && m[3] === 0 ? 255 : (m[0] + m[1] + m[2]) / 3; };
      return { secciones, oculto, bg: luz(getComputedStyle(document.body).backgroundColor), txt: luz(getComputedStyle(document.querySelector('.main h1')).color),
        panel: [...document.querySelectorAll('.section.visible .panel, .section.visible .detail')].some(e => luz(getComputedStyle(e).backgroundColor) < 200),
        ancho: document.documentElement.scrollWidth - document.documentElement.clientWidth };
    });
    if (m.secciones.length !== 1 || m.secciones[0] !== id) mal(id, `salen ${m.secciones.length} secciones (${m.secciones.slice(0, 3).join(', ')}…)`);
    if (m.oculto.length) mal(id, `se imprimen elementos de la interfaz: ${m.oculto.join(', ')}`);
    if (m.bg < 200) mal(id, 'fondo oscuro');
    if (m.txt > 80) mal(id, 'texto claro sobre papel');
    if (m.panel) mal(id, 'paneles con fondo oscuro');
    if (m.ancho > 4) mal(id, `se desborda ${m.ancho}px a lo ancho`);
    const pdf = await p.pdf({ format: 'A4' });
    const hojas = (pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
    if (hojas > MAX_HOJAS) mal(id, `${hojas} hojas (máximo ${MAX_HOJAS})`);
  }
  // El mapa conserva los colores de la leyenda al imprimir
  await p.emulateMedia({ media: 'screen' });
  await p.evaluate(() => showPage('mapa', true));
  await p.waitForTimeout(800);
  await p.emulateMedia({ media: 'print' });
  const sw = await p.evaluate(() => [...document.querySelectorAll('#mpLeyenda .mp-sw, #mpLeyenda .mp-esc i')].map(e => getComputedStyle(e).backgroundColor));
  if (!sw.length || sw.some(c => /rgba\(0, 0, 0, 0\)|transparent/.test(c))) mal('mapa', 'la leyenda del mapa pierde sus colores al imprimir');
  await b.close();
  if (fallos) { console.log(`impresión: ${fallos} fallos`); process.exit(1); }
  console.log(`impresión: ${pantallas.length} pantallas, una por impresión, en claro y en ≤ ${MAX_HOJAS} hojas`);
})().catch(e => { console.error(e); process.exit(1); });
