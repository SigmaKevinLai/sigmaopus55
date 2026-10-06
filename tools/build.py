"""Static multi-page, multi-language site generator for SIGMA.

Run from anywhere:  python3 tools/build.py
Writes HTML into the repository root (GitHub Pages serves main branch root).
No third-party dependencies.
"""
from html import escape
from pathlib import Path
import json
import re

from i18n import LANGS, ROUTES, NAV
from site_data import EMAIL, HQ_PHONE, ADC, ADC_ELEMENTS, ZINC, ZINC_ELEMENTS, LOCATIONS, HISTORY
import faq

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'src' / 'art'
BASE_URL = 'https://ed100084.github.io/sigma/'   # change when the official domain goes live
VERSION = '20261006-42'
GENERATED = []
TRANSLATED = {'zh-Hant'}  # languages with full page bodies; others get localized placeholders


def e(text):
    return escape(str(text), quote=True)


def art(name, cls='', label=None):
    svg = (ART / f'{name}.svg').read_text().strip()
    if label:
        svg = re.sub(r'aria-label="[^"]*"', f'aria-label="{e(label)}"', svg, count=1)
    else:
        svg = svg.replace('role="img" ', '', 1)
        svg = re.sub(r' aria-label="[^"]*"', ' aria-hidden="true" focusable="false"', svg, count=1)
    svg = svg.replace(' xmlns="http://www.w3.org/2000/svg"', '', 1)
    if cls:
        svg = svg.replace('class="art"', f'class="art {cls}"', 1)
    return svg


def route_path(key):
    return dict(ROUTES)[key]


class Page:
    def __init__(self, lang, key):
        self.lang, self.key = lang, key
        self.out = LANGS[lang]['prefix'] + route_path(key)
        depth = self.out.count('/')
        self.root = '../' * depth or './'

    def url(self, key, lang=None, anchor=''):
        target = LANGS[lang or self.lang]['prefix'] + route_path(key)
        href = self.root + target if target else self.root
        if href.startswith('./') and len(href) > 2:
            href = href[2:]
        return href + anchor

    def asset(self, path):
        return self.root + path if self.root != './' else './' + path


# --------------------------------------------------------------------------- layout

def header(p):
    ui = LANGS[p.lang]['ui']
    nav = ''.join(
        f'<li><a href="{p.url(k)}"{" aria-current=\"page\"" if k == p.key else ""}>{e(ui[k])}</a></li>' for k in NAV)
    langs = ''.join(
        f'<li><a href="{p.url(p.key, code)}" hreflang="{code}" lang="{code}"'
        f'{" aria-current=\"true\"" if code == p.lang else ""}>'
        f'<span>{e(meta["short"])}</span>{e(meta["name"])}</a></li>' for code, meta in LANGS.items())
    return f'''<a class="skip" href="#main">{e(ui['skip'])}</a>
<header class="site-header" data-header>
 <div class="bar wrap">
  <a class="logo" href="{p.url('home')}" aria-label="{e(ui['group'])} {e(ui['home'])}">{logo()}<span class="logo-text"><b>SIGMA</b><small>{e(ui['group'].replace('SIGMA ', ''))}</small></span></a>
  <nav class="primary" id="primary-nav" aria-label="{e(ui['home'])}"><ul>{nav}</ul>
   <a class="nav-contact" href="{p.url('contact')}">{e(ui['contact'])}</a></nav>
  <div class="tools">
   <details class="lang-menu" data-lang-menu><summary aria-label="{e(ui['language'])}: {e(LANGS[p.lang]['name'])}">{globe()}<span>{e(LANGS[p.lang]['short'])}</span></summary>
    <ul>{langs}</ul></details>
   <a class="btn btn-molten header-cta" href="{p.url('contact')}">{e(ui['cta'])}</a>
   <button class="menu-button" type="button" aria-expanded="false" aria-controls="primary-nav" data-open="{e(ui['menu'])}" data-close="{e(ui['close'])}" aria-label="{e(ui['menu'])}"><span></span><span></span></button>
  </div>
 </div>
</header>'''


def logo():
    return ('<svg class="logo-mark" viewBox="0 0 40 40" aria-hidden="true" focusable="false">'
            '<rect width="40" height="40" fill="currentColor"/><path d="M28 10H12v10h16v10H12" fill="none" stroke="#f16b40" stroke-width="5"/></svg>')


def globe():
    return ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/>'
            '<path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18"/></svg>')


def footer(p):
    ui = LANGS[p.lang]['ui']
    links = ''.join(f'<li><a href="{p.url(k)}">{e(ui[k])}</a></li>' for k in NAV + ['contact'])
    langs = ''.join(f'<li><a href="{p.url(p.key, c)}" hreflang="{c}" lang="{c}">{e(m["name"])}</a></li>' for c, m in LANGS.items())
    return f'''<footer class="site-footer">
 <div class="wrap footer-grid">
  <div class="footer-brand"><a class="logo" href="{p.url('home')}">{logo()}<span class="logo-text"><b>SIGMA</b><small>{e(ui['group'].replace('SIGMA ', ''))}</small></span></a>
   <p>{e(ui['footer_about'])}</p><p class="tagline">{e(ui['tagline'])}</p></div>
  <nav aria-label="{e(ui['footer_sitemap'])}"><h2>{e(ui['footer_sitemap'])}</h2><ul>{links}</ul></nav>
  <div><h2>{e(ui['footer_contact'])}</h2><address>新格發企業股份有限公司<br>臺灣高雄市小港區台機路 24 號<br>
   <a href="tel:{HQ_PHONE.replace('-', '')}">{HQ_PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></address></div>
  <nav aria-label="{e(ui['language'])}"><h2>{e(ui['language'])}</h2><ul>{langs}</ul></nav>
 </div>
 <div class="wrap footer-bottom"><span>© <span data-year>2026</span> SIGMA Group. All rights reserved.</span><a href="#top">{e(ui['top'])} ↑</a></div>
</footer>'''


def document(p, title, description, body, index=True):
    meta = LANGS[p.lang]
    canonical = BASE_URL + p.out
    alternates = ''
    if index:
        alternates = ''.join(
            f'<link rel="alternate" hreflang="{c}" href="{BASE_URL + LANGS[c]["prefix"] + route_path(p.key)}">'
            for c in LANGS if c in TRANSLATED)
        alternates += f'<link rel="alternate" hreflang="x-default" href="{BASE_URL + route_path(p.key)}">'
    robots = '' if index else '<meta name="robots" content="noindex">'
    font_preload = ''  # 400 KB CJK subset loads with font-display:swap; not preloaded to protect LCP
    full_title = title if p.key == 'home' else f'{title}｜{meta["ui"]["group"]}'
    return f'''<!doctype html>
<html lang="{p.lang}" id="top">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">{robots}
<link rel="canonical" href="{canonical}">{alternates}
<meta name="theme-color" content="#191c1b">
<meta property="og:type" content="website"><meta property="og:site_name" content="{e(meta['ui']['group'])}">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}"><meta property="og:locale" content="{meta['og']}">
<meta property="og:image" content="{BASE_URL}assets/og-image.png">
<link rel="icon" href="{p.asset('assets/favicon.svg')}" type="image/svg+xml">
{font_preload}<link rel="stylesheet" href="{p.asset('assets/site.css')}?v={VERSION}">
<script src="{p.asset('assets/site.js')}?v={VERSION}" defer></script>
</head>
<body class="page-{p.key}">
{header(p)}
<main id="main" tabindex="-1">
{body}
</main>
{footer(p)}
</body>
</html>
'''


