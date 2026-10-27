const test = require('node:test');
const assert = require('node:assert/strict');
const {load} = require('../assets/coding-state.js');
function storage(entries, failWrites = false) {
  const data = new Map(Object.entries(entries));
  return {get length() {return data.size;}, key: i => [...data.keys()][i],
    getItem: k => data.get(k) ?? null,
    setItem(k,v) {if (failWrites) throw new Error('full'); data.set(k,v);}};
}
const oldKey = 'sideinn:coding:legacy-ai-infra:v1';
const key = 'sideinn:coding:ai-infra:v1';
const old = {'OLD-01': {status:'done',draft:'def solve(): pass',notes:'edge cases',checks:['0','2']}};
test('renamed course preserves drafts, checks and status without removing old data', () => {
  const s = storage({[oldKey]:JSON.stringify(old)});
  const result = load(s, 'ai-infra', '', ['AI-01']);
  assert.deepEqual(result.records['AI-01'],old['OLD-01']);
  assert.deepEqual(JSON.parse(s.getItem(key)), result.records);
  assert.equal(s.getItem(oldKey),JSON.stringify(old));
  assert.deepEqual(Object.keys(result.records), ['AI-01']);
});
test('existing neutral records take precedence, and preview is isolated', () => {
  const current = {'AI-01':{status:'review',draft:'new draft'}};
  const s = storage({[oldKey]:JSON.stringify(old),[key]:JSON.stringify(current)});
  assert.deepEqual(load(s,'ai-infra','',['AI-01']).records,current);
  assert.deepEqual(load(s,'ai-infra',':preview',['AI-01']).records,{});
  s.setItem(oldKey+':preview', JSON.stringify(old));
  assert.deepEqual(load(s,'ai-infra',':preview',['AI-01']).records['AI-01'],old['OLD-01']);
});
test('failed persistence preserves in-memory migrated content and original backup', () => {
  const s = storage({[oldKey]:JSON.stringify(old)}, true);
  const result=load(s,'ai-infra','',['AI-01']);
  assert.equal(result.writable,false);
  assert.deepEqual(result.records['AI-01'],old['OLD-01']);
  assert.ok(s.getItem(oldKey));
});
test('invalid storage does not break loading', () => {
  const s=storage({[key]:'broken',[oldKey]:'[]'});
  assert.deepEqual(load(s,'ai-infra','',['AI-01']).records,{});
});
