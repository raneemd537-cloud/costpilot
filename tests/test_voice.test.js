const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(new URL('../web/app.js', `file://${__filename}`), 'utf8');
const voiceStart = source.indexOf('function setupVoice() {');
const populateStart = source.indexOf('function populateVoice(text) {');
const populateEnd = source.indexOf('\nasync function openSharedDialog', populateStart);
assert.ok(voiceStart >= 0 && populateStart > voiceStart && populateEnd > populateStart, 'voice functions are present');
const voiceFunction = source.slice(voiceStart, populateStart);
const populateFunction = source.slice(populateStart, populateEnd);

function createVoiceRuntime({ startError = null } = {}) {
  const state = { lang: 'ar', recognition: null, recording: false, voiceStarting: false,
    voiceStopping: false, voiceAbort: false, voiceTranscript: '', voiceErrorMessage: '' };
  const classes = new Set();
  const button = { attributes: {}, innerHTML: '', classList: {
    add: value => classes.add(value), remove: value => classes.delete(value),
    contains: value => classes.has(value),
  }, setAttribute(name, value) { this.attributes[name] = value; } };
  const status = { textContent: '' };
  const populated = [];
  class FakeRecognition {
    static instances = [];
    constructor() { this.results = []; FakeRecognition.instances.push(this); }
    start() { if (startError) throw new Error('start failed'); this.onstart?.(); }
    stop() { this.stopped = true; this.onend?.(); }
    abort() { this.aborted = true; this.onend?.(); }
  }
  const context = {
    window: { SpeechRecognition: FakeRecognition }, state,
    $: selector => selector === '#voiceButton' ? button : status,
    t: key => `<${key}>`, populateVoice: text => populated.push(text),
  };
  vm.runInNewContext(`${voiceFunction}; globalThis.runVoice = setupVoice;`, context);
  return { run: context.runVoice, state, button, status, populated, FakeRecognition, classes };
}

test('voice final transcript populates fields and stop restores the control', () => {
  const app = createVoiceRuntime();
  app.run();
  const recognition = app.FakeRecognition.instances[0];
  assert.equal(recognition.lang, 'ar');
  assert.equal(app.button.attributes['aria-pressed'], 'true');
  recognition.results = [{ 0: { transcript: '٤ قطع' }, isFinal: true }];
  recognition.onresult();
  assert.equal(app.populated[0], '٤ قطع');
  app.run();
  assert.equal(recognition.stopped, true);
  assert.equal(app.button.attributes['aria-pressed'], 'false');
  assert.equal(app.state.recording, false);
  assert.equal(app.status.textContent, '<transcribed>');
});

test('voice permission failures restore the control and show a specific message', () => {
  const app = createVoiceRuntime();
  app.run();
  app.FakeRecognition.instances[0].onerror({ error: 'not-allowed' });
  assert.equal(app.button.attributes['aria-pressed'], 'false');
  assert.equal(app.status.textContent, '<permissionVoice>');
  assert.equal(app.state.recording, false);
});

test('synchronous microphone start errors leave voice input reusable', () => {
  const app = createVoiceRuntime({ startError: true });
  app.run();
  assert.equal(app.button.attributes['aria-pressed'], 'false');
  assert.equal(app.status.textContent, '<voiceError>');
  assert.equal(app.state.recognition, null);
});

test('populateVoice extracts quantities, prices, discounts, and currency in English and Arabic', () => {
  const fields = {};
  const state = { draft: {} };
  const context = {
    state,
    $: selector => {
      const match = selector.match(/name="([^"]+)"/);
      if (!match) return null;
      const name = match[1];
      fields[name] = fields[name] || { value: '', classList: { add() {} } };
      return fields[name];
    },
  };
  vm.runInNewContext(`${populateFunction}; globalThis.runPopulate = populateVoice;`, context);

  // Arabic test with number before unit: '٤ قطع'
  context.runPopulate('منتج: كوب قهوة ٤ قطع سعر القطعة ١٢ سعر البيع ٢٠ خصم ٥٪ شيكل');
  assert.equal(state.draft.name, 'كوب قهوة');
  assert.equal(state.draft.quantity, '4');
  assert.equal(state.draft.unit_cost, '12');
  assert.equal(state.draft.selling_price, '20');
  assert.equal(state.draft.discount_percent, '5');
  assert.equal(state.draft.currency, 'ILS');

  // English test with number before unit: '50 pieces'
  state.draft = {};
  context.runPopulate('product: Ceramic Bowl 50 pieces unit cost 10 selling price 25 discount 10% USD');
  assert.equal(state.draft.name, 'Ceramic Bowl');
  assert.equal(state.draft.quantity, '50');
  assert.equal(state.draft.unit_cost, '10');
  assert.equal(state.draft.selling_price, '25');
  assert.equal(state.draft.discount_percent, '10');
  assert.equal(state.draft.currency, 'USD');
});
