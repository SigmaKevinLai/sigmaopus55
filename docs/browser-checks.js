// Multi-page interaction, accessibility and layout checks. Run through docs/run-browser-checks.py.
// The base URL is the page already opened by the runner.
async (page) => {
 const base = new URL('./', page.url()).href.replace(/(\/(zh-hans|en|ja|about|products|technology|sustainability|support|locations|contact)\/)+$/, '/');
 const fail = m => { throw new Error(m); };
 const log = [];
 const errors = [];
 page.on('pageerror', e => errors.push(e.message));
 page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
 const routes = ['', 'about/', 'products/', 'technology/', 'sustainability/', 'support/', 'locations/', 'contact/'];

 // 1. Every page, four widths: no horizontal overflow, single h1, touch targets.
 for (const w of [320, 390, 768, 1440]) {
  await page.setViewportSize({ width: w, height: 900 });
  for (const r of routes) {
   await page.goto(base + r, { waitUntil: 'load' });
   const res = await page.evaluate(() => ({
    over: document.documentElement.scrollWidth - innerWidth,
    h1: document.querySelectorAll('h1').length,
    small: [...document.querySelectorAll('a,button,summary,select,input,textarea')].filter(el => {
     const b = el.getBoundingClientRect(); if (!b.width || el.closest('p,li:not(.location),dd,address,td,.crumbs,.footer-bottom,.site-footer')) return false;
     return b.height < 24 || b.width < 24;
    }).map(el => el.outerHTML.slice(0, 60))
   }));
   if (res.over > 0) fail(`${r || 'home'} overflows by ${res.over}px at ${w}`);
   if (res.h1 !== 1) fail(`${r} h1 count ${res.h1}`);
   if (res.small.length) fail(`${r} small targets at ${w}: ${res.small.join(' | ')}`);
  }
 }
 log.push('layout 4 widths × 8 pages');

 // 2. Mobile menu: open, focus, Escape restores focus, aria state.
 await page.setViewportSize({ width: 390, height: 844 });
 await page.goto(base + 'about/');
 const btn = page.locator('.menu-button');
 await btn.click();
 if (await btn.getAttribute('aria-expanded') !== 'true') fail('menu not expanded');
 if (!await page.locator('#primary-nav').isVisible()) fail('menu not visible');
 if (!await page.evaluate(() => document.activeElement.closest('#primary-nav') !== null)) fail('focus not moved into menu');
 if (await page.locator('#primary-nav a[aria-current="page"]').textContent() !== '關於新格') fail('aria-current wrong');
 await page.keyboard.press('Escape');
 if (await btn.getAttribute('aria-expanded') !== 'false') fail('Escape did not close');
 if (!await page.evaluate(() => document.activeElement.classList.contains('menu-button'))) fail('focus not restored');
 log.push('mobile menu');

 // 3. Language switcher reaches the same route in each language, placeholders link back.
 await page.setViewportSize({ width: 1440, height: 900 });
 await page.goto(base + 'products/');
 await page.locator('.lang-menu summary').click();
 await page.locator('.lang-menu a[hreflang="en"]').click();
 await page.waitForURL(/\/en\/products\/$/);
 if (await page.getAttribute('html', 'lang') !== 'en') fail('en lang attr');
 if (!await page.locator('meta[name=robots][content=noindex]').count()) fail('placeholder must be noindex');
 await page.locator('main a[hreflang="zh-Hant"]').click();
 await page.waitForURL(/\/products\/$/);
 if (page.url().includes('/en/')) fail('placeholder back-link wrong');
 log.push('language switcher');

 // 4. Products: comparison highlights differences.
 await page.goto(base + 'products/');
 await page.selectOption('[data-compare-a]', 'ADC 14');
 await page.selectOption('[data-compare-b]', 'ADC 12');
 const status = await page.textContent('[data-compare-status]');
 if (!status.includes('6 項')) fail('ADC14 vs ADC12 should differ in 6 elements: ' + status);
 if (await page.locator('td.is-diff').count() !== 12) fail('diff cell count');
 log.push('alloy comparison');

 // 5. Support: search filters, highlights, empty state.
 await page.goto(base + 'support/');
 await page.fill('#qa-search', '氣孔');
 await page.waitForTimeout(300);
 const visible = await page.locator('[data-qa]:visible').count();
 if (visible !== 2) fail('search 氣孔 visible ' + visible);
 if (!await page.locator('mark').count()) fail('no highlight');
 if (!(await page.textContent('[data-qa-status]')).includes(`${visible}`)) fail('status count');
 await page.fill('#qa-search', 'zzzz');
 await page.waitForTimeout(300);
 if (!await page.locator('[data-qa-empty]').isVisible()) fail('empty state');
 await page.fill('#qa-search', '');
 await page.waitForTimeout(300);
 if (await page.locator('[data-qa]:visible').count() !== 37) fail('reset');
 log.push('Q&A search');

 // 6. Locations filter.
 await page.goto(base + 'locations/');
 await page.click('[data-filter="base"]');
 if (await page.locator('.location:visible').count() !== 9) fail('9 production bases expected');
 await page.click('[data-filter="all"]');
 if (await page.locator('.location:visible').count() !== 14) fail('14 locations expected');
 log.push('locations filter');

 // 7. Contact: validation, then mailto with prefilled content.
 await page.goto(base + 'contact/?topic=supply');
 if (await page.inputValue('select[name=topic]') !== 'supply') fail('topic param');
 await page.click('.inquiry button[type=submit]');
 if (!await page.locator('[data-form-error]').isVisible()) fail('error summary');
 if (await page.evaluate(() => document.activeElement.name) !== 'company') fail('focus first invalid');
 if (await page.locator('[aria-invalid=true]').count() !== 4) fail('4 invalid fields expected');
 await page.fill('[name=company]', '測試公司'); await page.fill('[name=name]', '王小明');
 await page.fill('[name=email]', 'bad'); await page.fill('[name=message]', '需要 ADC 12 報價');
 await page.click('.inquiry button[type=submit]');
 if (await page.getAttribute('[name=email]', 'aria-invalid') !== 'true') fail('email format');
 await page.fill('[name=email]', 'buyer@example.com');
 const nav = await page.evaluate(() => new Promise(res => {
  const form = document.querySelector('[data-inquiry]');
  form.addEventListener('submit', () => setTimeout(() => res(document.querySelector('[data-mail-body]').value), 0));
  form.requestSubmit();
 }));
 if (!nav.includes('收件人：info@sigmasha.com') || !nav.includes('原料供應') || !nav.includes('ADC 12')) fail('mail body ' + nav);
 if (!await page.locator('[data-mail-fallback]').isVisible()) fail('fallback visible');
 log.push('contact form');

 // 8. axe on every zh-Hant page and one placeholder (if bundle available locally).
 {
  for (const r of [...routes, 'en/']) {
   await page.goto(base + r);
   await page.addScriptTag({ path: '/tmp/sigma-axe.min.js' });
   const v = await page.evaluate(async () => (await axe.run(document, { resultTypes: ['violations'] })).violations.map(x => `${x.id}(${x.nodes.length})`));
   if (v.length) fail(`axe ${r || 'home'}: ${v.join(', ')}`);
  }
  log.push('axe 9 pages: 0 violations');
 }

 // 9. No-JS baseline: content visible, enhancements hidden.
 const ctx = await page.context().browser().newContext({ javaScriptEnabled: false });
 const nj = await ctx.newPage();
 await nj.goto(base + 'support/');
 if (await nj.locator('[data-qa-search]').isVisible()) fail('search should stay hidden without JS');
 await nj.locator('#al-1 summary').click();
 if (!await nj.locator('#al-1 .qa-body').isVisible()) fail('details should work without JS');
 await nj.goto(base + 'products/');
 if (await nj.locator('#adc-table tbody tr').count() !== 5) fail('table no-JS');
 await ctx.close();
 log.push('no-JS baseline');

 if (errors.length) fail('console/page errors: ' + errors.join(' | '));
 return 'PASS ' + log.join('; ');
}
