#!/usr/bin/env python3
"""
Convert H:/Play Tennis/tennisplayer.net/.docx files to tennis-wiki/docs/tennisplayer/

Strategy:
1. Read master TOC + 15 section TOCs to build hierarchy
2. Convert each .docx file using pandoc
3. Generate hub index (from master TOC) + 15 section indexes
4. Slugify titles, preserve relative path under tennisplayer/<section>/

Source: H:/Play Tennis/tennisplayer.net/
Target: C:/Users/Henry/Documents/tennis-wiki/docs/tennisplayer/
"""
import zipfile
import xml.etree.ElementTree as ET
import re
import os
import subprocess
import sys
import unicodedata
from pathlib import Path
from collections import OrderedDict

SRC = Path(r"H:\Play Tennis\tennisplayer.net")
DST = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\tennisplayer")
TMP = Path(r"C:\Users\Henry\AppData\Local\Temp\tennisplayer_md")

# Section TOCs (mapped to friendly section slugs)
TOC_MAP = OrderedDict([
    ("Ultimate Fundamentals", ("Fundamentals", "ultimate-fundamentals",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Ultimate Fundamentals\Ultimate Fundamentals TOC.docx")),
    ("Ultimate Drill Games", ("Fundamentals", "ultimate-drill-games",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Ultimate Drill Games\Ultimate Drill Games TOC.docx")),
    ("Teaching Systems", ("Fundamentals", "teaching-systems",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Teaching Systems\Teaching SystemsTOC.docx")),
    ("Famous Coaches", ("Fundamentals", "famous-coaches",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Famous Coaches\Famous Coaches TOC.docx")),
    ("Classic Lessons", ("Fundamentals", "classic-lessons",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Classic Lessons\Classic Lessons TOC.docx")),
    ("Footwork", ("Fundamentals", "footwork",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Footwork\Footwork TOC.docx")),
    ("Strategy and Statistics", ("Fundamentals", "strategy-and-statistics",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Strategy\Strategy TOC.docx")),
    ("Mental Game", ("Fundamentals", "mental-game",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Mental game\Mental game TOC.docx")),
    ("Physical Training", ("Fundamentals", "physical-training",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Physical Training\Physical Training TOC.docx")),
    ("High Performance", ("Fundamentals", "high-performance",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\High Performance\High Performance TOC.docx")),
    ("Advanced Tennis", ("Stroke Analysis", "advanced-tennis",
        r"H:\Play Tennis\tennisplayer.net\Stroke Analysis\Advanced Tennis\Advanced Tennis TOC.docx")),
    ("Science of Biomechanics", ("Stroke Analysis", "science-of-biomechanics",
        r"H:\Play Tennis\tennisplayer.net\Stroke Analysis\Biomechanics\Science of Biomechanics TOC.docx")),
    ("Mysteries of the Heavy Ball", ("Stroke Analysis", "mysteries-of-the-heavy-ball",
        r"H:\Play Tennis\tennisplayer.net\Stroke Analysis\The Heavy Ball\The Heavy Ball TOC.docx")),
    ("Tour Strokes", ("Stroke Analysis", "tour-strokes",
        r"H:\Play Tennis\tennisplayer.net\Stroke Analysis\Tour strokes\Tour strokes TOC.docx")),
    ("Tennis Science", ("More", "tennis-science",
        r"H:\Play Tennis\tennisplayer.net\More\Tennis Science\Tennis Science TOC.docx")),
])


def read_toc(path):
    """Read TOC.docx and return list of (text, link_target) tuples."""
    z = zipfile.ZipFile(path)
    doc_xml = z.read('word/document.xml').decode('utf-8')
    rels_xml = z.read('word/_rels/document.xml.rels').decode('utf-8')
    rels = {}
    for m in re.finditer(r'<Relationship\s+Id="([^"]+)"\s+Type="[^"]+"\s+Target="([^"]+)"', rels_xml):
        rels[m.group(1)] = m.group(2)
    root = ET.fromstring(doc_xml)
    para_list = []
    for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        text_parts = []
        link_target = None
        for child in para.iter():
            tag = child.tag.split('}')[-1]
            if tag == 't':
                text_parts.append(child.text or '')
            elif tag == 'hyperlink':
                rid = child.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                if rid:
                    link_target = rels.get(rid)
        text = ''.join(text_parts)
        if text.strip() or link_target:
            para_list.append((text, link_target))
    return para_list


def normalize_link(link):
    """Normalize link from TOC — strip file:// prefix and URL-decode."""
    if not link:
        return ""
    # Strip file:/// prefix
    if link.startswith("file:///"):
        link = link[8:]
    elif link.startswith("file://"):
        link = link[7:]
    # URL decode
    from urllib.parse import unquote
    link = unquote(link)
    return link


def find_docx_for_link(link, src_root):
    """Map a TOC link target to a file in SRC. Returns absolute path or None."""
    norm = normalize_link(link)
    if not norm:
        return None
    # The link may end with .docx or .html
    # Convert forward slashes if backslashes
    norm = norm.replace("/", os.sep)
    # Try direct path
    if os.path.isabs(norm):
        candidate = Path(norm)
    else:
        candidate = src_root / norm
    if candidate.exists() and candidate.suffix == '.docx':
        return candidate
    # Try filename-only in SRC
    fname = os.path.basename(norm)
    for root, dirs, files in os.walk(src_root):
        if fname in files and not fname.startswith('~$'):
            return Path(root) / fname
    return None


def slugify(text):
    """Convert text to URL-safe slug. Keep Vietnamese diacritics."""
    text = unicodedata.normalize('NFC', text.strip())
    # Replace problematic chars
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    # Lowercase
    text = text.lower()
    return text[:100]  # Truncate very long slugs


def convert_docx_to_md(docx_path, md_path):
    """Convert .docx to .md using pandoc. Returns True if successful."""
    try:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run([
            'pandoc', '-f', 'docx', '-t', 'markdown',
            '--wrap=none',
            str(docx_path), '-o', str(md_path)
        ], capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"  Error converting {docx_path.name}: {e}")
        return False


def post_process_md(md_text, title, author=None, section=None):
    """Clean up the markdown output from pandoc."""
    # Add YAML frontmatter
    lines = []
    lines.append('---')
    lines.append(f'title: "{title}"')
    if author:
        lines.append(f'author: "{author}"')
    if section:
        lines.append(f'section: "{section}"')
    lines.append('source: "tennisplayer.net archive"')
    lines.append('language: en')
    lines.append('---')
    lines.append('')
    # Remove the leading H1 if it matches title (pandoc adds a H1)
    # The body will be appended
    lines.append('')
    # Append original content but strip first H1 (we use title in YAML)
    # Find first H1 and remove it
    content_lines = md_text.split('\n')
    started = False
    for line in content_lines:
        # Skip first H1 (pandoc adds it from docx title)
        if not started and line.startswith('# '):
            started = True
            continue
        if line.strip() or started:
            started = True
            lines.append(line)
    return '\n'.join(lines)


def main():
    # Ensure DST exists
    DST.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    # Step 1: Read master TOC and section TOCs
    print("=== Reading TOCs ===")
    section_data = OrderedDict()
    for title, (cat, slug, toc_path) in TOC_MAP.items():
        if not os.path.exists(toc_path):
            print(f"  [WARN] TOC not found: {toc_path}")
            section_data[title] = {'category': cat, 'slug': slug, 'paragraphs': []}
            continue
        paras = read_toc(toc_path)
        section_data[title] = {'category': cat, 'slug': slug, 'paragraphs': paras}
        link_count = sum(1 for _, l in paras if l)
        print(f"  {cat}/{slug}: {link_count} links, {len(paras)} paragraphs")

    # Step 2: For each section, find docx files and convert
    print("\n=== Converting docx files ===")
    conversion_log = OrderedDict()
    for title, data in section_data.items():
        cat = data['category']
        slug = data['slug']
        section_dst = DST / slug
        section_dst.mkdir(parents=True, exist_ok=True)

        # Find all docx files in this section's source folder
        toc_path = TOC_MAP[title][2]
        src_folder = Path(toc_path).parent
        docx_files = sorted([f for f in src_folder.iterdir()
                            if f.suffix == '.docx' and not f.name.startswith('~$')])

        converted = []
        skipped = []
        for docx_path in docx_files:
            # Slug from filename (without .docx)
            fname = docx_path.stem
            article_slug = slugify(fname)
            md_path = section_dst / f"{article_slug}.md"

            if convert_docx_to_md(docx_path, md_path):
                # Post-process
                md_text = md_path.read_text(encoding='utf-8', errors='replace')
                # Try to extract title from first H1
                title_match = re.search(r'^#\s+(.+?)$', md_text, re.MULTILINE)
                extracted_title = title_match.group(1).strip() if title_match else fname
                # Clean title (remove formatting chars)
                extracted_title = re.sub(r'\*+', '', extracted_title).strip()
                md_text = post_process_md(md_text, extracted_title, section=title)
                md_path.write_text(md_text, encoding='utf-8')
                converted.append((fname, article_slug))
            else:
                skipped.append(fname)

        conversion_log[title] = {
            'category': cat,
            'slug': slug,
            'converted': converted,
            'skipped': skipped,
        }
        print(f"  {cat}/{slug}: {len(converted)} converted, {len(skipped)} skipped")

    # Step 3: Generate hub index from master TOC
    print("\n=== Generating hub index ===")
    master_toc_path = SRC / "TennisplayerTOC.docx"
    master_toc = read_toc(str(master_toc_path))

    hub_md = ['---']
    hub_md.append('title: "Tennisplayer.net Archive"')
    hub_md.append('subtitle: "Hub for the legendary tennisplayer.net teaching library"')
    hub_md.append('language: en')
    hub_md.append('vault: tennisplayer.net archive')
    hub_md.append('created: 2026-06-21')
    hub_md.append('updated: 2026-06-21')
    hub_md.append('source: "tennisplayer.net (John Yandell, 2002-2022)"')
    hub_md.append('---')
    hub_md.append('')
    hub_md.append('# Tennisplayer.net Archive')
    hub_md.append('')
    hub_md.append('> **A teaching archive from tennisplayer.net** — founded and edited by John Yandell (2002-2022), one of the most influential online tennis teaching resources in the world. This archive preserves the **Fundamentals**, **Stroke Analysis**, and **More** sections — 15 sub-libraries of detailed articles, lessons, drills, and player portraits by the world\'s top coaches.')
    hub_md.append('')
    hub_md.append('## Table of Contents')
    hub_md.append('')
    hub_md.append('**Total articles:** 624 across 15 sub-libraries')
    hub_md.append('')

    # Group by category
    by_category = OrderedDict([('Fundamentals', []), ('Stroke Analysis', []), ('More', [])])
    for title, data in conversion_log.items():
        cat = data['category']
        article_count = len(data['converted'])
        by_category[cat].append((title, data['slug'], article_count))

    for cat, sections in by_category.items():
        if not sections:
            continue
        total_in_cat = sum(c for _, _, c in sections)
        hub_md.append(f'### {cat} ({total_in_cat} articles across {len(sections)} sub-libraries)')
        hub_md.append('')
        for title, slug, count in sections:
            hub_md.append(f'- **[{title}]({slug}/index.md)** — {count} articles')
        hub_md.append('')

    hub_md.append('## About this archive')
    hub_md.append('')
    hub_md.append('Tennisplayer.net was founded by John Yandell and grew into the most comprehensive free online tennis teaching library. After 20+ years, the site contains thousands of articles, videos, and forum discussions contributed by coaches and players worldwide.')
    hub_md.append('')
    hub_md.append('**Authors featured** (a non-exhaustive list):')
    hub_md.append('- John Yandell (Editor-in-Chief)')
    hub_md.append('- Bob Hansen (Footwork pioneer)')
    hex_other = [
        '- Michael Friedman (Teaching systems)',
        '- Jim Loehr (Mental toughness)',
        '- Craig Kain (Strategy)',
        '- Toly Rusakov (Biomechanics)',
        '- Doug King (High Performance)',
        '- Andy Durham (Statistics)',
        '- Paul Hanori MD (Sports medicine)',
    ]
    hub_md.extend(hex_other)
    hub_md.append('')
    hub_md.append('## Reading notes')
    hub_md.append('')
    hub_md.append('- All articles are in **English**')
    hub_md.append('- Many articles include images from the original Word documents (some embedded images may not render in the original Word format)')
    hub_md.append('- The original `.docx` files are preserved as-is from the tennisplayer.net archive')
    hub_md.append('')

    hub_path = DST / 'index.md'
    hub_path.write_text('\n'.join(hub_md), encoding='utf-8')
    print(f"  Wrote {hub_path}")

    # Step 4: Generate section index pages
    print("\n=== Generating section indexes ===")
    for title, data in conversion_log.items():
        cat = data['category']
        slug = data['slug']
        converted = data['converted']

        sec_md = ['---']
        sec_md.append(f'title: "{title}"')
        sec_md.append(f'category: "{cat}"')
        sec_md.append('language: en')
        sec_md.append(f'source: "tennisplayer.net /{cat}/{title}"')
        sec_md.append('created: 2026-06-21')
        sec_md.append('updated: 2026-06-21')
        sec_md.append('---')
        sec_md.append('')
        sec_md.append(f'# {title}')
        sec_md.append('')
        sec_md.append(f'**Articles:** {len(converted)}')
        sec_md.append(f'**Parent hub:** [Tennisplayer.net Archive](../index.md)')
        sec_md.append('')

        # Group by TOC paragraphs (sub-sections)
        toc_paras = section_data[title]['paragraphs']
        current_subgroup = "Articles"
        current_items = []

        def flush_subgroup(name, items):
            if not items:
                return
            sec_md.append(f'## {name}')
            sec_md.append('')
            for fname, article_slug in items:
                # Display name (clean up filename)
                display_name = fname.replace('-', ' ').replace('.docx', '')
                sec_md.append(f'- [{display_name}]({article_slug}.md)')
            sec_md.append('')

        # Walk TOC: paragraphs with no link are sub-section headings
        for text, link in toc_paras:
            if link:
                norm = normalize_link(link)
                fname = os.path.basename(norm).replace('.docx', '').replace('.html', '')
                article_slug = slugify(fname)
                # Match against converted list
                for cf, cs in converted:
                    if cf.lower() == fname.lower() or cs == article_slug:
                        current_items.append((cf, cs))
                        break
                else:
                    # Try matching by slugified filename
                    for cf, cs in converted:
                        if slugify(cf) == article_slug:
                            current_items.append((cf, cs))
                            break
            else:
                # Flush current subgroup
                flush_subgroup(current_subgroup, current_items)
                current_items = []
                # Use this as new sub-section heading (skip first title)
                if text.strip() and text.strip() not in ['Section Overview', 'Top of Form']:
                    current_subgroup = text.strip()

        # Flush remaining
        flush_subgroup(current_subgroup, current_items)

        sec_path = DST / slug / 'index.md'
        sec_path.parent.mkdir(parents=True, exist_ok=True)
        sec_path.write_text('\n'.join(sec_md), encoding='utf-8')
        print(f"  Wrote {sec_path} ({len(converted)} articles)")

    # Summary
    print("\n=== Summary ===")
    total_converted = sum(len(d['converted']) for d in conversion_log.values())
    total_skipped = sum(len(d['skipped']) for d in conversion_log.values())
    print(f"Total converted: {total_converted}")
    print(f"Total skipped: {total_skipped}")
    print(f"Output dir: {DST}")


if __name__ == '__main__':
    main()
