#!/usr/bin/env node
'use strict';
// Issue #232: read-only provenance and Git-blob integrity gate for the five
// October 29 railway directional candidates. Never writes to the checkout.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const root = path.resolve(process.argv[2] || '.');
const prefix = 'chatgpt_map_assets/';
const paths = {
  registry: prefix + 'manifests/connection_45_candidate_registry_2026-10-30.json',
  copied: prefix + 'candidates/rail_endpoints_and_t_2026-10-26/candidate_manifest.json',
  derived: prefix + 'generated/rail_directional_2026-10-29/manifest.json'
};
function file(rel) {
  if (path.isAbsolute(rel) || rel.split(/[\\/]/).includes('..')) throw Error('Unsafe path: ' + rel);
  return fs.readFileSync(path.join(root, rel));
}
function json(rel) { return JSON.parse(file(rel).toString('utf8')); }
function blobSha(rel) {
  const b = file(rel);
  return crypto.createHash('sha1').update(Buffer.from('blob ' + b.length + '\0')).update(b).digest('hex');
}
function eq(actual, expected, context) {
  if (actual !== expected) throw Error(context + ': expected ' + expected + ', got ' + actual);
}
function run() {
  const registry = json(paths.registry);
  const copied = json(paths.copied);
  const derived = json(paths.derived);
  const entries = registry.assets.filter(a => a.provenance_group === '2026-10-29_corrected_and_rotated');
  eq(entries.length, 5, 'derived registry count');
  eq(derived.items.length, 5, 'derived manifest count');
  const result = [];
  for (const item of derived.items) {
    const target = entries.find(a => a.asset_id === item.asset_id);
    if (!target) throw Error('Missing registry asset: ' + item.asset_id);
    const origin = copied.candidates.find(c => c.candidate_path === item.source_path);
    if (!origin) throw Error('Missing intermediate provenance: ' + item.source_path);
    eq(target.candidate_path, item.path, item.asset_id + ' output path');
    eq(target.git_blob_sha, item.output_git_blob_sha, item.asset_id + ' output manifest SHA');
    eq(target.source_id, origin.asset_id, item.asset_id + ' immediate source alias');
    eq(item.source_git_blob_sha, origin.git_blob_sha, item.asset_id + ' intermediate manifest SHA');
    eq(blobSha(origin.source_path), origin.git_blob_sha, item.asset_id + ' original Git blob');
    eq(blobSha(origin.candidate_path), origin.git_blob_sha, item.asset_id + ' copied Git blob');
    eq(blobSha(item.path), item.output_git_blob_sha, item.asset_id + ' derived Git blob');
    result.push({
      asset_id: item.asset_id, direction_mask: item.direction_mask,
      immediate_source_alias: target.source_id,
      original_source_id: origin.source_id,
      original_path: origin.source_path,
      intermediate_path: origin.candidate_path,
      output_path: item.path,
      original_blob_sha: origin.git_blob_sha,
      output_blob_sha: item.output_git_blob_sha,
      rotation_clockwise_quarter_turns: item.rotation_clockwise_quarter_turns,
      git_blob_integrity: 'PASS',
      original_game_fidelity: 'NOT_VERIFIED',
      visual_seams: 'NOT_VERIFIED',
      godot_runtime: 'NOT_RUN'
    });
  }
  eq(new Set(result.map(x => x.asset_id)).size, 5, 'unique asset IDs');
  console.log(JSON.stringify({issue: 232, status: 'PROVENANCE_AND_BLOB_SHA_PASS_ONLY', checked: result.length, results: result}, null, 2));
}
try { run(); } catch (e) { console.error('FAIL:', e.message); process.exitCode = 1; }
