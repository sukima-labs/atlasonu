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

// Al instalarse guarda lo imprescindible para abrir la portada sin red (la página, los datos y la letra). El resto de
// pantallas (mapa, EPU, noticias…) se guardan la primera vez que se abren. Si algo falla, la instalación sigue igual.
const BASICO = ['./', 'data/atlas-data.js', 'data/atlas-actos.js', 'assets/idiomas.js', 'manifest.webmanifest',
  'assets/fonts/dejavu-sans-regular.woff2', 'assets/fonts/dejavu-sans-bold.woff2'];
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(BASICO.map(ruta => {
    const u = new URL(ruta, BASE).href;
    return fetch(u).then(r => { if (r.ok && r.type === 'basic') return c.put(u === BASE + 'index.html' ? PAGINA : u, r); })
      .catch(() => {});
  }))).catch(() => {}));
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
  try {
    const r = await fetch(req);
    if (r && r.ok && r.type === 'basic') {
      const copia = r.clone();
      e.waitUntil(caches.open(CACHE).then(c => c.put(k, copia)).catch(() => {}));
    }
    return r;
  } catch (err) {
    const guardada = await caches.match(k, { cacheName: CACHE });
    if (!guardada) throw err;
    e.waitUntil(avisa(req.mode === 'navigate' ? (e.resultingClientId || e.clientId) : e.clientId));
    return guardada;
  }
}

self.addEventListener('fetch', e => {
  if (!seGuarda(e.request)) return; // lo demás (búsqueda en vivo, otros dominios) va directo a la red
  e.respondWith(primeroLaRed(e));
});

// La página pregunta al arrancar si su HTML salió de la copia (la navegación llega antes de que exista la pestaña).
self.addEventListener('message', e => {
  if (!e.data || e.data.atlas !== 'sw-estado' || !e.source) return;
  const id = e.source.id;
  e.source.postMessage({ atlas: desdeCopia.has(id) ? 'sw-copia' : 'sw-red' });
  desdeCopia.delete(id);
});
