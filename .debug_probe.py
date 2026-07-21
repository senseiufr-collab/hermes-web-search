import sys
sys.path.insert(0, '/Users/andrew/Documents/скрипты hermes/web-search')
from search import search_bing
qs = [
    'Osaurus AI market size growth forecast',
    'Osurus AI industry trends 2025 2026',
    'Osurus AI competitors comparison',
]
for q in qs:
    r = search_bing(q, max_results=2)
    print('Q', q[:60], '->', len(r))
    for item in r:
        print(item)
