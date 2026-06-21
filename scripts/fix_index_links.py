#!/usr/bin/env python3
"""Fix incoming links to deleted files (including index.md)."""
import re
from pathlib import Path

DOCS = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs")

all_to_delete = [
    'co-sinh-hoc/tennis-training-manual-architecture',
    'ky-thuat/extended-wiki-chapters-1-12',
    'ky-thuat/modern-tennis-volley-handbook-2026-docx',
    'ky-thuat/tennis-backhand-techniques-esssential-detailed-report',
    'ky-thuat/tennis-biomechanics-ground-reaction-forces',
    'ky-thuat/tennis-biomechanics-manual-conversion',
    'ky-thuat/tennis-return-of-serve-positioning-geometry',
    'ky-thuat/the-integration-of-sensory-systems-and-neural-feedback-loops',
    'wiki/tennis-neurological-specialist-1',
    'ky-thuat/neuro-motor-manual-of-tennis-mastery-1',
    'ky-thuat/neuro-motor-manual-of-tennis-mastery-complete-corrected',
    'ky-thuat/neuro-motor-manual-of-tennis-mastery-complete',
    'ky-thuat/neuro-motor-manual-of-tennis-mastery-final',
    'ky-thuat/ence-manual-for-elite-players-and-coaches-tennis-manual-full',
    'ky-thuat/tennis-manual-chapter12',
    'ky-thuat/tennis-manual-full',
    'ky-thuat/4377bb3b-3d48-4d81-a1b6-103191b2b3ca',
    'ky-thuat/tfl-tennis-3-0-scaffold',
]

all_pats = []
for deleted in all_to_delete:
    cat, sl = deleted.split('/')
    all_pats.append(rf'\[[^\]]*\]\(\.\./{re.escape(cat)}/{re.escape(sl)}\.md\)')
    all_pats.append(rf'\[[^\]]*\]\({re.escape(cat)}/{re.escape(sl)}\.md\)')
    all_pats.append(rf'\[[^\]]*\]\({re.escape(sl)}\.md\)')
mega_pat = re.compile('|'.join(all_pats))

total_changes = 0
for f in DOCS.rglob("*.md"):
    rel = str(f.relative_to(DOCS))
    if f.parent == DOCS and f.name == 'index.md':
        continue  # Skip main index only
    text = f.read_text(encoding='utf-8', errors='replace')
    new_lines = []
    changes = 0
    for line in text.split('\n'):
        if mega_pat.search(line):
            changes += 1
        else:
            new_lines.append(line)
    if changes > 0:
        new_text = '\n'.join(new_lines)
        f.write_text(new_text, encoding='utf-8')
        total_changes += changes
        print(f"  Fixed {changes} links in {rel}")

print(f"\nTotal link fixes: {total_changes}")
