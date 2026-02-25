/**
 * Bundle script – copies the web-app assets from the repo root into www/
 * so that Capacitor can sync them into the Android project.
 *
 * Run automatically via "prebuild" hook in package.json.
 * Can also be run directly: node scripts/bundle.js
 */
'use strict';

const fs   = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..'); // repo root
const WWW  = path.resolve(__dirname, '..', 'www'); // mobile-capacitor/www/

// Files / directories to copy from repo root → www/
const ASSETS = [
  'index.html',
  'sw.js',
  'language_selection.html',
  'anleitung.html',
  'Lernprogramm_Bibel.csv',
  'elberfelder_1905.csv',
  'kjv_1769.csv',
  'app',
  'preview',
];

// Re-create the www/ output directory
if (fs.existsSync(WWW)) {
  fs.rmSync(WWW, { recursive: true, force: true });
}
fs.mkdirSync(WWW, { recursive: true });

// Critical assets that must be present – abort if any are missing.
const REQUIRED = ['index.html', 'sw.js', 'app'];

let copied = 0;
const missing = [];
for (const asset of ASSETS) {
  const src = path.join(ROOT, asset);
  const dst = path.join(WWW, asset);
  if (!fs.existsSync(src)) {
    console.warn(`[bundle] SKIP (not found): ${asset}`);
    if (REQUIRED.includes(asset)) missing.push(asset);
    continue;
  }
  fs.cpSync(src, dst, { recursive: true });
  copied++;
  console.log(`[bundle] Copied: ${asset}`);
}

if (missing.length > 0) {
  console.error(`[bundle] ERROR – required asset(s) not found: ${missing.join(', ')}`);
  process.exit(1);
}

console.log(`[bundle] Done – ${copied} asset(s) bundled into www/`);
