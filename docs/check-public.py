"""Public artifact integrity check: compare every generated file and shared asset
on GitHub Pages byte-for-byte with the checkout.
python3 docs/check-public.py
An unavailable network is a failure, not an assumed deployment success.
"""
from pathlib import Path
import json, sys, urllib.request
root = Path(__file__).resolve().parent.parent
base = 'https://ed100084.github.io/sigma/'
files = json.loads((root / 'tools/generated.json').read_text()) + [
    'assets/site.css', 'assets/site.js', 'assets/favicon.svg', 'assets/og-image.png', 'assets/fonts/noto-tc-core.woff2']
for name in files:
    url = base + name.removesuffix('index.html')
    try:
        req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'Sigma-release-check'})
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
        if content != (root / name).read_bytes():
            raise ValueError('public bytes differ from checkout')
    except Exception as error:
        if name == '404.html' and getattr(error, 'code', None) == 404:
            continue
        print('FAIL:', name, str(error), file=sys.stderr, flush=True)
        sys.exit(1)
print(f'PASS: {len(files)} public artifacts match checkout; interaction testing is separate.')