def page_hero(p, eyebrow, title, lead, art_name, crumbs=True):
    ui = LANGS[p.lang]['ui']
    crumb = (f'<nav class="crumbs" aria-label="{e(ui["breadcrumb"])}"><ol><li><a href="{p.url("home")}">{e(ui["home"])}</a></li>'
             f'<li><span aria-current="page">{e(ui[p.key])}</span></li></ol></nav>') if crumbs else ''
    return f'''<section class="page-hero dark">
 <div class="wrap page-hero-grid">
  <div>{crumb}<p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p class="lead">{lead}</p></div>
  <div class="page-hero-art">{art(art_name, 'art-dark')}</div>
 </div>
</section>'''


def section_head(index, label, title, intro=''):
    intro_html = f'<p class="section-intro">{intro}</p>' if intro else ''
    return f'<header class="section-head"><p class="eyebrow"><span>{index}</span>{label}</p><h2>{title}</h2>{intro_html}</header>'


def table(spec, cls='data-table'):
    head = ''.join(f'<th scope="col">{e(h)}</th>' for h in spec['head'])
    rows = ''.join('<tr>' + f'<th scope="row">{e(r[0])}</th>' + ''.join(f'<td>{e(c)}</td>' for c in r[1:]) + '</tr>'
                   for r in spec['rows'])
    return (f'<div class="table-scroll" tabindex="0" role="region" aria-label="{e(spec["caption"])}"><table class="{cls}">'
            f'<caption>{e(spec["caption"])}</caption><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')


def cta_band(p, title, text, button):
    return f'''<section class="cta-band dark"><div class="wrap cta-grid">
 <div><h2>{title}</h2><p>{text}</p></div>
 <a class="btn btn-molten btn-lg" href="{p.url('contact')}">{button}<span aria-hidden="true">→</span></a>
</div></section>'''


# --------------------------------------------------------------------------- zh-Hant pages

def home(p):
    products = [
        ('products', '#casting-alloys', 'ingots', '01', '鑄造鋁合金', 'ADC 3 · 6 · 10 · 12 · 14 · A356.2', '以鋁合金錠供應壓鑄與澆鑄產業，可生產日、美、歐及中國國家標準牌號，或依客戶要求訂製。'),
        ('products', '#molten', 'ladle', '02', '鋁液直供', '200 公里供應圈', '以保溫鋁湯包將熔融鋁液直送壓鑄現場，省去客戶重熔，縮短流程並降低能耗。'),
        ('products', '#wrought', 'slab', '03', '變形鋁合金與扁錠', '3104 · 5182 · 6063 · 3033', '易開罐料保級還原再利用，扁錠供應高端鋁板帶材：罐身、罐蓋、拉環與汽車板。'),
        ('products', '#zinc', 'zinc', '04', '鋅合金錠', 'Zamak-3 · Zamak-5 · ZSG-3', '以純鋅錠為原料，依國際標準或客戶需求生產壓鑄用鋅合金錠。'),
    ]
    cards = ''.join(f'''<li><a class="product-tile" href="{p.url(k, anchor=a)}">
 <span class="tile-index">{i}</span><div class="tile-art">{art(img)}</div>
 <h3>{t}</h3><p class="tile-spec">{s}</p><p>{d}</p><span class="tile-more">了解規格 <span aria-hidden="true">→</span></span></a></li>'''
                    for k, a, img, i, t, s, d in products)
    steps = [('回收', '全球採購網路，依 ISRI 規格購入 Tense、Taint/Tabor、Zorba 等廢鋁。'),
             ('預處理', '破碎、重介質浮選、磁選與脫漆，從源頭提高原料純淨度。'),
             ('熔煉精煉', '永磁攪拌與熱交換節能技術，每一爐檢驗成分與金相。'),
             ('交付', '以合金錠或高溫鋁液交付，回到汽車、家電與工業製造。')]
    step_html = ''.join(f'<li><span class="step-no">0{n + 1}</span><h3>{t}</h3><p>{d}</p></li>' for n, (t, d) in enumerate(steps))
    return document(p, 'SIGMA 新格集團｜再生鋁合金・鋁液直供・鋅合金',
                    '新格集團 1978 年創立，深耕再生鋁合金、鋁液直供、鋅合金製造與廢金屬貿易，在臺灣與中國大陸設有九大生產基地，年產能逾 120 萬噸。',
                    f'''<section class="home-hero dark">
 <div class="wrap hero-grid">
  <div class="hero-copy">
   <p class="eyebrow"><span>SINCE 1978</span>再生鋁合金 · 鋁液直供 · 鋅合金</p>
   <h1>熔鑄，<br>更好的<em>明天</em>。</h1>
   <p class="lead">世上本沒有垃圾，只有放錯了位置的資源。新格將回收金屬熔鑄為高品質合金，供應汽車、家電與工業製造。</p>
   <div class="actions"><a class="btn btn-molten btn-lg" href="{p.url('products')}">產品與規格 <span aria-hidden="true">→</span></a>
    <a class="btn btn-ghost btn-lg" href="{p.url('contact')}">詢價與合作</a></div>
  </div>
  <div class="hero-art">{art('hero', 'art-dark')}<p class="hero-caption"><span aria-hidden="true"><small>13</small>Al</span>鋁可無限次循環，<br>再生能耗不到原鋁的 5%</p></div>
 </div>
 <div class="wrap"><dl class="stat-strip">
  <div><dt>創立</dt><dd><b>1978</b></dd></div>
  <div><dt>生產基地</dt><dd><b>9</b><small>座</small></dd></div>
  <div><dt>集團年產能</dt><dd><b>120</b><small>萬噸+</small></dd></div>
  <div><dt>合金產品規格</dt><dd><b>100</b><small>種+</small></dd></div>
 </dl></div>
</section>

<section class="section">
 <div class="wrap">
  {section_head('01', '產品與服務', '為製造現場，<br>供應對的材料。', '從鋁合金錠到高溫鋁液，新格以穩定的成分控制與就近供應，成為壓鑄、澆鑄與軋製產業的材料夥伴。')}
  <ul class="product-tiles">{cards}</ul>
 </div>
</section>

<section class="section tone">
 <div class="wrap split">
  <div>
   {section_head('02', '循環製造', '資源沒有終點，<br>只有下一次開始。')}
   <p class="body-lg">鋁具有優越的再生性能，可多次循環而不影響使用性能。再生鋁製程短、排放少，能耗不到原鋁生產的 5%。新格把城市中的廢舊金屬，重新熔鑄為工業所需的高品質材料。</p>
   <a class="text-link" href="{p.url('technology')}">看完整製程與品質管理 <span aria-hidden="true">→</span></a>
  </div>
  <div class="cycle-figure">{art('cycle')}</div>
 </div>
 <div class="wrap"><ol class="process-steps">{step_html}</ol></div>
</section>

<section class="section">
 <div class="wrap">
  {section_head('03', '品質與信譽', '國際市場<br>認可的品質。')}
  <div class="trust-grid">
   <article class="trust-card"><h3>LME 註冊品牌</h3><p class="brands"><b>SBI</b><b>SIGMA</b><b>ZSM</b></p><p>高雄、上海、漳州三大品牌於倫敦金屬交易所註冊；1996 年成為中國第一家在 LME 註冊的再生鋁廠。</p></article>
   <article class="trust-card"><h3>國際體系認證</h3><ul class="tag-list"><li>IATF 16949</li><li>ISO 9001</li><li>ISO 14001</li><li>ISO 45001</li><li>ISO 50001</li><li>ISO 14021</li></ul><p>中國首批循環經濟試點單位，並獲綠色工廠、高新技術企業等榮譽。</p></article>
   <article class="trust-card"><h3>每一爐都檢驗</h3><p>除化學成分外，同步檢驗金相、含渣量、含氣量與拉力；品管團隊並提供免費售後技術諮詢。</p><a class="text-link" href="{p.url('support')}">鑄造技術支援 <span aria-hidden="true">→</span></a></article>
  </div>
 </div>
</section>

<section class="section dark network">
 <div class="wrap split">
  <div>
   {section_head('04', '全球據點', '九大生產基地，<br>就近供應。')}
   <p class="body-lg">總部位於臺灣高雄，在浙江、重慶、山東、四川、內蒙古與河南設立規模化熔煉廠，並於美國、日本設有貿易據點，建構橫跨三大洲的採購與供應網路。</p>
   <ul class="place-list">{''.join(f'<li>{e(l["city"])}</li>' for l in LOCATIONS if l['kind'] == 'base')}</ul>
   <a class="btn btn-ghost" href="{p.url('locations')}">查看據點與聯絡方式 <span aria-hidden="true">→</span></a>
  </div>
  <div class="map-figure">{art('map', 'art-dark')}</div>
 </div>
</section>

<section class="section">
 <div class="wrap split">
  <div>{section_head('05', '永續循環', '連鋁灰，<br>都能再利用。')}</div>
  <div><p class="body-lg">2017 年成立環保科技事業部，以自主研發的無害化工藝處理鋁灰，除氟效率大於 99.99%，並轉化為無機人造石、PC 磚與耐火澆注料，朝製程「零排放」邁進。</p>
   <a class="text-link" href="{p.url('sustainability')}">了解永續循環 <span aria-hidden="true">→</span></a></div>
 </div>
</section>
{cta_band(p, '需要報價或規格確認？', '告訴我們合金牌號、供應形式與月需求量，業務團隊將與您聯繫。', '聯絡業務團隊')}''')


