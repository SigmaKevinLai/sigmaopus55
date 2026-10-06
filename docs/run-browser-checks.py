"""Run the multi-page browser checks and fail on CLI-reported browser errors.
python3 docs/run-browser-checks.py [http://127.0.0.1:4286/]
Requires globally installed playwright-cli + Chromium, a running preview, and the
axe-core bundle at /tmp/sigma-axe.min.js.
"""
from pathlib import Path
import os, subprocess, sys, uuid
root = Path(__file__).resolve().parent.parent
url = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:4286/'
assert url.startswith(('http://', 'https://')), 'HTTP(S) target required'
assert Path('/tmp/sigma-axe.min.js').is_file(), 'Place the axe-core bundle at /tmp/sigma-axe.min.js'
session = 'sigma-audit-' + uuid.uuid4().hex[:8]
env = {**os.environ, 'PLAYWRIGHT_MCP_BROWSER': 'chromium'}


def run(*args):
    result = subprocess.run(['playwright-cli', '-s=' + session, *args], cwd=root, env=env, text=True, capture_output=True, timeout=600)
    print(result.stdout, end=''); print(result.stderr, end='', file=sys.stderr)
    if result.returncode or '### Error' in result.stdout or '### Error' in result.stderr:
        raise RuntimeError('Browser check failed: ' + ' '.join(args))


try:
    run('open', url)
    run('run-code', '--filename=docs/browser-checks.js')
    print('\nPASS: multi-page browser checks.', flush=True)
finally:
    subprocess.run(['playwright-cli', '-s=' + session, 'close'], cwd=root, env=env, timeout=30, check=False)
