// Fase 6 del plan de diseño (#228) · Web instalable (PWA) con service worker «primero la red».
// Sirve el repositorio por http://localhost bajo /atlasonu/ (como GitHub Pages) con un servidor mínimo y comprueba:
//  1. el manifest es válido y sus iconos cargan con el tamaño que declaran;
//  2. el service worker se registra y controla la página;
//  3. sin red, al recargar se ve la portada con el aviso «Sin conexión: datos del …»;
//  4. con red otra vez, al recargar llega lo NUEVO del servidor (la página y los datos), no la copia: primero la red;
//  5. un idioma guardado (árabe) también funciona sin red desde la primera visita; no se guarda la búsqueda en vivo ni nada de otro dominio, y la copia no se multiplica por el «?v=…»;
//     con el logo de DIGNITYOS y las letras árabes, y sin bajar los diccionarios de los otros idiomas;
//  6. el arranque del celular en «sitio de computador» (marco de la línea 5 de index.html) sigue funcionando, también sin red;
//  7. en el celular, el aviso flotante «Sin conexión.» ocupa el ancho, se cierra (× y Esc) y no tapa el control con el foco.
// Uso: npm i --no-save playwright && node tests/pwa.cjs
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const RAIZ = path.resolve(__dirname, '..');
const BASE = '/atlasonu/';
const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json',
  '.webmanifest': 'application/manifest+json', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.woff2': 'font/woff2', '.css': 'text/css', '.txt': 'text/plain; charset=utf-8', '.atom': 'application/atom+xml' };
let version = 'v1'; // lo que «publica» el servidor; la prueba lo cambia para ver si llega lo nuevo

const servidor = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://localhost');
  if (!u.pathname.startsWith(BASE)) { res.writeHead(302, { location: BASE }); return res.end(); }
  let rel = decodeURIComponent(u.pathname.slice(BASE.length)) || 'index.html';
  const f = path.resolve(RAIZ, rel);
  if (!f.startsWith(RAIZ + path.sep) || f.includes(`${path.sep}node_modules${path.sep}`) || !fs.existsSync(f) || !fs.statSync(f).isFile()) {
    res.writeHead(404); return res.end('no');
  }
  let cuerpo = fs.readFileSync(f);
  if (rel === 'index.html') cuerpo = Buffer.from(cuerpo.toString().replace('<meta charset="UTF-8">', `<meta charset="UTF-8"><meta name="atlas-prueba" content="${version}">`));
  if (rel === 'data/atlas-data.js') cuerpo = Buffer.concat([cuerpo, Buffer.from(`\n;window.__pruebaDatos=${JSON.stringify(version)};`)]);
  res.writeHead(200, { 'content-type': TIPOS[path.extname(f)] || 'application/octet-stream', 'cache-control': 'no-cache' });
  res.end(cuerpo);
});

let fallos = 0;
const ok = (n, c, extra) => { console.log(`${c ? '✓' : '✗'} ${n}${!c && extra ? ' · ' + extra : ''}`); if (!c) fallos++; };
const pngTam = b => b.length > 24 && b.readUInt32BE(0) === 0x89504e47 ? [b.readUInt32BE(16), b.readUInt32BE(20)] : null;

async function preparar(ctx) {
  // La búsqueda en vivo nunca se llama de verdad en las pruebas.
  await ctx.route(/sk-atlas\.pig-mimosa/, r => r.fulfill({ status: 200, contentType: 'application/json',
    headers: { 'access-control-allow-origin': '*' }, body: '{"resultados":[]}' }));
}
const lista = (pg, t = 15000) => pg.waitForFunction(() => window.__atlasListo === true, null, { timeout: t });
const controlada = pg => pg.waitForFunction(() => !!(navigator.serviceWorker && navigator.serviceWorker.controller), null, { timeout: 15000 });