def about(p):
    timeline = ''.join(
        f'<li><h3>{y}</h3><ul>' + ''.join(f'<li><span>{e(m)}</span>{e(t)}</li>' for m, t in events) + '</ul></li>'
        for y, events in HISTORY)
    plants = [('高雄', '6,000'), ('重慶', '10,000'), ('日照', '10,000'), ('包頭', '10,000'), ('浙江', '10,000'),
              ('濱州', '8,000'), ('鞏義', '8,000'), ('長春', '6,500'), ('成都', '5,000')]
    plant_rows = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in plants)
    return document(p, '關於新格', '新格集團 1978 年創立，主要經營再生鋁合金錠、鋁液直供、鋁合金壓鑄件、鋅合金錠與廢金屬貿易。認識新格的理念、規模、品牌與沿革。', f'''
{page_hero(p, 'ABOUT SIGMA', '全球再生鋁<br>產業的長期實踐者', '自 1978 年起，新格持續投入資源回收、環境改善與循環利用，以 RECYCLING FOR A BETTER TOMORROW 為經營理念。', 'furnace')}
<section class="section">
 <div class="wrap split">
  <div>{section_head('01', '集團簡介', '把城市礦山，<br>熔鑄為工業材料。')}</div>
  <div class="prose">
   <p>新格集團創立於 1978 年，主要致力於再生鋁合金、鋅合金的生產及廢金屬貿易。以報廢汽車等廢舊金屬為原料，生產 100 多種規格的鋁合金產品，廣泛供應汽車與機車零部件、家用電器、工業裝備及其他製造業。</p>
   <p>新格發企業股份有限公司於 1981 年在臺灣高雄成立，為集團金屬貿易總部。集團在高雄、浙江、重慶永川、重慶綦江、日照、成都、包頭、濱州與鞏義設有九大生產基地，並在東莞、漳州、長春設有業務據點，在美國與日本設有貿易辦事處。</p>
   <p>新格是全球鋁回收利用體系的重要一環。進口原料依美國 ISRI 標準採購，主要來自北美與歐洲；國內原料則包括回收市場廢鋁、金屬矽、電解鋁錠、純銅與工廠下腳料。</p>
  </div>
 </div>
 <div class="wrap"><dl class="stat-grid">
  <div><dt>集團年產能</dt><dd><b>120</b><small>萬噸+</small></dd></div>
  <div><dt>年產值（人民幣）</dt><dd><b>80</b><small>億+</small></dd></div>
  <div><dt>員工</dt><dd><b>1,300</b><small>名+</small></dd></div>
  <div><dt>專利技術</dt><dd><b>150</b><small>項+</small></dd></div>
 </dl></div>
</section>

<section class="section tone">
 <div class="wrap split">
  <div>{section_head('02', '經營理念', '誠信、節約、<br>環保、永續。')}
   <blockquote class="quote"><p>世上本沒有垃圾，<br>只有放錯了位置的資源。</p></blockquote></div>
  <div class="prose">
   <p>鋁具有優越的再生性能，可以多次循環利用而不影響使用性能。鋁的再生能耗不到原鋁生產的 5%，工藝流程短，有害氣體與粉塵排放少。無論從資源、環境、市場或社會與經濟效益來看，鋁的再生利用都是利在當代、功在千秋的事業。</p>
   <p>2005 年，新格在上海寶山投資 3,800 萬美元，依工業生態學觀念興建 30 萬噸級鑄造鋁合金、鋅合金工廠，並獲列為中國首批循環經濟試點單位。</p>
   <p>無論時代如何變遷，新格將恪守誠信、節約、環保、永續經營的發展理念，開拓進取、勇於創新、以人為本，實現回饋社會、造福人類、保護地球的願望。</p>
  </div>
 </div>
</section>

<section class="section">
 <div class="wrap">
  {section_head('03', '規模與品牌', '穩定供應的<br>產能基礎。')}
  <div class="split align-start">
   <div class="table-scroll" tabindex="0" role="region" aria-label="主要熔煉廠月產能"><table class="data-table compact"><caption>主要熔煉廠月產能（噸）</caption><thead><tr><th scope="col">廠區</th><th scope="col">月產能</th></tr></thead><tbody>{plant_rows}</tbody></table></div>
   <div class="stack">
    <article class="trust-card"><h3>LME 註冊品牌</h3><p class="brands"><b>SBI</b><b>SIGMA</b><b>ZSM</b></p><p>高雄 SBI、上海 SIGMA、漳州 ZSM 三大品牌於倫敦金屬交易所註冊，為中國第一家獲准進入 LME 市場交割的二次鋁合金廠商。</p></article>
    <article class="trust-card"><h3>認證與榮譽</h3><ul class="tag-list"><li>IATF 16949</li><li>ISO 9001</li><li>ISO 14001</li><li>ISO 45001</li><li>ISO 50001</li><li>ISO 14021</li></ul>
     <p>中國首批循環經濟示範企業、工信部《廢銅鋁加工利用行業規範條件》首批達標企業；獲評綠色工廠、高新技術企業、專精特新企業與健康企業。</p></article>
   </div>
  </div>
 </div>
</section>

<section class="section dark">
 <div class="wrap split">
  <div>{section_head('04', '產業生態', '重慶新格鋁製<br>汽車零部件產業園')}</div>
  <div class="prose">
   <p>永川基地 30 萬噸再生鋁產能已投產，規劃引進 20 家鋁合金壓鑄與機械加工企業，打造百億級鋁製汽車零部件產業基地。</p>
   <p>園區首創「鋁液直供－壓鑄成型」短流程體系，協助入園企業降本增效。永川區政府提供政策支持，新格負責園區建設、招商與營運；廠房可租可買，企業可「拎包入駐」。</p>
   <p>2026 年 2 月，全國首個江海聯運進口再生鋁檢驗監管優化試點於永川新格落地，有效降低原料成本，鞏固鋁液保供體系。</p>
  </div>
 </div>
</section>

<section class="section">
 <div class="wrap">
  {section_head('05', '發展沿革', '四十多年，<br>一路熔鑄向前。')}
  <ol class="timeline">{timeline}</ol>
 </div>
</section>
{cta_band(p, '與新格建立長期合作', '無論是合金採購、鋁液直供或原料供應，歡迎與我們聯繫。', '聯絡我們')}''')


