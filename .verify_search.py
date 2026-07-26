import json
import subprocess
from pathlib import Path

base = Path("/Users/andrew/Documents/скрипты hermes/web-search")
cli = base / ".venv" / "bin" / "python"
script = base / "search.py"

checks = []

def check(name, condition, detail=''):
    status = 'PASS' if condition else 'FAIL'
    checks.append((name, status, detail))
    print(f'[{status}] {name} {detail}'.rstrip())

help_out = subprocess.run([str(cli), str(script), "--help"], capture_output=True, text=True)
check('search.py --help rc=0', help_out.returncode == 0)
check('searx/brave/yandex in help', all(x in help_out.stdout for x in ['searx', 'brave', 'yandex']))

queries = [
    "coinglass crypto funding rate",
    "cryptopanic latest crypto news",
    "BTC ETF inflows today",
]
real_results_found = False
for q in queries:
    out = subprocess.run(
        [str(cli), str(script), q, "-n", "3", "-b", "auto", "--json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    check(f'auto search rc={q}', out.returncode == 0, f'q={q}')
    body = (out.stdout or out.stderr).strip()
    has_results = False
    try:
        data = json.loads(out.stdout)
        has_results = isinstance(data, list) and len(data) > 0
    except Exception:
        pass
    check(f'auto search results={q}', has_results, f'q={q}')
    real_results_found = real_results_found or has_results
    print(f'=== {q} ===')
    print(body[:700])
    print()

check('any real search results across auto backends', real_results_found)

failed = [c for c in checks if c[1] == 'FAIL']
print(f'SUMMARY: {len(checks) - len(failed)}/{len(checks)} passed')
if failed:
    print('FAILED:')
    for c in failed:
        print(f' - {c[0]}: {c[2]}')
