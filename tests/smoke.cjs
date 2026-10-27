const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/../index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const ids=[...html.matchAll(/id="([^"]+)"/g)].map(x=>x[1]);
const els=Object.fromEntries(ids.map(id=>[id,{id,value:'',innerHTML:'',textContent:'',classList:{toggle(){},add(){}},addEventListener(){},dataset:{},click(){}}]));
const document={getElementById(id){if(!els[id])throw Error('Unknown DOM id '+id);return els[id]},querySelectorAll(){return []},createElement(){return {click(){},set href(x){},set download(x){}}}};
const window={scrollTo(){}};const URL={createObjectURL(){return 'blob:fake'},revokeObjectURL(){}};const Blob=function(){};
const context=vm.createContext({document,window,URL,Blob,console});
vm.runInContext(script,context,{timeout:5000});
const run=fn=>vm.runInContext(fn,context,{timeout:5000});
assert.equal(run('D.length'),28);assert.ok(run('T.length')>=10);assert.ok(els.kpis.innerHTML.includes('28'));
for(const [q, expected] of [['tortura','tortura'],['desapariciones','Desapariciones'],['mercenarios','Mercenarios'],['enforced disappearance','Desapariciones']]){
 els.q.value=q;run('filterMandates()');assert.ok(els.mandBody.innerHTML.toLowerCase().includes(expected.toLowerCase()),'search failed '+q);
}
els.q.value='zzzxwqnomatch';run('filterMandates()');assert.ok(els.mandBody.innerHTML.includes('Sin coincidencias'));
els.q.value='';els.yearfrom.value='1980';els.yearto.value='1980';run('filterMandates()');assert.ok(els.mandBody.innerHTML.includes('Desapariciones'));
els.yearfrom.value='';els.yearto.value='';run('clearFilters()');
els.recoverQuery.value='E/CN.4/RES/20(XXXVI)';run('recoverDocument()');assert.ok(els.recoverResult.innerHTML.includes('E/1980/13'));
els.recoverQuery.value='A/HRC/RES/54/14';run('recoverDocument()');assert.ok(els.recoverResult.innerHTML.includes('digitallibrary.un.org'));
run('details(0)');assert.ok(els.cardsResults.innerHTML.includes('Desapariciones'));
assert.ok(html.includes('cataplum1414/onu-arqueologia-documental'));
console.log(JSON.stringify({success:true,tests:14,mandates:run('D.length'),traces:run('T.length'),alerts:run('A.length'),html_bytes:Buffer.byteLength(html)}));