def composition_table(caption, elements, data, table_id):
    head = '<th scope="col">牌號</th>' + ''.join(f'<th scope="col"><abbr title="{e(n)}">{s}</abbr></th>' for s, n in elements)
    rows = ''.join(f'<tr data-alloy="{e(k)}"><th scope="row">{e(k)}</th>' + ''.join(f'<td>{e(v)}</td>' for v in vals) + '</tr>'
                   for k, vals in data.items())
    return (f'<div class="table-scroll" tabindex="0" role="region" aria-label="{e(caption)}"><table class="data-table spec" id="{table_id}">'
            f'<caption>{e(caption)}</caption><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')


def products(p):
    finder = [('壓鑄汽機車、家電零件', '#casting-alloys', 'ADC 12 / ADC 10'), ('輪轂、精密與重力鑄造', '#a356', 'A356.2'),
              ('易開罐、鋁板帶材', '#wrought', '3104 / 5182'), ('縮短流程、免重熔', '#molten', '鋁液直供'),
              ('五金、拉鍊、鋅壓鑄', '#zinc', 'Zamak / ZSG'), ('閥門、燃氣具', '#copper', 'YSBC3')]
    finder_html = ''.join(f'<li><a href="{a}"><span>{e(n)}</span><b>{e(r)}</b><i aria-hidden="true">↓</i></a></li>' for n, a, r in finder)
    toc = [('#casting-alloys', '鑄造鋁合金'), ('#a356', 'A356.2'), ('#wrought', '變形鋁合金'), ('#molten', '鋁液直供'),
           ('#zinc', '鋅合金'), ('#copper', '銅合金'), ('#sourcing', '原料採購')]
    toc_html = ''.join(f'<li><a href="{a}">{t}</a></li>' for a, t in toc)
    options = ''.join(f'<option value="{e(k)}">{e(k)}</option>' for k in ADC)
    scrap = ['生雜鋁料', '打包軟鋁料', '混合鋁切片', '浮水鋁切片', '厚鋁板', '鋁質印刷版廢料', '散熱水箱廢料', '鋁線', '壓包易拉罐', '鋸屑']
    return document(p, '產品中心', '新格產品：ADC 系列鑄造鋁合金、A356.2、3104/5182 扁錠與變形鋁合金、鋁液直供、Zamak 鋅合金與 YSBC3 銅合金，附化學成分規格表。', f'''
{page_hero(p, 'PRODUCTS', '產品中心', '以鋁合金錠和鋁液，為壓鑄、澆鑄與軋製產業提供 100 多種規格產品；可生產日標、美標、歐標及中國國標牌號，或依客戶要求訂製成分。', 'ingots')}
<section class="section finder-section">
 <div class="wrap">
  <h2 class="h-small">依應用快速找材料</h2>
  <ul class="finder">{finder_html}</ul>
 </div>
</section>
<div class="wrap with-toc">
 <nav class="toc" aria-label="產品分類"><p>產品分類</p><ul>{toc_html}</ul></nav>
 <div class="toc-body">

<section class="product-block" id="casting-alloys" aria-labelledby="h-casting">
 <div class="product-head"><div><p class="eyebrow"><span>01</span>DIE CASTING ALLOYS</p><h2 id="h-casting">鑄造鋁合金錠</h2>
  <p class="body-lg">鋁合金比重僅 2.6–2.7，質輕且機械性質與耐蝕性優秀，廣泛應用於汽機車、產業機械、農漁機具、電氣通信、精密機器與日用品。亞洲地區普遍採用日本 JIS 規格，新格亦可依 DIN、BS、GB、ASTM 等標準生產。</p></div>
  <div class="product-art">{art('casting')}</div></div>
 <dl class="facts"><div><dt>供應形式</dt><dd>鋁合金錠、鋁液</dd></div><div><dt>主要應用</dt><dd>汽機車零件、家電、產業機械、通訊</dd></div><div><dt>授權產品</dt><dd>K-Alloy™（經許可生產）</dd></div></dl>
 {composition_table('常用鑄造鋁合金化學成分（%，鋁錠與鋁液）', ADC_ELEMENTS, ADC, 'adc-table')}
 <div class="compare" data-compare hidden>
  <h3>比較兩種牌號</h3>
  <div class="compare-controls"><label>牌號 A<select data-compare-a>{options}</select></label><label>牌號 B<select data-compare-b>{options}</select></label></div>
  <p class="compare-status" role="status" aria-live="polite" data-compare-status></p>
 </div>
 <p class="note">表列為主要元素上限或範圍，其餘為鋁（Al）。實際規格、公差與檢驗項目以雙方確認之技術協議為準。</p>
</section>

<section class="product-block" id="a356" aria-labelledby="h-a356">
 <div class="product-head"><div><p class="eyebrow"><span>02</span>PRECISION CASTING</p><h2 id="h-a356">A356.2 合金</h2>
  <p class="body-lg">由重慶綦江基地專業化生產，兼具輕量化、高強度、易鑄造與耐腐蝕等優勢，為汽車、航空、機械與電子領域提供主流關鍵材料。</p></div></div>
 <dl class="facts"><div><dt>生產基地</dt><dd>重慶綦江</dd></div><div><dt>特性</dt><dd>輕量、高強度、易鑄造、耐腐蝕</dd></div><div><dt>應用</dt><dd>汽車輪轂與結構件、航空、機械、電子</dd></div></dl>
</section>

<section class="product-block" id="wrought" aria-labelledby="h-wrought">
 <div class="product-head"><div><p class="eyebrow"><span>03</span>WROUGHT ALLOYS &amp; SLABS</p><h2 id="h-wrought">變形鋁合金與高端扁錠</h2>
  <p class="body-lg">以重熔錠與鋁液供應變形鋁合金。2025 年 11 月重慶新格扁錠項目投產，生產高端鋁板帶材的核心原料。</p></div>
  <div class="product-art">{art('slab')}</div></div>
 <ul class="spec-cards">
  <li><b>3104</b><p>易開罐系列。重慶、鞏義、濱州、日照基地專業生產，保級還原，成分、性能與純淨度全面達到食品級標準，實現高價值閉環循環。用於啤酒、飲料罐罐身。</p></li>
  <li><b>5182</b><p>罐蓋、拉環與汽車板用合金扁錠。</p></li>
  <li><b>6063</b><p>變形鋁合金重熔錠與鋁液。</p></li>
  <li><b>3033</b><p>變形鋁合金重熔錠與鋁液。</p></li>
 </ul>
</section>

<section class="product-block" id="molten" aria-labelledby="h-molten">
 <div class="product-head"><div><p class="eyebrow"><span>04</span>MOLTEN ALUMINUM</p><h2 id="h-molten">鋁液直供</h2>
  <p class="body-lg">新格首創「鋁液直供－壓鑄成型」短流程體系：熔煉完成的鋁液以保溫鋁湯包直接配送至客戶壓鑄現場，客戶無需再將合金錠重新熔化，節省能源、時間與熔損。</p></div>
  <div class="product-art">{art('ladle')}</div></div>
 <ol class="flow"><li>熔煉精煉</li><li>調質爐</li><li>保溫爐</li><li>鋁湯包</li><li>配送至壓鑄現場</li></ol>
 <dl class="facts"><div><dt>供應半徑</dt><dd>約 200 公里鋁液供應圈</dd></div><div><dt>占產能比重</dt><dd>約 60% 產能以鋁液直供</dd></div><div><dt>合作案例</dt><dd>現代集團日照威亞發動機廠、一汽集團長春總廠等配套工廠</dd></div></dl>
 <p class="note">鋁液直供需依廠區距離、合金牌號、月用量與交付節拍個別評估，歡迎與業務團隊討論。</p>
</section>

<section class="product-block" id="zinc" aria-labelledby="h-zinc">
 <div class="product-head"><div><p class="eyebrow"><span>05</span>ZINC ALLOYS</p><h2 id="h-zinc">鋅合金錠</h2>
  <p class="body-lg">以純鋅錠為原料，於 5 噸鋅熔解爐生產線生產，在嚴格品質檢測下製成符合國際標準的鋅合金錠，並可依客戶特殊需求訂製。</p></div>
  <div class="product-art">{art('zinc')}</div></div>
 {composition_table('常用鋅合金錠化學成分（%）', ZINC_ELEMENTS, ZINC, 'zinc-table')}
 <p class="note">表列為主要元素上限或範圍，其餘為鋅（Zn）。</p>
</section>

<section class="product-block" id="copper" aria-labelledby="h-copper">
 <div class="product-head"><div><p class="eyebrow"><span>06</span>COPPER ALLOYS</p><h2 id="h-copper">銅合金</h2>
  <p class="body-lg">生產銅合金 YSBC3，適用於各類閥門及燃氣具。</p></div></div>
 <dl class="facts"><div><dt>牌號</dt><dd>YSBC3</dd></div><div><dt>含銅量</dt><dd>58–60% 及 60–62% 兩種</dd></div><div><dt>應用</dt><dd>閥門、燃氣具</dd></div></dl>
</section>

<section class="product-block" id="sourcing" aria-labelledby="h-sourcing">
 <div class="product-head"><div><p class="eyebrow"><span>07</span>SCRAP SOURCING</p><h2 id="h-sourcing">原料採購</h2>
  <p class="body-lg">新格是臺灣第一家同時成為美國 ISRI 與歐洲 BIR 會員的廢金屬貿易商，每年自世界各地採購超過 30 萬噸各式廢料，除供應自有熔煉廠，也經營廢料貿易。歡迎全球廢料供應商與我們聯繫。</p></div>
  <div class="product-art">{art('bale')}</div></div>
 <div class="sourcing-grid">
  <div><h3>鋁廢料</h3><ul class="tag-list">{''.join(f'<li>{s}</li>' for s in scrap)}</ul></div>
  <div><h3>銅廢料與重金屬</h3><ul class="tag-list"><li>黃銅廢料</li><li>1 號紫銅</li><li>2 號紫銅</li><li>黃銅雜錠</li><li>重金屬混合切片</li></ul></div>
  <div><h3>純金屬</h3><ul class="tag-list"><li>純鋁錠／次級純鋁錠</li><li>純鋅錠</li></ul></div>
 </div>
 {table(dict(caption='金屬矽採購規格', head=['項目', '553 金屬矽', '441 金屬矽'], rows=[
        ['成分要求', 'Si ≥ 98.5%；Fe ≤ 0.5%；Al ≤ 0.5%；Ca ≤ 0.3%', 'Si ≥ 98.5%；Fe ≤ 0.4%；Al ≤ 0.4%；Ca ≤ 0.1%'],
        ['粒度要求', '10–100 mm ≥ 90%', '10–100 mm ≥ 90%'],
        ['包裝要求', '1 噸塑膠編織袋', '1 噸塑膠編織袋']]))}
 <a class="btn btn-dark" href="{p.url('contact')}?topic=supply">成為供應夥伴 <span aria-hidden="true">→</span></a>
</section>
 </div>
</div>
{cta_band(p, '找不到需要的牌號？', '新格可生產日標、美標、歐標及中國國標牌號，或依您的成分要求訂製。', '提出規格需求')}''')


