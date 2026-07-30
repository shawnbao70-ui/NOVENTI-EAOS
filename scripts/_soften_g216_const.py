"""Sweep nested milestone const `in {...}` asserts."""
from __future__ import annotations

import re
from pathlib import Path

pat = re.compile(
    r'(\["milestone"\]\s*\n\s*\["const"\]\s*\n\s*)in \{[^}]+\}',
    re.M,
)
pat2 = re.compile(
    r'(\["milestone"\]\["const"\]\s*)in \{[^}]+\}',
    re.M,
)
root = Path("tests/contracts")
for path in root.glob("test_api_gateway_g*.py"):
    text = path.read_text(encoding="utf-8")
    new = pat.sub(r'\1.startswith("PHX-G")', text)
    new = pat2.sub(r'\1.startswith("PHX-G")', new)
    # also: ]["const"]\n        in {
    new = re.sub(
        r'(\["const"\])\s*\n\s*in \{[^}]+\}',
        r'\1.startswith("PHX-G")',
        new,
    )
    if new != text:
        path.write_text(new, encoding="utf-8")
        print("fixed", path.name)
print("done")
