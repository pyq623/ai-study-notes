const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
require('../assets/records.js');
const records = globalThis.StudyRecords;
const data = file => JSON.parse(fs.readFileSync(`docs/${file}.html`,'utf8').match(/<script id="quiz-data" type="application\/json">(.*?)<\/script>/s)[1]);
const infra=data('unit-5'), ds=data('unit-6'), systems=data('unit-7'), engineering=data('engineering');
function storage(values={}) {
  const store = new Map(Object.entries(values).map(([key,value])=>[key,JSON.stringify(value)]));
  return {getItem:key=>store.get(key)??null,setItem:(key,value)=>store.set(key,value)};
}
const answer={selected:['B'],submitted:true,last:true,first:false,confidence:'sure',attempts:3};
const read=(store,config)=>records.read(store,config,config.questions.map(q=>q.id));
test('reads previous answers by question ID and isolates engineering from new unit 6',()=>{
  const store=storage({[infra.storage_key]:{'5-01':answer,'5-39':answer,'5-48':answer},[engineering.storage_key]:{'E-08':answer}});
  assert.deepEqual(Object.keys(read(store,infra).records),['5-01']);
  assert.deepEqual(read(store,ds).records['5-39'],answer);
  assert.deepEqual(Object.keys(read(store,systems).records),['5-48']);
  assert.deepEqual(Object.keys(read(store,engineering).records),['E-08']);
});
test('new answers and reset drafts override legacy results without erasing another chapter',()=>{
  const store=storage({[infra.storage_key]:{'5-01':answer,'5-39':answer,'5-48':answer},[engineering.storage_key]:{'E-08':answer}});
  const reset={selected:[],confidence:'',submitted:false,first:false,last:true,attempts:3};
  assert.equal(records.write(store,ds.storage_key,{'5-39':reset}),true);
  assert.deepEqual(read(store,ds).records['5-39'],reset);
  records.write(store,systems.storage_key,{'5-48':{...answer,last:false,attempts:4}});
  records.write(store,infra.storage_key,{'5-01':{...answer,attempts:4}});
  assert.equal(read(store,systems).records['5-48'].attempts,4);
  assert.equal(read(store,ds).records['5-39'].attempts,3);
  assert.deepEqual(JSON.parse(store.getItem(infra.storage_key))['5-39'],answer);
  assert.deepEqual(read(store,engineering).records['E-08'],answer);
});
test('preview records never consume real records and storage failures remain recoverable',()=>{
  const store=storage({[infra.storage_key]:{'5-39':answer}});
  assert.deepEqual(records.read(store,ds,['5-39'],'-preview').records,{});
  store.setItem(ds.storage_key,'invalid JSON');
  const result=read(store,ds);
  assert.equal(result.ok,false);
  assert.deepEqual(result.records['5-39'],answer);
  const unavailable={getItem(){throw new Error('denied')},setItem(){throw new Error('denied')}};
  assert.equal(read(unavailable,ds).ok,false);
  assert.equal(records.write(unavailable,ds.storage_key,{}),false);
});
test('every old bookmark redirects to its new target and keeps preview query',()=>{
  const mapping=JSON.parse(fs.readFileSync('content/legacy-unit-5-links.json','utf8'));
  const script=fs.readFileSync('assets/legacy-links.js','utf8');
  for (const [anchor,target] of Object.entries(mapping)) {
    let redirected,handler;
    const href=`https://pyq623.github.io/ai-study-notes/unit-5.html?preview=1#${anchor}`;
    const location={href,hash:`#${anchor}`,search:'?preview=1',replace:url=>redirected=url};
    vm.runInNewContext(script,{URL,location,document:{getElementById:()=>({textContent:JSON.stringify(mapping)})},window:{addEventListener:(name,callback)=>handler=callback}});
    const expected=new URL(target,href);expected.search='?preview=1';
    assert.equal(redirected,expected.href);
    redirected=undefined;location.hash='#lesson-1';handler();
    assert.equal(redirected,undefined);
    location.hash='#q-5-39';handler();
    assert.equal(redirected,'https://pyq623.github.io/ai-study-notes/unit-6.html?preview=1#q-5-39');
  }
});
