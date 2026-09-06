'use strict';

const { enrichScanResult: enrichV2 } = require('./mega-evidence');

const RANK = { unknown: 0, low: 1, caution: 2, high: 3 };
function clean(v, max = 700) { return String(v == null ? '' : v).replace(/\0/g, '').replace(/\s+/g, ' ').trim().slice(0, max); }
function risk(v) { const x = clean(v, 30).toLowerCase(); return Object.prototype.hasOwnProperty.call(RANK, x) ? x : 'unknown'; }
function uniq(items, keyFn, max = 20) { const out = [], seen = new Set(); for (const x of items || []) { const k = keyFn(x); if (!k || seen.has(k)) continue; seen.add(k); out.push(x); if (out.length >= max) break; } return out; }
function maxRisk(values) { return (values || []).reduce((best, x) => RANK[risk(x)] > RANK[best] ? risk(x) : best, 'unknown'); }
function weakAccountText(v) { return /low[_ -]?account[_ -]?metrics|minimal account history|few followers|only one follower|follower|following|new account|recent account|account age|joined/i.test(clean(v, 1200)); }
function noWarningText(v) { return /no obvious|no major warning|no strong impersonation|did not return a caution|did not return a high-risk|nothing suspicious/i.test(clean(v, 1200)); }
function semanticKey(v) { return clean(v, 800).toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/\b(the|a|an|this|that|profile|account|indicating|meaning|while|only)\b/g, ' ').replace(/\s+/g, ' ').trim(); }
function dedupeReasons(reasons) {
  const out = [];
  for (const r of reasons || []) {
    if (!r) continue;
    const title = clean(r.title || 'Signal', 180), detail = clean(r.detail || '', 500);
    if (!title && !detail) continue;
    const key = semanticKey(detail || title);
    if (out.some(x => {
      const k = semanticKey(x.detail || x.title);
      return key === k || (key.length > 45 && k.length > 45 && (key.includes(k) || k.includes(key)));
    })) continue;
    out.push({ ...r, title, detail });
    if (out.length >= 5) break;
  }
  return out;
}
function normalizedDomain(v) {
  const value = clean(v, 500).toLowerCase().replace(/^www\./, '');
  if (!value) return '';
  try { return new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`).hostname.toLowerCase().replace(/^www\./, ''); }
  catch (_) { return value.replace(/^https?:\/\//, '').split(/[\/?#]/)[0].replace(/^www\./, ''); }
}
function sanitizeDetectedElements(result) {
  const base = result && result.detectedElements && typeof result.detectedElements === 'object' ? result.detectedElements : {};
  const domains = uniq((base.domains || []).map(x => normalizedDomain(x)).filter(Boolean), x => x, 12);
  for (const u of base.urls || []) {
    const d = normalizedDomain(u);
    if (d && !domains.includes(d)) domains.push(d);
  }
  const domainSet = new Set(domains);
  const files = uniq((base.files || []).map(x => clean(x, 140)).filter(Boolean), x => x.toLowerCase(), 12).filter(name => {
    const lower = name.toLowerCase().replace(/^www\./, '');
    if (domainSet.has(lower)) return false;
    if (/^https?:\/\//i.test(lower) || /^@/.test(lower)) return false;
    return true;
  });
  return {
    ...base,
    urls: uniq((base.urls || []).map(x => clean(x, 600)).filter(Boolean), x => x.toLowerCase(), 12),
    domains,
    emails: uniq((base.emails || []).map(x => clean(x, 320)).filter(Boolean), x => x.toLowerCase(), 10),
    phones: uniq((base.phones || []).map(x => clean(x, 120)).filter(Boolean), x => x, 10),
    crypto: uniq((base.crypto || []).map(x => clean(x, 220)).filter(Boolean), x => x.toLowerCase(), 8),
    qr: uniq((base.qr || []).map(x => clean(x, 600)).filter(Boolean), x => x, 8),
    files,
    socialProfiles: uniq((base.socialProfiles || []).filter(Boolean), x => typeof x === 'string' ? x.toLowerCase() : JSON.stringify(x), 8),
    claimedBrands: uniq((base.claimedBrands || []).map(x => clean(x, 140)).filter(Boolean), x => x.toLowerCase(), 8)
  };
}
function confirmedEvidence(result) {
  const out = [];
  for (const rel of result.relationshipChecks || []) {
    if (rel && rel.positive && rel.status === 'confirmed') out.push({
      type: 'reciprocal-social-link', strength: 'strong', title: 'Website links back to the same social profile',
      detail: clean(rel.detail, 420), websiteDomain: clean(rel.websiteDomain, 253), platform: clean(rel.socialPlatform, 50), handle: clean(rel.socialHandle, 120)
    });
  }
  return uniq(out, x => `${x.type}:${x.websiteDomain || ''}:${x.platform || ''}:${x.handle || ''}`, 6);
}
function noWarningEvidence(result) {
  const out = [];
  const checks = Array.isArray(result.crossChecks) ? result.crossChecks : [];
  const socialLow = checks.find(x => x && x.type === 'social-profile' && risk(x.risk) === 'low');
  if (socialLow) out.push({
    type: 'social-check-low', title: 'No strong impersonation pattern found in the profile check',
    detail: clean(socialLow.summary, 360) || 'The specialized social-profile check did not return a caution or high-risk result.'
  });
  const urlLow = checks.find(x => x && x.type === 'url' && risk(x.risk) === 'low');
  if (urlLow) out.push({
    type: 'url-check-low', title: 'No major URL warning found in the website check',
    detail: clean(urlLow.summary, 360) || 'The specialized URL check did not return a caution or high-risk result.'
  });
  const messageLow = checks.find(x => x && x.type === 'message' && risk(x.risk) === 'low');
  if (messageLow) out.push({
    type: 'message-check-low', title: 'No major scam-language warning found in the visible text',
    detail: clean(messageLow.summary, 360) || 'The visible-message check did not return a caution or high-risk result.'
  });
  return uniq(out, x => x.type, 6);
}
function identityConsistency(result, positives) {
  const mismatches = result.brandMismatch && Array.isArray(result.brandMismatch.items) ? result.brandMismatch.items : [];
  if (mismatches.some(x => x && x.severity === 'high')) return { level: 'low', score: 0.18, label: 'Identity conflict', detail: 'A claimed identity conflicts with an observed sender or destination domain.' };
  const reciprocal = positives.find(x => x.type === 'reciprocal-social-link');
  if (reciprocal) return { level: 'high', score: 0.9, label: 'Strong identity consistency', detail: `${reciprocal.websiteDomain} links back to the same ${reciprocal.platform.toUpperCase()} profile @${reciprocal.handle}. This is strong consistency evidence, not proof of who controls the accounts.` };
  const hasSocial = Boolean(result.detectedElements && result.detectedElements.socialProfiles && result.detectedElements.socialProfiles.length);
  const hasWebsite = Boolean(result.detectedElements && ((result.detectedElements.urls && result.detectedElements.urls.length) || (result.detectedElements.domains && result.detectedElements.domains.length)));
  const unavailable = (result.relationshipChecks || []).some(x => x && x.status === 'unavailable');
  if (hasSocial && hasWebsite) return { level: 'medium', score: unavailable ? 0.5 : 0.56, label: 'Identity not confirmed', detail: unavailable ? 'A profile and website were detected, but their relationship could not be independently checked.' : 'A profile and website were detected, but a reciprocal link to the exact profile was not confirmed.' };
  return { level: 'unknown', score: 0.35, label: 'Identity not established', detail: 'There is not enough independent relationship evidence to establish identity consistency.' };
}
function augmentGraph(result, positives) {
  const graph = result.evidenceGraph && typeof result.evidenceGraph === 'object' ? result.evidenceGraph : { version: '3.1', nodes: [], edges: [] };
  const nodes = Array.isArray(graph.nodes) ? graph.nodes.map(x => ({ ...x })) : [];
  const edges = Array.isArray(graph.edges) ? graph.edges.map(x => ({ ...x })) : [];
  const nodeMap = new Map();
  for (const n of nodes) nodeMap.set(`${clean(n.type, 50)}:${clean(n.value, 500).toLowerCase()}`, n.id);
  const addNode = (type, value, source, extra = {}) => {
    value = clean(value, 500); if (!value) return null;
    const key = `${type}:${value.toLowerCase()}`; if (nodeMap.has(key)) return nodeMap.get(key);
    const id = `v3e${nodes.length + 1}`; nodes.push({ id, type, value, source, ...extra }); nodeMap.set(key, id); return id;
  };
  const edgeKeys = new Set(edges.map(e => `${e.from}:${e.to}:${e.relation}`));
  const addEdge = (from, to, relation, strength) => { if (!from || !to || from === to) return; const k = `${from}:${to}:${relation}`; if (edgeKeys.has(k)) return; edgeKeys.add(k); edges.push({ from, to, relation, ...(strength ? { strength } : {}) }); };
  for (const p of positives.filter(x => x.type === 'reciprocal-social-link')) {
    const d = addNode('domain', p.websiteDomain, 'relationship-check', { role: 'website' });
    const s = addNode('social', `${p.platform.toUpperCase()} @${p.handle}`, 'relationship-check', { platform: p.platform, handle: p.handle });
    addEdge(d, s, 'links_to_exact_profile', 'strong');
  }
  const elements = result.detectedElements || {};
  for (const f of elements.files || []) addNode('file', clean(f, 120), 'screenshot');
  return { version: '3.1', nodes: nodes.slice(0, 30), edges: edges.slice(0, 40) };
}
function recalcFinalRisk(result) {
  const analysisRisk = risk(result.analysis && result.analysis.risk);
  const checks = (result.crossChecks || []).map(x => risk(x && x.risk));
  const correlations = (result.correlations || []).filter(x => !weakAccountText(`${x && x.title || ''} ${x && x.detail || ''}`)).map(x => x && x.severity === 'high' ? 'high' : x && x.severity === 'caution' ? 'caution' : 'low');
  const mismatches = result.brandMismatch && Array.isArray(result.brandMismatch.items) ? result.brandMismatch.items : [];
  const mismatchRisk = mismatches.some(x => x && x.severity === 'high') ? 'high' : mismatches.length ? 'caution' : 'unknown';
  // The primary scanner may be the only source for a message, file or email.
  // Never discard its verdict while assembling the universal summary.
  return maxRisk([risk(result.safety && result.safety.status), risk(result.technicalCheck && result.technicalCheck.safety && result.technicalCheck.safety.status), analysisRisk, mismatchRisk, ...checks, ...correlations]);
}
function specificLimits(result) {
  const limits = [];
  const platform = clean(result.analysis && result.analysis.social_profile && result.analysis.social_profile.platform, 50) || clean(result.socialProfile && result.socialProfile.platform, 50);
  if (platform) {
    limits.push(`Who actually controls the ${platform} account`);
    limits.push('Historical username or ownership changes');
    limits.push('Private account activity that is not publicly visible');
    limits.push('Whether the platform has independently verified the organization');
  } else {
    if (result.detectedElements && result.detectedElements.emails && result.detectedElements.emails.length) limits.push('Who controls the detected mailbox');
    if (result.detectedElements && result.detectedElements.phones && result.detectedElements.phones.length) limits.push('Who owns the detected phone number');
    limits.push('Information not visible in the screenshot or public sources');
  }
  return uniq(limits, x => x.toLowerCase(), 4);
}
function upgradeMegaResult(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input) || input.error) return input;
  const detectedElements = sanitizeDetectedElements(input);
  const result = {
    ...input,
    detectedElements,
    orchestration: input.orchestration && detectedElements.files.length === 0
      ? { ...input.orchestration, contextualOnly: (input.orchestration.contextualOnly || []).filter(x => !/^File names visible/i.test(clean(x, 300))) }
      : input.orchestration
  };
  const positives = confirmedEvidence(result);
  const noWarnings = noWarningEvidence(result);
  const identity = identityConsistency(result, positives);
  const finalRisk = recalcFinalRisk(result);
  const account = result.accountContext || { maturity: 'unknown', note: null };
  const baseEx = result.explanation || {};
  let reasons = dedupeReasons((baseEx.reasons || []).filter(r => {
    const text = `${r && r.title || ''} ${r && r.detail || ''}`;
    return !weakAccountText(text) && !noWarningText(text);
  }));
  if (account.maturity === 'limited') reasons = dedupeReasons([...reasons, { severity: 'context', title: 'New or limited account history', detail: account.note || 'Limited history is useful context but is not evidence of impersonation by itself.' }]);

  let headline = clean(baseEx.headline, 500);
  let action = clean(baseEx.action, 600);
  if (finalRisk === 'low' && identity.level === 'high') {
    headline = account.maturity === 'limited'
      ? 'Profile and website are mutually consistent; the account still appears new.'
      : 'Profile and website show strong identity consistency.';
    action = 'No strong impersonation sign was found. Continue with normal caution and independently verify any sensitive payment, password or recovery request.';
  } else if (finalRisk === 'low' && identity.level === 'medium') {
    headline = 'No major safety warning was found, but the identity relationship was not independently confirmed.';
    action = 'Verify the account through an official website, app or other independent channel before any sensitive payment, password or recovery action.';
  } else if (finalRisk === 'low' && identity.level === 'unknown') {
    headline = 'No major safety warning was found, but the identity could not be established.';
    action = 'Continue only if the request was expected, and independently verify the sender before sharing sensitive information.';
  } else if (finalRisk === 'low' && !headline) {
    headline = 'No major warning was found in the checks that completed.';
  }

  const graph = augmentGraph(result, positives);
  const confidenceScore = identity.level === 'high' && finalRisk === 'low' ? 0.88 : Number(baseEx.confidence && baseEx.confidence.score) || 0.55;
  const confidenceLevel = confidenceScore >= 0.76 ? 'high' : confidenceScore >= 0.52 ? 'medium' : 'low';
  const explanation = {
    ...baseEx,
    verdict: finalRisk,
    headline,
    reasons,
    action,
    confidence: {
      level: confidenceLevel,
      score: Number(confidenceScore.toFixed(2)),
      explanation: identity.level === 'high'
        ? 'Independent relationship evidence supports the identity consistency result.'
        : clean(baseEx.confidence && baseEx.confidence.explanation, 420) || 'The result combines the evidence and specialized checks that completed.'
    },
    couldNotVerify: specificLimits(result)
  };

  const shareSummary = result.shareSummary && typeof result.shareSummary === 'object' ? { ...result.shareSummary } : {};
  shareSummary.schema = 3;
  shareSummary.verdict = finalRisk;
  shareSummary.headline = headline;
  shareSummary.confidence = confidenceLevel;
  shareSummary.identityConsistency = { level: identity.level, label: identity.label };
  shareSummary.positiveEvidence = positives.slice(0, 2).map(x => ({ title: x.title, detail: x.detail }));
  shareSummary.noWarningEvidence = noWarnings.slice(0, 2).map(x => ({ title: x.title, detail: x.detail }));
  shareSummary.note = 'Shared summary only. Run a fresh scan to verify the current result.';

  return {
    ...result,
    evidenceGraph: graph,
    positiveEvidence: positives,
    noWarningEvidence: noWarnings,
    verifiedRelationships: positives.filter(x => x.type === 'reciprocal-social-link').map(x => ({
      type: 'website-social', websiteDomain: x.websiteDomain, platform: x.platform, handle: x.handle, status: 'confirmed'
    })),
    identityConsistency: identity,
    accountContext: account,
    explanation,
    shareSummary,
    megaScanner: {
      ...(result.megaScanner || {}),
      version: '3.1',
      finalRisk,
      evidenceCount: graph.nodes.length,
      positiveEvidenceCount: positives.length,
      noWarningEvidenceCount: noWarnings.length,
      identityConsistency: identity.level,
      correlationMode: 'multi-element + verified relationship'
    }
  };
}
function enrichScanResult(args) {
  return upgradeMegaResult(enrichV2(args));
}

module.exports = { enrichScanResult, upgradeMegaResult, dedupeReasons, identityConsistency, recalcFinalRisk, sanitizeDetectedElements, confirmedEvidence, noWarningEvidence };
