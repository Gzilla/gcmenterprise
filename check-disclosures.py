#!/usr/bin/env python
"""Assert the legal disclosure block is byte-identical on every page.

Standing rule: the disclosure block appears on EVERY page verbatim and
unmodified. There is no build step and no templating, so the block is
duplicated per page and the first hand-edit silently desynchronises
legally load-bearing text. Run this before every commit.

    python check-disclosures.py        -> exit 0 clean, 1 on drift
"""
import io, re, sys, glob, hashlib

BLOCK = re.compile(r'<div class="legal">(.*?)\n    </div>', re.S)

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

pages = sorted(glob.glob('index.html') + glob.glob('*/index.html'))
found = {}
for p in pages:
    m = BLOCK.search(io.open(p, encoding='utf-8').read())
    if not m:
        print('  MISSING disclosure block: %s' % p)
        sys.exit(1)
    found[p] = hashlib.sha256(norm(m.group(1)).encode()).hexdigest()[:16]

print('  pages checked: %d' % len(found))
for p, h in found.items():
    print('    %-28s %s' % (p, h))

if len(set(found.values())) == 1:
    print('  OK - disclosure block identical across all pages')
    sys.exit(0)
print('  DRIFT - the disclosure block differs between pages')
sys.exit(1)
