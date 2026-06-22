#!/usr/bin/env python3
"""Fix inter-article .docx links in tennisplayer MD files."""
import re
from pathlib import Path
from urllib.parse import unquote

DST = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\tennisplayer")


def slugify(text):
    text = text.replace('.docx', '').replace('.html', '')
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-').lower()
    return text[:100]


def find_target_md(basename, current_section_slug):
    target_slug = slugify(basename)
    if (DST / current_section_slug / f"{target_slug}.md").exists():
        return target_slug, ""
    for section_dir in DST.iterdir():
        if section_dir.is_dir() and (section_dir / f"{target_slug}.md").exists():
            return target_slug, f"../{section_dir.name}/"
    return None, None


LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+\.docx)\)')
LINK_PATTERN_ENCODED = re.compile(r'\[([^\]]*)\]\(([^)]*%[^)]+)\)')

total_fixed = 0
files_fixed = 0

for md_file in DST.rglob("*.md"):
    if md_file.name == 'index.md':
        continue
    text = md_file.read_text(encoding='utf-8', errors='replace')
    original = text
    current_section = md_file.parent.name
    file_fixed_count = [0]

    def make_replacer():
        def replace_link(match):
            link_text = match.group(1)
            link_target = match.group(2)
            link_target_decoded = unquote(link_target)
            basename = link_target_decoded.split('/')[-1].split('\\')[-1]
            if not basename.endswith('.docx'):
                return match.group(0)
            target_slug, prefix = find_target_md(basename, current_section)
            if target_slug:
                file_fixed_count[0] += 1
                return f'[{link_text}]({prefix}{target_slug}.md)'
            else:
                return link_text if link_text else ''
        return replace_link

    text = LINK_PATTERN.sub(make_replacer(), text)
    text = LINK_PATTERN_ENCODED.sub(make_replacer(), text)

    if text != original:
        md_file.write_text(text, encoding='utf-8')
        files_fixed += 1
        total_fixed += file_fixed_count[0]

print(f"Fixed {total_fixed} .docx links in {files_fixed} files")
