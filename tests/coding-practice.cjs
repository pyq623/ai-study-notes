const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const CodingState = require('../assets/coding-state.js');
const script = fs.readFileSync(require.resolve('../assets/coding-practice.js'), 'utf8');
const key = 'sideinn:coding:ai-infra:v1';

function storage() {
  const data = new Map();
  return {fail: false, get length() {return data.size;}, key: i => [...data.keys()][i],
    getItem: k => data.get(k) ?? null,
    setItem(k, v) {if (this.fail) throw new Error('full'); data.set(k, v);},
    records() {return JSON.parse(data.get(key));}};
}

// Run the real page handlers in separate contexts, as two tabs sharing storage.
function tab(localStorage, hash = '') {
  const element = () => ({value: '', textContent: '', addEventListener(type, handler) {this[type] = handler;}});
  const elements = Object.fromEntries(['coding-search', 'coding-tier', 'coding-filter', 'coding-progress',
    'coding-meter', 'coding-empty', 'coding-save', 'coding-export'].map(id => [id, element()]));
  const cards = ['AI-01', 'AI-03'].map(id => {
    const fields = {'[data-review]': element(), '.coding-draft': element(), '.coding-notes': element()};
    const checks = ['0', '1'].map(check => ({...element(), dataset: {check}, checked: false}));
    return {id, dataset: {tier: '必练'}, textContent: id, fields, checks,
      querySelector: selector => fields[selector],
      querySelectorAll: selector => selector.endsWith(':checked') ? checks.filter(box => box.checked) : checks};
  });
  const root = {dataset: {codingCourse: 'ai-infra'}, querySelectorAll: () => cards, addEventListener() {}};
  let exported;
  vm.runInNewContext(script, {localStorage, CodingState, URLSearchParams, Date,
    location: {search: '', hash}, window: {addEventListener() {}},
    document: {querySelector: () => root, getElementById: id => elements[id], createElement: () => ({click() {}})},
    Blob: class {constructor(parts) {exported = JSON.parse(parts[0]);}},
    URL: {createObjectURL: () => 'blob:export', revokeObjectURL() {}}, setTimeout() {}});
  return {
    edit(id, field, value) {
      const card = cards.find(card => card.id === id);
      const area = card.fields[field === 'status' ? '[data-review]' : '.coding-' + field];
      area.value = value;
      if (field === 'status') area.change({target: area}); else area.input();
    },
    check(id, index) {const box = cards.find(card => card.id === id).checks[index]; box.checked = true; box.change();},
    export() {elements['coding-export'].click(); return exported.records;},
    value(id, field) {return cards.find(card => card.id === id).fields['.coding-' + field].value;},
  };
}

test('two tabs preserve drafts on other questions and other fields of the same question', () => {
  const s = storage(), a = tab(s), b = tab(s);
  a.edit('AI-01', 'draft', 'sqrt draft');
  b.edit('AI-03', 'draft', 'attention draft');
  a.edit('AI-01', 'notes', 'boundary notes');
  b.edit('AI-01', 'status', 'done');
  a.check('AI-01', 0);
  assert.equal(s.records()['AI-01'].draft, 'sqrt draft');
  assert.equal(s.records()['AI-01'].notes, 'boundary notes');
  assert.equal(s.records()['AI-01'].status, 'done');
  assert.deepEqual(s.records()['AI-01'].checks, ['0']);
  assert.equal(s.records()['AI-03'].draft, 'attention draft');
  assert.equal(b.value('AI-01', 'draft'), 'sqrt draft');
});

test('failed writes remain exportable and all pending fields survive a later retry', () => {
  const s = storage(), a = tab(s), b = tab(s);
  s.fail = true;
  a.edit('AI-01', 'draft', 'unsaved draft');
  a.edit('AI-03', 'notes', 'unsaved notes');
  assert.equal(a.export()['AI-01'].draft, 'unsaved draft');
  assert.equal(a.export()['AI-03'].notes, 'unsaved notes');
  s.fail = false;
  b.edit('AI-01', 'notes', 'other tab notes');
  a.edit('AI-03', 'status', 'review');
  assert.equal(s.records()['AI-01'].draft, 'unsaved draft');
  assert.equal(s.records()['AI-01'].notes, 'other tab notes');
  assert.equal(s.records()['AI-03'].notes, 'unsaved notes');
  assert.equal(s.records()['AI-03'].status, 'review');
});

test('exports retain only current question IDs', () => {
  const s = storage();
  s.setItem(key, JSON.stringify({'AI-02': {draft: 'removed question'}}));
  const a = tab(s);
  a.edit('AI-01', 'draft', 'current draft');
  assert.deepEqual(Object.keys(a.export()), ['AI-01', 'AI-03']);
});

test('failed migration is preserved through a successful edit retry', () => {
  const s = storage();
  s.setItem('sideinn:coding:legacy-ai-infra:v1', JSON.stringify({'OLD-01': {draft: 'legacy draft', notes: 'legacy notes'}}));
  s.fail = true;
  const a = tab(s);
  s.fail = false;
  a.edit('AI-03', 'draft', 'new draft');
  assert.equal(s.records()['AI-01'].draft, 'legacy draft');
  assert.equal(s.records()['AI-01'].notes, 'legacy notes');
});

test('malformed stored field types and URL fragments do not interrupt practice', () => {
  const s = storage(), a = tab(s, '#%E0%A4%A');
  s.setItem(key, JSON.stringify({'AI-03': {checks: {}, status: 'unknown', draft: 42, notes: []}}));
  a.edit('AI-01', 'draft', 'valid draft');
  assert.deepEqual(s.records()['AI-03'], {checks: [], status: 'todo', draft: '', notes: ''});
  assert.equal(a.export()['AI-01'].draft, 'valid draft');
});
