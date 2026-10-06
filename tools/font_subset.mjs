// Regenerate the self-hosted Noto Sans TC subset from every generated page.
// Development-only setup (not committed, not a runtime dependency):
//   mkdir -p /tmp/fontwork && cd /tmp/fontwork && npm i subset-font@2
//   curl -L -o NotoSansTC.ttf "https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf"
// Run: NODE_PATH=/tmp/fontwork/node_modules node tools/font_subset.mjs [/tmp/fontwork/NotoSansTC.ttf]
// License: SIL OFL — assets/fonts/OFL-NotoSansTC.txt.
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const subsetFont = require(require.resolve('subset-font', { paths: [process.env.NODE_PATH || '/tmp/fontwork/node_modules'] }));
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = process.argv[2] || '/tmp/fontwork/NotoSansTC.ttf';
const files = JSON.parse(readFileSync(path.join(root, 'tools/generated.json'), 'utf8'));
let text = files.filter(f => f.endsWith('.html')).map(f => readFileSync(path.join(root, f), 'utf8')).join('');
text += readFileSync(path.join(root, 'assets/site.js'), 'utf8');
const chars = new Set([...text].filter(c => c.codePointAt(0) > 0x7f));
for (let c = 0x20; c < 0x7f; c++) chars.add(String.fromCodePoint(c));
const out = await subsetFont(readFileSync(source), [...chars].join(''), {
  targetFormat: 'woff2',
  variationAxes: { wght: { min: 400, max: 800 } },
});
writeFileSync(path.join(root, 'assets/fonts/noto-tc-core.woff2'), out);
console.log(`noto-tc-core.woff2: ${out.length} bytes, ${chars.size} characters`);
