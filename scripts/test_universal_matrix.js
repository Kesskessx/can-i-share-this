#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const MATRIX_PATH = path.join(ROOT, 'tests', 'universal_safety_matrix.json');
const HOME_PATH = path.join(ROOT, 'dist', 'index.html');

function fail(message) {
  console.error('FAIL:', message);
  process.exitCode = 1;
}

function extractFunction(source, name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  if (start < 0) throw new Error(`Missing ${marker} in dist/index.html`);
  const braceStart = source.indexOf('{', start);
  if (braceStart < 0) throw new Error(`Malformed ${marker}`);
  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let i = braceStart; i < source.length; i += 1) {
    const ch = source[i];
    if (quote) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === quote) quote = null;
      continue;
    }
    if (ch === "'" || ch === '"' || ch === '`') {
      quote = ch;
      continue;
    }
    if (ch === '{') depth += 1;
    else if (ch === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`Unbalanced function ${name}`);
}

function parsedHost(url) {
  try {
    return new URL(url).hostname.toLowerCase().replace(/^www\./, '');
  } catch (_) {
    return '';
  }
}

function fixtureMeta(fixture) {
  if (!fixture || !fixture.sensitive_category) return {};
  const map = {
    adult: { pageTitle: 'Adult videos 18+ adult content', pageDescription: 'adult videos' },
    weapons: { pageTitle: 'Firearms ammunition gun store', pageDescription: 'firearm dealer' },
    drugs: { pageTitle: 'Cannabis dispensary THC products', pageDescription: 'recreational cannabis' },
    'file-sharing': { pageTitle: 'Torrent download magnet link', pageDescription: 'torrent files' },
  };
  return map[fixture.sensitive_category] || {};
}

const matrix = JSON.parse(fs.readFileSync(MATRIX_PATH, 'utf8'));
const html = fs.readFileSync(HOME_PATH, 'utf8');

const sandbox = { input: { value: '' }, URL };
vm.createContext(sandbox);

const functionNames = [
  'cistSensitiveHost',
  'cistTermHits',
  'cistSensitiveCategory',
  'cistHostMatches',
  'cistLinkType',
];

vm.runInContext(functionNames.map((name) => extractFunction(html, name)).join('\n'), sandbox);

let checked = 0;
let skipped = 0;

for (const test of matrix.cases) {
  const expected = test.expected || {};
  if (expected.input_type !== 'url' || !expected.content) {
    skipped += 1;
    continue;
  }

  sandbox.input.value = test.input;
  const fixture = test.fixture || {};
  const finalUrl = fixture.final_url || test.input;
  const data = {
    finalUrl,
    finalHost: parsedHost(finalUrl),
    redirects: fixture.redirects || [],
    ...fixtureMeta(fixture),
  };

  const base = sandbox.cistLinkType(data);
  const sensitive = sandbox.cistSensitiveCategory(data);
  const effectiveContent = sensitive ? sensitive.typeLabel : base.label;
  const effectivePlatform = sensitive ? '' : (base.platform || '');

  if (effectiveContent !== expected.content) {
    fail(`${test.id}: content expected "${expected.content}", got "${effectiveContent}"`);
  }

  if (expected.platform !== undefined && expected.platform !== null) {
    if (effectivePlatform !== expected.platform) {
      fail(`${test.id}: platform expected "${expected.platform}", got "${effectivePlatform}"`);
    }
  }

  if (fixture.final_url && expected.destination && expected.destination !== 'unknown-until-resolved') {
    const host = parsedHost(fixture.final_url);
    if (host !== expected.destination) {
      fail(`${test.id}: fixture destination expected "${expected.destination}", got "${host}"`);
    }
  }
  checked += 1;
}

if (!process.exitCode) {
  console.log(`Universal classifier matrix: ${checked} deterministic URL cases passed; ${skipped} non-classifier cases reserved for API/privacy/live smoke tests.`);
}
