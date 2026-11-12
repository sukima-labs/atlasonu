// P9 (plan de diseño, fase 8 «Medir y cerrar», #226): las metas medibles de la interfaz en el celular, en un solo sitio.
// La usan tests/auditar_ux.cjs (informe y --comprobar) y tests/browser.cjs (en modo oscuro y en claro).
//  · Ningún control que se toca (botón, enlace, campo, desplegable, pestaña) mide menos de 44 px de alto o de ancho,
//    salvo los enlaces que van dentro de una frase (texto corrido: WCAG 2.5.8 los exime) y el «Saltar al contenido»
//    mientras está escondido fuera de la pantalla.
//  · Ningún texto visible baja de 13 px.
//  · Ninguna pantalla pasa de unas 8 pantallas de alto sin paginar (se admite hasta 9).
const METAS = { control: 44, texto: 13, largo: 9 };

// Se ejecuta DENTRO de la página (page.evaluate(medirPantalla, METAS)); devuelve los números y unos ejemplos de lo que falla.
function medirPantalla(M) {
  const visible = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden'; };
  const enFrase = e => e.tagName === 'A' && /^inline/.test(getComputedStyle(e).display) && [...e.parentElement.childNodes].some(n => n !== e && n.nodeType === 3 && n.textContent.trim().length > 1);
  const escondido = e => getComputedStyle(e).position === 'absolute' && e.getBoundingClientRect().bottom <= 0 && document.activeElement !== e;
  const nombre = e => { const r = e.getBoundingClientRect(); return (e.id ? '#' + e.id : e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className ? '.' + e.className.trim().split(/\s+/)[0] : '')) + ` ${Math.round(r.width)}×${Math.round(r.height)} «${(e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 30)}»`; };
  const controles = [...document.querySelectorAll('button,a[href],select,input:not([type=hidden]),textarea,summary,[role=button],[role=tab]')]
    .filter(visible).filter(e => !enFrase(e) && !escondido(e))
    .filter(e => { const r = e.getBoundingClientRect(); return r.height < M.control - 0.5 || r.width < M.control - 0.5; });
  const textos = [...document.querySelectorAll('body *')]
    .filter(e => visible(e) && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1) && parseFloat(getComputedStyle(e).fontSize) < M.texto - 0.01);
  return {
    ancho: document.documentElement.scrollWidth, W: innerWidth,
    largo: Math.round(document.documentElement.scrollHeight / innerHeight * 10) / 10,
    controles: controles.length, controlesEj: controles.slice(0, 4).map(nombre),
    textos: textos.length, textosEj: textos.slice(0, 4).map(e => nombre(e) + ' ' + getComputedStyle(e).fontSize),
  };
}

const cumple = (m, M = METAS) => m.ancho <= m.W + 1 && m.controles === 0 && m.textos === 0 && m.largo <= M.largo;

module.exports = { METAS, medirPantalla, cumple };
