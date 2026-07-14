#!/usr/bin/env python3
"""Batch reformat all HTML files in docs/cam-nang/tfl/"""

import os
import glob
import sys
sys.path.insert(0, r"C:\Users\Henry\GITHUB\tennis-wiki-vi\scripts")
from reformat_tfl_html import reformat

SRCDIR = r"C:\Users\Henry\GITHUB\tennis-wiki-vi\docs\cam-nang\tfl"

files = glob.glob(os.path.join(SRCDIR, "*.html"))
# Exclude backups
files = [f for f in files if not f.endswith(".bak")]

print(f"Found {len(files)} HTML files to reformat\n")

for i, f in enumerate(files, 1):
    filename = os.path.basename(f)
    print(f"[{i}/{len(files)}] {filename}")
    try:
        result = reformat(f)
        print(f"  → {result['original_lines']} lines → {result['output_lines']} lines")
        print(f"  → ASCII: {result['ascii_blocks']}, Cards: {result['cards_converted']}, Steps: {result['steps_tagged']}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
    print()

print("✅ Batch complete!")