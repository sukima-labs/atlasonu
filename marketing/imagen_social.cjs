// Genera la imagen para compartir enlaces (1200x630) en assets/social/atlas-onu-og.png.
// Uso (desde la raíz del repo, con Playwright instalado): node marketing/imagen_social.cjs
// Las cifras salen de data/estado.json; sin fuentes ni recursos externos (no se carga nada de la red).
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const raiz = path.join(__dirname, '..');
const c = JSON.parse(fs.readFileSync(path.join(raiz, 'data/estado.json'), 'utf8')).contadores;
const meridianos = [...Array(7)].map((_, i) => `<ellipse cx="900" cy="315" rx="${40 + i * 48}" ry="270" />`).join('');
const paralelos = [-190, -120, -50, 20, 90, 160, 230].map(y => `<line x1="560" x2="1240" y1="${315 + y * 0.9}" y2="${315 + y * 0.9}" />`).join('');
const html = `<!doctype html><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;background:radial-gradient(900px 600px at 85% 40%,#2b2418 0%,#171512 60%);color:#f6ead7;
font-family:'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,'Noto Serif',serif;position:relative;overflow:hidden}
svg{position:absolute;right:-120px;top:0;width:700px;height:630px;opacity:.35}
svg ellipse,svg line{fill:none;stroke:#d9a24e;stroke-width:1.6}
.barra{position:absolute;left:0;top:0;bottom:0;width:14px;background:#d9a24e}
.marca{position:absolute;left:72px;top:58px;font:700 34px/1 Inter,system-ui,'Segoe UI',sans-serif;letter-spacing:.04em}
.marca b{color:#e8c27c}
.sub{position:absolute;left:74px;top:104px;font:600 17px/1 Inter,system-ui,'Segoe UI',sans-serif;letter-spacing:.22em;color:#b39e79}
h1{position:absolute;left:72px;top:160px;width:720px;font-size:46px;line-height:1.18;font-weight:600}
.cifras{position:absolute;left:72px;top:400px;display:flex;gap:16px;font-family:Inter,system-ui,'Segoe UI',sans-serif}
.cifras div{background:rgba(217,162,78,.14);border:1px solid rgba(217,162,78,.4);border-radius:14px;padding:12px 20px}
.cifras b{display:block;font-size:34px;color:#e8c27c;line-height:1.1}.cifras span{font-size:16px;color:#d8c9ae}
.pie{position:absolute;left:72px;bottom:44px;right:60px;font:500 20px/1.4 Inter,system-ui,'Segoe UI',sans-serif;color:#d8c9ae}
.pie strong{color:#f6ead7}.pie small{display:block;font-size:15px;color:#b39e79;margin-top:6px}
</style><div class="barra"></div>
<svg viewBox="0 0 700 630"><defs><clipPath id="g"><ellipse cx="900" cy="315" rx="288" ry="270"/></clipPath></defs><g transform="translate(-560,0)" clip-path="url(#g)">${meridianos}${paralelos}</g></svg>
<div class="marca">ATLAS <b>ONU</b></div><div class="sub">ARQUEOLOGÍA DOCUMENTAL</div>
<h1>Entiende cómo la ONU protege los derechos humanos, con los documentos delante</h1>
<div class="cifras"><div><b>${c.mandatos}</b><span>mandatos de relatores</span></div><div><b>${c.paises}</b><span>fichas de país</span></div><div><b>6</b><span>idiomas</span></div></div>
<div class="pie"><strong>sukima-labs.github.io/atlasonu</strong> · Gratis · Código abierto · Sin rastreo<small>Iniciativa independiente de Sukima-Labs; no es un producto oficial de Naciones Unidas.</small></div>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.setContent(html);
  const destino = path.join(raiz, 'assets/social/atlas-onu-og.png');
  await p.screenshot({ path: destino });
  await b.close();
  console.log('escrito', path.relative(raiz, destino), fs.statSync(destino).size, 'bytes');
})();
