#!/usr/bin/env python3
"""Fix media links in tennisplayer MD files by stripping them or converting to inline."""
import re
from pathlib import Path

DST = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\tennisplayer")

# Pattern for pandoc-generated media links
# ![alt](media/image1.png)
MEDIA_PATTERNS = [
    (re.compile(r'!\[[^\]]*\]\(media/[^)]+\)\s*\{[^}]*\}'), ''),  # with size attrs
    (re.compile(r'!\[[^\]]*\]\(media/[^)]+\)'), ''),                # plain
    (re.compile(r'\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)'), ''),       # wrapped
    (re.compile(r'\[\s*!\[[^\]]*\]\(media/[^)]+\)\s*\{[^}]*\}\s*\]\([^)]*\)'), ''),
]


total_cleaned = 0
files_cleaned = 0

for md_file in DST.rglob("*.md"):
    text = md_file.read_text(encoding='utf-8', errors='replace')
    original = text
    file_cleaned = 0

    for pattern, replacement in MEDIA_PATTERNS:
        new_text = pattern.sub(replacement, text)
        if new_text != text:
            file_cleaned += text.count('media/')
            text = new_text

    if text != original:
        md_file.write_text(text, encoding='utf-8')
        files_cleaned += 1
        total_cleaned += file_cleaned

print(f"Cleaned {total_cleaned} media refs in {files_cleaned} files")
