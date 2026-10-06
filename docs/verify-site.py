"""Static integrity checks for the generated multi-page site.
Run: python3 docs/verify-site.py [--source]
  --source  also re-fetch the ADC table from the previous company website and compare 40 values.
No dependencies.
"""
from pathlib import Path
from html.parser import HTMLParser
import json, re, sys, urllib.parse, urllib.request

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / 'tools'))
from site_data import ADC, EMAIL  # noqa: E402

files = json.loads((root / 'tools/generated.json').read_text())
pages = [f for f in files if f.endswith('.html')]
assert len(pages) == 33, f'Expected 32 language pages + 404, got {len(pages)}'


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = []; self.refs = []; self.links = []; self.h1 = 0; self.lang = None; self.main = 0
        self.imgs_no_alt = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'h1': self.h1 += 1
        if tag == 'main': self.main += 1
        if tag == 'img' and 'alt' not in a: self.imgs_no_alt += 1
        if 'id' in a: self.ids.append(a['id'])
        for k in ('href', 'src'):
            if k in a: self.links.append(a[k])
        for k in ('for', 'aria-controls', 'aria-labelledby', 'aria-describedby'):
            if k in a: self.refs.extend(a[k].split())


banned = ['非官方', '不是官方', '原站', '依原站', 'sigmacorp.com', 'fonts.googleapis.com', 'Lorem']
checked_links = 0
for rel in pages:
    text = (root / rel).read_text()
    p = Page(); p.feed(text)
    assert p.lang, f'{rel}: missing lang'
    assert p.h1 == 1, f'{rel}: expected one h1, got {p.h1}'
    assert p.main == 1, f'{rel}: expected one main'
    assert p.imgs_no_alt == 0, f'{rel}: img without alt'
    assert len(p.ids) == len(set(p.ids)), f'{rel}: duplicate ids'
    for r in p.refs: assert r in p.ids, f'{rel}: missing referenced id {r}'
    for word in banned: assert word not in text, f'{rel}: banned wording "{word}"'
    for link in p.links:
        if link.startswith(('http', 'mailto:', 'tel:')) or link.startswith('/sigma/'):
            if link.startswith('/sigma/'):
                target = root / urllib.parse.urlsplit(link).path.removeprefix('/sigma/')
                assert target.exists() and (target.is_file() or (target / 'index.html').is_file()), f'{rel}: broken {link}'
            continue
        parts = urllib.parse.urlsplit(link)
        if not parts.path:
            if parts.fragment: assert parts.fragment in p.ids or parts.fragment == 'top', f'{rel}: broken fragment {link}'
            continue
        target = ((root / rel).parent / parts.path).resolve()
        if link.endswith('/') or target.is_dir(): target = target / 'index.html'
        assert target.is_file(), f'{rel}: broken link {link}'
        if parts.fragment and target.suffix == '.html':
            tp = Page(); tp.feed(target.read_text())
            assert parts.fragment in tp.ids, f'{rel}: broken cross-page fragment {link}'
        checked_links += 1
    if '/' in rel and not rel.startswith(('zh-hans', 'en', 'ja')) or rel == 'index.html':
        assert f'mailto:{EMAIL}' in text, f'{rel}: group email missing'

for css in ['assets/site.css']:
    for url in re.findall(r"url\('?([^)'\"]+)", (root / css).read_text()):
        assert (root / 'assets' / urllib.parse.urlsplit(url).path).is_file(), f'missing CSS asset {url}'

products = (root / 'products/index.html').read_text()
for name, values in ADC.items():
    row = re.search(r'<tr data-alloy="' + re.escape(name) + r'">(.*?)</tr>', products)
    assert row, f'missing {name}'
    cells = re.findall(r'<td>([^<]*)</td>', row.group(1))
    assert cells == values, f'{name} mismatch'
for alloy in ['3104', '5182', '6063', '3033', 'Zamak-3', 'Zamak-5', 'ZSG-3', 'A356.2', 'YSBC3']:
    assert alloy in products, f'missing {alloy}'
assert '3003' not in products, '3033 must not be changed to 3003'
assert len(re.findall(r'data-qa>', (root / 'support/index.html').read_text())) == 37, 'expected 37 Q&A items'
print(f'PASS: {len(pages)} pages, {checked_links} internal links, ids/aria refs, wording, alloy data, 37 Q&A.')

if '--source' in sys.argv:
    html = urllib.request.urlopen('http://www.sigmacorp.com/cht/spec/spec.aspx', timeout=30).read().decode('utf-8', 'replace')
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S | re.I)
    count = 0
    for r in rows:
        cells = [re.sub(r'\s+|<[^>]+>|&nbsp;', '', c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S | re.I)]
        if len(cells) != 9 or cells[0] not in ['ADC3', 'ADC6', 'ADC10', 'ADC12', 'ADC14']: continue
        expected = [('≤' + v[:-3] if v.endswith('max') else v.replace('-', '–')) for v in cells[1:]]
        actual = [v.replace(' ', '') for v in ADC['ADC ' + cells[0][3:]]]
        assert actual == expected, f'source mismatch {cells[0]}'; count += 1
    assert count == 5, f'expected five source rows, found {count}'
    print('PASS: all 40 ADC composition values match the source specification sheet.')
