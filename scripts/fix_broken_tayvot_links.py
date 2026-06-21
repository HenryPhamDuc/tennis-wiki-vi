#!/usr/bin/env python3
"""
Fix all broken tay-vot links across the site.
For each broken link, either:
  - Replace with equivalent in another category
  - Remove the link entirely
"""
import re
import os
from pathlib import Path

DOCS = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs")

# Map of deleted tay-vot slugs to replacement (slug, target_category) or None
# target is the target's slug in another category, and category for relative path
# NOTE: Keys include subfolder prefix (e.g. 'federer/foo') for files that were in subdirs
REPLACEMENTS = {
    # alcaraz subfolder
    'alcaraz/alcaraz-forehand': ('roger-federer-forehand-guide-18', 'ky-thuat'),  # federer instead of alcaraz (no alcaraz equiv)
    'alcaraz/forehand-technique-comparison---rublev-vs-alcaraz-vs-sinner': ('forehand-technique-comparison-rublev-vs-alcaraz-vs-sinner', 'he-thong'),
    # root level
    'chương-1': None,
    'chuong-21': None,
    'determination---quyết-tâm': None,
    'embodied-cognition': None,
    'hồi-phục-sau-cú-đánh': None,
    'mingmen': ('dantian', 'ky-thuat'),
    'phong-cách-hiện-đại---compact-power': ('compact-power-analysis', 'ky-thuat'),
    'song-trong-tennis-hien-dai': ('tạo-sóng-trong-tennis', 'ky-thuat'),
    'tải-cơ-thể': ('trọng-tâm-cơ-thể', 'ky-thuat'),
    'tennis-grip-pressure-and-neurological-threshold': None,
    'tennis-the-kình-engine': None,
    'two-engines': None,
    'vòng-lớn---vai': None,
    # federer subfolder
    'federer/federer-forehand': ('roger-federer-forehand-guide-18', 'ky-thuat'),
    'federer/one-hand-backhand-biomechanics': ('roger-federer-backhand-guide', 'ky-thuat'),
    # nadal subfolder
    'nadal/nadal-forehand': None,
}

# Build pattern for matching deleted slugs in links
# Links look like: [text](tay-vot/foo.md) or [text](../tay-vot/foo.md) or [text](foo.md) (when in tay-vot/)
slugs_to_fix = list(REPLACEMENTS.keys())


def fix_links(content, is_in_tay_vot=False, verbose=False):
    """Fix all broken tay-vot links in the content."""
    changes = 0
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line is None:
            continue
        new_line = line
        # Check each broken slug
        for slug in slugs_to_fix:
            # If line was already marked for removal, stop
            if new_line is None:
                break
            # Match various link patterns
            # [text](tay-vot/slug.md) or [text](../tay-vot/slug.md)
            pat1 = rf'\[([^\]]*)\]\((?:\.\./)?tay-vot/{re.escape(slug)}\.md\)'
            # [text](slug.md) when in tay-vot/ subdir
            pat2 = rf'\[([^\]]*)\]\({re.escape(slug)}\.md\)'

            matched = False
            for pat in (pat1, pat2):
                m = re.search(pat, new_line)
                if m:
                    text = m.group(1)
                    replacement = REPLACEMENTS[slug]
                    if replacement is None:
                        # Mark line for removal (set to None)
                        new_line = None
                        changes += 1
                        if verbose:
                            print(f"  REMOVE: {slug} -> '{text}'")
                    else:
                        target_slug, target_cat = replacement
                        new_link = f"[{text}](../{target_cat}/{target_slug}.md)"
                        new_line = re.sub(pat, new_link, new_line)
                        changes += 1
                        if verbose:
                            print(f"  REPLACE: {slug} -> {target_cat}/{target_slug}")
                    matched = True
                    break
        if new_line is not None:
            new_lines.append(new_line)
    return '\n'.join(new_lines), changes


# Walk all MD files
total_changes = 0
for f in DOCS.rglob("*.md"):
    if f.name == "index.md":
        continue
    is_in_tay_vot = f.parent.name == "tay-vot"
    content = f.read_text(encoding='utf-8', errors='replace')
    new_content, changes = fix_links(content, is_in_tay_vot=is_in_tay_vot, verbose=False)
    if changes > 0:
        print(f"{f.relative_to(DOCS)}: {changes} changes")
        f.write_text(new_content, encoding='utf-8')
        total_changes += changes

print(f"\n=== Total changes: {total_changes} ===")
