// P8 · Componentes (plan de diseño, fase 7; docs/DISENO.md): pastilla de estado con su fuente, comparador de varios países,
// asistente paso a paso, línea de tiempo compacta y ficha de delegación imprimible.
// Los componentes viven en index.html, pero el asistente, la línea de tiempo y la ficha todavía no los usa ninguna pantalla
// (sus contenidos son de T75, T76, T77 y T83). Esta prueba los monta en una pantalla de muestra que SOLO existe aquí
// (no está en el menú ni en la web) y comprueba, en los dos modos, a 390 px y a 1280 px:
//   axe sin incumplimientos (WCAG 2.2 AA), sin desbordar la pantalla, la primera columna fija del comparador,
//   el asistente con el teclado (error si no se elige, foco en cada pregunta, «Atrás», resumen), la impresión de una sola
//   parte y que en inglés no quede ningún texto de los componentes sin traducir.
// Los textos de muestra dicen que son de muestra: no son contenido de ATLAS.
// Uso: npm i --no-save playwright axe-core && node tests/componentes.cjs   (CAPTURAS=<carpeta> guarda capturas de cada caso)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const AXE = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const INDEX = 'file://' + path.resolve(__dirname, '..', 'index.html');
const REGLAS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
const CAPTURAS = process.env.CAPTURAS || '';
let fallos = 0, bien = 0;
const ok = (n, c, info) => { if (c) { bien++; console.log('✓ ' + n); } else { fallos++; console.log('✗ ' + n + (info ? ' ' + JSON.stringify(info) : '')); } };

// Pantalla de muestra: se crea dentro de .main y se abre con showPage, como cualquier otra.
function monta() {
  const s = document.createElement('section');
  s.id = 'muestra-componentes'; s.className = 'section';
  const P = ['COL', 'ESP', 'KEN', 'JPN'].map(id => PID[id]);
  const F = P.map(p => compararFilas(p));
  const pais = P[0];
  s.innerHTML = `<h1 tabindex="-1">Muestra de componentes</h1>
  <h2>Pastillas</h2><p class="pills-muestra" style="display:flex;flex-wrap:wrap;gap:8px">
  ${pastilla('ok', 'Hecho', { t: '#1', url: 'https://github.com/sukima-labs/atlasonu/issues/1' })}
  ${pastilla('parcial', 'Corregido', { html: 'según <a href="https://digitallibrary.un.org/">Biblioteca Digital</a>' })}
  ${pastilla('aviso', 'En curso')}${pastilla('mal', 'Bloqueado')}${pastilla('neutro', 'Pendiente', { t: 'texto de muestra' })}${pastilla('nd')}</p>
  <h2>Comparador</h2><div id="mxCmp">${comparador({ etiqueta: 'Comparación entre países', cab: 'Aspecto', cols: P.map(p => esc(p.es)),
    filas: F[0].map((f, i) => ({ h: f[0], v: F.map(x => x[i][1]), dif: new Set(F.map(x => x[i][2])).size > 1 })).slice(0, 8) })}</div>
  <h2>Asistente</h2><div id="mxAsis"></div>
  <h2>Línea de tiempo compacta</h2>${lineaCompacta([
    { ciclo: 'Ciclo 1', fecha: '2008', est: 'ok', txt: 'Hecho', fuente: { t: 'texto de muestra' } },
    { ciclo: 'Ciclo 2', fecha: '2013', est: 'aviso', txt: 'En curso' },
    { ciclo: 'Ciclo 3', fecha: '2018', est: 'mal', txt: 'Bloqueado' },
    { ciclo: 'Ciclo 4', fecha: '2023', est: 'nd', actual: true }], 'Muestra')}
  <h2>Ficha de delegación</h2><div id="mxFicha">${fichaDelegacion({ pais: pais.es, codigo: pais.id, sub: esc(F[0][0][1]),
    bloques: F[0].slice(0, 3).map(f => ({ t: f[0].replace(/<[^>]+>/g, ''), html: '<p>' + f[1] + '</p>' })).concat([{ t: 'Muestra', html: '<span class="fd-linea"></span><span class="fd-linea"></span>', ancho: true }]),
    pie: 'Muestra' })}</div>`;
  document.querySelector('.main').appendChild(s);
  window.mxA = asistente(document.getElementById('mxAsis'), { pasos: [
    { titulo: 'Uno', pregunta: 'Pregunta de muestra 1', ayuda: 'Texto de muestra.', opciones: [['a', 'Opción A'], ['b', 'Opción B']] },
    { titulo: 'Dos', pregunta: 'Pregunta de muestra 2', opciones: [['c', 'Opción C'], ['d', 'Opción D']] }],
    resultado: R => '<p>Muestra: ' + esc(Object.values(R).join(', ')) + '</p>' });
  showPage('muestra-componentes', true); cmpxDesborda();
}

