/* ATLAS ONU · idiomas de la interfaz (T26; árabe, chino y ruso en T66, el árabe de derecha a izquierda). Sin servicios externos: diccionarios propios en data/idiomas/<ln>.js.
   Traduce solo los textos de la interfaz que están en el diccionario, por coincidencia exacta. Los datos oficiales
   (títulos de documentos, resoluciones, nombres de mandatos que vienen de la ONU) no están en el diccionario, así que
   se quedan en el idioma en que los publica la ONU: no se traducen ni se inventan.
   Clave de una «frase» (elemento cuyo contenido es solo texto y etiquetas en línea): su texto con los espacios
   colapsados y las etiquetas sin atributos, «Pulsa <b>Ver ficha</b> para…». La misma regla la sigue
   scripts/idiomas_textos.py para comprobar que el diccionario cubre index.html. Al traducir se reutilizan los
   elementos originales (enlaces, botones con su onclick) en el orden en que aparecen en la traducción.
   El idioma elegido se guarda en localStorage («atlas_idioma»); cambiarlo recarga la página en la misma pantalla. */
(function () {
  'use strict';
  var IDIOMAS = [['es', 'ES', 'Español'], ['en', 'EN', 'English'], ['fr', 'FR', 'Français'], ['ar', 'AR', 'العربية'], ['zh', 'ZH', '中文'], ['ru', 'RU', 'Русский']];
  var RTL = { ar: true }; // T66: el árabe se lee de derecha a izquierda
  var EN_LINEA = /^(A|ABBR|B|BR|CITE|CODE|EM|I|KBD|MARK|Q|S|SMALL|SPAN|STRONG|SUB|SUP|U)$/;
  var SALTAR = /^(SCRIPT|STYLE|SVG|NOSCRIPT|TEMPLATE)$/, SOLO_ATRS = /^(INPUT|TEXTAREA)$/; // de un campo, nunca lo escrito
  var ATRS = ['placeholder', 'aria-label', 'title', 'alt'];
  var AVISO = {
    en: 'Interface translated by ATLAS. Documents and official data keep the language in which the UN publishes them.',
    fr: 'Interface traduite par ATLAS. Les documents et les données officielles restent dans la langue où l’ONU les publie.',
    ar: 'واجهة مترجمة من ATLAS. تبقى الوثائق والبيانات الرسمية باللغة التي تنشرها بها الأمم المتحدة.',
    zh: '界面由 ATLAS 翻译。文件和官方数据保留联合国发布时所用的语言。',
    ru: 'Интерфейс переведён ATLAS. Документы и официальные данные остаются на том языке, на котором их публикует ООН.'
  };
  var guardado = null;
  try { guardado = localStorage.getItem('atlas_idioma'); } catch (e) {}
  var ln = /^(en|fr|ar|zh|ru)$/.test(guardado || '') ? guardado : 'es';
  var dic = null, hechos = new WeakSet(), pendientes = Object.create(null);

  var MESES_ES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var MESES = {
    en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    fr: ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
  };
  var FECHA = new RegExp('\\b(\\d{1,2}) de (' + MESES_ES.join('|') + ') de (\\d{4})\\b', 'gi');
  // Fecha corta de las fichas de país («15 sep 2002», T67): también es {fecha}, y cada idioma la escribe a su modo.
  var CORTOS_ES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var FECHA_CORTA = new RegExp('\\b(\\d{1,2}) (' + CORTOS_ES.join('|') + ') (\\d{4})\\b', 'g');
  var CORTOS = {
    en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    fr: ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
  };
  var fecha = function (x) { // x = [día, mes 0-11, año, corta]
    if (!MESES[ln]) { try { return new Intl.DateTimeFormat(ln, { day: 'numeric', month: x[3] ? 'short' : 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(Date.UTC(+x[2], x[1], x[0]))); } catch (e) { return x[0] + '.' + (x[1] + 1) + '.' + x[2]; } } // ar, zh, ru: el propio navegador
    return (ln === 'fr' && x[0] === 1 ? '1er' : x[0]) + ' ' + (x[3] ? CORTOS : MESES)[ln][x[1]] + ' ' + x[2];
  };

  var colapsa = function (t) { return t.replace(/\s+/g, ' '); };
  var excluido = function (el) { return SALTAR.test(el.nodeName) || el.getAttribute('translate') === 'no' || el.hasAttribute('data-sin-traducir'); };
  function soloEnLinea(el) {
    for (var c = el.firstElementChild; c; c = c.nextElementSibling) if (!EN_LINEA.test(c.nodeName) || !soloEnLinea(c)) return false;
    return true;
  }
  // Huecos que la página rellena con un valor (fecha de los datos, nombre del país): en la clave van vacíos (T67).
  var opaco = function (n) { return n.classList && (n.classList.contains('fechaDatos') || n.classList.contains('vh')); };
  function canon(el) {
    var out = '';
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) out += colapsa(n.data);
      else if (n.nodeType === 1) {
        var t = n.nodeName.toLowerCase();
        // <abbr> lo pone el glosario de siglas (T63) después de pintar: no cuenta para la clave.
        out += t === 'br' ? '<br>' : t === 'abbr' ? canon(n) : opaco(n) ? '<' + t + '></' + t + '>' : '<' + t + '>' + canon(n) + '</' + t + '>';
      }
    }
    return out;
  }
  var tieneLetras = function (k) { return /[A-Za-zÀ-ÿ]{2}/.test(k.replace(/<[^>]+>/g, '')); };
  function busca(k, bloque) { // bloque: si falla no se anota, porque se baja a sus partes
    k = k.trim();
    if (!k || !tieneLetras(k)) return null;
    if (Object.prototype.hasOwnProperty.call(dic, k)) return dic[k];
    // Fechas escritas («17 de marzo de 2003»): la clave lleva {fecha} y se escriben al modo del idioma elegido.
    var fechas = [], kf = k.replace(FECHA, function (x, d, m, a) { fechas.push([+d, MESES_ES.indexOf(m.toLowerCase()), a]); return '{fecha}'; });
    kf = kf.replace(FECHA_CORTA, function (x, d, m, a) { fechas.push([+d, CORTOS_ES.indexOf(m), a, true]); return '{fecha}'; });
    if (fechas.length) {
      var r = busca(kf, true);
      if (r != null) { var f = 0; return r.replace(/\{fecha\}/g, function () { return fecha(fechas[f++]); }); }
      k = kf;
    }
    // Frases con cifras que cambian («Mostrando 20 de 196»): la clave lleva {n} y las cifras se pasan en orden.
    var nums = [], kn = k.replace(/\d+(?:[.,]\d+)*/g, function (x) { nums.push(x); return '{n}'; });
    if (nums.length && Object.prototype.hasOwnProperty.call(dic, kn)) {
      var i = 0;
      return dic[kn].replace(/\{n\}/g, function () { return nums[i++]; });
    }
    if (!bloque) pendientes[nums.length ? kn : k] = 1;
    return null;
  }
  function atributos(el) {
    for (var i = 0; i < ATRS.length; i++) {
      var v = el.getAttribute(ATRS[i]);
      if (v) { var t = busca(colapsa(v)); if (t != null) el.setAttribute(ATRS[i], t); }
    }
  }
  // Reconstruye el contenido de «el» con la traducción, reutilizando sus elementos en línea por orden y por etiqueta.
  function aplica(el, trad) {
    var reserva = {};
    el.querySelectorAll('*').forEach(function (d) { if (d.nodeName !== 'ABBR') (reserva[d.nodeName] = reserva[d.nodeName] || []).push(d); });
    var raiz = document.createDocumentFragment(), pila = [raiz], re = /<(\/?)([a-z]+)>|([^<]+)/g, m;
    while ((m = re.exec(trad))) {
      var cima = pila[pila.length - 1];
      if (m[3] != null) { cima.appendChild(document.createTextNode(m[3])); continue; }
      var tag = m[2].toUpperCase();
      if (m[1]) { if (pila.length > 1) pila.pop(); continue; }
      var e = (reserva[tag] || []).shift() || document.createElement(tag);
      if (!opaco(e)) while (e.firstChild) e.removeChild(e.firstChild);
      cima.appendChild(e);
      if (tag !== 'BR') pila.push(e);
    }
    var lead = (el.firstChild && el.firstChild.nodeType === 3 && /^\s/.test(el.firstChild.data)) ? ' ' : '';
    var tail = (el.lastChild && el.lastChild.nodeType === 3 && /\s$/.test(el.lastChild.data)) ? ' ' : '';
    while (el.firstChild) el.removeChild(el.firstChild);
    if (lead) el.appendChild(document.createTextNode(lead));
    el.appendChild(raiz);
    if (tail) el.appendChild(document.createTextNode(tail));
  }
  function texto(n) {
    var t = busca(colapsa(n.data));
    if (t == null) return;
    var d = n.data, i = d.search(/\S/), j = d.search(/\s*$/);
    var cola = d.slice(j);
    if (/['’]$/.test(t)) cola = cola.replace(/^\s+/, ''); // «de l'» + «ONU»: en francés sin espacio tras el apóstrofo
    n.data = d.slice(0, i) + t + cola;
  }
  // T67: el glosario (T63) parte el texto en «…Biblioteca Digital de la », <abbr>ONU</abbr>, «, revisados…». Si el bloque
  // entero no está en el diccionario, se prueba el tramo seguido de texto y siglas como una sola frase antes de bajar a
  // cada trozo: así el orden de palabras lo decide la traducción («数字图书馆» + «联合国» no se pegan a la fuerza).
  var esAbbr = function (n) { return n && n.nodeType === 1 && n.nodeName === 'ABBR'; };
  var esTramo = function (n) { return n && (n.nodeType === 3 || esAbbr(n)); };
  function tramo(n) {
    if (!esAbbr(n.previousSibling) && !esAbbr(n.nextSibling)) return false;
    var a = n; while (esTramo(a.previousSibling)) a = a.previousSibling;
    var nodos = [], k = '';
    for (var x = a; esTramo(x); x = x.nextSibling) { nodos.push(x); k += colapsa(x.nodeType === 3 ? x.data : x.textContent); }
    nodos.forEach(function (x) { if (x.nodeType === 3) hechos.add(x); }); // cada tramo se resuelve una sola vez
    var t = busca(k, true);
    if (t == null) { // se anota el tramo entero, no sus trozos, y se traducen los trozos que sí estén (diccionarios viejos)
      if (tieneLetras(k)) pendientes[k.trim().replace(/\d+(?:[.,]\d+)*/g, '{n}')] = 1;
      nodos.forEach(function (x) { if (x.nodeType === 3 && busca(colapsa(x.data), true) != null) texto(x); });
      return true;
    }
    // Sin quitar nodos (el bucle de recorre va por los hermanos): el primer texto lleva la frase y el resto se vacía.
    var lead = /^\s/.test(k) ? ' ' : '', tail = /\s$/.test(k) ? ' ' : '';
    var primero = nodos.filter(function (x) { return x.nodeType === 3; })[0];
    if (nodos[0] !== primero) { primero = document.createTextNode(''); hechos.add(primero); a.parentNode.insertBefore(primero, a); }
    nodos.forEach(function (x) { if (x !== primero) { if (x.nodeType === 3) x.data = ''; else x.textContent = ''; } });
    primero.data = lead + t + tail;
    return true;
  }
  function recorre(el) {
    if (el.nodeType === 3) { if (!hechos.has(el) && el.parentNode && !hechos.has(el.parentNode) && !tramo(el)) texto(el); return; }
    if (el.nodeType !== 1 || excluido(el) || hechos.has(el)) return;
    // Un <option> sin value usa su texto como valor y los filtros lo comparan: se fija el original antes de traducir.
    if (el.nodeName === 'OPTION' && !el.hasAttribute('value')) el.setAttribute('value', el.value);
    atributos(el);
    if (SOLO_ATRS.test(el.nodeName)) return;
    // Un elemento en línea (span, b…) solo llega aquí si su bloque no estaba entero en el diccionario: se prueba como frase.
    if (el.firstChild && soloEnLinea(el) && el.nodeName !== 'BR') {
      el.querySelectorAll('*').forEach(atributos);
      var t = busca(canon(el), true);
      if (t != null) { aplica(el, t); hechos.add(el); return; }
    }
    for (var n = el.firstChild; n; n = n.nextSibling) recorre(n);
  }
  function selector() {
    var css = document.createElement('style');
    css.textContent = '.idioma{display:flex;gap:4px;align-items:center;margin:10px 0 4px}.idioma button{min-width:40px;min-height:32px;padding:2px 8px;border:1px solid #6b5a40;border-radius:6px;background:transparent;color:#eacfa6;font:600 12px/1 system-ui,sans-serif;cursor:pointer}.idioma button[aria-pressed=true]{background:#e1bb81;color:#191714;border-color:#e1bb81}.idioma button:focus-visible{outline:2px solid #f6ead7;outline-offset:2px}.appbar .idioma{margin:0 0 0 auto}.idioma-aviso{font-size:11px;line-height:1.4;color:#c6b69b;margin:2px 0 8px}' +
      // «Ver más» y «Ocultar» de los recuadros «Para qué sirve esta pantalla» son content de CSS, no texto
      ({ en: ['See more', 'Hide'], fr: ['Voir plus', 'Masquer'], ar: ['عرض المزيد', 'إخفاء'], zh: ['查看更多', '收起'], ru: ['Подробнее', 'Скрыть'] }[ln] || []).reduce(function (c, t, i) { return c + (i ? '.about[open] summary::after{content:"' + t + '"}' : '.about summary::after{content:"' + t + '"}'); }, '') +
      '.idioma{flex-wrap:wrap}.idioma select{min-height:32px;max-width:9.5em;padding:2px 6px;border:1px solid #6b5a40;border-radius:6px;background:#1f1c18;color:#eacfa6;font:600 12px/1 system-ui,sans-serif}' +
      // árabe: el menú lateral del celular sale por la derecha, donde está su botón
      // P1: en el celular, un solo selector de idioma (el desplegable de la barra superior, con 44 px de alto); los botones del menú quedan para el escritorio
      '@media(max-width:1080px){.side .idioma{display:none}.appbar .idioma select{min-height:44px;font-size:14px}}' +
      '@media(max-width:1080px){html[dir=rtl] .side{left:auto;right:0;transform:translateX(104%);border-right:0;border-left:1px solid #38322a;box-shadow:-12px 0 40px rgba(0,0,0,.45)}html[dir=rtl] body.menu-open .side{transform:none}}';
    document.head.appendChild(css);
    var hacer = function () {
      var g = document.createElement('div');
      g.className = 'idioma'; g.setAttribute('role', 'group'); g.setAttribute('translate', 'no');
      g.setAttribute('aria-label', { en: 'Language', fr: 'Langue', ar: 'اللغة', zh: '语言', ru: 'Язык' }[ln] || 'Idioma');
      IDIOMAS.forEach(function (x) {
        var b = document.createElement('button');
        b.type = 'button'; b.textContent = x[1]; b.lang = x[0]; b.title = x[2]; b.setAttribute('aria-label', x[2]);
        b.setAttribute('aria-pressed', String(x[0] === ln));
        b.onclick = function () { cambia(x[0]); };
        g.appendChild(b);
      });
      return g;
    };
    var sub = document.querySelector('.side .subbrand');
    if (sub) {
      var g = hacer(); sub.parentNode.insertBefore(g, sub.nextSibling);
      if (AVISO[ln]) { var p = document.createElement('p'); p.className = 'idioma-aviso'; p.setAttribute('translate', 'no'); p.textContent = AVISO[ln]; g.parentNode.insertBefore(p, g.nextSibling); }
    }
    var bar = document.querySelector('.appbar');
    if (bar) { // T66: con seis idiomas los botones no caben a 390 px; arriba va un desplegable con el nombre de cada idioma
      var d = document.createElement('div'), sel = document.createElement('select');
      d.className = 'idioma'; d.setAttribute('translate', 'no');
      sel.setAttribute('aria-label', { en: 'Language', fr: 'Langue', ar: 'اللغة', zh: '语言', ru: 'Язык' }[ln] || 'Idioma');
      IDIOMAS.forEach(function (x) { var o = document.createElement('option'); o.value = x[0]; o.lang = x[0]; o.textContent = x[2]; o.selected = x[0] === ln; sel.appendChild(o); });
      sel.onchange = function () { cambia(sel.value); };
      d.appendChild(sel); bar.appendChild(d);
    }
  }
  function cambia(nuevo) {
    if (nuevo === ln) return;
    try { if (nuevo === 'es') localStorage.removeItem('atlas_idioma'); else localStorage.setItem('atlas_idioma', nuevo); } catch (e) {}
    location.reload();
  }
  function arranca() {
    document.documentElement.lang = ln;
    if (RTL[ln]) document.documentElement.dir = 'rtl';
    var t = busca(colapsa(document.title));
    if (t != null) document.title = t;
    recorre(document.body);
    new MutationObserver(function (ms) {
      ms.forEach(function (m) { m.addedNodes.forEach(recorre); });
    }).observe(document.body, { childList: true, subtree: true });
  }
  window.ATLAS_IDIOMA = { actual: ln, cambia: cambia, pendientes: function () { return Object.keys(pendientes); } };
  selector();
  if (ln === 'es') return;
  var s = document.createElement('script');
  s.src = 'data/idiomas/' + ln + '.js?v=4';
  s.onload = function () { dic = window['ATLAS_IDIOMA_' + ln]; if (dic) arranca(); };
  document.head.appendChild(s);
})();
