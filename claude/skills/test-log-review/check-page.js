// Check a filled-in review page before publishing it.
//
// Usage: node check-page.js <page.html>
//
// Extracts the page's script by its <script> markers, renders it against a
// stub DOM and a stub answer store that refuses invalid document ids (as the
// real store does), then checks that every decision and item renders, that
// every answer key is a valid id, and that accept-all saves an answer for
// every unanswered entry while keeping answers already given.
'use strict';
const fs = require('fs');

const html = fs.readFileSync(process.argv[2], 'utf8');
const start = html.indexOf('<script>');
const end = html.lastIndexOf('</script>');
if (start < 0 || end < 0) { console.error('no <script> block'); process.exit(1); }
const src = html.slice(start + '<script>'.length, end);
// The page's script is evaluated on purpose: it is the review page this skill
// wrote, checked locally before it is published. Never run this on a page
// from anywhere else.
new Function(src); // syntax check: throws on a parse error

class N {
  constructor(t) { this.tagName = t.toUpperCase(); this.children = []; this.attrs = {}; this.className = ''; this.listeners = {}; this.value = ''; this.textContent = ''; this.parent = null; }
  setAttribute(k, v) { this.attrs[k] = v; }
  getAttribute(k) { return this.attrs[k]; }
  addEventListener(e, f) { (this.listeners[e] = this.listeners[e] || []).push(f); }
  append(...ks) { for (let k of ks) { if (k == null) continue; if (typeof k === 'string') { const t = new N('#text'); t.textContent = k; k = t; } k.parent = this; this.children.push(k); } }
  remove() { const p = this.parent; if (p) p.children = p.children.filter(c => c !== this); }
  all() { return this.children.flatMap(c => [c, ...c.all()]); }
  querySelectorAll(s) {
    if (s === '.card') return this.all().filter(n => n.className.split(' ').includes('card'));
    const m = s.match(/^\[data-saved="(.+)"\]$/);
    if (m) return this.all().filter(n => n.attrs['data-saved'] === m[1]);
    return [];
  }
  querySelector(s) { if (s.startsWith('#')) return this.all().find(n => n.attrs.id === s.slice(1)) || null; return this.querySelectorAll(s)[0] || null; }
}

const root = new N('body');
for (const id of ['meta', 'heading', 'lede', 'status', 'accept-all', 'checks', 'decisions', 'sections']) { const n = new N('div'); n.attrs.id = id; root.append(n); }
global.document = { title: '', createElement: t => new N(t), querySelector: s => root.querySelector(s), querySelectorAll: s => root.querySelectorAll(s), getElementById: id => root.querySelector('#' + id), activeElement: null };
const VALID = /^[A-Za-z0-9_\-.~:@+]+$/;
const store = {};
const db = { collection: () => ({
  doc: id => ({ set: async d => { if (!VALID.test(id)) throw new Error('invalid document id ' + id); store[id] = d; } }),
  onSnapshot: next => { setTimeout(() => next({ docs: [] }), 0); return () => {}; },
}) };
global.window = { claude: { use: async () => db } };

const failures = [];
const check = (ok, what) => { console.log((ok ? 'pass ' : 'FAIL ') + what); if (!ok) failures.push(what); };

eval(src + `
;(async () => {
  await new Promise(r => setTimeout(r, 20));
  check(ITEMS.length + DECISIONS.length > 0 && CHECKS.length > 0, 'the data block is filled in (items or decisions, and checks)');
  const cards = root.querySelectorAll('.card');
  check(cards.length === DECISIONS.length + ITEMS.length, 'every decision and item renders (' + cards.length + ' cards)');
  check(DECISIONS.every(d => d.opts.filter(o => o[3]).length === 1), 'every decision has exactly one recommended option');
  check(ITEMS.every(i => SECTIONS.some(s => s.id === i.sec)), 'every item names a known section');
  const ids = [...ITEMS.map(i => itemId(i.n)), ...DECISIONS.map(d => decId(d.id))];
  check(new Set(ids).size === ids.length, 'answer keys are unique');
  check(ids.every(i => VALID.test(i)), 'every answer key is a valid document id');
  const firstItem = ids.find(i => i.startsWith('item-'));
  const firstDec = DECISIONS[0];
  if (firstItem) answers[firstItem] = { verdict: 'flag' };
  const other = firstDec && firstDec.opts.find(o => !o[3]);
  if (other) answers[decId(firstDec.id)] = { choice: other[0] };
  await acceptAll();
  const preset = [firstItem, other && decId(firstDec.id)].filter(Boolean);
  check(ids.filter(i => !preset.includes(i)).every(i => store[i] && (store[i].verdict === 'approve' || store[i].choice)), 'accept-all saves every unanswered entry');
  check(!firstItem || answers[firstItem].verdict === 'flag', 'accept-all keeps a flag already given');
  check(!other || answers[decId(firstDec.id)].choice === other[0], 'accept-all keeps a non-recommended choice already made');
  check(DECISIONS.filter(d => !(other && d === firstDec)).every(d => store[decId(d.id)].choice === d.opts.find(o => o[3])[0]), 'accept-all picks the recommended option');
  process.exit(failures.length ? 1 : 0);
})();`);