def technology(p):
    steps = [
        ('01', '原料採購', '依 ISRI 規格採購 Tense、Taint/Tabor、Zorba、Twitch 等廢鋁；進口廢料由臺灣、美國、日本辦事處購入，新格為中國最大的鋁廢料進口商之一。'),
        ('02', '預處理與分選', '上海、重慶、日照廠設有重介質浮選設備，分選破碎後的混合金屬與細鋁；多廠增設破碎設備，實現更精確的檢驗與更快速的分選。'),
        ('03', '熔煉與精煉', '每套熔鋁爐配置永磁攪拌器與熱交換器，提高熔解速度與回收率，並回收煙氣熱能節省燃料。'),
        ('04', '品質檢驗', '每一爐檢驗化學成分，並同步檢驗金相、含渣量、含氣量與拉力。'),
        ('05', '鑄錠與鋁液', '依客戶需求鑄造合金錠，或以保溫鋁湯包直送鋁液。'),
        ('06', '物流出貨', '龍門吊卸櫃、自動卸料與懸吊式出貨平台，每日可處理逾 150 個貨櫃。'),
    ]
    step_html = ''.join(f'<li><span class="step-no">{n}</span><h3>{t}</h3><p>{d}</p></li>' for n, t, d in steps)
    equipment = ['日本島津／德國 Spectrolab 光譜分析儀', '萬能材料試驗機', '日本 Flux 真空試驗機', '布氏硬度計', '日本 Olympus 金相顯微鏡',
                 'METKON 雙盤拋光機', 'METKON 鑲嵌機', '5 公斤測試電爐', '鋁熔體快速測氫儀']
    return document(p, '製程與品質', '新格鋁合金錠生產流程：原料採購、預處理分選、熔煉精煉、品質檢驗、鑄錠與鋁液交付；以及品管檢驗設備與管理體系。', f'''
{page_hero(p, 'PROCESS &amp; QUALITY', '製程與品質', '從原料進廠到成品出貨，每一個階段——原料篩選、熔煉、精煉、鑄錠、包裝——都層層把關。', 'lab')}
<section class="section">
 <div class="wrap">
  {section_head('01', '生產流程', '鋁合金錠<br>生產流程')}
  <ol class="process-steps six">{step_html}</ol>
 </div>
</section>
<section class="section tone">
 <div class="wrap">
  {section_head('02', '核心技術', '為品質與節能<br>持續投資。')}
  <div class="feature-grid">
   <article><h3>永磁攪拌器</h3><p>於每套熔鋁爐加裝鋁液永磁攪拌器，提高精煉過程的金屬熔解速度與回收率；熔煉特殊規格鋁錠時效果尤其明顯，金相組織均勻細化。</p></article>
   <article><h3>熱交換器</h3><p>每套熔鋁爐增設兩台熱交換器，高溫煙氣預熱助燃空氣至約 300°C，回收熱能、提高燃燒效率，並減少不完全燃燒的污染。</p></article>
   <article><h3>集中監控室</h3><p>以自動監控設備全面控制爐溫、爐壓、燒嘴與閥門，並與收塵設備連動，提升能耗效率、降低不規則排放。</p></article>
   <article><h3>進口原料預處理</h3><p>原料到港前實施拆包、分選、磁選、脫漆、冷卻、壓包一體化預處理，以自主設計專用裝備精準溫控脫漆，去除有機雜質並避免原料破碎。</p></article>
   <article><h3>鋅合金生產線</h3><p>上海新格設有 5 噸鋅熔解爐生產線 2 套，以純鋅錠為原料生產符合國際標準的鋅合金錠。</p></article>
   <article><h3>研發合作</h3><p>長期與知名學術研究單位合作再生合金專題研究，開發新工藝；廢鋁分選、再生鋁熔煉、鋁灰資源化等技術已取得多項發明專利。</p></article>
  </div>
 </div>
</section>
<section class="section">
 <div class="wrap split align-start">
  <div>{section_head('03', '品質管理', '品質第一，<br>全程管理。')}
   <p class="body-lg">新格採用 IATF 16949、ISO 9001 等國際品質體系作為全廠管理系統，持續改進以滿足顧客要求。品管團隊同時為客戶提供免費售後諮詢；客戶生產中遇到品質相關困難時，我們協助解決。</p>
   <a class="text-link" href="{p.url('support')}">查看鑄造技術問答 <span aria-hidden="true">→</span></a></div>
  <div><h3 class="h-small">品管檢驗室主要設備</h3><ul class="check-list">{''.join(f'<li>{x}</li>' for x in equipment)}</ul>
   <h3 class="h-small">每爐檢驗項目</h3><ul class="tag-list"><li>化學成分</li><li>金相組織</li><li>含渣量</li><li>含氣量</li><li>拉力</li></ul></div>
 </div>
</section>
{cta_band(p, '需要材質證明或檢驗資料？', '請提供訂單或批號，品管團隊將協助提供相關文件。', '聯絡品管與業務')}''')


