#!/usr/bin/env python3
"""
Cleanup corrupted-title and duplicate files in tennis-wiki.

Phase 1: 9 corrupted-title files (have [[...]] in title, mostly junk)
Phase 2: 4 neuro-motor duplicates (keep the-neuro-motor-manual-of-tennis-mastery-full)
Phase 3: 3 Art of Modern Tennis duplicates in ky-thuat (kept version in cam-nang)
Phase 4: 1 UUID-nonsense file (duplicate of tennis-volley-deep-research)
Phase 5: 1 tfl-tennis-3-0-scaffold (keep tfl-tennis-3-0-details)

Total: 18 files to delete
"""
import re
import os
from pathlib import Path

DOCS = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs")


# Phase 1: 9 corrupted-title files (definite junk)
PHASE1 = [
    'co-sinh-hoc/tennis-training-manual-architecture',
    'ky-thuat/extended-wiki-chapters-1-12',
    'ky-thuat/modern-tennis-volley-handbook-2026-docx',
    'ky-thuat/tennis-backhand-techniques-esssential-detailed-report',
    'ky-thuat/tennis-biomechanics-ground-reaction-forces',
    'ky-thuat/tennis-biomechanics-manual-conversion',
    'ky-thuat/tennis-return-of-serve-positioning-geometry',
    'ky-thuat/the-integration-of-sensory-systems-and-neural-feedback-loops',
    'wiki/tennis-neurological-specialist-1',
]
# KEEP despite title corruption (have real content):
# - ky-thuat/tennis-volley-deep-research.md (5130 lines real research)
# - ky-thuat/tennis-manual-chapter12.md (handled in Phase 3)

# Phase 2: 4 neuro-motor duplicates
PHASE2 = [
    'ky-thuat/neuro-motor-manual-of-tennis-mastery-1',
    'ky-thuat/neuro-motor-manual-of-tennis-mastery-complete-corrected',
    'ky-thuat/neuro-motor-manual-of-tennis-mastery-complete',
    'ky-thuat/neuro-motor-manual-of-tennis-mastery-final',
]
# Keep: the-neuro-motor-manual-of-tennis-mastery-full (4544 lines, complete)

# Phase 3: Art of Modern Tennis duplicates
PHASE3 = [
    'ky-thuat/ence-manual-for-elite-players-and-coaches-tennis-manual-full',
    'ky-thuat/tennis-manual-chapter12',
    'ky-thuat/tennis-manual-full',
]
# Real version: cam-nang/the-art-of-modern-tennis-a-complete-reference-manual-for-elite-players-and-coach.md

# Phase 4: UUID-nonsense file
PHASE4 = [
    'ky-thuat/4377bb3b-3d48-4d81-a1b6-103191b2b3ca',
]
# Real: ky-thuat/tennis-volley-deep-research.md

# Phase 5: tfl-tennis-3-0 (keep details, delete scaffold)
PHASE5_DELETE = [
    'ky-thuat/tfl-tennis-3-0-scaffold',  # shorter (508 lines)
]
# Keep: tfl-tennis-3-0-details (3248 lines, more complete)

# Combine
all_to_delete = PHASE1 + PHASE2 + PHASE3 + PHASE4 + PHASE5_DELETE
all_to_delete = list(dict.fromkeys(all_to_delete))

print(f"=== Files to delete: {len(all_to_delete)} ===")
for f in all_to_delete:
    print(f"  - {f}")


print("\n=== Fixing incoming links ===")
# Build a single mega-regex of all patterns
all_pats = []
for deleted in all_to_delete:
    cat, sl = deleted.split('/')
    all_pats.append(rf'\[[^\]]*\]\(\.\./{re.escape(cat)}/{re.escape(sl)}\.md\)')
    all_pats.append(rf'\[[^\]]*\]\({re.escape(cat)}/{re.escape(sl)}\.md\)')
    all_pats.append(rf'\[[^\]]*\]\({re.escape(sl)}\.md\)')
mega_pat = re.compile('|'.join(all_pats))
deleted_set = set([f"{x}.md" for x in all_to_delete])

total_changes = 0
for f in DOCS.rglob("*.md"):
    rel = str(f.relative_to(DOCS))
    if rel in deleted_set:
        continue
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

print(f"Total link fixes: {total_changes}")

# Step 2: Delete files
print("\n=== Deleting files ===")
for path in all_to_delete:
    f = DOCS / f"{path}.md"
    if f.exists():
        f.unlink()
        print(f"  ✓ Deleted: {path}.md")
    else:
        print(f"  - Not found: {path}.md")

# Verify
remaining = sum(1 for _ in DOCS.rglob('*.md') if _.name != 'index.md')
print(f"\n=== Remaining non-index files: {remaining} ===")
