"""Language framework.

Every route exists in every language. A page is "translated" when a body
builder exists for that language in build.py; otherwise a localized
placeholder (noindex) points visitors to the Traditional Chinese page.
To add a translation: write the body builder and register it in BODIES.
"""

ROUTES = [
    ('home', ''), ('about', 'about/'), ('products', 'products/'), ('technology', 'technology/'),
    ('sustainability', 'sustainability/'), ('support', 'support/'), ('locations', 'locations/'),
    ('contact', 'contact/'),
]
NAV = ['about', 'products', 'technology', 'sustainability', 'support', 'locations']

LANGS = {
    'zh-Hant': dict(prefix='', short='繁中', name='繁體中文', og='zh_TW', ui=dict(
        home='首頁', about='關於新格', products='產品中心', technology='製程與品質', sustainability='永續循環',
        support='技術支援', locations='全球據點', contact='聯絡我們',
        skip='跳至主要內容', menu='開啟選單', close='關閉選單', language='語言', cta='詢價與合作',
        group='SIGMA 新格集團', tagline='RECYCLING FOR A BETTER TOMORROW',
        footer_about='1978 年創立，深耕再生鋁合金、鋅合金製造與廢金屬貿易。',
        footer_sitemap='網站導覽', footer_contact='集團總部', top='回到頂端',
        stub_title='此頁面翻譯準備中', stub_body='', stub_cta='', breadcrumb='目前位置')),
    'zh-Hans': dict(prefix='zh-hans/', short='简中', name='简体中文', og='zh_CN', ui=dict(
        home='首页', about='关于新格', products='产品中心', technology='制程与品质', sustainability='永续循环',
        support='技术支持', locations='全球据点', contact='联系我们',
        skip='跳至主要内容', menu='打开菜单', close='关闭菜单', language='语言', cta='询价与合作',
        group='SIGMA 新格集团', tagline='RECYCLING FOR A BETTER TOMORROW',
        footer_about='1978 年创立，深耕再生铝合金、锌合金制造与废金属贸易。',
        footer_sitemap='网站导览', footer_contact='集团总部', top='回到顶端',
        stub_title='简体中文内容准备中',
        stub_body='本页面的简体中文版本正在编写。完整的公司、产品与技术资料，目前请参阅繁体中文版本。',
        stub_cta='前往繁体中文版本', breadcrumb='当前位置')),
    'en': dict(prefix='en/', short='EN', name='English', og='en_US', ui=dict(
        home='Home', about='About', products='Products', technology='Process & Quality', sustainability='Sustainability',
        support='Technical Support', locations='Locations', contact='Contact',
        skip='Skip to main content', menu='Open menu', close='Close menu', language='Language', cta='Enquiries',
        group='SIGMA Group', tagline='RECYCLING FOR A BETTER TOMORROW',
        footer_about='Founded in 1978. Secondary aluminium and zinc alloys, molten aluminium supply and scrap metal trading.',
        footer_sitemap='Site map', footer_contact='Group headquarters', top='Back to top',
        stub_title='English version in preparation',
        stub_body='This page is being translated into English. Full company, product and technical information is currently available in Traditional Chinese.',
        stub_cta='View the Traditional Chinese page', breadcrumb='You are here')),
    'ja': dict(prefix='ja/', short='日本語', name='日本語', og='ja_JP', ui=dict(
        home='ホーム', about='会社概要', products='製品情報', technology='製造・品質', sustainability='サステナビリティ',
        support='技術サポート', locations='拠点一覧', contact='お問い合わせ',
        skip='本文へ移動', menu='メニューを開く', close='メニューを閉じる', language='言語', cta='お問い合わせ',
        group='SIGMA 新格グループ', tagline='RECYCLING FOR A BETTER TOMORROW',
        footer_about='1978年創業。再生アルミニウム合金・亜鉛合金の製造と金属スクラップ貿易。',
        footer_sitemap='サイトマップ', footer_contact='グループ本社', top='ページの先頭へ',
        stub_title='日本語ページ準備中',
        stub_body='このページの日本語版は現在準備中です。会社・製品・技術情報の詳細は、繁體中文版をご覧ください。',
        stub_cta='繁體中文版を見る', breadcrumb='現在地')),
}
