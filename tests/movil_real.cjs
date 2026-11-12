// Prueba de celular contra la web PUBLICADA y la búsqueda en vivo REAL (sin simular nada).
// Cierra las confirmaciones «en celular real» de la cola (T51: T12, T14, T17, T19, T28).
// Emula teléfonos con pantalla táctil, agente de usuario de móvil y densidad de píxeles reales.
// Uso: node tests/movil_real.cjs   (ATLAS_URL cambia la dirección; por defecto, la web publicada)
// No va en la CI de cada PR porque depende de internet; corre a mano o cada semana (.github/workflows/movil.yml).
const { chromium, devices } = require('playwright');
const URL = process.env.ATLAS_URL || 'https://sukimalabs.com/atlasonu/';
const res = { url: URL, checks: [], errors: [] };
const ok = (n, c, extra) => { res.checks.push({ n, ok: !!c, ...(extra ? { extra } : {}) }); };
const reposo = async pg => { let a = -1; for (let i = 0; i < 40; i++) { await pg.waitForTimeout(150); const y = await pg.evaluate(() => scrollY); if (y === a) return; a = y; } };
(async () => {
  const browser = await chromium.launch({ channel: 'chromium' }); // Chromium completo: el «headless shell» no hace caso al pellizco de zoom
  for (const nom of ['Pixel 7', 'Galaxy S9+', 'iPhone 13']) {
    const ctx = await browser.newContext({ ...devices[nom], locale: 'es-CO', timezoneId: 'America/Bogota' });
    const pg = await ctx.newPage();
    try {
    pg.on('pageerror', e => res.errors.push(nom + ': ' + e.message));
    const { width: w, height: h } = devices[nom].viewport;
    await pg.goto(URL); await pg.waitForFunction(() => window.__atlasListo);
    const ancho = async () => pg.evaluate(() => { const fuera = []; const W = document.documentElement.clientWidth; document.querySelectorAll('body *').forEach(e => { const r = e.getBoundingClientRect(); if (r.width && r.right > screen.width + 0.5 && !e.closest('.tablewrap,[style*="overflow"]') && e.offsetParent) fuera.push((e.id ? '#' + e.id : e.tagName.toLowerCase() + '.' + String(e.className).trim().replace(/ +/g, '.')) + ' (' + Math.round(r.left) + '→' + Math.round(r.right) + ') «' + e.textContent.trim().slice(0, 25) + '»'); }); return { pantalla: screen.width, pagina: innerWidth, fuera: fuera.slice(0, 8) }; });
    const a0 = await ancho();
    ok(nom + ': la página mide lo mismo que la pantalla (el móvil no la encoge)', a0.pagina === a0.pantalla && a0.fuera.length === 0, a0);

    // T12: búsqueda en vivo real desde el celular, escribiendo y tocando «Buscar»
    await pg.tap('#quick'); await pg.keyboard.type('desertification'); await pg.tap('.hero-search button.primary');
    const t0 = Date.now();
    const vivo = await pg.waitForFunction(() => { const m = document.body.innerText.match(/Biblioteca Digital ONU (?:tiene \((\d+)\)|devolvieron resultados)/); return m ? (m[1] ? +m[1] : -1) : 0; }, null, { timeout: 15000, polling: 250 }).then(r => r.jsonValue()).catch(() => 0);
    ok(nom + ': T12 «desertification» trae resultados en vivo de la Biblioteca Digital ONU', vivo > 0, { resultados: vivo, segundos: (Date.now() - t0) / 1000 });

    // T14 + T28: el menú abre, se desliza con el dedo hasta el final y el fondo no se mueve
    await pg.evaluate(() => scrollTo({ top: 0, behavior: 'instant' }));
    await pg.tap('#burger'); await pg.waitForTimeout(400);
    const cdp = await ctx.newCDPSession(pg);
    const desliza = async (x, y0, y1) => { await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y: y0 }] }); for (let i = 1; i <= 12; i++) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y: y0 + (y1 - y0) * i / 12 }] }); await pg.waitForTimeout(16); } await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await pg.waitForTimeout(250); };
    for (let i = 0; i < 5; i++) await desliza(Math.min(140, w / 3), h - 90, 90);
    const fin = await pg.evaluate(() => { const s = document.getElementById('side'), b = [...s.querySelectorAll('.nav button')].pop(), r = b.getBoundingClientRect(); return { fin: s.scrollTop + s.clientHeight >= s.scrollHeight - 2, ultimo: b.textContent.trim(), visible: r.top >= 0 && r.bottom <= innerHeight, fondo: Math.round(scrollY) }; });
    ok(nom + ': T14/T28 el menú se desliza con el dedo hasta su último botón y el fondo no se mueve', fin.fin && fin.visible && fin.fondo === 0, fin);

    // T17: con el menú abierto, pellizco real de zoom 2× hacia la derecha; el menú sigue la zona visible y no queda cortado
    await pg.evaluate(() => { document.getElementById('side').scrollTop = 0; });
    // Zoom 2× y la zona visible movida a la derecha, como quien amplía con dos dedos y arrastra. El navegador sin pantalla de la CI
    // no hace caso al pellizco sintético, así que el zoom se fija con CDP y la zona visible se mueve con la rueda horizontal.
    await cdp.send('Input.synthesizePinchGesture', { x: w - 30, y: h / 2, scaleFactor: 2, gestureSourceType: 'touch' }); await pg.waitForTimeout(400);
    if (await pg.evaluate(() => visualViewport.scale < 1.5)) { await cdp.send('Emulation.setPageScaleFactor', { pageScaleFactor: 2 }); await pg.waitForTimeout(300); await cdp.send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: w - 20, y: h / 2, deltaX: w, deltaY: 0 }); await pg.waitForTimeout(600); }
    const z = await pg.evaluate(() => { const v = visualViewport, s = document.getElementById('side').getBoundingClientRect(); return { escala: +v.scale.toFixed(2), vistaIzq: Math.round(v.offsetLeft), menuIzq: Math.round(s.left), menuArriba: Math.round(s.top), vistaArriba: Math.round(v.offsetTop) }; });
    ok(nom + ': T17 con zoom 2× el menú empieza donde empieza la zona visible (no queda cortado)', z.escala >= 1.5 && z.vistaIzq > 0 && Math.abs(z.menuIzq - z.vistaIzq) <= 2 && Math.abs(z.menuArriba - z.vistaArriba) <= 2, z);
    await cdp.send('Emulation.setPageScaleFactor', { pageScaleFactor: 1 }); await pg.waitForTimeout(400);
    await pg.tap('.nav button[data-page="paises"]'); await pg.waitForTimeout(400);
    ok(nom + ': tocar una opción cierra el menú y abre la pantalla', !(await pg.isVisible('#side')) && (await pg.isVisible('#paises')));

    // T19: ficha de país con «Qué quieres ver», saltos con el dedo y «↑ Qué quieres ver»
    await pg.tap('#pQ'); await pg.keyboard.type('Colombia'); await pg.getByRole('button', { name: 'Buscar' }).first().tap(); await pg.waitForTimeout(800);
    const saltos = await pg.locator('#pNav button[onclick^="irSeccion"]').count();
    // Toque con el dedo en el centro del botón, como en un teléfono (sin forzar): se anota qué hay debajo del dedo
    const epuBtn = pg.locator('#pNav button', { hasText: 'EPU' }); await epuBtn.scrollIntoViewIfNeeded(); await reposo(pg);
    const bajo = await epuBtn.evaluate(b => { const r = b.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2, e = document.elementFromPoint(x, y); return { x: Math.round(x), y: Math.round(y), alto: innerHeight, ancho: innerWidth, debajo: e ? (e.id ? '#' + e.id : e.tagName.toLowerCase() + '.' + e.className) + ' «' + e.textContent.trim().slice(0, 30) + '»' : null, esElBoton: e === b || b.contains(e) }; });
    ok(nom + ': T19 el botón «EPU» de la ficha se puede tocar (nada lo tapa)', bajo.esElBoton, bajo);
    const y0 = await pg.evaluate(() => Math.round(scrollY));
    await pg.touchscreen.tap(bajo.x, bajo.y);
    const traza = []; for (let i = 0; i < 25; i++) { await pg.waitForTimeout(100); traza.push(await pg.evaluate(() => Math.round(scrollY))); }
    bajo.scrollAntes = y0; bajo.traza = traza.join(','); bajo.altoDoc = await pg.evaluate(() => document.documentElement.scrollHeight); bajo.epuAbs = await pg.evaluate(() => Math.round(document.getElementById('ps-epu').getBoundingClientRect().top + scrollY));
    res.checks.push({ n: nom + ': (diagnóstico del salto a EPU)', ok: true, extra: bajo });
    const epu = await pg.evaluate(() => Math.round(document.getElementById('ps-epu').getBoundingClientRect().top));
    const vuelve = (await pg.isVisible('#pTop')) && (await pg.tap('#pTop'), await reposo(pg), await pg.evaluate(() => Math.abs(document.getElementById('pNav').getBoundingClientRect().top) < 90));
    ok(nom + ': T19 la ficha de Colombia tiene 10 saltos, «EPU» lleva a su bloque y «↑ Qué quieres ver» vuelve', saltos === 10 && epu >= -5 && epu < h * 0.5 && vuelve, { saltos, epu });
    const a1 = await ancho();
    ok(nom + ': con la ficha abierta la página sigue midiendo lo que la pantalla', a1.pagina === a1.pantalla && a1.fuera.length === 0, a1);
    // T61: comparador tocado con el dedo desde la ficha de Colombia
    const cmpBtn = pg.locator('#pNav button[onclick^="compararCon"]'); await cmpBtn.scrollIntoViewIfNeeded(); await reposo(pg); await cmpBtn.tap(); await reposo(pg);
    await pg.selectOption('#cmpB', 'ESP'); await pg.waitForTimeout(300);
    await pg.locator('#cmpDif').scrollIntoViewIfNeeded(); await pg.tap('#cmpDif'); await pg.waitForTimeout(300);
    const cmp = await pg.evaluate(() => ({ abierto: document.getElementById('pComp').open, a: document.getElementById('cmpA').value, filas: document.querySelectorAll('#cmpOut tbody tr').length, dif: document.querySelectorAll('#cmpOut tbody tr.cmp-dif').length, etiquetas: document.querySelectorAll('#cmpOut td[data-label="España"]').length, pulsado: document.getElementById('cmpDif').getAttribute('aria-pressed') }));
    const a2 = await ancho();
    ok(nom + ': T61 «Comparar con otro país» con el dedo: Colombia frente a España, solo lo que cambia, en tarjetas y sin desbordar', cmp.abierto && cmp.a === 'COL' && cmp.filas > 0 && cmp.filas === cmp.dif && cmp.etiquetas === cmp.filas && cmp.pulsado === 'true' && a2.pagina === a2.pantalla && a2.fuera.length === 0, { ...cmp, ...a2 });
    } catch (e) { ok(nom + ': la prueba llegó al final', false, e.message.split('\n')[0]); }
    await ctx.close();
  }
  await browser.close();
  const failed = res.checks.filter(c => !c.ok);
  console.log(JSON.stringify({ ...res, passed: res.checks.length - failed.length, failed: failed.length }, null, 1));
  process.exit(failed.length || res.errors.length ? 1 : 0);
})();
