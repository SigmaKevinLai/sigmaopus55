// Screenshot every zh-Hant page at desktop and mobile widths into docs/*.png (gitignored).
async (page) => {
 const base = new URL('/', page.url()).href;
 const routes = ['', 'about/', 'products/', 'technology/', 'sustainability/', 'support/', 'locations/', 'contact/', 'en/'];
 const out = [];
 for (const [w, tag] of [[1440, 'd'], [390, 'm']]) {
  await page.setViewportSize({ width: w, height: 900 });
  for (const r of routes) {
   await page.goto(base + r, { waitUntil: 'networkidle' });
   await page.evaluate(() => document.fonts.ready);
   const name = (r.replace(/\//g, '') || 'home');
   await page.screenshot({ path: `docs/shot-${tag}-${name}.png`, fullPage: true });
   out.push(name + ':' + await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  }
 }
 return out.join(' ');
}
