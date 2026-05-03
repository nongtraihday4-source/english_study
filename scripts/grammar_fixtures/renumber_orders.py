#!/usr/bin/env python3
"""
Renumber order values in existing gen_a1_p*.py files to make room for 9 new topics.
Old → New mappings:
  Inserted at 4,5 (PP, PPC):      old 4..6 → 6..8
  Inserted at 9,10 (PastP, PPC):  old 7..8 → 11..12
  Inserted at 13,14,15,16,17:     old 9..30 → 18..39
"""
import re, os

MAPPINGS = {
    "gen_a1_p1.py": {4: 6},
    "gen_a1_p2.py": {5: 7, 6: 8, 7: 11, 8: 12, 9: 18, 10: 19, 11: 20},
    "gen_a1_p3.py": {12: 21, 13: 22, 14: 23, 15: 24, 16: 25, 17: 26, 18: 27},
    "gen_a1_p4.py": {
        19: 28, 20: 29, 21: 30, 22: 31, 23: 32,
        24: 33, 25: 34, 26: 35, 27: 36, 28: 37, 29: 38, 30: 39
    },
}

base = os.path.dirname(__file__)
for fname, mapping in MAPPINGS.items():
    path = os.path.join(base, fname)
    with open(path) as f:
        content = f.read()

    def replace_order(m):
        n = int(m.group(1))
        new_n = mapping.get(n, n)
        return f'"order": {new_n},'

    new_content = re.sub(r'"order": (\d+),', replace_order, content)
    with open(path, "w") as f:
        f.write(new_content)
    changes = [(k,v) for k,v in mapping.items()]
    print(f"  {fname}: updated {changes}")

print("✅ Renumbering done.")
