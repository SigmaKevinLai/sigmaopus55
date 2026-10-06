'use strict';
/* SIGMA Group site behaviour. Progressive enhancement: every page works without JS. */
(() => {
 const $ = (s, r = document) => r.querySelector(s);
 const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
 const year = $('[data-year]'); if (year) year.textContent = new Date().getFullYear();

 /* ---------- mobile menu */
 const menuBtn = $('.menu-button'), nav = $('#primary-nav');
 if (menuBtn && nav) {
  const compact = matchMedia('(max-width:980px)');
  const setOpen = open => {
   menuBtn.setAttribute('aria-expanded', String(open));
   menuBtn.setAttribute('aria-label', open ? menuBtn.dataset.close : menuBtn.dataset.open);
   nav.classList.toggle('is-open', open);
   document.body.style.overflow = open ? 'hidden' : '';
   if (open) nav.querySelector('a').focus();
  };
  menuBtn.addEventListener('click', () => setOpen(menuBtn.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('keydown', ev => {
   if (ev.key !== 'Escape') return;
   if (menuBtn.getAttribute('aria-expanded') === 'true') { setOpen(false); menuBtn.focus(); }
   const lang = $('[data-lang-menu][open]'); if (lang) { lang.open = false; lang.querySelector('summary').focus(); }
  });
  nav.addEventListener('keydown', ev => {
   if (ev.key !== 'Tab' || !compact.matches || menuBtn.getAttribute('aria-expanded') !== 'true') return;
   const items = [...$$('a', nav), menuBtn], first = items[0], last = items[items.length - 2];
   if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); menuBtn.focus(); }
   if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); menuBtn.focus(); }
  });
  compact.addEventListener('change', () => setOpen(false));
 }
 /* language menu closes on outside click */
 document.addEventListener('click', ev => {
  $$('[data-lang-menu][open]').forEach(d => { if (!d.contains(ev.target)) d.open = false; });
 });

 /* ---------- products: section TOC highlight */
 const tocLinks = $$('.toc a');
 if (tocLinks.length && 'IntersectionObserver' in window) {
  const map = new Map(tocLinks.map(a => [a.getAttribute('href').slice(1), a]));
  const io = new IntersectionObserver(entries => {
   entries.forEach(en => {
    if (!en.isIntersecting) return;
    tocLinks.forEach(a => a.removeAttribute('aria-current'));
    const a = map.get(en.target.id); if (a) a.setAttribute('aria-current', 'location');
   });
  }, { rootMargin: '-30% 0px -60% 0px' });
  map.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
 }

 /* ---------- products: alloy comparison (reads the visible table) */
 const compare = $('[data-compare]');
 if (compare) {
  const tableEl = $('#adc-table'), a = $('[data-compare-a]', compare), b = $('[data-compare-b]', compare), status = $('[data-compare-status]', compare);
  const names = $$('thead th', tableEl).slice(1).map(th => th.textContent.trim());
  a.value = 'ADC 12'; b.value = 'ADC 10';
  const row = n => $(`tr[data-alloy="${CSS.escape(n)}"]`, tableEl);
  const update = () => {
   $$('tr', tableEl).forEach(tr => tr.classList.remove('is-compared'));
   $$('td.is-diff', tableEl).forEach(td => td.classList.remove('is-diff'));
   const ra = row(a.value), rb = row(b.value);
   if (a.value === b.value) { ra.classList.add('is-compared'); status.textContent = '兩邊為同一牌號，請選擇另一個牌號比較。'; return; }
   ra.classList.add('is-compared'); rb.classList.add('is-compared');
   const ca = $$('td', ra), cb = $$('td', rb), diff = [];
   ca.forEach((td, i) => { if (td.textContent !== cb[i].textContent) { td.classList.add('is-diff'); cb[i].classList.add('is-diff'); diff.push(names[i]); } });
   status.textContent = `${a.value} 與 ${b.value}：${diff.length} 項元素範圍不同（${diff.join('、') || '無'}）。表格中已標示。`;
  };
  [a, b].forEach(s => s.addEventListener('change', update));
  compare.hidden = false; update();
 }

 /* ---------- support: Q&A search */
 const search = $('[data-qa-search]');
 if (search) {
  const input = $('input', search), status = $('[data-qa-status]'), empty = $('[data-qa-empty]');
  const items = $$('[data-qa]'), groups = $$('[data-qa-group]');
  items.forEach(d => { d.dataset.text = d.textContent.toLowerCase(); });
  const total = items.length;
  let timer;
  const clearMarks = () => $$('mark', document).forEach(m => m.replaceWith(m.textContent));
  const highlight = (el, term) => {
   const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), nodes = [];
   while (walker.nextNode()) nodes.push(walker.currentNode);
   nodes.forEach(n => {
    const i = n.data.toLowerCase().indexOf(term); if (i < 0) return;
    const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + term.length);
    const m = document.createElement('mark'); r.surroundContents(m);
   });
  };
  const run = () => {
   clearMarks(); $$('[data-qa]').forEach(d => d.normalize());
   const term = input.value.trim().toLowerCase();
   let shown = 0;
   items.forEach(d => {
    const hit = !term || d.dataset.text.includes(term);
    d.hidden = !hit; if (hit) shown++;
    if (term && hit) { d.open = true; highlight(d, term); } else if (!term) d.open = false;
   });
   groups.forEach(g => { g.hidden = $$('[data-qa]', g).every(d => d.hidden); });
   empty.hidden = shown > 0;
   status.textContent = term ? `找到 ${shown} 則相關問答` : `共 ${total} 則問答`;
  };
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(run, 150); });
  search.hidden = false;
  const q = new URLSearchParams(location.search).get('q'); if (q) { input.value = q; run(); }
  if (location.hash) { const t = document.getElementById(location.hash.slice(1)); if (t && t.matches('details')) t.open = true; }
 }

 /* ---------- locations filter */
 const filter = $('[data-loc-filter]');
 if (filter) {
  const buttons = $$('button', filter), cards = $$('.location'), status = $('[data-loc-status]');
  buttons.forEach(btn => btn.addEventListener('click', () => {
   buttons.forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
   let n = 0;
   cards.forEach(c => { const show = btn.dataset.filter === 'all' || c.dataset.kind === btn.dataset.filter; c.hidden = !show; if (show) n++; });
   $$('[data-loc-group]').forEach(g => { g.hidden = btn.dataset.filter !== 'all' && g.dataset.locGroup !== btn.dataset.filter; });
   status.textContent = `顯示 ${n} 個據點`;
  }));
  filter.hidden = false;
 }

 /* ---------- contact form → prefilled email */
 const form = $('[data-inquiry]');
 if (form) {
  const params = new URLSearchParams(location.search), topic = form.elements.topic;
  if (params.get('topic') && [...topic.options].some(o => o.value === params.get('topic'))) topic.value = params.get('topic');
  const errorBox = $('[data-form-error]', form), fallback = $('[data-mail-fallback]', form), bodyBox = $('[data-mail-body]', form);
  const labels = { company: '公司名稱', name: '聯絡人', email: '電子郵件', message: '需求說明' };
  const fieldError = el => {
   const v = el.value.trim();
   if (el.required && !v) return `請填寫${labels[el.name] || '此欄位'}`;
   if (el.type === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return '請輸入有效的電子郵件地址，例如 name@company.com';
   return '';
  };
  const show = (el, msg) => {
   const label = el.closest('.field'); let note = $('.field-error', label);
   if (msg) {
    if (!note) { note = document.createElement('span'); note.className = 'field-error'; note.id = `err-${el.name}`; label.append(note); }
    note.textContent = msg; el.setAttribute('aria-invalid', 'true'); el.setAttribute('aria-describedby', note.id);
   } else { if (note) note.remove(); el.removeAttribute('aria-invalid'); el.removeAttribute('aria-describedby'); }
  };
  $$('input,textarea', form).forEach(el => el.addEventListener('blur', () => { if (el.hasAttribute('aria-invalid') || el.value) show(el, fieldError(el)); }));
  form.addEventListener('input', () => { fallback.hidden = true; });
  form.addEventListener('submit', ev => {
   ev.preventDefault();
   const fields = $$('input:not([readonly]),textarea:not([readonly]),select', form).filter(el => el.name);
   const bad = fields.map(el => [el, fieldError(el)]).filter(([el, msg]) => { show(el, msg); return msg; });
   if (bad.length) { errorBox.textContent = `有 ${bad.length} 個欄位需要修正。`; errorBox.hidden = false; bad[0][0].focus(); return; }
   errorBox.hidden = true;
   const f = form.elements, topicText = topic.options[topic.selectedIndex].text;
   const body = [`詢問類型：${topicText}`, `公司名稱：${f.company.value.trim()}`, `聯絡人：${f.name.value.trim()}`, `電子郵件：${f.email.value.trim()}`,
    `電話：${f.phone.value.trim() || '—'}`, `國家／地區：${f.region.value.trim() || '—'}`, `合金牌號／月需求量：${f.spec.value.trim() || '—'}`, '', '需求說明：', f.message.value.trim()].join('\n');
   const subject = `【網站詢問】${topicText}－${f.company.value.trim()}`;
   const to = form.getAttribute('action').replace('mailto:', '');
   bodyBox.value = `收件人：${to}\n主旨：${subject}\n\n${body}`;
   fallback.hidden = false;
   location.href = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
  const copy = $('[data-copy]', form), copyStatus = $('[data-copy-status]', form);
  copy.addEventListener('click', async () => {
   try { await navigator.clipboard.writeText(bodyBox.value); copyStatus.textContent = '已複製'; }
   catch { bodyBox.select(); copyStatus.textContent = '請按 Ctrl+C（⌘C）複製已選取的內容'; }
  });
 }
})();
