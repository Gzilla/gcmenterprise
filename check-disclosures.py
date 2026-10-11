#!/usr/bin/env python
"""Check the legal disclosure block across every page.

Earlier this asserted the whole block was byte-identical everywhere. That
held while every page sold the same thing. /marketing/ does not: its block
legitimately names marketing analysis in the services list, swaps the
securities-specific non-solicitation sentence for ad-campaign ones, and
describes a different specimen.

So byte-identity is the wrong test. What must not drift are the paragraphs
that describe the SITE rather than the service:

  - the Google Analytics paragraph (how the site behaves)
  - the copyright line

Those are compared exactly. Everything else is reported for human review
rather than failed, so a real divergence is visible without the check
crying wolf on an intended difference.

    python check-disclosures.py     -> exit 0 clean, 1 on drift
"""
import io, re, sys, glob, hashlib, html as H

BLOCK = re.compile(r'<div class="legal">(.*?)\n    </div>', re.S)
SHARED = [("analytics", "This site uses Google Analytics"),
          ("copyright", "All rights reserved")]

def paras(path):
    m = BLOCK.search(io.open(path, encoding="utf-8").read())
    if not m:
        return None
    return [re.sub(r"\s+", " ", H.unescape(re.sub("<[^>]+>", "", p))).strip()
            for p in re.findall(r"<p[^>]*>(.*?)</p>", m.group(1), re.S)]

pages = sorted(glob.glob("index.html") + glob.glob("*/index.html"))
data = {}
for p in pages:
    ps = paras(p)
    if ps is None:
        print("  MISSING disclosure block: %s" % p); sys.exit(1)
    data[p] = ps

print("  pages checked: %d" % len(data))
fail = False
for label, needle in SHARED:
    found = {}
    for p, ps in data.items():
        hit = [x for x in ps if needle in x]
        if not hit:
            print("  %-10s MISSING in %s" % (label, p)); fail = True; continue
        found[p] = hashlib.sha256(hit[0].encode()).hexdigest()[:16]
    if found and len(set(found.values())) == 1:
        print("  %-10s identical across all pages  %s" % (label, next(iter(found.values()))))
    elif found:
        print("  %-10s DRIFT:" % label); fail = True
        for p, h in found.items():
            print("      %-26s %s" % (p, h))

base = data.get("index.html", [])
for p, ps in data.items():
    if p == "index.html":
        continue
    diff = [i + 1 for i, (a, b) in enumerate(zip(base, ps)) if a != b]
    extra = "" if len(base) == len(ps) else "  (paragraph COUNT differs: %d vs %d)" % (len(base), len(ps))
    print("  %-26s service-specific paragraphs: %s%s" % (p, diff or "none", extra))

sys.exit(1 if fail else 0)