(async () => {
  const b = await chromium.launch();
  for (const [vn, vp] of [['390px', { width: 390, height: 844, isMobile: true, hasTouch: true }], ['1280px', { width: 1280, height: 900 }]]) {
    for (const modo of ['dark', 'light']) {
      const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, hasTouch: !!vp.hasTouch, colorScheme: modo });
      const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
      await p.route(/sk-atlas\.pig-mimosa/, r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: '{"resultados":[]}' }));
      await p.goto(INDEX); await p.waitForFunction(() => window.__atlasListo);
      await p.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
      await p.evaluate(monta); await p.waitForTimeout(300);
      const caso = `${vn} ${modo}`;
      ok(caso + ': la página está en el modo pedido', await p.evaluate(m => document.documentElement.dataset.theme === m, modo));
      // Comparador: cuatro países, primera columna fija, cabe en la página y se desliza dentro de su caja
      const c = await p.evaluate(() => { const e = document.querySelector('#mxCmp .cmpx'), th = e.querySelector('tbody th');
        return { pagina: document.documentElement.scrollWidth, pantalla: innerWidth, dentro: e.scrollWidth > e.clientWidth + 2, desborda: e.hasAttribute('data-desborda'),
          pista: getComputedStyle(e.nextElementSibling).display, fija: getComputedStyle(th).position, foco: e.getAttribute('role') === 'region' && (e.tabIndex === 0) === e.hasAttribute('data-desborda') }; });
      ok(caso + ': nada se sale de la pantalla', c.pagina <= c.pantalla + 1, c);
      ok(caso + ': comparador con la primera columna fija; es parada del teclado solo si hay algo que deslizar', c.fija === 'sticky' && c.foco, c);
      if (vn === '390px') ok(caso + ': en el celular el comparador de 4 países se desliza dentro de su caja y dice «Desliza de lado»', c.dentro && c.desborda && c.pista === 'block', c);
      if (vn === '390px') { // al deslizar, la primera columna se queda en su sitio
        const x = await p.evaluate(() => { const e = document.querySelector('#mxCmp .cmpx'), th = e.querySelector('tbody th'), a = th.getBoundingClientRect().left; e.scrollLeft = 200; const d = th.getBoundingClientRect().left; e.scrollLeft = 0; return { a, d }; });
        ok(caso + ': al deslizar el comparador la columna «Aspecto» no se mueve', Math.abs(x.a - x.d) < 1, x);
      }
      // Pastillas: cada estado tiene su palabra, y «Sin información» sale cuando no se da texto
      ok(caso + ': pastillas con su estado y su fuente; sin texto dice «Sin información»', await p.evaluate(() => {
        const L = [...document.querySelectorAll('.pills-muestra .pill')]; return L.length === 6 && L.every(e => e.querySelector('.pill-est').textContent.trim().length > 2) && /Sin información/.test(L[5].textContent) && L[0].querySelector('.pill-fuente a[href]') && /según/.test(L[1].textContent); }));
      // Línea de tiempo: el ciclo actual lleva aria-current y su punto relleno
      ok(caso + ': línea de tiempo: el ciclo actual está marcado (aria-current y punto relleno)', await p.evaluate(() => { const L = [...document.querySelectorAll('.ltc-it')], a = L.filter(x => x.hasAttribute('aria-current')), bg = e => getComputedStyle(e, '::after').backgroundColor;
        return a.length === 1 && /Ciclo 4/.test(a[0].textContent) && bg(a[0]) !== bg(L[0]); }));
      // Asistente con el teclado
      await p.evaluate(() => document.querySelector('#mxAsis .asis-sig').click());
      const e1 = await p.evaluate(() => ({ err: document.querySelector('#mxAsis .asis-error').textContent, foco: document.activeElement.matches('#mxAsis .asis-ops input') }));
      ok(caso + ': asistente: sin elegir, avisa «Elige una opción» y lleva el foco a las opciones', /Elige una opción/.test(e1.err) && e1.foco, e1);
      ok(caso + ': asistente: las opciones quedan marcadas como no válidas y apuntan al aviso', await p.evaluate(() => { const r = document.querySelector('#mxAsis .asis-ops input'), d = r.getAttribute('aria-describedby'); return r.getAttribute('aria-invalid') === 'true' && !!d && /Elige una opción/.test(document.getElementById(d).textContent); }));
      await p.check('#mxAsis .asis-ops input[value="b"]');
      ok(caso + ': asistente: al elegir, el aviso y la marca de no válido se quitan', await p.evaluate(() => !document.querySelector('#mxAsis .asis-error').textContent && !document.querySelector('#mxAsis [aria-invalid]')));
      await p.click('#mxAsis .asis-sig');
      const e2 = await p.evaluate(() => ({ foco: document.activeElement.textContent, paso: document.querySelector('#mxAsis .asis-cuenta').textContent, actual: document.querySelector('#mxAsis [aria-current=step]').textContent, atras: !!document.querySelector('#mxAsis .asis-atras') }));
      ok(caso + ': asistente: «Siguiente» pasa a la pregunta 2 con el foco en ella, «Paso 2 de 3» y «Atrás»', e2.foco === 'Pregunta de muestra 2' && e2.paso === 'Paso 2 de 3' && e2.actual === 'Dos' && e2.atras, e2);
      await p.click('#mxAsis .asis-atras');
      ok(caso + ': asistente: «Atrás» vuelve a la pregunta 1 y recuerda lo elegido', await p.evaluate(() => document.activeElement.textContent === 'Pregunta de muestra 1' && document.querySelector('#mxAsis input[value="b"]').checked));
      await p.click('#mxAsis .asis-sig'); await p.check('#mxAsis .asis-ops input[value="c"]'); await p.click('#mxAsis .asis-sig');
      const e3 = await p.evaluate(() => ({ foco: document.activeElement.textContent, dd: [...document.querySelectorAll('#mxAsis dd')].map(x => x.textContent), fin: document.querySelector('#mxAsis .asis-res-final').textContent }));
      ok(caso + ': asistente: el resumen recoge las respuestas y el foco va a «Resumen»', e3.foco === 'Resumen' && e3.dd.join('|') === 'Opción B|Opción C' && /b, c/.test(e3.fin), e3);
      await p.waitForTimeout(150);
      if (CAPTURAS) { fs.mkdirSync(CAPTURAS, { recursive: true });
        for (const [n, sel] of [['pastillas', '.pills-muestra'], ['comparador', '#mxCmp'], ['asistente', '#mxAsis'], ['linea', '.ltc'], ['ficha', '#mxFicha']]) await (await p.$(sel)).screenshot({ path: path.join(CAPTURAS, `${n}-${vn}-${modo}.png`) });
        await p.evaluate(() => window.mxA.ir(0)); await p.waitForTimeout(100); await (await p.$('#mxAsis')).screenshot({ path: path.join(CAPTURAS, `asistente-paso1-${vn}-${modo}.png`) }); await p.evaluate(() => window.mxA.ir(2)); }
      // axe en toda la pantalla de muestra
      await p.addScriptTag({ content: AXE });
      await p.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
      for (const vista of ['resumen', 'pregunta']) {
        if (vista === 'pregunta') { await p.evaluate(() => window.mxA.ir(0)); await p.evaluate(() => document.querySelector('#mxAsis .asis-sig').click()); await p.waitForTimeout(100); } // con el aviso de error a la vista
        const v = await p.evaluate(async r => (await axe.run('#muestra-componentes', { runOnly: r })).violations.map(x => ({ id: x.id, n: x.nodes.length, ej: x.nodes[0].target.join(' ') })), REGLAS);
        ok(caso + ': axe sin incumplimientos (asistente en ' + vista + ')', v.length === 0, v);
      }
      // Imprimir una sola parte: con la ficha marcada, la hoja solo lleva la ficha
      if (vn === '1280px') {
        await p.evaluate(() => { window.mxFin = marcarImpresion(document.querySelector('#mxFicha .ficha-del')); });
        await p.emulateMedia({ media: 'print' });
        const im = await p.evaluate(() => { const vis = e => e.getClientRects().length > 0; return { ficha: vis(document.querySelector('.ficha-del')), cmp: vis(document.querySelector('#mxCmp')), asis: vis(document.querySelector('#mxAsis')), h1: vis(document.querySelector('#muestra-componentes h1')) }; });
        const pdf = await p.pdf({ format: 'A4' }); const hojas = (pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
        ok(caso + ': «Imprimir la ficha» saca solo la ficha, en una hoja', im.ficha && !im.cmp && !im.asis && !im.h1 && hojas === 1, { ...im, hojas });
        await p.evaluate(() => window.mxFin()); await p.emulateMedia({ media: 'screen' });
        ok(caso + ': después de imprimir, la pantalla vuelve a estar entera', await p.evaluate(() => !document.querySelector('.imp-camino,.imp-esto') && !document.documentElement.classList.contains('imp-parcial')));
      }
      // Alertas › Exactitud de números: la pastilla del estado no se aplasta en su columna (nunca más de dos líneas)
      if (vn === '1280px') {
        const al = await p.evaluate(async () => { showPage('auditoria', true); numFiltro = 'todos'; numVista = 'actos'; numRender(); await new Promise(r => setTimeout(r, 50));
          const L = [...document.querySelectorAll('#numAudit table .pill')].filter(e => e.getClientRects().length); return { n: L.length, alto: Math.max(0, ...L.map(e => e.getBoundingClientRect().height)) }; });
        ok(caso + ': Alertas: la pastilla del estado en la tabla de actos cabe en dos líneas como mucho', al.n > 0 && al.alto < 56, al);
      }
      ok(caso + ': sin errores de JavaScript', errs.length === 0, errs);
      await ctx.close();
    }
  }
  // En inglés: los textos de los componentes salen traducidos (el diccionario los tiene) y no queda ninguno pendiente
  {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    await ctx.addInitScript(() => { try { localStorage.setItem('atlas_idioma', 'en'); } catch (e) {} });
    const p = await ctx.newPage();
    await p.goto(INDEX); await p.waitForFunction(() => window.__atlasListo && window.ATLAS_IDIOMA_en);
    await p.evaluate(monta); await p.waitForTimeout(400);
    const t0 = await p.evaluate(() => document.getElementById('muestra-componentes').innerText);
    await p.evaluate(() => window.mxA.ir(2)); await p.waitForTimeout(300);
    const t = t0 + await p.evaluate(() => document.getElementById('mxAsis').innerText);
    ok('en inglés: pastillas, comparador, asistente y ficha traducidos', /No information/.test(t) && /\bper\b/.test(t) && /Digital Library/.test(t) && /In testing/.test(t) && /Step 1 of 3/.test(t) && /Step 3 of 3/.test(t) && /Print the summary/.test(t) && /Change the answers/.test(t) && /Delegation card/.test(t) && /Swipe sideways/.test(t) && /Aspect/.test(t), t.slice(0, 400));
    const comp = ['según', 'Sin información', 'En pruebas', 'Paso', 'Atrás', 'Siguiente', 'Resumen', 'Imprimir', 'Cambiar las respuestas', 'Empezar de nuevo', 'Ficha de delegación', 'Desliza de lado', 'Aspecto', 'Elige una opción'];
    await p.evaluate(() => { window.mxA.ir(0); document.querySelector('#mxAsis .asis-sig').click(); }); await p.waitForTimeout(200);
    const pend = (await p.evaluate(() => ATLAS_IDIOMA.pendientes())).filter(k => comp.some(c => k.startsWith(c) || k.includes('>' + c)));
    ok('en inglés: ningún texto de los componentes queda sin traducir (también el aviso de error)', pend.length === 0 && /Choose an option/.test(await p.textContent('#mxAsis .asis-error')), pend);
    await ctx.close();
  }
  await b.close();
  console.log(`componentes: ${bien} bien, ${fallos} fallos`);
  if (fallos) process.exit(1);
})().catch(e => { console.error(e); process.exit(1); });
