# SIGMA 新格集團 — corporate website

[Live GitHub Pages](https://ed100084.github.io/sigma/)

Multi-page corporate website for SIGMA Group (再生鋁合金、鋁液直供、鋅合金). Traditional Chinese content, language framework for 简体中文 / English / 日本語. Industrial style: graphite, mineral white, molten orange; isometric technical line art. Static HTML/CSS/JS, no framework, no runtime third-party requests.

## Structure
| Path | Page |
|---|---|
| `/` | 首頁 |
| `/about/` | 關於新格（簡介、理念、規模、產業園、沿革） |
| `/products/` | 產品中心（ADC 系列含成分比較、A356.2、3104/5182/6063/3033、鋁液直供、鋅合金、YSBC3、原料採購） |
| `/technology/` | 製程與品質 |
| `/sustainability/` | 永續循環 |
| `/support/` | 技術支援（37 則可搜尋問答、壓鑄參數表） |
| `/locations/` | 全球據點（14 個據點，可篩選） |
| `/contact/` | 聯絡我們（表單產生寄往 info@sigmasha.com 的電子郵件） |
| `/zh-hans/` `/en/` `/ja/` | 各語言同路由；未翻譯頁為 noindex 佔位頁，連回繁中 |

## Editing content
All HTML is generated. Do not edit the HTML files by hand.

| File | Holds |
|---|---|
| `tools/site_data.py` | Alloy compositions, locations, history |
| `tools/faq.py` | Technical Q&A and casting tables |
| `tools/i18n.py` | Languages, routes, UI strings |
| `tools/build.py` | Page bodies and layout; `VERSION` is the asset cache key (bump on every CSS/JS/font change, also in `assets/site.css` font URL) |
| `tools/art.py` | Generates `src/art/*.svg` isometric illustrations |

```sh
python3 tools/art.py          # only when illustrations change
python3 tools/build.py
NODE_PATH=/tmp/fontwork/node_modules node tools/font_subset.mjs   # after copy changes; setup in file header
```
To translate a language: add body builders for it in `build.py`, register them in `BODIES`, and add the language to `TRANSLATED` so it gets indexed and hreflang links. When the official domain goes live, change `BASE_URL` in `build.py`.

## Preview and checks
```sh
python3 -m http.server 4286 --bind 127.0.0.1
python3 docs/verify-site.py [--source]    # links, ids, aria refs, wording, 40 ADC values vs source sheet
python3 docs/run-browser-checks.py        # 4 widths × 8 pages, menu, language switch, comparison, search, filter, form, axe, no-JS
python3 docs/check-public.py              # after deploy: public bytes == checkout
```
`docs/throttled-performance.js` (via `playwright-cli run-code`) gives lab LCP/CLS under 150 ms latency, 1.6 Mbps, 4× CPU. Lab results are not field Core Web Vitals; axe passing does not certify WCAG conformance.

## Deploy
GitHub Pages serves the `main` branch root (`.nojekyll`). Push, confirm the Pages run for the pushed SHA, then run `check-public.py`.

## Launch checklist (not done yet)
- Company approval of copy, figures and certification list; real photography if available.
- Real form backend (current form opens the visitor's email client).
- Custom domain, `BASE_URL` update, redirects from old `.aspx` URLs (handled at the domain's server/DNS).
- Translations for 简体中文 / English / 日本語.
# sigmaopus55
