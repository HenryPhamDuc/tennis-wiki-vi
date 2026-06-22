#!/usr/bin/env python3
"""Final fix: strip remaining .docx links (TOC files, broken names)."""
import re
from pathlib import Path

DST = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\tennisplayer")

# Strip any .docx link, keep just the link text
# Match: [text](path.docx) with URL-encoded paths and special chars
DOCX_LINK = re.compile(r'\[([^\]]+)\]\(([^)]*\.docx)\)')

# Specific pattern for TOC files
TOC_LINK = re.compile(r'\[([^\]]*)\]\([^)]*TOC\.docx\)')

total_stripped = 0
files_changed = 0

for md_file in DST.rglob("*.md"):
    if md_file.name == 'index.md':
        continue
    text = md_file.read_text(encoding='utf-8', errors='replace')
    original = text
    file_count = [0]

    # Strip TOC links first
    def strip_toc(m):
        if 'TOC' in m.group(0).upper():
            file_count[0] += 1
            return m.group(1) if m.group(1).strip() else ''
        return m.group(0)
    text = TOC_LINK.sub(strip_toc, text)

    # Strip remaining .docx links that won't resolve
    def strip_residual(m):
        link_text = m.group(1)
        link_target = m.group(2)
        # Decode URL
        from urllib.parse import unquote
        decoded = unquote(link_target)
        # Check if file exists
        basename = decoded.split('/')[-1].split('\\')[-1]
        if not basename.endswith('.docx'):
            return m.group(0)
        # Search for it in any section
        target_slug = re.sub(r'\.docx$', '', basename)
        target_slug = re.sub(r'[<>:"/\\|?*]', '', target_slug)
        target_slug = re.sub(r'\s+', '-', target_slug).lower().strip('-')[:100]
        # Check any section
        found = False
        for section_dir in DST.iterdir():
            if section_dir.is_dir() and (section_dir / f"{target_slug}.md").exists():
                found = True
                break
        if not found:
            file_count[0] += 1
            return link_text if link_text else ''
        return m.group(0)

    text = DOCX_LINK.sub(strip_residual, text)

    if text != original:
        md_file.write_text(text, encoding='utf-8')
        files_changed += 1
        total_stripped += file_count[0]

print(f"Stripped {total_stripped} broken .docx links in {files_changed} files")