def sustainability(p):
    return document(p, '永續循環', '新格的永續實踐：再生鋁循環、鋁灰無害化與資源化產品、收塵與廢水循環設備，以及企業社會責任方針。', f'''
{page_hero(p, 'SUSTAINABILITY', '永續循環', '以「資源回收、環境改善、回饋社會」為社會責任方針，持續定義綠色工業的新標準。', 'cycle')}
<section class="section">
 <div class="wrap split">
  <div>{section_head('01', '再生鋁', '再生，<br>是最好的節能。')}</div>
  <div class="prose"><p>鋁的再生不構成環境污染，能耗不到原鋁生產的 5%，工藝流程短，有害氣體與粉塵排放少。新格充分利用「城市礦山」中的廢鋁資源，保護天然鋁資源，為鋁工業的永續發展盡心盡力。</p>
   <dl class="stat-grid two"><div><dt>再生能耗</dt><dd><b>&lt;5</b><small>% 原鋁</small></dd></div><div><dt>年回收採購</dt><dd><b>30</b><small>萬噸+ 廢料</small></dd></div></dl></div>
 </div>
</section>
<section class="section tone">
 <div class="wrap">
  {section_head('02', '鋁灰資源化', '讓熔煉副產物<br>成為新材料。', '新格的鋁灰綜合利用研究起步於十多年前，與上海交通大學聯合研發；2018 年起自主研發，已具備鋁灰無害化、資源化技術。2017 年成立環保科技事業部，於重慶、包頭、濱州、鞏義成立環保科技公司，處理工藝已申請國家發明專利。')}
  <div class="split align-start">
   <div><h3 class="h-small">無害化工藝特點</h3><ol class="num-list"><li>處理量大</li><li>除氟效率大於 99.99%</li><li>不產生含氟廢水</li><li>無二次污染與設備腐蝕問題</li></ol></div>
   <div><h3 class="h-small">資源化產品</h3><ul class="spec-cards">
    <li><b>無機人造石</b><p>取代天然石材的新一代環保建材。</p></li>
    <li><b>PC 磚</b><p>主要應用於戶外廣場磚、人行道磚。</p></li>
    <li><b>耐火澆注料</b><p>以處理後的鋁灰及收塵灰生產高強度耐火材料。</p></li>
    <li><b>混凝土路面磚</b><p>產品均滿足相關品質標準。</p></li></ul></div>
  </div>
 </div>
</section>
<section class="section">
 <div class="wrap">
  {section_head('03', '環保設備', '乾淨的工廠，<br>從設備開始。')}
  <div class="feature-grid">
   <article><h3>袋式集塵設備</h3><p>自主研發大功率袋式集塵設備：風量 110,000 m³/h、功率 200 kW、過濾面積 2,331 m²，全面控制煙塵與粉塵排放。</p></article>
   <article><h3>輻射偵測儀</h3><p>引進門式輻射偵測儀，防止放射性物質混入廢金屬進廠，保障員工與公眾安全。</p></article>
   <article><h3>鋁灰處理設備</h3><p>以球磨機、振動篩、除鐵器等密封設備分離灰砂、鋁片與鐵屑後再利用，廢灰可作為陶瓷燒製原料。</p></article>
   <article><h3>洗料廢水循環</h3><p>洗料廢水經機械柵格、沉澱、污泥脫水處理後回到水洗車間循環使用，避免二次污染。</p></article>
  </div>
 </div>
</section>
<section class="section dark">
 <div class="wrap split align-start">
  <div>{section_head('04', '企業社會責任', '以人為本，<br>回饋社會。')}</div>
  <div class="prose">
   <p>新格的社會責任策略涵蓋責任管理、員工、環境、產品與社會五大模組。</p>
   <ul class="check-list">
    <li>遵守所有適用法律法規、行業標準、國際勞工組織與聯合國公約</li>
    <li>尊重員工自由結社與集體談判權，杜絕任何形式的歧視</li>
    <li>報酬不低於法定最低工資，遵守工時規定，提供健康安全的工作環境</li>
    <li>杜絕童工與強迫勞動，堅持平等雇用、同工同酬，保護女性員工權益</li>
    <li>加強環境評估、檢測與應急管理，提高可再生原料利用、節能減耗</li>
    <li>成立員工志工組織，推動公益捐贈；設置員工申訴管道並定期檢查</li>
   </ul>
  </div>
 </div>
</section>
{cta_band(p, '一起推動循環經濟', '歡迎原料供應商、園區夥伴與研究單位與我們交流合作。', '與我們聯繫')}''')


