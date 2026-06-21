#!/usr/bin/env python3
"""
Phase 2: Dedup + quality rank tennis PDFs.

Quality signals:
- Tennis score
- Number of pages (more = book/major treatise)
- Size (larger = more content)
- Title keywords (research, biomechanics, modern, advanced)
"""
import json
import re
from pathlib import Path
from collections import defaultdict

INVENTORY = json.load(open(r"C:\Users\Henry\Documents\tennis-wiki\scripts\pdf_inventory.json", encoding='utf-8'))

# Group by content hash
by_hash = defaultdict(list)
for p, v in INVENTORY.items():
    if v['score'] >= 1:  # tennis or maybe
        by_hash[v['hash']].append((p, v))

# Within each hash, pick the best one (largest + most pages + cleanest name)
def quality_key(item):
    path, v = item
    name = Path(path).name
    name_score = 0
    # Prefer clean names (no PDFDrive, no (1), no copy)
    if 'PDFDrive' not in name: name_score += 2
    if '(1)' in name: name_score -= 2
    if ' - Copy' in path: name_score -= 1
    if re.search(r'\(\d+\)', name) and 'PDFDrive' not in name: name_score -= 1
    # Bonus for research-quality keywords
    if any(k in name.lower() for k in ['biomechan', 'modern', 'advanced', 'kinetic', 'research', 'elite']):
        name_score += 1
    return (
        v['score'] * 1000 +          # tennis relevance most important
        name_score * 100 +            # then name quality
        v['pages'] * 2 +              # more pages = more content
        min(v['size'] // 10000, 100)  # cap size contribution
    )

# Pick one per hash
unique = []
for h, items in by_hash.items():
    items.sort(key=quality_key, reverse=True)
    unique.append(items[0])

# Sort by quality
unique.sort(key=lambda x: quality_key(x), reverse=True)

# Categorize
def categorize(item):
    path, v = item
    name = Path(path).name.lower()
    cats = []
    if 'biomechan' in name or 'kinematic' in name or 'kinetic chain' in name:
        cats.append('co-sinh-hoc')
    elif 'biomech' in name.lower():
        cats.append('co-sinh-hoc')
    if any(k in name for k in ['forehand', 'backhand', 'volley', 'serve', 'return', 'footwork', 'split step']):
        cats.append('ky-thuat')
    if any(k in name for k in ['tennis', 'racket', 'racquet', 'usta', 'atp', 'wta', 'wimbledon']):
        if not cats:
            cats.append('ky-thuat')
    if 'train' in name or 'drill' in name or 'practice' in name or 'condition' in name or 'fitness' in name:
        cats.append('the-luc')
    if 'tactic' in name or 'pattern' in name or 'strategy' in name or 'ranking' in name:
        cats.append('chien-thuat')
    if 'mental' in name or 'psychol' in name or 'focus' in name or 'concentr' in name:
        cats.append('tam-ly')
    if 'physiology' in name or 'anatomy' in name or 'skeletal' in name or 'muscle' in name:
        cats.append('co-sinh-hoc')
    if not cats:
        cats.append('tham-khao')
    return cats


# Top 50 by quality
print("=" * 80)
print(f"Total unique tennis-related PDFs after dedup: {len(unique)}")
print(f"Total raw tennis/maybe PDFs: {sum(len(v) for v in by_hash.values())}")
print()
print("Top 30 highest-quality tennis PDFs:")
print()
for i, (path, v) in enumerate(unique[:30], 1):
    name = Path(path).name
    cats = categorize((path, v))
    pages = v.get('pages', 0)
    sz_mb = v.get('size', 0) / 1024 / 1024
    print(f"  {i:2d}. score={v['score']:2d}  pages={pages:3d}  {sz_mb:5.1f}MB  [{'/'.join(cats)}]")
    print(f"      {name[:90]}")

# Categorize all
from collections import Counter
all_cats = Counter()
for item in unique:
    for c in categorize(item):
        all_cats[c] += 1
print()
print("By category (each PDF may belong to multiple):")
for cat, count in all_cats.most_common():
    print(f"  {cat:20s} {count:3d}")

# Save the unique list
out = r"C:\Users\Henry\Documents\tennis-wiki\scripts\pdf_unique.json"
with open(out, 'w', encoding='utf-8') as f:
    pdfs = []
    for path, v in unique:
        pdfs.append({
            'path': path,
            'name': Path(path).name,
            'size': v['size'],
            'pages': v['pages'],
            'score': v['score'],
            'hash': v['hash'],
            'categories': categorize((path, v)),
            'first_chars': v.get('first_chars', ''),
        })
    json.dump(pdfs, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(pdfs)} unique PDFs to {out}")
