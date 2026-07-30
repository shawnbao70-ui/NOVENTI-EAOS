"""Find duplicate button binds in smart_terminal app.js."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

js = Path("smart_terminal/ui/app.js").read_text(encoding="utf-8")
ids = re.findall(r'bind\("([^"]+)"', js)
c = Counter(ids)
dups = {k: v for k, v in c.items() if v > 1}
print("binds", len(ids), "unique", len(c), "dups", len(dups))
for k, v in sorted(dups.items()):
    print(f"{k}: {v}")

# HTML buttons without bind
html = Path("smart_terminal/ui/index.html").read_text(encoding="utf-8")
btn_ids = set(re.findall(r'id="(btn[^"]+)"', html))
bound = set(ids)
missing = sorted(btn_ids - bound)
extra = sorted(bound - btn_ids)
print("html buttons", len(btn_ids), "unbound", len(missing), "bound-no-html", len(extra))
for x in missing[:40]:
    print("UNBOUND", x)
for x in extra[:20]:
    print("NOHTML", x)