def qa_items(prefix, items):
    out = []
    for n, (q, answer) in enumerate(items, 1):
        parts, bullets = [], []
        for para in answer:
            m = re.match(r'^([A-E])\. (.*)$', para)
            if m:
                bullets.append(f'<li><span>{m.group(1)}</span>{e(m.group(2))}</li>')
            else:
                if bullets:
                    parts.append('<ol class="cause-list">' + ''.join(bullets) + '</ol>'); bullets = []
                parts.append(f'<p>{e(para)}</p>')
        if bullets:
            parts.append('<ol class="cause-list">' + ''.join(bullets) + '</ol>')
        out.append(f'<details class="qa" id="{prefix}{n}" data-qa><summary><span class="qa-no">{n:02d}</span><h3>{e(q)}</h3><span class="qa-icon" aria-hidden="true"></span></summary><div class="qa-body">{"".join(parts)}</div></details>')
    return ''.join(out)


def support(p):
    groups = [('al', '鋁合金鑄造問題', faq.ALUMINIUM), ('zn', '鋅合金問題', faq.ZINC), ('cu', '銅合金問題', faq.COPPER), ('kn', '材料基礎知識', faq.KNOWLEDGE)]
    total = sum(len(g[2]) for g in groups)
    chips = ''.join(f'<li><a href="#group-{k}">{t}<span>{len(items)}</span></a></li>' for k, t, items in groups)
    blocks = ''.join(f'<section class="qa-group" id="group-{k}" aria-labelledby="h-{k}" data-qa-group><h2 id="h-{k}">{t}</h2>{qa_items(k + "-", items)}</section>' for k, t, items in groups)
    coatings = '<ul class="check-list"><li>5% 氧化鋅 + 1.2% 水玻璃 + 水</li><li>膠體石墨</li><li>3–5% 聚乙烯 + 煤油</li></ul>'
    return document(p, '技術支援', f'新格鑄造技術支援：{total} 則鋁合金、鋅合金、銅合金鑄造問題與材料知識問答，以及澆注溫度、模具溫度與壓鑄缺陷對照表。', f'''
{page_hero(p, 'TECHNICAL SUPPORT', '鑄造技術支援', '整理新格品管團隊多年協助客戶排除鑄造問題的經驗。找不到答案時，歡迎直接聯繫，我們提供免費的售後技術諮詢。', 'casting')}
<section class="section">
 <div class="wrap support-layout">
  <div class="support-side">
   <div class="search" data-qa-search hidden><label for="qa-search">搜尋問題</label>
    <input id="qa-search" type="search" placeholder="例如：氣孔、粘模、ADC 12" autocomplete="off">
    <p class="search-status" role="status" aria-live="polite" data-qa-status>共 {total} 則問答</p></div>
   <ul class="chip-nav">{chips}<li><a href="#reference">參數對照表</a></li></ul>
   <div class="side-cta"><p>問題仍未解決？</p><a class="btn btn-dark" href="{p.url('contact')}?topic=support">諮詢品管團隊 <span aria-hidden="true">→</span></a></div>
  </div>
  <div class="support-main">{blocks}
   <p class="empty-result" data-qa-empty hidden>找不到相符的問題。請嘗試其他關鍵字，或直接<a href="{p.url('contact')}?topic=support">聯繫品管團隊</a>。</p>
   <section class="qa-group" id="reference" aria-labelledby="h-ref"><h2 id="h-ref">壓鑄參數對照表</h2>
    <p class="note">以下為一般參考範圍；實際參數須依鑄件結構、模具與設備調整。</p>
    {table(faq.POUR_TEMP)}{table(faq.DIE_TEMP)}{table(faq.DEFECTS)}
    <h3 class="h-small">鋁合金壓鑄常用塗料</h3>{coatings}
    <p class="note">塗料的作用：預防粘模、減少模具導熱、改善成形性、避免鋁液直接沖刷模具，並具潤滑作用。</p>
   </section>
  </div>
 </div>
</section>''')


def locations(p):
    def card(l):
        contact = ''
        if l['tel']:
            contact += f'<div><dt>電話</dt><dd><a href="tel:{l["tel"].replace("-", "")}">{e(l["tel"])}</a></dd></div>'
        if l['fax']:
            contact += f'<div><dt>傳真</dt><dd>{e(l["fax"])}</dd></div>'
        address = (f'<div><dt>地址</dt><dd>{e(l["address"])}</dd></div>' if l['address']
                   else f'<div><dt>聯絡</dt><dd>請洽集團總部 <a href="tel:{HQ_PHONE.replace("-", "")}">{HQ_PHONE}</a></dd></div>')
        kind = '生產基地' if l['kind'] == 'base' else '業務／貿易據點'
        return (f'<li class="location" id="{l["id"]}" data-kind="{l["kind"]}"><p class="loc-kind">{kind}</p><h3>{e(l["city"])}</h3>'
                f'<p class="loc-name">{e(l["name"])}</p><p class="loc-role">{e(l["role"])}</p><dl>{address}{contact}</dl></li>')
    bases = [l for l in LOCATIONS if l['kind'] == 'base']
    offices = [l for l in LOCATIONS if l['kind'] == 'office']
    return document(p, '全球據點', '新格集團全球據點：高雄總部與浙江、重慶、日照、成都、包頭、濱州、鞏義等九大生產基地，以及長春、漳州、東莞、美國、日本業務據點的地址與電話。', f'''
{page_hero(p, 'GLOBAL NETWORK', '全球據點', '九大生產基地就近供應鋁合金錠與鋁液，業務與貿易據點橫跨臺灣、中國大陸、美國與日本。', 'map')}
<section class="section">
 <div class="wrap">
  <div class="filter-bar" data-loc-filter hidden role="group" aria-label="篩選據點">
   <button type="button" aria-pressed="true" data-filter="all">全部<span>{len(LOCATIONS)}</span></button>
   <button type="button" aria-pressed="false" data-filter="base">生產基地<span>{len(bases)}</span></button>
   <button type="button" aria-pressed="false" data-filter="office">業務／貿易據點<span>{len(offices)}</span></button>
  </div>
  <p class="visually-hidden" role="status" aria-live="polite" data-loc-status></p>
  <section class="loc-group" data-loc-group="base" aria-labelledby="h-bases"><h2 id="h-bases" class="loc-heading">生產基地<span>{len(bases)}</span></h2>
   <ul class="location-grid">{''.join(card(l) for l in bases)}</ul></section>
  <section class="loc-group" data-loc-group="office" aria-labelledby="h-offices"><h2 id="h-offices" class="loc-heading">業務與貿易據點<span>{len(offices)}</span></h2>
   <ul class="location-grid">{''.join(card(l) for l in offices)}</ul></section>
 </div>
</section>
{cta_band(p, '不確定該聯繫哪個據點？', '請透過聯絡表單告訴我們交貨地點與需求，我們將轉交最近的業務窗口。', '填寫聯絡表單')}''')


