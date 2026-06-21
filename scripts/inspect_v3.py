#!/usr/bin/env python3
"""Inspect VN_Tennis_Vault_v3_Final."""
from pathlib import Path
import os

SRC = Path(r"C:\Users\Henry\Documents\MY VAULT\Documents\Obsidian Vault\tennis-vault\VN_Tennis_Vault_v3_Final\VN_Tennis_Vault")
files = sorted(SRC.rglob("*.md"))
print(f"Total: {len(files)}")
print()

# By subdir
from collections import defaultdict
by_sub = defaultdict(list)
for f in files:
    rel = f.relative_to(SRC)
    by_sub[rel.parts[0]].append(f)

for sub, items in by_sub.items():
    print(f"  {sub:30s} {len(items):3d} files")

print()
print("=== Top 10 by size ===")
sized = [(f, f.stat().st_size) for f in files]
sized.sort(key=lambda x: -x[1])
for f, s in sized[:10]:
    rel = f.relative_to(SRC)
    print(f"  {s//1024:5d}KB  {rel}")

print()
# First 30 chars of content
print("=== Content samples ===")
for f in sized[0:3]:
    print(f"\n--- {f[0].name} ---")
    print(f[0].read_text(encoding='utf-8', errors='replace')[:400])
