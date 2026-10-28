// Mide a 390 px cada pantalla del menú: desbordes, controles táctiles pequeños, tablas anchas, texto diminuto y largo de página. Uso: node tests/auditar_ux.cjs (informe de T15 en docs/INFORME_UX.md)
const { chromium } = require('playwright');
const path=require('path').resolve(__dirname,'..','index.html');
(async()=>{
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:390,height:844}});
 await p.route(/dignityos\.tailaa1f76/,r=>r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:'{"resultados":[]}'}));
 await p.goto('file://'+path);
 const pages=await p.evaluate(()=>[...document.querySelectorAll('.nav button[data-page]')].map(x=>x.dataset.page));
 for(const id of pages){
  await p.evaluate(i=>showPage(i),id); await p.waitForTimeout(400);
  const r=await p.evaluate(()=>{
   const sec=document.querySelector('section.active,.page.active,main section:not([hidden])')||document.body;
   const W=innerWidth;
   const out={sw:document.documentElement.scrollWidth,W};
   out.pequeños=[...document.querySelectorAll('button,a,select,input,summary')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&(r.height<32||r.width<32)&&getComputedStyle(e).visibility!=='hidden'&&e.offsetParent}).length;
   out.tablas=[...document.querySelectorAll('table')].filter(t=>t.offsetParent).map(t=>({w:Math.round(t.scrollWidth),cont:Math.round(t.parentElement.clientWidth),scroll:getComputedStyle(t.parentElement).overflowX}));
   const txt=document.body.innerText; out.sinEnlace=(txt.match(/Sin enlace directo verificado/g)||[]).length;
   out.largo=Math.round(document.documentElement.scrollHeight/innerHeight*10)/10;
   out.fuentePeq=[...document.querySelectorAll('td,p,li,span,small')].filter(e=>e.offsetParent&&e.children.length==0&&e.textContent.trim().length>3&&parseFloat(getComputedStyle(e).fontSize)<12).length;
   return out;});
  console.log(id,JSON.stringify(r));
 }
 await b.close();
})();