def contact(p):
    topics = [('quote', '產品詢價'), ('molten', '鋁液直供合作'), ('supply', '原料供應'), ('support', '技術支援'), ('other', '其他')]
    topic_html = ''.join(f'<option value="{k}">{t}</option>' for k, t in topics)
    return document(p, '聯絡我們', f'聯絡新格集團：產品詢價、鋁液直供合作、原料供應與技術支援。電子郵件 {EMAIL}，總部電話 {HQ_PHONE}。', f'''
{page_hero(p, 'CONTACT', '聯絡我們', '產品詢價、鋁液直供合作、原料供應或技術問題，請留下需求，業務與品管團隊將儘快回覆。', 'ladle')}
<section class="section">
 <div class="wrap contact-layout">
  <form class="inquiry" action="mailto:{EMAIL}" method="post" enctype="text/plain" data-inquiry novalidate>
   <h2>線上詢問</h2>
   <p class="form-note">標示 <abbr title="必填">*</abbr> 為必填欄位。</p>
   <div class="field-grid">
    <label class="field"><span>詢問類型 <abbr title="必填">*</abbr></span><select name="topic" required>{topic_html}</select></label>
    <label class="field"><span>公司名稱 <abbr title="必填">*</abbr></span><input name="company" autocomplete="organization" required></label>
    <label class="field"><span>聯絡人 <abbr title="必填">*</abbr></span><input name="name" autocomplete="name" required></label>
    <label class="field"><span>電子郵件 <abbr title="必填">*</abbr></span><input name="email" type="email" autocomplete="email" required></label>
    <label class="field"><span>電話</span><input name="phone" type="tel" autocomplete="tel"></label>
    <label class="field"><span>國家／地區</span><input name="region" autocomplete="country-name"></label>
    <label class="field wide"><span>合金牌號／月需求量</span><input name="spec" placeholder="例如：ADC 12，每月 200 噸，合金錠"></label>
    <label class="field wide"><span>需求說明 <abbr title="必填">*</abbr></span><textarea name="message" rows="6" required maxlength="2000"></textarea></label>
   </div>
   <p class="error-summary" role="alert" data-form-error hidden></p>
   <button class="btn btn-molten btn-lg" type="submit">以電子郵件送出 <span aria-hidden="true">→</span></button>
   <p class="form-note">送出後將開啟您的電子郵件程式，內容會預先填入，確認後寄出即可。表單資料不會儲存在本網站。</p>
   <div class="mail-fallback" data-mail-fallback hidden>
    <p>沒有開啟郵件程式嗎？請複製以下內容，寄至 <a href="mailto:{EMAIL}">{EMAIL}</a>。</p>
    <textarea readonly rows="8" aria-label="詢問內容" data-mail-body></textarea>
    <button class="btn btn-dark" type="button" data-copy>複製內容</button><span class="copy-status" role="status" aria-live="polite" data-copy-status></span>
   </div>
  </form>
  <div class="contact-side">
   <div class="contact-card dark"><h2>集團總部</h2><p>新格發企業股份有限公司</p>
    <dl><div><dt>電子郵件</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
     <div><dt>電話</dt><dd><a href="tel:{HQ_PHONE.replace('-', '')}">{HQ_PHONE}</a></dd></div>
     <div><dt>傳真</dt><dd>+886-7-803-2211</dd></div>
     <div><dt>地址</dt><dd>臺灣高雄市小港區台機路 24 號（81246）</dd></div></dl></div>
   <div class="contact-card"><h2>各地據點</h2><p>九大生產基地與海外貿易據點的地址與電話。</p><a class="text-link" href="{p.url('locations')}">查看全球據點 <span aria-hidden="true">→</span></a></div>
   <div class="contact-card"><h2>技術問題</h2><p>先查看常見鑄造問題與參數對照表。</p><a class="text-link" href="{p.url('support')}">前往技術支援 <span aria-hidden="true">→</span></a></div>
  </div>
 </div>
</section>''')


BODIES = {'zh-Hant': dict(home=home, about=about, products=products, technology=technology,
                          sustainability=sustainability, support=support, locations=locations, contact=contact)}


def placeholder(p):
    ui = LANGS[p.lang]['ui']
    return document(p, ui['stub_title'] if p.key == 'home' else f'{ui[p.key]}', ui['stub_body'], f'''
<section class="page-hero dark stub">
 <div class="wrap page-hero-grid">
  <div><p class="eyebrow">{e(LANGS[p.lang]['name'])}</p><h1>{e(ui[p.key])}</h1>
   <p class="lead">{e(ui['stub_title'])}</p><p>{e(ui['stub_body'])}</p>
   <div class="actions"><a class="btn btn-molten btn-lg" href="{p.url(p.key, 'zh-Hant')}" hreflang="zh-Hant">{e(ui['stub_cta'])} <span aria-hidden="true">→</span></a>
    <a class="btn btn-ghost btn-lg" href="mailto:{EMAIL}">{EMAIL}</a></div></div>
  <div class="page-hero-art">{art('hero', 'art-dark')}</div>
 </div>
</section>''', index=False)


def not_found():
    p = Page('zh-Hant', 'home')
    p.out = '404.html'
    p.root = '/sigma/'  # 404 is served at arbitrary depth; GitHub Pages project path
    body = f'''<section class="page-hero dark stub"><div class="wrap page-hero-grid"><div>
<p class="eyebrow">404 · PAGE NOT FOUND</p><h1>找不到這個頁面</h1>
<p class="lead">頁面可能已搬移。舊網站的網址已不再使用，請從以下入口繼續瀏覽。</p>
<div class="actions"><a class="btn btn-molten btn-lg" href="{p.root}">回到首頁</a><a class="btn btn-ghost btn-lg" href="{p.root}products/">產品中心</a><a class="btn btn-ghost btn-lg" href="{p.root}contact/">聯絡我們</a></div>
</div><div class="page-hero-art">{art('ingots', 'art-dark')}</div></div></section>'''
    return document(p, '找不到頁面', '找不到頁面', body, index=False)


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    GENERATED.append(rel)


def main():
    for lang in LANGS:
        for key, _ in ROUTES:
            p = Page(lang, key)
            builder = BODIES.get(lang, {}).get(key)
            html = builder(p) if builder else placeholder(p)
            write(p.out + 'index.html', html)
    write('404.html', not_found())
    urls = ''.join(f'<url><loc>{BASE_URL + LANGS[l]["prefix"] + r}</loc></url>' for l in LANGS if l in TRANSLATED for _, r in ROUTES)
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n')
    (ROOT / 'tools' / 'generated.json').write_text(json.dumps(sorted(GENERATED), indent=1) + '\n')
    print(f'Built {len(GENERATED)} files (version {VERSION}).')


if __name__ == '__main__':
    main()