(async () => {
  await new Promise(r => servidor.listen(0, '127.0.0.1', r));
  const ORIGEN = `http://localhost:${servidor.address().port}`;
  const URL0 = ORIGEN + BASE;
  const b = await chromium.launch();
  try {
    // 1 · Manifest e iconos
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    await preparar(ctx);
    const pg = await ctx.newPage();
    const errores = [];
    pg.on('pageerror', e => errores.push(String(e)));
    await pg.goto(URL0);
    await lista(pg);
    const href = await pg.evaluate(() => { const l = document.querySelector('link[rel="manifest"]'); return l && l.href; });
    ok('la página enlaza el manifest con una ruta relativa', !!href && href === URL0 + 'manifest.webmanifest', href);
    const rm = await ctx.request.get(href);
    let m = {};
    try { m = await rm.json(); } catch (e) { /* lo marca la siguiente comprobación */ }
    ok('el manifest se sirve y es JSON válido', rm.ok() && !!m.name);
    ok('manifest: nombre, idioma y modo', m.name === 'ATLAS ONU' && m.short_name === 'ATLAS ONU' && m.lang === 'es' && m.display === 'standalone',
      JSON.stringify({ n: m.name, s: m.short_name, l: m.lang, d: m.display }));
    ok('manifest: start_url y scope relativos (funcionan bajo /atlasonu/)', m.start_url === './' && m.scope === './');
    ok('manifest: colores grafito de la marca', /^#10131c$/i.test(m.background_color || '') && /^#10131c$/i.test(m.theme_color || ''));
    const iconos = m.icons || [];
    const quiere = [['192x192', 'any'], ['512x512', 'any'], ['512x512', 'maskable']];
    for (const [tam, uso] of quiere) {
      const i = iconos.find(x => x.sizes === tam && (x.purpose || 'any').split(' ').includes(uso));
      if (!i) { ok(`icono ${tam} ${uso} declarado`, false); continue; }
      const r = await ctx.request.get(new URL(i.src, href).href);
      const t = r.ok() ? pngTam(await r.body()) : null;
      ok(`icono ${tam} ${uso} carga y mide lo que dice`, !!t && `${t[0]}x${t[1]}` === tam && i.type === 'image/png', `${i.src} → ${t}`);
    }
    ok('meta para iOS: apple-touch-icon y apple-mobile-web-app-*', await pg.evaluate(() => !!document.querySelector('link[rel="apple-touch-icon"]') &&
      document.querySelector('meta[name="apple-mobile-web-app-capable"]')?.content === 'yes' &&
      document.querySelector('meta[name="apple-mobile-web-app-title"]')?.content === 'ATLAS ONU'));

    // 2 · Service worker
    await controlada(pg);
    const sw = await pg.evaluate(async () => { const r = await navigator.serviceWorker.ready; return { scope: r.scope, url: r.active && r.active.scriptURL }; });
    ok('el service worker se registra con el alcance de la web', sw.scope === URL0 && sw.url === URL0 + 'sw.js', JSON.stringify(sw));
    ok('con red no hay aviso de «sin conexión»', await pg.evaluate(() => document.getElementById('sinRedCopia').hidden && document.getElementById('sinRedSolo').hidden));
    // Visita normal ya controlada (guarda la copia de lo que usa la portada) y una búsqueda (no debe guardarse).
    await pg.reload(); await lista(pg);
    await pg.evaluate(() => fetch('https://sk-atlas.pig-mimosa.ts.net/buscar?q=agua').catch(() => {}));
    await pg.waitForTimeout(500);
    const claves = await pg.evaluate(async () => { const c = await caches.open('atlas-onu-v1'); return (await c.keys()).map(r => r.url); });
    ok('la copia guarda la página y los datos', claves.includes(URL0) && claves.includes(URL0 + 'data/atlas-data.js'), claves.slice(0, 8).join(' '));
    ok('nada de otro dominio en la copia (ni la búsqueda en vivo)', claves.every(u => u.startsWith(ORIGEN)), claves.filter(u => !u.startsWith(ORIGEN)).join(' '));
    ok('la copia no se multiplica por el «?v=…» de los datos', claves.every(u => !u.includes('?')), claves.filter(u => u.includes('?')).join(' '));

    // Abrir un archivo de descarga (navegación a un JSON) no puede pisar la copia de la página ni guardarse.
    await pg.goto(URL0 + 'data/catalogo.json');
    await pg.goto(URL0); await lista(pg);
    const tras = await pg.evaluate(async () => { const c = await caches.open('atlas-onu-v1'); const r = await c.match(new URL('./', location.href).href);
      return { html: !!r && /^<!DOCTYPE html>/i.test((await r.text()).trim()), json: !!(await c.match(new URL('data/catalogo.json', location.href).href)) }; });
    ok('abrir una descarga no pisa la copia de la página ni se guarda', tras.html && !tras.json, JSON.stringify(tras));

    // 3 · Sin red
    await ctx.setOffline(true);
    await pg.reload(); await lista(pg);
    await pg.waitForTimeout(3000); // el navegador puede recolocar el desplazamiento al terminar de cargar: se mira después
    const sinRed = await pg.evaluate(() => ({ v: document.querySelector('meta[name="atlas-prueba"]')?.content, d: window.__pruebaDatos,
      aviso: !document.getElementById('sinRedCopia').hidden, solo: !document.getElementById('sinRedSolo').hidden, txt: document.getElementById('sinRedCopia').textContent,
      arriba: document.getElementById('sinRedCopia').getBoundingClientRect().top, y: scrollY, inicio: document.getElementById('inicio')?.classList.contains('visible') }));
    ok('sin red, la portada se abre desde la copia', sinRed.inicio && sinRed.v === 'v1' && sinRed.d === 'v1', JSON.stringify(sinRed));
    ok('sin red, aviso «Sin conexión: datos del <fecha>»', sinRed.aviso && /Sin conexión: datos del \d{1,2} de [a-z]+ de \d{4}\./.test(sinRed.txt), sinRed.txt);
    ok('sin red, el aviso se ve entero arriba (sin anclaje que lo saque de la pantalla)', sinRed.arriba >= 0 && sinRed.y === 0, JSON.stringify({ top: sinRed.arriba, y: sinRed.y }));
    ok('sin red y con la copia, no sale además el aviso flotante', !sinRed.solo);
    ok('sin red, el punto «en vivo» del contador se apaga', await pg.evaluate(() => document.getElementById('visBar').classList.contains('sin-red-activo')));
    await pg.screenshot({ path: process.env.PWA_CAPTURA || path.join(require('os').tmpdir(), 'atlas-pwa-sin-red.png') }).catch(() => {});

    // 4 · Con red otra vez y una versión nueva publicada: debe llegar la nueva, no la copia
    version = 'v2';
    await ctx.setOffline(false);
    await pg.reload(); await lista(pg);
    const conRed = await pg.evaluate(() => ({ v: document.querySelector('meta[name="atlas-prueba"]')?.content, d: window.__pruebaDatos, aviso: !document.getElementById('sinRedCopia').hidden || !document.getElementById('sinRedSolo').hidden }));
    ok('con red, llega la página nueva (primero la red)', conRed.v === 'v2', JSON.stringify(conRed));
    ok('con red, llegan los datos nuevos', conRed.d === 'v2', JSON.stringify(conRed));
    ok('con red, sin aviso', !conRed.aviso);
    ok('con red, el punto «en vivo» vuelve', await pg.evaluate(() => !document.getElementById('visBar').classList.contains('sin-red-activo')));
    // Y la copia queda al día para la próxima vez sin red.
    await ctx.setOffline(true);
    await pg.reload(); await lista(pg);
    ok('la copia se actualizó con lo nuevo', (await pg.evaluate(() => window.__pruebaDatos)) === 'v2');
    await ctx.setOffline(false);
    // Se va la red con la página ya abierta desde la red: no es la copia, así que sale el aviso flotante y no «la copia guardada».
    await pg.reload(); await lista(pg);
    await ctx.setOffline(true);
    await pg.waitForFunction(() => !document.getElementById('sinRedSolo').hidden, null, { timeout: 5000 }).catch(() => {});
    const aMedias = await pg.evaluate(() => ({ solo: !document.getElementById('sinRedSolo').hidden, copia: !document.getElementById('sinRedCopia').hidden,
      fijo: getComputedStyle(document.getElementById('sinRedSolo')).position, vivo: document.getElementById('sinRed').getAttribute('role') }));
    ok('se va la red con la página abierta: aviso flotante y no «copia guardada»', aMedias.solo && !aMedias.copia && aMedias.fijo === 'fixed', JSON.stringify(aMedias));
    ok('el aviso está dentro de una región «status» que siempre existe', aMedias.vivo === 'status');
    await ctx.setOffline(false);
    await pg.waitForFunction(() => document.getElementById('sinRedSolo').hidden, null, { timeout: 5000 }).catch(() => {});
    ok('vuelve la red: se quita el aviso flotante', await pg.evaluate(() => document.getElementById('sinRedSolo').hidden));
    ok('sin errores de JavaScript', errores.length === 0, errores.slice(0, 3).join(' | '));
    await ctx.close();

    // 5 · Idioma guardado (árabe) en la PRIMERA visita: su diccionario se baja antes de que exista el service worker; la copia
    // tiene que tenerlo igual, o sin red la web saldría en español y de izquierda a derecha.
    const ca = await b.newContext({ viewport: { width: 1440, height: 900 } });
    await preparar(ca);
    await ca.addInitScript(() => { try { localStorage.setItem('atlas_idioma', 'ar'); } catch (e) {} });
    const pa = await ca.newPage();
    await pa.goto(URL0); await lista(pa);
    await controlada(pa);
    await pa.evaluate(async () => { const r = await navigator.serviceWorker.ready; if (r.installing || r.waiting) await new Promise(ok => setTimeout(ok, 1500)); });
    await pa.waitForFunction(async () => !!(await (await caches.open('atlas-onu-v1')).match(new URL('data/idiomas/ar.js', location.href).href)), null, { timeout: 15000 }).catch(() => {});
    await ca.setOffline(true);
    await pa.reload(); await lista(pa);
    await pa.waitForFunction(() => !document.getElementById('sinRedCopia').hidden, null, { timeout: 5000 }).catch(() => {});
    await pa.waitForTimeout(3000); // el navegador puede recolocar el desplazamiento al terminar de cargar: se mira después
    const ar = await pa.evaluate(() => ({ y: scrollY, dir: document.documentElement.dir, txt: document.getElementById('sinRedCopia').textContent,
      top: document.getElementById('sinRedCopia').getBoundingClientRect().top, visible: !document.getElementById('sinRedCopia').hidden }));
    ok('árabe en la primera visita, sin red: de derecha a izquierda y aviso en árabe', ar.dir === 'rtl' && ar.visible && /لا يوجد اتصال/.test(ar.txt), JSON.stringify(ar));
    ok('árabe sin red: el aviso se ve entero', ar.top >= 0, String(ar.top));
    ok('árabe sin red: la fecha va escrita entera, no en ISO', /2\d{3}/.test(ar.txt) && !/\d{4}-\d\d-\d\d/.test(ar.txt), ar.txt);
    // Lo que pide la primera visita antes de que exista el service worker (logo de DIGNITYOS, letras árabes) está en la copia.
    await pa.evaluate(() => showPage('defensores'));
    await pa.waitForTimeout(500);
    const imgs = await pa.evaluate(() => [...document.querySelectorAll('#defensores img, .side img, .franja-dig img')]
      .map(i => ({ src: i.getAttribute('src'), w: i.complete ? i.naturalWidth : 0 })));
    ok('sin red, DIGNITYOS y el menú muestran el logo (ninguna imagen rota)', imgs.length > 0 && imgs.every(i => i.w > 0), JSON.stringify(imgs.filter(i => !i.w)));
    const letras = await pa.evaluate(async () => { await document.fonts.ready;
      return [...document.fonts].filter(f => f.family.replace(/"/g, '') === 'DejaVu Sans' && f.unicodeRange.includes('U+600')).map(f => f.status); });
    ok('sin red, las letras árabes salen de la copia', letras.length > 0 && !letras.includes('error'), JSON.stringify(letras));
    const otros = await pa.evaluate(async () => { const c = await caches.open('atlas-onu-v1'); const f = [];
      for (const l of ['en', 'fr', 'zh', 'ru']) if (await c.match(new URL(`data/idiomas/${l}.js`, location.href).href)) f.push(l);
      return f; });
    ok('solo se guarda el diccionario del idioma que se usa (ahorra datos)', otros.length === 0, otros.join(' '));
    // Las pantallas de datos que se cargan aparte (mapa, noticias…) están en la copia aunque no se hayan abierto con red.
    const aparte = await pa.evaluate(async () => { const c = await caches.open('atlas-onu-v1'); const f = [];
      for (const r of ['data/mapa.js', 'data/noticias.js', 'data/epu.js', 'data/conflictos.js', 'data/jurisprudencia.js', 'data/comunicaciones.js'])
        if (!(await c.match(new URL(r, location.href).href))) f.push(r);
      return f; });
    ok('la copia trae ya el mapa, las noticias y los otros datos que se cargan aparte', aparte.length === 0, aparte.join(' '));
    await ca.close();

    // 6 · Celular en «sitio de computador»: la página se abre dentro del marco (#188) y el service worker no lo rompe
    const cel = await b.newContext({ viewport: { width: 980, height: 1800 }, screen: { width: 412, height: 915 }, hasTouch: true, isMobile: false });
    await preparar(cel);
    const pc = await cel.newPage();
    await pc.goto(URL0);
    const marco = async () => { await pc.waitForSelector('#marcoMovil', { timeout: 10000 }); const f = await (await pc.$('#marcoMovil')).contentFrame(); await lista(f); return f; };
    let f = await marco();
    ok('celular en modo computador: la web se abre en el marco', /[?&]movil=1/.test(f.url()), f.url());
    await f.waitForFunction(() => !!navigator.serviceWorker.controller, null, { timeout: 15000 });
    await pc.reload(); f = await marco();
    await cel.setOffline(true);
    await pc.reload(); f = await marco();
    ok('celular en modo computador, sin red: marco y aviso', await f.evaluate(() => !document.getElementById('sinRedCopia').hidden && document.getElementById('inicio').classList.contains('visible')));
    await cel.close();

    // 7 · Celular (Pixel 7): se va la red con la página abierta
    const { devices } = require('playwright');
    const px = await b.newContext({ ...devices['Pixel 7'] });
    await preparar(px);
    const pp = await px.newPage();
    await pp.goto(URL0); await lista(pp);
    await px.setOffline(true);
    await pp.waitForFunction(() => !document.getElementById('sinRedSolo').hidden, null, { timeout: 5000 }).catch(() => {});
    const caja = await pp.evaluate(() => { const r = document.getElementById('sinRedSolo').getBoundingClientRect(); return { l: r.left, r: innerWidth - r.right, h: r.height }; });
    ok('celular: el aviso flotante ocupa el ancho (16 px a cada lado)', Math.abs(caja.l - 16) < 2 && Math.abs(caja.r - 16) < 2, JSON.stringify(caja));
    let tapados = [];
    for (let i = 0; i < 100; i++) {
      await pp.keyboard.press('Tab');
      const t = await pp.evaluate(() => { const a = document.activeElement, s = document.getElementById('sinRedSolo');
        if (!a || a === document.body || s.hidden || s.contains(a)) return null;
        const r = a.getBoundingClientRect(), b = s.getBoundingClientRect();
        return r.width && r.top >= b.top && r.bottom <= b.bottom && r.left >= b.left && r.right <= b.right ? (a.textContent || a.id).trim().slice(0, 30) : null; });
      if (t) tapados.push(t);
    }
    ok('celular: el aviso no tapa el control con el foco (WCAG 2.4.11)', tapados.length === 0, tapados.join(' | '));
    await pp.click('#sinRedSolo .sin-red-x');
    ok('celular: el aviso se cierra con ×', await pp.evaluate(() => document.getElementById('sinRedSolo').hidden));
    await px.setOffline(false); await pp.waitForTimeout(200);
    await px.setOffline(true);
    await pp.waitForFunction(() => !document.getElementById('sinRedSolo').hidden, null, { timeout: 5000 }).catch(() => {});
    ok('celular: en el siguiente corte vuelve a salir', await pp.evaluate(() => !document.getElementById('sinRedSolo').hidden));
    await pp.keyboard.press('Escape');
    ok('celular: también se cierra con Esc', await pp.evaluate(() => document.getElementById('sinRedSolo').hidden));
    await px.close();
  } catch (e) {
    ok('la prueba terminó sin excepciones', false, e && e.stack || String(e));
  } finally {
    await b.close();
    servidor.close();
  }
  console.log(fallos ? `\n${fallos} fallo(s)` : '\nPWA: todo bien');
  process.exit(fallos ? 1 : 0);
})();
