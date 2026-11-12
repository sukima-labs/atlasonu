/* ATLAS ONU · service worker (fase 6 del plan de diseño, docs/PLAN_DISENO_UX.md; reabre la decisión de T58).
   Regla única: PRIMERO LA RED. Con conexión, cada petición va a la red y lo que llega se guarda como copia; la copia
   solo se usa cuando no hay red. Así la web nunca enseña datos viejos después de la revisión diaria, que era el
   riesgo por el que T58 descartó la PWA.
   - Solo peticiones GET del mismo sitio y dentro de la web (la página, assets/ y data/). Nunca la búsqueda en vivo
     (sk-atlas.pig-mimosa.ts.net) ni nada de otro dominio: eso no pasa por aquí.
   - La copia se guarda sin la parte «?v=…» de la dirección (los datos llevan un número que cambia cada 5 minutos para
     saltarse la caché del navegador); así hay una sola copia de cada archivo.
   - Todas las pantallas son la misma página (index.html, con «#pantalla»): «./» e «index.html» comparten una copia.
   - Si una respuesta sale de la copia, se avisa a la página para que muestre «Sin conexión: datos del …».
   Para cambiar la lógica de este archivo, sube la versión de CACHE: al activarse, se borran las copias anteriores. */
'use strict';
const CACHE = 'atlas-onu-v1';
const BASE = new URL('./', self.location).href; // p. ej. https://sukima-labs.github.io/atlasonu/
const PAGINA = BASE; // clave de la copia de index.html
const desdeCopia = new Set(); // ids de las pestañas a las que se sirvió algo de la copia

// Al instalarse guarda lo necesario para abrir sin red la portada y las pantallas de datos que se cargan aparte (mapa,
// noticias, EPU, conflictos, jurisprudencia, comunicaciones), con las imágenes y letras que pide la primera visita: todo
// eso se baja ANTES de que exista el service worker, así que sin esta lista la copia quedaría coja (logo roto, árabe con
// otra letra). Unos 2 MB sin comprimir. El diccionario de otro idioma NO va aquí: la página dice cuál usa (mensaje
// «sw-guarda») y solo se guarda ese, para no gastar datos del móvil en idiomas que nadie lee. Si algo falla, sigue igual.
const BASICO = ['./', 'data/atlas-data.js', 'data/atlas-actos.js', 'assets/idiomas.js', 'manifest.webmanifest',
  'assets/fonts/dejavu-sans-regular.woff2', 'assets/fonts/dejavu-sans-bold.woff2',
  'assets/fonts/dejavu-sans-regular-arabe.woff2', 'assets/fonts/dejavu-sans-bold-arabe.woff2',
  'assets/marca/dignityos_provisional.svg', 'assets/marca/favicon_32.png', 'assets/marca/apple_touch_icon_180.png',
  'data/noticias.js', 'data/mapa.js', 'data/epu.js', 'data/conflictos.js', 'data/jurisprudencia.js', 'data/comunicaciones.js',
  'data/seguimiento.js', 'data/estado.json'];
function guarda(c, ruta) {
  const u = new URL(ruta, BASE).href;
  return fetch(u, { cache: 'no-cache' }).then(r => { if (r.ok && r.type === 'basic') return c.put(u === BASE + 'index.html' ? PAGINA : u, r); })
    .catch(() => {});
}
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(BASICO.map(ruta => guarda(c, ruta)))).catch(() => {}));
});
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const nombres = await caches.keys();
    await Promise.all(nombres.filter(n => n.startsWith('atlas-onu-') && n !== CACHE).map(n => caches.delete(n)));
    await self.clients.claim();
  })());
});

function clave(req) {
  const u = new URL(req.url);
  u.search = '';
  u.hash = '';
  return u.href === BASE + 'index.html' ? PAGINA : u.href;
}

function seGuarda(req) {
  if (req.method !== 'GET') return false;
  const u = new URL(req.url);
  if (u.origin !== self.location.origin || !u.href.startsWith(BASE)) return false;
  const ruta = u.pathname.slice(new URL(BASE).pathname.length);
  // Navegaciones: solo la página (con cualquier «?movil=1» o «#pantalla»). Abrir un archivo de descarga (Excel,
  // catálogo JSON) va directo a la red y no se guarda.
  if (req.mode === 'navigate') return ruta === '' || ruta === 'index.html';
  return ruta === '' || ruta === 'index.html' || ruta.startsWith('assets/') || ruta.startsWith('data/') ||
    ruta === 'manifest.webmanifest';
}

async function avisa(id) {
  if (!id) return;
  desdeCopia.add(id);
  try {
    const c = await self.clients.get(id);
    if (c) c.postMessage({ atlas: 'sw-copia' });
  } catch (e) { /* la pestaña aún no existe: lo pregunta ella al arrancar */ }
}

async function primeroLaRed(e) {
  const req = e.request, k = clave(req);
  const idPestana = req.mode === 'navigate' ? (e.resultingClientId || e.clientId) : e.clientId;
  // La red, siempre. Lo que llega se guarda como copia.
  let guardado = Promise.resolve();
  const red = fetch(req).then(r => {
    if (r && r.ok && r.type === 'basic') {
      const copia = r.clone();
      guardado = caches.open(CACHE).then(c => c.put(k, copia)).catch(() => {});
    }
    return r;
  });
  e.waitUntil(red.then(() => guardado, () => {}));
  const deLaCopia = async err => {
    const guardada = await caches.match(k, { cacheName: CACHE });
    if (!guardada) throw err;
    // Sin «await»: la pestaña de una navegación no existe hasta que reciba esta respuesta (esperarla bloquearía la carga).
    e.waitUntil(avisa(idPestana).catch(() => {}));
    return guardada;
  };
  // Primero la red, sin plazo: la copia solo se usa cuando la red falla de verdad (sin conexión). Una red lenta espera
  // a la red, para no decir «Sin conexión» a quien sí la tiene.
  try { return await red; } catch (err) { return deLaCopia(err); }
}

self.addEventListener('fetch', e => {
  if (!seGuarda(e.request)) return; // lo demás (búsqueda en vivo, otros dominios) va directo a la red
  e.respondWith(primeroLaRed(e));
});

// La página pregunta al arrancar si su HTML salió de la copia (la navegación llega antes de que exista la pestaña).
// También dice qué diccionario de idioma usa, para guardarlo aunque se bajara antes de existir el service worker.
self.addEventListener('message', e => {
  if (e.data && e.data.atlas === 'sw-guarda' && /^data\/idiomas\/[a-z]{2}\.js$/.test(e.data.ruta || '')) {
    e.waitUntil(caches.open(CACHE).then(c => guarda(c, e.data.ruta)).catch(() => {}));
    return;
  }
  if (!e.data || e.data.atlas !== 'sw-estado' || !e.source) return;
  const id = e.source.id;
  e.source.postMessage({ atlas: desdeCopia.has(id) ? 'sw-copia' : 'sw-red' });
  desdeCopia.delete(id);
});
