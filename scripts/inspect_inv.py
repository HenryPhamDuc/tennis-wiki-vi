#!/usr/bin/env python3
"""Inspect PDF inventory sample."""
import json
from pathlib import Path

data = json.load(open(r"C:\Users\Henry\Documents\tennis-wiki\scripts\pdf_inventory.json", encoding='utf-8'))

# Sample by name
tennis_named = []
for p, v in data.items():
    name = Path(p).name.lower()
    if any(k in name for k in ['tennis', 'racket', 'racquet', 'forehand', 'backhand', 'volley', 'serve', 'usta', 'atp', 'wimbledon', 'biomech']):
        tennis_named.append((Path(p).name, v['size'], v['pages'], v['score']))

print(f"Total files: {len(data)}")
print(f"Files with tennis-related names: {len(tennis_named)}")
print()
print("First 30 tennis-named files:")
for n, s, pg, sc in sorted(tennis_named)[:30]:
    print(f"  score={sc:2d}  pages={pg:3d}  size={s//1024:5d}KB  {n[:70]}")

# Sample one to see first chars
print()
print("=" * 70)
print("Sample first chars (first 600):")
sample = [k for k in data if 'Anatomy-of-Modern' in k][0]
print(f"File: {Path(sample).name}")
print(repr(data[sample]['first_chars'][:600]))
